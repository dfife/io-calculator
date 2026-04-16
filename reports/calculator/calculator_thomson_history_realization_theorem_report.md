# Calculator Thomson-History Realization Theorem

## Status line

- `derived / scoped`: the surviving `theta*` branch must be realized on the coupled Thomson-history tuple.
- `derived / no-go`: a single-site `dkappa` rescaling in only one downstream location is not an admissible realization of that branch.

## Theorem 37.TH2 (Thomson-history realization theorem)

### Premises

1. Calculator.TH1 localizes the surviving `theta*` frontier to a broad Thomson-history operator on the coupled drag/hierarchy/TCA tuple.

2. In the local perturbation carrier, the photon-baryon acoustic evolution and tight-coupling subsystem depend on the effective Thomson history through both drag and hierarchy rates, not through a single post-solve source multiplier.

3. The tight-coupling system depends not only on `tau_c` itself but also on `dtau_c` and on the distinct drag/hierarchy rates that feed slip and shear.

### Carrier formulas

The local carrier realizes the surviving family through

    factor(τ) = io_acoustic_scattering_factor * (1 + io_acoustic_scattering_ionization_amp * u_xe(τ))
    thomson_drag_rate = drag_factor(τ) * dkappa(τ)
    thomson_hierarchy_rate = hierarchy_factor(τ) * dkappa(τ)
    tau_c = 1 / thomson_drag_rate
    dtau_c = - d(thomson_drag_rate) * tau_c^2

and the baryon/photon evolution plus TCA closure then depend on

    tau_c, dtau_c, thomson_drag_rate, thomson_hierarchy_rate, slip, shear.

### Statement

Any exact IO-native closure on the surviving `theta*` branch must be realized as
an operator on the coupled Thomson-history tuple

    (thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear).

A single-site rescaling of `dkappa` in only one downstream location is not an
admissible realization of the surviving branch.

### Proof

TH1 already localizes the surviving branch to broad Thomson history.

The carrier equations realize Thomson history in two coupled rates: drag and
hierarchy.

These rates feed `tau_c` and `dtau_c`, which in turn enter slip, shear, and the
baryon/photon evolution equations.

Therefore any admissible exact operator must act coherently on this coupled
tuple. Acting at only one downstream site would break the realized history
grammar and no longer represent the surviving branch. QED.

## Consequence

- The frontier is now more concrete than “deeper Thomson/diffusion operator.”
- The next exact target is the functional form of an IO-native operator on the coupled Thomson-history tuple, potentially with state dependence inherited from the exact Stage-2 chemistry/history block.

