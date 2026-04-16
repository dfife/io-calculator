#!/usr/bin/env python3
"""Build the static JSON bundle consumed by the publishable calculator page.

The generated bundle does two jobs:

1. carry the numeric branch data needed by the static browser calculator
2. carry enough claim-boundary metadata that the page can explain what is
   closed, conditional, or still open without server-side code
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator import (  # noqa: E402
    ACTIVE_BARYON_SLOTS,
    ACTIVE_BRANCH,
    ACTIVE_IO_CONSTANTS,
    AUTHORITY_PATHS,
    CurvedBackgroundModel,
    hydrogen_number_density_m3,
    late_eta_io,
    local_background_state,
    local_baryon_loading_R,
    local_scattering_to_expansion_ratio,
    local_sound_speed_m_s,
    optical_depth_gradient_per_redshift,
    explained_output_specs,
    primitive_local_kappa_prime,
    published_explained_outputs,
    saha_equilibrium_xe,
    theorem_graph,
)
from aio_calculator.static_render import (  # noqa: E402
    render_public_calculator_page,
    render_public_theorem_dictionary_page,
)


BUNDLE_PATH = ROOT / "data" / "aio_calculator_bundle.json"
LOCAL_CALCULATOR_HTML = ROOT / "calculator.html"
LOCAL_THEOREMS_HTML = ROOT / "calculator-theorems.html"
PUBLIC_SITE_ROOT = ROOT.parent / "tmp" / "dfife.github.io"
CURVE_SAMPLE_Z = [
    0.0,
    0.1,
    0.25,
    0.5,
    0.57,
    0.706,
    1.0,
    1.321,
    1.484,
    2.0,
    2.33,
    3.0,
    5.0,
]


def load_json(path: Path) -> dict:
    """Read a small authority JSON file into memory."""

    return json.loads(path.read_text(encoding="utf-8"))


def selected_papers() -> list[dict]:
    """Keep only papers that control the live theorem-grade calculator surface."""

    papers = load_json(AUTHORITY_PATHS["public_paper_index"])
    keep = {10, 21, 26, 27, 29, 30, 31, 32, 35, 36, 37}
    return [paper for paper in papers if int(paper["paper"]) in keep]


def sample_curve(model: CurvedBackgroundModel) -> dict[str, list[float]]:
    """Sample the background model at a fixed set of redshifts for the page."""

    z_values = CURVE_SAMPLE_Z
    curve = {
        "z": z_values,
        "H_km_s_mpc": [],
        "DM_mpc": [],
        "DH_mpc": [],
        "DV_mpc": [],
        "lookback_gyr": [],
        "age_gyr": [],
        "DM_over_rd": [],
        "DH_over_rd": [],
        "DV_over_rd": [],
    }
    for z in z_values:
        snap = model.snapshot(z, n=4096)
        curve["H_km_s_mpc"].append(snap["H_km_s_mpc"])
        curve["DM_mpc"].append(snap["DM_mpc"])
        curve["DH_mpc"].append(snap["DH_mpc"])
        curve["DV_mpc"].append(snap["DV_mpc"])
        curve["lookback_gyr"].append(snap["lookback_gyr"])
        curve["age_gyr"].append(snap["age_gyr"])
        curve["DM_over_rd"].append(snap["DM_over_rd"])
        curve["DH_over_rd"].append(snap["DH_over_rd"])
        curve["DV_over_rd"].append(snap["DV_over_rd"])
    return curve


def source_links() -> list[dict[str, str]]:
    """Files intentionally exposed as direct local links from the static page."""

    return [
        {"label": "README", "href": "README.md"},
        {"label": "Package Definition", "href": "pyproject.toml"},
        {"label": "Bundle Builder", "href": "build_bundle.py"},
        {"label": "Python Constants", "href": "src/aio_calculator/constants.py"},
        {"label": "Python Model", "href": "src/aio_calculator/model.py"},
        {"label": "Python Recombination", "href": "src/aio_calculator/recombination.py"},
        {"label": "Python CLI", "href": "src/aio_calculator/__main__.py"},
        {"label": "Calculator Preview HTML", "href": "calculator.html"},
        {"label": "Theorem Dictionary Preview HTML", "href": "calculator-theorems.html"},
        {"label": "Frontend HTML Template", "href": "index.html"},
        {"label": "Frontend JS", "href": "assets/calculator.js"},
        {"label": "Frontend CSS", "href": "assets/calculator.css"},
    ]


def _write_optional_public_site_copy(
    *,
    relative_path: str,
    payload: str,
    written_paths: list[Path],
) -> None:
    """Mirror one generated artifact into the website repo when it is available."""

    if not PUBLIC_SITE_ROOT.exists():
        return
    target = PUBLIC_SITE_ROOT / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    written_paths.append(target)


def main() -> None:
    """Rebuild the publishable static bundle from local authority files."""

    model = CurvedBackgroundModel()

    paper30 = load_json(AUTHORITY_PATHS["paper30_legacy_recompute"])
    paper31 = load_json(AUTHORITY_PATHS["paper31_legacy_recompute"])
    paper35_de = load_json(AUTHORITY_PATHS["paper35_dark_energy"])
    paper35_eta = load_json(AUTHORITY_PATHS["paper35_eta_closure"])

    snapshot_057 = model.snapshot(0.57, n=4096)
    snapshot_051 = model.snapshot(0.51, n=4096)
    snapshot_233 = model.snapshot(2.33, n=4096)
    recombination_state_1100 = local_background_state(1100.0)
    x_e_saha_1100 = saha_equilibrium_xe(1100.0)

    # Keep the bundle declarative. The static page should be able to explain
    # the current branch and claim boundaries without importing lab internals.
    bundle = {
        "metadata": {
            "name": "AIO Calculator",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "branch_status": "active_paper10_legacy_branch",
            "calculator_scope": [
                "derived or verified closed-FRW background geometry",
                "active-branch BAO distance observables",
                "late-time eta_IO closure",
                "theorem-grade local recombination primitives on omega_b,geom",
                "conditional exact inherited-FULL Stage-2 dynamic-network history builder",
                "typed visibility-packet operators on supplied exact Stage-2 histories",
                "active-branch vacuum mapping summary",
                "theorem-grade active-branch theta_* with full provenance",
            ],
            "calculator_boundaries": [
                "no universal IO-native Stage-2 renormalization theorem in the live package beyond the conditional inherited-FULL builder",
                "no theorem-grade full TT/TE/EE spectrum solver in the live package",
                "no theorem-grade Planck acoustic extractor in the live package",
                "no theorem-grade universal off-branch theta_* transfer theorem",
                "no theorem-grade SH0ES or TRGB stellar projector closure",
                "no theorem-grade exact TDCOSMO lens-normalization selector",
            ],
        },
        "branch": ACTIVE_BRANCH.as_dict(),
        "baryons": ACTIVE_BARYON_SLOTS.as_dict(),
        "io_constants": ACTIVE_IO_CONSTANTS.as_dict(),
        "derived_examples": {
            "age_today_gyr": model.age_today_gyr(n=4096),
            "eta_io_late": late_eta_io(),
            "z_0_57": snapshot_057,
            "z_0_51": snapshot_051,
            "z_2_33": snapshot_233,
            "recombination_local_z_1100": {
                "z": 1100.0,
                "u": recombination_state_1100.u,
                "a_loc_m": recombination_state_1100.a_loc_m,
                "H_loc_s_inv": recombination_state_1100.H_loc_s_inv,
                "T_r_loc_K": recombination_state_1100.T_r_loc_K,
                "n_H_geom_m3": recombination_state_1100.n_H_geom_m3,
                "x_e_saha": x_e_saha_1100,
                "n_e_m3": x_e_saha_1100 * hydrogen_number_density_m3(1100.0),
                "kappa_prime_loc": primitive_local_kappa_prime(1100.0, x_e_saha_1100),
                "d_tau_obs_dz": optical_depth_gradient_per_redshift(1100.0, x_e_saha_1100),
                "Gamma_T_over_H_loc": local_scattering_to_expansion_ratio(
                    1100.0, x_e_saha_1100
                ),
                "R_local_geom": local_baryon_loading_R(1100.0),
                "c_s_local_m_s": local_sound_speed_m_s(1100.0),
            },
        },
        "curves": sample_curve(model),
        "paper30_summary": {
            "active_inputs": paper30["inputs"]["io_background"],
            "pantheon_delta_chi2": paper30["tests"]["pantheon"]["planck"]["chi2"]
            - paper30["tests"]["pantheon"]["io"]["chi2"],
            "strong_lensing_delta_chi2": paper30["tests"]["strong_lensing"]["planck"]["chi2"]
            - paper30["tests"]["strong_lensing"]["io"]["chi2"],
            "observer_age_gyr_reported": 13.543919214135,
        },
        "paper31_summary": {
            "geometric_pre_drag_ruler": paper31["geometric_pre_drag_ruler"],
            "bao_galaxy_block": paper31["bao_galaxy_block"],
            "sigma8_s8_eg": paper31["sigma8_s8_eg"],
        },
        "paper35_dark_energy": paper35_de["final_assessment"],
        "paper35_dark_energy_reinterpretation": paper35_de[
            "route_5_flat_cpl_reinterpretation"
        ],
        "paper35_eta": {
            "closure": paper35_eta["closed_late_time_chain"],
            "mass_conventions": paper35_eta["mass_conventions"],
            "remaining_open": paper35_eta["what_remains_open"],
        },
        "provenance_graph": {key: node.as_dict() for key, node in theorem_graph().items()},
        "explained_output_specs": explained_output_specs(),
        "explained_outputs": published_explained_outputs(),
        "papers": selected_papers(),
        "source_code_links": source_links(),
        "authority_paths": {key: str(path) for key, path in AUTHORITY_PATHS.items()},
    }

    payload = json.dumps(bundle, indent=2) + "\n"
    calculator_html = render_public_calculator_page(bundle)
    theorems_html = render_public_theorem_dictionary_page(bundle)

    written_paths = []
    BUNDLE_PATH.write_text(payload, encoding="utf-8")
    written_paths.append(BUNDLE_PATH)
    LOCAL_CALCULATOR_HTML.write_text(calculator_html, encoding="utf-8")
    written_paths.append(LOCAL_CALCULATOR_HTML)
    LOCAL_THEOREMS_HTML.write_text(theorems_html, encoding="utf-8")
    written_paths.append(LOCAL_THEOREMS_HTML)

    _write_optional_public_site_copy(
        relative_path="data/aio_calculator_bundle.json",
        payload=payload,
        written_paths=written_paths,
    )
    _write_optional_public_site_copy(
        relative_path="calculator.html",
        payload=calculator_html,
        written_paths=written_paths,
    )
    _write_optional_public_site_copy(
        relative_path="calculator-theorems.html",
        payload=theorems_html,
        written_paths=written_paths,
    )

    for path in written_paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
