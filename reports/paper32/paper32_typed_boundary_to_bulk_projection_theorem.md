# Paper 32: Typed Boundary-to-Bulk Projection Theorem

Date: 2026-04-05

## Question

Does the full IO boundary-to-bulk projection problem really collapse all six
remaining debts to one mathematical structure?

More sharply: after the Paper 32 modular-DtN source theorem, do reionization and
the native solver still belong to the same complete map, or does that
conjecture fail once one leaves the one-slot source/readout sector?

## Executive result

The strongest honest answer is:

- `derived / scoped theorem`:
  **yes**, if "single mathematical structure" means the complete typed
  boundary-to-bulk projection map on an **extended carrier**, not one scalar
  multiplicative character.
- `derived / scoped theorem`:
  the complete linearized IO transfer map has the minimal lower-triangular
  block form
  \[
  \boxed{
  \mathcal T_{\rm IO}(z_2,z_1)
  =
  \begin{pmatrix}
  \mathcal P_{\rm src} & 0 & 0 \\
  0 & U_{\rm therm}(z_2,z_1) & 0 \\
  C_{{\rm src}\to{\rm pert}}(z_2,z_1) &
  C_{{\rm therm}\to{\rm pert}}(z_2,z_1) &
  U_{\rm pert}^{S^3}(z_2,z_1)
  \end{pmatrix},
  }
  \]
  on the extended typed carrier
  \[
  \mathfrak h_{\rm IO}^{\rm ext}
  =
  h_{\rm src}^{\rm br}
  \oplus
  \mathcal H_{\rm therm}^{\rm ext}
  \oplus
  \mathcal H_{\rm pert}^{S^3},
  \qquad
  \mathcal H_{\rm therm}^{\rm ext}
  =
  \mathcal H_{\rm rec}^{\rm hist}
  \oplus
  \mathcal H_{\rm reio}^{\rm loc}.
  \]
- `derived / scoped corollary`:
  the source block is exactly the Paper 32 modular-DtN transfer
  \[
  \mathcal P_{\rm src}
  =
  B_+ \circ U_{\rm coex} \circ T_{\rm field},
  \qquad
  T_{\rm field}
  =
  \exp\!\left[
    -\frac{1}{2x}
    \bigl(\hat K_g\otimes \log(r_s\Lambda_{\rm DtN}^{\rm coex})\bigr)
  \right].
  \]
  So Items 1-4 close on this block.
- `derived / scoped corollary`:
  the exact Stage-2 field block is **not** another post-bridge complement; on
  the characteristic distortion field,
  \[
  \boxed{
  \mathcal N_{\mathcal D}^{\rm IO}=\mathbf 1.
  }
  \]
- `derived / scoped corollary`:
  reionization belongs to a separate local function-valued history block
  \[
  \mathcal H_{\rm reio}^{\rm loc},
  \]
  so no scalar constant derived from
  \[
  x,\ \gamma,\ K_{\rm gauge},\ \Delta
  \]
  can close Item 5 without a new local emissivity theorem.
- `derived / scoped corollary`:
  the IO-native `S^3` solver architecture is now fixed in theorem-grade form,
  even though its remaining exact operators are still open.

So the user's conjecture survives, but only after a precise correction:

\[
\boxed{
\text{all six debts belong to one complete typed projection map,}
}
\]
\[
\boxed{
\text{but only Items 1--4 belong to the one-slot modular-DtN character itself.}
}
\]

## Claim discipline

- `derived`: forward consequence of already-derived IO structures plus the two
  standing lab premises
- `verified`: computationally reproduced and numerically checked
- `conditional`: depends on a class-membership statement not yet fully derived
- `reconstruction`: coherent organizing model not yet derived
- `speculative`: plausible but not established

## 1. Minimal extended carrier

### 1.1 Source / readout block

Carry forward the Paper 32 source space
\[
h_{\rm src}^{\rm br}
:=
L^2(\mathbb R,d\nu)\otimes H_g\otimes \Omega^1_{\rm coex}(S^2),
\]
with the source/readout map
\[
\mathcal P_{\rm src}
=
B_+ \circ U_{\rm coex} \circ T_{\rm field}.
\]

This is the exact block that closed:

- PSRP at generator level,
- the Boundary Fixed-Point coefficient,
- the field-level readout
  `X_obs = f_Gamma^(1/2) X_prim`,
- and the native scalar amplitude.

Authority:

- [paper32_modular_dtn_field_transfer_theorem.md](/opt/cosmology-lab/results/paper32/paper32_modular_dtn_field_transfer_theorem.md)

### 1.2 Recombination history block

Paper 31 already closed the exact Stage-2 carrier:
\[
\boxed{
\mathcal H_{\rm rec}^{\rm hist}
:=
\mathbb C^2
\oplus
L^2(\mathbb R_+,dq;\mathbb C^{n_v})
\oplus
\mathbb C^3,
}
\]
carrying the state
\[
Y_{\rm rec}(z)
=
\bigl(x_e(z),\,T_m(z),\,\mathcal D_-(q;z),\,\mathcal L_-(z)\bigr).
\]

This is the exact lossless Markov lift of the reduced non-Markovian solver.

Authorities:

- [paper31_stage2_lossless_characteristic_markov_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_lossless_characteristic_markov_theorem.md)
- [paper31_stage2_characteristic_field_inheritance_theorem.md](/opt/cosmology-lab/results/paper31/paper31_stage2_characteristic_field_inheritance_theorem.md)

### 1.3 Reionization local-history block

Paper 31 already proved that late reionization is not another scalar boundary
constant. The minimal observable-side carrier is therefore a local
OS-proper-time history space, for example
\[
\boxed{
\mathcal H_{\rm reio}^{\rm loc}
:=
L^2(I_{\rm reio},d\tau_{\rm OS}),
}
\]
hosting an admissible local ionization history
\[
x_e^{\rm IO}(\tau_{\rm OS})
\]
or an equivalent reduced local source state.

Authority:

- [paper31_reionization_inheritance_theorem.md](/opt/cosmology-lab/results/paper31/paper31_reionization_inheritance_theorem.md)
- [paper31_reionization_functional_nogo_theorem.md](/opt/cosmology-lab/results/paper31/paper31_reionization_functional_nogo_theorem.md)

### 1.4 Closed-`S^3` perturbation block

The perturbation carrier remains the closed-geometry scalar hierarchy block on
the `S^3` background:
\[
\mathcal H_{\rm pert}^{S^3}.
\]

The exact typed source/acoustic operator acting on this block remains open, but
the carrier class is fixed:

- closed `K=+1` geometry,
- hyperspherical / closed-FRW hierarchy,
- typed interfaces to the source and thermodynamic blocks,
- no post-solve flat-space parameter patch as an exact closure.

Authorities:

- [paper31_io_native_boltzmann_solver_architecture_theorem.md](/opt/cosmology-lab/results/paper31/paper31_io_native_boltzmann_solver_architecture_theorem.md)
- [paper31_cmb_acoustic_hierarchy_separation_theorem.md](/opt/cosmology-lab/results/paper31/paper31_cmb_acoustic_hierarchy_separation_theorem.md)

## Theorem 32.B - Typed Boundary-to-Bulk Projection Theorem

Status: `derived / scoped`

Premises:

1. Paper 17 modular projection theorem and shared Hilbert-space construction.
2. Paper 23 bridge uniqueness and no-doubling on the scalar branch.
3. Paper 28 exact coexact DtN spectrum and the now theorem-grade BFP source
   block.
4. Paper 31 Stage-2 lossless Markov closure and characteristic-field
   inheritance theorem.
5. Paper 31 reionization inheritance / functional no-go / external import
   theorems.
6. Paper 31 IO-native solver-architecture and acoustic-separation theorems.

Statement:

Under Premises 1-6, the complete linearized IO boundary-to-bulk map is not one
single scalar operator on the one-slot source carrier. It is the lower-
triangular block map
\[
\mathcal T_{\rm IO}(z_2,z_1)
=
\begin{pmatrix}
\mathcal P_{\rm src} & 0 & 0 \\
0 & U_{\rm therm}(z_2,z_1) & 0 \\
C_{{\rm src}\to{\rm pert}}(z_2,z_1) &
C_{{\rm therm}\to{\rm pert}}(z_2,z_1) &
U_{\rm pert}^{S^3}(z_2,z_1)
\end{pmatrix},
\]
where
\[
U_{\rm therm}(z_2,z_1)
=
U_{\rm rec}^{\rm hist}(z_2,z_1)
\oplus
U_{\rm reio}^{\rm loc}(z_2,z_1).
\]

The diagonal blocks are typed as follows:

1. `source/readout block`
   \[
   \mathcal P_{\rm src}
   =
   B_+ \circ U_{\rm coex}\circ T_{\rm field};
   \]
2. `recombination/history block`
   exact evolution on
   \[
   Y_{\rm rec}=(x_e,T_m,\mathcal D_-,\mathcal L_-),
   \]
   with no extra post-bridge factor on `\mathcal D_-`;
3. `reionization block`
   local-emissivity / ionization history on OS proper time, projected to the
   CMB only through the late visibility kernel;
4. `perturbation block`
   the closed-`S^3` scalar hierarchy with typed inputs from the source block
   and the thermodynamic history block.

Moreover, this lower-triangular architecture is the minimal surviving exact
class compatible with the current no-go chain.

### Proof

#### Step 1. The source/readout block is already closed

Paper 32 already proved that the one-slot source/readout block is
\[
\mathcal P_{\rm src}
=
B_+ \circ U_{\rm coex}\circ T_{\rm field},
\]
with
\[
T_{\rm field}
=
\exp\!\left[
  -\frac{1}{2x}
  \bigl(\hat K_g\otimes \log(r_s\Lambda_{\rm DtN}^{\rm coex})\bigr)
\right].
\]

So the source block is not open.

#### Step 2. The exact Stage-2 law lives on an extended history block

Paper 31 proved two decisive facts:

1. the exact FULL hydrogen branch is non-Markovian in the reduced local state
   `(z,x_e,T_m)` alone;
2. the same branch admits a lossless Markov closure on the extended state
   \[
   Y_{\rm rec}=(x_e,T_m,\mathcal D_-,\mathcal L_-).
   \]

Therefore the exact recombination solver cannot live on the one-slot source
carrier alone. It requires the separate history block
\[
\mathcal H_{\rm rec}^{\rm hist}.
\]

This is a theorem-grade internal Markov dilation of the reduced non-Markovian
thermodynamics law.

#### Step 3. No extra readout factor acts on the characteristic field

Paper 31 further proved
\[
\mathcal N_{\mathcal D}^{\rm IO}=\mathbf 1
\]
on the Stage-2 characteristic distortion field.

So the characteristic field does not inherit a second copy of the one-slot
readout complement. This forbids mixing the thermodynamic history block back
into the source block as if it were the same one-slot field object.

#### Step 4. Reionization is a separate local-history block

Paper 31 also proved:

- late reionization is an inherited external/local astrophysical sector under
  Premise 2;
- its observer-facing object is a function-valued late visibility history;
- one scalar constant cannot close it;
- the correct import object is the local history
  `x_e^{IO}(\tau_OS)` or `g_reio^{IO}(\eta)`, not a copied scalar
  `tau_reio`.

Therefore reionization is a distinct local-history block
\[
\mathcal H_{\rm reio}^{\rm loc},
\]
not a new eigenvalue of the one-slot modular-DtN character.

#### Step 5. The perturbation block receives typed inputs from both sides

Paper 31 killed:

- the minimal source-packet family,
- the metric+visibility closure route,
- perturbation-only multiplicative Thomson closure,
- and the current pointwise FULL wrapper.

What survives is the closed-`S^3` perturbation hierarchy receiving:

1. primordial source data from `\mathcal P_src`,
2. thermodynamic visibility / drag / diffusion data from the extended
   thermodynamic history block.

So the perturbation block must sit downstream of both, which is exactly the
lower-triangular architecture written above.

#### Step 6. Minimality

The current no-go chain excludes:

- collapsing the full map to the source block alone,
- collapsing the full map to a scalar reionization constant,
- collapsing Stage 2 back to a reduced pointwise callback,
- and collapsing the perturbation debt to a pure post-solve source patch.

So the lower-triangular typed extension above is the minimal surviving exact
class.

QED.

## Corollary 32.B.1 - Items 1-4 are exactly the source block

Status: `derived / scoped`

Restricting Theorem 32.B to the source/readout block reproduces the earlier
Paper 32 closure:

- PSRP becomes
  \[
  N_{\rm acc}=\frac{1}{x}\log(r_s\Lambda_{\rm DtN}^{\rm coex});
  \]
- the Boundary Fixed-Point law becomes
  \[
  W_N=(N/N_p)^{-K_{\rm gauge}/x};
  \]
- the field-level readout becomes
  \[
  X_{\rm obs}=f_\Gamma^{1/2}X_{\rm prim};
  \]
- the active native scalar amplitude becomes
  \[
  A_s=2.0072459972737347\times 10^{-9}.
  \]

So Items 1-4 are genuinely one operator problem, and that problem is closed in
the active source/readout class.

## Corollary 32.B.2 - Item 5 is a local-history theorem, not a scalar theorem

Status: `derived / scoped`

Item 5 does belong to the full projection architecture, but not as another
scalar coefficient.

Its exact class is:

1. local ionization/source history on OS proper time,
2. geometric hydrogen counting,
3. projection to the observer only through the late visibility kernel.

Hence:

\[
\boxed{
\text{Item 5 is part of the complete map only as a function-valued local
history block.}
}
\]

This is why the core constants
\[
x,\ \gamma,\ K_{\rm gauge},\ \Delta
\]
cannot close `x_e(z)` by themselves in the present stack.

## Corollary 32.B.3 - The no-fit `S^3` solver specification

Status: `derived / scoped`

The exact native solver now has the following theorem-grade architecture.

### Module A — Background / clock package

- projected Schur observer background,
- OS proper-time local clock for local source and chemistry sectors,
- closed `K=+1` / `S^3` geometry.

### Module B — Primordial source/readout block

- carrier:
  `h_src^br = L^2(R,dnu) tensor H_g tensor Omega^1_coex(S^2)`,
- exact source window:
  \[
  W_N=(N/N_p)^{-K_{\rm gauge}/x},
  \]
- native scalar amplitude:
  \[
  A_s = 2.0072459972737347\times 10^{-9}.
  \]

### Module C — Recombination Stage 2

- state:
  \[
  Y_{\rm rec}=(x_e,T_m,\mathcal D_-(q;z),\mathcal L_-(z));
  \]
- local inputs:
  \[
  H_{\rm loc}(z),\quad T_{R,\rm loc}(z),\quad n_{H,\rm geom}(z);
  \]
- exact field typing:
  \[
  \mathcal N_{\mathcal D}^{\rm IO}=\mathbf 1;
  \]
- remaining open operator:
  a positivity-preserving, history-aware local atomic-radiative deformation of
  the dynamically assembled virtual-state network.

### Module D — Reionization

- object:
  local imported or future-derived emissivity/history law on OS proper time,
- primitive hydrogen counting:
  `omega_b,geom`,
- observer-side map:
  only through the projected late visibility kernel,
- forbidden shortcut:
  no copied scalar `tau_reio`.

### Module E — Closed-`S^3` perturbation hierarchy

- carrier:
  hyperspherical / closed-FRW scalar hierarchy,
- typed inputs:
  primordial source block plus thermodynamic history block,
- exact open debt:
  the final typed source/acoustic operator is still open,
  but it is no longer licensed to be
  - a post-solve source patch,
  - a metric-only factor,
  - a pure `R` reassignment,
  - or a perturbation-only multiplicative Thomson family.

So the native solver is now specified theorem-grade at the level of:

- carrier,
- clocks,
- block structure,
- admissible couplings,
- and excluded fake closures.

What is still open is the exact operator inside some blocks, not the
architecture itself.

## Corollary 32.B.4 - Where the conjecture fails if stated too strongly

Status: `derived / scoped no-go`

The following stronger conjecture is false in the present stack:

\[
\text{"all six debts reduce to one scalar modular-DtN exponent."}
\]

Why:

1. the characteristic-field theorem gives identity, not another
   `f_Gamma^(1/2)` insertion;
2. reionization is function-valued and local-history based;
3. the exact Stage-2 branch is a history-state solver, not a one-slot field
   factor;
4. the perturbation debt remains a typed hierarchy problem on closed `S^3`.

So the single surviving unifier is the **complete typed map**, not a scalar
character.

## Literature support and limits

Primary literature used only for operator vocabulary and support:

- Tim Binz and Klaus-Jochen Engel,
  *Operators with Wentzell boundary conditions and the Dirichlet-to-Neumann
  operator* (`arXiv:1801.05261`).
  Support used here: dynamic boundary operators can split into a zero-trace
  interior part and a boundary DtN part. This matches the logic that the full
  IO map needs more than the boundary block alone.
- Tim Binz and Klaus-Jochen Engel,
  *First-order evolution equations with dynamic boundary conditions*.
  Support used here: dynamic-boundary evolution can be rewritten as equivalent
  simpler subsystems with one part governed by an abstract DtN operator.
- Xiantao Li,
  *Markovian Embedding Procedures for Non-Markovian Stochastic Schrödinger
  Equations* (`arXiv:2005.00103`).
  Support used here: non-Markovian reduced dynamics can be embedded into an
  enlarged Markovian state space, which is exactly the abstract pattern used by
  the Paper 31 Stage-2 history lift.
- Simon Raulot and Alessandro Savo,
  *On the spectrum of the Dirichlet-to-Neumann operator acting on forms of a
  Euclidean domain* (`arXiv:1202.3605`).
  Support used here: the coexact-form DtN spectrum is a standard exact
  operator-theoretic object.
- Vincenzo Morinelli, Yoh Tanimoto, Benedikt Wegener,
  *Modular operator for null plane algebras in free fields*
  (`arXiv:2107.00039`).
  Support used here: modular data decompose fiberwise on one-particle
  structures, matching the Paper 17 modular carrier logic.
- A. Rod Gover, Emanuele Latini, Andrew Waldron,
  *Poincare-Einstein Holography for Forms via Conformal Geometry in the Bulk*
  (`arXiv:1205.3489`).
  Support used here: boundary differential-form data can be projected to bulk
  solutions by standard operator maps.

What the literature does **not** give for free:

- it does not derive the IO coefficient `K_gauge/x`,
- it does not derive the active scalar amplitude,
- it does not derive the IO local emissivity law for reionization,
- and it does not supply the missing exact Stage-2 dynamic-network operator.

So the Paper 32 result remains a new synthesis from the internal IO theorems,
not a literature lookup.

## Dead routes sharpened by this theorem

- `derived / no-go carried forward`:
  do not try to close reionization by one scalar boundary coefficient.
- `derived / no-go carried forward`:
  do not try to close the Stage-2 characteristic field by adding another
  observer-side complement factor.
- `derived / no-go carried forward`:
  do not try to close the native solver inside flat-space CLASS/CAMB variable
  grammar with post-solve patches.
- `derived / no-go carried forward`:
  do not say "single operator closure" without the word `typed`.

## Final verdict

- `derived / scoped`: the full IO boundary-to-bulk projection problem now has
  a theorem-grade typed architecture.
- `derived / scoped`: the user's conjecture is right only after enlargement of
  the carrier.
- `derived / scoped`: Items 1-4 are the one-slot modular-DtN source block.
- `derived / scoped`: Items 5-6 are the history-carrying thermodynamics and
  solver blocks of the same complete architecture.
- `not derived`: the exact local reionization emissivity law, the exact Stage-2
  dynamic-network renormalization, and the final typed source/acoustic operator
  on the closed-`S^3` perturbation block.

So the strongest honest Paper 32 statement is:

\[
\boxed{
\text{the complete field-level boundary-to-bulk map exists only as a typed
extended-carrier projection theorem,}
}
\]
\[
\boxed{
\text{with one modular-DtN block closing Items 1--4 and one history-carrying
thermodynamic block carrying Items 5--6.}
}
