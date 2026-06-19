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
    style: str = "science"
    data: Optional[pd.DataFrame] = None

class PlotREPL:
    def __init__(self):
        self.state = PlotState()

    def run(self):
        while True:
            cmd = input("PREPL> ").strip()
            self.handle(cmd)

    def save_state(self, file):
        with open(file, "w") as f:
            json.dump(asdict(self.state), f, default=str)

    def load_state(self, file):
        with open(file) as f:
            data = json.load(f)
        self.state = PlotState(**data)

    def handle(self, cmd: str):
        parts = shlex.split(cmd) 
        if not parts:
            return

        match parts[0]:
            case "data":
                self.data_cmd(parts[1:])
            case "plot":
                if len(parts) < 2:
                    self.plot("Unnamed")
                else:
                    self.plot(parts[1])
            case "reset":
                self.reset()
            case "set":
                self.set_cmd(parts[1:])
            case "save":
                self.save_state("save.json")
            case "load":
                self.load_state("save.json")
                self.loadData()
            case "exit":
                exit(0)
            case _:
                print("Unknown Command")

    def data_cmd(self, args):
        match args[0]:
            case "load":
                self.state.dataPath = INPUT_DIR / args[1]
                print("Data path set to " + str(self.state.dataPath))
                try:
                    self.loadData()
                except Exception:
                    print("Could not load data")
            case "view":
                if self.state.data is None:
                    print("Data not loaded")
                    return
                print(f"Columns: {list(self.state.data.columns)}")
            case "select":

                if self.state.data is None:
                    print("No data selected")
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

            case "help":
                print("L")
            case _:
                print("Unknown Command")

    def set_cmd(self, args):
        match args[0]:
            case "xlabel":
                self.state.xlabel = args[1]
            case "ylabel":
                self.state.ylabel = args[1]

    def loadData(self):
        self.state.data = pd.read_csv(self.state.dataPath)

    def plot(self, fileName):

        try:
            self.loadData()
        except Exception:
            print("Could not load data")
            return

        data = self.state.data

        plt.style.use(self.state.style)
        plt.figure()

        for col in self.state.y:
            plt.plot(data[self.state.x], data[col], label=col)

        plt.xlabel(self.state.xlabel)
        plt.ylabel(self.state.ylabel)
        plt.legend()

        saveLocation = OUTPUT_DIR / fileName

        plt.savefig(saveLocation, bbox_inches="tight")
        print(f"Saved {saveLocation}")

if __name__ == "__main__":
    plotter = PlotREPL()
    plotter.run()
