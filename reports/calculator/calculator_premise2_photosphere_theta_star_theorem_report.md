# Calculator Premise-2 Operational Tau=1 Photosphere Estimator

## Executive result

- `verified / operational`: the clean local-history HyRec surface below is reproducible and numerically stable on the IO local background-state map.
- `not theorem-grade`: Paper 32 still leaves the exact IO Stage-2 dynamic-network renormalization open, so the clean HyRec surface is an operational estimator, not an exact IO closure.
- `verified / operational`: on the carried active legacy branch this estimator yields the photosphere and ruler-angle numbers listed below.
- `not theorem-grade`: the exported `theta_* = r_s(z_*) / D_M(z_*)` value is a hybrid local-history / observer-distance estimator and is not yet identified with the Paper 20 / 21 `theta*_bare` or `theta*_obs` objects.

## Estimator chain

1. Paper 31 already closes the local background-state map for primordial recombination: `H_loc(z)`, `T_R,loc(z)`, and `n_H,geom(z)`.
2. Paper 31 already closes the thermal distortion boundary state: `D_-(q; z_0) = 0`, `L_-(z_0) = 0` on the accepted Hawking/KMS class.
3. Under Premise 2, the local atomic/radiative equations inside the horizon may be explored with the standard exterior FULL multilevel hydrogen solver on the IO local background-state map, provided the result is treated as an operational surface rather than an exact IO theorem.
4. On that operational surface, the exported solver photosphere leaf `z_star` is the `tau = 1` photosphere of the clean HyRec history.
5. The corresponding angle-like estimator is the exported pair `z_star`, `rs_star` combined with the branch `D_M(z_star)`, giving `theta_* = r_s(z_*) / D_M(z_*)`.

## Exact boundary

- `derived`: the local background-state map and thermal boundary state remain theorem-grade.
- `verified / operational`: the clean HyRec toggle surface below is reproducible.
- `not theorem-grade`: no theorem currently upgrades this surface to the exact IO Stage-2 solver.
- `not theorem-grade`: no theorem currently identifies the resulting `theta_*` estimator with the Paper 20 / 21 observed acoustic-angle readout.

## Clean estimator surface

- `recombination = hyrec`
- `io_recombination_use_full_hyrec = yes`
- `io_recombination_local_hubble = yes`
- `io_recombination_use_tio_temperature = yes`
- `io_recombination_inverse_upward_rates = no`
- `io_recombination_line_escape_complement = no`
- `io_recombination_lya_diffusion_complement = no`
- chemistry bound to `omega_b,geom`

## Active Legacy Branch

- branch label: `active_paper10_legacy_projected_branch`
- `z_* = 1149.841939260518`
- `z_rec = 1148.2251273558281`
- `z_d = 1109.0843000875734`
- `r_s(z_*) = 136.41379151104525 Mpc`
- `r_s(z_rec) = 136.54022029489573 Mpc`
- `r_d = 139.68100176915075 Mpc`
- `D_M(z_*) = 12508.639206218242 Mpc`
- `100theta_* = 1.0905566086136074`
- `100theta_s = 1.0915863374047807`

## Accepted Geometric Branch

- branch label: `accepted_paper10_geometric_branch`
- `z_* = 1123.440245003334`
- `z_rec = 1124.0448338535157`
- `z_d = 1085.9068780634586`
- `r_s(z_*) = 166.6801689263022 Mpc`
- `r_s(z_rec) = 166.61455889023412 Mpc`
- `r_d = 170.86150501739897 Mpc`
- `D_M(z_*) = 14084.262234264517 Mpc`
- `100theta_* = 1.1834497693517745`
- `100theta_s = 1.182982063274966`

## Code authorities

- local background-state map: `/opt/cosmology-lab/results/paper31/paper31_stage2_local_background_state_map_theorem.md`
- thermal boundary state: `/opt/cosmology-lab/results/paper31/paper31_stage2_thermal_boundary_state_theorem.md`
- solver specification: `/opt/cosmology-lab/results/paper32/paper32_s3_native_solver_specification_theorem.md`
- exact `z_star` definition in solver code: `/opt/cosmology-lab/src/class_public/include/thermodynamics.h` and `/opt/cosmology-lab/src/class_public/source/thermodynamics.c`

