# Paper 29 sound-speed baryon-slot selector audit

## Headline

- `derived / scoped theorem`: on the rebuilt reduced-stack scope, the baryon density entering the local sound-speed loading term
  `R(z) = 3 rho_b / [4 rho_gamma]`
  is uniquely the `alpha = 1` inventory branch `omega_b,geom`.
- `derived`: this does **not** close the full BAO standard-ruler sector. Rebuilt Paper 19 still marks BAO drag-epoch closure as open.

## Why alpha = 1 is the unique theorem-grade slot

1. Paper 18 Theorem 18.B identifies the baryonic selector as a 1-form observable on the standard minimal-coupling matter class.
2. Paper 21 states that the local plasma computation, specifically the Thomson-scattering / baryon-photon integral, is gauge-neutral in the reduced-core sense.
3. In standard tight-coupling physics, `R(z)` is the local inertia coefficient in the photon-baryon fluid equations, built from local stress-energy densities, not from an observer-side readout map.
4. Paper 19's `alpha = 3/2` branch is scoped to late-time clustering scalarization. That scalarization bridge is absent in the local plasma inertia coefficient.
5. Rebuilt Paper 19 says only two baryon classes are theorem-grade at present: `alpha = 1` and `alpha = 3/2`. Since `alpha = 3/2` is ruled out structurally for this slot, `alpha = 1` is unique among theorem-grade classes.

## Exact rebuilt-paper evidence

### Paper 18

- `P131`: Theorem 18.B (BDP Modular Derivation). On the reduced Schwarzschild tangential observer algebra of H_IO (Paper 17), within the standard minimal-coupling matter class, the baryon fraction is:
- `P139`: Step 1. The baryonic observable is the first variation of U_c(A) = P exp(−∫_c A). This is a 1-form / line-transfer observable. (§9.1.)
- `P151`: B4. The baryonic observable is a 1-form transfer observable: the first variation of U_c(A). (Derived in this paper, §9.1.)
- `P156`: The scope limitation is specific: the theorem applies to the standard minimal-coupling matter class. It does not claim to be a theorem of arbitrary hidden-sector or non-minimally coupled dark-matter microphysics. Within the IO framework’s founding assumption that physics inside and outside the horizon is the same, standard minimal coupling is the natural matter class.
- `P168`: This paper derives the baryon fraction from the operator infrastructure of H_IO. The baryonic observable is the first variation of open covariant transport (§9.1), forcing the 1-form type. The derivative selection rule identifies V′(α) = 2γ as the unique first-order covector coefficient (§9.2). Boundary-to-bulk 1-form scaling provides the factor x⁻¹ (§9.3). Combined: f_b = 2γ/x.

### Paper 19

- `P13`: The core discovery: the BDP baryon fraction f_b = 2γ/x = 0.3127 is a gauge-coupling inventory fraction, not a universal late-time density parameter. Different cosmological observables see different effective baryon densities through observable-class Jacobians: ω_b(O) = ω_b^(α=1) × x^(1−α_O), where α_O is the geometric dimension of the observable.
- `P14`: The paper derives, through adversarial multi-AI review and three rounds of Wolfram validation, that the matter power spectrum P(k) evaluates baryons at α = 3/2 on the geometric ladder, corresponding to the free-fall transport scalarization of the BDP 1-form line observable into the scalar density contrast. Three bridge theorems — a density reconstruction theorem, a faithful representation theorem, and a transport no-go theorem — establish that the conserved dust-density scalar entering P(k) necessarily descends from the timelike dust current within the proper-time comoving-dust metric-measure extension of the reduced H_IO observer algebra. The resulting clustering baryon density is ω_b = 0.01705.
- `P121`: 2. BBN and clustering see different effective baryon densities: ω_b,BBN = 0.02108 (α = 1) vs ω_b,clust = 0.01705 (α = 3/2). The split is derived, not fitted.
- `P160`: Applying the theorem: photon radiation (closed), vacuum energy (closed conditionally on local-energy class), curvature (closed conditionally on N_mode), conserved dust/clustering (closed on perturbative/current slot only, not homogeneous Friedmann). The clustering baryon scalarization (α = 3/2) is a perturbation-sector result and does not enter the homogeneous H²(z) directly.
- `P207`: Foundation punch list item #6. The observable-class Jacobian formula ω_b(O) = ω_b^(α=1) × x^(1−α_O) is real once α_O is known. Two classes are theorem-grade: inventory/BDP baryon selector (α = 1, derived Paper 12/18) and late-time total-matter clustering entering P(k) (α = 3/2, derived Paper 19 §§7–10, Wolfram validated). STATUS: CLOSED to current mathematical limit.
- `P208`: Remaining sectors and their specific blockers: CMB acoustics (missing acoustic baryon loading theorem, unreduced CMB perturbation algebra, internal neutrino sector); BAO standard-ruler (missing drag-epoch closure, same blockers as CMB); lensing (missing vector/tensor/multipole reduction, shear/convergence 2-point Hodge package); dark-matter-only maps (DM ontology closed as complementary gauge-neutral dust, but no pure-DM observable-class theorem); neutrino maps (no internal neutrino sector). Each remaining sector is blocked by one or more Paper 20 items (#4 reduced → full extension, #7 radiation-slot identity, #8 spatial Hodge complex). STATUS: Deferred to Paper 20 for remaining sectors.

### Paper 21

- `P44`: G1. The background sound horizon r_s is a 1D acoustic-history observable on the observer-side homogeneous comoving-dust sector. STATUS: DERIVED/THEOREM (Theorem 20.1, AH1–AH7).
- `P45`: G2 / AB5. The local plasma computation (Thomson scattering, baryon-photon integral) is gauge-neutral in the reduced-core sense. STATUS: DERIVED.
- `P62`: Proof. Three candidates eliminated: (1) Local plasma microphysics — ruled out by Paper 20 G2/AB5. (2) Transverse denominator — ruled out by Paper 20 AB4. (3) Universal transport / bulk duplication — ruled out by Paper 16 P6 and Paper 19 FC5. QED.
- `P69`: Within the homogeneous observer-side acoustic-history scope, AC1 is replaced by the derived statement: the numerator readout is one-slot / degree-1; the denominator is gauge-neutral.
- `P70`: Proof. By Paper 20 G1: J_r,geom = x^(1/2). By Paper 20 AB3/AB4: J_D = x, gauge-neutral. By Theorem P21.A4: one-slot degree-1. By Paper 20 PC1–PC2: phase lattice. Therefore J_r = x^(1/2)√(1+γ²), J_D = x, J_θ = x^(-1/2)√(1+γ²) = 0.83395. QED.
- `P150`: Under Paper 17 GTTP theorem, Paper 19 observable-class architecture, Paper 21 Theorem 21.J, and the minimal new premise TIO1 (BBN abundance/rate observables are local bulk thermodynamic plasma observables with no primitive RT/BY optical readout leg), GTTP belongs only to the RT/BY optical readout class. Local bulk thermodynamic observables are on the local/bare branch and are immune to the RT/BY optical GTTP correction.
- `P151`: Proof. GTTP was derived in Paper 17 as a theorem about boundary-photon readout, not as a universal replacement of every thermal scale. Papers 19 and 21 localize that machinery to the optical RT/BY class. Once BBN is typed as local bulk thermodynamics rather than optical readout, GTTP has no primitive slot on which to act. The BBN plasma state stays on the base KMS branch T_IO, with baryon loading on the Paper 19 α = 1 rung. QED.
- `P153`: Scope boundary: This is a theorem about the reduced bulk-vs-optical class architecture. It does not assert that every pre-recombination quantity uses T_IO; it classifies BBN specifically as local bulk thermodynamics, not optical readout.

## Scope boundary

- `derived`: this theorem selects the local `omega_b` slot inside `R(z)`.
- `derived`: it does **not** prove the full drag ruler `r_d`, because rebuilt Paper 19 paragraph 208 explicitly keeps BAO standard-ruler open.
- `killed`: `alpha = 3/2` for sound-speed baryon loading.
- `killed`: any optical GTTP-style dressing on the local baryon-photon integral.

## External standard-physics imports

- Ma & Bertschinger (1995): coupled fluid/Boltzmann/Einstein treatment of baryons and photons. https://arxiv.org/abs/astro-ph/9506072
- Hu & Sugiyama (1995/1996): analytic tight-coupling baryon-loading framework. https://arxiv.org/abs/astro-ph/9510117
- Pookkillath, De Felice, Mukohyama (2019/2020): action-principle and stress-energy derivations of baryon equations in tight coupling. https://arxiv.org/abs/1906.06831
