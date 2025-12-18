"""
Lifex-specific ParameterSpace implementations.

This module adapts OptimFlow's parameter-space workflow to Lifex simulations by using
`LifexParams`, which writes a deal.II `.prm` file alongside the usual JSON metadata.

Classes
- `LifexParameterSpaceExploration`:
  - Extends `ParameterSpaceExploration`.
  - `dump_params(...)` generates `case_*` directories.
  - For each sample from `OptimParams.linear_oneatatime_iter(...)`, it:
    - copies the baseline `LifexParams`
    - sets `out_dir` to `case_<i>`
    - applies sampled parameters via `LifexParams.add_optim_params(...)`
    - saves the updated `.prm` + metadata (and `infos.json`)

- `LifexParameterSpaceAsk`:
  - Extends `ParameterSpaceAsk`.
  - `dump_params(values, ...)` generates `pop_*` directories from an explicit matrix of
    candidate values (e.g. CMA-ES / external optimizer).
  - For each row, it:
    - updates the `optim_params` instance values in key order
    - applies them to `LifexParams` via `add_optim_params(...)`
    - saves the updated `.prm` + metadata

Notes
- Both classes clear the output directory with `clean_dir(self.out_dir)` before dumping.
- `values` is expected to be an iterable of rows matching `optim_params.all_keys`.
"""

import logging

from optimflow.utils import clean_dir
from optimflow import OptimParams, ParameterSpaceExploration, ParameterSpaceAsk

from optimflow_lifex.lifex_params import LifexParams


class LifexParameterSpaceExploration(ParameterSpaceExploration):
    def dump_params(
        self, simu_params: LifexParams, optim_params: OptimParams, n: int = 5
    ):
        clean_dir(self.out_dir)

        for i, x, infos in optim_params.linear_oneatatime_iter(
            *optim_params.all_keys, n=n
        ):
            params = simu_params.copy()
            params.out_dir = self.out_dir / f"case_{i}"
            params.add_optim_params(x)
            params.save(infos)


class LifexParameterSpaceAsk(ParameterSpaceAsk):
    def dump_params(self, values, simu_params: LifexParams, optim_params: OptimParams):
        clean_dir(self.out_dir)

        for i, row in enumerate(values):
            params = simu_params.copy()
            params.out_dir = self.out_dir / f"pop_{i}"
            for k, v in zip(optim_params.all_keys, row):
                setattr(optim_params, k, v)
            params.add_optim_params(optim_params)
            params.save()


log = logging.getLogger(__name__)
