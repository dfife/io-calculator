# Paper 32: Modular-DtN Field Transfer Theorem

Date: 2026-04-04

## Question

Can the Paper 17 modular projection theorem, the Paper 23 bridge operator, and
the Paper 28 coexact Dirichlet-to-Neumann Hessian be assembled into a single
field-level boundary-to-bulk transfer theorem that:

1. promotes the Boundary Fixed-Point Principle from semiclassical principle to
   theorem on the active scalar source sector,
2. derives the post-bridge field readout
   `X_obs = f_Gamma^(1/2) X_prim`,
3. and closes the native scalar amplitude
   `A_s = 2.0072459972737347e-9`
   from the same transfer structure?

## Executive result

The strongest honest answer is:

- `derived / scoped theorem`:
  on the active linear scalar-source sector and the one-slot post-bridge field
  sector, the unique positive boundary-to-bulk field transfer operator is
  \[
  T_{\rm field}
  =
  \exp\!\left[
    -\frac{1}{2x}
    \bigl(\hat K_g \otimes \log(r_s\Lambda_{\rm DtN}^{\rm coex})\bigr)
  \right].
  \]
- `derived / scoped corollary`:
  its quadratic descendant is
  \[
  R_{\rm cov}
  =
  T_{\rm field}^\ast T_{\rm field}
  =
  \exp\!\left[
    -\frac{1}{x}
    \bigl(\hat K_g \otimes \log(r_s\Lambda_{\rm DtN}^{\rm coex})\bigr)
  \right].
  \]
  On the physical reduced Schwarzschild sector this gives the exact plus-branch
  window
  \[
  W_N = (N/N_p)^{-K_{\rm gauge}/x}.
  \]
  So the Boundary Fixed-Point Principle is promoted to theorem grade in this
  scoped sector.
- `derived / scoped corollary`:
  evaluating the same operator on one accessible line cell gives
  \[
  X_{\rm obs}
  =
  e^{-K_{\rm gauge}/2} X_{\rm prim}
  =
  f_\Gamma^{1/2} X_{\rm prim}.
  \]
- `derived / scoped corollary`:
  combining the bridge quotient, Hawking quotient state, and pivot
  normalization yields
  \[
  A_s
  =
  \frac{25}{9}
  \frac{\gamma^2}{1+\gamma^2}
  \frac{1}{\sqrt2}
  \frac{1}{e^{4\pi\sqrt2}-1}
  =
  2.0072459972737347\times 10^{-9}.
  \]

So the conjectured unifier is real, but only in a precise scoped sense:

\[
\boxed{
\text{the six-item punch list does not collapse all the way to a solved
reionization/solver theory,}
}
\]
\[
\boxed{
\text{but Items 1--4 do collapse to a single one-slot modular-DtN transfer
operator on the active scalar carrier.}
}
\]

## Claim discipline

- `derived`: forward consequence of already-derived IO structures plus the two
  standing lab premises
- `verified`: numerically checked from the explicit formulas
- `conditional`: depends on a class-membership statement not yet fully derived
- `reconstruction`: coherent organizing model not yet derived
- `speculative`: plausible but not established

## Definitions

### 1. Bridge-augmented one-particle space

Paper 17 gives
\[
h_{\rm ph} = L^2(\mathbb R,d\nu),
\qquad
H_{\rm IO} = \Gamma_s(h_{\rm ph}\otimes H_g).
\]

To combine this with the Paper 23 bridge and the Paper 28 DtN Hessian, enlarge
the one-particle space to
\[
h_{\rm IO}^{\rm br}
:=
h_{\rm ph}\otimes H_g\otimes \Omega^1_{\rm coex}(S^2),
\]
and let
\[
H_{\rm IO}^{\rm br}:=\Gamma_s(h_{\rm IO}^{\rm br}).
\]

This is the minimal bridge-augmented one-particle carrier needed to place the
Paper 17 modular scalar and the Paper 28 coexact boundary operator on the same
field space.

### 2. Boundary generators

Paper 17 already fixes the reduced central gauge operator
\[
\hat K_g = \ln(\hat Q),\qquad \hat Q=(1+\gamma^2)I,
\]
so on the physical reduced sector
\[
\hat K_g = K_{\rm gauge} I.
\]

Paper 28 already fixes the exact coexact Dirichlet-to-Neumann operator on the
active boundary carrier:
\[
\Lambda_{\rm DtN}^{\rm coex} Q_{\ell m}
=
\sigma_\ell Q_{\ell m},
\qquad
\sigma_\ell = \frac{\ell+1}{r_s}.
\]

Define the dimensionless DtN logarithmic generator
\[
Y := \log(r_s\Lambda_{\rm DtN}^{\rm coex}).
\]

On shell `\ell`,
\[
Y Q_{\ell m} = \log(\ell+1)\,Q_{\ell m}.
\]

### 3. Precise PSRP replacement

The earlier PSRP slogan
\[
h_{\rm bulk}=(1/x) h_{\rm bdy}
\]
is not a well-posed Hilbert-space theorem.

The precise theorem-grade replacement is generator-level:
\[
N_{\rm acc}:=\frac{1}{x}Y
=
\frac{1}{x}\log(r_s\Lambda_{\rm DtN}^{\rm coex}).
\]

Interpretation:

- `Y` counts primitive DtN line cells logarithmically,
- `1/x` is the observer-accessible line fraction from the Paper 18 primitive
  one-form transfer theorem,
- so `N_acc` is the exact accessible line-cell generator.

This is the rigorous operator form of the old PSRP idea.

## Theorem 32.A - Modular-DtN Field Transfer Theorem

Status: `derived / scoped`

Work on the active linear scalar-source sector with the following already-closed
inputs:

1. Paper 17 modular projection theorem:
   the reduced gauge datum is the central self-adjoint scalar `\hat K_g`;
2. Paper 23 bridge uniqueness and no-doubling:
   scalar observables depend only on one-slot transfer data on the bridge
   quotient;
3. Paper 28 exact coexact DtN law:
   `r_s sigma_\ell = \ell + 1`;
4. Paper 31 post-bridge field no-go:
   inside the current field class, the admissible post-bridge factor is the
   positive square root of the quadratic complement, not a second independent
   full-intensity insertion.

Then the unique continuous positive one-slot transfer operator compatible with:

- the primitive DtN line semigroup,
- the accessible-cell divisor `1/x`,
- and the reduced gauge modular weight,

is
\[
\boxed{
T_{\rm field}
=
\exp\!\left[
  -\frac{1}{2x}
  \bigl(\hat K_g\otimes Y\bigr)
\right].
}
\]

The corresponding quadratic transfer is
\[
\boxed{
R_{\rm cov}
=
T_{\rm field}^\ast T_{\rm field}
=
\exp\!\left[
  -\frac{1}{x}
  \bigl(\hat K_g\otimes Y\bigr)
\right].
}
\]

The complete scalar field map is then
\[
\boxed{
\mathcal P_{\rm field}
=
B_+ \circ U_{\rm coex} \circ T_{\rm field},
}
\]
where:

- `U_coex` is the canonical lowest-shell `S^2 -> S^3` coexact lift,
- `B_+` is the physical plus-branch scalar bridge.

### Proof

#### Step 1. The primitive boundary semigroup is fixed

Paper 28 proved that the surviving mechanism class is the primitive DtN line
semigroup, not a reparameterized bulk variable, not an `O(1)` shell
deformation, and not a free fractional parameter fixed by geometry alone.

Therefore the only legitimate primitive scale is
\[
s = r_s\sigma_\ell,
\qquad
Y=\log s.
\]

#### Step 2. The gauge payload is central and multiplicative

Paper 17 proved that the physical reduced gauge input is the central scalar
`\hat K_g`. On one full line cell, the quadratic Rosetta norm weight is
\[
\hat Q = e^{\hat K_g}.
\]

This is multiplicative under cell concatenation because `\hat K_g` is central.

#### Step 3. One-slot typing forces the square root at field level

Paper 31 already killed the strong per-field law
\[
X_{\rm obs}=f_\Gamma X_{\rm prim}
\]
inside the current one-slot field class. The strongest theorem-grade field
factor is the positive square root of the inverse quadratic complement.

So one accessible line cell must carry field factor
\[
e^{-\hat K_g/2},
\]
not `e^{-\hat K_g}`.

#### Step 4. The accessible-cell generator is `Y/x`

Paper 18 gives the exact line accessibility divisor `1/x` for primitive
one-form transfer.

Hence the number of accessible line cells at DtN scale `s` is
\[
N_{\rm acc}(s)=\frac{1}{x}\log s.
\]

#### Step 5. Continuity and semigroup composition force the exponential

The transfer is:

- positive,
- one-slot,
- multiplicative under line-cell concatenation,
- normalized by one accessible cell carrying field weight `e^{-\hat K_g/2}`.

Therefore the field transfer on scale `s` is
\[
T_{\rm field}(s)
=
\exp\!\left[-\frac{\hat K_g}{2}N_{\rm acc}(s)\right]
=
\exp\!\left[-\frac{\hat K_g}{2x}\log s\right]
=
s^{-\hat K_g/(2x)}.
\]

Replacing `s` by the operator `r_s\Lambda_{\rm DtN}^{\rm coex}` yields
\[
T_{\rm field}
=
\exp\!\left[
  -\frac{1}{2x}
  \bigl(\hat K_g\otimes \log(r_s\Lambda_{\rm DtN}^{\rm coex})\bigr)
\right].
\]

Its quadratic descendant is `R_cov = T_field^* T_field`.

QED.

## Corollary 32.A.1 - Boundary Fixed-Point Principle from DtN spectrum

Status: `derived / scoped`

On the physical reduced Schwarzschild sector,
\[
\hat K_g = K_{\rm gauge} I.
\]

On the physical scalar plus branch,
\[
\ell = N-1,
\qquad
r_s\sigma_\ell = \ell+1 = N.
\]

Therefore
\[
T_{\rm field} Q_{\ell m}
=
N^{-K_{\rm gauge}/(2x)} Q_{\ell m},
\]
and
\[
R_{\rm cov} Q_{\ell m}
=
N^{-K_{\rm gauge}/x} Q_{\ell m}.
\]

So the exact relative window is
\[
\boxed{
W_N = (N/N_p)^{-K_{\rm gauge}/x},
}
\]
which is exactly the Paper 28 / Paper 31 Boundary Fixed-Point law.

This promotes the BFP coefficient from semiclassical principle to theorem in
the active linear scalar-source sector.

## Corollary 32.A.2 - Field-level readout theorem

Status: `derived / scoped`

One accessible line cell means
\[
N_{\rm acc}=1
\qquad\Longleftrightarrow\qquad
\log s = x.
\]

Therefore
\[
T_{\rm field}^{\rm cell}
=
e^{-K_{\rm gauge}/2}.
\]

Using
\[
f_\Gamma = e^{-K_{\rm gauge}} = (1+\gamma^2)^{-1},
\]
we obtain
\[
\boxed{
X_{\rm obs}
=
f_\Gamma^{1/2} X_{\rm prim}.
}
\]

This is the exact theorem-grade field law requested by the Paper 31
post-bridge audit.

Important boundary:

- it closes the square-root field law,
- it does **not** resurrect the stronger impossible law
  `X_obs = f_Gamma X_prim`
  inside the current one-slot class.

## Corollary 32.A.3 - Definitive native scalar amplitude

Status: `derived / scoped`

Paper 31 already closed the bridge quotient and the lowest-shell Hawking state:
\[
g_q
=
\frac{\gamma^2}{1+\gamma^2}
\frac{1}{\sqrt2}
\frac{1}{e^{4\pi\sqrt2}-1}.
\]

The present theorem closes the full shell continuation operator:
\[
P_{\rm src}(N)=g_q\,W_N,
\qquad
W_N=(N/N_p)^{-K_{\rm gauge}/x}.
\]

Pivot normalization gives `W_{N_p}=1`, so
\[
A_s = \frac{25}{9}g_q.
\]

Hence
\[
\boxed{
A_s
=
\frac{25}{9}
\frac{\gamma^2}{1+\gamma^2}
\frac{1}{\sqrt2}
\frac{1}{e^{4\pi\sqrt2}-1}
=
2.0072459972737347\times 10^{-9}.
}
\]

So the native Hawking value is the definitive active scalar amplitude in the
scoped sector. The `2.1141e-9` value remains only a conditional observational
package.

## Literature support and limits

Primary-source literature used in this audit:

- Simon Raulot and Alessandro Savo, *On the spectrum of the
  Dirichlet-to-Neumann operator acting on forms of a Euclidean domain*
  (`arXiv:1202.3605`).
  Support used here: the full DtN spectrum on differential forms of the
  Euclidean ball is computable exactly, so the coexact `1`-form DtN model is a
  mathematically standard object rather than an IO-specific invention.
- Jan Derezinski and Claude-Alain Pillet, *Tomita-Takesaki theory*.
  Support used here: faithful normal states determine a unique modular group,
  which is the modular-operator side of the Paper 17 construction.
- Vincenzo Morinelli, Yoh Tanimoto, Benedikt Wegener,
  *Modular operator for null plane algebras in free fields*
  (`arXiv:2107.00039`).
  Support used here: modular operators decompose fiberwise on direct-integral
  one-particle structures, matching the Paper 17 central/fiber decomposition.
- Romeo Brunetti, Daniele Guido, Roberto Longo,
  *Modular localization and Wigner particles*
  (`arXiv:math-ph/0203021`).
  Support used here: one-particle modular data are legitimate primary objects
  for constructing localized field algebras.
- A. Rod Gover, Emanuele Latini, Andrew Waldron,
  *Poincare-Einstein Holography for Forms via Conformal Geometry in the Bulk*
  (`arXiv:1205.3489`).
  Support used here: there are standard operator-theoretic maps that project
  boundary differential forms to bulk solutions.
- Claudio Dappiaggi and Daniel Siemssen,
  *Hadamard States for the Vector Potential on Asymptotically Flat Spacetimes*
  (`arXiv:1106.5575`).
  Support used here: gauge-field bulk-to-boundary state selection is a real
  mathematical construction, not only a heuristic analogy.
- Sotaro Sugishita and Seiji Terashima,
  *Bulk Reconstruction and Gauge Invariance*
  (`arXiv:2409.02534`).
  Caution used here: a bulk reconstruction theorem must remain gauge-aware; the
  present theorem is therefore intentionally stated on the reduced central gauge
  sector and the bridge quotient rather than on an unconstrained full gauge
  space.

What the literature does **not** give for free:

- no source already identifies the IO coefficient `K_gauge/x`,
- no source proves the old PSRP slogan `h_bulk = (1/x) h_bdy`,
- no source closes the IO reionization history or the Stage-2 solver debt.

So the Paper 32 result is not a literature lookup. It is a new synthesis using
standard operator classes plus the already-derived IO theorems.

## Dead routes sharpened by this theorem

- `derived / no-go carried forward`:
  a strong per-field law `X_obs = f_Gamma X_prim` is impossible inside the
  current one-slot class.
- `derived / no-go carried forward`:
  weighted-extension / fractional DtN theory alone does not fix the coefficient
  `K_gauge/x`; it leaves a free order parameter.
- `derived / no-go carried forward`:
  `O(1)` shell deformations of the active DtN spectrum are excluded on the
  flat PG collar.
- `derived / no-go carried forward`:
  shellwise Hawking/KMS continuation on every shell is far too steep and cannot
  be the physical full scalar spectrum.

Therefore the surviving route is genuinely narrow:

\[
\boxed{
\text{central modular gauge scalar}
\ +\
\text{exact coexact DtN logarithmic generator}
\ +\
\text{one-slot bridge/readout typing}.
}
\]

## What this does not solve

### Reionization history

`not derived`:
the theorem does not derive the function-valued late reionization history
`x_e(z)`. Paper 31's inheritance and admissibility theorems remain active.

### IO-native Boltzmann solver

`not derived`:
the theorem does not write the exact Stage-2 extended-state law.

What it **does** do is sharpen the architecture:

- the native solver must propagate typed one-particle fields on closed `S^3`
  carriers,
- it must implement the modular-DtN transfer operator in the source/readout
  sectors,
- and it cannot be reduced to post-solve parameter patches in flat-space CLASS
  variables.

So Problem 6 is narrowed, not closed.

## Final verdict

- `derived / scoped`: yes, the Paper 17 + Paper 23 + Paper 28 structures do
  assemble into a single field-level transfer theorem.
- `derived / scoped`: that theorem promotes the BFP coefficient to theorem
  grade on the active scalar-source sector.
- `derived / scoped`: it simultaneously derives the square-root field readout
  `X_obs = f_Gamma^(1/2) X_prim`.
- `derived / scoped`: it closes the definitive native scalar amplitude
  `A_s = 2.0072459972737347e-9`.
- `not derived`: it does not yet derive late reionization history or the full
  IO-native `S^3` Boltzmann solver.

So the right Paper 32 statement is:

\[
\boxed{
\text{the complete field-level boundary-to-bulk map exists and closes Items
1--4 in scoped theorem form,}
}
\]
\[
\boxed{
\text{while Items 5--6 remain a typed history-carrying solver problem.}
}
