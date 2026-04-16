"""Lock the clean operational Calculator Stage-2 toggle surface."""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator import (  # noqa: E402
    ACTIVE_BARYON_SLOTS,
    ACTIVE_BRANCH,
    operational_stage2_params,
)


def test_theorem_stage2_params_keep_only_the_clean_premise2_surface() -> None:
    """The operational star estimator must stay off the old complement routes."""

    params = operational_stage2_params()
    assert params["recombination"] == "hyrec"
    assert params["reio_parametrization"] == "reio_none"
    assert params["io_recombination_use_full_hyrec"] == "yes"
    assert params["io_recombination_local_hubble"] == "yes"
    assert params["io_recombination_use_tio_temperature"] == "yes"
    assert params["io_recombination_inverse_upward_rates"] == "no"
    assert params["io_recombination_line_escape_complement"] == "no"
    assert params["io_recombination_lya_diffusion_complement"] == "no"
    assert math.isclose(
        float(params["omega_b"]),
        ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
        rel_tol=0.0,
        abs_tol=1.0e-18,
    )
    expected_omega_cdm = (
        ACTIVE_BRANCH.Omega_m * ACTIVE_BRANCH.h**2
        - ACTIVE_BARYON_SLOTS.omega_b_geom_h2
    )
    assert math.isclose(
        float(params["omega_cdm"]),
        expected_omega_cdm,
        rel_tol=0.0,
        abs_tol=1.0e-18,
    )
