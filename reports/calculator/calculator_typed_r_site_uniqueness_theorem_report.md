# Calculator Typed `R` Site-uniqueness Theorem

Date: 2026-04-15

## Executive result

- `derived / scoped`:
  on the accepted equal-rate scoped branch
  `thomson_hierarchy_rate = thomson_drag_rate`, the site-wise typed hierarchy
  placements in the full typed `R` operator are
  the **unique admissible** placements on the current IO stack.
- `derived / scoped`:
  no alternative typed `R` placement is compatible simultaneously with
  - the primitive local enthalpy theorem,
  - the no-single-slot theorem,
  - the Thomson-history tuple theorem,
  - and the lower-triangular non-backpropagation boundary.

This is the missing named theorem Cosmo asked for.

## Question

The full typed `R` operator gives the four actual hierarchy sites:

1. momentum coupling,
2. pressure restoring force,
3. baryon inertia / dynamic odd-even loading,
4. Silk damping.

Are those only structurally plausible, or are they the unique admissible typed
placements?

## Inputs

1. Primitive local enthalpy theorem

   `R_local,geom = 3 rho_b,geom / (4 rho_gamma)`

   is the primitive local baryon-photon enthalpy ratio.

2. No-single-slot theorem

   the full hierarchy does not close by any pure substitution

   `R -> R(omega_b^*)`.

3. Thomson-history tuple theorem

   the exact hierarchy carrier is the coupled tuple

   `(thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear)`

   with

   `tau_c = 1 / thomson_drag_rate`.

4. Lower-triangular non-backpropagation boundary

   observer/readout typing does not propagate backward into the primitive local
   thermodynamic bulk leg.

## Theorem 37.RU1 (typed `R` site-uniqueness theorem)

### Statement

On the accepted equal-rate scoped branch

`thomson_hierarchy_rate = thomson_drag_rate`,

the unique admissible site-wise hierarchy placements on the current IO stack
for the closed scalar photon-baryon oscillator are:

1. Momentum coupling

   `Gamma_gammab = thomson_drag_rate`

   `Gamma_bgamma = R_local,geom * thomson_drag_rate = R_local,geom / tau_c`

2. Pressure restoring force

   `c_bgamma^2 = 1 / [3 (1 + R_local,geom)]`

3. Inertia and dynamic odd-even loading

   `M_bgamma = 1 + R_local,geom`

   `L_odd/even = R_local,geom / (1 + R_local,geom)`

4. Silk damping

   `D_heat = R_local,geom^2 / [6 (1+R_local,geom)^2 thomson_drag_rate]`

   `D_visc = 16 / [90 (1+R_local,geom) thomson_hierarchy_rate]`

   `D_silk = D_heat + D_visc`

No alternative site placement is theorem-grade admissible.

### Proof

#### Step 1. Pressure and inertia cannot move off the primitive local enthalpy object

The pressure and inertia sites are the primitive local baryon-photon enthalpy
sites. Moving either one off `R_local,geom` would require at least one of:

- a drag-vs-sound branch separation for the same primitive local `R`,
- observer/readout back-propagation into the primitive thermodynamic row,
- or a new primitive local object distinct from the local enthalpy ratio.

All three are already killed:

- the primitive local enthalpy theorem fixes the local object,
- the lower-triangular boundary kills observer/readout backflow,
- the prior Paper 34 sound/inertia audits kill a separate primitive sound-speed
  rung.

Therefore the unique pressure/inertia placements are

`c_bgamma^2 = 1 / [3 (1 + R_local,geom)]`

and

`M_bgamma = 1 + R_local,geom`,

with the corresponding dynamic loading factor

`L_odd/even = R_local,geom / (1 + R_local,geom)`.

#### Step 2. Momentum coupling is fixed once the tuple convention is fixed

The hierarchy carrier uses

`tau_c = 1 / thomson_drag_rate`.

Therefore the photon-side scattering coefficient is already fixed:

`Gamma_gammab = thomson_drag_rate`.

The baryon-side coefficient must be the enthalpy-weighted reciprocal coupling,
so on this carrier it is

`Gamma_bgamma = R_local,geom / tau_c = R_local,geom * thomson_drag_rate`.

Any alternative:

- `thomson_drag_rate / R_local,geom`,
- or a distinct slot substitution inside `R`,

either changes carrier convention or reopens the forbidden one-slot
reassignment route. Hence the momentum site is unique.

#### Step 3. Silk damping is forced to split by sector

The standard one-rate diffusion law is

`D_silk = [1 / (6 kappa')] * [R^2 / (1+R) + 16/15] / (1+R)`.

On the full tuple carrier, the hierarchy has two distinct local sectors:

- the slip/TCA sector governed by `tau_c`, `dtau_c`, and drag,
- the photon hierarchy/shear sector governed by the hierarchy rate.

The heat-conduction term is the slip-sector term, so it must inherit
`thomson_drag_rate`:

`D_heat = R_local,geom^2 / [6 (1+R_local,geom)^2 thomson_drag_rate]`.

The viscosity term is the photon-shear hierarchy term, so it must inherit
`thomson_hierarchy_rate`:

`D_visc = 16 / [90 (1+R_local,geom) thomson_hierarchy_rate]`.

Assigning both pieces to one rate collapses the split tuple. Swapping them
misidentifies the slip and hierarchy sectors. So the damping split is unique.

#### Step 4. Exhaustion

Every surviving alternative falls into one of the killed families:

- one-slot substitution,
- primitive-site reassignment off the local enthalpy object,
- observer-side back-propagation,
- convention mismatch in the momentum coefficient,
- or loss of the drag/hierarchy sector distinction.

Therefore the site map above is the unique admissible typed hierarchy operator.

QED.

## Boundary

What this theorem closes:

- uniqueness of the four actual oscillator-site placements
- uniqueness of the Silk split on the tuple carrier
- uniqueness of the dynamic odd-even loading factor inside the oscillator

Accepted scope:

- equal-rate scoped branch
  `thomson_hierarchy_rate = thomson_drag_rate`

What it does not claim:

- that the final observed peak-height pattern is a primitive one-slot baryon
  observable
- that the current TT driver is already fully physically validated
- that a nontrivial drag-vs-hierarchy deformation of the tuple is already
  derived

## Calculator surface

This theorem is surfaced into the theorem dictionary as:

- `local.typed_r_site_uniqueness`

and supports:

- `local.typed_r_operator`
- `local.closed_scalar_acoustic_generator`
