# Paper 32: Hidden-Identification Repair Theorem

Date: 2026-04-05

## Question

Cosmo's second validation pass identified three hidden identifications inside
Theorem 32.A:

1. shell/spectral lift `\ell -> N`,
2. area-to-line descent `1/x^2 -> 1/x`,
3. fixed-point normalization `Z(e^x)=Q`.

Do these identifications collapse, or does one of them remain a genuine premise?

## Executive result

The strongest honest answer is:

- `derived / scoped repair`:
  the old shorthand
  \[
  r_s \sigma_\ell = \ell+1 = N
  \]
  is not theorem-grade and should be replaced.
  The DtN weight lives on the boundary line variable
  \[
  s_\ell := r_s \sigma_\ell = \ell+1,
  \]
  and under the accepted even-shell boundary lift plus Paper 23 bridge grammar
  it pushes forward to an **affine odd-shell** law in `N`, not to the literal
  identity `N=\ell+1`.
- `derived / scoped repair`:
  the `1/x` factor is theorem-grade on the current Paper 32 object class.
  It is not imported from the old Paper 10 area fraction.
  It follows because the active object is a primitive one-slot line operator on
  the coexact `1`-form carrier, and Paper 23 zero-order bridge scalarization
  preserves the `alpha=1` rung.
- `derived / no-go`:
  SP-3 / Hawking-lock does **not** force the fixed-point normalization
  \[
  Z(e^x)=Q.
  \]
  State uniqueness on the quotient does not determine the normalization of the
  DtN multiplicative character.

So the final status is:

\[
\boxed{
\text{Hidden IDs 1 and 2 can be repaired.}
}
\]
\[
\boxed{
\text{Hidden ID 3 remains the one explicit premise.}
}
\]

That is the honest Paper 32 endpoint:

\[
\boxed{
\text{Items 1--4 survive as theorem-grade after repairs to (1) and (2),}
}
\]
\[
\boxed{
\text{conditional on one remaining stated premise: } Z(e^x)=Q
\text{ or an equivalent fixed-point normalization law.}
}
\]

## Claim discipline

- `derived`: forward consequence of stated assumptions and already-derived stack
- `verified`: numerically checked from explicit formulas
- `conditional`: depends on a class-membership or normalization statement not yet derived
- `reconstruction`: coherent organizing model, not yet derived
- `speculative`: idea worth exploring, not yet established

## 1. Hidden Identification 1: shell relabeling

### 1.1 What must be corrected

Paper 32 Corollary 32.A.1 used the compressed shorthand
\[
r_s \sigma_\ell = \ell+1 = N.
\]

That is too strong.

The correct data split into three stages:

1. `boundary DtN shell`
   \[
   s_\ell := r_s \sigma_\ell = \ell+1;
   \]
2. `accepted coexact boundary lift`
   \[
   n = 2\ell;
   \]
3. `Paper 23 bridge selection rule`
   \[
   N = n-1 \quad \text{or} \quad N = n+1.
   \]

Therefore the actual scalar-shell labels are
\[
N = 2\ell - 1
\qquad\text{or}\qquad
N = 2\ell + 1,
\]
not `N=\ell+1`.

### 1.2 What survives under the correction

The Paper 32 DtN exponent acts on the boundary spectral scale
\[
s_\ell = \ell+1,
\]
so the boundary dressing is
\[
W_\ell = \left(\frac{\ell+1}{\ell_p+1}\right)^{-\beta},
\qquad
\beta = \frac{K_{\rm gauge}}{x}.
\]

Under the plus branch
\[
N = 2\ell+1,
\qquad
\ell = \frac{N-1}{2},
\]
this becomes
\[
W_N^{(+)}
=
\left(
\frac{(N+1)/2}{(N_p+1)/2}
\right)^{-\beta}
=
\left(
\frac{N+1}{N_p+1}
\right)^{-\beta}.
\]

Under the minus branch
\[
N = 2\ell-1,
\qquad
\ell = \frac{N+1}{2},
\]
this becomes
\[
W_N^{(-)}
=
\left(
\frac{(N+3)/2}{(N_p+3)/2}
\right)^{-\beta}
=
\left(
\frac{N+3}{N_p+3}
\right)^{-\beta}.
\]

So the power law survives exactly, but in an **affine branch variable**:

- plus branch: `N+1`,
- minus branch: `N+3`.

The naive `N^{-beta}` form is only a large-shell shorthand.

## Theorem 32.L - Shell-Relabeling Pushforward Theorem

Status: `derived / scoped`

Assume the current Paper 23/Paper 28 coexact boundary-lift dictionary:

1. the DtN carrier is the coexact `S^2` boundary `1`-form shell labeled by
   `\ell`;
2. the accepted boundary-to-vector lift is the even-shell map
   \[
   n=2\ell;
   \]
3. the scalar bridge is the Paper 23 multiplicity-one adjacent-shell map
   \[
   N=n\pm1.
   \]

Then the boundary DtN power law
\[
G_{\rm bdy}^{(1)}(\ell) \propto (\ell+1)^{-\beta}
\]
pushes forward to the scalar shell law
\[
G_{\rm scal}^{(+)}(N)\propto \left(\frac{N+1}{2}\right)^{-\beta},
\qquad
G_{\rm scal}^{(-)}(N)\propto \left(\frac{N+3}{2}\right)^{-\beta}.
\]

Relative windows are therefore
\[
W_N^{(+)}=\left(\frac{N+1}{N_p+1}\right)^{-\beta},
\qquad
W_N^{(-)}=\left(\frac{N+3}{N_p+3}\right)^{-\beta}.
\]

### Proof

This is direct substitution of the branch relations into the boundary DtN shell
variable `s_\ell=\ell+1`.

The factor `2` cancels in relative windows, so the bridge relabeling does not
change the exponent.

QED.

## Corollary 32.L.1 - What the bridge coefficients do

Status: `derived / scoped`

The Paper 23 / Paper 28 shell-averaged normalized adjacent-branch coefficients
are shell-flat, so they do not create a new spectral exponent.

Therefore the exact scalar covariance on the two-branch channel has the form
\[
C_N
=
B_{N,-}\left(\frac{N+1}{2}\right)^{-\beta}

+ B_{N,+}\left(\frac{N+3}{2}\right)^{-\beta},
\]
with bridge coefficients carrying branch amplitude/adjacency information, not a
new power of shell number.

### Claim boundary

What is repaired is the **relabeling of the exponent**.

What is not claimed is a literal identity between the boundary shell number and
the scalar shell number.

So Corollary 32.A.1 should not say `\ell+1=N`.
It should say:

\[
\text{the DtN exponent lives on } s_\ell=\ell+1
\text{ and pushes forward through the bridge to affine odd-shell laws.}
\]

## 2. Hidden Identification 2: area-to-line descent

### 2.1 The object-class distinction

The old Paper 10 factor
\[
1/x^2
\]
belongs to the area/intensity legacy branch.

The active Paper 32 object is different.

Paper 28 already isolated the correct object:

\[
R_\gamma := O_\gamma O_0^{-1},
\]

the relative boundary effective kernel on the canonical coexact carrier.

Paper 28 proved:

- `R_gamma` is a one-slot positive line operator;
- it acts on the coexact `1`-form carrier;
- it is not a scalar self-intensity and not a two-slot object.

That is exactly the object class on which Paper 18 BDP acts.

### 2.2 What Paper 18 and Paper 23 now imply

Paper 18 proved:

- primitive `1`-form transfer belongs to `alpha=1`,
- line transport scales with one power of length,
- therefore the accessible divisor is `1/x`.

Paper 23 proved:

- the scalar bridge is zero-order and derivative-free,
- zero-order bridge scalarization preserves the `alpha=1` rung.

So there is no class-membership gap on the current one-slot source/readout
sector:

\[
\text{coexact one-slot line object}
\xrightarrow{\;B_N\;}
\text{still } \alpha=1.
\]

## Theorem 32.M - Line-Class Descent Theorem

Status: `derived / scoped`

Work on the Paper 32 one-slot source/readout sector.

Assume:

1. the active source object is the relative boundary kernel ratio
   \[
   R_\gamma = O_\gamma O_0^{-1}
   \]
   or its field-level positive square root;
2. the carrier is the canonical coexact `1`-form boundary carrier;
3. the scalar bridge is the Paper 23 zero-order one-slot bridge.

Then:

1. the active object belongs to the primitive line / `alpha=1` class;
2. the observer-accessible cell count on the multiplicative DtN line scale is
   \[
   n_{\rm acc}(s)=\frac{1}{x}\ln s;
   \]
3. the corresponding covariance dressing is
   \[
   R_\gamma(s)=Q^{n_{\rm acc}(s)}=s^{K_{\rm gauge}/x};
   \]
4. the field-level transfer is its positive square root
   \[
   T_{\rm field}(s)=s^{-K_{\rm gauge}/(2x)}.
   \]

### Proof

Step 1:
Paper 28 fixes `R_gamma` as a one-slot positive line operator.

Step 2:
Paper 18 BDP gives `1/x` for primitive `1`-form transfer.

Step 3:
Paper 23 Lemma 23.B proves the zero-order bridge preserves `alpha=1`.

Step 4:
Paper 31 post-bridge field no-go forces the field object to be the positive
square root of the quadratic complement, not a second full-intensity insertion.

Therefore the accessible count is line-like and the field operator carries
`1/(2x)` while its quadratic descendant carries `1/x`.

QED.

## Corollary 32.M.1 - Exact exclusion of `1/x^2`

Status: `derived / scoped`

The old area law `1/x^2` cannot be substituted into Theorem 32.A.

Reason:

- `1/x^2` belongs to the area / two-slot / legacy intensity branch;
- Theorem 32.A lives on the one-slot line / `alpha=1` branch.

So there is no hidden descent
\[
1/x^2 \to 1/x
\]
inside the same theorem.

There is instead an object-class replacement:

\[
\text{old area branch }(1/x^2)
\quad\longrightarrow\quad
\text{new line branch }(1/x).
\]

This repairs Hidden Identification 2.

## 3. Hidden Identification 3: fixed-point normalization

This is the hard gate, but it splits into two different statements.

### 3.1 What is already local and derived

If the physical object is the relative kernel ratio `R_gamma`, then the local
primitive cell ratio
\[
R_\gamma^{\rm cell}=Q=1+\gamma^2
\]
is already the derived collar-level statement.

### 3.2 What is still not derived

The remaining step is stronger:

> identify the multiplicative fixed-point character `Z(s)` on the accessible DtN
> line semigroup with that local cell ratio, so that
> \[
> Z(e^x)=Q.
> \]

That identification is not forced by SP-3.

State uniqueness and character normalization are different logical objects:

- SP-3 fixes the input state on the quotient,
- Hidden ID 3 fixes which multiplicative character acts on that state.

## Theorem 32.N - Hawking-Lock Normalization No-Go

Status: `derived / no-go`

Let `G_H` be the unique Hawking state covariance on the lowest-shell
bridge-readable quotient from SP-3.

For every real `eta`, define the positive transfer family
\[
T_\eta(s)=s^{-\eta/2}
=
\exp\!\left[-\frac{\eta}{2}\log s\right].
\]

On the same unique Hawking state, each `eta` produces a valid output covariance
\[
C_\eta(s)=T_\eta(s)\,G_H\,T_\eta(s)^\ast
=
s^{-\eta} G_H.
\]

In particular, on one accessible cell `s=e^x`,
\[
C_\eta(e^x)=e^{-\eta x} G_H.
\]

Distinct values of `eta` therefore give distinct output covariances on the same
unique Hawking input state.

So the uniqueness of `G_H` does **not** determine `eta`, and does not force
\[
Z(e^x)=Q.
\]

### Proof

The Hawking theorem fixes the state `G_H`.

But the map
\[
\eta \mapsto T_\eta
\]
is an independent one-parameter family of positive characters on the DtN line
semigroup. Nothing in SP-3 singles out one value of `eta`.

Therefore state uniqueness cannot fix character normalization.

QED.

## Corollary 32.N.1 - Exact remaining premise

Status: `derived / boundary`

The remaining explicit premise is:

\[
\boxed{
Z(e^x)=Q
\quad\text{or an equivalent statement identifying the physical fixed-point
character with the relative kernel one-cell ratio.}
}
\]

Without that premise, Theorem 32.A remains:

- `derived / repaired` in its relabeling and line-class structure,
- `conditional` in its coefficient normalization.

With that premise, Items 1-4 remain theorem-grade in the repaired scoped form.

## 4. Exact repaired version of Theorem 32.A

The repaired theorem package is:

1. `boundary spectral scale`
   \[
   s_\ell=\ell+1
   \]
   on the canonical coexact carrier.

2. `field transfer on the line class`
   \[
   T_{\rm field}(s)=s^{-K_{\rm gauge}/(2x)}
   \]
   once the fixed-point normalization is supplied.

3. `bridge pushforward`
   under `n=2\ell`, `N=n\pm1`, the exact branch windows are
   \[
   W_N^{(+)}=\left(\frac{N+1}{N_p+1}\right)^{-\beta},
   \qquad
   W_N^{(-)}=\left(\frac{N+3}{N_p+3}\right)^{-\beta}.
   \]

4. `claim boundary`
   raw `N^{-\beta}` is only asymptotic shorthand;
   the theorem-grade law is affine in the odd-shell branch variable.

## 5. Final grading

### Hidden Identification 1

- `derived / scoped repair`: yes

### Hidden Identification 2

- `derived / scoped repair`: yes

### Hidden Identification 3

- `not derived`: still one explicit premise

## Bottom line

The right honest statement for Paper 32 is:

\[
\boxed{
\text{Theorem 32.A survives after two repairs and one explicit surviving premise.}
}
\]

The two repairs are:

- correct bridge relabeling of the DtN exponent,
- correct `alpha=1` line-class descent.

The surviving premise is:

- fixed-point normalization
  \[
  Z(e^x)=Q.
  \]

SP-3 does not remove that last premise.
