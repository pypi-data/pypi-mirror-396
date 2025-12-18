import logging
import json
from typing import Iterator, Tuple

import param

from optimflow.param_iter import (
    LHSParamIter,
    LinearIter,
    LinearOneAtATimeIter,
    RandomSamplingParamIter,
)


class OptimParams(param.Parameterized):
    def to_dict(self) -> dict:
        x = json.loads(self.param.serialize_parameters())
        x.pop("name")
        return x

    def assign(self, x: list):
        for k, v in zip(self.all_keys, x):
            setattr(self, k, v)

    @property
    def all_keys(self):
        return list(self.to_dict().keys())

    @property
    def items(self):
        for k, v in self.to_dict().items():
            yield k, v

    def linear_iter(
        self, *ps: str, n: int = None
    ) -> Iterator[Tuple[int, param.Parameterized]]:
        """
        Iterate over several sets of parameters
        """
        for i, x in enumerate(
            LinearIter(*[self.param[k] for k in list(ps)], defaults=self, n=n).gen
        ):
            yield i, x

    def linear_oneatatime_iter(
        self, *ps: str, n: int = None
    ) -> Iterator[Tuple[int, param.Parameterized, dict]]:
        """
        Iterate over several sets of parameters
        """
        it = LinearOneAtATimeIter(
            *[self.param[k] for k in list(ps)], defaults=self, n=n
        )
        for i, (x, xi) in enumerate(zip(it.gen, it.gen_infos)):
            yield i, x, xi

    def lhs_iter(self, *ps: str, n: int = None) -> Iterator[param.Parameterized]:
        """
        Iterate over several sets of parameters
        """
        for x in LHSParamIter(
            *[self.param[k] for k in list(ps)], defaults=self, n=n
        ).gen:
            yield x

    def random_sampling_iter(
        self, *ps: str, n: int = None
    ) -> Iterator[Tuple[int, param.Parameterized]]:
        """
        Iterate over several sets of parameters
        """
        for i, x in enumerate(
            RandomSamplingParamIter(
                *[self.param[k] for k in list(ps)], defaults=self, n=n
            ).gen
        ):
            yield i, x


log = logging.getLogger(__name__)
