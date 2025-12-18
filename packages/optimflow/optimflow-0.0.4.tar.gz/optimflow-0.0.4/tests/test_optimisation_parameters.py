import unittest

import param

from optimflow.optimisation_parameters import OptimParams


"""Container for optimization parameters with utilities for serialization and iteration"""


class TestOptimParams(unittest.TestCase):
    def test_to_dict_excludes_name(self) -> None:
        class P(OptimParams):
            p1 = param.Number(1.0, bounds=(0.0, 1.0))
            p2 = param.Number(2.0, bounds=(0.0, 3.0))

        p = P()
        d = p.to_dict()

        self.assertNotIn("name", d)
        self.assertEqual(d["p1"], 1.0)
        self.assertEqual(d["p2"], 2.0)

    def test_all_keys_matches_to_dict_keys(self) -> None:
        class P(OptimParams):
            p1 = param.Number(1.0, bounds=(0.0, 1.0))
            p2 = param.Number(2.0, bounds=(0.0, 3.0))

        p = P()
        self.assertEqual(p.all_keys, list(p.to_dict().keys()))

    def test_items_yields_pairs_from_to_dict(self) -> None:
        class P(OptimParams):
            p1 = param.Number(1.0, bounds=(0.0, 1.0))
            p2 = param.Number(2.0, bounds=(0.0, 3.0))

        p = P()
        self.assertEqual(dict(p.items), p.to_dict())

    def test_assign_sets_values_in_key_order(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.0, bounds=(0.0, 1.0))
            p2 = param.Number(0.0, bounds=(0.0, 3.0))

        p = P()
        self.assertEqual(p.all_keys, ["p1", "p2"])

        p.assign([0.3, 2.7])
        self.assertAlmostEqual(p.p1, 0.3, places=12)
        self.assertAlmostEqual(p.p2, 2.7, places=12)

    def test_linear_iter_yields_index_and_parameterized(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        p = P()
        out = list(p.linear_iter("p1", "p2", n=3))

        self.assertEqual(len(out), 3)
        self.assertEqual([i for i, _ in out], [0, 1, 2])

        xs = [x for _, x in out]
        for x in xs:
            self.assertTrue(hasattr(x, "p1"))
            self.assertTrue(hasattr(x, "p2"))

        p1_vals = [x.p1 for x in xs]
        p2_vals = [x.p2 for x in xs]
        self.assertGreater(len(set(p1_vals)), 1)
        self.assertGreater(len(set(p2_vals)), 1)

    def test_linear_oneatatime_iter_yields_infos_and_changes_one_param(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        p = P()
        out = list(p.linear_oneatatime_iter("p1", "p2", n=3))

        self.assertTrue(out)

        for idx, x, xi in out:
            self.assertIsInstance(idx, int)
            self.assertTrue(hasattr(x, "p1"))
            self.assertTrue(hasattr(x, "p2"))
            self.assertIsInstance(xi, dict)

            self.assertEqual(set(xi.keys()), {"i", "varying", "value"})
            self.assertIsInstance(xi["i"], int)
            self.assertIn(xi["varying"], {"p1", "p2"})

            changed_key = xi["varying"]
            self.assertAlmostEqual(getattr(x, changed_key), xi["value"], places=12)

            other_key = "p2" if changed_key == "p1" else "p1"
            self.assertAlmostEqual(
                getattr(x, other_key), getattr(p, other_key), places=12
            )

    def test_lhs_iter_yields_index_and_parameterized_within_bounds(self) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        p = P()
        out = list(p.lhs_iter("p1", "p2", n=8))

        self.assertEqual(len(out), 8)

        idxs = [i for i, _ in out]
        self.assertEqual(idxs, list(range(8)))

        xs = [x for _, x in out]
        for x in xs:
            self.assertTrue(p.param["p1"].bounds[0] <= x.p1 <= p.param["p1"].bounds[1])
            self.assertTrue(p.param["p2"].bounds[0] <= x.p2 <= p.param["p2"].bounds[1])

        p1_vals = [x.p1 for x in xs]
        p2_vals = [x.p2 for x in xs]
        self.assertGreater(len(set(p1_vals)), 1)
        self.assertGreater(len(set(p2_vals)), 1)

    def test_random_sampling_iter_yields_index_and_parameterized_within_bounds(
        self,
    ) -> None:
        class P(OptimParams):
            p1 = param.Number(0.5, bounds=(0.0, 1.0))
            p2 = param.Number(1.0, bounds=(0.9, 1.1))

        p = P()
        out = list(p.random_sampling_iter("p1", "p2", n=10))

        self.assertEqual(len(out), 10)
        self.assertEqual([i for i, _ in out], list(range(10)))

        xs = [x for _, x in out]
        for i, x in xs:
            self.assertTrue(p.param["p1"].bounds[0] <= x.p1 <= p.param["p1"].bounds[1])
            self.assertTrue(p.param["p2"].bounds[0] <= x.p2 <= p.param["p2"].bounds[1])

        p1_vals = [x.p1 for i, x in xs]
        p2_vals = [x.p2 for i, x in xs]
        self.assertGreater(len(set(p1_vals)), 1)
        self.assertGreater(len(set(p2_vals)), 1)


if __name__ == "__main__":
    unittest.main()
