"""Checks for the exact inherited-FULL Stage-2 dynamic-history builder."""

from __future__ import annotations

import math
import sys
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.recombination import build_visibility_packet, solve_exact_stage2_history  # noqa: E402
from aio_calculator.scalar_hierarchy import (  # noqa: E402
    ScalarHierarchyState,
    build_scalar_hierarchy_carrier,
)
from aio_calculator.scalar_metric_state import (  # noqa: E402
    build_newtonian_scalar_metric_state,
    build_scalar_stress_energy_summary,
)
from aio_calculator.scalar_transfer_projector import (  # noqa: E402
    build_newtonian_scalar_source_history,
    project_closed_s3_scalar_temperature,
)
from aio_calculator.stage2_dynamic_network import (  # noqa: E402
    InheritedFullStage2DynamicHistoryBuilder,
    build_inherited_full_exact_stage2_history,
    build_inherited_full_stage2_history,
)


@lru_cache(maxsize=1)
def _exact_history():
    """Return one cached exact inherited-FULL history sample."""

    return build_inherited_full_exact_stage2_history([900.0, 1100.0, 1400.0, 2000.0])


@lru_cache(maxsize=1)
def _observer_reduced_history():
    """Return one cached observer-absolute reduced Stage-2 history."""

    return build_inherited_full_stage2_history([0.0, 900.0, 1100.0])


def test_inherited_full_builder_returns_exact_sampled_extended_state() -> None:
    """The builder should export the full sampled `Y_rec = (x_e, T_m, D_-, L_-)` state."""

    history = _exact_history()
    assert history.claim_status == "conditional / scoped"
    assert history.provenance_node_ids == (
        "premise.2",
        "paper31.stage2_markov_state",
        "local.inherited_full_stage2_dynamic_history_builder",
    )
    assert history.line_labels == ("Ly_alpha", "Ly_beta", "Ly_gamma")
    assert len(history.characteristic_energy_eV) == 311
    assert len(history.D_minus) == 311
    assert len(history.D_minus[0]) == 4
    assert len(history.L_minus) == 3
    assert math.isclose(history.history_activation_z, 1741.6653759861101, rel_tol=0.0, abs_tol=1.0e-9)
    assert math.isclose(history.x_e[1], 0.0845372978636342, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(history.T_m_loc_K[1], 2932.4741060366673, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(history.x_e[2], 0.7059223673067317, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(history.T_m_loc_K[2], 3731.552491309313, rel_tol=0.0, abs_tol=1.0e-12)


def test_prehistory_region_is_exactly_thermal_in_exported_distortion_state() -> None:
    """Samples above the activation redshift should carry zero exported distortions."""

    history = _exact_history()
    assert history.z_obs[-1] > history.history_activation_z
    assert all(math.isclose(row[-1], 0.0, rel_tol=0.0, abs_tol=1.0e-30) for row in history.D_minus[:10])
    assert all(math.isclose(row[-1], 0.0, rel_tol=0.0, abs_tol=1.0e-30) for row in history.L_minus)
    assert any(abs(row[1]) > 0.0 for row in history.D_minus[:10])
    assert any(abs(row[1]) > 0.0 for row in history.L_minus)


def test_exact_history_reduction_requires_explicit_characteristic_compression_choice() -> None:
    """The smaller Stage-2 carrier should not invent a preferred `D_-` reduction."""

    history = _exact_history()
    reduced = history.reduce_to_stage2_history()
    assert reduced.D_minus_norm is None
    assert reduced.L_minus is None

    selected = history.reduce_to_stage2_history(characteristic_bin=0, line_channel=0)
    assert selected.D_minus_norm == history.D_minus[0]
    assert selected.L_minus == history.L_minus[0]


def test_builder_implements_the_existing_exact_stage2_solver_surface() -> None:
    """The inherited-FULL builder should plug into `solve_exact_stage2_history()` cleanly."""

    builder = InheritedFullStage2DynamicHistoryBuilder()
    reduced = solve_exact_stage2_history([900.0, 1100.0, 1400.0], solver=builder)
    assert reduced.z_obs == (900.0, 1100.0, 1400.0)
    assert math.isclose(reduced.x_e[1], 0.0845372978636342, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(reduced.T_m_loc_K[2], 3731.552491309313, rel_tol=0.0, abs_tol=1.0e-12)
    assert reduced.D_minus_norm is None
    assert reduced.L_minus is None


def test_exact_stage2_history_wires_to_visibility_and_transfer_carrier() -> None:
    """The inherited-FULL history should drive an observer-absolute scalar source projector."""

    history = _observer_reduced_history()
    visibility = build_visibility_packet(history)
    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    states = (
        ScalarHierarchyState(
            phi=1.0e-4,
            psi=1.0e-4,
            delta_gamma=1.5e-2,
            theta_gamma=2.0e-3,
            delta_b=1.1e-2,
            theta_b=3.0e-3,
            photon_multipoles=(2.0e-4,),
            polarization_multipoles=(4.0e-4, 0.0, 8.0e-4),
        ),
        ScalarHierarchyState(
            phi=1.1e-4,
            psi=1.1e-4,
            delta_gamma=1.8e-2,
            theta_gamma=2.5e-3,
            delta_b=1.2e-2,
            theta_b=3.3e-3,
            photon_multipoles=(2.2e-4,),
            polarization_multipoles=(4.5e-4, 0.0, 9.0e-4),
        ),
        ScalarHierarchyState(
            phi=1.2e-4,
            psi=1.2e-4,
            delta_gamma=2.0e-2,
            theta_gamma=2.8e-3,
            delta_b=1.3e-2,
            theta_b=3.5e-3,
            photon_multipoles=(2.4e-4,),
            polarization_multipoles=(5.0e-4, 0.0, 1.0e-3),
        ),
    )
    stresses = (
        build_scalar_stress_energy_summary(
            delta_rho=0.10,
            delta_p=0.03,
            rho_plus_p_theta=0.04,
            rho_plus_p_shear=0.02,
        ),
        build_scalar_stress_energy_summary(
            delta_rho=0.11,
            delta_p=0.031,
            rho_plus_p_theta=0.041,
            rho_plus_p_shear=0.021,
        ),
        build_scalar_stress_energy_summary(
            delta_rho=0.12,
            delta_p=0.032,
            rho_plus_p_theta=0.042,
            rho_plus_p_shear=0.022,
        ),
    )
    metric_states = tuple(
        build_newtonian_scalar_metric_state(
            carrier,
            stress,
            scale_factor=0.02,
            a_prime_over_a_mpc_inv=0.4,
            phi=phi,
        )
        for stress, phi in zip(stresses, (2.0e-4, 2.2e-4, 2.4e-4))
    )
    source_history = build_newtonian_scalar_source_history(
        carrier,
        conformal_time_mpc=[0.2, 0.4, 0.6],
        visibility=visibility,
        states=states,
        metric_states=metric_states,
    )
    packet = project_closed_s3_scalar_temperature(
        source_history,
        tau_observer_mpc=0.9,
        ell_values=[0],
    )
    assert visibility.absolute_to_observer is True
    assert packet.ell_values == (0,)
    assert math.isfinite(packet.delta_l[0].real)
    assert abs(packet.delta_l[0]) > 0.0
