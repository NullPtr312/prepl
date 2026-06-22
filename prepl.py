from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass, field, asdict
from typing import Optional
import shlex
import json

# CONFIG START

OUTPUT_DIR = Path("~/Documents/Figures").expanduser()
INPUT_DIR = Path("~/Documents/Data").expanduser()

# CONFIG END

@dataclass
class PlotState:
    dataPath: Path | None = None
    x: str | None = None
    y: list[str] = field(default_factory=list)
    xlabel: str | None = None
    ylabel: str | None = None
    title: str | None = None
    legend: bool = True
    grid: bool = True
    style: str = "science"
    data: Optional[pd.DataFrame] = None

class PlotREPL:

    # METHODS
    def __init__(self):
        self.state = PlotState()
        self.commands = {
            "data": self.data_cmd,
            "plot": self.plot_cmd,
            "set": self.set_cmd,
            "state": self.state_cmd,
            "exit": self.exit_cmd,
        }

    def run(self):
        while True:
            cmd = input("PREPL> ").strip()
            self.handle(cmd)

    def require_args(self, args, n, usage):
        if len(args) < n:
            print(f"Not enough arguments (requires {n}). Usage: {usage}")
            return False
        return True

    def require_data(self):
        if self.state.data is None:
            print("Error: No data loaded. Use 'data load <file>' to load data")
            return False
        return True

    def handle(self, instruction: str):
        try:
            parts = shlex.split(instruction) 
            if not parts:
                return

            cmd = parts[0]
            args = parts[1:]

            if cmd in self.commands:
                self.commands[cmd](args)
            else:
                print(f"Unknown command: {cmd}")
        except Exception as e:
            print(f"Error: {e}")

    # COMMANDS

    def exit_cmd(self, args):
        exit(0)

    def save_state(self, file):
        with open(file, "w") as f:
            json.dump(asdict(self.state), f, default=str)

    def load_state(self, file):
        with open(file) as f:
            data = json.load(f)
        self.state = PlotState(**data)

    def state_cmd(self, args):
        if not self.require_args(args, 1, "save, load, reset"):
            return

        match args[0]:
            case "save":
                if not self.require_args(args, 2, "state save <filename>"):
                    return
                self.save_state(args[1])
            case "load":
                if not self.require_args(args, 2, "state load <filename>"):
                    return
                self.load_state(args[1])
            case "reset":
                self.state = PlotState()
                print("State reset")

    def data_cmd(self, args):

        if not (self.require_args(args, 1, "open, reload, view, select")):
            return

        match args[0]:
            case "open":
                if not self.require_args(args, 2, "data open <file>"):
                    return

                self.state.dataPath = INPUT_DIR / args[1]
                print("Data path set to " + str(self.state.dataPath))
                
                try:
                    self.loadData()
                except Exception:
                    print(f"Could not load data at {self.state.dataPath}.")

            case "reload":
                try:
                    self.loadData()
                except Exception:
                    print(f"Could not load data at {self.state.dataPath}.")

            case "view":
                if not self.require_data():
                    return
                print(f"Columns: {list(self.state.data.columns)}")

            case "select":
                if not (self.require_data() and self.require_args(args, 3, "data select <x> <y1> <y2>...")):
                    return

                cols = self.state.data.columns

                x = args[1]
                ys = args[2:]

                if x not in cols:
                    print(f"Invalid x column: {x}")
                    return

                for y in ys:
                    if y not in cols:
                        print(f"Invalid y column: {y}")
                        return

                self.state.x = x
                self.state.y = ys

            case _:
                print("Unknown Command")

    def set_cmd(self, args):
        if not self.require_args(args, 2, "xlabel, ylabel, style, title, grid, legend\nset <value> <argument>"):
            return 

        match args[0]:
            case "xlabel":
                self.state.xlabel = args[1]
            case "ylabel":
                self.state.ylabel = args[1]
            case "title":
                self.state.title = args[1]
            case "grid":
                if args[1] == "true":
                    self.state.grid = True
                elif args[1] == "false":
                    self.state.grid = False
                else:
                    print("Use: set grid true/false")
            case "legend":
                if args[1] == "true":
                    self.state.legend = True
                elif args[1] == "false":
                    self.state.legend = False
                else:
                    print("Use: set legend true/false")
            case "style":
                self.state.style = args[1]

    def loadData(self):
        self.state.data = pd.read_csv(self.state.dataPath)

    def plot_cmd(self, args):

        if not (self.require_data() and self.require_args(args, 1, "plot <outputfile> | plot show")):
            return

        data = self.state.data

        plt.style.use(self.state.style)
        plt.figure()

        for col in self.state.y:
            plt.plot(data[self.state.x], data[col], label=col)

        plt.xlabel(self.state.xlabel)
        plt.ylabel(self.state.ylabel)
        plt.title(self.state.title)
        if(self.state.legend):
            plt.legend()
        if(self.state.grid):
            plt.grid()


        saveLocation = OUTPUT_DIR / args[0]

        if(args[0] == "show"):
            plt.show()
        else:
            plt.savefig(saveLocation, bbox_inches="tight")
            print(f"Saved {saveLocation}")

if __name__ == "__main__":
    plotter = PlotREPL()
    plotter.run()
