"""CLI for the active-branch AIO calculator.

The CLI exposes three theorem-grade public surfaces, one scoped TT surface,
and one fenced research tool:

- late-time/background distances and BAO ratios
- local recombination primitives on the inventory branch
- active-branch theorem-grade `theta_*` from the carried selector closure
- conditional/scoped canonical first-peak TT spectrum
- the clean Premise-2 `tau=1` photosphere estimator on the internal HyRec
  surface

It still does not claim to be a theorem-grade full CLASS-like CMB pipeline. In
particular the TT command is a scoped first-peak carrier, not a closed high-
`ell` CMB solver or a theorem-grade Planck peak extractor.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from .model import CurvedBackgroundModel, late_eta_io
from .provenance import (
    TT_FIRST_PEAK_APPROVED_STATUS,
    explain_active_branch_theta_star,
    explain_background_snapshot,
    explain_recombination_point,
    explain_tt_first_peak_support,
    explained_output_specs,
    theorem_graph,
)
from .recombination import (
    free_electron_density_m3,
    hydrogen_number_density_m3,
    local_background_state,
    local_baryon_loading_R,
    local_scattering_to_expansion_ratio,
    local_sound_speed_m_s,
    optical_depth_gradient_per_redshift,
    primitive_local_kappa_prime,
    saha_equilibrium_xe,
)
from .theorem_cmb import compute_operational_star_estimate
from .theorem_theta_star import compute_active_branch_theta_star
from .scalar_tt_driver import run_canonical_first_peak_tt_driver


def _background_parser() -> argparse.ArgumentParser:
    """Build the background-only parser used for backward compatibility."""

    parser = argparse.ArgumentParser(description="AIO active-branch calculator")
    parser.add_argument("--z", type=float, default=0.57, help="redshift to evaluate")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--explain",
        action="store_true",
        help="include the provenance scaffold for this output",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments.

    If no subcommand is given, preserve the original background-calculator
    interface so the existing public examples do not break.
    """

    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0].startswith("-"):
        args = _background_parser().parse_args(argv)
        args.command = "background"
        return args

    parser = argparse.ArgumentParser(description="AIO active-branch calculator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    background = subparsers.add_parser(
        "background",
        help="evaluate the theorem-grade late-time/background surface",
    )
    background.add_argument("--z", type=float, default=0.57, help="redshift to evaluate")
    background.add_argument("--json", action="store_true", help="emit JSON")
    background.add_argument(
        "--explain",
        action="store_true",
        help="include the provenance scaffold for this output",
    )

    recombination = subparsers.add_parser(
        "recombination-point",
        help="evaluate theorem-grade local recombination primitives at one redshift",
    )
    recombination.add_argument("--z", type=float, required=True, help="redshift to evaluate")
    recombination.add_argument(
        "--x-e",
        type=float,
        default=None,
        help="override the ionization fraction; default is the local Saha seed",
    )
    recombination.add_argument("--json", action="store_true", help="emit JSON")
    recombination.add_argument(
        "--explain",
        action="store_true",
        help="include the provenance scaffold for this output",
    )

    theta_star = subparsers.add_parser(
        "theta-star-theorem",
        help="return the theorem-grade active-branch theta_* closure",
    )
    theta_star.add_argument("--json", action="store_true", help="emit JSON")
    theta_star.add_argument(
        "--explain",
        action="store_true",
        help="print the full theorem chain in text mode",
    )

    theta_star = subparsers.add_parser(
        "theta-star",
        help=(
            "compute the research-only Premise-2 operational tau=1 "
            "photosphere estimator on the active branch"
        ),
    )
    theta_star.add_argument(
        "--rebuild-class-public",
        action="store_true",
        help="force a rebuild of the internal class_public backend before computing",
    )
    theta_star.add_argument("--json", action="store_true", help="emit JSON")

    provenance = subparsers.add_parser(
        "provenance-catalog",
        help="list the current theorem nodes and explained-output families",
    )
    provenance.add_argument("--json", action="store_true", help="emit JSON")

    tt = subparsers.add_parser(
        "tt-spectrum",
        help="run the canonical conditional/scoped first-peak TT carrier",
    )
    tt.add_argument("--json", action="store_true", help="emit JSON")
    tt.add_argument(
        "--explain",
        action="store_true",
        help="include the provenance nodes for this TT carrier",
    )
    tt.add_argument(
        "--workers",
        type=int,
        default=1,
        help="number of shell worker processes for the canonical TT run",
    )

    return parser.parse_args(argv)


def _background_snapshot(z: float) -> dict[str, float]:
    """Collect the public late-time/background payload."""

    model = CurvedBackgroundModel()
    snapshot = model.snapshot(z)
    snapshot["eta_IO_late"] = late_eta_io()
    return snapshot


def _recombination_point(z: float, x_e_override: float | None) -> dict[str, float]:
    """Collect the local theorem-grade recombination payload at one redshift."""

    state = local_background_state(z)
    x_e = saha_equilibrium_xe(z) if x_e_override is None else x_e_override
    return {
        "z": z,
        "x_e": x_e,
        "u": state.u,
        "a_loc_m": state.a_loc_m,
        "H_loc_s_inv": state.H_loc_s_inv,
        "T_r_loc_K": state.T_r_loc_K,
        "n_H_geom_m3": hydrogen_number_density_m3(z),
        "n_e_m3": free_electron_density_m3(z, x_e),
        "kappa_prime_loc": primitive_local_kappa_prime(z, x_e),
        "d_tau_obs_dz": optical_depth_gradient_per_redshift(z, x_e),
        "Gamma_T_over_H_loc": local_scattering_to_expansion_ratio(z, x_e),
        "R_local_geom": local_baryon_loading_R(z),
        "c_s_local_m_s": local_sound_speed_m_s(z),
    }


def _theta_star_snapshot(*, rebuild_class_public: bool) -> dict[str, float | str]:
    """Collect the clean Premise-2 operational photosphere/theta payload."""

    return asdict(compute_operational_star_estimate(rebuild_class_public=rebuild_class_public))


def _theta_star_theorem_snapshot() -> dict[str, float | str]:
    """Collect the theorem-grade active-branch theta payload."""

    return asdict(compute_active_branch_theta_star())


def _provenance_catalog_snapshot() -> dict[str, object]:
    """Collect the theorem dictionary and explained-output family specs."""

    return {
        "theorem_nodes": {key: node.as_dict() for key, node in theorem_graph().items()},
        "explained_output_specs": explained_output_specs(),
    }


def _tt_spectrum_snapshot(*, workers: int) -> dict[str, object]:
    """Collect the canonical conditional/scoped first-peak TT payload."""

    result = run_canonical_first_peak_tt_driver(shell_parallel_workers=workers)
    explained = explain_tt_first_peak_support()
    provenance_ids = (*result.provenance_node_ids, "local.scoped_tt_first_peak_support")
    graph = theorem_graph()
    provenance_nodes = {
        node_id: graph[node_id].as_dict()
        for node_id in provenance_ids
        if node_id in graph
    }
    return {
        "claim_status": TT_FIRST_PEAK_APPROVED_STATUS,
        "driver_claim_status": result.claim_status,
        "scope_boundary": list(explained.scope_boundary),
        "provenance_node_ids": list(provenance_ids),
        "provenance_nodes": provenance_nodes,
        "config": {
            "exact_history_samples": result.config.exact_history_samples,
            "prehistory_samples": result.config.prehistory_samples,
            "n_max": result.config.n_max,
            "ell_max": result.config.ell_max,
            "shell_step": result.config.shell_step,
            "shell_parallel_workers": result.config.shell_parallel_workers,
            "project_metric_constraint": result.config.project_metric_constraint,
            "constraint_metric_source_only": result.config.constraint_metric_source_only,
            "constraint_consistent_seed": result.config.constraint_consistent_seed,
            "metric_baryon_momentum_slot": result.config.metric_baryon_momentum_slot,
            "source_shell_weight_interpretation": result.config.source_shell_weight_interpretation,
            "source_shell_support": result.config.source_shell_support,
        },
        "validation": asdict(result.validation),
        "peak": asdict(result.peak),
        "ell_values": list(result.spectrum.ell_values),
        "c_ell": list(result.spectrum.c_ell),
    }


def _emit_theorem_node_text(node: dict[str, object], *, index: int | None = None) -> None:
    """Print one theorem node as a self-contained theorem dictionary entry."""

    prefix = f"{index}. " if index is not None else "- "
    print(f"{prefix}{node['label']} [{node['claim_status']}]")
    print(f"   node_id = {node['node_id']}")
    print(f"   statement = {node['statement']}")
    print(f"   scope = {node['scope']}")
    if node.get("depends_on"):
        print("   depends_on = " + ", ".join(node["depends_on"]))
    for premise in node.get("premises", []):
        print(f"   premise = {premise}")
    for step in node.get("proof_outline", []):
        print(f"   proof_outline = {step}")
    for boundary in node.get("scope_boundary", []):
        print(f"   scope_boundary = {boundary}")
    for note in node.get("notes", []):
        print(f"   note = {note}")
    if node.get("authority_paths"):
        print(f"   references = {node.get('reference_note')}")
        for path in node["authority_paths"]:
            print(f"   reference_path = {path}")


def _emit_explained_text(explained: dict[str, object]) -> None:
    """Print one explained output in a compact text form."""

    primary_key = str(explained["primary_key"])
    primary_value = explained["primary_value"]
    units = explained["units"]
    print(f"{primary_key} = {primary_value}" + (f" {units}" if units else ""))
    print(f"claim_status = {explained['claim_status']}")
    print(f"provenance_status = {explained['provenance_status']}")
    print(f"zero_fitted_parameters = {explained['zero_fitted_parameters']}")
    print("conditional_on = " + ", ".join(explained["conditional_on_premises"]))
    for boundary in explained["scope_boundary"]:
        print(f"scope = {boundary}")
    if explained.get("geometry_explanation"):
        print(f"geometry = {explained['geometry_explanation']}")
    comparison = explained.get("direct_observable_comparison")
    if comparison:
        print(
            "direct_observable = "
            f"{comparison['label']}: predicted {comparison['predicted_value']:.12f} "
            f"vs observed {comparison['observed_reference']:.12f} "
            f"({comparison['units']}, delta {comparison['delta']:+.12f})"
        )
    provenance = explained.get("provenance")
    if provenance:
        print("derivation_chain:")
        for index, node_id in enumerate(provenance["chain_ids"], start=1):
            node = provenance["nodes"][node_id]
            _emit_theorem_node_text(node, index=index)


def main() -> None:
    """Evaluate one calculator payload and print it in text or JSON form."""

    args = parse_args()

    if args.command == "recombination-point":
        if args.explain and args.json:
            print(json.dumps(explain_recombination_point(args.z, args.x_e).as_dict(), indent=2))
            return
        snapshot = _recombination_point(args.z, args.x_e)
        if args.json:
            print(json.dumps(snapshot, indent=2))
            return
        print(f"z = {snapshot['z']}")
        print(f"x_e = {snapshot['x_e']:.12f}")
        print(f"u(z) = {snapshot['u']:.12e}")
        print(f"a_loc(z) = {snapshot['a_loc_m']:.12e} m")
        print(f"H_loc(z) = {snapshot['H_loc_s_inv']:.12e} s^-1")
        print(f"T_R,loc(z) = {snapshot['T_r_loc_K']:.12f} K")
        print(f"n_H,geom(z) = {snapshot['n_H_geom_m3']:.12e} m^-3")
        print(f"n_e(z) = {snapshot['n_e_m3']:.12e} m^-3")
        print(f"kappa'_loc(z) = {snapshot['kappa_prime_loc']:.12e}")
        print(f"d tau_obs / dz = {snapshot['d_tau_obs_dz']:.12e}")
        print(f"Gamma_T / H_loc = {snapshot['Gamma_T_over_H_loc']:.12e}")
        print(f"R_local,geom = {snapshot['R_local_geom']:.12e}")
        print(f"c_s,local = {snapshot['c_s_local_m_s']:.12e} m/s")
        if args.explain:
            _emit_explained_text(explain_recombination_point(args.z, args.x_e).as_dict())
        return

    if args.command == "theta-star-theorem":
        explained = explain_active_branch_theta_star().as_dict()
        snapshot = _theta_star_theorem_snapshot()
        if args.json:
            print(json.dumps(explained, indent=2))
            return
        print(f"branch = {snapshot['branch_label']}")
        print(f"claim_status = {snapshot['claim_status']}")
        print(f"z_sel = {snapshot['selector_leaf_z']:.12f}")
        print(f"theta_bare = {snapshot['theta_bare_deg']:.12f} deg")
        print(f"theta_obs = {snapshot['theta_obs_deg']:.12f} deg")
        print(f"100theta_* = {snapshot['theta_star_100']:.12f}")
        print(f"selector_roundtrip_error = {snapshot['selector_roundtrip_error']:+.12e}")
        if args.explain:
            _emit_explained_text(explained)
        return

    if args.command == "theta-star":
        snapshot = _theta_star_snapshot(
            rebuild_class_public=args.rebuild_class_public
        )
        if args.json:
            print(json.dumps(snapshot, indent=2))
            return
        print(f"branch = {snapshot['branch_label']}")
        print(f"claim_status = {snapshot['claim_status']}")
        print(f"z_* = {snapshot['z_star']:.12f}")
        print(f"z_rec = {snapshot['z_rec']:.12f}")
        print(f"z_d = {snapshot['z_d']:.12f}")
        print(f"r_s(z_*) = {snapshot['rs_star_mpc']:.12f} Mpc")
        print(f"r_s(z_rec) = {snapshot['rs_rec_mpc']:.12f} Mpc")
        print(f"r_d = {snapshot['rs_d_mpc']:.12f} Mpc")
        print(f"D_M(z_*) = {snapshot['dm_star_mpc']:.12f} Mpc")
        print(f"100theta_* = {snapshot['theta_star_100']:.12f}")
        print(f"100theta_s = {snapshot['theta_s_100']:.12f}")
        print("note = research-only operational estimator; not theorem-grade theta_*")
        return

    if args.command == "provenance-catalog":
        snapshot = _provenance_catalog_snapshot()
        if args.json:
            print(json.dumps(snapshot, indent=2))
            return
        print("Explained output families:")
        for key, spec in snapshot["explained_output_specs"].items():
            print(
                f"- {key}: {spec['claim_status']} "
                f"(provenance {spec['provenance_status']})"
            )
        print("Theorem nodes:")
        for key, node in snapshot["theorem_nodes"].items():
            _emit_theorem_node_text(node)
        return

    if args.command == "tt-spectrum":
        snapshot = _tt_spectrum_snapshot(workers=args.workers)
        if args.json:
            print(json.dumps(snapshot, indent=2))
            return
        validation = snapshot["validation"]
        print(f"claim_status = {snapshot['claim_status']}")
        print(f"driver_claim_status = {snapshot['driver_claim_status']}")
        print(
            "config = "
            f"exact={snapshot['config']['exact_history_samples']} "
            f"pre={snapshot['config']['prehistory_samples']} "
            f"n_max={snapshot['config']['n_max']} "
            f"ell_max={snapshot['config']['ell_max']} "
            f"workers={snapshot['config']['shell_parallel_workers']}"
        )
        print(f"ell_peak = {validation['ell_peak']}")
        print(f"c220_over_peak = {validation['c_220_over_peak']}")
        print(f"c2_over_c30 = {validation['plateau_2_to_30_ratio']}")
        for boundary in snapshot["scope_boundary"]:
            print(f"scope = {boundary}")
        if args.explain:
            print("derivation_chain:")
            for index, node_id in enumerate(snapshot["provenance_node_ids"], start=1):
                node = snapshot["provenance_nodes"].get(node_id)
                if node is not None:
                    _emit_theorem_node_text(node, index=index)
        else:
            print("use --json for the full C_l array or --explain for theorem nodes")
        return

    if args.explain and args.json:
        print(json.dumps(explain_background_snapshot(args.z).as_dict(), indent=2))
        return
    snapshot = _background_snapshot(args.z)
    if args.json:
        print(json.dumps(snapshot, indent=2))
        return

    print(f"z = {args.z}")
    print(f"H(z) = {snapshot['H_km_s_mpc']:.12f} km/s/Mpc")
    print(f"D_M(z) = {snapshot['DM_mpc']:.12f} Mpc")
    print(f"D_H(z) = {snapshot['DH_mpc']:.12f} Mpc")
    print(f"D_V(z) = {snapshot['DV_mpc']:.12f} Mpc")
    print(f"D_M / r_d = {snapshot['DM_over_rd']:.12f}")
    print(f"D_H / r_d = {snapshot['DH_over_rd']:.12f}")
    print(f"D_V / r_d = {snapshot['DV_over_rd']:.12f}")
    print(f"lookback = {snapshot['lookback_gyr']:.12f} Gyr")
    print(f"age(z) = {snapshot['age_gyr']:.12f} Gyr")
    print(f"eta_IO,late = {snapshot['eta_IO_late']:.12e}")
    if args.explain:
        _emit_explained_text(explain_background_snapshot(args.z).as_dict())


if __name__ == "__main__":
    main()
