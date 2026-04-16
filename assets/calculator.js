/*
 * Browser mirror of the late-time background engine in
 * `src/aio_calculator/model.py`.
 *
 * This duplication is intentional: the calculator is meant to be publishable as
 * a static folder with no server-side runtime. If the Python formulas change,
 * update the matching logic here and keep the tests/bundle in sync.
 */

const bundlePath = "data/aio_calculator_bundle.json";
const SPEED_OF_LIGHT_KM_S = 299792.458;
const MPC_IN_METERS = 3.0856775814913673e22;
const GYR_IN_SECONDS = 365.25 * 24 * 3600 * 1e9;
const INTEGRATION_STEPS = 4096;

function simpson(fn, a, b, n) {
  let steps = n;
  if (steps % 2 === 1) steps += 1;
  const h = (b - a) / steps;
  let total = fn(a) + fn(b);
  for (let i = 1; i < steps; i += 1) {
    total += (i % 2 === 1 ? 4 : 2) * fn(a + i * h);
  }
  return total * h / 3;
}

function formatNumber(value, digits = 6) {
  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
  });
}

function formatFixed(value, digits = 6) {
  return Number(value).toFixed(digits);
}

function formatSci(value, digits = 6) {
  return Number(value).toExponential(digits);
}

function statusClass(status) {
  const lower = String(status).toLowerCase();
  if (lower.includes("conditional")) return "status-conditional";
  if (lower.includes("open") || lower.includes("not")) return "status-open";
  return "status-derived";
}

function computeSnapshot(bundle, z) {
  // This mirrors `CurvedBackgroundModel.snapshot()` from the Python engine so
  // the browser calculator can evaluate arbitrary z values without needing
  // server-side code generation.
  const branch = bundle.branch;
  const e = (redshift) => {
    const zp1 = 1 + redshift;
    return Math.sqrt(
      branch.Omega_r * zp1 ** 4 +
      branch.Omega_m * zp1 ** 3 +
      branch.Omega_k * zp1 ** 2 +
      branch.Omega_lambda
    );
  };
  // Use the same `u = ln(1+z)` integration variable as the Python engine.
  const chi = simpson((u) => {
    const redshift = Math.exp(u) - 1;
    return Math.exp(u) / e(redshift);
  }, 0, Math.log1p(z), INTEGRATION_STEPS);
  const sK = (chiValue) => {
    if (Math.abs(branch.Omega_k) < 1e-15) return chiValue;
    if (branch.Omega_k > 0) {
      const root = Math.sqrt(branch.Omega_k);
      return Math.sinh(root * chiValue) / root;
    }
    const root = Math.sqrt(-branch.Omega_k);
    return Math.sin(root * chiValue) / root;
  };
  const dm = (SPEED_OF_LIGHT_KM_S / branch.H0) * sK(chi);
  const dh = SPEED_OF_LIGHT_KM_S / (branch.H0 * e(z));
  const da = dm / (1 + z);
  const dl = dm * (1 + z);
  const dv = (dm * dm * dh * z) ** (1 / 3);
  const hubbleGyrInv = (branch.H0 * 1000 / MPC_IN_METERS) * GYR_IN_SECONDS;
  const lookback = simpson(
    (u) => 1 / e(Math.exp(u) - 1),
    0,
    Math.log1p(z),
    INTEGRATION_STEPS
  ) / hubbleGyrInv;
  const age = simpson(
    (u) => 1 / e(Math.exp(-u) - 1),
    Math.log(1e-10),
    Math.log(1 / (1 + z)),
    INTEGRATION_STEPS
  ) / hubbleGyrInv;
  return {
    H_km_s_mpc: branch.H0 * e(z),
    DM_mpc: dm,
    DA_mpc: da,
    DL_mpc: dl,
    DH_mpc: dh,
    DV_mpc: dv,
    lookback_gyr: lookback,
    age_gyr: age,
    DM_over_rd: dm / branch.rd_mpc,
    DH_over_rd: dh / branch.rd_mpc,
    DV_over_rd: dv / branch.rd_mpc,
  };
}

function metricCard(label, value, note) {
  return `
    <article class="metric-card">
      <div class="metric-label">${label}</div>
      <div class="metric-value">${value}</div>
      ${note ? `<div class="metric-note">${note}</div>` : ""}
    </article>
  `;
}

function pathLabel(path) {
  return String(path).split("/").filter(Boolean).pop();
}

function theoremStep(index, node) {
  return `
    <details class="why-step" ${index === 0 ? "open" : ""}>
      <summary>
        <span>${index + 1}. ${node.label}</span>
        <span class="status-pill ${statusClass(node.claim_status)}">${node.claim_status}</span>
      </summary>
      <div class="why-body">
        <p>${node.statement}</p>
        <p><strong>Scope.</strong> ${node.scope}</p>
        ${node.notes.length ? node.notes.map((note) => `<p>${note}</p>`).join("") : ""}
        <div class="mini-links">
          ${node.authority_paths.map((path) => `<span class="mini-link">${pathLabel(path)}</span>`).join("")}
        </div>
      </div>
    </details>
  `;
}

async function main() {
  const response = await fetch(bundlePath);
  const bundle = await response.json();

  const redshiftInput = document.getElementById("redshift-input");
  const resultsGrid = document.getElementById("results-grid");

  // Populate the static explanatory sections from the generated bundle so the
  // page ships with the same claim boundaries as the Python source of truth.
  document.getElementById("scope-badges").innerHTML = bundle.metadata.calculator_scope
    .map((item) => `<span class="badge">${item}</span>`)
    .join("");

  const branchGrid = document.getElementById("branch-grid");
  branchGrid.innerHTML = [
    metricCard("H0", `${formatFixed(bundle.branch.H0, 6)} km/s/Mpc`, "Paper 10 legacy branch"),
    metricCard("Omega_m", formatFixed(bundle.branch.Omega_m, 9), "Active projected matter slot"),
    metricCard("Omega_k", formatFixed(bundle.branch.Omega_k, 9), "Closed positive-curvature branch"),
    metricCard("Omega_lambda", formatFixed(bundle.branch.Omega_lambda, 9), "Constant observer-side vacuum slot"),
    metricCard("r_d", `${formatFixed(bundle.branch.rd_mpc, 9)} Mpc`, "Carried active-branch pre-drag ruler"),
    metricCard("omega_b,geom", formatFixed(bundle.baryons.omega_b_geom_h2, 12), "Preferred physical-density slot"),
    metricCard("eta_IO,late", formatSci(bundle.derived_examples.eta_io_late, 6), "Paper 35 preferred convention"),
    metricCard("age(today)", `${formatFixed(bundle.derived_examples.age_today_gyr, 6)} Gyr`, "Reproduces paper 30 reported age"),
  ].join("");

  const theta = bundle.explained_outputs.theta_star_theorem;
  document.getElementById("theta-output-grid").innerHTML = [
    metricCard("100theta_*", formatFixed(theta.theta_star_100, 12), "Derived / scoped active-branch output"),
    metricCard("theta_obs", `${formatFixed(theta.theta_obs_deg, 12)} deg`, "Observer-side acoustic angle"),
    metricCard("z_sel", formatFixed(theta.selector_leaf_z, 12), "Carried physical selector leaf"),
    metricCard("ell_peak", formatFixed(theta.ell_peak, 6), "Direct first TT peak observable"),
  ].join("");

  document.getElementById("theta-summary-panel").innerHTML = `
    <div class="stat-line"><span>Claim status</span><strong class="status-pill ${statusClass(theta.claim_status)}">${theta.claim_status}</strong></div>
    <div class="stat-line"><span>Zero fitted parameters</span><strong>${theta.zero_fitted_parameters ? "yes" : "no"}</strong></div>
    <div class="stat-line"><span>Conditional on</span><strong>${theta.conditional_on_premises.join(", ")}</strong></div>
    <div class="stat-line"><span>Planck flat reference</span><strong>${formatFixed(theta.comparison_context.planck_flat_reference_theta_mc_100, 5)}</strong></div>
    <div class="stat-line"><span>Planck closed refit</span><strong>${formatFixed(theta.comparison_context.planck_closed_reference_theta_mc_100, 5)}</strong></div>
    <div class="comparison-card">
      <p><strong>Calculator statement.</strong> This number differs from Planck's reported value because Planck assumes flat space. The IO framework derives closed space. The direct observable — the first peak position — agrees.</p>
      <p>${theta.geometry_explanation}</p>
      <p>${theta.comparison_context.statement}</p>
    </div>
  `;

  const thetaComparison = theta.direct_observable_comparison;
  const thetaNodes = theta.provenance.nodes;
  const thetaChain = theta.provenance.chain_ids.map((nodeId, index) => theoremStep(index, thetaNodes[nodeId])).join("");
  const thetaSupporting = theta.provenance.supporting_node_ids.map((nodeId, index) => theoremStep(index, thetaNodes[nodeId])).join("");
  document.getElementById("theta-why-panel").innerHTML = `
    <div class="comparison-card">
      <div class="stat-line"><span>Predicted first peak</span><strong>${formatFixed(thetaComparison.predicted_value, 6)}</strong></div>
      <div class="stat-line"><span>Observed reference peak</span><strong>${formatFixed(thetaComparison.observed_reference, 3)}</strong></div>
      <div class="stat-line"><span>Delta</span><strong>${formatFixed(thetaComparison.delta, 6)}</strong></div>
      <p>${thetaComparison.note}</p>
    </div>
    <div class="explain-card">
      <p><strong>Scope boundary.</strong></p>
      ${theta.scope_boundary.map((item) => `<p>${item}</p>`).join("")}
      <p><strong>Non-claims.</strong></p>
      ${theta.non_claims.map((item) => `<p>${item}</p>`).join("")}
    </div>
    ${thetaChain}
    ${thetaSupporting ? `<div class="explain-card"><p><strong>Supporting geometry context.</strong></p></div>${thetaSupporting}` : ""}
  `;

  document.getElementById("eta-panel").innerHTML = `
    <div class="stat-line"><span>Preferred eta_IO,late</span><strong>${formatSci(bundle.paper35_eta.closure.preferred_eta, 6)}</strong></div>
    <div class="stat-line"><span>Closure status</span><strong>${bundle.paper35_eta.closure.status}</strong></div>
    <div class="stat-line"><span>Convention</span><strong>${bundle.paper35_eta.closure.preferred_convention}</strong></div>
    <p>${bundle.paper35_eta.closure.statement}</p>
  `;

  document.getElementById("dark-energy-panel").innerHTML = `
    <div class="stat-line"><span>Active observer-side EOS</span><strong>w = -1</strong></div>
    <div class="stat-line"><span>Flat reinterpretation</span><strong>(w0, wa) = (${formatFixed(bundle.paper35_dark_energy_reinterpretation.flat_cpl_best_fit_to_active_io_bao.w0, 3)}, ${formatFixed(bundle.paper35_dark_energy_reinterpretation.flat_cpl_best_fit_to_active_io_bao.wa, 3)})</strong></div>
    <div class="stat-line"><span>Status</span><strong>${bundle.paper35_dark_energy.status}</strong></div>
    <p>${bundle.paper35_dark_energy.resolution}</p>
  `;

  document.getElementById("paper31-panel").innerHTML = `
    <div class="stat-line"><span>Pre-drag ruler</span><strong>${formatFixed(bundle.paper31_summary.geometric_pre_drag_ruler.r_d_mpc, 9)} Mpc</strong></div>
    <div class="stat-line"><span>Galaxy block chi2</span><strong>${formatFixed(bundle.paper31_summary.bao_galaxy_block.galaxy_block_chi2_with_kernel, 6)}</strong></div>
    <div class="stat-line"><span>S8_weyl</span><strong>${formatFixed(bundle.paper31_summary.sigma8_s8_eg.S8_weyl, 6)}</strong></div>
    <p>The active branch no longer carries the old Schur-era scalar BAO near-hit. The surviving paper 31 surface is the anisotropic legacy-branch kernel package.</p>
  `;

  document.getElementById("closed-list").innerHTML = bundle.metadata.calculator_scope
    .map((item) => `<li>${item}</li>`)
    .join("");

  document.getElementById("open-list").innerHTML = bundle.metadata.calculator_boundaries
    .map((item) => `<li>${item}</li>`)
    .join("");

  document.getElementById("paper-grid").innerHTML = bundle.papers.map((paper) => `
    <article class="paper-card">
      <span class="paper-meta">Paper ${paper.paper} · ${paper.era}</span>
      <h3>${paper.short_title}</h3>
      <p class="paper-note">${paper.summary}</p>
      <div class="source-link">${paper.zenodo}</div>
    </article>
  `).join("");

  document.getElementById("provenance-output-grid").innerHTML = Object.entries(bundle.explained_output_specs).map(([key, spec]) => `
    <article class="source-card">
      <div>
        <span class="source-label">Explained output</span>
        <h3>${spec.label}</h3>
        <p class="source-note">${key}</p>
        <p class="paper-note">${spec.note}</p>
      </div>
      <div>
        <div class="status-pill ${statusClass(spec.claim_status)}">${spec.claim_status}</div>
        <div class="status-pill ${statusClass(spec.provenance_status)}">${spec.provenance_status}</div>
      </div>
    </article>
  `).join("");

  document.getElementById("source-grid").innerHTML = bundle.source_code_links.map((source) => `
    <article class="source-card">
      <div>
        <span class="source-label">Local source</span>
        <h3>${source.label}</h3>
        <p class="source-note">${source.href}</p>
      </div>
      <a class="source-link" href="${source.href}">Open file</a>
    </article>
  `).join("");

  function updateResults() {
    const z = Math.max(0, Number(redshiftInput.value || 0));
    const snapshot = computeSnapshot(bundle, z);
    resultsGrid.innerHTML = [
      metricCard("H(z)", `${formatFixed(snapshot.H_km_s_mpc, 6)} km/s/Mpc`, "Observer-side active branch"),
      metricCard("D_M(z)", `${formatFixed(snapshot.DM_mpc, 6)} Mpc`, "Closed-FRW transverse distance"),
      metricCard("D_A(z)", `${formatFixed(snapshot.DA_mpc, 6)} Mpc`, "Angular-diameter distance"),
      metricCard("D_L(z)", `${formatFixed(snapshot.DL_mpc, 6)} Mpc`, "Luminosity distance"),
      metricCard("D_H(z)", `${formatFixed(snapshot.DH_mpc, 6)} Mpc`, "Instantaneous Hubble distance"),
      metricCard("D_V(z)", `${formatFixed(snapshot.DV_mpc, 6)} Mpc`, "Isotropic BAO volume distance"),
      metricCard("D_M / r_d", formatFixed(snapshot.DM_over_rd, 6), "BAO transverse ratio"),
      metricCard("D_H / r_d", formatFixed(snapshot.DH_over_rd, 6), "BAO radial ratio"),
      metricCard("D_V / r_d", formatFixed(snapshot.DV_over_rd, 6), "BAO isotropic ratio"),
      metricCard("lookback", `${formatFixed(snapshot.lookback_gyr, 6)} Gyr`, "Proper observer-side lookback time"),
      metricCard("age(z)", `${formatFixed(snapshot.age_gyr, 6)} Gyr`, "Observer-side cosmic age at redshift"),
    ].join("");
  }

  redshiftInput.addEventListener("input", updateResults);
  updateResults();
}

main().catch((error) => {
  console.error(error);
});
