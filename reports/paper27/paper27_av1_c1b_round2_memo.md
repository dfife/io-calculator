Paper 27
AV1 and C1b Round 2 Memo
========================

Executive result
----------------

Two results survive this round.

1. `derived / scoped theorem`:
   `AV1` can be promoted in reduced observer-side form.
   The correct theorem is not about recombination chemistry and not about the
   entire CMB perturbation source. It is:

       Thomson-gated scalar CMB readouts inherit the acoustic baryon slot.

   Equivalently, the visibility/readout operator belongs to the reduced optical
   scalar-acoustic class and therefore uses

       omega_b,vis = omega_b,eff.

2. `not derived`, but with a sharper conditional near-hit:
   the new `A_tan` isotropy route does not close `C1b` from the present stack,
   but it isolates the exact missing theorem. If one could prove that the
   physical centered tangential connection fluctuations are the isotropic
   quasi-free/KMS fluctuations on the explicit tangential carrier

       E_tan = span{I,J},

   then the Paper 26 Rosetta ratio

       <|delta K|^2> / <|delta A|^2> = gamma^2/(1+gamma^2)

   would follow immediately.


==================================================
I. AV1
==================================================

Question
--------

Does the existing stack force the visibility/readout sector into the acoustic
baryon class once one stays on the observer-side scalar readout chain and
excludes recombination chemistry?


I.1 The right scope
-------------------

The theorem target is not:

    "all recombination microphysics is acoustic class"

and not:

    "the full tightly coupled CMB-era baryon source is now closed."

The actual target is narrower and exactly matches Paper 26 section 3.5:

    the observer-side Thomson-gated scalar readout inherits its baryon slot
    from the acoustic readout class.

So the theorem lives on the reduced optical/readout side.
It does not assign the local Saha/Peebles/HyRec atom-counting map.


I.2 Existing derived inputs
---------------------------

1. Paper 26 Lemma 26.TK1:
   the same local Thomson opacity kernel

       kappa' = a n_e sigma_T

   enters both:

   - the visibility construction
         g = kappa' exp(-kappa),
   - and the photon-baryon momentum-transfer / drag system.

2. Paper 20 AB5 and Paper 21 AC1/A5:
   the local Thomson / baryon-photon integral is gauge-neutral on the reduced
   stack.
   The surviving gauge-sensitive correction does not enter through a second
   local plasma slot.

3. Paper 21 Theorem 21.J:
   observer-side optical readouts reduce through the reduced RT/BY optical
   filter and see only the central optical sector.

4. Paper 21 A4/A5:
   inside the reduced scalar/longitudinal acoustic chain, gauge-neutral
   direction collection and scalar optical reduction preserve the one-slot
   primitive stage and do not create a second A-sensitive slot.

5. Paper 21 Theorem 21.L:
   local bulk thermodynamic observables with no primitive optical leg are a
   different class. This excludes the visibility/readout operator from the raw
   inventory / BBN class.

6. Paper 18 / 19:
   once the reduced acoustic observer class is fixed, the framework-native
   acoustic baryon branch is

       omega_b,eff.


I.3 Minimal reduced object
--------------------------

Use the reduced visibility readout algebra already isolated in the Paper 26
promotion audit:

    M_vis^red
      := A_vis^gn bar-tensor M_ac
       = A_vis^gn bar-tensor L^infty(X,m) bar-tensor Z_g,

where:

- `A_vis^gn` is the gauge-neutral optical / line-of-sight visibility algebra,
- `L^infty(X,m)` is the scalar history cell,
- `Z_g` is the unique surviving reduced gauge scalar.

This is the correct object for the visibility/readout question.


I.4 New lemma: gauge-neutral Thomson gating is type-preserving
--------------------------------------------------------------

Lemma 27.AV1.1 (gauge-neutral visibility gating lemma)
------------------------------------------------------

Let `O_ac` be a reduced scalar acoustic observable in `M_ac` carrying the
unique surviving acoustic slot on `Z_g`.
Let `m` be any gauge-neutral scalar multiplier in

    A_vis^gn bar-tensor L^infty(X,m)

that commutes with `Z_g`.
Then

    m O_ac,   O_ac m

belong to the same reduced optical scalar-acoustic class and carry the same
unique baryon slot as `O_ac`.

Status:

    derived

Proof
-----

`m` acts only on the gauge-neutral optical/history factors and is trivial on
the reduced gauge factor `Z_g`.
Therefore multiplication by `m` cannot introduce a new A-sensitive leg and
cannot retag the existing one.
It only weights the already-certified scalar readout within the gauge-neutral
optical/history algebra.
So the active baryon slot is unchanged.

QED.


I.5 Visibility readout is exactly such a gauge-neutral Thomson gate
-------------------------------------------------------------------

Lemma 27.AV1.2 (visibility gate lemma)
--------------------------------------

The visibility factors

    kappa',
    kappa = integral kappa',
    exp(-kappa),
    g = kappa' exp(-kappa)

belong to the gauge-neutral optical/history side of `M_vis^red` and do not
create an independent gauge slot.

Status:

    derived / scoped theorem

Proof
-----

By Lemma 26.TK1, `kappa'` is the shared local Thomson interaction kernel.
By Paper 20 AB5 and Paper 21 A5, this local Thomson kernel is gauge-neutral on
the reduced stack.
Integration in redshift/time and scalar functional calculus

    kappa' -> kappa -> exp(-kappa) -> g

take place entirely inside the gauge-neutral optical/history algebra.
By Theorem 21.J and Paper 21 A4/A5, those gauge-neutral scalar operations do
not create a second A-sensitive slot.

QED.


I.6 The theorem
---------------

Theorem 27.AV1 (Thomson visibility class theorem)
-------------------------------------------------

Within the reduced observer-side scalar CMB readout sector, every
Thomson-gated scalar readout belongs to the reduced optical scalar-acoustic
class

    M_vis^red = A_vis^gn bar-tensor M_ac.

Therefore the visibility/readout baryon slot is the acoustic branch

    omega_b,vis = omega_b,eff.

Status:

    derived / scoped theorem

Proof
-----

1. By Theorem 21.L, the visibility/readout operator is excluded from the
   primitive local inventory / BBN class because it has a primitive optical
   leg.

2. By Lemma 26.TK1, the visibility gate and the acoustic momentum-transfer
   sector share the same Thomson kernel `kappa'`.

3. By Paper 20 AB5 and Paper 21 A5, the local Thomson kernel is gauge-neutral,
   so it does not furnish a second independent A-sensitive plasma slot.

4. By Paper 21 A4/A5, the reduced scalar acoustic chain has only one surviving
   A-sensitive slot.

5. By Lemma 27.AV1.2, the visibility factors

       kappa', kappa, exp(-kappa), g

   are gauge-neutral optical/history multipliers on that already-certified
   scalar acoustic chain.

6. By Lemma 27.AV1.1, such gauge-neutral Thomson gating is type-preserving and
   cannot change the active baryon slot.

7. Therefore the visibility/readout operator belongs to

       A_vis^gn bar-tensor M_ac

   and inherits the baryon slot of `M_ac`.

8. By the Paper 18 / 19 acoustic branch assignment, that slot is

       omega_b,eff.

So

    omega_b,vis = omega_b,eff.

QED.


I.7 Exact boundary
------------------

This theorem does close `AV1`, but only in the exact reduced scope above.

It does **not** prove:

- the local recombination chemistry map uses `omega_b,eff`,
- the full Peebles/HyRec microphysical source map is closed,
- the tightly coupled gravitational baryon source is closed,
- the entire CMB-era baryon sector is now one theorem.

What it does prove is the precise Paper 26 readout claim:

    the observer-side visibility/readout slot is acoustic class.


==================================================
II. C1b
==================================================

Question
--------

Does the explicit tangential identity

    A_tan = (-gamma I + J) / r_s,
    A_tan^dagger A_tan = (1+gamma^2) / r_s^2 * I_2

force the fluctuation variances of the `K` and `Gamma` pieces to split in the
ratio `gamma^2 : 1` because the A-vacuum is defined from `A` rather than from
`K` and `Gamma` separately?


II.1 Strong conditional near-hit
--------------------------------

Define the normalized tangential carrier

    E_tan = span{e_K, e_Gamma},
    e_K     := -I / r_s,
    e_Gamma :=  J / r_s.

Write the centered tangential fluctuation as

    delta A_tan = gamma xi_K e_K + xi_Gamma e_Gamma.

Lemma 27.C1b.1 (isotropic tangential covariance implies Rosetta ratio)
----------------------------------------------------------------------

Assume the coefficient vector

    xi = (xi_K, xi_Gamma)

has isotropic centered covariance

    <xi_i xi_j^*> = sigma^2 delta_ij

on `E_tan`.
Then

    <delta Gamma · delta K> = 0

and

    <|delta K|^2> / <|delta A|^2> = gamma^2 / (1+gamma^2).

Status:

    conditional

Proof
-----

Under the isotropic covariance,

    <|xi_K|^2> = <|xi_Gamma|^2> = sigma^2,
    <xi_K xi_Gamma^*> = 0.

So the orthogonal `K/Gamma` decomposition gives

    <|delta A|^2>
      = gamma^2 <|xi_K|^2> + <|xi_Gamma|^2>
      = (1+gamma^2) sigma^2,

while the extrinsic contribution is

    <|delta K|^2> = gamma^2 sigma^2.

Therefore

    <|delta K|^2> / <|delta A|^2>
      = gamma^2 / (1+gamma^2).

QED.

So the user's route is mathematically real.
If the physical fluctuation covariance is exactly the isotropic tangential one,
the Paper 26 ratio follows in one line.


II.2 Where derivation breaks
----------------------------

The present theorem stack does **not** derive the hypothesis of
Lemma 27.C1b.1.

The exact break is:

    "A-vacuum is defined from A"
    does not yet imply
    "the physical centered fluctuation covariance is the isotropic quasi-free
     covariance on the explicit tangential carrier E_tan."

Three reasons block the jump.

1. Paper 17 lives on the reduced thermal-plus-gauge sector

       M_th bar-tensor Z_g,
       Z_g = W*(K_hat_g),
       K_hat_g = K_gauge I,

   not on an explicit tangential fluctuation CCR algebra for `delta A_tan`.
   The theorem-grade object there is the central reduced scalar `K_hat_g`, not
   a `2 x 2` tangential covariance operator.

2. The identity

       A_tan^dagger A_tan = (1+gamma^2) I_2 / r_s^2

   proves background isotropy of the tangential block, but it does **not**
   identify the centered fluctuation covariance.
   A scalar background quadratic form does not by itself fix the covariance
   width or even the relevant fluctuation algebra.

3. The existing Paper 26 spatial A-vacuum analysis already proved a closely
   related obstruction:
   symmetry and A-vacuum compatibility reduce the spatial bridge covariance to
   a one-parameter family, but do not fix its normalization.
   Many centered quasi-free states can share the same reduced A-vacuum marginal.


II.3 Exact surviving seam
-------------------------

The new route does not close `C1b`, but it sharpens the missing theorem
substantially.

The exact needed new theorem is now:

    TC1:
    the physical centered tangential Ashtekar-Barbero fluctuation covariance is
    the isotropic positive quasi-free/KMS covariance on E_tan determined by the
    tangential A-connection quadratic form A_tan^dagger A_tan.

If `TC1` were proved, then Lemma 27.C1b.1 would immediately close `C1b`.

So the new result is a real narrowing:

- old bottleneck:
  some unknown operator theorem must fix the Rosetta ratio
- new bottleneck:
  prove the physical fluctuation covariance is the isotropic tangential
  covariance on `span{I,J}`.


II.4 Honest boundary
--------------------

What is now established:

- `derived / conditional`: the `A_tan` route gives a clean short implication
  from isotropic tangential covariance to the Paper 26 ratio.
- `not derived`: the current Paper 17 / 25 / 26 stack does not yet provide that
  isotropic tangential covariance theorem.

Future overclaim boundary:

Do **not** say:

- "the A-vacuum is defined from A, therefore C1b now follows;"
- "A_tan^dagger A_tan proportional to I_2 already proves the fluctuation ratio;"
- "Paper 17's A-vacuum is already a theorem about centered tangential
  connection fluctuations."

The honest state is narrower:

- the tangential route is the cleanest conditional near-hit so far,
- but `C1b` itself remains open.


==================================================
III. Bottom line
==================================================

This round gives one true promotion and one sharpened bottleneck.

- `derived / scoped theorem`:
  `AV1` closes on the observer-side readout chain.
  The visibility/readout slot is acoustic class and uses `omega_b,eff`.

- `open`, but with a much better target:
  `C1b` still needs a new fluctuation-covariance theorem, and the right one is
  now visible. The clean candidate is an isotropic tangential covariance
  identification on `E_tan = span{I,J}`.
