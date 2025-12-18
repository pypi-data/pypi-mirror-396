import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import param

from optimflow.optimisation_parameters import OptimParams
from optimflow.simulation_parameters import SimulationParams


"""Simulation parameters persistence helpers (save/load/copy/save_with)."""


class TestSimulationParams(unittest.TestCase):
    def test_to_dict_serializes_out_dir_as_string_or_none(self) -> None:
        p = SimulationParams()
        d = p.to_dict()
        self.assertIn("out_dir", d)
        self.assertIsNone(d["out_dir"])

        with TemporaryDirectory() as td:
            p.out_dir = Path(td)
            d = p.to_dict()
            self.assertEqual(d["out_dir"], str(Path(td)))

    def test_save_writes_params_json_and_optional_infos_json(self) -> None:
        with TemporaryDirectory() as td:
            out = Path(td) / "run"
            out.mkdir(parents=True, exist_ok=True)

            p = SimulationParams()
            p.out_dir = out

            p.save(data={"a": 1})

            self.assertTrue((out / "params.json").exists())
            self.assertTrue((out / "infos.json").exists())

            params_payload = json.loads((out / "params.json").read_text())
            infos_payload = json.loads((out / "infos.json").read_text())

            self.assertIn("out_dir", params_payload)
            self.assertEqual(params_payload["out_dir"], str(out))
            self.assertEqual(infos_payload, {"a": 1})

    def test_load_from_restores_known_fields_and_adds_unknown_as_numbers(self) -> None:
        with TemporaryDirectory() as td:
            out = Path(td) / "run"
            out.mkdir(parents=True, exist_ok=True)

            payload = {"out_dir": str(out), "p1": 0.25, "p2": 1.05}
            (out / "params.json").write_text(json.dumps(payload))

            p = SimulationParams.load_from(out)

            self.assertEqual(p.out_dir, out)
            self.assertTrue(hasattr(p, "p1"))
            self.assertTrue(hasattr(p, "p2"))
            self.assertAlmostEqual(p.p1, 0.25, places=12)
            self.assertAlmostEqual(p.p2, 1.05, places=12)

            self.assertIsInstance(p.param["p1"], param.Number)
            self.assertIsInstance(p.param["p2"], param.Number)

    def test_copy_creates_independent_object(self) -> None:
        with TemporaryDirectory() as td:
            p = SimulationParams()
            p.out_dir = Path(td)
            p.param.add_parameter("p1", param.Number(0.1))

            q = p.copy()
            self.assertIsNot(p, q)
            self.assertEqual(q.out_dir, p.out_dir)
            self.assertAlmostEqual(q.p1, p.p1, places=12)

            q.p1 = 0.9
            self.assertAlmostEqual(p.p1, 0.1, places=12)
            self.assertAlmostEqual(q.p1, 0.9, places=12)

    def test_save_with_sets_out_dir_adds_optim_params_and_saves(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.3, bounds=(0.0, 1.0))
            p2 = param.Number(1.02, bounds=(0.9, 1.1))

        optim = P()

        with TemporaryDirectory() as td:
            out = Path(td) / "run"
            sp = SimulationParams()
            sp.save_with(out, optim)

            self.assertEqual(sp.out_dir, out)
            self.assertTrue((out / "params.json").exists())

            saved = json.loads((out / "params.json").read_text())
            self.assertIn("p1", saved)
            self.assertIn("p2", saved)
            self.assertAlmostEqual(saved["p1"], 0.3, places=12)
            self.assertAlmostEqual(saved["p2"], 1.02, places=12)

            loaded = SimulationParams.load_from(out)
            self.assertAlmostEqual(loaded.p1, 0.3, places=12)
            self.assertAlmostEqual(loaded.p2, 1.02, places=12)


if __name__ == "__main__":
    unittest.main()
