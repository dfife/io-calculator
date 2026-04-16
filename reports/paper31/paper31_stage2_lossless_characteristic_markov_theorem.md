# Paper 31: Stage-2 Lossless Characteristic Markov Theorem

Date: 2026-04-03

## Question

Does the exact Stage-2 solver admit any **lossless** Markov closure, or must it
remain fundamentally non-Markovian even after lifting the state?

## Executive result

Yes.

The strongest honest answer is:

- `derived / scoped`: the exact Stage-2 FULL branch is non-Markovian only in
  the reduced thermodynamics variables `(z, x_e, T_m)` alone.
- `derived / scoped`: it admits a **lossless extended-state Markov closure** in
  an outgoing characteristic distortion field plus the local thermodynamic
  variables.
- `verified`: the coded HyRec channel transport is exactly evaluation of that
  characteristic field representation, not a separate larger history object.

So the exact future solver class is now explicit:

\[
\boxed{
Y_{\rm rec}(z)=\big(x_e(z),\,T_m(z),\,\mathcal D_-(q;z),\,\mathcal L_-(z)\big)
}
\]

with

- `\mathcal D_-(q;z)` the outgoing virtual-bin distortion field on the
  conserved characteristic `q=aE`,
- `\mathcal L_-(z)` the finite line-channel handoff sector
  (Ly-`alpha`, Ly-`beta`, Ly-`gamma`).

## 1. The exact structure of the update

At each Stage-2 step, the FULL hydrogen branch proceeds as:

1. **Characteristic transport**
   \[
   (\mathcal D_-,\mathcal L_-) \mapsto (\mathcal D_+,\mathcal L_+)
   \]
   by free streaming on `q=aE`.

2. **Local radiative solve**
   use `(\mathcal D_+,\mathcal L_+)` plus local `(x_e,T_m,n_H,H,...)` to build
   the `T`-matrices and solve for the real/virtual populations.

3. **Outgoing update**
   compute the new outgoing distortion data
   \[
   (\mathcal D_-^{\rm new},\mathcal L_-^{\rm new})
   \]
   from the just-solved real/virtual populations.

4. **Local thermodynamic update**
   update `(x_e,T_m)` from the same solved state.

Every future step depends only on the current extended state
\[
Y_{\rm rec}(z).
\]

## 2. Lossless equivalence to the coded history arrays

The existing HyRec implementation stores the outgoing distortion field as
history arrays indexed by time and bin:

- `Dfminus_hist`
- `Dfminus_Ly_hist`

But Paper 31 now proves these are only one storage realization of the true
transport object.

Authorities:

- [paper31_stage2_characteristic_distortion_transport_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_characteristic_distortion_transport_theorem.md)
- [paper31_stage2_radiation_history_support_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_radiation_history_support_theorem.md)

The direct equivalence check is:

- [paper31_stage2_characteristic_field_equivalence_check.py](/opt/cosmology-lab/results/paper31/paper31_stage2_characteristic_field_equivalence_check.py)
- [paper31_stage2_characteristic_field_equivalence_check_report.txt](/opt/cosmology-lab/results/paper31/paper31_stage2_characteristic_field_equivalence_check_report.txt)
- [paper31_stage2_characteristic_field_equivalence_check_results.json](/opt/cosmology-lab/results/paper31/paper31_stage2_characteristic_field_equivalence_check_results.json)

It gives

\[
\max |\Delta| = 0,
\]

for the tested channel maps. So the history arrays are not a larger exact
object than the characteristic field; they are an exact representation of it.

## 3. Theorem statement

### Stage-2 lossless characteristic Markov theorem

Status: `derived / scoped` plus `verified`

Premises:

1. the Stage-2 non-Markovian radiative-transfer no-go theorem;
2. the Stage-2 characteristic distortion transport theorem;
3. the explicit outgoing-update equations in `rec_HMLA_2photon_dxHIIdlna(...)`.

Statement:

The exact FULL Stage-2 solver admits a lossless Markov closure in the extended
state

\[
Y_{\rm rec}(z)=\big(x_e(z),\,T_m(z),\,\mathcal D_-(q;z),\,\mathcal L_-(z)\big),
\]

where `\mathcal D_-` is the outgoing characteristic distortion field and
`\mathcal L_-` is the finite line-channel handoff sector. The apparent
non-Markovianity of the current wrapper arises only from projecting this exact
state down to the smaller local thermodynamics variables.

## 4. What this does and does not close

- `derived / scoped`: exact lossless extended-state Markov closure exists.
- `derived / scoped no-go`: no fixed finite-dimensional scalar-moment closure
  can replace that field exactly; see
  [paper31_stage2_finite_moment_closure_nogo_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_finite_moment_closure_nogo_theorem.md).
- `not derived`: the exact IO renormalization law acting on that field.
- `not derived`: the most computationally efficient lossless encoding.

## Final verdict

Paper 31 no longer needs to choose between “non-Markovian history tape” and
“finite local closure.” The exact situation is now sharper:

- there **is** a lossless exact Markov closure,
- but it lives on a function-valued characteristic distortion field,
- and not on any fixed finite-dimensional local moment vector.
