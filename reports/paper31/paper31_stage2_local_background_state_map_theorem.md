# Paper 31: Stage-2 Local Background-State Map Theorem

Date: 2026-04-03

## Question

After closing the characteristic-field seam, can the local background-state map
feeding the inherited FULL Stage-2 law be sharpened beyond a generic open
placeholder?

Equivalently: what are the exact or best-closed formulas for

\[
H_{\rm loc}(z_{\rm obs}),\qquad
T_{R,\rm loc}(z_{\rm obs}),\qquad
n_{H,\rm loc}(z_{\rm obs}),\qquad
T_{m,\rm loc}(z_{\rm obs})?
\]

## Executive result

The strongest honest answer is:

- `derived / scoped`: the local expansion-rate map is exact:
  \[
  H_{\rm loc}(z_{\rm obs})
  =
  \frac{c}{r_s}\sqrt{\frac{1-u(z_{\rm obs})}{u(z_{\rm obs})^3}},
  \qquad
  u(z)=\frac{1}{x(1+z)}.
  \]
- `derived / conditional`: the local radiation-temperature map is
  \[
  T_{R,\rm loc}(z_{\rm obs})
  =
  T_{\rm IO,0}\,(1+z_{\rm obs})
  =
  x^{-K_{\rm gauge}}\,T_{\rm obs,0}\,(1+z_{\rm obs}),
  \]
  because the `TR` variable in the inherited FULL hydrogen equations is a local
  bulk radiation-state variable, not an observer-side optical readout.
- `derived / scoped`: the local hydrogen-density map remains
  \[
  n_{H,\rm loc}(z_{\rm obs})=n_{H0,\rm geom}(1+z_{\rm obs})^3.
  \]
- `derived / scoped`: `T_{m,\rm loc}` is **not** another prescribed branch-map
  scalar. It is a solved component of the extended Stage-2 state, with the
  high-redshift anchor
  \[
  T_{m,\rm loc}\to T_{R,\rm loc}.
  \]

So the remaining Stage-2 open object is no longer the whole local background
map. It is narrower:

\[
\boxed{
\text{the implementation of the inherited FULL extended-state solver on this}
\ \text{local background map.}
}
\]

## 1. Exact local scale-factor map

Paper 28 already proves on the homogeneous OS background:

\[
1+z_{\rm obs}=\frac{a(\eta_s)}{a(\eta_e)},
\qquad
a(\eta_s)=\frac{r_s}{x},
\qquad
u(z):=\frac{a(\eta_e)}{r_s}=\frac{1}{x(1+z)}.
\]

Authorities:

- [paper28_redshift_to_event_theorem_report.md](/opt/cosmology-lab/results/paper28/paper28_redshift_to_event_theorem_report.md)
- [paper28_jwst_clock_map_theorem_report.md](/opt/cosmology-lab/results/paper28/paper28_jwst_clock_map_theorem_report.md)

Therefore the local OS scale factor at the emission event is exactly

\[
a_{\rm loc}(z_{\rm obs})=r_s\,u(z_{\rm obs}).
\]

## 2. Exact local Hubble map

Since

\[
\tau(u)=\frac{r_s}{2c}\left[\arccos(1-2u)-2\sqrt{u(1-u)}\right],
\]

direct differentiation gives

\[
\frac{d\tau}{du}=\frac{r_s}{c}\sqrt{\frac{u}{1-u}}.
\]

Hence

\[
H_{\rm loc}
:=
\frac{1}{a_{\rm loc}}\frac{da_{\rm loc}}{d\tau}
=
\frac{1}{u}\frac{du}{d\tau}
=
\frac{c}{r_s}\sqrt{\frac{1-u}{u^3}}.
\]

This is exactly the same quantity previously written as the chain-rule form

\[
H_{\rm loc}=\frac{H_{\rm proj}}{R_{\rm rec}},
\qquad
R_{\rm rec}=\frac{|d\tau_{\rm OS}/dz|}{|dt_{\rm proj}/dz|}.
\]

Reproducible audit:

- [paper31_stage2_local_background_state_map_audit.py](/opt/cosmology-lab/results/paper31/paper31_stage2_local_background_state_map_audit.py)
- [paper31_stage2_local_background_state_map_audit_report.txt](/opt/cosmology-lab/results/paper31/paper31_stage2_local_background_state_map_audit_report.txt)
- [paper31_stage2_local_background_state_map_audit_results.json](/opt/cosmology-lab/results/paper31/paper31_stage2_local_background_state_map_audit_results.json)

The equality is verified numerically to machine precision across the
recombination window.

## 3. Local hydrogen density

The local hydrogen inventory theorem already closes the branch:

\[
n_{H,\rm loc}(z_{\rm obs}) = n_{H0,\rm geom}(1+z_{\rm obs})^3.
\]

This follows because:

1. recombination chemistry is a local bulk inventory/rate observable;
2. its baryon slot is `\omega_{b,\rm geom}`;
3. the exact redshift theorem still gives `a_s/a_e = 1+z_{\rm obs}` for
   comoving source and observer on the homogeneous OS background.

Authority:

- [paper31_baryon_assignment_theorems.md](/opt/cosmology-lab/results/paper31/paper31_baryon_assignment_theorems.md)

## 4. Local radiation temperature

Paper 21 already proved that GTTP is an observer-side optical readout theorem,
not a universal replacement for every bulk thermal variable:

- [paper21_tio_branch_assignment_theorem_report.txt](/opt/cosmology-lab/results/paper21/paper21_tio_branch_assignment_theorem_report.txt)

What remained open was whether the `TR` argument in the inherited FULL hydrogen
equations is a local bulk radiation variable or an observer-side optical
readout variable.

Paper 31 now audits the exact FULL hydrogen code path and finds:

- `TR` enters only through local bulk roles:
  - Saha/detailed-balance exponentials,
  - local rate interpolation tables,
  - `TM/TR` thermal ratios,
  - line-transfer occupation factors;
- no observer-side readout variables (`kappa`, visibility, harmonic `\ell`,
  `C_\ell`, lensing, source-packet objects) appear inside those TR-dependent
  Stage-2 functions.

Reproducible audit:

- [paper31_stage2_local_background_state_map_audit.py](/opt/cosmology-lab/results/paper31/paper31_stage2_local_background_state_map_audit.py)

So within the inherited FULL Stage-2 class, `TR` belongs to the local bulk
radiation sector. Therefore its present normalization is the local bulk thermal
scale `T_{\rm IO,0}`, not the observer optical readout `T_{\rm obs,0}`.

Since local blackbody radiation on the homogeneous OS background scales as
`1/a`, and `a_s/a_e = 1+z_{\rm obs}`, the exact homogeneous local map is

\[
T_{R,\rm loc}(z_{\rm obs})=T_{\rm IO,0}(1+z_{\rm obs})
=x^{-K_{\rm gauge}}T_{\rm obs,0}(1+z_{\rm obs}).
\]

## 5. Local matter temperature

Unlike `H_{\rm loc}`, `n_H`, and `T_R`, the baryon matter temperature is not a
separate observer/readout-branch choice. In the exact inherited FULL law it is
already part of the dynamical state itself.

So the correct status is:

- `derived / scoped`: `T_{m,\rm loc}` is **solved**, not prescribed.
- `derived / scoped`: at sufficiently high redshift, Compton coupling anchors
  the local matter temperature to the local radiation temperature,
  \[
  T_{m,\rm loc}\to T_{R,\rm loc}.
  \]

This is standard exterior recombination microphysics admissible under Premise
2.

## 6. Why this does not contradict the earlier local-transport no-go

The earlier theorem

- [paper31_stage2_local_transport_nogo_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_local_transport_nogo_theorem.md)

killed **bare** `H_{\rm loc}` and **bare** `T_{\rm IO}` as standalone reduced
local closure candidates inside the current pointwise wrapper / reduced-state
solver class.

That theorem did **not** prove that `H_{\rm loc}` is false as the exact local
geometric background input, nor that `T_{R,\rm loc}=T_{\rm IO,0}(1+z)` is false
as the local bulk radiation-temperature map.

Paper 31 now has stronger architecture theorems:

1. the pointwise reduced wrapper is not exact;
2. the exact law lives on the extended characteristic-field state;
3. the characteristic-field law itself is inherited from exterior FULL.

So the correct interpretation is:

- the reduced local-transport route was the wrong **solver class**;
- these maps can still be exact **background inputs** to the correct extended
  solver class.

## 7. Theorem statement

### Stage-2 local background-state map theorem

Status:

- `derived / scoped` for `H_{\rm loc}`, `n_H`, and the dynamical status of
  `T_m`
- `derived / conditional` for `T_{R,\rm loc}`, conditional on the accepted
  identification of HyRec `TR` as a local bulk radiation-state variable under
  Premise 2

Premises:

1. the Paper 28 homogeneous OS redshift-to-event theorem,
2. the Paper 21 local-bulk versus optical-readout theorem,
3. the Paper 31 characteristic-field inheritance theorem,
4. the Paper 31 baryon assignment theorem for local hydrogen chemistry.

Statement:

The local background-state inputs feeding the inherited FULL Stage-2 law are

\[
a_{\rm loc}(z_{\rm obs})=r_s\,u(z_{\rm obs}),
\qquad
u(z)=\frac{1}{x(1+z_{\rm obs})},
\]
\[
H_{\rm loc}(z_{\rm obs})
=
\frac{c}{r_s}\sqrt{\frac{1-u}{u^3}},
\qquad
n_{H,\rm loc}(z_{\rm obs})=n_{H0,\rm geom}(1+z_{\rm obs})^3,
\]
\[
T_{R,\rm loc}(z_{\rm obs})
=
T_{\rm IO,0}(1+z_{\rm obs}),
\]
while `T_{m,\rm loc}` is a dynamically solved component of the extended FULL
state, with high-redshift anchor `T_{m,\rm loc}\to T_{R,\rm loc}`.

## 8. Claim boundary

- `derived / scoped`: the local Hubble map is exact and no longer open.
- `derived / scoped`: the local hydrogen-density map is exact and no longer
  open.
- `derived / conditional`: the local radiation-temperature map is closed at the
  class level.
- `not derived`: the exact numerical recombination history on this map until
  the extended-state solver is implemented.

## Final verdict

The remaining Stage-2 frontier is narrower than before.

The local background-state map is no longer an undifferentiated open object.
It now splits cleanly:

- `H_{\rm loc}`: closed
- `n_H`: closed
- `T_{R,\rm loc}`: class-closed
- `T_{m,\rm loc}`: solved dynamically inside the inherited FULL law

So the exact remaining solver debt is implementation of the inherited FULL
extended-state law on this IO local background map, not discovery of another
background branch factor.
