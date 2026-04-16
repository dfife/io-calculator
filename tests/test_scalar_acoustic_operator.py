"""Checks for the local closed-`S^3` scalar acoustic generator."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.recombination import (  # noqa: E402
    OpenTheoremBoundaryError,
    Stage2History,
    local_baryon_loading_R,
)
from aio_calculator.scalar_acoustic_operator import (  # noqa: E402
    ClosedS3ScalarAcousticOperator,
    ScalarHierarchyRegime,
    build_closed_s3_scalar_acoustic_sample,
    build_newtonian_metric_drive,
    build_scalar_metric_drive,
    build_synchronous_metric_drive,
    evaluate_closed_s3_scalar_acoustic_derivatives,
    predict_first_order_tight_coupling_contract,
)
from aio_calculator.scalar_hierarchy import (  # noqa: E402
    ScalarHierarchyState,
    build_scalar_hierarchy_carrier,
    evolve_scalar_hierarchy_step,
    make_scalar_hierarchy_step_request,
)
from aio_calculator.thomson_history_contract import build_thomson_history_contract  # noqa: E402


def _make_sample(*, slip_mid: float = 2.0e-3, shear_mid: float = 5.0e-4):
    """Build one reusable explicit scalar acoustic sample on a conformal grid."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=2.0)
    history = Stage2History.from_sequences(
        [900.0, 1100.0, 1300.0],
        [5.0e-2, 1.0e-1, 2.0e-1],
        [2600.0, 3000.0, 3300.0],
    )
    thomson = build_thomson_history_contract(
        [900.0, 1100.0, 1300.0],
        [8.0, 10.0, 14.0],
        [9.0, 11.0, 15.0],
        [-0.2, -0.3, -0.4],
        [1.0e-3, slip_mid, 3.0e-3],
        [4.0e-4, shear_mid, 6.0e-4],
        derivative_coordinate="conformal_time",
    )
    metric_drive = build_scalar_metric_drive(
        metric_continuity=7.0e-3,
        metric_euler=-9.0e-3,
        metric_shear=4.0e-3,
        metric_shear_prime=-2.0e-3,
    )
    sample = build_closed_s3_scalar_acoustic_sample(
        carrier,
        history,
        thomson,
        index=1,
        conformal_time_mpc=0.7,
        a_prime_over_a_mpc_inv=0.08,
        a_primeprime_over_a_mpc_inv2=0.01,
        metric_drive=metric_drive,
    )
    return carrier, history, thomson, metric_drive, sample


def test_scalar_acoustic_sample_derives_closed_geometry_and_local_loading() -> None:
    """The sample builder should reproduce the closed-shell and local-leg formulas."""

    carrier, _, _, _, sample = _make_sample()
    assert sample.carrier == carrier
    assert math.isclose(sample.laplacian_k_sq_mpc_inv2, 6.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.shifted_scalar_sq_mpc_inv2, 5.25, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.q_sq_mpc_inv2, 6.25, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.nu, 5.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.s2_squared, 0.875, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        sample.R_loading,
        1.0 / local_baryon_loading_R(1100.0),
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(sample.typed_R.R_hierarchy, sample.R_loading, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.typed_R.baryon_inertia_factor, 1.0 + sample.R_loading, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        sample.typed_R.odd_even_dynamic_loading_factor,
        sample.R_loading / (1.0 + sample.R_loading),
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert sample.cb2 > 0.0
    assert math.isfinite(sample.cb2)
    assert math.isfinite(sample.dcb2_dconformal_mpc_inv)
    assert sample.supports_ell(4) is True
    assert sample.supports_ell(5) is False
    assert sample.claim_status == "derived / scoped local scalar acoustic sample"


def test_metric_drive_builders_reproduce_standard_gauge_quartets() -> None:
    """Gauge packets should map to the exact scalar acoustic quartet formulas."""

    newtonian = build_newtonian_metric_drive(
        phi_prime=1.5e-3,
        psi=-2.0e-3,
        laplacian_k_sq_mpc_inv2=6.0,
    )
    synchronous = build_synchronous_metric_drive(
        h_prime=4.0e-3,
        alpha=5.0e-4,
        alpha_prime=-7.0e-4,
        laplacian_k_sq_mpc_inv2=6.0,
    )

    assert math.isclose(newtonian.metric_continuity, -4.5e-3, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(newtonian.metric_euler, -1.2e-2, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(newtonian.metric_shear, 0.0, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(newtonian.metric_shear_prime, 0.0, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(synchronous.metric_continuity, 2.0e-3, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(synchronous.metric_euler, 0.0, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(synchronous.metric_shear, 3.0e-3, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(synchronous.metric_shear_prime, -4.2e-3, rel_tol=0.0, abs_tol=1.0e-18)


def test_scalar_acoustic_sample_requires_conformal_time_tuple() -> None:
    """The theorem-grade sample builder should reject non-conformal tuple coordinates."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=2.0)
    history = Stage2History.from_sequences(
        [900.0, 1100.0, 1300.0],
        [5.0e-2, 1.0e-1, 2.0e-1],
        [2600.0, 3000.0, 3300.0],
    )
    thomson = build_thomson_history_contract(
        [900.0, 1100.0, 1300.0],
        [8.0, 10.0, 14.0],
        [9.0, 11.0, 15.0],
        [-0.2, -0.3, -0.4],
        [1.0e-3, 2.0e-3, 3.0e-3],
        [4.0e-4, 5.0e-4, 6.0e-4],
    )
    metric_drive = build_scalar_metric_drive(
        metric_continuity=0.0,
        metric_euler=0.0,
        metric_shear=0.0,
    )
    with pytest.raises(OpenTheoremBoundaryError):
        build_closed_s3_scalar_acoustic_sample(
            carrier,
            history,
            thomson,
            index=1,
            conformal_time_mpc=0.7,
            a_prime_over_a_mpc_inv=0.08,
            a_primeprime_over_a_mpc_inv2=0.01,
            metric_drive=metric_drive,
        )


def test_full_hierarchy_derivatives_match_closed_scalar_formulas() -> None:
    """The explicit full-hierarchy RHS should reproduce the local closed-shell equations."""

    _, _, _, _, sample = _make_sample()
    state = ScalarHierarchyState(
        phi=1.0e-5,
        psi=2.0e-5,
        delta_gamma=1.5e-2,
        theta_gamma=-2.0e-2,
        delta_b=1.2e-2,
        theta_b=1.0e-2,
        photon_multipoles=(2.0e-2, 3.0e-2, 1.0e-2),
        polarization_multipoles=(4.0e-2, 5.0e-2, 6.0e-2, 7.0e-2, 8.0e-2),
    )
    derivatives = evaluate_closed_s3_scalar_acoustic_derivatives(state, sample)

    shear = state.photon_multipoles[0]
    l3 = state.photon_multipoles[1]
    l4 = state.photon_multipoles[2]
    pol0, pol1, pol2, pol3, pol4 = state.polarization_multipoles
    s2 = sample.s_l(2)
    s3 = sample.s_l(3)
    s4 = sample.s_l(4)
    P0 = (pol0 + pol2 + 2.0 * s2 * shear) / 8.0

    expected_delta_gamma = -4.0 / 3.0 * (state.theta_gamma + sample.metric_drive.metric_continuity)
    expected_delta_b = -(state.theta_b + sample.metric_drive.metric_continuity)
    expected_theta_b = (
        -sample.a_prime_over_a_mpc_inv * state.theta_b
        + sample.metric_drive.metric_euler
        + sample.laplacian_k_sq_mpc_inv2 * sample.cb2 * state.delta_b
        + sample.typed_R.baryon_momentum_exchange_rate * (state.theta_gamma - state.theta_b)
    )
    expected_theta_gamma = (
        sample.laplacian_k_sq_mpc_inv2 * (state.delta_gamma / 4.0 - sample.s2_squared * shear)
        + sample.metric_drive.metric_euler
        + sample.thomson.thomson_drag_rate * (state.theta_b - state.theta_gamma)
    )
    expected_shear_prime = 0.5 * (
        8.0 / 15.0 * (state.theta_gamma + sample.metric_drive.metric_shear)
        - 3.0 / 5.0 * sample.laplacian_k_mpc_inv * s3 / s2 * l3
        - sample.thomson.thomson_hierarchy_rate * (2.0 * shear - 4.0 / (5.0 * s2) * P0)
    )
    expected_l3_prime = (
        sample.laplacian_k_mpc_inv
        / 7.0
        * (3.0 * s3 * 2.0 * s2 * shear - 4.0 * s4 * l4)
        - sample.thomson.thomson_hierarchy_rate * l3
    )
    expected_pol0_prime = (
        -sample.laplacian_k_mpc_inv * pol1
        - sample.thomson.thomson_hierarchy_rate * (pol0 - 4.0 * P0)
    )

    assert derivatives.used_contract_slip is None
    assert derivatives.used_contract_shear is None
    assert math.isclose(derivatives.delta_gamma_prime, expected_delta_gamma, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(derivatives.delta_b_prime, expected_delta_b, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(derivatives.theta_b_prime, expected_theta_b, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(derivatives.theta_gamma_prime, expected_theta_gamma, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(derivatives.photon_multipole_prime[0], expected_shear_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(derivatives.photon_multipole_prime[1], expected_l3_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        derivatives.polarization_multipole_prime[0],
        expected_pol0_prime,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_tight_coupling_contract_regime_uses_supplied_slip_and_shear() -> None:
    """The reduced contract should consume slip/shear explicitly and stop there."""

    _, _, _, _, sample = _make_sample(slip_mid=7.5e-4, shear_mid=2.5e-4)
    state = ScalarHierarchyState(
        phi=0.0,
        psi=0.0,
        delta_gamma=1.2e-2,
        theta_gamma=1.5e-2,
        delta_b=9.0e-3,
        theta_b=7.0e-3,
    )
    derivatives = evaluate_closed_s3_scalar_acoustic_derivatives(
        state,
        sample,
        regime=ScalarHierarchyRegime.TIGHT_COUPLING_CONTRACT,
    )
    inertia_factor = sample.typed_R.baryon_inertia_factor
    odd_even_factor = sample.typed_R.odd_even_dynamic_loading_factor

    expected_theta_b = (
        (-sample.a_prime_over_a_mpc_inv * state.theta_b)
        + sample.laplacian_k_sq_mpc_inv2 * sample.cb2 * state.delta_b
    ) / inertia_factor + sample.metric_drive.metric_euler + odd_even_factor * (
        sample.laplacian_k_sq_mpc_inv2 * (state.delta_gamma / 4.0 - sample.s2_squared * sample.thomson.shear)
        + sample.thomson.slip
    )

    assert derivatives.regime == ScalarHierarchyRegime.TIGHT_COUPLING_CONTRACT.value
    assert derivatives.photon_multipole_prime == ()
    assert derivatives.polarization_multipole_prime == ()
    assert math.isclose(derivatives.used_contract_slip or 0.0, sample.thomson.slip, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(derivatives.used_contract_shear or 0.0, sample.thomson.shear, rel_tol=0.0, abs_tol=1.0e-18)
    assert math.isclose(derivatives.theta_b_prime, expected_theta_b, rel_tol=0.0, abs_tol=1.0e-15)


def test_first_order_tca_prediction_reports_zero_residual_on_matching_contract() -> None:
    """The first-order audit should vanish when the tuple is rebuilt from its own prediction."""

    carrier, history, _, metric_drive, sample = _make_sample(slip_mid=0.0, shear_mid=0.0)
    state = ScalarHierarchyState(
        phi=0.0,
        psi=0.0,
        delta_gamma=1.5e-2,
        theta_gamma=-2.0e-2,
        delta_b=1.2e-2,
        theta_b=1.0e-2,
    )
    prediction = predict_first_order_tight_coupling_contract(state, sample)
    rebuilt_thomson = build_thomson_history_contract(
        [900.0, 1100.0, 1300.0],
        [8.0, 10.0, 14.0],
        [9.0, 11.0, 15.0],
        [-0.2, -0.3, -0.4],
        [1.0e-3, prediction.predicted_slip, 3.0e-3],
        [4.0e-4, prediction.predicted_shear, 6.0e-4],
        derivative_coordinate="conformal_time",
    )
    rebuilt_sample = build_closed_s3_scalar_acoustic_sample(
        carrier,
        history,
        rebuilt_thomson,
        index=1,
        conformal_time_mpc=0.7,
        a_prime_over_a_mpc_inv=0.08,
        a_primeprime_over_a_mpc_inv2=0.01,
        metric_drive=metric_drive,
    )
    rebuilt_prediction = predict_first_order_tight_coupling_contract(state, rebuilt_sample)

    assert math.isclose(rebuilt_prediction.slip_residual, 0.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(rebuilt_prediction.shear_residual, 0.0, rel_tol=0.0, abs_tol=1.0e-15)


def test_closed_scalar_acoustic_operator_refuses_missing_sample_and_integrates_with_shell() -> None:
    """The local operator should require an explicit sample and then work through the shell carrier."""

    carrier, history, thomson, _, sample = _make_sample()
    state = ScalarHierarchyState(
        phi=0.0,
        psi=0.0,
        delta_gamma=1.0e-2,
        theta_gamma=-1.0e-2,
        delta_b=8.0e-3,
        theta_b=6.0e-3,
        photon_multipoles=(3.0e-3, 2.0e-3),
        polarization_multipoles=(1.0e-3, 2.0e-3, 3.0e-3, 4.0e-3),
    )
    operator = ClosedS3ScalarAcousticOperator()

    with pytest.raises(OpenTheoremBoundaryError):
        operator.apply(
            make_scalar_hierarchy_step_request(carrier, state, history, thomson).perturbation_inputs,
            carrier=carrier,
            state=state,
        )

    request = make_scalar_hierarchy_step_request(carrier, state, history, thomson)
    derivatives = evolve_scalar_hierarchy_step(
        request,
        operator=operator,
        sample=sample,
        regime=ScalarHierarchyRegime.FULL_HIERARCHY,
    )
    assert derivatives.regime == ScalarHierarchyRegime.FULL_HIERARCHY.value
    assert len(derivatives.photon_multipole_prime) == 2
    assert len(derivatives.polarization_multipole_prime) == 4
