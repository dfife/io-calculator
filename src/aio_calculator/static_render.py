"""Static HTML rendering for the public calculator pages.

The public website keeps the JSON bundle as the canonical data product, but the
HTML pages are pre-rendered from that bundle so the theorem content is present
in page source without requiring JavaScript execution.
"""

from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

from .model import CurvedBackgroundModel


_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_PAPER_SINGLE_RE = re.compile(r"\bPaper (\d+)\b")
FRAMEWORK_MOTTO = "If the theory is correct, the math will just work."
PREDICTION_SUMMARY_ITEMS = (
    "T_CMB (0.3σ from FIRAS)",
    "H0 (0.35σ from Planck)",
    "Omega_k within 1σ of Planck CMB-only",
    "BBN triple (chi^2 = 1.13)",
    "Hubble tension resolved (max 0.57σ across 6 methods)",
    "40-year lithium problem resolved",
    "CMB first peak ell = 224",
)
OUTPUT_SCHEMA_COMPARISONS: dict[str, dict[str, object]] = {
    "active_t_cmb": {
        "measured_label": "FIRAS CMB temperature reference",
        "measured_value": 2.7255,
        "units": "K",
        "tension_sigma": 0.3,
        "reference_name": "FIRAS",
    },
    "branch_h0": {
        "measured_label": "Planck H0 reference",
        "measured_value": 67.4,
        "units": "km/s/Mpc",
        "tension_sigma": 0.35,
        "reference_name": "Planck",
    },
    "branch_omega_k": {
        "measured_label": "Planck CMB-only non-flat Omega_k reference",
        "measured_value": -0.044,
        "tension_sigma": 1.0,
        "reference_name": "Planck CMB-only",
    },
    "bbn_deuterium_ratio": {
        "measured_label": "Cooke et al. deuterium reference",
        "tension_sigma": 0.61,
        "reference_name": "Cooke et al.",
    },
    "bbn_helium_fraction": {
        "measured_label": "Aver et al. helium reference",
        "tension_sigma": 0.68,
        "reference_name": "Aver et al.",
    },
    "bbn_lithium_ratio": {
        "measured_label": "Spite plateau lithium reference",
        "tension_sigma": 0.55,
        "reference_name": "Spite plateau",
    },
    "scalar_tilt_ns": {
        "measured_label": "Planck scalar tilt reference",
        "tension_sigma": 0.24,
        "reference_name": "Planck",
    },
    "branch_rd_mpc": {
        "measured_label": "Planck drag-ruler reference",
        "measured_value": 147.09,
        "units": "Mpc",
        "tension_sigma": 11.83,
        "reference_name": "Planck",
    },
    "native_scalar_amplitude_as": {
        "measured_label": "Planck scalar amplitude reference",
        "measured_value": 2.1e-9,
        "tension_sigma": 3.09,
        "reference_name": "Planck",
    },
    "tt_first_peak_support": {
        "measured_label": "Observed first TT peak reference",
        "measured_value": 220.0,
        "units": "ell",
        "reference_name": "Observed first TT peak",
    },
}
SOURCE_REPO_URL = "https://github.com/dfife/io-calculator"
DATASET_LICENSE_URL = "https://dfife.github.io/data-license.html"


def paper_url_map() -> dict[int, str]:
    """Load the published Zenodo URLs keyed by paper number."""

    papers_path = Path(__file__).resolve().parents[2] / "data" / "papers.json"
    if not papers_path.exists():
        return {}
    try:
        payload = json.loads(papers_path.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, list):
        return {}
    mapping: dict[int, str] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        try:
            number = int(item["paper"])
        except (KeyError, TypeError, ValueError):
            continue
        url = item.get("zenodo")
        if isinstance(url, str) and url:
            mapping[number] = url
    return mapping


def link_paper_references(rendered_html: str) -> str:
    """Turn plain-text single-paper references into Zenodo links."""

    mapping = paper_url_map()
    if not mapping:
        return rendered_html

    def replace(match: re.Match[str]) -> str:
        number = int(match.group(1))
        url = mapping.get(number)
        if not url:
            return match.group(0)
        return (
            f'<a class="calc-inline-link" href="{escape_html(url)}" '
            f'target="_blank" rel="noreferrer">{match.group(0)}</a>'
        )

    return _PAPER_SINGLE_RE.sub(replace, rendered_html)


def escape_html(value: object) -> str:
    """Escape an arbitrary scalar for direct HTML insertion."""

    return html.escape(str(value), quote=True)


def render_inline(value: object) -> str:
    """Render inline code markers while keeping everything else escaped."""

    escaped = escape_html(value)
    return _INLINE_CODE_RE.sub(r"<code>\1</code>", escaped)


def format_number(value: float, digits: int = 6) -> str:
    """Match the browser formatter used on the public page."""

    fixed = f"{float(value):.{digits}f}"
    fixed = re.sub(r"(\.\d*?[1-9])0+$", r"\1", fixed)
    fixed = re.sub(r"\.0+$", "", fixed)
    return fixed


def format_scalar(value: object) -> str:
    """Render a scalar in the same style as the existing web surface."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return render_inline(value)
    numeric = float(value)
    if not math.isfinite(numeric):
        return render_inline(value)
    absolute = abs(numeric)
    if (absolute != 0 and absolute < 1.0e-4) or absolute >= 1.0e5:
        return escape_html(f"{numeric:.6e}")
    if absolute >= 1000:
        return escape_html(format_number(numeric, 6))
    return escape_html(format_number(numeric, 12))


def status_class(status: str) -> str:
    """Map claim-status text to the existing badge palette."""

    lower = str(status).lower()
    if "conditional/scoped/verified tt first-peak support" in lower:
        return "is-mixed"
    if "conditional premise" in lower:
        return "is-premise"
    if "conditional / scoped" in lower:
        return "is-conditional"
    if "derived / scoped as maps" in lower:
        return "is-derived"
    if "derived / scoped" in lower:
        return "is-derived"
    if "verified" in lower and "derived" in lower:
        return "is-mixed"
    if "verified" in lower:
        return "is-verified"
    if "theorem" in lower:
        return "is-derived"
    if "conditional" in lower:
        return "is-conditional"
    if "scaffold" in lower:
        return "is-neutral"
    return "is-derived"


def compact_status(status: str) -> str:
    """Return the compact badge label used by the current UI."""

    lower = str(status).lower()
    if "conditional/scoped/verified tt first-peak support" in lower:
        return str(status)
    if "conditional premise" in lower:
        return "premise"
    if "conditional / scoped" in lower:
        return "conditional / scoped"
    if "derived / scoped as maps" in lower:
        return "derived / scoped as maps"
    if "derived / scoped" in lower:
        return "derived / scoped"
    if "verified / scoped" in lower:
        return "verified / scoped"
    if "conditional" in lower:
        return "conditional"
    if "scaffold" in lower:
        return "scaffold"
    return str(status)


def status_badge(status: str, extra_class: str = "") -> str:
    """Render a colored status badge."""

    extra_classes = []
    if extra_class:
        extra_classes.append(extra_class)
    if "conditional/scoped/verified tt first-peak support" in str(status).lower():
        extra_classes.append("is-verbatim-status")
    extra = f" {' '.join(extra_classes)}" if extra_classes else ""
    return (
        f'<span class="calc-badge {status_class(status)}{extra}">'
        f"{escape_html(compact_status(status))}</span>"
    )


def neutral_badge(label: str) -> str:
    """Render a neutral status badge."""

    return f'<span class="calc-badge is-neutral">{escape_html(label)}</span>'


def metric_row(label: str, value: str) -> str:
    """Render a two-column metric row."""

    return (
        '<div class="calc-row">'
        f'<span class="calc-row-label">{escape_html(label)}</span>'
        f'<span class="calc-row-value">{value}</span>'
        "</div>"
    )


def list_markup(items: list[str] | tuple[str, ...] | None) -> str:
    """Render a flat calculator list."""

    if not items:
        return ""
    rendered = "".join(f"<li>{render_inline(item)}</li>" for item in items)
    return f'<ul class="calc-list">{rendered}</ul>'


def authority_chips(authority_paths: list[str] | tuple[str, ...] | None) -> str:
    """Render reference filename chips."""

    if not authority_paths:
        return ""
    chips = "".join(
        f'<span class="calc-chip">{escape_html(Path(path).name)}</span>'
        for path in authority_paths
    )
    return f'<div class="calc-chip-row">{chips}</div>'


def section_list(label: str, items: list[str] | tuple[str, ...] | None) -> str:
    """Render a labeled list subsection."""

    if not items:
        return ""
    return (
        '<div class="calc-subsection">'
        f'<p class="calc-section-label">{escape_html(label)}</p>'
        f"{list_markup(items)}"
        "</div>"
    )


def theorem_node_detail(
    node: dict[str, object], *, index: int | None = None, open_node: bool = False
) -> str:
    """Render a theorem node with full theorem text."""

    kind = escape_html(str(node.get("kind", "theorem")))
    show_index = index is not None
    depends_on = node.get("depends_on") or []
    notes = node.get("notes") or []
    authority_paths = node.get("authority_paths") or []
    depends_markup = (
        "<p><strong>Depends on.</strong> "
        + ", ".join(
            f"<code>{escape_html(item)}</code>" for item in depends_on  # type: ignore[arg-type]
        )
        + "</p>"
        if depends_on
        else ""
    )
    notes_markup = "".join(
        f"<p>{link_paper_references(render_inline(note))}</p>" for note in notes
    )  # type: ignore[arg-type]
    premises = section_list("Premises", node.get("premises"))  # type: ignore[arg-type]
    proof_outline = section_list("Proof outline", node.get("proof_outline"))  # type: ignore[arg-type]
    scope_boundary = section_list("Scope boundary", node.get("scope_boundary"))  # type: ignore[arg-type]
    references = (
        '<div class="calc-subsection">'
        '<p class="calc-section-label">Supporting references</p>'
        f'<p class="calc-node-caption">{link_paper_references(render_inline(node.get("reference_note", "")))}</p>'
        f"{authority_chips(authority_paths)}"
        "</div>"
        if authority_paths
        else ""
    )
    header = (
        f'<span class="calc-step">{index}.</span>'
        if show_index
        else f'<span class="calc-kind">{kind}</span>'
    )
    open_attr = " open" if open_node else ""
    node_id = escape_html(str(node["node_id"]))
    return (
        f'<details class="calc-node" data-node-id="{node_id}"{open_attr}>'
        '<summary class="calc-node-summary">'
        '<div class="calc-node-main">'
        f"{header}"
        f'<span>{link_paper_references(escape_html(node["label"]))}</span>'
        "</div>"
        '<div class="calc-badge-row">'
        f"{status_badge(str(node['claim_status']))}"
        '<span class="calc-chevron" aria-hidden="true">›</span>'
        "</div>"
        "</summary>"
        '<div class="calc-node-body">'
        '<p class="calc-section-label">Statement</p>'
        f"<p>{link_paper_references(render_inline(node['statement']))}</p>"
        f"<p><strong>Node id.</strong> <code>{node_id}</code></p>"
        f"<p><strong>Scope summary.</strong> {link_paper_references(render_inline(node['scope']))}</p>"
        f"{depends_markup}"
        f"{premises}"
        f"{proof_outline}"
        f"{scope_boundary}"
        f"{notes_markup}"
        f"{references}"
        "</div>"
        "</details>"
    )


def output_card_name(output: dict[str, object]) -> str:
    """Return the compact output label used on the summary line."""

    output_id = output["output_id"]
    if output_id == "theta_star_theorem":
        return "100theta_*"
    if output_id == "tt_first_peak_support":
        return "TT first peak"
    if output_id == "branch_rd_mpc":
        return "r_d"
    if output_id == "branch_h0":
        return "H0"
    if output_id == "branch_omega_m":
        return "Omega_m"
    if output_id == "branch_omega_k":
        return "Omega_k"
    if output_id == "branch_omega_lambda":
        return "Omega_Lambda"
    if output_id == "active_t_cmb":
        return "T_CMB"
    if output_id == "bare_master_clock_age":
        return "Age_bare"
    if output_id == "scalar_tilt_ns":
        return "n_s"
    if output_id == "native_scalar_amplitude_as":
        return "A_s"
    if output_id == "bbn_deuterium_ratio":
        return "D/H"
    if output_id == "bbn_helium_fraction":
        return "Y_p"
    if output_id == "bbn_lithium_ratio":
        return "Li-7/H"
    if output_id == "baryon_fraction_fb":
        return "f_b"
    if output_id == "eta_io_late":
        return "eta_IO"
    if output_id == "background_snapshot":
        return f"D_M(z = {format_number(float(output['z']), 2)})"
    if output_id == "recombination_point":
        return f"kappa'_loc(z = {format_number(float(output['z']), 0)})"
    return str(output["primary_key"])


def output_card_value(output: dict[str, object]) -> str:
    """Return the primary scalar value displayed in the card summary."""

    return format_scalar(output["primary_value"])


def payload_key_label(key: str) -> str:
    """Stable human labels for bundle payload keys."""

    labels = {
        "branch_label": "Branch",
        "r_d_mpc": "r_d",
        "H0_km_s_mpc": "H0",
        "Omega_m": "Omega_m",
        "Omega_k": "Omega_k",
        "Omega_Lambda": "Omega_Lambda",
        "T_CMB_K": "T_CMB",
        "T_IO_K": "T_IO",
        "age_bare_gyr": "Age_bare",
        "H0_bare_km_s_mpc": "H0_bare",
        "Omega_m_bare": "Omega_m,bare",
        "Omega_k_bare": "Omega_k,bare",
        "Omega_Lambda_bare": "Omega_Lambda,bare",
        "Omega_r_bare": "Omega_r,bare",
        "n_s": "n_s",
        "A_s": "A_s",
        "gamma_BI": "gamma_BI",
        "x": "x",
        "K_gauge": "K_gauge",
        "D_H_ratio": "D/H",
        "Y_p": "Y_p",
        "Li7_H_ratio": "Li-7/H",
        "f_b": "f_b",
        "eta_IO_late": "eta_IO,late",
        "z": "z",
        "H_km_s_mpc": "H(z)",
        "DM_mpc": "D_M",
        "DA_mpc": "D_A",
        "DL_mpc": "D_L",
        "DH_mpc": "D_H",
        "DV_mpc": "D_V",
        "lookback_gyr": "Lookback",
        "age_gyr": "Age",
        "DM_over_rd": "D_M / r_d",
        "DH_over_rd": "D_H / r_d",
        "DV_over_rd": "D_V / r_d",
        "x_e": "x_e",
        "u": "u",
        "a_loc_m": "a_loc",
        "H_loc_s_inv": "H_loc",
        "T_r_loc_K": "T_R,loc",
        "n_H_geom_m3": "n_H,geom",
        "n_e_m3": "n_e",
        "kappa_prime_loc": "kappa'_loc",
        "d_tau_obs_dz": "d tau_obs / dz",
        "Gamma_T_over_H_loc": "Gamma_T / H_loc",
        "R_local_geom": "R_local,geom",
        "c_s_local_m_s": "c_s,local",
        "selector_leaf_z": "Selector leaf",
        "theta_bare_deg": "theta_bare",
        "theta_obs_deg": "theta_obs",
        "theta_star_100": "100theta_*",
        "selector_roundtrip_error": "Selector roundtrip",
        "ell_peak": "ell_peak",
        "observed_first_peak_ell_reference": "Observed peak",
        "first_peak_delta": "Peak delta",
        "c_220_over_peak": "C_220 / C_peak",
        "c_2_over_c_30": "C_2 / C_30",
        "exact_history_samples": "Exact history samples",
        "prehistory_samples": "Prehistory samples",
        "n_max": "n_max",
        "shell_step": "Shell step",
        "metric_baryon_momentum_slot": "Metric baryon slot",
        "source_shell_support": "Source shell support",
        "source_shell_weight_interpretation": "Shell weight convention",
        "neighbor_n_max": "Neighbor ceiling",
        "neighbor_ell_peak": "Neighbor ell_peak",
        "neighbor_c_220_over_peak": "Neighbor C_220 / C_peak",
    }
    return labels.get(key, key)


def payload_key_unit(key: str, output_units: str | None) -> str:
    """Stable units for bundle payload keys."""

    units = {
        "r_d_mpc": "Mpc",
        "H0_km_s_mpc": "km/s/Mpc",
        "T_CMB_K": "K",
        "T_IO_K": "K",
        "age_bare_gyr": "Gyr",
        "H0_bare_km_s_mpc": "km/s/Mpc",
        "H_km_s_mpc": "km/s/Mpc",
        "DM_mpc": "Mpc",
        "DA_mpc": "Mpc",
        "DL_mpc": "Mpc",
        "DH_mpc": "Mpc",
        "DV_mpc": "Mpc",
        "lookback_gyr": "Gyr",
        "age_gyr": "Gyr",
        "a_loc_m": "m",
        "H_loc_s_inv": "s^-1",
        "T_r_loc_K": "K",
        "n_H_geom_m3": "m^-3",
        "n_e_m3": "m^-3",
        "c_s_local_m_s": "m/s",
        "theta_bare_deg": "deg",
        "theta_obs_deg": "deg",
        "theta_star_100": "100theta_*",
        "ell_peak": "ell",
        "observed_first_peak_ell_reference": "ell",
        "first_peak_delta": "ell",
        "neighbor_ell_peak": "ell",
    }
    return units.get(key, output_units or "")


def payload_row_keys(output: dict[str, object]) -> list[str]:
    """Preserve the existing row order for computed-value sections."""

    preferred = {
        "branch_rd_mpc": ["branch_label", "r_d_mpc"],
        "tt_first_peak_support": [
            "ell_peak",
            "observed_first_peak_ell_reference",
            "first_peak_delta",
            "c_220_over_peak",
            "c_2_over_c_30",
            "exact_history_samples",
            "prehistory_samples",
            "n_max",
            "shell_step",
            "metric_baryon_momentum_slot",
            "source_shell_support",
            "source_shell_weight_interpretation",
            "neighbor_n_max",
            "neighbor_ell_peak",
            "neighbor_c_220_over_peak",
        ],
        "branch_h0": ["branch_label", "H0_km_s_mpc"],
        "branch_omega_m": ["branch_label", "Omega_m"],
        "branch_omega_k": ["branch_label", "Omega_k"],
        "branch_omega_lambda": ["branch_label", "Omega_Lambda"],
        "active_t_cmb": ["branch_label", "T_CMB_K", "T_IO_K", "x", "K_gauge"],
        "bare_master_clock_age": [
            "branch_label",
            "age_bare_gyr",
            "H0_bare_km_s_mpc",
            "Omega_m_bare",
            "Omega_k_bare",
            "Omega_Lambda_bare",
            "Omega_r_bare",
            "T_CMB_K",
        ],
        "scalar_tilt_ns": ["n_s", "K_gauge", "x"],
        "native_scalar_amplitude_as": ["A_s", "gamma_BI", "x", "K_gauge"],
        "bbn_deuterium_ratio": ["D_H_ratio"],
        "bbn_helium_fraction": ["branch_label", "Y_p"],
        "bbn_lithium_ratio": ["Li7_H_ratio"],
        "baryon_fraction_fb": ["f_b", "gamma_BI", "x"],
        "eta_io_late": ["branch_label", "eta_IO_late"],
        "background_snapshot": [
            "z",
            "H_km_s_mpc",
            "DM_mpc",
            "DH_mpc",
            "DV_mpc",
            "DM_over_rd",
            "DH_over_rd",
            "DV_over_rd",
            "lookback_gyr",
            "age_gyr",
            "eta_IO_late",
        ],
        "recombination_point": [
            "z",
            "x_e",
            "H_loc_s_inv",
            "T_r_loc_K",
            "n_H_geom_m3",
            "n_e_m3",
            "kappa_prime_loc",
            "d_tau_obs_dz",
            "Gamma_T_over_H_loc",
            "R_local_geom",
            "c_s_local_m_s",
        ],
    }
    ordered = preferred.get(str(output["output_id"]))
    if ordered is not None:
        return [key for key in ordered if key in output]
    return list(output.keys())


def output_metric_rows(output: dict[str, object]) -> str:
    """Render the computed-value rows for a non-theta output card."""

    skip = {
        "output_id",
        "label",
        "primary_key",
        "primary_value",
        "units",
        "claim_status",
        "provenance_status",
        "zero_fitted_parameters",
        "conditional_on_premises",
        "scope_boundary",
        "non_claims",
        "notes",
        "geometry_explanation",
        "comparison_context",
        "direct_observable_comparisons",
        "direct_observable_comparison",
        "provenance",
    }
    rows = []
    for key in payload_row_keys(output):
        if key in skip:
            continue
        unit = payload_key_unit(key, output.get("units"))  # type: ignore[arg-type]
        value = format_scalar(output[key])
        if unit:
            value = f'{value} <span class="calc-inline-unit">{escape_html(unit)}</span>'
        rows.append(metric_row(payload_key_label(key), value))
    return "".join(rows)


def theorem_chain_section(output: dict[str, object], graph: dict[str, dict[str, object]]) -> str:
    """Render the main derivation chain plus any supporting nodes."""

    provenance = output["provenance"]  # type: ignore[assignment]
    chain_ids = provenance["chain_ids"]  # type: ignore[index]
    supporting_nodes = provenance.get("supporting_node_ids", [])  # type: ignore[assignment]
    chain_markup = "".join(
        theorem_node_detail(graph[node_id], index=index + 1)
        for index, node_id in enumerate(chain_ids)
    )
    supporting_markup = (
        '<section class="calc-section">'
        '<p class="calc-section-label">Supporting node</p>'
        '<div class="calc-nested-stack">'
        + "".join(theorem_node_detail(graph[node_id]) for node_id in supporting_nodes)
        + "</div>"
        "</section>"
        if supporting_nodes
        else ""
    )
    return (
        '<section class="calc-section">'
        '<p class="calc-section-label">Derivation chain</p>'
        '<div class="calc-nested-stack">'
        f"{chain_markup}"
        "</div>"
        "</section>"
        f"{supporting_markup}"
    )


def theta_card(output: dict[str, object], graph: dict[str, dict[str, object]]) -> str:
    """Render the dedicated theta-star card."""

    comparison = output["direct_observable_comparison"]  # type: ignore[assignment]
    comparison_context = output["comparison_context"]  # type: ignore[assignment]
    conditional = ", ".join(
        f"<code>{escape_html(item)}</code>" for item in output["conditional_on_premises"]  # type: ignore[index]
    )
    return (
        '<details class="calc-card" id="theta-output-card">'
        '<summary class="calc-card-summary">'
        '<div class="calc-card-heading">'
        '<div class="calc-card-title-row">'
        f'<span class="calc-card-name">{escape_html(output_card_name(output))}</span>'
        f"{status_badge(str(output['claim_status']))}"
        "</div>"
        f'<p class="calc-card-subtitle">{escape_html(output["label"])}</p>'
        "</div>"
        '<div class="calc-card-value-block">'
        f'<div class="calc-card-value">{output_card_value(output)}</div>'
        f'<div class="calc-card-unit">{escape_html(output["units"])}</div>'
        '<span class="calc-chevron" aria-hidden="true">›</span>'
        "</div>"
        "</summary>"
        '<div class="calc-card-body">'
        '<section class="calc-section">'
        '<p class="calc-section-label">Published result</p>'
        '<div class="calc-metrics">'
        f'{metric_row("Claim status", render_inline(output["claim_status"]))}'
        f'{metric_row("Provenance status", neutral_badge(str(output["provenance_status"])))}'
        f'{metric_row("Zero fitted parameters", "yes" if output["zero_fitted_parameters"] else "no")}'
        f'{metric_row("Conditional on", conditional)}'
        f'{metric_row("Selector leaf", f"{format_scalar(output['selector_leaf_z'])} <span class=\"calc-inline-unit\">z</span>")}'
        f'{metric_row("Observer-side angle", f"{format_scalar(output['theta_obs_deg'])} <span class=\"calc-inline-unit\">deg</span>")}'
        "</div>"
        f"{list_markup(output.get('notes'))}"
        "</section>"
        '<section class="calc-section">'
        '<p class="calc-section-label">Why this differs from Planck</p>'
        '<div class="calc-note">'
        "<p><strong>Calculator statement.</strong> This number differs from Planck's reported value because Planck assumes flat space. The IO framework derives closed space. The direct observable — the first peak position — agrees.</p>"
        f"<p>{render_inline(output['geometry_explanation'])}</p>"
        f"<p>{render_inline(comparison_context['statement'])}</p>"
        "</div>"
        '<div class="calc-metrics">'
        f'{metric_row("Planck flat reference", format_scalar(comparison_context["planck_flat_reference_theta_mc_100"]))}'
        f'{metric_row("Planck closed refit", format_scalar(comparison_context["planck_closed_reference_theta_mc_100"]))}'
        f'{metric_row("Closed refit Omega_k", format_scalar(comparison_context["planck_closed_reference_omegak"]))}'
        "</div>"
        "</section>"
        '<section class="calc-section">'
        '<p class="calc-section-label">Direct observable</p>'
        '<div class="calc-metrics">'
        f'{metric_row("Predicted first peak", f"{format_scalar(comparison['predicted_value'])} <span class=\"calc-inline-unit\">{escape_html(comparison['units'])}</span>")}'
        f'{metric_row("Observed first peak", f"{format_scalar(comparison['observed_reference'])} <span class=\"calc-inline-unit\">{escape_html(comparison['units'])}</span>")}'
        f'{metric_row("Delta", f"{format_scalar(comparison['delta'])} <span class=\"calc-inline-unit\">{escape_html(comparison['units'])}</span>")}'
        "</div>"
        '<div class="calc-note">'
        f"<p>{render_inline(comparison['note'])}</p>"
        "</div>"
        "</section>"
        f"{theorem_chain_section(output, graph)}"
        '<section class="calc-section">'
        '<p class="calc-section-label">Scope boundary</p>'
        f"{list_markup(output['scope_boundary'])}"
        '<p class="calc-section-label calc-section-label-secondary">Non-claims</p>'
        f"{list_markup(output['non_claims'])}"
        "</section>"
        "</div>"
        "</details>"
    )


def generic_output_card(output: dict[str, object], graph: dict[str, dict[str, object]]) -> str:
    """Render a non-theta explained output card."""

    conditional = ", ".join(
        f"<code>{escape_html(item)}</code>" for item in output["conditional_on_premises"]  # type: ignore[index]
    )
    non_claims = output.get("non_claims") or []
    non_claims_markup = (
        '<p class="calc-section-label calc-section-label-secondary">Non-claims</p>'
        f"{list_markup(non_claims)}"
        if non_claims
        else ""
    )
    return (
        f'<details class="calc-card" id="output-{escape_html(output["output_id"])}">'
        '<summary class="calc-card-summary">'
        '<div class="calc-card-heading">'
        '<div class="calc-card-title-row">'
        f'<span class="calc-card-name">{escape_html(output_card_name(output))}</span>'
        f"{status_badge(str(output['claim_status']))}"
        "</div>"
        f'<p class="calc-card-subtitle">{escape_html(output["label"])}</p>'
        "</div>"
        '<div class="calc-card-value-block">'
        f'<div class="calc-card-value">{output_card_value(output)}</div>'
        f'<div class="calc-card-unit">{escape_html(output.get("units") or output["primary_key"])}</div>'
        '<span class="calc-chevron" aria-hidden="true">›</span>'
        "</div>"
        "</summary>"
        '<div class="calc-card-body">'
        '<section class="calc-section">'
        '<p class="calc-section-label">Published result</p>'
        '<div class="calc-metrics">'
        f'{metric_row("Claim status", render_inline(output["claim_status"]))}'
        f'{metric_row("Provenance status", neutral_badge(str(output["provenance_status"])))}'
        f'{metric_row("Zero fitted parameters", "yes" if output["zero_fitted_parameters"] else "no")}'
        f'{metric_row("Conditional on", conditional)}'
        "</div>"
        "</section>"
        '<section class="calc-section">'
        '<p class="calc-section-label">Computed values</p>'
        '<div class="calc-metrics">'
        f"{output_metric_rows(output)}"
        "</div>"
        f"{list_markup(output.get('notes') or [])}"
        "</section>"
        f"{theorem_chain_section(output, graph)}"
        '<section class="calc-section">'
        '<p class="calc-section-label">Scope boundary</p>'
        f"{list_markup(output.get('scope_boundary') or [])}"
        f"{non_claims_markup}"
        "</section>"
        "</div>"
        "</details>"
    )


def theorem_dictionary_markup(bundle: dict[str, object]) -> str:
    """Render the standalone theorem dictionary contents."""

    graph = bundle["provenance_graph"]  # type: ignore[assignment]
    dictionary_markup = "".join(
        theorem_node_detail(node) for node in graph.values()  # type: ignore[union-attr]
    )
    return (
        '<div class="calc-note">'
        "<p>The calculator page carries derivation chains inside each output card. This reference page is the standalone theorem dictionary for the live bundle.</p>"
        "</div>"
        '<div class="calc-card-stack">'
        f"{dictionary_markup}"
        "</div>"
    )


def prediction_summary_markup() -> str:
    """Render the compact top-level prediction summary."""

    items = "".join(f"<li>{escape_html(item)}</li>" for item in PREDICTION_SUMMARY_ITEMS)
    return (
        '<section class="calc-summary-panel" aria-label="What can this predict">'
        '<p class="calc-section-label">What can this predict</p>'
        '<ul class="calc-summary-list">'
        f"{items}"
        "</ul>"
        "</section>"
    )


def redshift_widget_markup() -> str:
    """Render the precomputed redshift widget shell for the calculator page."""

    z_default = 0.57
    model = CurvedBackgroundModel()
    snapshot = model.snapshot(z_default)
    widget_rows = (
        ("H(z)", snapshot["H_km_s_mpc"], "km/s/Mpc"),
        ("D_M(z)", snapshot["DM_mpc"], "Mpc"),
        ("D_A(z)", snapshot["DA_mpc"], "Mpc"),
        ("D_L(z)", snapshot["DL_mpc"], "Mpc"),
        ("Age(z)", snapshot["age_gyr"], "Gyr"),
    )
    row_markup = "".join(
        "<tr>"
        f'<th scope="row"><a class="calc-inline-link" href="#output-background_snapshot_z_0_57">{escape_html(label)}</a></th>'
        f"<td>{format_scalar(value)}</td>"
        f"<td>{escape_html(unit)}</td>"
        f'<td><a class="calc-inline-link" href="{escape_html(paper_url_map().get(30, "calculator-theorems.html#paper30.background_surface"))}" target="_blank" rel="noreferrer">Paper 30</a> background surface</td>'
        "</tr>"
        for label, value, unit in widget_rows
    )
    return (
        f'<section class="calc-widget-shell" id="redshift-widget" '
        f'data-h0="{escape_html(model.branch.H0)}" '
        f'data-omega-m="{escape_html(model.branch.Omega_m)}" '
        f'data-omega-r="{escape_html(model.branch.Omega_r)}" '
        f'data-omega-k="{escape_html(model.branch.Omega_k)}" '
        f'data-omega-lambda="{escape_html(model.branch.Omega_lambda)}" '
        f'data-rd="{escape_html(model.branch.rd_mpc)}" '
        f'data-z-default="{escape_html(z_default)}">'
        '<div class="calc-widget-head">'
        '<div>'
        '<p class="calc-section-label">Try it yourself</p>'
        '<h2 class="calc-widget-title">Redshift calculator</h2>'
        '<p class="calc-widget-copy">'
        "Client-side mirror of the active-branch background engine from "
        '<code>aio_calculator/model.py</code>. Enter a redshift and the page '
        "computes the same closed-FRW background quantities in the browser, "
        "with clickable links back to the theorem-bearing background card and "
        "the theorem dictionary."
        "</p>"
        "</div>"
        '<label class="calc-widget-input-wrap" for="redshift-widget-input">'
        '<span class="calc-widget-label">Redshift z</span>'
        f'<input id="redshift-widget-input" class="calc-widget-input" type="number" min="0" step="0.001" value="{escape_html(z_default)}">'
        "</label>"
        "</div>"
        '<div class="calc-table-wrap">'
        '<table class="calc-table" aria-label="Redshift calculator outputs">'
        "<thead><tr><th>Observable</th><th>Value</th><th>Unit</th><th>Theorem</th></tr></thead>"
        f'<tbody id="redshift-widget-results">{row_markup}</tbody>'
        "</table>"
        "</div>"
        "</section>"
    )


def about_note_markup(text: str, *, label: str = "About this calculator") -> str:
    """Render a crawler-visible explanatory note below the page title."""

    return (
        '<section class="calc-intro-panel">'
        f'<p class="calc-section-label">{escape_html(label)}</p>'
        '<div class="calc-note">'
        f"<p>{escape_html(text)}</p>"
        f'<p class="quiet-motto">{escape_html(FRAMEWORK_MOTTO)}</p>'
        "</div>"
        "</section>"
    )


def source_repo_note_markup() -> str:
    """Render a compact source-repository callout for the calculator page."""

    return (
        '<section class="calc-intro-panel">'
        '<p class="calc-section-label">Calculator code</p>'
        '<div class="calc-note">'
        '<p>The alpha public source release of the calculator is available on GitHub, including the Python engine, theorem graph, tests, bundle builder, and reproducible CLI surfaces.</p>'
        f'<p><a class="calc-link" href="{escape_html(SOURCE_REPO_URL)}">Open the calculator source code</a></p>'
        "</div>"
        "</section>"
    )


def organization_schema() -> dict[str, object]:
    """Return site-wide Organization markup for the IO Framework."""

    return {
        "@type": "Organization",
        "@id": "https://dfife.github.io/#organization",
        "name": "The Interior Observer Framework",
        "url": "https://dfife.github.io/",
        "description": (
            "The Interior Observer Framework is a black hole cosmology research "
            "program publishing theorem-grade predictions and reproducible "
            "cosmological calculator outputs with zero fitted parameters."
        ),
        "founder": {"@type": "Person", "name": "David Fife"},
        "sameAs": [
            "https://github.com/dfife/io-framework-public",
            "https://zenodo.org/communities/interior-observer",
            "https://orcid.org/0009-0001-0090-5825",
        ],
    }


def calculator_application_schema() -> dict[str, object]:
    """Return a page-level SoftwareApplication record for the calculator."""

    return {
        "@type": "SoftwareApplication",
        "@id": "https://dfife.github.io/calculator.html#application",
        "name": "Interior Observer cosmological calculator",
        "url": "https://dfife.github.io/calculator.html",
        "applicationCategory": "ScientificApplication",
        "operatingSystem": "Web",
        "creator": {"@id": "https://dfife.github.io/#organization"},
        "description": (
            "A cosmological calculator for the Interior Observer Framework, a "
            "black hole cosmology publishing theorem-grade predictions with "
            "zero fitted parameters."
        ),
        "keywords": [
            "Interior Observer Framework",
            "black hole cosmology",
            "cosmological calculator",
            "zero fitted parameters",
            "theorem-grade predictions",
        ],
    }


def calculator_data_catalog_schema() -> dict[str, object]:
    """Return the DataCatalog record referenced by calculator datasets."""

    return {
        "@type": "DataCatalog",
        "@id": "https://dfife.github.io/calculator.html#catalog",
        "name": "Interior Observer Framework calculator datasets",
        "url": "https://dfife.github.io/calculator.html",
        "creator": {"@id": "https://dfife.github.io/#organization"},
        "description": (
            "Machine-readable theorem-bearing calculator outputs published on "
            "the Interior Observer Framework calculator surface."
        ),
        "license": DATASET_LICENSE_URL,
    }


def theorem_dictionary_schema() -> dict[str, object]:
    """Return a page-level scholarly record for the theorem dictionary."""

    return {
        "@type": "ScholarlyArticle",
        "@id": "https://dfife.github.io/calculator-theorems.html#article",
        "headline": "Interior Observer calculator theorem dictionary",
        "url": "https://dfife.github.io/calculator-theorems.html",
        "author": {"@id": "https://dfife.github.io/#organization"},
        "publisher": {"@id": "https://dfife.github.io/#organization"},
        "description": (
            "Standalone theorem dictionary for the Interior Observer Framework "
            "cosmological calculator, carrying self-contained theorem text, "
            "proof outlines, scope boundaries, and claim-status labels."
        ),
        "keywords": [
            "Interior Observer Framework",
            "black hole cosmology",
            "theorem dictionary",
            "cosmological calculator",
            "theorem-grade predictions",
        ],
    }


def output_dataset_schema(
    output: dict[str, object],
    graph: dict[str, dict[str, object]],
) -> dict[str, object]:
    """Return one Dataset record for a published output card."""

    provenance = output["provenance"]  # type: ignore[assignment]
    root_id = provenance["root_node"]  # type: ignore[index]
    root_node = graph[root_id]
    output_id = str(output["output_id"])
    dataset: dict[str, object] = {
        "@type": "Dataset",
        "@id": f"https://dfife.github.io/calculator.html#output-{output_id}",
        "name": str(output["label"]),
        "url": "https://dfife.github.io/calculator.html",
        "creator": {"@id": "https://dfife.github.io/#organization"},
        "includedInDataCatalog": {"@id": "https://dfife.github.io/calculator.html#catalog"},
        "license": DATASET_LICENSE_URL,
        "description": (
            f"{output['claim_status']}. {root_node['label']}. "
            f"{root_node['scope']}"
        ),
        "keywords": [
            "Interior Observer Framework",
            "black hole cosmology",
            "zero fitted parameters",
            "theorem-grade predictions",
            str(output["output_id"]),
        ],
        "measurementTechnique": str(output["claim_status"]),
        "variableMeasured": [
            {
                "@type": "PropertyValue",
                "name": str(output["primary_key"]),
                "value": output["primary_value"],
                "unitText": str(output.get("units") or ""),
            }
        ],
        "additionalProperty": [
            {
                "@type": "PropertyValue",
                "name": "claim status",
                "value": str(output["claim_status"]),
            },
            {
                "@type": "PropertyValue",
                "name": "theorem authority",
                "value": str(root_node["label"]),
            },
            {
                "@type": "PropertyValue",
                "name": "theorem node id",
                "value": str(root_id),
            },
        ],
    }
    comparison = OUTPUT_SCHEMA_COMPARISONS.get(output_id, {})
    if comparison:
        variable_measured = dataset["variableMeasured"]  # type: ignore[assignment]
        assert isinstance(variable_measured, list)
        measured_value = comparison.get("measured_value")
        if measured_value is not None:
            variable_measured.append(
                {
                    "@type": "PropertyValue",
                    "name": str(comparison.get("measured_label", "measured value")),
                    "value": measured_value,
                    "unitText": str(
                        comparison.get("units")
                        or output.get("units")
                        or ""
                    ),
                }
            )
        tension_sigma = comparison.get("tension_sigma")
        if tension_sigma is not None:
            dataset["additionalProperty"].append(  # type: ignore[union-attr]
                {
                    "@type": "PropertyValue",
                    "name": "tension sigma",
                    "value": tension_sigma,
                }
            )
        reference_name = comparison.get("reference_name")
        if reference_name is not None:
            dataset["additionalProperty"].append(  # type: ignore[union-attr]
                {
                    "@type": "PropertyValue",
                    "name": "reference dataset",
                    "value": reference_name,
                }
            )
    direct_comparison = output.get("direct_observable_comparison")
    if isinstance(direct_comparison, dict):
        dataset["additionalProperty"].append(  # type: ignore[union-attr]
            {
                "@type": "PropertyValue",
                "name": "direct observable comparison",
                "value": str(direct_comparison.get("label", "")),
            }
        )
    return dataset


def render_json_ld(objects: list[dict[str, object]]) -> str:
    """Render a single JSON-LD graph script."""

    payload = {"@context": "https://schema.org", "@graph": objects}
    return (
        '<script type="application/ld+json">'
        + json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        + "</script>"
    )


def calculator_json_ld(bundle: dict[str, object]) -> str:
    """Return calculator-page JSON-LD for outputs and the site org."""

    graph = bundle["provenance_graph"]  # type: ignore[assignment]
    outputs = bundle["explained_outputs"]  # type: ignore[assignment]
    objects: list[dict[str, object]] = [
        organization_schema(),
        calculator_application_schema(),
        calculator_data_catalog_schema(),
    ]
    objects.extend(output_dataset_schema(output, graph) for output in outputs.values())  # type: ignore[union-attr]
    return render_json_ld(objects)


def theorem_dictionary_json_ld() -> str:
    """Return theorem-dictionary page JSON-LD."""

    return render_json_ld([organization_schema(), theorem_dictionary_schema()])


def calculator_cards_markup(bundle: dict[str, object]) -> str:
    """Render the full output-card stack."""

    graph = bundle["provenance_graph"]  # type: ignore[assignment]
    outputs = bundle["explained_outputs"]  # type: ignore[assignment]
    grouped_ids = (
        (
            "Geometry",
            (
                "branch_h0",
                "branch_omega_m",
                "branch_omega_k",
                "branch_omega_lambda",
                "bare_master_clock_age",
            ),
        ),
        ("Temperature", ("active_t_cmb",)),
        (
            "Acoustic Scale",
            (
                "theta_star_theorem",
                "tt_first_peak_support",
                "branch_rd_mpc",
                "scalar_tilt_ns",
                "native_scalar_amplitude_as",
            ),
        ),
        (
            "Nucleosynthesis",
            (
                "bbn_deuterium_ratio",
                "bbn_helium_fraction",
                "bbn_lithium_ratio",
            ),
        ),
        ("Structure", ("baryon_fraction_fb", "eta_io_late")),
        (
            "Recombination",
            ("recombination_point_z_1100", "background_snapshot_z_0_57"),
        ),
    )

    def render_output_card(output_dict: dict[str, object]) -> str:
        if output_dict["output_id"] == "theta_star_theorem":
            return theta_card(output_dict, graph)
        return generic_output_card(output_dict, graph)

    sections = []
    seen: set[str] = set()
    for label, output_ids in grouped_ids:
        cards = []
        for output_id in output_ids:
            output_dict = outputs.get(output_id)  # type: ignore[union-attr]
            if output_dict is None:
                continue
            seen.add(output_id)
            cards.append(render_output_card(output_dict))
        if not cards:
            continue
        sections.append(
            '<details class="calc-output-group">'
            '<summary class="calc-group-summary">'
            f'<span class="calc-group-label">{escape_html(label)}</span>'
            '<span class="calc-chevron" aria-hidden="true">›</span>'
            "</summary>"
            '<div class="calc-group-stack">'
            f"{''.join(cards)}"
            "</div>"
            "</details>"
        )

    remaining_cards = []
    for output_id, output_dict in outputs.items():  # type: ignore[union-attr]
        if output_id in seen:
            continue
        remaining_cards.append(render_output_card(output_dict))
    if remaining_cards:
        sections.append(
            '<details class="calc-output-group">'
            '<summary class="calc-group-summary">'
            '<span class="calc-group-label">Additional</span>'
            '<span class="calc-chevron" aria-hidden="true">›</span>'
            "</summary>"
            '<div class="calc-group-stack">'
            f"{''.join(remaining_cards)}"
            "</div>"
            "</details>"
        )
    return "".join(sections)


def _page_shell(
    *,
    title: str,
    description: str,
    canonical: str,
    overline: str,
    heading: str,
    lede: str,
    link_href: str,
    link_label: str,
    mount_id: str,
    mount_content: str,
    intro_panels: str = "",
    structured_data: str = "",
) -> str:
    """Render the shared calculator-site shell."""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="google-site-verification" content="ihikTXBZEMflSxSz3z3o8zG1uNf-3ClCW-JLcyYna04">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <title>{escape_html(title)}</title>
  <meta
    name="description"
    content="{escape_html(description)}"
  >
  <link rel="canonical" href="{escape_html(canonical)}">
  <link rel="icon" href="data:,">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@300;400;500&display=swap"
    rel="stylesheet"
  >
  <link rel="stylesheet" href="assets/css/site.css">
  {structured_data}
</head>
<body class="calculator-body">
  <div class="site-shell">
    <header class="site-header dark">
      <div class="nav-wrap">
        <a class="brand-block" href="index.html" aria-label="The Interior Observer Framework home">
          <span class="brand-kicker">IO Framework</span>
          <span class="brand-title">The Interior Observer Framework</span>
        </a>
        <nav class="nav-links" aria-label="Primary">
          <a class="nav-link" href="index.html">Home</a>
          <a class="nav-link" href="bridge-map.html">Bridge Map</a>
          <a class="nav-link" href="papers.html">Papers</a>
          <a class="nav-link active" href="calculator.html">Calculator</a>
          <a class="nav-link" href="lithium.html">Lithium</a>
          <a class="nav-link" href="scorecard.html">Scorecard</a>
        </nav>
      </div>
    </header>

    <main class="calc-page">
      <div class="calc-column">
        <header class="calc-intro">
          <p class="calc-overline">{escape_html(overline)}</p>
          <h1 class="calc-title">{escape_html(heading)}</h1>
          <p class="calc-lede">
            {escape_html(lede)}
          </p>
          <div class="calc-link-row">
            <a class="calc-link" href="{escape_html(link_href)}">{escape_html(link_label)}</a>
          </div>
        </header>

        {intro_panels}

        <div class="calc-card-stack" id="{escape_html(mount_id)}" data-prerendered="true">
          {mount_content}
        </div>
      </div>
    </main>

    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-title">David Fife | Independent Researcher | david@fife.cc</div>
        <div>Multi-AI Collaboration: Claude (Anthropic), Codex/ChatGPT (OpenAI), Gemini (Google DeepMind)</div>
        <div class="footer-small">All papers open-access on Zenodo.</div>
        <div class="footer-small">Copyright © 2026 David Fife. All rights reserved.</div>
      </div>
    </footer>
  </div>

  <script src="assets/js/calculator.js" defer></script>
</body>
</html>
"""


def render_public_calculator_page(bundle: dict[str, object]) -> str:
    """Render the output-card page from the generated bundle."""

    return _page_shell(
        title="IO Calculator Theorem Surface",
        description=(
            "Interior Observer Framework black hole cosmology calculator with "
            "zero fitted parameters, theorem-grade predictions, and "
            "machine-readable output provenance."
        ),
        canonical="https://dfife.github.io/calculator.html",
        overline="Theorem-grade surface",
        heading="Interior Observer Calculator",
        lede=(
            "The Interior Observer Framework is a black hole cosmology and "
            "cosmological calculator publishing theorem-grade predictions with "
            "zero fitted parameters. Every published output expands into claim "
            "status, direct-observable comparison, theorem chain, and explicit "
            "scope boundary."
        ),
        link_href="calculator-theorems.html",
        link_label="Open theorem dictionary",
        mount_id="calculator-card-stack",
        mount_content=calculator_cards_markup(bundle),
        intro_panels=(
            about_note_markup(
                "This Interior Observer Framework calculator publishes theorem-grade "
                "predictions from a black hole cosmology with zero fitted "
                "parameters. The current live surface spans geometry, "
                "nucleosynthesis, recombination, acoustic-scale observables, "
                "and the first IO-native CMB TT first-peak support carrier."
            )
            + source_repo_note_markup()
            + redshift_widget_markup()
            + prediction_summary_markup()
        ),
        structured_data=calculator_json_ld(bundle),
    )


def render_public_theorem_dictionary_page(bundle: dict[str, object]) -> str:
    """Render the standalone theorem dictionary page from the generated bundle."""

    return _page_shell(
        title="IO Calculator Theorem Dictionary",
        description=(
            "Standalone theorem dictionary for the Interior Observer Framework "
            "cosmological calculator, with theorem-grade predictions, claim "
            "boundaries, and crawler-visible theorem text."
        ),
        canonical="https://dfife.github.io/calculator-theorems.html",
        overline="Reference page",
        heading="Calculator Theorem Dictionary",
        lede=(
            "Standalone reference for the Interior Observer Framework black "
            "hole cosmology calculator. This theorem dictionary carries the "
            "self-contained theorem text behind the zero-fitted-parameter "
            "cosmological calculator and its theorem-grade predictions."
        ),
        link_href="calculator.html",
        link_label="Back to output cards",
        mount_id="theorem-dictionary-stack",
        mount_content=theorem_dictionary_markup(bundle),
        intro_panels=(
            about_note_markup(
                "This theorem dictionary is the public reference surface for the "
                "Interior Observer Framework cosmological calculator. It keeps "
                "the theorem text, scope boundaries, and claim statuses visible "
                "to readers and crawlers without requiring the paper archive."
            )
            + prediction_summary_markup()
        ),
        structured_data=theorem_dictionary_json_ld(),
    )
