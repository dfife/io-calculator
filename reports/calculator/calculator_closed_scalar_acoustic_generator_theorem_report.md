# Closed Scalar Acoustic Generator Theorem

Date: 2026-04-14

## Status line

- `derived / scoped`: on an explicit physical closed-`S^3` scalar shell and an explicit sampled thermodynamic / Thomson-history packet, the local photon-baryon acoustic generator is fixed.
- `derived / scoped`: the gauge-to-quartet metric map is fixed:
  - Newtonian gauge:
    `metric_continuity = -3 phi'`,
    `metric_euler = k_n^2 psi`,
    `metric_shear = 0`,
    `metric_shear_prime = 0`
  - synchronous gauge:
    `metric_continuity = h'/2`,
    `metric_euler = 0`,
    `metric_shear = k_n^2 alpha`,
    `metric_shear_prime = k_n^2 alpha'`
- `derived / scoped boundary`: the remaining exact debt is not a free coefficient family inside the local scalar hierarchy. It is the construction of the explicit upstream inputs:
  1. source-to-initial-condition bridge,
  2. exact Stage-2 dynamic-network history builder,
  3. exact Einstein-side metric-state builder,
  4. hierarchy-to-transfer projector.

## Question

Can the open perturbation center be reduced from an unspecified
`U_pert^{S^3}` to an explicit theorem-grade operator object?

More sharply: once the closed `S^3` shell, typed baryon architecture, and
Calculator Thomson-history tuple are fixed, is the surviving ambiguity still
inside the local photon-baryon hierarchy coefficients, or only in the external
objects that feed that hierarchy?

## Inputs

### Internal

1. `derived / scoped`: Paper 23 fixes the physical scalar shell on closed `S^3`
   with
   `n >= 2`,
   `lambda_n - 3 = (n-1)(n+3)`,
   and `ell = 0,1,...,n`.
2. `derived / scoped`: Paper 29 fixes the primitive local sound-speed loading
   slot
   `R(z) = 3 rho_b / (4 rho_gamma)`
   on `omega_b,geom`.
3. `derived / scoped`: Paper 32 fixes the typed solver grammar and forbids
   collapsing the perturbation block to one baryon slot or to a source-only /
   metric-only / pure-`R` / pure-Thomson multiplicative patch.
4. `derived / scoped`: Calculator fixes the exact coupled Thomson-history tuple
   `(thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear)`.

### External

Under Premise 2, the accepted exterior closed-FRW scalar hierarchy and
tight-coupling algebra are admissible local microphysics on the interior
branch. The exact non-flat scalar carrier formulas used here are the standard
closed-space formulas implemented in the local non-flat hierarchy code.

## Theorem

### Statement

On one explicit physical scalar shell `n >= 2`, with curvature radius
`R_curv`, explicit conformal-time sample `tau`, explicit Stage-2 sample
`(x_e(z), T_m(z))`, explicit coupled Thomson-history tuple, and explicit metric
quartet, the local linearized photon-baryon acoustic generator is fixed by

`k_n^2 = n(n+2) / R_curv^2`

`q_n^2 = k_n^2 + K = (n+1)^2 / R_curv^2`

`s_l = sqrt(1 - K (l^2-1) / k_n^2)`

`cot_K^gen(tau) = sqrt(K) / [k_n tan(sqrt(K) tau)]`

`s_2^2 = (lambda_n - 3) / lambda_n = (n-1)(n+3) / [n(n+2)]`

`R(z) = 3 rho_b(z) / [4 rho_gamma(z)]`

`c_b^2 = (k_B / (m_H c^2)) * (1 + (1/4 - 1) Y_He + x_e (1-Y_He)) * T_m * (1 + (1+z) d ln T_m / dz / 3)`

with local continuity equations

`delta_gamma' = -(4/3) (theta_gamma + metric_continuity)`

`delta_b' = -(theta_b + metric_continuity)`

and local Euler equations

`theta_b' = -a'/a theta_b + metric_euler + k_n^2 c_b^2 delta_b + R * thomson_drag_rate * (theta_gamma - theta_b)`

`theta_gamma' = k_n^2 (delta_gamma / 4 - s_2^2 F_2) + metric_euler + thomson_drag_rate * (theta_b - theta_gamma)`

with photon shear / hierarchy

`P0 = (G_0 + G_2 + 2 s_2 F_2) / 8`

`F_2' = (1/2) [ (8/15)(theta_gamma + metric_shear) - (3/5) k_n (s_3/s_2) F_3 - thomson_hierarchy_rate (2 F_2 - 4 P0 / (5 s_2)) ]`

for `3 <= l < l_max`

`F_l' = k_n / (2l+1) [ l s_l F_{l-1} - (l+1) s_{l+1} F_{l+1} ] - thomson_hierarchy_rate F_l`

and at hierarchy cutoff

`F_l' = k_n [ s_l F_{l-1} - (l+1) cot_K^gen F_l ] - thomson_hierarchy_rate F_l`

with polarization

`G_0' = -k_n G_1 - thomson_hierarchy_rate (G_0 - 4 P0)`

`G_1' = (k_n/3) (G_0 - 2 s_2 G_2) - thomson_hierarchy_rate G_1`

`G_2' = (k_n/5) (2 s_2 G_1 - 3 s_3 G_3) - thomson_hierarchy_rate (G_2 - 4 P0/5)`

and the same closed recurrence / cutoff rule for `G_l`, `l >= 3`.

In the reduced tight-coupling-contract regime, the exact admissible local RHS is

`theta_b' = [ -a'/a theta_b + k_n^2 ( c_b^2 delta_b + R (delta_gamma/4 - s_2^2 shear) ) + R * slip ] / (1+R) + metric_euler`

`theta_gamma' = -(theta_b' + a'/a theta_b - k_n^2 c_b^2 delta_b)/R + k_n^2 (delta_gamma/4 - s_2^2 shear) + ((1+R)/R) metric_euler`

where `slip` and `shear` are consumed from the exact Thomson-history tuple
rather than silently rebuilt from a chosen approximation.

Therefore the local scalar acoustic generator is fixed once the explicit
sampled history, Thomson tuple, and metric drive are supplied.

### Proof sketch

1. Paper 23 fixes the discrete scalar shell and its shifted scalar operator on
   closed `S^3`. This determines the shell support and the closed recurrence
   geometry factors `s_l`, `s_2^2`, and `cot_K^gen`.
2. Paper 29 fixes the local inertia leg `R(z)` on `omega_b,geom`, and the
   sampled Stage-2 history fixes `c_b^2` and `d c_b^2 / d tau` directly from
   `(x_e(z), T_m(z))`.
3. Calculator fixes the admissible Thomson carrier as the coupled tuple
   `(thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear)`.
4. Inserting those typed coefficients into the accepted closed-FRW scalar
   photon-baryon equations yields the explicit full-hierarchy and reduced-TCA
   RHS above.
5. The remaining ambiguity is therefore not in the local hierarchy
   coefficients. It is only in the construction of the external inputs feeding
   that local generator. QED.

## Corollary: Source Neutrality Of The Local Generator

Paper 32 places the one-slot modular-DtN dressing in the source/readout block
`P_src`, not in the local bulk hierarchy coefficients. Therefore the local
generator above is source-neutral in the following precise sense:

- the local coefficients are determined by closed-shell geometry, local
  thermodynamic history, the typed baryon slots, and the Thomson-history tuple;
- the source block enters only through the upstream source-to-initial-condition
  bridge and normalization of the perturbation state;
- no extra hidden `f_Gamma`-type multiplicative factor is licensed inside the
  local acoustic operator itself.

So the surviving source-side debt is the bridge `C_src->pert`, not another
coefficient family inside the local scalar hierarchy.

## Exact boundary

This theorem does **not** close the full end-to-end
`U_pert^{S^3} : (P_src, K_therm) -> y^(md,ic,q)(tau)` as a fully automatic
calculator path.

What remains open:

1. `source-to-initial-condition bridge`
   There is still no theorem-grade builder turning the source block `P_src`
   into the full scalar hierarchy initial state on all species.

2. `exact Stage-2 dynamic-network history builder`
   The current theorem uses an explicit sampled `Stage2History`; it does not
   close the missing operator that produces
   `Y_rec = (x_e, T_m, D_-(q;z), L_-(z))`.

3. `exact Einstein-side metric-state builder`
   The gauge-to-quartet map is closed, but the builder from the full metric /
   matter perturbation state to the needed gauge variables (`phi'`, `psi`) or
   (`h'`, `alpha`, `alpha'`) is not closed on the current calculator carrier.

4. `hierarchy-to-transfer projector`
   The theorem does not derive the exact LOS projector
   `y^(md,ic,q)(tau) -> Delta_l^X(q)`.

So the honest closure is:

- `closed`: the local scalar acoustic generator,
- `not closed`: the automatic construction of all inputs that make it a full
  solver.

## Reproducibility

Code:

- [scalar_acoustic_operator.py](/opt/cosmology-lab/calculator/src/aio_calculator/scalar_acoustic_operator.py)

Tests:

- [test_scalar_acoustic_operator.py](/opt/cosmology-lab/calculator/tests/test_scalar_acoustic_operator.py)
- [test_scalar_hierarchy.py](/opt/cosmology-lab/calculator/tests/test_scalar_hierarchy.py)
- [test_thomson_history_contract.py](/opt/cosmology-lab/calculator/tests/test_thomson_history_contract.py)

Key supporting authorities:

- [paper23_scalar_perturbations_report.txt](/opt/cosmology-lab/results/paper23/paper23_scalar_perturbations_report.txt)
- [paper29_sound_speed_baryon_selector_audit_report.md](/opt/cosmology-lab/results/paper29/paper29_sound_speed_baryon_selector_audit_report.md)
- [paper32_s3_native_solver_specification_theorem.md](/opt/cosmology-lab/results/paper32/paper32_s3_native_solver_specification_theorem.md)
- [calculator_thomson_history_realization_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_thomson_history_realization_theorem_report.md)

## Bottom line

- The local closed-`S^3` scalar acoustic generator is no longer the open center.
- The open center has been sharpened to the explicit upstream builders feeding
  that local generator.
- Future AI must not say the perturbation center is still blocked by unknown
  photon-baryon hierarchy coefficients, nor pretend that the full solver is now
  closed automatically.
