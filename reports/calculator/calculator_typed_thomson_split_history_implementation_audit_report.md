# Calculator Typed Thomson Split-history Implementation Audit

Date: 2026-04-15

## Question

Does the live calculator actually build the Thomson tuple from the typed split
history

- local chemistry / local opacity on the geometric inventory branch,
- observer-side visibility/readout on the acoustic optical branch,

or does it silently flatten everything into one undifferentiated opacity?

## Executive result

- `verified / implementation`:
  the live TT path now exposes the typed split explicitly.
- `derived / scoped as maps`:
  the implementation path is

  `kappa'_loc -> visibility packet -> conformal Thomson tuple`,

  not one raw opacity scalar reused at every layer.

## Live code path

### 1. Local chemistry / primitive local opacity

In [recombination.py](/opt/cosmology-lab/calculator/src/aio_calculator/recombination.py):

- `free_electron_density_m3(z, x_e)` builds
  `n_e = x_e n_H`
- `primitive_local_kappa_prime(z, x_e)` builds
  `kappa'_loc = a n_e sigma_T`

This is the primitive local microphysical contact operator on the geometric
inventory branch.

### 2. Observer-side visibility/readout packet

Still in [recombination.py](/opt/cosmology-lab/calculator/src/aio_calculator/recombination.py):

- `optical_depth_gradient_per_redshift(z, x_e)` builds
  `d tau_obs / dz`
- `build_visibility_packet(history)` then builds
  `tau_obs`
  and
  `g_obs = exp(-tau_obs) d tau_obs / dz`

So the observer-side optical packet is a distinct object constructed from, but
not identical to, the primitive local opacity.

### 3. Conformal Thomson tuple

The live TT driver now goes through
[build_typed_split_thomson_history_realization()](/opt/cosmology-lab/calculator/src/aio_calculator/thomson_history_contract.py),
called by
[build_visibility_derived_conformal_thomson_history()](/opt/cosmology-lab/calculator/src/aio_calculator/scalar_tt_driver.py).

That builder performs:

1. `primitive_local_kappa_prime(z, x_e)`
2. `build_visibility_packet(history)`
3. transport of the visibility packet onto the conformal clock:

   `thomson_drag_rate = |(d tau_obs / dz) / (dC / dz)|`

4. packaging of the tuple through

   `build_thomson_history_contract(...)`

with

`thomson_hierarchy_rate = thomson_drag_rate`,
`tau_c = 1 / thomson_drag_rate`,
`dtau_c = - d(thomson_drag_rate) tau_c^2`.

## Meaning of the split

The current scoped TT driver still uses the equal-rate branch

`thomson_drag_rate = thomson_hierarchy_rate`,

so this audit does **not** claim that a nontrivial drag-vs-hierarchy deformation
is already implemented.

What it does prove is narrower and exact:

- the implementation keeps the local-opacity and observer-side visibility
  layers distinct,
- the conformal tuple is built from the visibility/readout packet and the clock,
  not by passing one undifferentiated opacity scalar straight into the
  hierarchy.

## Verification

The live regression test is
[test_thomson_history_contract.py](/opt/cosmology-lab/calculator/tests/test_thomson_history_contract.py):

- it checks that the typed realization exposes
  `primitive_local_kappa_prime`,
  the full `VisibilityPacket`,
  and the resulting `ThomsonHistoryContract`
- it verifies that the contract drag rate is computed from
  `d_tau_obs_dz / dC_dz`
  rather than from the primitive local opacity directly

## Honest boundary

What is verified:

- typed split history path is explicit in the implementation
- the tuple is built from local opacity plus visibility/readout plus clock

What remains open:

- a theorem-grade nontrivial split
  `thomson_drag_rate != thomson_hierarchy_rate`
- the exact IO-native operator on the coupled tuple beyond the current scoped
  equal-rate realization
