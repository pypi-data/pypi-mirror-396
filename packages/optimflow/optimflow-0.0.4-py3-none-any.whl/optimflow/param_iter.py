import logging
from pathlib import Path
from copy import deepcopy
from typing import Protocol
import numpy as np

import param
from smt.sampling_methods import LHS, Random

from optimflow.utils import dump_json


class DefaultsLike(Protocol):
    def to_dict(self) -> dict: ...


class ParamIter:
    """
    Class intended to provide methods to iterate over several sets
    of parameters
    """

    def __init__(
        self,
        *ps: param.Parameter,
        defaults: DefaultsLike,
        n: int = None,
    ):
        self.params = list(ps)
        self.defaults = defaults
        self.n = n

    def __len__(self):
        return len(self.params)

    @property
    def gen(self):
        raise NotImplementedError

    def save(self, fname: str):
        fname = Path(fname)
        fname.parent.mkdir(exist_ok=True)
        dump_json(
            fname,
            {
                "n": self.n,
                "N": len(self),
                "varying": [x.name for x in self.params],
                "bounds": [x.bounds for x in self.params],
                "defaults": self.defaults.to_dict(),
            },
        )
        return self


class LinearIter(ParamIter):
    def __len__(self):
        return self.n

    @property
    def gen(self):
        """
        Return self.n sets of parameters, each parameter has n values
        varying linearly between its bounds
        """
        bds = [np.linspace(*x.bounds, self.n) for x in self.params]
        for i in range(self.n):
            d = deepcopy(self.defaults)
            updates = {p.name: bds[j][i] for j, p in enumerate(self.params)}
            d.param.update(**updates)
            yield d


class LinearOneAtATimeIter(ParamIter):
    def __len__(self):
        return self.n * len(self.params)

    @property
    def gen(self):
        """
        Return self.n*len(self.params) sets of parameters, each parameter has n values
        varying linearly between its bounds while the other are set to default
        """
        for x in self.params:
            bds = x.bounds
            for val in np.linspace(*bds, self.n):
                d = deepcopy(self.defaults)
                setattr(d, x.name, val)
                yield d

    @property
    def gen_infos(self):
        for x in self.params:
            bds = x.bounds
            for i, val in enumerate(np.linspace(*bds, self.n)):
                d = deepcopy(self.defaults)
                setattr(d, x.name, val)
                yield {"i": i, "varying": x.name, "value": val}


class LHSParamIter(ParamIter):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        bds = [x.bounds for x in self.params]
        sampling = LHS(xlimits=np.array(bds), criterion="ese")
        self.sampling = sampling(self.n)

    def __len__(self):
        return self.n

    @property
    def gen(self):
        for i in range(self.n):
            d = deepcopy(self.defaults)
            for j, x in enumerate(self.params):
                setattr(d, x.name, self.sampling[i][j])
            yield i, d


class RandomSamplingParamIter(ParamIter):
    """
    Uniform sampling
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        bds = [x.bounds for x in self.params]
        sampling = Random(xlimits=np.array(bds))
        self.sampling = sampling(self.n)

    def __len__(self):
        return self.n

    @property
    def gen(self):
        for i in range(self.n):
            d = deepcopy(self.defaults)
            for j, x in enumerate(self.params):
                setattr(d, x.name, self.sampling[i][j])
            yield i, d


log = logging.getLogger(__name__)
