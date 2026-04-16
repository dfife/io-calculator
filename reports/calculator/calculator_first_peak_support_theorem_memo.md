# Calculator First-Peak Support Theorem Memo

Date: 2026-04-16

## Purpose

This memo packages the complete current chain behind the scoped TT
first-peak-support result for Cosmo review.

It answers the precise question:

- does the current IO closed-`S^3` scalar pipeline now carry an executable TT
  branch whose first broad acoustic peak lands in the physical `ell ~ 220`
  family?

It also states the exact remaining boundary:

- this is **not** yet a theorem-grade full high-`ell` TT closure
- the `n_max >= 601` shell-ceiling drift remains open

## Executive result

What is now closed:

- `conditional / scoped`:
  the executable active-branch closed-`S^3` TT composition
- `verified / scoped`:
  a canonical repaired first-peak support carrier on which the TT spectrum
  lands in the physical first-peak family

Canonical verified carrier:

- `exact_history_samples = 120`
- `prehistory_samples = 40`
- `n_max = 501`
- `shell_step = 1`
- `project_metric_constraint = False`
- `constraint_metric_source_only = True`
- `constraint_consistent_seed = True`
- `metric_baryon_momentum_slot = omega_b,eff`
- `source_shell_support = odd_plus_branch`
- `source_shell_weight_interpretation = covariance`

Canonical verified result:

\[
\boxed{
\ell_{\rm peak} = 224
}
\]

\[
\boxed{
\frac{C_{220}}{C_{\rm peak}} = 0.9938104102565932
}
\]

\[
\boxed{
\frac{C_2}{C_{30}} = 1148.794609154744
}
\]

Neighboring lower ceiling support on the same repaired branch:

\[
\ell_{\rm peak}(n_{\max}=453) = 222,
\qquad
\frac{C_{220}}{C_{\rm peak}} = 0.976859196443279.
\]

So the repaired branch now genuinely reaches the physical first-peak family on
the canonical scoped carrier.

## Exact theorem statement

### Theorem FP1. Scoped TT First-peak Support Theorem

On the repaired active-branch closed-`S^3` scalar TT carrier with:

- the active scalar-source block,
- the inherited-FULL Stage-2 exact-history segment on `z <= z_exact_max`,
- the explicit thermal prehistory extension on `z > z_exact_max`,
- the typed equal-rate Thomson-history realization,
- the repaired Einstein-side metric/source closure,
- the repaired odd-shell source support,
- covariance shell weights,
- and the canonical runtime parameters
  `(exact_history_samples, prehistory_samples, n_max, shell_step) = (120, 40, 501, 1)`,

the executable shell-summed temperature spectrum `C_l^{TT}` lands in the
physical first-peak family with

\[
\ell_{\rm peak} = 224,
\qquad
\frac{C_{220}}{C_{\rm peak}} = 0.9938104102565932.
\]

This is a `verified / scoped` first-peak-support theorem on the canonical
carrier only. It is **not** a theorem-grade full high-`ell` TT closure.

## Premise layer

### Working premises

- `premise.1`:
  the IO black-hole cosmology framework and its closed-geometry branch setting
- `premise.2`:
  accepted exterior local microphysics is licensed inside the horizon

### Published-paper authorities in the chain

1. Paper 22
   spatial `S^3` carrier, scalar shell support, closed mode ladder
2. Paper 23
   closed scalar operator, shell geometry, `lambda_n - 3 = (n-1)(n+3)`
3. Paper 28
   exact closed-`S^3` shell-power definition and observer-side shell Jacobian
4. Paper 29
   local sound-speed / primitive acoustic loading selector
5. Paper 31
   baryon assignment, local Stage-2 background map, exact Stage-2 Markov state
6. Paper 32
   modular DtN source block, hidden-identification repair, typed solver grammar
7. Calculator
   Thomson-history tuple theorem and peak-functional separation

### New derivations created in this closure program

These are not published papers; they are local theorem-grade additions in the
calculator/reports layer:

1. Inherited FULL Stage-2 Dynamic-history Builder Theorem
2. Closed Scalar Metric-state Builder Theorem
3. Closed Scalar Acoustic Generator Theorem
4. Closed Scalar Transfer Projector Theorem
5. Scoped Closed-scalar Pipeline Theorem
6. Scoped TT Driver Composition Theorem
7. Scoped TT First-peak Support Theorem

## Theorem chain

### Step 1. Closed `S^3` scalar carrier

Published input:

- Paper 22
- Paper 23

Content:

\[
k_n^2 = \frac{n(n+2)}{R_{\rm curv}^2},
\qquad
q_n^2 = \frac{(n+1)^2}{R_{\rm curv}^2},
\qquad
\ell < \nu = n+1,
\qquad
n \ge 2.
\]

Status:

- `derived / scoped`

Role:

- fixes the discrete shell geometry and the exact shell-to-`ell` support class

### Step 2. Active scalar source block and shell law

Published input:

- Paper 32 modular DtN source theorem
- Paper 32 hidden-identification repair

Content:

\[
T_{\rm field}
=
e^{- (K_g \otimes \log(r_s \Lambda_{\rm DtN}^{\rm coex}))/(2x)},
\qquad
P_{\rm src} = B_+ \circ U_{\rm coex} \circ T_{\rm field},
\]

with active scalar-shell covariance

\[
C_N^{\rm src} = A_s W_N^{(+)},
\qquad
A_s = 2.0072459972737347 \times 10^{-9}.
\]

Status:

- `derived / scoped`

Role:

- fixes the admitted active source shell law used by the TT runtime

### Step 3. Source-to-initial-condition bridge

New derivation:

- Closed Scalar Adiabatic Seed Bridge

Content:

the runtime carries the admitted leading closed-shell adiabatic seed on the
active scalar-source branch and transports it explicitly to Newtonian gauge.

Status:

- `derived / scoped`

Role:

- fixes the source-to-seed bridge without importing a CLASS primordial fit

### Step 4. Exact Stage-2 history carrier

Published input:

- Paper 31 Stage-2 Markov state

New derivation:

- Inherited FULL Stage-2 Dynamic-history Builder Theorem

Content:

the runtime builds the exact sampled state

\[
Y_{\rm rec}(z) = (x_e(z), T_m(z), D_-(q;z), L_-(z))
\]

on the active IO local background, using inherited FULL HyRec physics under
Premise 2.

Status:

- `conditional / scoped`

Role:

- supplies the exact sampled history carrier used by the executable TT branch

### Step 5. Typed Thomson-history realization

Published input:

- Calculator Thomson-history realization theorem

New derivation:

- Typed Split Thomson-history Realization Theorem

Content:

the live branch builds the conformal tuple

\[
(\text{thomson\_drag\_rate},
\text{thomson\_hierarchy\_rate},
\tau_c,
d\tau_c,
\text{slip},
\text{shear})
\]

through the typed path

\[
\kappa'_{\rm loc}
\rightarrow
(d\tau_{\rm obs}/dz,\tau_{\rm obs},g_{\rm obs})
\rightarrow
\text{conformal Thomson tuple}.
\]

Current accepted scope:

\[
\text{thomson\_hierarchy\_rate}
=
\text{thomson\_drag\_rate}.
\]

Status:

- `derived / scoped as maps`

Role:

- fixes the admitted typed TT history carrier

### Step 6. Typed `R` hierarchy site closure

Published input:

- Paper 29
- Paper 31
- Paper 32
- Calculator tuple theorem

New derivations:

- Full Typed `R` Hierarchy Operator Theorem
- Typed `R` Site-uniqueness Theorem

Content:

the repaired local hierarchy uses the site-wise typed composites built from

\[
R_{\rm local,geom} = \frac{3\rho_{b,\rm geom}}{4\rho_\gamma}
\]

plus the Thomson tuple, with no hierarchy-wide one-slot collapse on `R`.

Status:

- `derived / scoped as maps`

Role:

- closes the local oscillator-site baryon/photon loading operator on the
  accepted equal-rate branch

### Step 7. Closed scalar metric, generator, and projector

New derivations:

1. Closed Scalar Metric-state Builder Theorem
2. Closed Scalar Acoustic Generator Theorem
3. Closed Scalar Transfer Projector Theorem

Content:

these fix the explicit map-level laws from shell stress summary to
metric quartet, from metric/history sample to shell hierarchy RHS, and from
shell source history to `Delta_l^T(q)`.

Status:

- `derived / scoped as maps`

Role:

- closes the local shell evolution and shell-to-transfer maps at explicit
  sample level

### Step 8. Scoped TT Driver Composition Theorem

New derivation:

- Scoped TT Driver Composition Theorem

Content:

the executable TT carrier is the explicit composition

\[
Y_{\rm rec}^{\rm scoped}
\rightarrow
\text{Thomson}^{\rm conf}
\rightarrow
\text{metric/state history}
\rightarrow
\Delta_l^T(q)
\rightarrow
C_l^{TT}
\]

with shell weight

\[
w(n) = \frac{(n+1)^2}{2\pi^2 R^3} P_X(n),
\]

and one common early-time carrier for the whole run.

Status:

- `conditional / scoped`

Role:

- closes the executable TT composition at honest inherited-FULL scope

### Step 9. Scoped TT First-peak Support Theorem

New derivation:

- Scoped TT First-peak Support Theorem

Content:

on the canonical repaired branch through `n_max = 501`, the shell-summed TT
spectrum lands in the physical first-peak family with

\[
\ell_{\rm peak} = 224,
\qquad
\frac{C_{220}}{C_{\rm peak}} = 0.9938104102565932.
\]

The neighboring lower ceiling

\[
n_{\max}=453
\]

stays in the same family with

\[
\ell_{\rm peak}=222.
\]

Status:

- `verified / scoped`

Role:

- this is the specific theorem David wants Cosmo to review

## Proof outline

1. Fix the exact closed-`S^3` scalar shell carrier and the active scalar source
   block from the published stack.
2. Build the source-to-initial-condition bridge on that shell carrier without
   importing flat-space primordial fit parameters.
3. Supply the exact sampled Stage-2 history through the inherited-FULL builder
   on the active IO local background.
4. Realize the typed conformal Thomson tuple from the typed split history path.
5. Use the uniquely admitted site-wise typed `R` hierarchy operator on the
   equal-rate branch.
6. Evolve the repaired closed-scalar hierarchy with the repaired
   Einstein/source closure and the repaired seed manifold.
7. Project the shell histories to `Delta_l^T(q)` and shell-sum to `C_l^{TT}`.
8. Evaluate the discrete peak functional on the canonical repaired branch and
   verify that the first broad peak lies in the physical `ell ~ 220` family on
   the canonical `n_max = 501` carrier.
9. Cross-check the neighboring lower ceiling and record the higher-ceiling
   upward drift as the exact remaining open boundary instead of hiding it.

## Scope boundary

This theorem closes only:

- the canonical repaired active-branch first-peak TT carrier
- the first broad TT peak family on that carrier

It does **not** close:

- a theorem-grade full high-`ell` TT closure
- TE or EE
- a theorem-grade Planck extractor
- a universal off-branch TT theorem
- the `n_max >= 601` shell-ceiling drift

The exact live open boundary is:

- on the same repaired branch, higher ceilings still drift upward
  (`ell_peak = 260` to `277` on tested `n_max = 601` carriers)
- therefore the remaining frontier is the source-to-seed / high-shell phase
  law above the canonical first-peak support ceiling

## Other new theorems created during this derivation

1. Inherited FULL Stage-2 Dynamic-history Builder Theorem
2. Typed Split Thomson-history Realization Theorem
3. Full Typed `R` Hierarchy Operator Theorem
4. Typed `R` Site-uniqueness Theorem
5. Closed Scalar Metric-state Builder Theorem
6. Closed Scalar Acoustic Generator Theorem
7. Closed Scalar Transfer Projector Theorem
8. Scoped Closed-scalar Pipeline Theorem
9. Scoped TT Driver Composition Theorem
10. Scoped TT First-peak Support Theorem

These are the post-Paper-32 local completions that made the scoped TT surface
admissible in the calculator.

## Non-claims

Cosmo should read the following as explicit non-claims:

1. This memo does **not** claim that the calculator now has a theorem-grade
   full CMB solver.
2. This memo does **not** claim that the high-`ell` tail is closed.
3. This memo does **not** claim that `n_max = 601` is converged.
4. This memo does **not** claim a theorem-grade strict-bare TT execution
   branch.
5. This memo does **not** claim a theorem-grade nontrivial
   `thomson_drag_rate != thomson_hierarchy_rate` closure.
6. This memo does **not** claim that the observed full Planck TT profile is
   reproduced theorem-grade.
7. This memo does **not** claim that the current peak support theorem removes
   the surviving source-to-seed / high-shell phase frontier.

## Where Cosmo should attack the chain

If Cosmo wants to break the scoped first-peak theorem, the attack must land in
one of these places:

1. the repaired active-branch TT carrier is internally inconsistent
2. the inherited-FULL Stage-2 builder is not admissible on the accepted scope
3. the typed equal-rate Thomson path is not the runtime branch actually used
4. the repaired Einstein/source closure is not the branch that generated the
   stated result
5. the shell-summed `n_max = 501` result is not reproducible
6. the higher-ceiling drift invalidates even the scoped `n_max = 501`
   first-peak-support claim

If none of those attacks lands, the honest conclusion is:

- the calculator now contains a publishable `conditional / scoped` TT
  first-peak surface
- but not yet a theorem-grade full high-`ell` TT closure

## Reproducibility

Primary authorities:

- [calculator_tt_first_peak_support_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_tt_first_peak_support_theorem_report.md)
- [calculator_tt_first_peak_support_results.json](/opt/cosmology-lab/results/calculator/calculator_tt_first_peak_support_results.json)
- [scalar_tt_driver.py](/opt/cosmology-lab/calculator/src/aio_calculator/scalar_tt_driver.py)
- [provenance.py](/opt/cosmology-lab/calculator/src/aio_calculator/provenance.py)

Canonical calculator command:

```bash
cd /opt/cosmology-lab/calculator
PYTHONPATH=src python -m aio_calculator tt-spectrum --workers 12 --json
```

Expected key outputs:

- `claim_status = conditional / scoped executable TT driver`
- `validation.ell_peak = 224`
- `validation.c_220_over_peak = 0.9938104102565932`
- provenance includes:
  - `local.scoped_tt_driver`
  - `local.scoped_tt_first_peak_support`
