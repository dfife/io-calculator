# Calculator Phase-Equivalent Selector Theorem

Status line
-----------

- `derived / conditional`: on Premise 2, the strict-bare running backbone `r_s^bulk(z) / D_M^bare(z)` is the unique selector-bearing representative of the primitive bare phase-ruler scalar on the homogeneous scalar/longitudinal scope.
- `derived / scoped`: the carried interval `[900, 1300]` is analytically monotone on the strict-bare branch.
- `derived / scoped`: the theorem-grade selector is the inverse-image map of that primitive scalar on the certified interval.
- `boundary`: this closes the selector map and its representative, not the upstream full exact Stage-2 phase/readout operator.

Theorem 36.S2 (strict-bare phase-ruler representation theorem)
---------------------------------------------------------------

Premises

1. Paper 20 G1: on the homogeneous observer-side acoustic-history scope, the bare sound horizon is the 1D history observable

       r_s^bulk(z) = integral_z^inf c_s,geom(z') / H_bare(z') dz'.

2. Paper 20 AB3 / AB4: the bare transverse angular sector is the pure gauge-neutral distance observable `D_M^bare(z)` on the strict-bare branch.
3. Paper 21 A2 / A5 / B6: peak positions inherit their nontrivial content only from the primitive phase-ruler stage; degree-2 intensity and uniform amplitude channels cannot move them.
4. Premise 2: standard scalar acoustic propagation holds on the local bulk background, so the primitive oscillatory transfer depends on the phase variable `k r_s^bulk(z)` and the sky projection depends on `k D_M^bare(z)`.

Statement

On the strict-bare homogeneous scalar/longitudinal phase sector, the primitive selector-bearing bare scalar at leaf `z` is uniquely

    theta_bare^prim(z) = r_s^bulk(z) / D_M^bare(z).

Proof

By Paper 20 G1, the bare numerator is the 1D longitudinal history ruler `r_s^bulk(z)`. By Paper 20 AB3 / AB4, the bare denominator is the pure transverse distance `D_M^bare(z)`. By Paper 21 A2 / B6, later intensity and amplitude stages are gauge-transparent for peak positions, so the selector-bearing content must live in the primitive phase lattice itself. Under Premise 2, that lattice depends on `k r_s^bulk(z)` before projection and on `k D_M^bare(z)` after projection to the sky. Eliminating the common wavenumber `k` leaves exactly one dimensionless bare phase-ruler scalar: `r_s^bulk(z) / D_M^bare(z)`. No second independent bare scalar survives once numerator and denominator sectors are fixed, so this representative is unique on the stated scope. QED.

Theorem 36.S3 (strict-bare selector monotonicity theorem)
----------------------------------------------------------

Premises

1. On the strict-bare branch,

       D_M^bare(z) = (c / (H0 sqrt(-Omega_k))) sin(psi(z)),
       psi(z) = sqrt(-Omega_k) integral_0^z dz' / E(z').

2. The bare sound horizon obeys

       d r_s^bulk / dz = -c_s / H_bare < 0.

3. The local loading is `R(z) = const / (1+z)`, so `c_s(z)` is increasing with `z`.

Statement

On the carried interval `I = [900, 1300]`, the strict-bare backbone `theta_bare^bulk(z)` is strictly decreasing.

Proof

Differentiate `D_M^bare(z)` using `d psi / dz = H0 sqrt(-Omega_k) / H_bare(z)` to obtain

    d D_M^bare / dz = c cos(psi) / H_bare.

Therefore

    d theta_bare^bulk / dz
      = -[c_s D_M + c r_s cos(psi)] / [H_bare D_M^2].

It is enough to prove

    M(z) := (c_s/c) (D_M/r_s) + cos(psi) > 0

on `I`.

Now `psi(z)` is increasing, and the endpoint evaluations give
    psi(900) = 1.8265124950753593,
    psi(1300) = 1.83365664322909,

so `pi/2 < psi(z) < pi` throughout `I`. Hence `D_M(z)` decreases and `cos(psi(z)) >= cos(psi(1300))` on `I`. Also `r_s(z)` decreases, so `r_s(z) <= r_s(900)`, and `c_s(z)` increases, so `c_s(z) >= c_s(900)`. Therefore

    M(z)
      >= (c_s(900)/c) * D_M(1300) / r_s(900) + cos(psi(1300))
      = 29.79550105950255
      > 0.

So `d theta_bare^bulk / dz < 0` everywhere on `I`. QED.

Theorem 36.S1 (phase-equivalent inverse-image selector theorem)
----------------------------------------------------------------

Premises

1. Papers 20-21 fix the physical acoustic-angle scalar to the primitive phase-ruler readout on the reduced scalar/longitudinal acoustic sector, with later intensity and peak-extraction stages gauge-transparent.
2. Calculator.S2 identifies the strict-bare bulk backbone as the exact primitive selector-bearing bare scalar.

3. Calculator.S3 proves that on `I = [900, 1300]`, `theta_bare^bulk` is continuous and strictly monotone.

Statement

Let `theta_bare^prim` be the exact primitive bare acoustic-angle scalar on the reduced scalar/longitudinal phase-ruler sector. Then on every certified monotone interval `I`, the redshift selector is uniquely

    z_sel := (theta_bare^bulk|_I)^(-1)(theta_bare^prim).

Equivalently, if the observer-side acoustic scalar is used instead,

    z_sel := (theta_bare^bulk|_I)^(-1)(theta_obs / J_theta),

with the exact Paper 20 / 21 observer Jacobian

    J_theta = x^(-1/2) sqrt(1 + gamma^2).

Proof

By Theorem 36.S2, `theta_bare^bulk(z)` is the exact primitive selector-bearing bare scalar on the stated scope. By Theorem 36.S3, this scalar is strictly monotone on `I = [900, 1300]`, hence bijective onto its image and therefore invertible. Applying that inverse to the exact primitive bare scalar produces one and only one redshift leaf. The observer-side form follows immediately from `theta_obs = J_theta theta_bare^prim`. QED.

Analytical carried-domain certificate
------------------------------------

Verified endpoint values used in the monotonicity proof:
- `z_min = 900.0`
- `z_max = 1300.0`
- `theta_min_deg = 0.6352760906128453`
- `theta_max_deg = 0.8240479826304431`
- `psi(900) = 1.8265124950753593`
- `psi(1300) = 1.83365664322909`
- `D_M(900) = 13795.722162384218 Mpc`
- `D_M(1300) = 13769.60316695438 Mpc`
- `r_s(900) = 198.41491142025706 Mpc`
- `r_s(1300) = 152.67267054453322 Mpc`
- `lower_bound(D_M / r_s) = 69.39802592709812`
- `lower_bound(c_s / c) = 0.43308645073947144`
- `lower_bound(cos psi) = -0.25984367759019306`
- `lower_bound(monotonicity margin) = 29.79550105950255`

Round-trip witnesses
--------------------

- `z = 950.0`
  - `theta_bare = 0.7942024070424165 deg`
  - `theta_obs = 0.6623220633637245 deg`
  - `z_from_bare = 950.0`
  - `z_from_obs = 950.0`
- `z = 1100.0`
  - `theta_bare = 0.716893402127029 deg`
  - `theta_obs = 0.5978505140481843 deg`
  - `z_from_bare = 1100.0`
  - `z_from_obs = 1100.0`
- `z = 1250.0`
  - `theta_bare = 0.6538184070320143 deg`
  - `theta_obs = 0.5452493628459875 deg`
  - `z_from_bare = 1250.0`
  - `z_from_obs = 1250.0`

Boundary
--------

These theorems do **not** claim that a photosphere threshold, a visibility percentile, `tau = 1`, `Gamma_T/H = 1`, or any other raw history threshold is the selector. They close the selector only as the inverse image of the exact primitive phase-ruler scalar on the strict-bare homogeneous scalar/longitudinal scope. Computing that scalar numerically on the full exact Stage-2 source/readout operator remains a separate upstream task.
