"""Checks for the theorem dictionary and explained-output layer."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator import (  # noqa: E402
    explain_active_t_cmb,
    explain_active_branch_theta_star,
    explain_branch_rd_mpc,
    explain_branch_h0,
    explain_branch_omega_k,
    explain_branch_omega_lambda,
    explain_branch_omega_m,
    explain_bare_master_clock_age,
    explain_baryon_fraction_fb,
    explain_bbn_deuterium_ratio,
    explain_bbn_helium_fraction,
    explain_bbn_lithium_ratio,
    explain_eta_io_late,
    explain_background_snapshot,
    explain_native_scalar_amplitude_as,
    explain_recombination_point,
    explain_scalar_tilt_ns,
    explained_output_specs,
    theorem_graph,
)


def test_theta_star_explained_output_carries_full_chain() -> None:
    """The first explained output should ship the accepted theta_* theorem chain."""

    explained = explain_active_branch_theta_star().as_dict()
    assert explained["claim_status"].startswith("derived / scoped")
    assert explained["provenance_status"] == "full"
    assert explained["zero_fitted_parameters"] is True
    assert explained["conditional_on_premises"] == ["premise.1", "premise.2"]
    assert math.isclose(
        explained["theta_star_100"],
        1.048683904878751,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert explained["provenance"]["root_node"] == "calculator.active_branch_theta_star"
    assert explained["provenance"]["chain_ids"] == [
        "premise.1",
        "premise.2",
        "paper21.branch_assignment",
        "calculator.phase_equivalent_selector",
        "calculator.packet_coefficient_fixing",
        "calculator.highz_tail_slaving",
        "calculator.peak_window_tail_profile_audit",
        "calculator.selector_support_promotion",
        "calculator.active_branch_theta_star",
    ]
    theta_node = explained["provenance"]["nodes"]["calculator.active_branch_theta_star"]
    assert theta_node["label"] == "Active-branch Theta-star Theorem"
    assert theta_node["premises"] == [
        "`calculator.selector_support_promotion` fixes the carried physical selector leaf on the active branch.",
        "`calculator.phase_equivalent_selector` gives the exact observer-side map from that leaf to `theta_*`.",
    ]
    assert len(theta_node["proof_outline"]) == 3
    assert theta_node["scope_boundary"][0] == "Fixed active Paper 10 legacy projected branch only."
    assert theta_node["reference_note"].startswith("Supporting references only.")
    assert "`100theta_* = 1.048683904879`" in theta_node["statement"]
    comparison = explained["direct_observable_comparison"]
    assert math.isclose(
        comparison["predicted_value"],
        220.47514473507064,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert math.isclose(
        comparison["observed_reference"],
        220.0,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert "Planck assumes flat space" in explained["geometry_explanation"]


def test_recombination_explained_output_becomes_conditional_with_override() -> None:
    """Supplying `x_e` should change the chemistry-dependent rows to conditional."""

    explained = explain_recombination_point(1100.0, x_e_override=0.1).as_dict()
    assert explained["claim_status"].startswith("conditional")
    assert explained["provenance_status"] == "full"
    assert explained["zero_fitted_parameters"] is False
    assert explained["provenance"]["chain_ids"] == [
        "premise.1",
        "premise.2",
        "paper21.branch_assignment",
        "paper31.baryon_assignment",
        "paper29.sound_speed_selector",
        "paper31.local_background_state_map",
        "paper31.recombination_clock_transport",
    ]


def test_branch_rd_explained_output_carries_full_chain() -> None:
    """The active-branch `r_d` output should ship a full theorem chain."""

    explained = explain_branch_rd_mpc().as_dict()
    assert explained["provenance_status"] == "full"
    assert math.isclose(
        explained["r_d_mpc"],
        144.01351425392883,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert explained["provenance"]["chain_ids"] == [
        "premise.1",
        "premise.2",
        "paper21.branch_assignment",
        "paper29.sound_speed_selector",
        "paper31.geometric_pre_drag_ruler",
    ]
    selector = explained["provenance"]["nodes"]["paper29.sound_speed_selector"]
    assert "`R(z) = 3 rho_b(z) / [4 rho_gamma(z)]`" in selector["statement"]
    assert "omega_b,geom" in selector["statement"]


def test_eta_io_explained_output_carries_full_chain() -> None:
    """The late-time `eta_IO` output should ship a full theorem chain."""

    explained = explain_eta_io_late().as_dict()
    assert explained["provenance_status"] == "full"
    assert math.isclose(
        explained["eta_IO_late"],
        5.748778515173696e-10,
        rel_tol=0.0,
        abs_tol=1.0e-22,
    )
    assert explained["provenance"]["chain_ids"] == [
        "premise.1",
        "premise.2",
        "paper21.branch_assignment",
        "paper35.late_baryon_counting_law",
        "paper35.eta_io_late_closure",
    ]
    baryon_law = explained["provenance"]["nodes"]["paper35.late_baryon_counting_law"]
    assert baryon_law["authority_paths"] == []
    assert "`n_b = rho_b / m_bar" in baryon_law["statement"]
    closure = explained["provenance"]["nodes"]["paper35.eta_io_late_closure"]
    assert closure["label"] == "Late-time eta_IO Closure Theorem"
    assert "`eta_IO,late = C_eta(T_obs, m_bar) * omega_b,geom`" in closure["statement"]


def test_active_branch_parameter_cards_carry_full_chain() -> None:
    """The active branch package cards should point back to the carried runtime package."""

    h0 = explain_branch_h0().as_dict()
    om = explain_branch_omega_m().as_dict()
    ok = explain_branch_omega_k().as_dict()
    ol = explain_branch_omega_lambda().as_dict()
    tcmb = explain_active_t_cmb().as_dict()

    assert math.isclose(h0["H0_km_s_mpc"], 67.57585653582628, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(om["Omega_m"], 0.34868395067621694, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(ok["Omega_k"], -0.04579112576013168, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(ol["Omega_Lambda"], 0.69701575761593, rel_tol=0.0, abs_tol=1.0e-15)
    assert h0["provenance"]["chain_ids"] == [
        "premise.1",
        "premise.2",
        "paper21.branch_assignment",
        "paper30.active_branch_parameter_package",
    ]
    assert tcmb["provenance"]["chain_ids"] == [
        "premise.1",
        "premise.2",
        "paper17.gttp_thermal_readout",
        "paper21.branch_assignment",
        "paper30.active_branch_parameter_package",
    ]
    assert math.isclose(tcmb["T_CMB_K"], 2.7253, rel_tol=0.0, abs_tol=1.0e-12)
    thermal = tcmb["provenance"]["nodes"]["paper17.gttp_thermal_readout"]
    assert "`T_obs = T_IO x^K_gauge`" in thermal["statement"]
    package = h0["provenance"]["nodes"]["paper30.active_branch_parameter_package"]
    assert "`H0 = 67.575856535826 km/s/Mpc`" in package["statement"]


def test_bare_clock_scalar_and_bbn_cards_preserve_status_and_formulas() -> None:
    """The new cards should keep the archive's honest split between derived and conditional."""

    bare_age = explain_bare_master_clock_age().as_dict()
    ns = explain_scalar_tilt_ns().as_dict()
    amp = explain_native_scalar_amplitude_as().as_dict()
    fb = explain_baryon_fraction_fb().as_dict()
    dh = explain_bbn_deuterium_ratio().as_dict()
    yp = explain_bbn_helium_fraction().as_dict()
    li = explain_bbn_lithium_ratio().as_dict()

    assert math.isclose(
        bare_age["age_bare_gyr"],
        19.181055510108134,
        rel_tol=0.0,
        abs_tol=1.0e-9,
    )
    assert bare_age["provenance"]["root_node"] == "paper30.bare_master_clock"
    assert "`t_bare(z) = integral_z^infinity dz' / [(1+z') H_bare(z')]`" in bare_age["provenance"]["nodes"][
        "paper30.bare_master_clock"
    ]["statement"]

    assert ns["claim_status"].startswith("conditional / scoped")
    assert ns["provenance"]["root_node"] == "paper28.boundary_fixed_point_scalar_tilt"
    assert "`n_s = 1 - K_gauge / x = 0.9639`" in ns["provenance"]["nodes"][
        "paper28.boundary_fixed_point_scalar_tilt"
    ]["statement"]

    assert amp["claim_status"].startswith("derived / scoped")
    assert math.isclose(amp["A_s"], 2.0072459972737347e-9, rel_tol=0.0, abs_tol=1.0e-24)
    assert "`A_s = (25/9) [gamma^2 / (1 + gamma^2)] [1 / sqrt(2)] [exp(4 pi sqrt(2)) - 1]^-1`" in amp[
        "provenance"
    ]["nodes"]["paper32.modular_dtn_field_transfer"]["statement"]

    assert math.isclose(fb["f_b"], 0.3127083362150252, rel_tol=0.0, abs_tol=1.0e-15)
    assert fb["provenance"]["root_node"] == "paper12.baryon_dictionary_fraction"
    assert "`f_b = 2 gamma_BI / x = 0.312708336215025`" in fb["provenance"]["nodes"][
        "paper12.baryon_dictionary_fraction"
    ]["statement"]

    assert math.isclose(dh["D_H_ratio"], 2.509e-05, rel_tol=0.0, abs_tol=1.0e-16)
    assert math.isclose(yp["Y_p"], 0.2477, rel_tol=0.0, abs_tol=1.0e-12)
    assert li["claim_status"].startswith("conditional / scoped")
    assert math.isclose(li["Li7_H_ratio"], 1.7500878203658553e-10, rel_tol=0.0, abs_tol=1.0e-24)
    assert li["provenance"]["root_node"] == "paper24.conditional_lithium_scorecard"


def test_background_snapshot_explained_output_carries_full_chain() -> None:
    """The parameterized background snapshot should ship a full theorem chain."""

    explained = explain_background_snapshot(0.57).as_dict()
    assert explained["provenance_status"] == "full"
    assert math.isclose(
        explained["DM_mpc"],
        2165.6006007820824,
        rel_tol=0.0,
        abs_tol=1.0e-9,
    )
    assert explained["provenance"]["chain_ids"] == [
        "premise.1",
        "premise.2",
        "paper21.branch_assignment",
        "paper30.background_surface",
        "paper29.sound_speed_selector",
        "paper31.geometric_pre_drag_ruler",
    ]
    background = explained["provenance"]["nodes"]["paper30.background_surface"]
    assert "`H(z) = H_0 sqrt[Omega_r (1+z)^4 + Omega_m (1+z)^3 + Omega_k (1+z)^2 + Omega_Lambda]`" in background["statement"]


def test_tt_provenance_nodes_are_present_and_scoped_honestly() -> None:
    """The TT carrier and canonical first-peak support nodes should be explicit."""

    graph = theorem_graph()
    driver = graph["local.scoped_tt_driver"].as_dict()
    first_peak = graph["local.scoped_tt_first_peak_support"].as_dict()

    assert driver["claim_status"] == "conditional / scoped"
    assert "one common early-time carrier" in driver["statement"]
    assert "high-shell source/phase frontier remains open" in driver["proof_outline"][-1]

    assert (
        first_peak["claim_status"]
        == "Conditional/scoped/verified TT first-peak support on the repaired active-branch canonical carrier (n_max = 501), with inherited-FULL Stage-2 history and equal-rate typed Thomson specialization."
    )
    assert "`ell_peak = 224`" in first_peak["statement"]
    assert "`n_max >= 601`" in first_peak["scope_boundary"][-1]
    assert first_peak["authority_paths"]


def test_recombination_explained_output_carries_full_chain() -> None:
    """The default recombination primitives should ship a full theorem chain."""

    explained = explain_recombination_point(1100.0).as_dict()
    assert explained["provenance_status"] == "full"
    assert explained["provenance"]["chain_ids"] == [
        "premise.1",
        "premise.2",
        "paper21.branch_assignment",
        "paper31.baryon_assignment",
        "paper29.sound_speed_selector",
        "paper31.local_background_state_map",
        "local.saha_seed",
        "paper31.recombination_clock_transport",
    ]
    saha = explained["provenance"]["nodes"]["local.saha_seed"]
    assert saha["authority_paths"] == []
    assert "`x_e^2/(1-x_e) =" in saha["statement"]
    baryon = explained["provenance"]["nodes"]["paper31.baryon_assignment"]
    assert "`kappa'_loc = a_loc n_e sigma_T`" in baryon["statement"]


def test_provenance_specs_and_graph_expose_theta_and_scaffolds() -> None:
    """The theorem dictionary should expose full published outputs and theorem nodes."""

    specs = explained_output_specs()
    graph = theorem_graph()
    assert specs["theta_star_theorem"]["provenance_status"] == "full"
    assert specs["tt_first_peak_support"]["provenance_status"] == "full"
    assert specs["branch_rd_mpc"]["provenance_status"] == "full"
    assert specs["branch_h0"]["provenance_status"] == "full"
    assert specs["branch_omega_m"]["provenance_status"] == "full"
    assert specs["branch_omega_k"]["provenance_status"] == "full"
    assert specs["branch_omega_lambda"]["provenance_status"] == "full"
    assert specs["active_t_cmb"]["provenance_status"] == "full"
    assert specs["bare_master_clock_age"]["provenance_status"] == "full"
    assert specs["scalar_tilt_ns"]["provenance_status"] == "full"
    assert specs["native_scalar_amplitude_as"]["provenance_status"] == "full"
    assert specs["bbn_deuterium_ratio"]["provenance_status"] == "full"
    assert specs["bbn_helium_fraction"]["provenance_status"] == "full"
    assert specs["bbn_lithium_ratio"]["provenance_status"] == "full"
    assert specs["baryon_fraction_fb"]["provenance_status"] == "full"
    assert specs["eta_io_late"]["provenance_status"] == "full"
    assert specs["background_snapshot"]["provenance_status"] == "full"
    assert specs["recombination_point"]["provenance_status"] == "full"
    assert "paper12.baryon_dictionary_fraction" in graph
    assert "paper17.gttp_thermal_readout" in graph
    assert "paper28.boundary_fixed_point_scalar_tilt" in graph
    assert "paper30.active_branch_parameter_package" in graph
    assert "paper30.bare_master_clock" in graph
    assert "paper30.deuterium_scorecard" in graph
    assert "paper30.primordial_helium_scorecard" in graph
    assert "paper24.conditional_lithium_scorecard" in graph
    assert "calculator.active_branch_theta_star" in graph
    assert graph["paper12.baryon_dictionary_fraction"].label == "Paper 12 Baryon Dictionary Fraction Theorem"
    assert "`f_b = 2 gamma_BI / x = 0.312708336215025`" in graph[
        "paper12.baryon_dictionary_fraction"
    ].statement
    assert graph["paper17.gttp_thermal_readout"].label == "Paper 17 GTTP Thermal Readout Theorem"
    assert "`T_obs = T_IO x^K_gauge`" in graph["paper17.gttp_thermal_readout"].statement
    assert graph["paper28.boundary_fixed_point_scalar_tilt"].claim_status == "conditional / scoped"
    assert "`n_s = 1 - K_gauge / x = 0.9639`" in graph[
        "paper28.boundary_fixed_point_scalar_tilt"
    ].statement
    assert graph["paper30.active_branch_parameter_package"].label == "Paper 30 Active-branch Parameter Package"
    assert "`Omega_k = -0.045791125760`" in graph["paper30.active_branch_parameter_package"].statement
    assert graph["paper30.bare_master_clock"].label == "Paper 30 Bare Master-clock Theorem"
    assert "`t_bare(a) = H0_bare^-1 integral_0^a da' / sqrt(Omega_r + Omega_m a' + Omega_k a'^2 + Omega_Lambda a'^4)`" in graph[
        "paper30.bare_master_clock"
    ].statement
    assert graph["paper24.conditional_lithium_scorecard"].claim_status == "conditional / scoped"
    assert "`Li-7/H = 1.750087820365855e-10`" in graph[
        "paper24.conditional_lithium_scorecard"
    ].statement
    assert graph["paper32.closed_s3_solver_spec"].claim_status.startswith("derived / scoped")
    assert "local.typed_r_operator" in graph
    assert graph["local.typed_r_operator"].claim_status == "derived / scoped as maps"
    assert graph["local.typed_r_operator"].label == "Full Typed R Hierarchy Operator Theorem"
    assert "accepted equal-rate scoped branch" in graph["local.typed_r_operator"].statement
    assert "`Gamma_bgamma = R_local,geom thomson_drag_rate = R_local,geom / tau_c`" in graph["local.typed_r_operator"].statement
    assert "`L_odd/even = R_local,geom / (1 + R_local,geom)`" in graph["local.typed_r_operator"].statement
    assert "equal-rate scoped branch" in graph["local.typed_r_operator"].scope.lower()
    assert (
        "Conditional/scoped/verified TT first-peak support on the repaired active-branch canonical carrier (n_max = 501), with inherited-FULL Stage-2 history and equal-rate typed Thomson specialization."
        == graph["local.scoped_tt_first_peak_support"].claim_status
    )
    assert "local.typed_r_site_uniqueness" in graph
    assert graph["local.typed_r_site_uniqueness"].label == "Typed R Site-uniqueness Theorem"
    assert "accepted equal-rate scoped branch" in graph["local.typed_r_site_uniqueness"].statement
    assert "`D_visc = 16 / [90 (1+R_local,geom) thomson_hierarchy_rate]`" in graph[
        "local.typed_r_site_uniqueness"
    ].statement
    assert "local.typed_thomson_split_history_realization" in graph
    assert graph["local.typed_thomson_split_history_realization"].label == "Typed Split Thomson-history Realization Theorem"
    assert "accepted equal-rate scoped conformal tuple" in graph[
        "local.typed_thomson_split_history_realization"
    ].statement
    assert "`thomson_drag_rate = |(d tau_obs / dz) / (dC / dz)|`" in graph[
        "local.typed_thomson_split_history_realization"
    ].statement
    assert graph["paper32.typed_baryon_slot_spec"].statement.endswith(
        "No silent one-slot collapse on `R` is licensed anywhere in the perturbation pipeline."
    )
    assert graph["premise.1"].scope_boundary[0].startswith("Applies only as a lab working assumption")
    assert len(graph["calculator.phase_equivalent_selector"].proof_outline) == 3
    assert graph["calculator.phase_equivalent_selector"].label == "Phase-equivalent Selector Theorem"
    assert "`theta_bare(z_sel) = r_s(z_sel) / D_M(z_sel)`" in graph["calculator.phase_equivalent_selector"].statement
    assert graph["calculator.packet_coefficient_fixing"].label == "Packet Coefficient Fixing Theorem"
    assert "`xr[1] = 3 x1s Dfplus_Ly[0]`" in graph["calculator.packet_coefficient_fixing"].statement
    assert graph["calculator.highz_tail_slaving"].label == "High-z Tail Slaving Theorem"
    assert graph["paper35.late_baryon_counting_law"].authority_paths == ()
    assert graph["paper31.local_background_state_map"].premises[1].startswith(
        "`paper31.baryon_assignment`"
    )
    assert graph["paper22.spatial_mode_ladder"].label == "Paper 22 Spatial Mode Ladder"
    assert "`lambda_n^(S) = n(n+2) / a^2`" in graph["paper22.spatial_mode_ladder"].statement
    assert graph["paper23.closed_scalar_operator"].label == "Paper 23 Closed Scalar Operator Theorem"
    assert "`lambda_n - 3 = (n-1)(n+3)`" in graph["paper23.closed_scalar_operator"].statement
    assert graph["paper28.closed_s3_shell_power"].label == "Paper 28 Closed S^3 Shell-power Definition"
    assert "`Delta_MS^2(n) = (((n-1)(n+1)(n+3)) / (2 pi^2 R^3)) P_X(n)`" in graph[
        "paper28.closed_s3_shell_power"
    ].statement
    assert graph["paper32.modular_dtn_field_transfer"].label == "Paper 32 Modular-DtN Field Transfer"
    assert "`P_src = B_+ o U_coex o T_field`" in graph["paper32.modular_dtn_field_transfer"].statement
    assert graph["paper32.typed_baryon_slot_spec"].label == "Typed Baryon-slot Specification"
    assert "reduced visibility/readout `omega_b,eff`" in graph["paper32.typed_baryon_slot_spec"].statement
    assert graph["paper31.stage2_markov_state"].label == "Paper 31 Stage-2 Markov State"
    assert "`Y_rec = (x_e, T_m, D_-(q;z), L_-(z))`" in graph["paper31.stage2_markov_state"].statement
    assert (
        graph["local.inherited_full_stage2_dynamic_history_builder"].label
        == "Inherited FULL Stage-2 Dynamic-history Builder Theorem"
    )
    assert "`H_loc(z) = (c / R_S) sqrt((1-u)/u^3)`" in graph[
        "local.inherited_full_stage2_dynamic_history_builder"
    ].statement
    assert "`D_-(q;z) = interp_Dfnu(lna_0, dlna, Dfminus_hist(q;.), N_z, -ln(1+z))`" in graph[
        "local.inherited_full_stage2_dynamic_history_builder"
    ].statement
    assert graph["calculator.thomson_history_realization"].label == "Thomson-history Realization Theorem"
    assert "`tau_c = 1 / thomson_drag_rate`" in graph["calculator.thomson_history_realization"].statement
    assert graph["local.closed_scalar_metric_state_builder"].label == "Closed Scalar Metric-state Builder Theorem"
    assert graph["local.closed_scalar_metric_state_builder"].claim_status == "derived / scoped as maps"
    assert "`psi = phi - 4.5 (a^2 / k_n^2) rho_plus_p_shear`" in graph[
        "local.closed_scalar_metric_state_builder"
    ].statement
    assert graph["local.closed_scalar_adiabatic_seed_bridge"].label == "Closed Scalar Adiabatic-seed Bridge Theorem"
    assert "`C_N^src = A_s W_N^(+) = A_s ((N+1) / (N_p+1))^(-K_gauge / x)`" in graph[
        "local.closed_scalar_adiabatic_seed_bridge"
    ].statement
    assert graph["local.closed_scalar_acoustic_generator"].label == "Closed Scalar Acoustic Generator Theorem"
    assert graph["local.closed_scalar_acoustic_generator"].claim_status == "derived / scoped as maps"
    assert "`k_n^2 = n(n+2) / R_curv^2`" in graph["local.closed_scalar_acoustic_generator"].statement
    assert "`theta_b' = -a'/a theta_b + metric_euler + k_n^2 c_b^2 delta_b + R * drag_rate * (theta_gamma-theta_b)`" in graph[
        "local.closed_scalar_acoustic_generator"
    ].statement
    assert graph["local.closed_scalar_transfer_projector"].label == "Closed Scalar Transfer Projector Theorem"
    assert graph["local.closed_scalar_transfer_projector"].claim_status == "derived / scoped as maps"
    assert "`Phi_0 = sin(beta chi) / [beta sin chi]`" in graph[
        "local.closed_scalar_transfer_projector"
    ].statement
    assert "`Delta_l^T(q)` and `Delta_l^E(q)`" in graph["local.closed_scalar_transfer_projector"].statement
    assert graph["local.scoped_closed_scalar_pipeline"].label == "Scoped Closed-scalar Pipeline Theorem"
    assert graph["local.scoped_closed_scalar_pipeline"].claim_status == "conditional / scoped"
    assert "No silent one-slot collapse on the hierarchy-wide perturbation `R` slot appears anywhere in this composition." in graph[
        "local.scoped_closed_scalar_pipeline"
    ].statement
    assert graph["calculator.null_family_acoustic_readout"].label == "Null-family Acoustic Readout Theorem"
    assert "`omega_hat(eta) = (ev_eta tensor C_n) P_src(Phi)`" in graph[
        "calculator.null_family_acoustic_readout"
    ].statement
    assert graph["calculator.peak_functional_separation"].label == "Peak-functional Separation Theorem"
    assert "`100theta_s = 100 r_s(z_rec) / D_M(z_rec)`" in graph[
        "calculator.peak_functional_separation"
    ].statement


def test_theta_star_cli_json_includes_provenance() -> None:
    """The published theta_* CLI JSON should emit the explained record."""

    env = os.environ | {"PYTHONPATH": str(SRC)}
    result = subprocess.run(
        [sys.executable, "-m", "aio_calculator", "theta-star-theorem", "--json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["output_id"] == "theta_star_theorem"
    assert payload["provenance"]["root_node"] == "calculator.active_branch_theta_star"
    assert payload["direct_observable_comparison"]["label"] == "First TT peak position"


def test_theta_star_cli_explain_prints_full_theorem_text() -> None:
    """Text-mode explain output should include theorem premises, proof outline, and scope."""

    env = os.environ | {"PYTHONPATH": str(SRC)}
    result = subprocess.run(
        [sys.executable, "-m", "aio_calculator", "theta-star-theorem", "--explain"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "premise = `calculator.selector_support_promotion` fixes the carried physical selector leaf" in result.stdout
    assert "proof_outline = Evaluate the exact strict-bare selector backbone" in result.stdout
    assert "scope_boundary = Fixed active Paper 10 legacy projected branch only." in result.stdout
