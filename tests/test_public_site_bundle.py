"""Checks that the public website receives the bundle and prerendered theorem HTML."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CALCULATOR_ROOT = Path(__file__).resolve().parents[1]
LOCAL_BUNDLE = CALCULATOR_ROOT / "data" / "aio_calculator_bundle.json"
LOCAL_HTML = CALCULATOR_ROOT / "calculator.html"
LOCAL_THEOREMS_HTML = CALCULATOR_ROOT / "calculator-theorems.html"
PUBLIC_SITE_ROOT = CALCULATOR_ROOT.parent / "tmp" / "dfife.github.io"
PUBLIC_BUNDLE = PUBLIC_SITE_ROOT / "data" / "aio_calculator_bundle.json"
PUBLIC_INDEX_HTML = PUBLIC_SITE_ROOT / "index.html"
PUBLIC_HTML = PUBLIC_SITE_ROOT / "calculator.html"
PUBLIC_THEOREMS_HTML = PUBLIC_SITE_ROOT / "calculator-theorems.html"
PUBLIC_LITHIUM_HTML = PUBLIC_SITE_ROOT / "lithium.html"
PUBLIC_SCORECARD_HTML = PUBLIC_SITE_ROOT / "scorecard.html"
PUBLIC_SITEMAP = PUBLIC_SITE_ROOT / "sitemap_index.xml"
PUBLIC_JS = PUBLIC_SITE_ROOT / "assets" / "js" / "calculator.js"


def test_build_bundle_exports_local_bundle_and_pages() -> None:
    """`build_bundle.py` should always refresh the repo-local bundle and previews."""

    subprocess.run(
        [sys.executable, "build_bundle.py"],
        cwd=CALCULATOR_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(LOCAL_BUNDLE.read_text(encoding="utf-8"))
    assert "theta_star_theorem" in payload["explained_outputs"]
    assert "tt_first_peak_support" in payload["explained_outputs"]
    assert "branch_h0" in payload["explained_outputs"]
    assert "native_scalar_amplitude_as" in payload["explained_outputs"]
    assert "bbn_lithium_ratio" in payload["explained_outputs"]
    assert payload["explained_outputs"]["theta_star_theorem"]["provenance"]["root_node"] == (
        "calculator.active_branch_theta_star"
    )
    assert LOCAL_HTML.exists()
    assert LOCAL_THEOREMS_HTML.exists()


def test_local_preview_prerenders_calculator_and_theorem_pages() -> None:
    """The repo-local previews should contain theorem content directly in HTML."""

    html = LOCAL_HTML.read_text(encoding="utf-8")
    theorems_html = LOCAL_THEOREMS_HTML.read_text(encoding="utf-8")

    assert "application/ld+json" in html
    assert "Interior Observer Framework is a black hole cosmology and cosmological calculator" in html
    assert "What can this predict" in html
    assert 'id="calculator-card-stack"' in html
    assert "Conditional/scoped/verified TT first-peak support on the repaired active-branch canonical carrier (n_max = 501), with inherited-FULL Stage-2 history and equal-rate typed Thomson specialization." in html
    assert "shell-ceiling drift remains open" in html
    assert 'data-prerendered="true"' in html
    assert "application/ld+json" in theorems_html
    assert "Calculator Theorem Dictionary" in theorems_html
    assert "Typed R Site-uniqueness Theorem" in theorems_html
    assert "Proof outline" in theorems_html
    assert "Scope boundary" in theorems_html


def test_public_site_prerenders_when_site_clone_is_present() -> None:
    """The website mirror should still be refreshed when the site repo is present."""

    if not PUBLIC_SITE_ROOT.exists():
        return

    subprocess.run(
        [sys.executable, "build_bundle.py"],
        cwd=CALCULATOR_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    html = PUBLIC_HTML.read_text(encoding="utf-8")
    index_html = PUBLIC_INDEX_HTML.read_text(encoding="utf-8")
    theorems_html = PUBLIC_THEOREMS_HTML.read_text(encoding="utf-8")
    lithium_html = PUBLIC_LITHIUM_HTML.read_text(encoding="utf-8")
    scorecard_html = PUBLIC_SCORECARD_HTML.read_text(encoding="utf-8")
    sitemap_xml = PUBLIC_SITEMAP.read_text(encoding="utf-8")
    js = PUBLIC_JS.read_text(encoding="utf-8")

    assert "application/ld+json" in html
    assert 'name="robots"' in html
    assert 'name="googlebot"' in html
    assert "ScientificApplication" in html
    assert '"@type":"Dataset"' in html
    assert "Interior Observer Framework is a black hole cosmology and cosmological calculator" in html
    assert "What can this predict" in html
    assert "T_CMB (0.3σ from FIRAS)" in html
    assert "Hubble tension resolved (max 0.57σ across 6 methods)" in html
    assert "Redshift calculator" in html
    assert "Try it yourself" in html
    assert 'id="redshift-widget"' in html
    assert 'id="redshift-widget-input"' in html
    assert 'id="redshift-widget-results"' in html
    assert 'href="https://zenodo.org/records/19376058/latest"' in html
    assert ">Paper 30</a> background surface" in html
    assert "lithium.html" in html
    assert "scorecard.html" in html
    assert 'id="calculator-card-stack"' in html
    assert 'data-prerendered="true"' in html
    assert "calculator-theorems.html" in html
    assert "Loading theorem surface" not in html
    assert html.count('class="calc-output-group"') == 6
    assert html.count('class="calc-group-summary"') == 6
    assert "Geometry" in html
    assert "Temperature" in html
    assert "Acoustic Scale" in html
    assert "Nucleosynthesis" in html
    assert "Structure" in html
    assert "Recombination" in html
    assert "Canonical TT first-peak support" in html
    assert "Conditional/scoped/verified TT first-peak support on the repaired active-branch canonical carrier (n_max = 501), with inherited-FULL Stage-2 history and equal-rate typed Thomson specialization." in html
    assert "shell-ceiling drift remains open" in html
    assert "Active-branch H0" in html
    assert "Baryon dictionary fraction" in html
    assert "Conditional BBN lithium scorecard" in html
    assert "Phase-equivalent Selector Theorem" in html
    assert "Packet Coefficient Fixing Theorem" in html
    assert "Why this differs from Planck" in html
    assert "Direct observable" in html
    assert "Proof outline" in html
    assert "Scope boundary" in html
    assert "application/ld+json" in theorems_html
    assert 'name="robots"' in theorems_html
    assert 'name="googlebot"' in theorems_html
    assert "ScholarlyArticle" in theorems_html
    assert "This theorem dictionary is the public reference surface for the Interior Observer Framework cosmological calculator." in theorems_html
    assert "What can this predict" in theorems_html
    assert "lithium.html" in theorems_html
    assert "scorecard.html" in theorems_html
    assert 'id="theorem-dictionary-stack"' in theorems_html
    assert 'data-prerendered="true"' in theorems_html
    assert "Loading theorem dictionary" not in theorems_html
    assert "Calculator Theorem Dictionary" in theorems_html
    assert "Typed R Site-uniqueness Theorem" in theorems_html
    assert "Typed Split Thomson-history Realization Theorem" in theorems_html
    assert "Statement" in theorems_html
    assert "Premises" in theorems_html
    assert "Proof outline" in theorems_html
    assert "Supporting references" in theorems_html
    assert "Scoped Closed-scalar Pipeline Theorem" in theorems_html
    assert "conditional / scoped" in theorems_html
    assert "derived / scoped as maps" in theorems_html
    assert "No silent one-slot collapse on the hierarchy-wide perturbation" in theorems_html
    assert "application/ld+json" in index_html
    assert 'name="robots"' in index_html
    assert 'name="googlebot"' in index_html
    assert "The Interior Observer Framework is a black hole cosmology with a cosmological calculator" in index_html
    assert "theorem-grade predictions" in index_html
    assert "zero fitted parameters" in index_html
    assert "CMB first peak ell = 224" in index_html
    assert "lithium.html" in index_html
    assert "scorecard.html" in index_html
    assert "Read the Lithium Story" in index_html
    assert "View the Scorecard" in index_html
    assert "Interior Observer Framework" in lithium_html
    assert "application/ld+json" in lithium_html
    assert 'name="robots"' in lithium_html
    assert 'name="googlebot"' in lithium_html
    assert "ScholarlyArticle" in lithium_html
    assert "The Cosmological Lithium Problem, Resolved" in lithium_html
    assert "cosmological lithium problem resolved" in lithium_html
    assert "BBN lithium resolved" in lithium_html
    assert "calculator.html#output-bbn_lithium_ratio" in lithium_html
    assert "zenodo.org/records/19219282/latest" in lithium_html
    assert "application/ld+json" in scorecard_html
    assert 'name="robots"' in scorecard_html
    assert 'name="googlebot"' in scorecard_html
    assert "Dataset" in scorecard_html
    assert "Zero fitted cosmological parameters. One measured mass. 20+ predictions within 1σ of direct measurement." in scorecard_html
    assert "χ² = 2.42 across 8 independent observables" in scorecard_html
    assert "<th>Observable</th>" in scorecard_html
    assert "DESI evolving-w" in scorecard_html
    assert "Full high-ℓ TT spectrum" in scorecard_html
    assert 'href="https://zenodo.org/records/19561708/latest"' in scorecard_html
    assert ">Paper 35</a> baryogenesis obstruction" in scorecard_html
    assert "calculator.html#output-tt_first_peak_support" in scorecard_html
    assert "fetch(bundlePath)" not in js
    assert "data-prerendered='true'" in js
    assert "hashchange" in js
    assert "computeBackgroundSnapshot" in js
    assert "redshift-widget" in js
    assert "https://dfife.github.io/calculator.html" in sitemap_xml
    assert "https://dfife.github.io/calculator-theorems.html" in sitemap_xml
    assert "https://dfife.github.io/lithium.html" in sitemap_xml
    assert "https://dfife.github.io/scorecard.html" in sitemap_xml
