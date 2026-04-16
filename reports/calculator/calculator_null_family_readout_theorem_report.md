# Calculator Null-Family Acoustic Readout Theorem

Status line
-----------

- `derived / scoped`: the explicit null-family acoustic readout field can be built on the current stack.
- `derived / scoped`: the resulting background acoustic estimator class is one-slot.
- `not derived`: theorem-grade numeric `theta_*` still requires the exact acoustic endpoint/phase scalar.

Theorem 37.NF1 (null-family acoustic readout field theorem)
-----------------------------------------------------------

Premises

1. Paper 32 closes the one-slot source/readout block

       P_src = B_+ ◦ U_coex ◦ T_field

   on the active scalar source sector.

2. Paper 21 proves that gauge-neutral direction collection and harmonic projection preserve one-slot degree and do not create a second gauge-bearing slot.

3. Paper 20 closes the homogeneous acoustic history-reduction operator

       R_hist^ac : f(eta)|deta wedge dchi|^(1/2) -> f(eta)|deta|^(1/2),

   and already isolates

       E_rs := integral_0^{eta_rec} c_s(eta) R_hist^ac(omega_hat(eta)) d eta

   as the correct observer-side acoustic estimator schema once the null-family field exists.

4. Gauge-neutral evaluation on the history label does not create a second gauge-bearing slot.

Statement

On the current stack, the explicit null-family acoustic readout field

    omega_hat(eta) := (ev_eta ⊗ C_n) P_src(Phi)

can be built as a gauge-neutral history-and-direction evaluation of the one-slot source block, and the resulting background acoustic estimator `E_rs` is itself a one-slot boundary observable.

Proof

By Premise 1, `P_src` is one-slot on the active scalar source sector.

By Premise 2, direction-resolved collection on the sky/readout side preserves one-slot degree.

By Premise 4, gauge-neutral evaluation at fixed history label `eta` also preserves one-slot degree.

Therefore `omega_hat(eta)` remains pointwise one-slot.

By Premise 3, `R_hist^ac` and the gauge-neutral kernel `c_s(eta)` add no second gauge slot, and the `eta` integral preserves slot count by linearity.

Hence `E_rs` is a one-slot boundary observable on the current scoped sector. QED.

Boundary
--------

This closes the explicit null-family field and the estimator class, but not theorem-grade numeric `theta_*`.
A further theorem is still needed to fix the exact acoustic endpoint/phase scalar numerically from the Stage-2/source bridge.

Remaining frontier
------------------

1. derive the exact acoustic endpoint/phase scalar from the Stage-2/source bridge;
2. prove that the physical peak-position functional on `A_peak` numerically selects that scalar.

Sources
-------

- [paper20_missing_operators_construction_report.txt](/opt/cosmology-lab/results/paper20/paper20_missing_operators_construction_report.txt)
- [paper20_minimal_acoustic_propagator_report.txt](/opt/cosmology-lab/results/paper20/paper20_minimal_acoustic_propagator_report.txt)
- [paper21_a4_bridge_theorem_report.txt](/opt/cosmology-lab/results/paper21/paper21_a4_bridge_theorem_report.txt)
- [paper32_modular_dtn_field_transfer_theorem.md](/opt/cosmology-lab/results/paper32/paper32_modular_dtn_field_transfer_theorem.md)
- [paper32_typed_boundary_to_bulk_projection_theorem.md](/opt/cosmology-lab/results/paper32/paper32_typed_boundary_to_bulk_projection_theorem.md)
