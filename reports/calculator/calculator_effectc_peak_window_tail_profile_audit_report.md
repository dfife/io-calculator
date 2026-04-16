# Calculator Effect-C Peak-Window Tail Profile Audit

Status line
-----------

- `verified / scoped`: on the first TT peak window, the residual `z > 1500` tail deforms the promoted packet1500 parent profile only at the few-ppm relative level after the best vertical rescale is removed.
- `verified / scoped`: the remaining first-peak motion is a tiny horizontal parent-profile shift, not a new large branch deformation.

Setup
-----

- compare the full effect-C plus line endpoint to the support-certified cumulative packet `z_cross < 1500`
- full fitting window: `ell in [150, 350]`
- local peak window: `ell in [190, 250]`

Best Vertical Match
-------------------

- optimal scale `alpha = 0.999989138924388`
- max absolute residual on full window: `6.819997142247303e-02`
- max absolute residual on peak window: `3.640057577376865e-02`
- RMS relative residual on peak window: `2.950052007950388e-06`

Peak Data
---------

- full endpoint: `ell_peak = 220.475583735759`, `peak_tt = 6090.683067225164`
- packet1500: `ell_peak = 220.475144735071`, `peak_tt = 6090.761397583940`
- residual peak shift: `Delta_ell = +4.390006880612418e-04`
- residual height shift: `Delta_peak_tt = -7.833035877592920e-02`
- PK3 shift estimate from the residual parent profile: `+4.389836987985153e-04`

Interpretation
--------------

After removing the best pure-amplitude rescale, the full endpoint differs from packet1500 in the first-peak window only by a tiny residual parent-profile deformation.
That deformation is strong enough to account for the tiny observed `Delta_ell`, but it is not a second large support branch.
