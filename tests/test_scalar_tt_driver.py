"""Checks for the scoped exploratory TT driver."""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.constants import ACTIVE_BRANCH  # noqa: E402
from aio_calculator.constants import (  # noqa: E402
    ACTIVE_BARYON_SLOTS,
    ACTIVE_IO_CONSTANTS,
    ACTIVE_PERTURBATION_PACKAGE,
    C_KM_S,
    STRICT_BARE_PERTURBATION_PACKAGE,
)
from aio_calculator.model import CurvedBackgroundModel  # noqa: E402
from aio_calculator.model import omega_gamma_h2  # noqa: E402
from aio_calculator.source_initial_conditions import build_scalar_source_shell_weight  # noqa: E402
from aio_calculator.closed_shell_power import shell_variance_prefactor  # noqa: E402
from aio_calculator.scalar_acoustic_operator import build_closed_s3_scalar_acoustic_sample  # noqa: E402
from aio_calculator.scalar_hierarchy import ScalarHierarchyState, build_scalar_hierarchy_carrier  # noqa: E402
from aio_calculator.scalar_metric_state import newtonian_constraint_phi  # noqa: E402
from aio_calculator.scalar_tt_driver import (  # noqa: E402
    ScopedTTDriverConfig,
    _build_conformal_source_visibility,
    _evolve_shell,
    _realize_first_order_tca_sample,
    _required_seed_redshift,
    _seed_start_is_early_enough,
    _stress_summary,
    _tight_coupling_active,
    _tt_shell_weight,
    build_scoped_conformal_clock,
    build_scoped_stage2_history_with_thermal_prehistory,
    build_visibility_derived_conformal_thomson_history,
    canonical_first_peak_tt_config,
    run_scoped_tt_driver,
)


def test_thermal_prehistory_extension_auto_raises_seed_start_for_high_shells() -> None:
    """The scoped prehistory extension should auto-raise `z_init` until the top shell is asymptotically safe."""

    config = ScopedTTDriverConfig(
        exact_history_samples=40,
        prehistory_samples=20,
        z_init=20000.0,
        n_max=450,
        ell_max=80,
        shell_step=4,
        observer_tau_samples=2048,
        line_of_sight_distance_samples=512,
    )
    required_z = _required_seed_redshift(
        config.n_max,
        package=config.perturbation_package,
        config=config,
    )
    assert required_z > config.z_init
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    assert staged.history.z_obs[-1] >= required_z
    assert _seed_start_is_early_enough(
        config.n_max,
        z=staged.history.z_obs[-1],
        package=config.perturbation_package,
        config=config,
    )


def test_scoped_tt_driver_runs_and_returns_finite_spectrum() -> None:
    """A reduced shell run should return a finite exploratory TT spectrum."""

    result = run_scoped_tt_driver(
        ScopedTTDriverConfig(
            exact_history_samples=40,
            prehistory_samples=16,
            z_init=8000.0,
            n_max=60,
            ell_max=80,
            shell_step=4,
            observer_tau_samples=2048,
            line_of_sight_distance_samples=512,
            peak_window_min=40,
            peak_window_max=80,
        )
    )
    assert result.claim_status == "conditional / scoped executable TT driver"
    assert result.spectrum.observable_pair == "TT"
    assert result.spectrum.ell_values[0] == 2
    assert all(math.isfinite(value) for value in result.spectrum.c_ell)
    assert result.validation.all_finite is True


def test_canonical_first_peak_tt_config_is_explicit_and_repaired() -> None:
    """The public TT helper should expose the exact canonical repaired branch."""

    config = canonical_first_peak_tt_config(shell_parallel_workers=3)
    assert config.exact_history_samples == 120
    assert config.prehistory_samples == 40
    assert config.n_max == 501
    assert config.shell_step == 1
    assert config.shell_parallel_workers == 3
    assert config.project_metric_constraint is False
    assert config.constraint_metric_source_only is True
    assert config.constraint_consistent_seed is True
    assert config.metric_baryon_momentum_slot == "eff"
    assert config.source_shell_support == "odd_plus_branch"
    assert config.source_shell_weight_interpretation == "covariance"


def test_conformal_source_visibility_uses_dtaudtau_not_dtaudz() -> None:
    """The executable LOS source leg should convert the visibility kernel to conformal time."""

    config = ScopedTTDriverConfig(
        exact_history_samples=30,
        prehistory_samples=12,
        z_init=6000.0,
        n_max=40,
        ell_max=60,
        shell_step=4,
        observer_tau_samples=1024,
        line_of_sight_distance_samples=256,
    )
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    thomson = build_visibility_derived_conformal_thomson_history(staged.history, clock)
    visibility = _build_conformal_source_visibility(staged.history, clock)
    index = len(visibility.z_obs) // 2
    expected = math.exp(-visibility.tau_obs[index]) * thomson.thomson_drag_rate[index]
    assert math.isclose(visibility.g_obs[index], expected, rel_tol=1.0e-12, abs_tol=0.0)


def test_conformal_source_visibility_applies_optical_history_factor() -> None:
    """The optical-history factor should realize `exp(-kappa)^c` and `g = c kappa' exp(-c kappa)`."""

    config = ScopedTTDriverConfig(
        exact_history_samples=30,
        prehistory_samples=12,
        z_init=6000.0,
        n_max=40,
        ell_max=60,
        shell_step=4,
        observer_tau_samples=1024,
        line_of_sight_distance_samples=256,
    )
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    opacity_factor = ACTIVE_IO_CONSTANTS.f_gamma * ACTIVE_IO_CONSTANTS.f_gamma
    visibility = _build_conformal_source_visibility(
        staged.history,
        clock,
        opacity_factor=opacity_factor,
    )
    reference = _build_conformal_source_visibility(staged.history, clock)
    drag_rate = build_visibility_derived_conformal_thomson_history(staged.history, clock).thomson_drag_rate
    index = len(visibility.z_obs) // 2
    assert math.isclose(visibility.tau_obs[index], opacity_factor * reference.tau_obs[index], rel_tol=1.0e-12, abs_tol=0.0)
    assert math.isclose(
        visibility.g_obs[index],
        opacity_factor * drag_rate[index] * math.exp(-visibility.tau_obs[index]),
        rel_tol=1.0e-12,
        abs_tol=0.0,
    )


def test_conformal_thomson_history_can_split_drag_and_hierarchy_rates() -> None:
    """The diagnostic branch should keep `tau_c` on the drag leg while splitting hierarchy damping."""

    config = ScopedTTDriverConfig(
        exact_history_samples=30,
        prehistory_samples=12,
        z_init=6000.0,
        n_max=40,
        ell_max=60,
        shell_step=4,
        observer_tau_samples=1024,
        line_of_sight_distance_samples=256,
    )
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    hierarchy_factor = ACTIVE_IO_CONSTANTS.f_gamma ** 3
    thomson = build_visibility_derived_conformal_thomson_history(
        staged.history,
        clock,
        drag_rate_factor=1.0,
        hierarchy_rate_factor=hierarchy_factor,
    )
    reference = build_visibility_derived_conformal_thomson_history(staged.history, clock)
    index = len(thomson.z_obs) // 2
    assert math.isclose(thomson.thomson_drag_rate[index], reference.thomson_drag_rate[index], rel_tol=1.0e-12, abs_tol=0.0)
    assert math.isclose(
        thomson.thomson_hierarchy_rate[index],
        hierarchy_factor * reference.thomson_hierarchy_rate[index],
        rel_tol=1.0e-12,
        abs_tol=0.0,
    )
    assert math.isclose(thomson.tau_c[index], reference.tau_c[index], rel_tol=1.0e-12, abs_tol=0.0)


def test_current_scoped_driver_does_not_yet_validate_the_first_peak() -> None:
    """The exploratory driver should report the active peak mismatch honestly."""

    result = run_scoped_tt_driver(
        ScopedTTDriverConfig(
            exact_history_samples=60,
            prehistory_samples=20,
            z_init=12000.0,
            n_max=160,
            ell_max=180,
            shell_step=8,
            observer_tau_samples=2048,
            line_of_sight_distance_samples=512,
            peak_window_min=80,
            peak_window_max=180,
        )
    )
    assert result.validation.peak_near_220 is False


def test_delta_q_shell_weight_branch_uses_closed_space_jacobian() -> None:
    """The controlled `Delta_q^2` branch should reduce the TT shell weight to `Delta_q^2/(n+1)`."""

    radius = CurvedBackgroundModel().curvature_radius_mpc
    n = 501
    source_weight = build_scalar_source_shell_weight(n).covariance_weight

    covariance_weight = _tt_shell_weight(
        n,
        radius=radius,
        config=ScopedTTDriverConfig(source_shell_weight_interpretation="covariance"),
    )
    delta_q_weight = _tt_shell_weight(
        n,
        radius=radius,
        config=ScopedTTDriverConfig(source_shell_weight_interpretation="delta_q_sq"),
    )

    assert math.isclose(
        covariance_weight,
        source_weight * shell_variance_prefactor(n, radius=radius),
        rel_tol=1.0e-12,
        abs_tol=0.0,
    )
    assert math.isclose(
        delta_q_weight,
        source_weight / (n + 1.0),
        rel_tol=1.0e-12,
        abs_tol=0.0,
    )
    assert delta_q_weight > covariance_weight


def test_default_tt_shell_support_uses_repaired_odd_plus_branch() -> None:
    """The default TT shell weight should vanish off the repaired odd-shell source support."""

    radius = CurvedBackgroundModel().curvature_radius_mpc
    config = ScopedTTDriverConfig()
    assert _tt_shell_weight(500, radius=radius, config=config) == 0.0
    assert _tt_shell_weight(501, radius=radius, config=config) > 0.0


def test_high_shell_evolution_remains_finite_after_substepping() -> None:
    """The stabilized shell stepper should carry the old `n~940` branch without overflow."""

    config = ScopedTTDriverConfig(
        exact_history_samples=120,
        prehistory_samples=40,
        z_init=20000.0,
        n_max=940,
        ell_max=180,
        shell_step=8,
        include_pressureless_matter=True,
        observer_tau_samples=4096,
        line_of_sight_distance_samples=1024,
    )
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    thomson = build_visibility_derived_conformal_thomson_history(staged.history, clock)
    states, metrics = _evolve_shell(940, staged, clock, thomson, config=config)
    terminal = states[-1]
    assert math.isfinite(terminal.phi)
    assert math.isfinite(terminal.delta_gamma)
    assert math.isfinite(metrics[-1].phi)


def test_typed_metric_stress_routes_geom_eff_and_clustering_channels() -> None:
    """The scoped metric source should keep density, momentum, and clustering legs distinct."""

    state = ScalarHierarchyState(
        phi=0.0,
        psi=0.0,
        delta_gamma=2.0,
        theta_gamma=3.0,
        delta_b=5.0,
        theta_b=7.0,
        photon_multipoles=(11.0,),
        polarization_multipoles=(),
    )
    z = 1000.0
    delta_m = 13.0
    theta_m = 17.0
    stress = _stress_summary(
        state,
        delta_ur=0.0,
        theta_ur=0.0,
        ur_multipoles=(),
        delta_m=delta_m,
        theta_m=theta_m,
        z=z,
        include_pressureless_matter=True,
    )
    h = ACTIVE_BRANCH.h
    hubble_factor = (ACTIVE_BRANCH.H0 / C_KM_S) ** 2
    rho_gamma = hubble_factor * (omega_gamma_h2(ACTIVE_BRANCH.T_cmb) / (h * h)) * (1.0 + z) ** 4
    rho_b_geom = hubble_factor * (ACTIVE_BARYON_SLOTS.omega_b_geom_h2 / (h * h)) * (1.0 + z) ** 3
    rho_b_eff = hubble_factor * (ACTIVE_BARYON_SLOTS.omega_b_eff_h2 / (h * h)) * (1.0 + z) ** 3
    rho_b_clustering = hubble_factor * (ACTIVE_BARYON_SLOTS.omega_b_clustering_h2 / (h * h)) * (1.0 + z) ** 3
    rho_pressureless = hubble_factor * max(
        ACTIVE_BRANCH.Omega_m
        - ACTIVE_BARYON_SLOTS.omega_b_geom_h2 / (h * h)
        - ACTIVE_BARYON_SLOTS.omega_b_clustering_h2 / (h * h),
        0.0,
    ) * (1.0 + z) ** 3
    assert math.isclose(
        stress.delta_rho,
        rho_gamma * state.delta_gamma + rho_b_geom * state.delta_b + (rho_b_clustering + rho_pressureless) * delta_m,
        rel_tol=1.0e-12,
        abs_tol=0.0,
    )
    assert math.isclose(
        stress.rho_plus_p_theta,
        (4.0 / 3.0) * rho_gamma * state.theta_gamma
        + rho_b_eff * state.theta_b
        + (rho_b_clustering + rho_pressureless) * theta_m,
        rel_tol=1.0e-12,
        abs_tol=0.0,
    )
    assert math.isclose(
        stress.rho_plus_p_shear,
        (8.0 / 3.0) * rho_gamma * state.photon_multipoles[0],
        rel_tol=1.0e-12,
        abs_tol=0.0,
    )
    total_density_weight = rho_b_geom + rho_b_clustering + rho_pressureless
    expected_total = hubble_factor * ACTIVE_BRANCH.Omega_m * (1.0 + z) ** 3
    assert math.isclose(total_density_weight, expected_total, rel_tol=1.0e-12, abs_tol=0.0)


def test_typed_metric_stress_uses_selected_perturbation_package() -> None:
    """The scoped stress builder should follow the carried perturbation package, not a hidden active default."""

    state = ScalarHierarchyState(
        phi=0.0,
        psi=0.0,
        delta_gamma=1.0,
        theta_gamma=1.0,
        delta_b=1.0,
        theta_b=1.0,
        photon_multipoles=(0.5,),
        polarization_multipoles=(),
    )
    z = 1000.0
    active_stress = _stress_summary(
        state,
        package=ACTIVE_PERTURBATION_PACKAGE,
        delta_ur=0.0,
        theta_ur=0.0,
        ur_multipoles=(),
        delta_m=0.0,
        theta_m=0.0,
        z=z,
        include_pressureless_matter=False,
    )
    bare_stress = _stress_summary(
        state,
        package=STRICT_BARE_PERTURBATION_PACKAGE,
        delta_ur=0.0,
        theta_ur=0.0,
        ur_multipoles=(),
        delta_m=0.0,
        theta_m=0.0,
        z=z,
        include_pressureless_matter=False,
    )
    assert not math.isclose(active_stress.delta_rho, bare_stress.delta_rho, rel_tol=1.0e-12, abs_tol=0.0)
    assert not math.isclose(active_stress.rho_plus_p_theta, bare_stress.rho_plus_p_theta, rel_tol=1.0e-12, abs_tol=0.0)


def test_constraint_enforcement_keeps_metric_phi_on_closed_newtonian_constraint() -> None:
    """Stored metric states should satisfy the closed Newtonian constraint when enforcement is on."""

    config = ScopedTTDriverConfig(
        exact_history_samples=50,
        prehistory_samples=18,
        z_init=10000.0,
        n_max=80,
        ell_max=120,
        shell_step=4,
        observer_tau_samples=2048,
        line_of_sight_distance_samples=512,
        include_pressureless_matter=True,
        project_metric_constraint=True,
    )
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    thomson = build_visibility_derived_conformal_thomson_history(staged.history, clock)
    _, metrics = _evolve_shell(80, staged, clock, thomson, config=config)
    sample_index = 3
    metric = metrics[sample_index]
    phi_constraint = newtonian_constraint_phi(
        metric.carrier,
        metric.stress,
        scale_factor=metric.scale_factor,
        a_prime_over_a_mpc_inv=metric.a_prime_over_a_mpc_inv,
    )
    assert math.isclose(metric.phi, phi_constraint, rel_tol=1.0e-12, abs_tol=1.0e-18)


def test_constraint_consistent_seed_reduces_high_z_constraint_residual() -> None:
    """The diagnostic seed switch should reduce the earliest stored high-z constraint residual."""

    base = dict(
        exact_history_samples=50,
        prehistory_samples=18,
        z_init=10000.0,
        n_max=80,
        ell_max=120,
        shell_step=4,
        observer_tau_samples=2048,
        line_of_sight_distance_samples=512,
        include_pressureless_matter=True,
        project_metric_constraint=False,
    )
    unconstrained = ScopedTTDriverConfig(constraint_consistent_seed=False, **base)
    seeded = ScopedTTDriverConfig(constraint_consistent_seed=True, **base)

    staged = build_scoped_stage2_history_with_thermal_prehistory(unconstrained)
    clock = build_scoped_conformal_clock(staged.history, config=unconstrained)
    thomson = build_visibility_derived_conformal_thomson_history(staged.history, clock)
    _, metrics_unconstrained = _evolve_shell(80, staged, clock, thomson, config=unconstrained)
    _, metrics_seeded = _evolve_shell(80, staged, clock, thomson, config=seeded)

    metric_unconstrained = metrics_unconstrained[-1]
    metric_seeded = metrics_seeded[-1]
    phi_constraint_unconstrained = newtonian_constraint_phi(
        metric_unconstrained.carrier,
        metric_unconstrained.stress,
        scale_factor=metric_unconstrained.scale_factor,
        a_prime_over_a_mpc_inv=metric_unconstrained.a_prime_over_a_mpc_inv,
    )
    phi_constraint_seeded = newtonian_constraint_phi(
        metric_seeded.carrier,
        metric_seeded.stress,
        scale_factor=metric_seeded.scale_factor,
        a_prime_over_a_mpc_inv=metric_seeded.a_prime_over_a_mpc_inv,
    )
    residual_unconstrained = abs(metric_unconstrained.phi - phi_constraint_unconstrained)
    residual_seeded = abs(metric_seeded.phi - phi_constraint_seeded)
    assert residual_seeded < residual_unconstrained


def test_constraint_metric_source_only_uses_constraint_metric_without_projecting_state() -> None:
    """The source-only diagnostic should close the metric drive while leaving the stored state free."""

    config = ScopedTTDriverConfig(
        exact_history_samples=50,
        prehistory_samples=18,
        z_init=10000.0,
        n_max=80,
        ell_max=120,
        shell_step=4,
        observer_tau_samples=2048,
        line_of_sight_distance_samples=512,
        include_pressureless_matter=True,
        project_metric_constraint=False,
        constraint_metric_source_only=True,
    )
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    thomson = build_visibility_derived_conformal_thomson_history(staged.history, clock)
    states, metrics = _evolve_shell(80, staged, clock, thomson, config=config)
    sample_index = 3
    metric = metrics[sample_index]
    state = states[sample_index]
    phi_constraint = newtonian_constraint_phi(
        metric.carrier,
        metric.stress,
        scale_factor=metric.scale_factor,
        a_prime_over_a_mpc_inv=metric.a_prime_over_a_mpc_inv,
    )
    assert math.isclose(metric.phi, phi_constraint, rel_tol=1.0e-12, abs_tol=1.0e-18)
    assert not math.isclose(state.phi, metric.phi, rel_tol=1.0e-6, abs_tol=1.0e-12)


def test_tca_branch_seeds_hidden_hierarchy_before_full_hierarchy_switch() -> None:
    """Tight coupling should carry non-zero shear/polarization into the switch."""

    config = ScopedTTDriverConfig(
        exact_history_samples=40,
        prehistory_samples=16,
        z_init=10000.0,
        n_max=80,
        ell_max=120,
        shell_step=4,
        observer_tau_samples=2048,
        line_of_sight_distance_samples=512,
    )
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    thomson = build_visibility_derived_conformal_thomson_history(staged.history, clock)
    states, _ = _evolve_shell(80, staged, clock, thomson, config=config)
    carrier = build_scalar_hierarchy_carrier(80, curvature_radius_mpc=CurvedBackgroundModel().curvature_radius_mpc)
    active_indices = [
        index
        for index, (tau_c, apoa) in enumerate(zip(thomson.tau_c, clock.a_prime_over_a_mpc_inv))
        if _tight_coupling_active(
            carrier,
            tau_c=tau_c,
            a_prime_over_a_mpc_inv=apoa,
            config=config,
        )
    ]
    high_z_index = max(active_indices)
    high_z_state = states[high_z_index]
    assert any(abs(value) > 0.0 for value in high_z_state.photon_multipoles)
    assert any(abs(value) > 0.0 for value in high_z_state.polarization_multipoles)
    transitions = [
        index
        for index in range(1, len(thomson.tau_c))
        if _tight_coupling_active(
            carrier,
            tau_c=thomson.tau_c[index - 1],
            a_prime_over_a_mpc_inv=clock.a_prime_over_a_mpc_inv[index - 1],
            config=config,
        )
        and not _tight_coupling_active(
            carrier,
            tau_c=thomson.tau_c[index],
            a_prime_over_a_mpc_inv=clock.a_prime_over_a_mpc_inv[index],
            config=config,
        )
    ]
    if transitions:
        switch_state = states[transitions[0]]
        assert any(abs(value) > 0.0 for value in switch_state.photon_multipoles)
        assert any(abs(value) > 0.0 for value in switch_state.polarization_multipoles)


def test_default_scoped_driver_realizes_nontrivial_tca_slip_and_shear() -> None:
    """The default executable TCA branch should no longer consume zero slip/shear."""

    config = ScopedTTDriverConfig(
        exact_history_samples=40,
        prehistory_samples=16,
        z_init=10000.0,
        n_max=80,
        ell_max=120,
        shell_step=4,
        observer_tau_samples=2048,
        line_of_sight_distance_samples=512,
    )
    assert config.use_first_order_tca is True

    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    thomson = build_visibility_derived_conformal_thomson_history(staged.history, clock)
    carrier = build_scalar_hierarchy_carrier(80, curvature_radius_mpc=CurvedBackgroundModel().curvature_radius_mpc)
    states, metrics = _evolve_shell(80, staged, clock, thomson, config=config)

    active_indices = [
        index
        for index, (tau_c, apoa) in enumerate(zip(thomson.tau_c, clock.a_prime_over_a_mpc_inv))
        if _tight_coupling_active(
            carrier,
            tau_c=tau_c,
            a_prime_over_a_mpc_inv=apoa,
            config=config,
        )
    ]
    sample_index = active_indices[len(active_indices) // 2]
    state = states[sample_index]
    metric = metrics[sample_index]
    sample = build_closed_s3_scalar_acoustic_sample(
        carrier,
        staged.history,
        thomson,
        index=sample_index,
        conformal_time_mpc=clock.tau_samples_mpc[sample_index],
        a_prime_over_a_mpc_inv=clock.a_prime_over_a_mpc_inv[sample_index],
        a_primeprime_over_a_mpc_inv2=clock.a_primeprime_over_a_mpc_inv2[sample_index],
        metric_drive=metric.acoustic_drive,
    )
    assert sample.thomson.slip == 0.0
    assert sample.thomson.shear == 0.0
    realized = _realize_first_order_tca_sample(state, sample)
    assert realized.thomson.slip != 0.0
    assert realized.thomson.shear != 0.0


def test_parallel_shell_driver_matches_serial_on_small_ladder() -> None:
    """Parallel shell evaluation should reproduce the serial spectrum on a small explicit ladder."""

    base = dict(
        exact_history_samples=30,
        prehistory_samples=12,
        z_init=8000.0,
        n_max=40,
        ell_max=60,
        shell_step=4,
        observer_tau_samples=512,
        line_of_sight_distance_samples=256,
        include_pressureless_matter=True,
        peak_window_min=20,
        peak_window_max=60,
    )
    serial = run_scoped_tt_driver(ScopedTTDriverConfig(shell_parallel_workers=1, **base))
    parallel = run_scoped_tt_driver(ScopedTTDriverConfig(shell_parallel_workers=2, **base))
    assert serial.spectrum.ell_values == parallel.spectrum.ell_values
    for a, b in zip(serial.spectrum.c_ell, parallel.spectrum.c_ell):
        assert math.isclose(a, b, rel_tol=1.0e-12, abs_tol=1.0e-24)
    assert serial.validation.ell_peak == parallel.validation.ell_peak


def test_tca_trigger_is_shell_dependent_on_closed_s3() -> None:
    """Higher closed shells should leave TCA earlier than low shells."""

    config = ScopedTTDriverConfig(
        exact_history_samples=60,
        prehistory_samples=20,
        z_init=12000.0,
        n_max=120,
        ell_max=120,
        shell_step=4,
        observer_tau_samples=2048,
        line_of_sight_distance_samples=512,
    )
    staged = build_scoped_stage2_history_with_thermal_prehistory(config)
    clock = build_scoped_conformal_clock(staged.history, config=config)
    thomson = build_visibility_derived_conformal_thomson_history(staged.history, clock)

    curvature_radius = CurvedBackgroundModel().curvature_radius_mpc
    shell_120 = build_scalar_hierarchy_carrier(120, curvature_radius_mpc=curvature_radius)
    shell_376 = build_scalar_hierarchy_carrier(376, curvature_radius_mpc=curvature_radius)
    active_120 = [
        index
        for index, (tau_c, apoa) in enumerate(zip(thomson.tau_c, clock.a_prime_over_a_mpc_inv))
        if _tight_coupling_active(shell_120, tau_c=tau_c, a_prime_over_a_mpc_inv=apoa, config=config)
    ]
    active_376 = [
        index
        for index, (tau_c, apoa) in enumerate(zip(thomson.tau_c, clock.a_prime_over_a_mpc_inv))
        if _tight_coupling_active(shell_376, tau_c=tau_c, a_prime_over_a_mpc_inv=apoa, config=config)
    ]
    assert active_120
    assert active_376
    assert thomson.z_obs[min(active_376)] > thomson.z_obs[min(active_120)]
