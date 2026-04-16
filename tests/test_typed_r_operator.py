"""Checks for the typed local `R` operator."""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.recombination import local_baryon_loading_R  # noqa: E402
from aio_calculator.thomson_history_contract import ThomsonHistorySample  # noqa: E402
from aio_calculator.typed_r_operator import (  # noqa: E402
    build_typed_r_operator_sample,
    single_rate_silk_diffusion_integrand,
)


def test_typed_r_operator_closes_local_loading_and_drag_composites() -> None:
    """The primitive local `R` leg should stay on `omega_b,geom` and close its composites."""

    sample = build_typed_r_operator_sample(
        1100.0,
        ThomsonHistorySample(
            z_obs=1100.0,
            thomson_drag_rate=12.0,
            thomson_hierarchy_rate=15.0,
            tau_c=1.0 / 12.0,
            dtau_c=-2.0e-3,
            slip=0.0,
            shear=0.0,
        ),
    )
    R_loading = local_baryon_loading_R(1100.0)
    R_hierarchy = 1.0 / R_loading
    assert math.isclose(sample.R_local_geom, R_loading, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.R_hierarchy, R_hierarchy, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.tau_c_drag, 1.0 / 12.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.photon_momentum_exchange_rate, 12.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.baryon_momentum_exchange_rate, 12.0 * R_hierarchy, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.photon_baryon_sound_speed_sq, 1.0 / (3.0 * (1.0 + R_loading)), rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.baryon_inertia_factor, 1.0 + R_hierarchy, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.odd_even_dynamic_loading_factor, R_hierarchy / (1.0 + R_hierarchy), rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.inverse_baryon_loading_factor, R_loading, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.tight_coupling_slip_factor, (1.0 / 12.0) / (1.0 + R_hierarchy), rel_tol=0.0, abs_tol=1.0e-15)
    assert sample.odd_even_loading_driver == sample.R_local_geom
    assert sample.observer_readout_slot == "omega_b,eff"
    assert sample.claim_status == "derived / scoped as maps"
    assert sample.provenance_node_ids == (
        "paper29.sound_speed_selector",
        "paper32.typed_baryon_slot_spec",
        "calculator.thomson_history_realization",
        "local.typed_r_operator",
        "local.typed_r_site_uniqueness",
    )


def test_typed_r_operator_silk_split_reduces_to_standard_single_rate_formula() -> None:
    """When drag and hierarchy rates coincide, the split Silk operator should reduce exactly."""

    z_obs = 900.0
    rate = 7.5
    sample = build_typed_r_operator_sample(
        z_obs,
        ThomsonHistorySample(
            z_obs=z_obs,
            thomson_drag_rate=rate,
            thomson_hierarchy_rate=rate,
            tau_c=1.0 / rate,
            dtau_c=-1.0e-3,
            slip=0.0,
            shear=0.0,
        ),
    )
    expected = single_rate_silk_diffusion_integrand(local_baryon_loading_R(z_obs), rate)
    assert math.isclose(sample.diffusion_total_integrand, expected, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        sample.diffusion_total_integrand,
        sample.diffusion_heat_conduction_integrand + sample.diffusion_viscosity_integrand,
        rel_tol=0.0,
        abs_tol=1.0e-18,
    )
