import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import param
import pandas as pd

from optimflow.optimisation_parameters import OptimParams
from optimflow.parameter_space import (
    ParameterSpace,
    ParameterSpaceAsk,
    ParameterSpaceExploration,
)
from optimflow.simulation_parameters import SimulationParams


"""Parameter space utilities: exploration (dump/run/gather/plot) and ask-mode dumping."""


def _worker(case_dir: Path) -> None:
    params = SimulationParams.load_from(case_dir)
    t = np.linspace(0.0, 1.0, 10)
    res = params.p1 * np.sin(params.p2 * 2.0 * np.pi * t)
    np.savetxt(Path(params.out_dir) / "result.txt", res)


class TestParameterSpace(unittest.TestCase):
    def test_base_dirs_uses_default_dir_key(self) -> None:
        with TemporaryDirectory() as td:
            out = Path(td) / "out"
            out.mkdir(parents=True, exist_ok=True)

            (out / f"{ParameterSpace.DIR_KEY}_0").mkdir()
            (out / f"{ParameterSpace.DIR_KEY}_1").mkdir()
            (out / "other_0").mkdir()

            ps = ParameterSpace(out)
            self.assertEqual([d.name for d in ps.dirs], ["case_0", "case_1"])


class TestParameterSpaceExploration(unittest.TestCase):
    def test_dump_params_creates_case_dirs_with_json(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        with TemporaryDirectory() as td:
            out = Path(td) / "out"
            explo = ParameterSpaceExploration(out)

            simu = SimulationParams()
            optim = P()

            explo.dump_params(simu, optim, n=2)

            dirs = explo.dirs
            self.assertEqual(len(dirs), 2 * len(optim.all_keys))
            for d in dirs:
                self.assertTrue(d.name.startswith("case_"))
                self.assertTrue((d / "params.json").exists())
                self.assertTrue((d / "infos.json").exists())

    def test_run_sequential_executes_worker_for_all_cases(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        with TemporaryDirectory() as td:
            out = Path(td) / "out"
            explo = ParameterSpaceExploration(out)

            simu = SimulationParams()
            optim = P()

            explo.dump_params(simu, optim, n=2)
            explo.run(_worker, parallel=False)

            for d in explo.dirs:
                self.assertTrue((d / "result.txt").exists())
                arr = np.loadtxt(d / "result.txt")
                self.assertEqual(arr.shape, (10,))
                self.assertTrue(np.isfinite(arr).all())

    def test_gather_results_builds_dataframe_and_writes_csv(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        with TemporaryDirectory() as td:
            out = Path(td) / "out"
            explo = ParameterSpaceExploration(out)

            simu = SimulationParams()
            optim = P()

            explo.dump_params(simu, optim, n=2)
            explo.run(_worker, parallel=False)

            df = explo.gather_results()

            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(df.shape[0], 10)
            self.assertEqual(df.columns.nlevels, 3)
            self.assertTrue((out / "results.csv").exists())

    def test_value_map_reads_infos(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        with TemporaryDirectory() as td:
            out = Path(td) / "out"
            explo = ParameterSpaceExploration(out)

            simu = SimulationParams()
            optim = P()

            explo.dump_params(simu, optim, n=2)

            vm = explo.value_map
            self.assertEqual(set(k[0] for k in vm.keys()), {"p1", "p2"})
            self.assertTrue(all(isinstance(k[1], int) for k in vm.keys()))
            self.assertTrue(all(isinstance(v, float) for v in vm.values()))

    def test_plot_results_creates_png(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        with TemporaryDirectory() as td:
            out = Path(td) / "out"
            explo = ParameterSpaceExploration(out)

            simu = SimulationParams()
            optim = P()

            explo.dump_params(simu, optim, n=2)
            explo.run(_worker, parallel=False)
            explo.gather_results()
            explo.plot_results(show=False)

            self.assertTrue((out / "plots.png").exists())


class TestParameterSpaceAsk(unittest.TestCase):
    def test_dirs_uses_pop_key(self) -> None:
        with TemporaryDirectory() as td:
            out = Path(td) / "out"
            out.mkdir(parents=True, exist_ok=True)
            (out / "pop_0").mkdir()
            (out / "pop_1").mkdir()
            (out / "case_0").mkdir()

            ask = ParameterSpaceAsk(out)
            self.assertEqual([d.name for d in ask.dirs], ["pop_0", "pop_1"])

    def test_dump_params_creates_pop_dirs_with_params_json(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.3, bounds=(0.0, 1.0))
            p2 = param.Number(0.93, bounds=(0.9, 1.1))

        with TemporaryDirectory() as td:
            out = Path(td) / "out"
            ask = ParameterSpaceAsk(out)

            simu = SimulationParams()
            optim = P()

            values = np.array([[0.2, 0.95], [0.8, 1.05]], dtype=float)
            ask.dump_params(values, simu, optim)

            dirs = ask.dirs
            self.assertEqual(len(dirs), 2)
            for d in dirs:
                self.assertTrue(d.name.startswith("pop_"))
                self.assertTrue((d / "params.json").exists())


if __name__ == "__main__":
    unittest.main()
