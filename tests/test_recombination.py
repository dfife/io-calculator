"""Numerical and boundary checks for the theorem-grade Phase 2 module."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator import (  # noqa: E402
    OpenTheoremBoundaryError,
    Stage2History,
    build_visibility_packet,
    local_background_state,
    local_baryon_loading_R,
    local_scattering_to_expansion_ratio,
    local_sound_speed_m_s,
    optical_depth_gradient_per_redshift,
    primitive_local_kappa_prime,
    saha_equilibrium_xe,
    solve_exact_stage2_history,
)


def test_local_background_state_matches_carried_io_map() -> None:
    """The local background map should stay pinned to the carried IO branch."""

    state = local_background_state(1100.0)
    assert math.isclose(state.T_r_loc_K, 2932.5082822644, rel_tol=0.0, abs_tol=1.0e-9)
    assert math.isclose(
        state.n_H_geom_m3,
        236605106.84411275,
        rel_tol=0.0,
        abs_tol=1.0e-3,
    )
    assert math.isclose(
        state.H_loc_s_inv,
        3.066896182991767e-14,
        rel_tol=0.0,
        abs_tol=1.0e-26,
    )


def test_saha_seed_and_local_opacity_outputs_are_reproducible() -> None:
    """The local chemistry seed and primitive opacity should be reproducible."""

    x_e = saha_equilibrium_xe(1100.0)
    assert math.isclose(x_e, 0.0025881144670350555, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        primitive_local_kappa_prime(1100.0, x_e),
        16.279919995444942,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert math.isclose(
        optical_depth_gradient_per_redshift(1100.0, x_e),
        0.0003616796656907364,
        rel_tol=0.0,
        abs_tol=1.0e-18,
    )
    assert math.isclose(
        local_scattering_to_expansion_ratio(1100.0, x_e),
        0.3982093119255007,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_local_sound_speed_helpers_stay_on_inventory_branch() -> None:
    """The isolated local `R` and `c_s` helpers are part of the live surface."""

    assert math.isclose(
        local_baryon_loading_R(1100.0),
        0.6351270933342528,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(
        local_sound_speed_m_s(1100.0),
        135358121.3870273,
        rel_tol=0.0,
        abs_tol=1.0e-6,
    )


def test_visibility_packet_is_relative_to_the_supplied_lower_boundary() -> None:
    """The readout packet should integrate only over the supplied history span."""

    history = Stage2History.from_sequences(
        [0.0, 1.0, 2.0],
        [1.0e-4, 2.0e-4, 3.0e-4],
        [2.0, 2.0, 2.0],
    )
    packet = build_visibility_packet(history)

    d0 = optical_depth_gradient_per_redshift(0.0, 1.0e-4)
    d1 = optical_depth_gradient_per_redshift(1.0, 2.0e-4)
    d2 = optical_depth_gradient_per_redshift(2.0, 3.0e-4)

    tau1 = 0.5 * (d0 + d1)
    tau2 = tau1 + 0.5 * (d1 + d2)

    assert packet.absolute_to_observer is True
    assert packet.tau_obs[0] == 0.0
    assert math.isclose(packet.tau_obs[1], tau1, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(packet.tau_obs[2], tau2, rel_tol=0.0, abs_tol=1.0e-18)
    assert packet.g_obs[0] > 0.0
    assert packet.g_obs[2] > packet.g_obs[0]


def test_exact_stage2_history_refuses_to_invent_a_solver() -> None:
    """The calculator should fail honestly at the exact Stage-2 seam."""

    with pytest.raises(OpenTheoremBoundaryError):
        solve_exact_stage2_history([900.0, 1100.0])
