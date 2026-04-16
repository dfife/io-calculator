"""Operational `z_*`, `r_s(z_*)`, and `theta_*` estimator on the clean HyRec surface.

This module no longer claims theorem-grade closure for `z_*`, `r_s(z_*)`, or
`theta_*`.

What survives after the Phase 2 review is narrower:

- `verified / operational`:
  the clean local-history HyRec toggle surface is a reproducible estimator
  surface on the IO local background-state map (`H_loc`, `T_R,loc`,
  `n_H,geom`) with the extra Paper 34 complement toggles disabled
- `verified / operational`:
  the exported `z_star`, `rs_star`, and `100*theta_star` values from that
  surface are useful numerical diagnostics
- `not theorem-grade`:
  no exact IO Stage-2 dynamic-network renormalization has been derived
- `not theorem-grade`:
  no bridge theorem currently identifies this estimator's
  `r_s(z_*) / D_M(z_*)` object with the Paper 20 / 21 `theta*_bare` or with
  the final observer-side `theta*_obs`

So this module is intentionally fenced as research support rather than live
calculator runtime math.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from .constants import (
    ACTIVE_BARYON_SLOTS,
    ACTIVE_BRANCH,
    CALCULATOR_ROOT,
    CLASS_PUBLIC_ROOT,
    BranchParameters,
)

CLASS_PUBLIC_BUILD_BASE = CALCULATOR_ROOT / ".class_public_build"
IO_RECOMBINATION_X = 1.5189873277742727
IO_RECOMBINATION_GAMMA = 0.2375
IO_RECOMBINATION_RS_M = 6.6835e26


def _omega_cdm_h2_for_geom_branch(
    branch: BranchParameters,
    *,
    omega_b_geom_h2: float,
) -> float:
    """Return the CDM physical density after reserving the geom baryon slot."""

    omega_m_total = branch.Omega_m * branch.h**2
    omega_cdm_h2 = omega_m_total - omega_b_geom_h2
    if omega_cdm_h2 <= 0.0:
        raise ValueError("omega_cdm must be positive on the supplied branch")
    return omega_cdm_h2


def _build_local_classy(*, rebuild: bool = False):
    """Build or reuse a local `classy` module from the vendored source tree."""

    if not CLASS_PUBLIC_ROOT.exists():
        raise RuntimeError(
            "The optional class_public vendor tree is not available. "
            "This research-only operational estimator requires a checkout at "
            f"{CLASS_PUBLIC_ROOT}."
        )

    if rebuild and CLASS_PUBLIC_BUILD_BASE.exists():
        shutil.rmtree(CLASS_PUBLIC_BUILD_BASE)

    build_libs = list(CLASS_PUBLIC_BUILD_BASE.glob("lib.*"))
    if rebuild or not build_libs:
        CLASS_PUBLIC_BUILD_BASE.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "python",
                "setup.py",
                "build",
                "--build-base",
                str(CLASS_PUBLIC_BUILD_BASE),
            ],
            cwd=CLASS_PUBLIC_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        build_libs = list(CLASS_PUBLIC_BUILD_BASE.glob("lib.*"))

    if not build_libs:
        raise RuntimeError("failed to build local class_public library")

    build_lib = build_libs[0]
    sys.path.insert(0, str(build_lib))
    try:
        for key in list(sys.modules):
            if key == "classy" or key.startswith("classy."):
                del sys.modules[key]
        return importlib.import_module("classy")
    finally:
        sys.path.pop(0)


def operational_stage2_params(
    branch: BranchParameters = ACTIVE_BRANCH,
    *,
    omega_b_geom_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
) -> dict[str, object]:
    """Return the clean local-history HyRec estimator surface.

    This is the calculator-side lock on the operational Calculator estimator:

    - FULL HyRec history enabled
    - local Hubble enabled
    - local bulk radiation temperature enabled
    - all extra Paper 34 complement toggles disabled
    - chemistry bound to the inventory / geom baryon slot

    The toggle package is reproducible and useful even though the exact IO
    Stage-2 solver class remains open.
    """

    return {
        "output": "",
        "reio_parametrization": "reio_none",
        "recombination": "hyrec",
        "H0": branch.H0,
        "T_cmb": branch.T_cmb,
        "Omega_k": branch.Omega_k,
        "N_ur": branch.N_eff,
        "N_ncdm": 0,
        "YHe": branch.YHe,
        "omega_b": omega_b_geom_h2,
        "omega_cdm": _omega_cdm_h2_for_geom_branch(
            branch,
            omega_b_geom_h2=omega_b_geom_h2,
        ),
        "io_recombination_use_full_hyrec": "yes",
        "io_recombination_local_hubble": "yes",
        "io_recombination_use_tio_temperature": "yes",
        "io_recombination_inverse_upward_rates": "no",
        "io_recombination_line_escape_complement": "no",
        "io_recombination_lya_diffusion_complement": "no",
        "io_recombination_x": IO_RECOMBINATION_X,
        "io_recombination_gamma": IO_RECOMBINATION_GAMMA,
        "io_recombination_rs_m": IO_RECOMBINATION_RS_M,
    }


@dataclass(frozen=True)
class OperationalStarEstimate:
    """Research-only photosphere/theta payload on the clean HyRec surface."""

    branch_label: str
    claim_status: str
    z_star: float
    z_rec: float
    z_d: float
    rs_star_mpc: float
    rs_rec_mpc: float
    rs_d_mpc: float
    dm_star_mpc: float
    theta_star_100: float
    theta_s_100: float

    def as_dict(self) -> dict[str, float | str]:
        return asdict(self)


def compute_operational_star_estimate(
    branch: BranchParameters = ACTIVE_BRANCH,
    *,
    rebuild_class_public: bool = False,
) -> OperationalStarEstimate:
    """Compute the clean Premise-2 operational `tau=1` photosphere estimator.

    The returned object is a verified numerical estimator on the clean
    local-history HyRec surface. It is not a theorem-grade closure of the IO
    `z_*`, `r_s(z_*)`, or `theta_*` problem.
    """

    classy_mod = _build_local_classy(rebuild=rebuild_class_public)
    cosmo = classy_mod.Class()
    try:
        cosmo.set(operational_stage2_params(branch))
        cosmo.compute()
        derived = cosmo.get_current_derived_parameters(
            [
                "z_star",
                "z_rec",
                "z_d",
                "100*theta_star",
                "100*theta_s",
                "rs_star",
                "rs_rec",
                "rs_d",
            ]
        )
        z_star = float(derived["z_star"])
        return OperationalStarEstimate(
            branch_label=branch.label,
            claim_status=(
                "verified operational estimator on the clean local-history "
                "HyRec surface; not theorem-grade closure"
            ),
            z_star=z_star,
            z_rec=float(derived["z_rec"]),
            z_d=float(derived["z_d"]),
            rs_star_mpc=float(derived["rs_star"]),
            rs_rec_mpc=float(derived["rs_rec"]),
            rs_d_mpc=float(derived["rs_d"]),
            dm_star_mpc=float(cosmo.angular_distance(z_star) * (1.0 + z_star)),
            theta_star_100=float(derived["100*theta_star"]),
            theta_s_100=float(derived["100*theta_s"]),
        )
    finally:
        try:
            cosmo.struct_cleanup()
            cosmo.empty()
        except Exception:
            pass


# Backward-compatible aliases kept for internal continuity while the boundary
# is repaired in the surrounding docs and reports.
TheoremStarQuantities = OperationalStarEstimate
theorem_stage2_params = operational_stage2_params
compute_theorem_star_quantities = compute_operational_star_estimate
