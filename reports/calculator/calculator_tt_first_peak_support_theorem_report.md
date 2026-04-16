# Scoped TT First-peak Support Theorem

Status: `verified / scoped`

## Claim

On the repaired active-branch closed-`S^3` TT carrier with:

- `exact_history_samples = 120`
- `prehistory_samples = 40`
- `n_max = 501`
- `shell_step = 1`
- `project_metric_constraint = False`
- `constraint_metric_source_only = True`
- `constraint_consistent_seed = True`
- `metric_baryon_momentum_slot = omega_b,eff`
- `source_shell_support = odd_plus_branch`
- `source_shell_weight_interpretation = covariance`

the executable TT spectrum lands in the physical first-peak family:

- `ell_peak = 224`
- `C_220 / C_peak = 0.9938104102565932`
- `C_2 / C_30 = 1148.794609154744`

This is a scoped verified first-peak-support result, not a theorem-grade full
high-`ell` TT closure.

## Supporting checks

Neighboring lower ceiling on the same repaired branch:

- `n_max = 453`
- same history carrier, same repaired branch controls
- result:
  - `ell_peak = 222`
  - `C_220 / C_peak = 0.976859196443279`
  - `C_2 / C_30 = 1330.8220145093353`

So the first-peak family is stable below the canonical ceiling.

## Remaining open boundary

The higher shell ceiling is still open on the current stack.

Tested full odd-support ladders on the same repaired branch:

- `n_max = 601`, `exact = 120`, `pre = 40`
  - `ell_peak = 277`
  - `C_220 / C_peak = 0.8428363982625747`
  - `C_2 / C_30 = 877.7607365906343`
- `n_max = 601`, `exact = 120`, `pre = 60`
  - `ell_peak = 260`
  - `C_220 / C_peak = 0.8958153212305773`
  - `C_2 / C_30 = 1298.3534990121832`
- `n_max = 601`, `exact = 120`, `pre = 120`
  - `ell_peak = 256`
  - `C_220 / C_peak = 0.9161860655243944`
  - `C_2 / C_30 = 1668.934235236747`

So the live ceiling drift is reduced by the better finite-history carrier, but
it is not closed. The remaining frontier is the source-to-seed / high-shell
phase law above the canonical first-peak support ceiling.

## Killed route

The shell-local prehistory carrier idea was tested and rejected as a live
runtime convention. Localizing the early-time carrier shell by shell moved the
peak materially:

- `n_max = 453` -> `ell_peak = 180`
- `n_max = 501` -> `ell_peak = 201`

That means shell-local truncation changes the cross-shell phase carrier rather
than acting as an innocent numerical cleanup. The runtime therefore keeps one
common early-time carrier for the whole run until a new theorem-grade
phase-coherent alternative exists.

## Reproducibility

Canonical verified run:

```bash
PYTHONPATH=/opt/cosmology-lab/calculator/src python - <<'PY'
from aio_calculator.scalar_tt_driver import (
    ScopedTTDriverConfig,
    run_scoped_tt_driver,
)

cfg = ScopedTTDriverConfig(
    exact_history_samples=120,
    prehistory_samples=40,
    n_max=501,
    ell_max=350,
    shell_step=1,
    shell_parallel_workers=12,
    project_metric_constraint=False,
    constraint_metric_source_only=True,
    constraint_consistent_seed=True,
    metric_baryon_momentum_slot="eff",
    source_shell_support="odd_plus_branch",
    source_shell_weight_interpretation="covariance",
)
res = run_scoped_tt_driver(cfg)
print(res.validation.ell_peak)
print(res.validation.c_220_over_peak)
print(res.validation.plateau_2_to_30_ratio)
PY
```

Expected output:

- `224`
- `0.9938104102565932`
- `1148.794609154744`
