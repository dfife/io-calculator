# Paper 28 - Closed `S^3` Power-Spectrum Definition Audit

## Scope

This audit answers one question:

What is the correct observer-side definition of the scalar primordial power
spectrum on a closed `K=+1` `S^3` spatial slice, without importing the flat
`k^3/(2 pi^2)` continuum formula as a primitive?

## Derived `S^3` definition

Let `X` be the scalar observable measured by the interior observer, expanded in
orthonormal scalar hyperspherical harmonics on `S^3`:

`X = sum_(n l m) X_(n l m) Q_(n l m)`.

For statistical isotropy on `S^3`,

`<X_(n l m) X_(n' l' m')^*> = P_X(n) delta_(n n') delta_(l l') delta_(m m')`.

This `P_X(n)` is the exact shell covariance on `S^3`.  The equal-point
variance decomposes shell-by-shell as

`<X^2> = sum_n [D_n / Vol(S^3)] P_X(n)`,

with

- scalar shell degeneracy `D_n = (n+1)^2`
- `Vol(S^3_R) = 2 pi^2 R^3`

Therefore the exact shell contribution to the variance is

`Var_n(X) = ((n+1)^2 / (2 pi^2 R^3)) P_X(n)`.

That is the first invariant observer-side object on closed `S^3`.

## Dimensionless shell power

If one wants a dimensionless analogue of the flat quantity “power per
logarithmic interval”, one must choose the shell label whose logarithmic
interval is being held fixed.  There are three natural choices in the present
stack:

1. `q_n = (n+1)/R`, the standard closed-universe discrete wavenumber.
2. `k_scalar(n) = sqrt(n(n+2))/R`, from the scalar Laplacian eigenvalue.
3. `k_MS(n) = sqrt((n-1)(n+3))/R`, from the `K=+1` scalar perturbation shell.

The exact dimensionless shell prefactors are then:

- `Delta_q^2(n) = ((n+1)^3 / (2 pi^2 R^3)) P_X(n)`
- `Delta_scalar^2(n) = (n (n+1) (n+2) / (2 pi^2 R^3)) P_X(n)`
- `Delta_MS^2(n) = ((n-1) (n+1) (n+3) / (2 pi^2 R^3)) P_X(n)`

These are all exact on closed `S^3`; they differ only by curvature-order
`O(n^-2)` factors at high shell.

## Convention boundary

There is no unique convention-independent analogue of the flat
`k^3/(2 pi^2)` formula until one decides which shell variable is being held
fixed.

This is not an IO oddity; it is already standard in non-flat Boltzmann
practice.  The local `CLASS` harmonic module comments note that in non-flat
space one can either:

- integrate over `dk/k` and keep a flat-style primordial `calP(k)`, or
- rewrite the integral in terms of the closed-universe shell variable `q` and
  absorb the Jacobian into a redefined primordial spectrum.

So the physically invariant object is the two-point function / shell covariance
itself, or equivalently the shell contribution to the variance.  Different
dimensionless `Delta^2` conventions are related by exact curvature Jacobians.

## Sample prefactors

| n | D_n | Var shell prefactor | Delta_q prefactor | Delta_scalar prefactor | Delta_MS prefactor |
| --- | --- | --- | --- | --- | --- |
| 2 | 9 | 0.455945326391 | 1.36783597917 | 1.21585420371 | 0.759908877318 |
| 5 | 36 | 1.82378130556 | 10.9426878334 | 10.6387242824 | 9.72683362966 |
| 10 | 121 | 6.12993161036 | 67.429247714 | 66.8719812039 | 65.2001816738 |
| 50 | 2601 | 131.768199327 | 6720.17816567 | 6717.59447549 | 6709.84340494 |
| 100 | 10201 | 516.788697168 | 52195.6584139 | 52190.5416942 | 52175.1915348 |
| 1000 | 1002001 | 50761.9636654 | 50812725.6291 | 50812674.9178 | 50812522.7841 |

## Closed-space scale invariance

On compact `S^3`, the natural analogue of Harrison-Zel'dovich is:

`constant contribution per logarithmic shell of the observer-side S^3 field`.

That means `Delta^2(n)` is approximately constant, not `P_X(n)` itself.

So the corresponding exact shell laws are:

- `Delta_q^2 = const`  ->  `P_X(n) propto 1 / (n+1)^3`
- `Delta_scalar^2 = const`  ->  `P_X(n) propto 1 / [n (n+1) (n+2)]`
- `Delta_MS^2 = const`  ->  `P_X(n) propto 1 / [(n-1) (n+1) (n+3)]`

Sample values for the exact scale-invariant shell laws:

| n | P_si,q | P_si,scalar | P_si,MS |
| --- | --- | --- | --- |
| 2 | 0.731081807488 | 0.822467033424 | 1.31594725348 |
| 5 | 0.091385225936 | 0.0939962323913 | 0.102808379178 |
| 10 | 0.0148303597312 | 0.0149539460623 | 0.0153373805767 |
| 50 | 0.000148805578565 | 0.000148862811479 | 0.000149034774681 |
| 100 | 1.91586815913e-05 | 1.91605598934e-05 | 1.91661970102e-05 |
| 1000 | 1.96801094139e-08 | 1.96801290548e-08 | 1.96801879775e-08 |

Asymptotically all three are `~ n^-3`.

If one wants a small tilted power-law fit in the usual observational sense,
the exact closed-space analogue is:

- `Delta_q^2(n) = A_s (q_n / q_*)^(n_s - 1)`
- `Delta_scalar^2(n) = A_s (k_scalar(n) / k_*)^(n_s - 1)`
- `Delta_MS^2(n) = A_s (k_MS(n) / k_*)^(n_s - 1)`

so, for the actual shell covariance,

- `P_X(n) = [2 pi^2 R^3 / (n+1)^3] A_s (q_n / q_*)^(n_s - 1)`
- `P_X(n) = [2 pi^2 R^3 / (n (n+1) (n+2))] A_s (k_scalar / k_*)^(n_s - 1)`
- `P_X(n) = [2 pi^2 R^3 / ((n-1) (n+1) (n+3))] A_s (k_MS / k_*)^(n_s - 1)`

For `n_s = 1`, these reduce exactly to the closed-space scale-invariant shell
laws above.

## Literature match

Two standard closed-universe references line up with this result.

1. Kiefer and Vardanyan (2022) define the closed-universe power spectrum by

`<v_n v_n'^*> = [2 pi^2 / (n (n^2 - K))] P_v delta...`

so

`P_v = [n (n^2 - K) / (2 pi^2)] <|v_n|^2>`.

For `K=1`, if their index is written as `q = n + 1`, this becomes exactly

`q (q^2 - 1) / (2 pi^2 R^3) = n (n+1) (n+2) / (2 pi^2 R^3)`,

which is the closed-`S^3` scalar-shell prefactor above.

2. Ratra (2017) states that the closed-model generalization of the flat
scale-invariant spectrum carries the characteristic denominator

`A (A+1) (A+2)`,

which is the same exact `S^3` `n^3` shell-counting structure written in the
usual closed-universe index.

So the flat `k^3` law is not primitive on `S^3`; the exact closed-space
replacement is a discrete `n (n+1) (n+2)` or `q (q^2 - 1)` shell factor.

## IO-specific answer

The `S^2` origin of the perturbations does **not** change the observer-side
definition of the power spectrum.

What it changes is the source-side shell covariance `P_X(n)` before it is
inserted into the closed-`S^3` observable.

So the correct observer-side IO question is:

What shell law for the lifted/bridged bulk scalar covariance `P_X(n)` is
generated by the `S^2 -> S^3` source chain?

The observable itself is the standard closed-`S^3` shell power above.

## Claim boundary

- `derived`: the first invariant closed-`S^3` observable is the shell
  contribution to the variance, `((n+1)^2 / (2 pi^2 R^3)) P_X(n)`.
- `derived`: a dimensionless shell spectrum on `S^3` is not uniquely
  primitive until one specifies the shell variable (`q_n`, `k_scalar`, or
  `k_MS`).
- `derived`: all natural closed-`S^3` definitions agree asymptotically that
  scale invariance means `P_X(n) ~ n^-3`.
- `derived`: the `S^2` boundary origin does not alter the observer-side
  definition; it only alters the source-side shell covariance.
- `derived boundary`: Paper 23's jump from white `S^2` angular covariance to
  bulk `n_s = 1` is not theorem-safe without the full `S^2 -> S^3` source
  chain.
- `derived boundary`: the current IO source-side factors still supply only
  `~ n^-2`, so one extra `n^-1` shell law remains missing if the framework is
  to recover approximate closed-space scale invariance.

## Primary sources

- Kiefer and Vardanyan, *Power spectrum for perturbations in an inflationary
  model for a closed universe* (2022): https://arxiv.org/abs/2111.07835
- Ratra, *Inflation in a closed universe* (2017):
  https://link.aps.org/accepted/10.1103/PhysRevD.96.103534
