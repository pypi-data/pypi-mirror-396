import logging
import json
from pathlib import Path
from copy import deepcopy

import param

from optimflow.optimisation_parameters import OptimParams
from optimflow.utils import dump_json, load_json, Foldername


class SimulationParams(param.Parameterized):
    dict_excluded = ("out_dir",)
    out_dir = Foldername(doc="Simulation output directory")

    def to_dict(self) -> dict:
        subset = [p for p in self.param if p not in self.dict_excluded]
        data = json.loads(self.param.serialize_parameters(subset))
        data["out_dir"] = str(self.out_dir) if self.out_dir is not None else None
        return data

    @classmethod
    def load_from(cls, dname):
        data = load_json(dname / "params.json")
        allowed = {k: v for k, v in data.items() if k in cls.param}
        others = {k: v for k, v in data.items() if k not in cls.param}
        p = cls(**allowed)
        for k, v in others.items():
            p.param.add_parameter(k, param.Number(v))
        return p

    def save(self, data: dict = None):
        dump_json(self.out_dir / "params.json", self.to_dict())
        if data is not None:
            dump_json(self.out_dir / "infos.json", data)

    def copy(self):
        return deepcopy(self)

    def save_with(self, out: str, optim_params: OptimParams):
        self.out_dir = Path(out)
        for k, v in optim_params.to_dict().items():
            self.param.add_parameter(k, param.Number(v))
        self.save()


log = logging.getLogger(__name__)
