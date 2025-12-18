"""
LifexParams: SimulationParams specialization for Lifex/deal.II `.prm` parameter files.

This module provides a bridge between OptimFlow simulation/optimization parameters and a
deal.II-style parameter file used by Lifex (here, the TTP06 ionic model).

Key points
- `LifexParams` extends `SimulationParams` with:
  - `lifex_params_fname`: path to a baseline `.prm` file (default: `log_params_TTP06.prm`)
  - `lifex_param_set`: parsed parameter tree (via `pyrameters.PRM`)
- When `lifex_params_fname` changes, `lifex_param_set` is automatically reloaded.
- Parameters are accessed/updated through `__getitem__`/`__setitem__` using keys under:
  `/Ionic model/TTP06/Physical constants/<key>`
- `add_optim_params()` applies an `OptimParams` instance to the `.prm` tree.
- `save()` writes the current `.prm` to `<out_dir>/lifex_params.prm`, updates
  `lifex_params_fname`, then persists the usual OptimFlow JSON files via `SimulationParams.save`.
- `save_with()` sets `out_dir`, applies `OptimParams`, and saves the updated `.prm`.

Typical usage
- Define an optimization parameter set (subclass of `OptimParams`), then:
  - load baseline `.prm` through `lifex_params_fname`
  - apply optimization values
  - save a runnable simulation directory with the updated `.prm` and JSON metadata
"""

import logging
from pathlib import Path

import param
from pyrameters import PRM

from optimflow import OptimParams, SimulationParams


DEFAULT_PARAMS = Path(__file__).parent / "log_params_TTP06.prm"


class LifexParams(SimulationParams):
    dict_excluded = ("out_dir", "lifex_param_set")
    lifex_params_fname = param.Filename(
        default=DEFAULT_PARAMS, doc="fname of baseline params"
    )
    lifex_param_set: dict = param.Dict(doc="dealII params")

    @param.depends("lifex_params_fname", watch=True, on_init=True)
    def _update_lifex_params_fname(self):
        with open(self.lifex_params_fname) as f:
            self.lifex_param_set = PRM(f.read())

    def __getitem__(self, item):
        _ = self.lifex_param_set.get(f"/Ionic model/TTP06/Physical constants/{item}")
        if _ is not None:
            return _
        else:
            log.error(f"Parameter {item!r} not found in TTP06 parameters")

    def __setitem__(self, idx, value):
        assert self[idx] is not None, f"Parameter {idx!r} not found in TTP06 parameters"
        self.lifex_param_set.set(f"/Ionic model/TTP06/Physical constants/{idx}", value)

    def add_optim_params(self, params: OptimParams):
        for k, v in params.items:
            self[k] = v

    def save(self, data: dict = None):
        with open(fname := self.out_dir / "lifex_params.prm", "w") as f:
            f.write(str(self.lifex_param_set))
        self.lifex_params_fname = fname
        super().save(data)

    def save_with(self, out: str, optim_params: OptimParams):
        self.out_dir = Path(out)
        for k, v in optim_params.items:
            self[k] = v
        self.save()


log = logging.getLogger(__name__)
