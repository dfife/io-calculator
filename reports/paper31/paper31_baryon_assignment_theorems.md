# Paper 31: Baryon Assignment Theorems for the Closed-S3 Boltzmann Chain

Date: 2026-04-03

## Question

At each actual CMB/Boltzmann insertion point on the closed `S^3` / `K=+1`
interior branch,

- recombination chemistry,
- Thomson scattering rate,
- baryon loading `R`,
- photon-baryon coupling,
- diffusion damping,
- and the scalar metric source,

which IO baryon density applies?

The available carried branches are:

- `omega_b,geom = 0.02108`
- `omega_b,eff = 0.02910`
- `omega_b,clustering = 0.017053042566349`

The key constraints are:

- the `R`-leg route is dead on the exact-kernel control compression,
- the surviving local ODE improvement is the Thomson/diffusion leg with
  `s_best = 0.959764553`,
- the narrow ionization-window correction is weaker than the broad Thomson leg,
- and the CMB perturbation gravitational source is not licensed to use the late
  clustering class.

## Executive result

The honest baryon map is:

| Entry point | Best current assignment | Status | Why |
| --- | --- | --- | --- |
| Recombination chemistry | `omega_b,geom` | `derived / scoped` | local bulk atomic/thermal rate observable; counts hydrogen inventory |
| Primitive local Thomson opacity `kappa' = a n_e sigma_T` | `omega_b,geom` | `derived / scoped` | local free-electron inventory `n_e = x_e n_H` |
| Reduced visibility/readout chain `kappa', kappa, e^{-kappa}, g` | `omega_b,eff` | `derived / scoped` | AV1: observer-side Thomson-gated scalar readout inherits the acoustic optical class |
| Baryon loading `R = 3 rho_b / 4 rho_gamma` | no theorem-grade single carried branch | `open` | acoustic class not closed; pure `R` reassignment route is dead |
| Photon-baryon coupling / drag | composite mixed operator built from `kappa'` and `R` | `derived / scoped` for composite form; exact slot `open` | equations depend on the pair `(kappa',R)`, not one slot |
| Diffusion damping | broad Thomson/diffusion hierarchy, not any single carried branch | `derived / scoped` for hierarchy statement; exact slot `open` | `s_best` survives, `R` route dies, narrow `x_e` window is too weak |
| Scalar metric source in CMB perturbations | not `omega_b,clustering`; strongest surviving family is the open pre-recombination/acoustic family | `derived / no-go` for clustering; exact slot `open` | typed TT penalty came from forcing clustering into the CMB source |

So the CMB baryon dictionary is not:

- one single slot everywhere,
- not `omega_b,clustering` transplanted into the pre-recombination chain,
- and not a theorem that `R`, `kappa'`, visibility, and diffusion all use the
  same carried branch.

The true surviving picture is more structured:

1. **local chemistry / local opacity** live on the geometric-inventory branch,
2. **reduced observer-side visibility/readout** lives on the acoustic optical
   branch,
3. **tight-coupling drag and diffusion** are composite operators depending on
   both the local Thomson sector and the still-open acoustic inertia sector,
4. **the scalar metric source** is not the late clustering branch.

## Fixed background and control context

The current exact-kernel control compression used in the Stage-3/5 no-gos is

- not a theorem-grade IO baryon value,
- but a one-fluid surrogate around `omega_b,control = 0.02710`.

This matters because the surviving Thomson optimum

\[
s_{\rm best}=0.959764553
\]

is a deformation around that surrogate branch, not a theorem that the physical
Thomson slot equals `0.9598 * omega_b,eff`.

That distinction will be enforced below.

## 1. Recombination Chemistry Theorem

### Statement

`derived / scoped`:
the recombination chemistry sector belongs to the geometric inventory branch

\[
\omega_{b,\rm chem} = \omega_{b,\rm geom}.
\]

### Proof sketch

1. The Paper 21 `T_IO` branch theorem already closed the logic that local bulk
   thermodynamic/rate observables with no primitive optical readout leg evaluate
   on the bulk branch rather than the observer optical branch.
2. Hydrogen recombination is exactly such a local bulk atomic/rate observable:
   the Peebles/HyRec equations depend on
   - the hydrogen inventory `n_H`,
   - local temperature history,
   - local atomic coefficients.
3. In the standard rate equations, the baryonic dependence enters through the
   actual hydrogen inventory
   \[
   n_H \propto \omega_b (1-Y_p)(1+z)^3.
   \]
4. The Paper 19 closed `alpha=1` rung is the inventory branch.
5. Therefore the recombination chemistry baryon slot is the geometric inventory
   branch.

### Authority

- [paper21_tio_branch_assignment_theorem_report.txt](/opt/cosmology-lab/results/paper21/paper21_tio_branch_assignment_theorem_report.txt)
- [paper26_io_native_recombination.md](/opt/cosmology-lab/results/paper26/paper26_io_native_recombination.md)

### Boundary

This is a theorem about the **local chemistry/rate algebra**, not yet a theorem
that the full CMB transfer chain uses only that slot.

## 2. Primitive Local Thomson-Opacity Theorem

### Statement

`derived / scoped`:
the primitive local Thomson opacity kernel belongs to the same geometric
inventory branch:

\[
\omega_{b,\kappa'} = \omega_{b,\rm geom},
\qquad
\kappa' = a n_e \sigma_T.
\]

### Proof sketch

1. The local opacity kernel counts actual free electrons:
   \[
   n_e = x_e n_H.
   \]
2. `x_e` is produced by the local chemistry sector above.
3. `n_H` is the actual hydrogen inventory and therefore lives on the geometric
   inventory branch.
4. Hence the primitive local contact operator `\kappa'` inherits the same local
   inventory slot.

### Authority

- [paper26_io_native_recombination.md](/opt/cosmology-lab/results/paper26/paper26_io_native_recombination.md)
- [paper26_thomson_kernel_identity_audit.md](/opt/cosmology-lab/results/paper26/paper26_thomson_kernel_identity_audit.md)

### Boundary

This is a theorem about the **primitive local opacity kernel**, not about the
reduced observer-side visibility/readout class built from it.

## 3. Reduced Visibility/Readout Theorem

### Statement

`derived / scoped`:
inside the reduced observer-side scalar CMB readout sector,

\[
\omega_{b,\rm vis} = \omega_{b,\rm eff}.
\]

### Proof sketch

1. The AV1 theorem proved that the reduced observer-side scalar readout chain
   built from
   \[
   \kappa',\ \kappa,\ e^{-\kappa},\ g
   \]
   is a gauge-neutral Thomson-gated optical/history multiplier on the already
   certified reduced acoustic scalar chain.
2. Such gauge-neutral Thomson gating is type-preserving and cannot create a new
   A-sensitive slot.
3. Therefore the reduced visibility/readout operator inherits the acoustic slot.

### Authority

- [paper27_av1_c1b_round2_memo.md](/opt/cosmology-lab/results/paper27/paper27_av1_c1b_round2_memo.md)

### Boundary

This does **not** contradict the primitive-local opacity theorem above.

The two theorems act at different layers:

- primitive local microphysical kernel: `omega_b,geom`
- reduced observer-side optical/readout chain: `omega_b,eff`

That split is real and already present in the theorem stack.

## 4. Baryon-Loading `R` No-Go Theorem

### Statement

`derived / no-go`:
the current stack does **not** license any theorem-grade assignment

\[
\omega_{b,R} \in \{\omega_{b,\rm geom},\ \omega_{b,\rm eff},\ \omega_{b,\rm clustering}\}
\]

for the acoustic inertia observable

\[
R = \frac{3\rho_b}{4\rho_\gamma}.
\]

### Proof sketch

1. Paper 19 already proves that the pre-recombination acoustic baryon class is
   not closed theorem-grade.
2. Paper 26 proves the perturbation equations do not force `R` and `kappa'` to
   use the same slot.
3. Paper 31 scanned the full minimal local acoustic ODE basis on the exact-kernel
   control compression and found:
   - `R`-leg optimum: essentially no shift from control,
   - physical branch substitutions are catastrophic.

Explicit control-branch results:

- baseline: `chi2 = 2834.716042`
- `r_best = 0.997728266 -> chi2 = 2833.175504`
- `r_geom = 0.777859779 -> chi2 = 20683.683798`
- `r_eff = 1.073800738 -> chi2 = 4206.728413`
- `r_cluster = 0.629263563 -> chi2 = 69000.513344`

So a pure one-slot `R` reassignment is dead on the current exact-kernel control
compression.

### Authority

- [paper19_item6_jacobian_completion_report.txt](/opt/cosmology-lab/results/paper19/paper19_item6_jacobian_completion_report.txt)
- [paper26_tight_coupling_slot_consistency_audit.md](/opt/cosmology-lab/results/paper26/paper26_tight_coupling_slot_consistency_audit.md)
- [paper31_cmb_acoustic_hierarchy_separation_theorem.md](/opt/cosmology-lab/results/paper31/paper31_cmb_acoustic_hierarchy_separation_theorem.md)
- [paper31_cmb_acoustic_operator_family_theorem_report.txt](/opt/cosmology-lab/results/paper31/paper31_cmb_acoustic_operator_family_theorem_report.txt)

### Boundary

This is a no-go theorem for **pure discrete slot assignment** on the present
surrogate branch. It does not prove that `R` has no IO modification. It proves
that the live `R` modification is not a simple substitution by one carried
baryon density.

## 5. Photon-Baryon Coupling Composite Theorem

### Statement

`derived / scoped`:
the photon-baryon coupling / drag sector is a **composite mixed observable**,
not a one-slot baryon observable.

### Proof

1. The tight-coupling equations depend on the pair
   \[
   (\kappa', R),
   \qquad
   \tau_c = 1/\kappa',
   \qquad
   F = \frac{\tau_c}{1+R}.
   \]
2. The Thomson-kernel identity proves that `kappa'` is the unique local
   scattering/contact kernel shared by visibility and drag.
3. The slot-consistency audit proves that the equations do not force `R` to use
   the same baryon slot as `kappa'`.
4. Therefore the photon-baryon coupling operator is intrinsically composite:
   - Thomson/contact leg from the local electron sector,
   - acoustic inertia leg from the still-open acoustic class.

Hence there is no theorem-grade single baryon density
\[
\omega_{b,\rm coupling}
\]
for the drag/slip operator.

### Authority

- [paper26_thomson_kernel_identity_audit.md](/opt/cosmology-lab/results/paper26/paper26_thomson_kernel_identity_audit.md)
- [paper26_tight_coupling_slot_consistency_audit.md](/opt/cosmology-lab/results/paper26/paper26_tight_coupling_slot_consistency_audit.md)

### Boundary

If one insists on a single slot here, one leaves the theorem-grade route.

The honest theorem-grade statement is the composite one.

## 6. Diffusion-Damping Hierarchy Theorem

### Statement

`derived / scoped`:
the CMB diffusion/damping sector is not governed by a pure `R` reassignment and
not by a narrow recombination-window correction. It belongs to a broader
pre-recombination Thomson/diffusion hierarchy.

### Internal argument

1. Paper 31 scanned the minimal ODE basis `{R, metric_euler, kappa'}` and found
   that almost all surviving improvement comes from the Thomson/diffusion leg.
2. The ionization-window extension
   \[
   \kappa'_{\rm eff}(\tau)=\kappa'(\tau)[1+a\,u_{xe}(\tau)]
   \]
   helps, but much less than the broad constant Thomson leg.

Numerically on the exact-kernel control compression:

- broad constant Thomson leg:
  \[
  s_{\rm best}=0.959764553,\qquad \chi^2=2619.355100
  \]
- narrow ionization-window optimum:
  \[
  a_{\rm best}=-0.068166012,\qquad \chi^2=2736.482786
  \]

So the missing structure is not a narrow visibility/recombination-window fix.

### External standard support

`derived / external`:
standard CMB theory already says diffusion damping depends jointly on

- the mean free path / Thomson opacity,
- the baryon loading `R`,
- and their time history through recombination.

In the Hu-Dodelson review, the damping scale is tied to the rapid growth of the
mean free path through recombination, while the phenomenology of the acoustic
peaks depends jointly on the damping scale `\ell_d` and the baryon-photon ratio
`R_*`. The damping/heat-conduction structure explicitly carries both the
Thomson term and the `R` dependence.  
Source: [Hu & Dodelson review](https://ned.ipac.caltech.edu/level5/Sept05/Hu/paper.pdf)

### Consequence

The exact damping branch is not one of the carried discrete baryon slots:

- not `omega_b,geom`,
- not `omega_b,eff`,
- not `omega_b,clustering`.

It is a broader composite Thomson/diffusion operator whose exact theorem-grade
form remains open.

### Authority

- [paper31_cmb_acoustic_hierarchy_separation_theorem.md](/opt/cosmology-lab/results/paper31/paper31_cmb_acoustic_hierarchy_separation_theorem.md)
- [paper31_cmb_acoustic_hierarchy_boundary_report.txt](/opt/cosmology-lab/results/paper31/paper31_cmb_acoustic_hierarchy_boundary_report.txt)

### Status

- broad Thomson/diffusion hierarchy statement: `derived / scoped`
- exact baryon-density realization: `open`

## 7. Metric-Source Non-Clustering Theorem

### Statement

`derived / no-go`:
the CMB perturbation metric source does **not** belong to the late-time
clustering baryon class

\[
\omega_{b,\rm metric\ source} \neq \omega_{b,\rm clustering}
\]

within the current theorem stack.

### Proof sketch

1. Paper 19 only closes `alpha = 3/2` for the late-time total-matter
   clustering observable entering `P(k)`.
2. Paper 26 proves no theorem connects the CMB-era perturbation gravitational
   source to that class.
3. The same audit verified that the typed TT penalty in the CMB fork comes from
   forcing the low clustering slot into the CMB perturbation source.
4. Restoring the source to the high pre-recombination/acoustic family collapses
   the typed source penalty back to the one-fluid control on that branch.

### Authority

- [paper26_cmb_gravity_source_class_audit.md](/opt/cosmology-lab/results/paper26/paper26_cmb_gravity_source_class_audit.md)

### Boundary

This does **not** close the exact metric-source baryon slot.

It proves only:

- not the clustering branch,
- strongest surviving family is the open pre-recombination/acoustic family.

Because the scalar metric seed itself belongs to the Weyl/slice-curvature
family `alpha_Phi = 2`, the metric source is not a clean baryon-Jacobian object
by itself.

## Final assignment map

### Closed or scoped-closed

- recombination chemistry:
  \[
  \omega_{b,\rm chem}=\omega_{b,\rm geom}
  \]
  `derived / scoped`

- primitive local Thomson opacity:
  \[
  \omega_{b,\kappa'}=\omega_{b,\rm geom}
  \]
  `derived / scoped`

- reduced observer-side visibility/readout:
  \[
  \omega_{b,\rm vis}=\omega_{b,\rm eff}
  \]
  `derived / scoped`

- photon-baryon drag/coupling:
  composite `(\kappa',R)` operator, not one slot
  `derived / scoped`

- diffusion damping:
  broad Thomson/diffusion hierarchy, not one discrete slot
  `derived / scoped` for the hierarchy statement

- scalar metric source:
  not `omega_b,clustering`
  `derived / no-go`

### Still open

- exact `R` slot
- exact full Thomson-sector class beyond primitive local opacity versus reduced
  readout
- exact theorem-grade diffusion operator
- exact full CMB typed hierarchy

## Best honest Paper 31 conclusion

The CMB baryon assignments are **not**:

- one universal `omega_b`,
- not a theorem that all Thomson-sector objects use `omega_b,eff`,
- and not a theorem that the pre-recombination chain should inherit
  `omega_b,clustering`.

The theorem-grade picture is more precise:

1. local chemistry and primitive local opacity are geometric inventory
   observables,
2. reduced observer-side visibility/readout is acoustic,
3. the drag/diffusion sector is composite and remains open beyond that split,
4. the metric source is not the clustering branch,
5. the surviving live CMB debt is exactly the deeper pre-LOS
   Thomson/diffusion hierarchy.
