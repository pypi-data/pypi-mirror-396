import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import param

from optimflow.param_iter import LinearIter, LinearOneAtATimeIter


"""Iterators over parameter spaces with linear sampling strategies."""


class _Defaults(param.Parameterized):
    p1 = param.Number(0.5, bounds=(0.0, 1.0))
    p2 = param.Number(1.0, bounds=(0.9, 1.1))

    def to_dict(self) -> dict:
        x = json.loads(self.param.serialize_parameters())
        x.pop("name", None)
        return x


class TestParamIter(unittest.TestCase):
    def test_len_paramiter_is_number_of_params(self) -> None:
        d = _Defaults()
        it = LinearIter(d.param["p1"], d.param["p2"], defaults=d, n=3)
        self.assertEqual(len(it), 3)

    def test_linear_iter_len_is_n(self) -> None:
        d = _Defaults()
        it = LinearIter(d.param["p1"], d.param["p2"], defaults=d, n=4)
        self.assertEqual(len(it), 4)

    def test_linear_iter_generates_n_samples_and_updates_all(self) -> None:
        d = _Defaults()
        it = LinearIter(d.param["p1"], d.param["p2"], defaults=d, n=3)

        xs = list(it.gen)
        self.assertEqual(len(xs), 3)

        p1_vals = [x.p1 for x in xs]
        p2_vals = [x.p2 for x in xs]
        self.assertGreater(len(set(p1_vals)), 1)
        self.assertGreater(len(set(p2_vals)), 1)

        for x in xs:
            self.assertTrue(d.param["p1"].bounds[0] <= x.p1 <= d.param["p1"].bounds[1])
            self.assertTrue(d.param["p2"].bounds[0] <= x.p2 <= d.param["p2"].bounds[1])

        self.assertAlmostEqual(d.p1, 0.5, places=12)
        self.assertAlmostEqual(d.p2, 1.0, places=12)

    def test_linear_oneatatime_iter_len_is_n_times_num_params(self) -> None:
        d = _Defaults()
        it = LinearOneAtATimeIter(d.param["p1"], d.param["p2"], defaults=d, n=3)
        self.assertEqual(len(it), 3 * 2)

    def test_gen_infos_matches_generated_values(self) -> None:
        d = _Defaults()
        it = LinearOneAtATimeIter(d.param["p1"], d.param["p2"], defaults=d, n=3)

        infos = list(it.gen_infos)
        xs = list(it.gen)

        self.assertEqual(len(infos), len(xs))
        self.assertEqual(len(infos), len(it))

        for x, xi in zip(xs, infos):
            self.assertEqual(set(xi.keys()), {"i", "varying", "value"})
            self.assertIsInstance(xi["i"], int)
            self.assertIn(xi["varying"], {"p1", "p2"})

            changed_key = xi["varying"]
            self.assertTrue(np.isfinite(xi["value"]))
            self.assertAlmostEqual(getattr(x, changed_key), xi["value"], places=12)

            other_key = "p2" if changed_key == "p1" else "p1"
            self.assertAlmostEqual(
                getattr(x, other_key), getattr(d, other_key), places=12
            )

    def test_save_writes_json_with_expected_keys(self) -> None:
        d = _Defaults()
        it = LinearIter(d.param["p1"], d.param["p2"], defaults=d, n=3)

        with TemporaryDirectory() as td:
            out = Path(td) / "iter.json"
            it.save(out)

            self.assertTrue(out.exists())
            payload = json.loads(out.read_text())

        self.assertEqual(
            set(payload.keys()), {"n", "N", "bounds", "varying", "defaults"}
        )
        self.assertEqual(payload["n"], 3)
        self.assertEqual(payload["N"], 3)
        self.assertIsInstance(payload["defaults"], dict)
        self.assertIn("p1", payload["defaults"])
        self.assertIn("p2", payload["defaults"])


if __name__ == "__main__":
    unittest.main()
