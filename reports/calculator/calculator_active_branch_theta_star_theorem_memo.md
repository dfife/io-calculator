# Calculator Active-Branch Theta-Star Theorem Memo

## Executive result

The current Calculator chain now closes theorem-grade numeric `theta_*` on the
fixed active branch package:

\[
\boxed{
z_{\rm sel}=1092.2670386731625
}
\]

\[
\boxed{
\theta_{\rm bare}=0.7204920802586844^\circ,
\qquad
\theta_*=0.6008516179285112^\circ
}
\]

\[
\boxed{
100\theta_*=1.048683904878751
}
\]

Status:

- `derived / scoped` for the active-branch selector leaf and numeric `theta_*`
- `verified` for the supporting packet, profile, round-trip, and calculator
  checks

Scope boundary:

- fixed active Paper 10 legacy projected branch only
- not a universal off-branch transfer theorem
- not a universal reduction theorem for arbitrary TT parent-profile
  deformations

The old Calculator numeric-theta no-go is superseded on this scope only:

- [calculator_theta_numeric_nogo_synthesis_report.md](/opt/cosmology-lab/results/calculator/calculator_theta_numeric_nogo_synthesis_report.md)

The active-branch closure theorem is:

- [calculator_active_branch_theta_star_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_active_branch_theta_star_theorem_report.md)

## Theorem chain

### Step 1. Exact selector backbone already existed

Calculator closed the exact strict-bare selector map on the certified interval:

\[
z_{\rm sel}
=
\left(\theta_{\rm bare}^{\rm bulk}\big|_I\right)^{-1}
\left(\theta_{\rm bare}^{\rm prim}\right),
\qquad
\theta_{\rm obs}=J_\theta\,\theta_{\rm bare}^{\rm prim},
\qquad
J_\theta=x^{-1/2}\sqrt{1+\gamma^2}.
\]

Authorities:

- [calculator_phase_equivalent_selector_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_phase_equivalent_selector_theorem_report.md)
- [selector.py](/opt/cosmology-lab/calculator/src/aio_calculator/selector.py)

Status:

- `derived / scoped`

What it did **not** yet supply:

- a theorem-grade numeric selector leaf

### Step 2. Packet law promoted from late packet to packet1500 support

The effect-C outgoing-update law was first fixed on the late packet, then
promoted to cumulative `z_cross < 1500` support with explicit state/update and
residual bounds.

Authorities:

- [calculator_effectc_packet_coefficient_fixing_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_packet_coefficient_fixing_theorem_report.md)
- [calculator_effectc_packet1500_support_promotion_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_packet1500_support_promotion_theorem_report.md)

Key promoted-support numbers:

- strongest state gap: `4.656020508191073e-15`
- strongest update gap: `2.846253454996449e-14`
- strongest candidate virtual residual: `3.176621920850654e-14`
- promoted-support carrier output:
  `100theta_star = 1.0486839048178105`,
  `ell_peak = 220.47514473507064`

Status:

- `derived / scoped plus verified / support-promoted`

### Step 3. High-z support above `z ~ 1500` was demoted to a slaved tail

The remaining `z > 1500` support was shown not to be an independent
selector-bearing branch once the lower packet is active.

Authority:

- [calculator_effectc_highz_tail_slaving_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_highz_tail_slaving_theorem_report.md)

Key numbers:

- standalone `z > 1500` fractions:
  `theta = 2.030538250669504e-01`,
  `ell = 2.013385089725805e-01`
- residual fractions after packet1500:
  `theta = 1.286253077827926e-04`,
  `ell = 5.195893073517421e-05`

Status:

- `derived / scoped plus verified / support sharpening`

Exact role in the chain:

- this kills the specific objection that a second high-`z` selector-bearing
  support class remains after packet1500

### Step 4. The residual high-z tail was checked directly on the first TT peak

The crucial new audit compares the full endpoint TT profile to packet1500 on
the first-peak window after removing the best pure-amplitude rescale.

Authority:

- [calculator_effectc_peak_window_tail_profile_audit_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_peak_window_tail_profile_audit_report.md)

Key numbers:

- best vertical match:
  `alpha = 0.999989138924388`
- RMS relative residual on `ell in [190,250]`:
  `2.950052007950388e-06`
- residual peak motion:
  `Delta_ell = +4.390006880612418e-04`
- PK3 parent-profile shift estimate:
  `+4.389836987985153e-04`

Status:

- `verified / scoped`

Exact role in the chain:

- it shows that the remaining full-minus-packet1500 first-peak mismatch is only
  a tiny slaved parent-profile deformation, not evidence for a second active
  selector-bearing support branch

### Step 5. Selector-support promotion

Using Step 2, Step 3, Step 4, and the exact Calculator backbone, the chain
promoted the packet1500 support leaf from a carried endpoint-family interval to
the carried physical selector leaf on the active branch.

Authority:

- [calculator_effectc_selector_support_promotion_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_selector_support_promotion_theorem_report.md)

Result:

\[
\boxed{
z_{\rm sel}=1092.2670386731625
}
\]

with the old raw operational proxy leaf

\[
1092.2749496996403
\]

demoted to a tiny slaved residual parent-profile effect rather than a second
physical selector.

Status:

- `derived / scoped plus verified / carried selector closure`

### Step 6. Active-branch numeric theta-star theorem

Once the selector leaf was fixed, numeric `theta_*` followed by direct
evaluation of the exact strict-bare backbone and observer Jacobian.

Authority:

- [calculator_active_branch_theta_star_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_active_branch_theta_star_theorem_report.md)

Exact evaluation:

\[
\theta_{\rm bare}
=
\theta_{\rm bare}^{\rm bulk}(1092.2670386731625)
=
0.7204920802586844^\circ
\]

\[
\theta_*
=
J_\theta \theta_{\rm bare}
=
0.6008516179285112^\circ
\]

\[
100\theta_*=1.048683904878751
\]

Round-trip check:

\[
\left(\theta_{\rm bare}^{\rm bulk}\big|_I\right)^{-1}(\theta_*/J_\theta)
=
1092.2670386731625
\]

with zero error at carried precision.

Status:

- `derived / scoped`

## Exact claim boundary

What is now closed:

- theorem-grade numeric `theta_*` on the fixed active branch package
- theorem-grade numeric `100theta_*` on the same scope
- theorem-grade selector leaf `z_sel` on the same scope

What is **not** being claimed:

- not a theorem for arbitrary alternative branch packages
- not a universal theorem reducing arbitrary TT parent-profile deformations to a
  primitive scalar
- not a full exact TT/TE/EE solver closure
- not a theorem that every historical operational `100theta_star` value equals
  the physical selector output

The theorem only needs one carried active branch. It does **not** require a
universal off-branch transfer theorem.

## Where Cosmo should attack the chain

If Cosmo wants to break the active-branch closure, the attack has to land in
one of the following places:

1. `OU10` is too weak:
   the residual `z > 1500` support might still contain an independent
   selector-bearing branch even after packet1500.

2. The peak-window audit is insufficient:
   the few-ppm residual parent-profile deformation may still encode a distinct
   selector-bearing support class rather than a slaved tail.

3. `OU14` overpromotes:
   the demotion of the raw full-endpoint operational proxy leaf to a slaved
   residual effect may be too strong.

4. The Calculator selector backbone is being used outside its certified scope.

5. The active-branch scope itself is illegitimate:
   a theorem-grade closure would then need an additional branch-selection
   theorem, not just the active carried branch.

What will **not** break the chain anymore:

- pointing out that `theorem_cmb.py` was only operational
  because `OU15` no longer depends on its numeric output as a theorem input
- pointing out that `ell_peak` usually remains attached to the parent `C_l`
  because `OU14` is scoped to the support-certified active packet-law closure,
  not to arbitrary parent-profile deformations

## Reproducibility checklist

Core Calculator artifacts:

- [calculator_effectc_highz_tail_slaving_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_highz_tail_slaving_theorem_report.md)
- [calculator_effectc_packet1500_support_promotion_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_packet1500_support_promotion_theorem_report.md)
- [calculator_effectc_peak_window_tail_profile_audit_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_peak_window_tail_profile_audit_report.md)
- [calculator_effectc_selector_support_promotion_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_effectc_selector_support_promotion_theorem_report.md)
- [calculator_active_branch_theta_star_theorem_report.md](/opt/cosmology-lab/results/calculator/calculator_active_branch_theta_star_theorem_report.md)

Calculator-side theorem surface:

- [theorem_theta_star.py](/opt/cosmology-lab/calculator/src/aio_calculator/theorem_theta_star.py)
- [test_theorem_theta_star.py](/opt/cosmology-lab/calculator/tests/test_theorem_theta_star.py)

Commands:

```bash
cd /opt/cosmology-lab
python results/calculator/calculator_effectc_peak_window_tail_profile_audit.py
python results/calculator/calculator_effectc_selector_support_promotion_theorem.py
python results/calculator/calculator_active_branch_theta_star_theorem.py
cd /opt/cosmology-lab/calculator
pytest tests -q
PYTHONPATH=src python -m aio_calculator theta-star-theorem --json
```

Expected theorem-grade calculator payload:

```json
{
  "branch_label": "active_paper10_legacy_projected_branch",
  "claim_status": "derived / scoped theorem-grade active-branch theta_* closure",
  "selector_leaf_z": 1092.2670386731625,
  "theta_bare_deg": 0.7204920802586844,
  "theta_obs_deg": 0.6008516179285112,
  "theta_star_100": 1.048683904878751,
  "selector_roundtrip_error": 0.0
}
```

## Bottom line for Cosmo

Cosmo does not need to evaluate the entire pre-Paper-37 archive from scratch to
judge the final closure.

The live review question is narrower:

- does `OU10 + OU12 + peak-window tail audit + OU14` legitimately promote the
  packet1500 selector leaf to the active physical leaf?

If yes, then `OU15` closes active-branch numeric `theta_*`:

\[
\boxed{
100\theta_*=1.048683904878751
}
\]

If no, the break must be stated precisely at one of the attack surfaces listed
above.
