# Calculator Late-Packet Coefficient-Fixing Theorem

Status line
-----------

- `derived / scoped`: the Ly-line coefficients are fixed exactly by the boundary transport identities, not by fitting.
- `derived / scoped plus verified / residual-bounded`: on the live late packet, the effect-C virtual coefficient is fixed to the transport endpoint up to explicit audited residual bounds.
- `verified / scoped`: the corresponding late-packet reduced law has a definite carrier output.

Theorem 37.OU9 (late-packet coefficient-fixing theorem)
--------------------------------------------------------

Exact boundary identities
-------------------------

HyRec imports the incoming line-center state from the previous outgoing history and exports the outgoing line state as

- `Dfminus_Ly_hist[0] = xr[1] / (3 x1s)`
- `Dfminus_Ly_hist[1] = xr[0] / x1s * exp(-E32 / TR)`

Therefore exact line inheritance on the packet forces the unique boundary-real-state candidate

- `xr[1] = 3 x1s Dfplus_Ly[0]`
- `xr[0] = x1s exp(E32 / TR) Dfplus_Ly[1]`

These coefficients are exact inverses of the line update formulas, so they are boundary-fixed rather than fit.

Virtual fixed-point identity
----------------------------

For the virtual packet candidate `xv_cand / x1s = Dfplus`, the exact local residual satisfies

    `Tvr xr_cand + Tvv x_vcand - sv = x1s Tvv[0] (1 - Pi_b) (Dfplus - Dfeq)`.

So the transport endpoint `Dfminus = Dfplus` is selected exactly when the local fixed-point condition `Dfeq = Dfplus` holds.

Late-packet witnesses
--------------------

- live packet: future Ly-alpha crossing below `z = 1400`, evaluated on `z <= 1400`
- strongest weighted state gap: `2.549329351461086e-15`
- strongest weighted update gap: `2.046708005456269e-14`
- strongest candidate weighted virtual residual: `2.438469806591446e-14`
- strongest candidate real residual channel `0`: `5.816661042639635e-12`
- strongest candidate real residual channel `1`: `4.912207130189217e-12`
- strongest local-vs-input line-0 gap: `9.135206293700707e-17`
- packet support fraction of full witness: `theta = 9.959084311714629e-01`, `ell = 9.991738332536461e-01`

Global onset marker
-------------------

- first global strengthening failure for the `z_cross < 1400` virtual packet appears just above the safe window at `z = 1400.132456749255653` with weighted residual `2.339460028161709e-13`
- strongest global real residual channel `0` occurs at `z = 1437.620556110531652` with residual `6.237331419985888e-12`
- strongest global real residual channel `1` occurs at `z = 1433.961051911046752` with residual `5.190694373767175e-12`

Packet-scoped carrier output
----------------------------

- `100theta_star = 1.048849865324736`
- `ell_peak = 220.468603457971`
- `z_star = 1218.242926026018495`
- `z_rec = 1222.249162933484740`
- phase-equivalent strict-bare leaf: `z_sel = 1092.023344710469246`

Boundary
--------

This theorem fixes the late-packet coefficients much more sharply than before, but only on the packet-scoped law.
It does not yet prove that the same endpoint law is exact on the remaining early support above the late packet, and it does not by itself promote the packet-scoped number to the full-branch physical `theta_*`.
