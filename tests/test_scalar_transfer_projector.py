"""Checks for the closed-`S^3` scalar hierarchy-to-transfer projector."""

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
    build_visibility_packet,
)
from aio_calculator.constants import ACTIVE_BRANCH_THETA_STAR_SELECTOR_Z  # noqa: E402
from aio_calculator.model import CurvedBackgroundModel  # noqa: E402
from aio_calculator.scalar_hierarchy import (  # noqa: E402
    ScalarHierarchyState,
    build_scalar_hierarchy_carrier,
)
from aio_calculator.scalar_metric_state import (  # noqa: E402
    build_newtonian_scalar_metric_state,
    build_scalar_stress_energy_summary,
    build_synchronous_scalar_metric_state,
)
from aio_calculator.scalar_transfer_projector import (  # noqa: E402
    build_newtonian_scalar_source_history,
    build_newtonian_scalar_source_history_integrated_by_parts,
    build_synchronous_scalar_source_history,
    evaluate_closed_s3_scalar_radial_chain,
    project_closed_s3_scalar_e_polarization,
    project_closed_s3_scalar_temperature,
)


def _make_visibility(z_values: list[float]) -> tuple[Stage2History, object]:
    """Return one exact local history plus its observer visibility packet."""

    history = Stage2History.from_sequences(
        z_values,
        [1.0, 0.5, 0.1],
        [3200.0, 3000.0, 2600.0],
    )
    return history, build_visibility_packet(history)


def _make_states() -> tuple[ScalarHierarchyState, ...]:
    """Return one explicit scalar hierarchy history."""

    return (
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


def _make_newtonian_metric_history(carrier) -> tuple[object, ...]:
    """Return one explicit Newtonian-gauge metric history."""

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
    phi_values = (2.0e-4, 2.2e-4, 2.4e-4)
    return tuple(
        build_newtonian_scalar_metric_state(
            carrier,
            stress,
            scale_factor=0.02,
            a_prime_over_a_mpc_inv=0.4,
            phi=phi,
        )
        for stress, phi in zip(stresses, phi_values)
    )


def _make_synchronous_metric_history(carrier) -> tuple[object, ...]:
    """Return one explicit synchronous-gauge metric history."""

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
    eta_values = (3.0e-4, 3.3e-4, 3.6e-4)
    return tuple(
        build_synchronous_scalar_metric_state(
            carrier,
            stress,
            scale_factor=0.02,
            a_prime_over_a_mpc_inv=0.4,
            eta=eta,
        )
        for stress, eta in zip(stresses, eta_values)
    )


def test_newtonian_scalar_source_history_matches_transparent_closed_formulas() -> None:
    """The Newtonian source carrier should expose the exact transparent LOS formulas."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    _, visibility = _make_visibility([0.0, 500.0, 1100.0])
    states = _make_states()
    metric_states = _make_newtonian_metric_history(carrier)
    source_history = build_newtonian_scalar_source_history(
        carrier,
        conformal_time_mpc=[0.2, 0.4, 0.6],
        visibility=visibility,
        states=states,
        metric_states=metric_states,
    )

    n = carrier.mode.n
    s2 = math.sqrt((n - 1.0) * (n + 3.0) / (n * (n + 2.0)))
    laplacian_k = math.sqrt(n * (n + 2.0)) / carrier.curvature_radius_mpc
    index = 1
    p_source = (
        states[index].polarization_multipoles[0]
        + states[index].polarization_multipoles[2]
        + 2.0 * s2 * states[index].photon_multipoles[0]
    ) / 8.0
    expected_0 = math.exp(-visibility.tau_obs[index]) * metric_states[index].phi_prime + visibility.g_obs[index] * states[index].delta_gamma / 4.0
    expected_1 = math.exp(-visibility.tau_obs[index]) * laplacian_k * metric_states[index].psi + visibility.g_obs[index] * states[index].theta_b / laplacian_k
    expected_2 = visibility.g_obs[index] * p_source

    assert source_history.gauge == "newtonian"
    assert math.isclose(source_history.temperature_source_0[index], expected_0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.temperature_source_1[index], expected_1, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.temperature_source_2[index], expected_2, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.polarization_source[index], expected_2, rel_tol=0.0, abs_tol=1.0e-15)


def test_synchronous_scalar_source_history_matches_transparent_closed_formulas() -> None:
    """The synchronous source carrier should expose the exact transparent LOS formulas."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    _, visibility = _make_visibility([0.0, 500.0, 1100.0])
    states = _make_states()
    metric_states = _make_synchronous_metric_history(carrier)
    source_history = build_synchronous_scalar_source_history(
        carrier,
        conformal_time_mpc=[0.2, 0.4, 0.6],
        visibility=visibility,
        states=states,
        metric_states=metric_states,
    )

    n = carrier.mode.n
    s2 = math.sqrt((n - 1.0) * (n + 3.0) / (n * (n + 2.0)))
    laplacian_k = math.sqrt(n * (n + 2.0)) / carrier.curvature_radius_mpc
    index = 1
    p_source = (
        states[index].polarization_multipoles[0]
        + states[index].polarization_multipoles[2]
        + 2.0 * s2 * states[index].photon_multipoles[0]
    ) / 8.0
    expected_0 = -math.exp(-visibility.tau_obs[index]) * metric_states[index].h_prime / 6.0 + visibility.g_obs[index] * states[index].delta_gamma / 4.0
    expected_1 = visibility.g_obs[index] * states[index].theta_b / laplacian_k
    expected_2 = math.exp(-visibility.tau_obs[index]) * laplacian_k * laplacian_k * (2.0 / 3.0) * s2 * metric_states[index].alpha + visibility.g_obs[index] * p_source

    assert source_history.gauge == "synchronous"
    assert math.isclose(source_history.temperature_source_0[index], expected_0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.temperature_source_1[index], expected_1, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.temperature_source_2[index], expected_2, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.polarization_source[index], visibility.g_obs[index] * p_source, rel_tol=0.0, abs_tol=1.0e-15)


def test_newtonian_integrated_source_history_matches_ibp_closed_formulas() -> None:
    """The integrated Newtonian source carrier should expose the IBP LOS formulas."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    _, visibility = _make_visibility([0.0, 500.0, 1100.0])
    states = _make_states()
    metric_states = _make_newtonian_metric_history(carrier)
    tau_grid = [0.2, 0.4, 0.6]
    source_history = build_newtonian_scalar_source_history_integrated_by_parts(
        carrier,
        conformal_time_mpc=tau_grid,
        visibility=visibility,
        states=states,
        metric_states=metric_states,
    )

    n = carrier.mode.n
    s2 = math.sqrt((n - 1.0) * (n + 3.0) / (n * (n + 2.0)))
    laplacian_k = math.sqrt(n * (n + 2.0)) / carrier.curvature_radius_mpc
    laplacian_k_sq = laplacian_k * laplacian_k
    index = 1
    g_prime = (visibility.g_obs[2] - visibility.g_obs[0]) / (tau_grid[2] - tau_grid[0])
    theta_b_prime = (states[2].theta_b - states[0].theta_b) / (tau_grid[2] - tau_grid[0])
    p_source = (
        states[index].polarization_multipoles[0]
        + states[index].polarization_multipoles[2]
        + 2.0 * s2 * states[index].photon_multipoles[0]
    ) / 8.0
    expected_0 = (
        visibility.g_obs[index] * (states[index].delta_gamma / 4.0 + metric_states[index].psi)
        + (g_prime * states[index].theta_b + visibility.g_obs[index] * theta_b_prime) / laplacian_k_sq
        + visibility.g_obs[index] * (metric_states[index].phi - metric_states[index].psi)
        + 2.0 * math.exp(-visibility.tau_obs[index]) * metric_states[index].phi_prime
    )
    expected_1 = math.exp(-visibility.tau_obs[index]) * laplacian_k * (metric_states[index].psi - metric_states[index].phi)
    expected_2 = visibility.g_obs[index] * p_source

    assert source_history.gauge == "newtonian"
    assert math.isclose(source_history.temperature_source_0[index], expected_0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.temperature_source_1[index], expected_1, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.temperature_source_2[index], expected_2, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(source_history.polarization_source[index], expected_2, rel_tol=0.0, abs_tol=1.0e-15)


def test_closed_scalar_radial_chain_matches_exact_ell0_formula() -> None:
    """The radial chain should reproduce the exact `ell=0` closed-shell identities."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    chi = 0.37
    beta = carrier.mode.n + 1
    radial = evaluate_closed_s3_scalar_radial_chain(carrier, ell=0, chi=chi)

    phi = math.sin(beta * chi) / (beta * math.sin(chi))
    dphi = math.cos(beta * chi) / math.sin(chi) - math.sin(beta * chi) * math.cos(chi) / (beta * math.sin(chi) ** 2)
    d2phi = -2.0 * (math.cos(chi) / math.sin(chi)) * dphi + (-beta * beta + 1.0) * phi

    assert math.isclose(radial.phi, phi, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(radial.dphi_dchi, dphi, rel_tol=0.0, abs_tol=2.0e-15)
    assert math.isclose(radial.d2phi_dchi2, d2phi, rel_tol=0.0, abs_tol=2.0e-14)


def test_temperature_projector_matches_manual_ell0_trapezoid() -> None:
    """The temperature projector should equal the explicit `ell=0` trapezoid sum."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    _, visibility = _make_visibility([0.0, 500.0, 1100.0])
    states = _make_states()
    metric_states = _make_newtonian_metric_history(carrier)
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

    n = carrier.mode.n
    laplacian_k_sq = n * (n + 2.0) / carrier.curvature_radius_mpc**2
    curvature_k = 1.0 / carrier.curvature_radius_mpc**2
    s2 = math.sqrt((n - 1.0) * (n + 3.0) / (n * (n + 2.0)))
    sqrtk_over_k = math.sqrt(curvature_k / laplacian_k_sq)
    prefactor2 = 3.0 * curvature_k / laplacian_k_sq
    beta = n + 1
    chi_values = tuple((0.9 - tau) / carrier.curvature_radius_mpc for tau in source_history.conformal_time_mpc)

    integrand = []
    for source_0, source_1, source_2, chi in zip(
        source_history.temperature_source_0,
        source_history.temperature_source_1,
        source_history.temperature_source_2,
        chi_values,
    ):
        phi = math.sin(beta * chi) / (beta * math.sin(chi))
        dphi = math.cos(beta * chi) / math.sin(chi) - math.sin(beta * chi) * math.cos(chi) / (beta * math.sin(chi) ** 2)
        d2phi = -2.0 * (math.cos(chi) / math.sin(chi)) * dphi + (-beta * beta + 1.0) * phi
        radial2 = (prefactor2 * d2phi + phi) / (2.0 * s2)
        integrand.append(source_0 * phi + source_1 * sqrtk_over_k * dphi + source_2 * radial2)

    expected = 0.0
    tau = source_history.conformal_time_mpc
    for tau0, tau1, y0, y1 in zip(tau, tau[1:], integrand, integrand[1:]):
        expected += 0.5 * (y0 + y1) * (tau1 - tau0)

    assert packet.observable.value == "T"
    assert packet.ell_values == (0,)
    assert math.isclose(packet.delta_l[0].real, expected, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(packet.delta_l[0].imag, 0.0, rel_tol=0.0, abs_tol=1.0e-18)


def test_projector_rejects_relative_visibility_packets() -> None:
    """The projector should refuse packets not measured to the observer boundary."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    _, visibility = _make_visibility([500.0, 900.0, 1100.0])
    states = _make_states()
    metric_states = _make_newtonian_metric_history(carrier)
    with pytest.raises(OpenTheoremBoundaryError):
        build_newtonian_scalar_source_history(
            carrier,
            conformal_time_mpc=[0.2, 0.4, 0.6],
            visibility=visibility,
            states=states,
            metric_states=metric_states,
        )


def test_e_projector_sets_subquadrupole_multipoles_to_zero() -> None:
    """Scalar E-polarization should vanish identically for `ell < 2`."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    _, visibility = _make_visibility([0.0, 500.0, 1100.0])
    states = _make_states()
    metric_states = _make_newtonian_metric_history(carrier)
    source_history = build_newtonian_scalar_source_history(
        carrier,
        conformal_time_mpc=[0.2, 0.4, 0.6],
        visibility=visibility,
        states=states,
        metric_states=metric_states,
    )
    packet = project_closed_s3_scalar_e_polarization(
        source_history,
        tau_observer_mpc=0.9,
        ell_values=[0, 1, 2],
    )
    assert packet.observable.value == "E"
    assert packet.ell_values == (0, 1, 2)
    assert packet.delta_l[0] == 0.0
    assert packet.delta_l[1] == 0.0


def test_closed_scalar_radial_chain_matches_class_reference_values_on_active_branch() -> None:
    """The closed projector should reproduce CLASS non-flat hyperspherical values."""

    model = CurvedBackgroundModel()
    chi_star = math.sqrt(-model.branch.Omega_k) * model.chi_dimless(ACTIVE_BRANCH_THETA_STAR_SELECTOR_Z)

    references = (
        (
            220,
            129,
            0.01491355710129287,
            -0.05572231127540558,
            -40.32823266428252,
        ),
        (
            320,
            189,
            0.01093576012008138,
            -0.01284196600318768,
            -46.654496651680745,
        ),
        (
            320,
            220,
            1.722052573561614e-08,
            3.042306121014527e-06,
            5.204404838094886e-04,
        ),
    )

    for n, ell, phi_ref, dphi_ref, d2phi_ref in references:
        carrier = build_scalar_hierarchy_carrier(n, curvature_radius_mpc=model.curvature_radius_mpc)
        radial = evaluate_closed_s3_scalar_radial_chain(carrier, ell=ell, chi=chi_star)
        assert math.isclose(radial.phi, phi_ref, rel_tol=1.0e-12, abs_tol=0.0)
        assert math.isclose(radial.dphi_dchi, dphi_ref, rel_tol=1.0e-12, abs_tol=0.0)
        assert math.isclose(radial.d2phi_dchi2, d2phi_ref, rel_tol=1.0e-12, abs_tol=0.0)


def test_active_branch_closed_projection_maps_shell_220_to_mid_ell_not_to_ell_220() -> None:
    """The closed `S^3` projector should peak shell 220 near the carried `nu sin chi_*` scale."""

    model = CurvedBackgroundModel()
    chi_star = math.sqrt(-model.branch.Omega_k) * model.chi_dimless(ACTIVE_BRANCH_THETA_STAR_SELECTOR_Z)
    carrier = build_scalar_hierarchy_carrier(220, curvature_radius_mpc=model.curvature_radius_mpc)

    phi_abs = [
        abs(evaluate_closed_s3_scalar_radial_chain(carrier, ell=ell, chi=chi_star).phi)
        for ell in range(carrier.ell_min, carrier.ell_max + 1)
    ]
    ell_values = list(range(carrier.ell_min, carrier.ell_max + 1))
    ell_peak = ell_values[max(range(len(phi_abs)), key=phi_abs.__getitem__)]
    expected_scale = (carrier.mode.n + 1) * math.sin(chi_star)

    assert ell_peak == 129
    assert abs(ell_peak - expected_scale) < 6.0
    assert ell_peak < 180
