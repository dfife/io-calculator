# Calculator Full Typed `R` Hierarchy Operator Theorem

Date: 2026-04-15

## Executive result

- `derived / scoped as maps`:
  on the accepted equal-rate scoped branch
  `thomson_hierarchy_rate = thomson_drag_rate`, the full closed-`S^3` scalar
  photon-baryon hierarchy does **not** close on a
  one-slot substitution
  `R -> R(omega_b^*)`.
- `derived / scoped as maps`:
  the exact surviving object is a **site-wise typed hierarchy operator**
  carried by one primitive local enthalpy ratio
  `R_local,geom = 3 rho_b,geom / (4 rho_gamma)`.
- `derived / scoped`:
  the alpha-ladder does **not** generate four different baryon slots at the
  four oscillator sites. It generates one primitive local `R` leg plus distinct
  Thomson/history and algebraic companions at each site.
- `derived / scoped`:
  dynamic odd/even loading is sourced inside the oscillator itself by the
  enthalpy maps
  `c_bgamma^2 = 1 / [3(1+R_local,geom)]`
  and
  `L_odd/even = R_local,geom / (1+R_local,geom)`;
  the final observed odd/even peak-height pattern is the downstream
  transfer/readout functional of that evolved hierarchy.

This supersedes the earlier narrower local-composite memo. It also repairs the
momentum-coupling convention: on the calculator carrier
`thomson_drag_rate = 1 / tau_c` is the photon-side Thomson rate, so the
baryon-side drag coefficient is
`Gamma_bgamma = R_local,geom * thomson_drag_rate`, not
`thomson_drag_rate / R_local,geom`.

## Question

Cosmo's attack point is correct: the odd/even peak modulation is dynamically
sourced inside the oscillator. So the real question is:

for the four actual hierarchy appearances

1. momentum coupling,
2. pressure restoring force,
3. baryon inertia,
4. Silk damping,

what typed `R` composite enters, and does any site require a different IO
baryon slot?

## Inputs

### Archive inputs

1. `paper29.sound_speed_selector`

   The primitive local baryon-photon enthalpy ratio is

   `R_local,geom(z) = 3 rho_b,geom(z) / [4 rho_gamma(z)]`.

2. `paper31.baryon_assignment`

   The hierarchy does not see a one-slot `R`; photon-baryon coupling is a
   composite observable built from the pair `(kappa', R)`, and diffusion lives
   on a broader Thomson/diffusion hierarchy.

3. `paper32.typed_baryon_slot_spec`

   The full hierarchy is not licensed to collapse silently to one carried
   baryon slot, and observer/readout typing does not back-propagate into the
   primitive bulk leg.

4. `calculator.thomson_history_realization`

   The exact local perturbation closure must consume the coupled tuple

   `(thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear)`

   with

   `tau_c = 1 / thomson_drag_rate`.

### External microphysics admitted under Premise 2

The accepted exterior tight-coupling and diffusion algebra is admissible
locally. In particular:

- the local oscillator depends on one primitive enthalpy ratio `R`,
- the photon-side Thomson rate is `1 / tau_c`,
- the baryon-side drag coefficient is the enthalpy-weighted rate
  `R / tau_c`,
- the combined-fluid acoustic speed is `1 / [3 (1+R)]`,
- the diffusion scale splits into heat-conduction and shear-viscosity terms.

## Theorem

### Statement

On the accepted equal-rate scoped branch

`thomson_hierarchy_rate = thomson_drag_rate`,

the exact typed `R` operator on the full closed-`S^3` scalar photon-baryon
hierarchy is:

`R_local,geom(z) = 3 rho_b,geom(z) / [4 rho_gamma(z)]`

and the four hierarchy sites are:

1. Momentum coupling

   photon-side coefficient:

   `Gamma_gammab(z) = thomson_drag_rate(z) = 1 / tau_c(z)`

   baryon-side coefficient:

   `Gamma_bgamma(z) = R_local,geom(z) thomson_drag_rate(z) = R_local,geom(z) / tau_c(z)`.

2. Pressure restoring force

   combined-fluid acoustic speed:

   `c_bgamma^2(z) = 1 / [3 (1 + R_local,geom(z))]`.

3. Baryon inertia / equilibrium loading

   inertia factor:

   `M_bgamma(z) = 1 + R_local,geom(z)`

   dynamic odd/even loading factor:

   `L_odd/even(z) = R_local,geom(z) / [1 + R_local,geom(z)]`.

4. Silk damping

   heat-conduction / slip term:

   `D_heat(z) = R_local,geom(z)^2 / [6 (1 + R_local,geom(z))^2 thomson_drag_rate(z)]`

   shear-viscosity term:

   `D_visc(z) = 16 / [90 (1 + R_local,geom(z)) thomson_hierarchy_rate(z)]`

   total:

   `D_silk(z) = D_heat(z) + D_visc(z)`.

The tight-coupling slip factor is correspondingly

`F_tca(z) = tau_c(z) / [1 + R_local,geom(z)]`.

When

`thomson_drag_rate = thomson_hierarchy_rate = kappa'`,

this reduces exactly to the standard one-rate diffusion law

`D_silk = [1 / (6 kappa')] * [R^2 / (1+R) + 16/15] / (1+R)`.

Therefore the exact full typed hierarchy operator is not a slot swap. It is
the site map

`(Gamma_gammab, Gamma_bgamma, c_bgamma^2, M_bgamma, L_odd/even, D_heat, D_visc, D_silk)`

built from

- one primitive local enthalpy ratio `R_local,geom`,
- the Calculator Thomson tuple,
- and no observer-side baryon-slot back-propagation.

### Interpretation by appearance

1. Momentum coupling

   The equations depend on the pair `(kappa', R)`, not on a new baryon slot.
   So this site is a mixed Thomson-contact / enthalpy operator:

   `Gamma_bgamma = R_local,geom * thomson_drag_rate`.

2. Pressure restoring force

   This is the primitive local baryon-photon enthalpy loading site:

   `c_bgamma^2 = 1 / [3 (1+R_local,geom)]`.

3. Baryon inertia and odd/even modulation

   The oscillator mass and equilibrium shift are

   `M_bgamma = 1 + R_local,geom`

   and

   `L_odd/even = R_local,geom / (1 + R_local,geom)`.

   So odd/even modulation is dynamically sourced in the oscillator, not only in
   the readout. But it is still sourced by the same primitive local enthalpy
   object rather than by a new baryon rung.

4. Silk damping

   This site is genuinely split:

   - `D_heat` belongs to baryon-photon slip / drag history,
   - `D_visc` belongs to photon hierarchy / shear history,
   - both retain the same primitive `R_local,geom`.

### Proof sketch

1. Paper 29 closes the primitive local enthalpy ratio to the inventory branch
   `omega_b,geom`.

2. Paper 31 and Paper 32 kill any one-slot hierarchy-wide `R` reassignment and
   force the surviving object to be operator-valued and typed.

3. Calculator fixes the exact Thomson tuple. Therefore the hierarchy cannot use a
   bare scalar `R` by itself; it must use explicit site composites built from
   `R_local,geom` and the tuple.

4. Standard tight-coupling algebra on the admitted exterior/local carrier fixes
   the site formulas:

   - photon drag at `1 / tau_c`,
   - baryon drag at `R / tau_c`,
   - sound speed at `1 / [3(1+R)]`,
   - inertia at `1+R`,
   - dynamic loading at `R/(1+R)`,
   - diffusion at the unique heat/viscosity split above.

5. None of those sites inserts a new observer/readout map. They are algebraic
   descendants of one primitive local enthalpy observable inside the same local
   bulk hierarchy, plus explicit Thomson/history companions where appropriate.
   So no new baryon slot is created there.

6. The observed peak-height ratio is a readout functional of the evolved
   hierarchy and transfer chain, not a primitive local coefficient. So
   `omega_b,eff` is not back-propagated into any of the four primitive
   oscillator sites.

QED.

## Exact boundary

Accepted scope:

- equal-rate scoped branch
  `thomson_hierarchy_rate = thomson_drag_rate`

What is closed:

- primitive local `R` leg -> `omega_b,geom`
- full site-wise hierarchy operator
  `(Gamma_gammab, Gamma_bgamma, c_bgamma^2, M_bgamma, L_odd/even, D_heat, D_visc, D_silk)`
- dynamic odd/even loading inside the oscillator
- explicit separation between the primitive local oscillator and the downstream
  observed peak-height readout

What is not claimed:

- that observer-side `omega_b,eff` becomes any primitive local oscillator
  coefficient
- that the full observed peak-height pattern is itself a one-slot baryon
  observable
- that the exploratory TT driver has already validated the late-time handoff
  after every corrected coefficient is inserted

## Calculator implementation

The theorem is encoded in

- [typed_r_operator.py](/opt/cosmology-lab/calculator/src/aio_calculator/typed_r_operator.py)

and surfaced into the hierarchy and theorem dictionary through

- [scalar_acoustic_operator.py](/opt/cosmology-lab/calculator/src/aio_calculator/scalar_acoustic_operator.py)
- [perturbation_types.py](/opt/cosmology-lab/calculator/src/aio_calculator/perturbation_types.py)
- [provenance.py](/opt/cosmology-lab/calculator/src/aio_calculator/provenance.py)

## Honest conclusion

The exact typed `R` closure is **not**

- `R -> omega_b,eff`,
- `R -> omega_b,clustering`,
- or a role-by-role baryon-slot swap between different carried densities.

It is:

- one primitive local enthalpy ratio on `omega_b,geom`,
- a full site-wise hierarchy operator built from that ratio plus the Thomson
  tuple,
- and a strict non-backpropagation boundary preventing observer-side readout
  typing from retagging the primitive oscillator.
