# Paper 31: Recombination Clock Transport Theorem

Date: 2026-04-03

## Question

Once the perturbation-only Thomson class is killed, what is the first
theorem-grade positive component of the deeper typed thermodynamics/bulk
hierarchy?

More sharply: does primordial recombination inherit the same OS-proper-time
transport structure already proved for late reionization?

## Executive result

The strongest honest answer is:

- `derived / conditional`: **yes**. Primordial hydrogen recombination is the
  same kind of local ionization/recombination balance law as late reionization,
  just in the early plasma rather than the late IGM.
- `derived / scoped`: therefore the observed-redshift recombination law must
  inherit the exact OS-clock transport factor
  \[
  \mathcal R_{\rm rec}(z)
  :=
  \frac{|d\tau_{\rm OS}/dz|}{|dt_{\rm proj}/dz|}.
  \]
- `verified`: on the active Schur branch this factor is large through the
  recombination window:
  \[
  \mathcal R_{\rm rec}(800) = 1.6726,\qquad
  \mathcal R_{\rm rec}(1100) = 1.7274,\qquad
  \mathcal R_{\rm rec}(1400) = 1.7806.
  \]

So the first positive deeper-law statement is:

\[
\boxed{
\text{the exact IO Stage-2 thermodynamics must include OS-clock transport of the}
\ \text{recombination chemistry itself.}
}
\]

This is a theorem about the class and transport law. It is not yet a full
solver closure.

## 1. Local class identification

### `derived / scoped`

Paper 21 already proves that local bulk thermodynamic/reaction observables are
not GTTP optical readouts:

- local bulk chemistry uses the local bulk branch,
- optical GTTP belongs only to the boundary readout class.

Authority:

- [paper21_tio_branch_assignment_theorem_report.txt](/opt/cosmology-lab/results/paper21/paper21_tio_branch_assignment_theorem_report.txt)

Paper 26 already proves for recombination that:

- the hydrogen inventory uses `omega_b,geom`,
- the primitive local free-electron opacity `n_e = x_e n_H` is a local
  electron-counting object and therefore follows the same local inventory
  branch.

Authority:

- [paper26_io_native_recombination.md](/opt/cosmology-lab/results/paper26/paper26_io_native_recombination.md)

Therefore the primitive recombination law is a local bulk chemistry/history
law, not an observer-side optical readout.

## 2. Transport inheritance from the two-clock program

### `derived / conditional`

Paper 28 / 29 / 31 already close the relevant two-clock rule:

- high-z local physics evolves on OS proper time,
- observed redshift is read out on the projected Schur branch.

Late reionization already inherited this structure theorem-grade in
[paper31_reionization_dynamical_transport_theorem.md](/opt/cosmology-lab/results/paper31/paper31_reionization_dynamical_transport_theorem.md).

Primordial recombination is the same class of object:

- local hydrogen/electron counting,
- local ionization/recombination source-minus-sink kinetics,
- observer-side readout only through the projected visibility chain.

So the same transport logic applies.

## 3. Exact transport factor

### `derived / scoped`

The OS proper-time map on the active high-z branch is

\[
\tau_{\rm OS}(u)
=
\frac{r_s}{2c}
\left[
\arccos(1-2u)-2\sqrt{u(1-u)}
\right],
\qquad
u(z)=\frac{1}{x(1+z)}.
\]

Hence

\[
\frac{d\tau_{\rm OS}}{dz}
=
-\frac{r_s}{c\,x(1+z)^2\sqrt{x(1+z)-1}}.
\]

The projected observer-age derivative is

\[
\frac{dt_{\rm proj}}{dz}
=
-\frac{1}{(1+z)H_{\rm Schur}(z)}.
\]

Therefore the exact recombination transport factor is

\[
\mathcal R_{\rm rec}(z)
=
\frac{|d\tau_{\rm OS}/dz|}{|dt_{\rm proj}/dz|}
=
\frac{r_s H_{\rm Schur}(z)}{c\,x(1+z)\sqrt{x(1+z)-1}}.
\]

## 4. Theorem statement

### Theorem 31.RC (Recombination clock transport theorem)

Status: `derived / conditional`

Premises:

1. primordial recombination chemistry is a local bulk ionization/recombination
   law with no primitive optical readout leg,
2. high-z local physics evolves on OS proper time,
3. observed redshift is read on the projected Schur branch.

Statement:

Under Premises 1-3, the observed-redshift form of the recombination evolution
law must be obtained by multiplying the local proper-time law by the exact
Jacobian `d tau_OS / dz`. Relative to a naive projected-clock formulation, the
local recombination source-minus-sink law is rescaled by the factor
`\mathcal R_{\rm rec}(z)`.

## 5. Verification on the active branch

Reproducible audit:

- [paper31_recombination_clock_transport_check.py](/opt/cosmology-lab/results/paper31/paper31_recombination_clock_transport_check.py)
- [paper31_recombination_clock_transport_check_report.txt](/opt/cosmology-lab/results/paper31/paper31_recombination_clock_transport_check_report.txt)
- [paper31_recombination_clock_transport_check_results.json](/opt/cosmology-lab/results/paper31/paper31_recombination_clock_transport_check_results.json)

### `verified`

On the active Schur branch:

- `z = 800`: `R_rec = 1.672575973`
- `z = 900`: `1.691037690`
- `z = 1000`: `1.709312032`
- `z = 1080`: `1.723798212`
- `z = 1100`: `1.727401581`
- `z = 1200`: `1.745310043`
- `z = 1400`: `1.780600094`

So across the entire recombination visibility window, the OS-clock transport is
not a tiny effect. It accelerates the local recombination law by about
`67%–78%` per unit observed redshift relative to the naive projected-clock
formulation.

## 6. Naive full pullback benchmark

### `verified / conditional`

As a first parameter-free benchmark, age-match the same local recombination
history `x_e(t)` from the projected solver onto the OS clock:

\[
x_e^{\rm pullback}(z_{\rm obs}) := x_e^{\rm proj}(t_{\rm proj}^{-1}(\tau_{\rm OS}(z_{\rm obs}))).
\]

This is **not** the final theorem-grade solver. It is the minimal imported
clock-only pullback of the current local history.

The benchmark shows:

- baseline projected history:
  \[
  z_{\rm peak}[g] = 1091.2675,\qquad
  {\rm FWHM}_z = 199.0
  \]
- naive OS-clock pullback:
  \[
  z_{\rm peak}[g] = 1599.7125,\qquad
  {\rm FWHM}_z = 84.0775
  \]
- at `z = 1100`:
  \[
  x_e^{\rm pullback}/x_e^{\rm base} \approx 0.01470.
  \]

So the clock transport acts in the right structural place, but a naive full
pullback of the current projected history overshoots badly.

## 7. Consequence

### `derived / scoped`

The true deeper solver branch must include Stage-2 clock transport.

### `verified / scoped`

But the exact deeper law is not the naive clock-only pullback of the existing
projected recombination history.

So the remaining exact thermodynamics/bulk law is now narrower:

\[
\boxed{
\text{Stage-2 must be rebuilt around OS-clock transport plus additional}
\ \text{bulk/thermodynamic structure, not around the old projected chemistry alone.}
}
\]

## 8. Claim boundary

- `derived / conditional`: recombination clock transport theorem.
- `verified`: the factor `R_rec(z)` is large throughout recombination on the
  active branch.
- `verified / conditional`: naive clock-only pullback is too strong.
- `not derived`: the exact corrected Stage-2 thermodynamic solver after
  transport.

## Honest conclusion

The deeper thermodynamics/bulk frontier is no longer shapeless.

Its first theorem-grade positive component is now explicit:

- recombination chemistry must be transported on the OS clock,
- but simple pullback of the old projected history is not enough.

So the remaining solver debt is a transported-and-renormalized Stage-2 law,
not a perturbation-only hierarchy patch.
