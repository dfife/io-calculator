# Paper 32: S^3-Native Solver Specification Theorem

Date: 2026-04-05

## Question

Can Issue 6 finally be promoted to theorem grade?

More sharply: after the Paper 31 no-go chain and the new Paper 32 typed
projection theorem, is the IO-native Boltzmann seam still "find the right
patch," or is the exact `S^3` solver specification already fixed?

## Executive result

The strongest honest answer is:

- `derived / scoped specification theorem`:
  **yes**, Issue 6 is now theorem-grade closed as a specification problem.
- `derived / scoped`:
  an admissible linear IO-native solver must be specified by the tuple
  \[
  \boxed{
  \mathfrak S_{\rm IO}
  =
  (\mathcal Q_{S^3},\ \mathcal P_{\rm src},\ U_{\rm rec}^{\rm hist},\
   U_{\rm reio}^{\rm red},\ \mathcal K_{\rm therm},\
   \mathcal E_{\rm pert}^{S^3},\ \mathcal L_{S^3}).
  }
  \]
- `derived / scoped`:
  the pieces are:
  1. a closed-universe mode ladder
     \[
     q^2 = k^2 + K(1+m)
     \]
     with the closed support rule
     \[
     l<\nu:=q/\sqrt K;
     \]
  2. the source/readout block
     \[
     \mathcal P_{\rm src}=B_+\circ U_{\rm coex}\circ T_{\rm field};
     \]
  3. the exact Stage-2 history-state evolution on
     \[
     Y_{\rm rec}=(x_e,T_m,\mathcal D_-(q;z),\mathcal L_-(z));
     \]
  4. a reduced or imported reionization-history block on the same IO branch;
  5. a typed thermodynamics table builder for
     \[
     x_e,\ \dot\kappa,\ e^{-\kappa},\ g,\ dg,\ ddg,\ \kappa_b;
     \]
  6. a closed-`S^3` perturbation evolution block acting through the
     perturbation hierarchy;
  7. a line-of-sight / transfer block using hyperspherical interpolation.
- `derived / scoped no-go`:
  no exact solver in the current stack can instead be
  - a pointwise local callback alone,
  - a copied scalar `tau_reio`,
  - a post-solve source patch,
  - or a perturbation-only multiplicative Thomson family.

So Issue 6 is no longer open as a *specification* question. It is open only as
an *operator-completion* question inside an already-fixed typed solver grammar.

## Claim discipline

- `derived`: forward consequence of already-derived IO theorems plus code-level
  module structure
- `verified`: audited directly in the local source tree
- `not derived`: the final explicit Stage-2 dynamic-network operator and the
  final typed source/acoustic operator

## 1. Code-level closed-geometry grammar

The active source tree already contains the exact non-flat transfer grammar:

1. in non-flat geometries,
   \[
   q^2 = k^2 + K(1+m),
   \]
   with `m=0,1,2` for scalar/vector/tensor modes;
2. the transfer layer is built on
   `hyperspherical.h`;
3. in the closed case,
   transfer support obeys
   \[
   l<\nu=q/\sqrt K.
   \]

Authorities / code evidence:

- [transfer.h](/opt/cosmology-lab/src/class_public/include/transfer.h)
- [hyperspherical.h](/opt/cosmology-lab/src/class_public/include/hyperspherical.h)
- [transfer.c](/opt/cosmology-lab/src/class_public/source/transfer.c)

This is exactly the `S^3` harmonic grammar needed for the native solver.

## 2. Exact thermodynamic history grammar

Paper 31 already proved:

1. the exact Stage-2 branch is non-Markovian in `(z,x_e,T_m)` alone;
2. it admits a lossless Markov closure on
   \[
   Y_{\rm rec}=(x_e,T_m,\mathcal D_-,\mathcal L_-);
   \]
3. the characteristic-field theorem is
   \[
   \mathcal N_{\mathcal D}^{\rm IO}=\mathbf 1;
   \]
4. the exact remaining Stage-2 operator is a positivity-preserving,
   history-aware local atomic-radiative deformation on the dynamically
   assembled network.

Code-level support:

- `rec_HMLA_2photon_dxHIIdlna(...)`
- `fplus_from_fminus(...)`
- `populateTS_2photon(...)`
- `Dfminus_hist`
- `Dfminus_Ly_hist`

Authorities:

- [paper31_stage2_lossless_characteristic_markov_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_lossless_characteristic_markov_theorem.md)
- [paper31_stage2_characteristic_field_inheritance_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_characteristic_field_inheritance_theorem.md)
- [paper31_stage2_positivity_admissibility_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_positivity_admissibility_theorem.md)

## 3. Exact reionization grammar

Paper 31 already proved:

1. reionization is a local OS-proper-time history sector;
2. copied `x_e(z)` or copied scalar `tau_reio` are class-mismatched;
3. the correct object is the imported or derived local history
   `x_e^{IO}(\tau_OS)` and its projected visibility history;
4. on the reduced admissible observable branch, Paper 32 now closes
   `x_e^{IO}(z)` itself theorem-grade.

Therefore the native solver cannot use a single scalar reionization parameter
as its exact state object.

Authorities:

- [paper31_external_reionization_import_theorem.md](/opt/cosmology-lab/results/paper31/paper31_external_reionization_import_theorem.md)
- [paper31_reionization_clock_transport_theorem.md](/opt/cosmology-lab/results/paper31/paper31_reionization_clock_transport_theorem.md)
- [paper32_reionization_reduced_history_closure_theorem.md](/opt/cosmology-lab/results/paper32/paper32_reionization_reduced_history_closure_theorem.md)

## 4. Typed perturbation / LOS grammar

The active code and theorem stack already isolate:

- perturbation evolution in
  `perturbations_derivs(...)`,
- source construction in
  `perturbations_sources(...)`,
- line-of-sight / transfer evaluation in the transfer module,
- hyperspherical interpolation through `hyperspherical_HIS_create(...)`.

The no-go chain already excludes exact closure by:

- source-packet families,
- metric-only families,
- perturbation-only multiplicative Thomson families.

So the exact perturbation block must consume:

1. the source/readout block from Paper 32,
2. the typed thermodynamic history tables from recombination and reionization.

## Theorem 32.S3 - S^3-Native Solver Specification Theorem

Status: `derived / scoped`

Premises:

1. the Paper 32 source/readout block
   \[
   \mathcal P_{\rm src}=B_+\circ U_{\rm coex}\circ T_{\rm field};
   \]
2. the Paper 31 Stage-2 history-state theorems;
3. the Paper 31 reionization import / transport / admissibility theorems;
4. the Paper 31 acoustic and solver no-go chain;
5. the local code evidence for closed transfer, hyperspherical interpolation,
   perturbation evolution, and thermodynamics/recombination interfaces.

Statement:

Under Premises 1-5, any admissible exact linear IO-native Boltzmann solver must
be specified by the tuple
\[
\boxed{
\mathfrak S_{\rm IO}
=
(\mathcal Q_{S^3},\ \mathcal P_{\rm src},\ U_{\rm rec}^{\rm hist},\
U_{\rm reio}^{\rm red},\ \mathcal K_{\rm therm},\
\mathcal E_{\rm pert}^{S^3},\ \mathcal L_{S^3}),
}
\]
with the following exact typing:

### (i) Closed-geometry mode ladder

\[
\mathcal Q_{S^3}=\{q\}
\]
obeys
\[
q^2=k^2+K(1+m),
\]
and in the closed case the transfer support satisfies
\[
l<\nu=q/\sqrt K.
\]

### (ii) Source/readout block

\[
\mathcal P_{\rm src}=B_+\circ U_{\rm coex}\circ T_{\rm field},
\]
with `T_field` the theorem-grade modular-DtN source operator.

### (iii) Recombination/history block

\[
U_{\rm rec}^{\rm hist}
\]
acts on
\[
Y_{\rm rec}=(x_e,T_m,\mathcal D_-(q;z),\mathcal L_-(z)),
\]
with:

- local inputs
  `H_loc(z)`, `T_R,loc(z)`, `n_H,geom(z)`,
- identity characteristic-field factor
  `N_D^IO = 1`,
- and an open but positivity-constrained dynamic-network operator.

### (iv) Reionization block

\[
U_{\rm reio}^{\rm red}
\]
acts on an imported or reduced-history reionization state on the same IO
branch, not on a copied scalar `tau_reio`.

### (v) Thermodynamics table builder

\[
\mathcal K_{\rm therm}
:
(U_{\rm rec}^{\rm hist},U_{\rm reio}^{\rm red})
\mapsto
(x_e,\dot\kappa,e^{-\kappa},g,dg,ddg,\kappa_b,\ldots).
\]

### (vi) Closed-`S^3` perturbation evolution

\[
\mathcal E_{\rm pert}^{S^3}
:
(\mathcal P_{\rm src},\mathcal K_{\rm therm})
\mapsto
y^{(md,ic,q)}(\tau)
\]
through the perturbation hierarchy.

### (vii) Hyperspherical LOS / transfer layer

\[
\mathcal L_{S^3}
:
y^{(md,ic,q)}(\tau)\mapsto \Delta_l^X(q)\mapsto C_l
\]
using the closed-geometry transfer layer with hyperspherical interpolation.

### Proof

#### Step 1. Closed-`S^3` transfer support is explicit

The code-level transfer grammar already enforces:

- non-flat `q/k` relation,
- hyperspherical transfer basis,
- and the closed support rule `l<nu`.

So any exact native solver must use a closed-`S^3` harmonic ladder rather than
a flat-space LOS grammar.

#### Step 2. Stage 2 cannot be reduced to a pointwise callback

Paper 31 already proved that the exact FULL Stage-2 branch cannot live on the
reduced pointwise callback `dx_H/dz = F(z,x_e,T_m)` alone.

Therefore any exact native solver must contain a separate history-state block
\[
U_{\rm rec}^{\rm hist}.
\]

#### Step 3. Reionization cannot be a scalar slot

Paper 31 and the new Paper 32 reionization theorem prove that the correct
reionization object is a function-valued history on the IO branch, not one
scalar `tau_reio`.

Therefore any exact native solver must contain a separate block
\[
U_{\rm reio}^{\rm red}.
\]

#### Step 4. Perturbation-only and source-packet closures are dead

The no-go chain excludes:

- source/readout-only closures,
- metric-only closures,
- perturbation-only multiplicative Thomson closures.

Therefore the perturbation hierarchy must sit downstream of both the source
block and the thermodynamic-history block.

#### Step 5. The solver tuple is minimal

Removing any one of:

- the closed mode ladder,
- the source block,
- the recombination history block,
- the reionization history block,
- the thermodynamics table builder,
- the perturbation hierarchy,
- the hyperspherical LOS block,

would violate one of the already-proved typing or no-go theorems.

So the tuple above is the minimal surviving exact specification class.

QED.

## Corollary 32.S3.1 - Typed baryon-slot specification

Status: `derived / scoped`

The native solver must preserve the active typed baryon assignment:

- recombination chemistry:
  `omega_b,geom`
- primitive local opacity:
  `omega_b,geom`
- reduced visibility/readout:
  `omega_b,eff`
- baryon loading `R`:
  exact slot still open
- scalar metric source:
  not `omega_b,clustering`; exact slot still open

So the solver issue is no longer "which one baryon number do we feed
everywhere?" The theorem-grade answer is: not one.

## Corollary 32.S3.2 - Issue 6 is closed at specification grade

Status: `derived / scoped`

The original Item 6 asked for the IO-native Boltzmann solver specification.

That specification is now theorem-grade closed:

- carrier,
- mode ladder,
- history states,
- module interfaces,
- baryon typing,
- and excluded fake closure classes

are all fixed.

What remains open is not the specification. It is the completion of two live
operators inside the specified grammar:

1. the exact Stage-2 dynamic-network operator,
2. the final typed source/acoustic operator on the closed-`S^3` perturbation
   hierarchy.

## Reproducibility

- [paper32_s3_native_solver_specification_audit.py](/opt/cosmology-lab/results/paper32/paper32_s3_native_solver_specification_audit.py)
- [paper32_s3_native_solver_specification_report.txt](/opt/cosmology-lab/results/paper32/paper32_s3_native_solver_specification_report.txt)
- [paper32_s3_native_solver_specification_results.json](/opt/cosmology-lab/results/paper32/paper32_s3_native_solver_specification_results.json)

The audit records the exact local code evidence for:

- closed `q/k` grammar,
- hyperspherical interpolation,
- perturbation/source interfaces,
- reionization function interfaces,
- and the HyRec FULL history-state support objects.

## Literature support and limits

Primary-source support used here:

- Antony Lewis, Anthony Challinor, Anthony Lasenby,
  *Efficient Computation of CMB anisotropies in closed FRW models*
  (`astro-ph/9911177`).
  Support used here: positive-curvature line-of-sight CMB computation is a
  standard exact operator class, not an IO-specific invention.
- Pedram Niazy, Amir H. Abbassi,
  *An analytical approach to the CMB anisotropies in a Spatially Closed
  background* (`arXiv:1709.06549`).
  Support used here: scalar TT line-of-sight treatment in a closed background.
- Pedram Niazy, Amir H. Abbassi,
  *An analytical approach to the CMB Polarization in a Spatially Closed
  background* (`arXiv:1801.02980`).
  Support used here: closed-background EE/TE line-of-sight treatment.

These sources support the closed-geometry LOS grammar. They do **not** supply
the IO typing, the modular-DtN source block, or the missing Stage-2 operator.

## Final verdict

- `derived / scoped`: Issue 6 is now theorem-grade closed as a solver
  specification problem.
- `derived / scoped`: the exact solver must be an `S^3` typed solver with
  separate source, recombination-history, reionization-history, perturbation,
  and LOS blocks.
- `not derived`: the explicit completion of all live operators inside that
  grammar.
