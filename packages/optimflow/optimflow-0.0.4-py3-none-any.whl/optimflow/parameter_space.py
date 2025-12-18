import logging
from functools import cached_property
from concurrent.futures import ProcessPoolExecutor
from typing import Callable
from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

import param

from optimflow.optimisation_parameters import OptimParams
from optimflow.simulation_parameters import SimulationParams
from optimflow.utils import clean_dir, load_json


class BaseParameterSpaceOperation:
    DIR_KEY = "case"

    def __init__(self, out: str):
        self.out_dir = Path(out)

    @property
    def dirs(self):
        return sorted(self.out_dir.glob(f"{BaseParameterSpaceOperation.DIR_KEY}_*"))

    def run(self, f: Callable, parallel=True) -> list:
        if not parallel:
            res = [f(x) for x in self.dirs]

        else:
            with ProcessPoolExecutor() as p:
                res = list(p.map(f, self.dirs))
        return res


class ParameterSpaceExploration(BaseParameterSpaceOperation):
    def dump_params(
        self, simu_params: SimulationParams, optim_params: OptimParams, n: int = 5
    ):
        clean_dir(self.out_dir)

        for i, x, infos in optim_params.linear_oneatatime_iter(
            *optim_params.all_keys, n=n
        ):
            params = simu_params.copy()
            params.out_dir = self.out_dir / f"{ParameterSpaceExploration.DIR_KEY}_{i}"
            for k, v in x.to_dict().items():
                params.param.add_parameter(k, param.Number(v))
            params.save(infos)

    def gather_results(self) -> pd.DataFrame:
        cases: dict[tuple[str, int], pd.DataFrame] = {}

        for case_dir in self.dirs:
            infos = load_json(case_dir / "infos.json")
            res = np.loadtxt(case_dir / "result.txt")
            df_case = pd.DataFrame({"result": np.atleast_1d(res)})
            key = (infos["varying"], infos["i"])
            cases[key] = df_case

        # columns MultiIndex: level 0 = varying, level 1 = i
        df = pd.concat(cases, axis=1)
        df = df.sort_index(axis=1)

        df.to_csv(self.out_dir / "results.csv")
        return df

    @cached_property
    def value_map(self):
        # build mapping (var, i) -> value from infos.json
        value_map_ = {}
        for case_dir in self.out_dir.glob("case_*"):
            infos = load_json(case_dir / "infos.json")
            key = (infos["varying"], int(infos["i"]))
            value_map_[key] = float(infos["value"])
        return value_map_

    def plot_results(self, show=True):
        df = pd.read_csv(self.out_dir / "results.csv", index_col=0, header=[0, 1, 2])
        groups = list(df.groupby(level=[0, 2], axis=1))
        n = len(groups)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))

        fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 3 * rows), sharex=True)
        for ax, ((var, comp), sub) in zip(axes, groups):
            block = sub.xs((var, comp), axis=1, level=[0, 2])

            for i in block.columns:
                v = self.value_map[(var, int(i))]
                ax.plot(block.index, block[i], label=f"{round(v, 3)}")

            ax.set_title(f"{var}")
            ax.set_xlabel("time [s]")
            ax.set_ylabel(f"{comp}")
            ax.legend()

        for ax in axes[n:]:
            ax.set_visible(False)
        fig.tight_layout()
        if show:
            plt.show()
        fig.savefig(self.out_dir / "plots.png")


class ParameterSpaceAsk(BaseParameterSpaceOperation):
    DIR_KEY = "pop"

    @property
    def dirs(self):
        return sorted(self.out_dir.glob(f"{ParameterSpaceAsk.DIR_KEY}_*"))

    def dump_params(
        self, values, simu_params: SimulationParams, optim_params: OptimParams
    ):
        # Create simulation dirs from sampled values (1 row per sample, ie one column per optim param)
        clean_dir(self.out_dir)

        for i, row in enumerate(values):
            params = simu_params.copy()
            params.out_dir = self.out_dir / f"{ParameterSpaceAsk.DIR_KEY}_{i}"
            names = optim_params.to_dict().keys()
            for k, v in zip(names, row):
                params.param.add_parameter(k, param.Number(v))
            params.save()


log = logging.getLogger(__name__)
