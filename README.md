# IO Calculator Alpha

The IO Calculator is an alpha public, theorem-bearing cosmological calculator for the Interior Observer Framework. It publishes curved closed-space background quantities, nucleosynthesis outputs, recombination primitives, acoustic-scale observables, a theorem dictionary with explicit claim boundaries, and a conditional/scoped/verified TT first-peak support carrier, all with zero fitted cosmological parameters on the live branch.

*If the theory is correct, the math will just work.*

This draft is for release planning and review. It is not yet the committed public `README.md`.

Alpha release status:

- release line: `0.1.0a1`
- intended tag: `v0.1.0-alpha.1`
- public consumption is allowed under the project license
- scholarly use should cite the software and the relevant theorem reports

## What This Calculator Is

The calculator is the executable surface of the Interior Observer Framework’s active branch. Unlike a standard cosmology code that only returns numbers, it returns numbers together with their derivation chain, theorem authority, scope boundary, and claim status.

The current public-facing scope includes:

- exact closed-FRW late-time background on the active branch
- distance and BAO observables on curved, closed space
- active-branch `theta_*` on the carried selector leaf
- BBN outputs including the lithium result
- theorem-grade local recombination primitives on the geometric baryon slot
- a theorem dictionary / provenance graph for published outputs
- a conditional/scoped/verified TT first-peak support carrier

The calculator does **not** currently claim:

- theorem-grade closure of the full high-`ell` TT spectrum
- a CLASS-equivalent full CMB Boltzmann solver
- theorem-grade TE/EE closure
- a theorem-grade Planck acoustic extractor

## Citation Request

This alpha release is intended for public use, inspection, and independent reproduction.
If you use the calculator, its outputs, or its theorem reports in research, software, teaching material, or public analysis, cite the repository and the relevant theorem authority nodes.

The final public source release should ship:

- `CITATION.cff`
- an `Apache-2.0` software license
- theorem reports for the live published outputs

## Two Working Premises

Premise 1: we live inside a black hole, and the CMB is the event horizon, with Hawking radiation falling inward and being observed from the interior.

Premise 2: the physics inside our black hole are the same as the physics outside our black hole.

## What You Can Validate Quickly

Within about ten minutes of cloning and installing, a physics-literate Python user should be able to:

1. run the theorem-grade active-branch `theta_*` closure
2. run the canonical TT first-peak carrier
3. inspect the theorem dictionary / provenance graph
4. rerun the full local test suite

Canonical validated TT result on the current public scope:

- claim status: `Conditional/scoped/verified TT first-peak support on the repaired active-branch canonical carrier (n_max = 501), with inherited-FULL Stage-2 history and equal-rate typed Thomson specialization.`
- canonical first peak: `ell_peak = 224`
- open frontier: the `n_max >= 601` ceiling drift remains explicit and unresolved

## Installation

### Option A: install from source with `pip` (recommended)

```bash
git clone <REPO-URL>
cd <REPO-DIR>
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

This repository currently exposes the package as:

- package name: `aio-calculator`
- CLI entry point: `aio-calculator`

### Option B: run directly from the source tree

```bash
git clone <REPO-URL>
cd <REPO-DIR>
PYTHONPATH=src python -m aio_calculator --help
```

### Planned packaging note

If David chooses a PyPI release later, this section can add:

```bash
python -m pip install aio-calculator
```

That command is **not** promised yet and should not appear in the final public README until the package actually exists on PyPI.

## First Validated Outputs

### Theorem-grade `theta_*`

```bash
aio-calculator theta-star-theorem --json
```

Expected output includes the active-branch theorem result:

- `100theta_* = 1.048683904878751`

and its full provenance chain.

### Canonical TT first-peak support

```bash
aio-calculator tt-spectrum --json --workers 12
```

Expected output includes:

- the approved scoped TT claim status
- the canonical runtime configuration
- `ell_peak = 224`
- `C_220 / C_peak ≈ 0.9938`
- the explicit `n_max >= 601` open frontier

### Background snapshot

```bash
aio-calculator background --z 0.57 --json
```

This returns the closed-FRW background snapshot used by the website redshift widget and the published background cards.

### Recombination primitives

```bash
aio-calculator recombination-point --z 1100 --json
```

This returns theorem-grade local recombination primitives on the geometric baryon slot, including:

- `T_R,loc`
- `H_loc`
- `n_H,geom`
- `x_e` from the local Saha seed
- `kappa'_loc`
- `d tau_obs / dz`

## Exploring the Theorem Dictionary

### CLI provenance catalog

```bash
aio-calculator provenance-catalog --json
```

This lists:

- all theorem nodes
- all explained-output families
- claim-status labels
- authority paths

### Static theorem surface

Build the public bundle and prerendered theorem pages:

```bash
python build_bundle.py
```

This writes:

- `data/aio_calculator_bundle.json`
- prerendered `calculator.html`
- prerendered `calculator-theorems.html`

The theorem dictionary page is the standalone reference surface; the calculator page embeds theorem chains inside each output card.

## Reproducing the Published Results

Run the full suite:

```bash
python -m pytest tests -q
```

At the current reviewed state, the local suite should pass in full.

Recommended reproduction path:

1. install the package from source
2. run `aio-calculator theta-star-theorem --json`
3. run `aio-calculator tt-spectrum --json --workers 12`
4. run `aio-calculator provenance-catalog --json`
5. run `python -m pytest tests -q`
6. run `python build_bundle.py`

The public website surfaces should then match the rebuilt local bundle.

## Project Layout

- `src/aio_calculator/`
  - source of truth for the calculator math, CLI, theorem graph, and TT carrier
- `tests/`
  - reproducibility and regression checks
- `build_bundle.py`
  - regenerates the JSON bundle and prerendered website theorem pages
- `data/aio_calculator_bundle.json`
  - machine-readable bundle used by the public site
- `README.md`
  - public alpha release guide

## Release Scope Recommendation

Decision still needed from David.

My recommendation:

1. Repo name
   - prefer a new dedicated source repo such as `io-calculator`
   - keep `io-framework-public` as the curated artifacts/reports/data repo
   - reason: source release cadence, issue tracking, packaging, and licensing are cleaner when the executable calculator is its own unit

2. License
   - prefer `Apache-2.0`
   - reason: permissive enough for broad reuse, but clearer than MIT on patents and contributor expectations

3. Public scope
   - publish: calculator source, tests, docs, bundle builder, final theorem reports needed for the live outputs
   - keep internal: failed routes, review notes, Roseta Smash, exploratory probes not needed for the release claims

4. Release tagging
   - yes: use tagged versions and a short changelog
   - minimum first tag suggestion: `v0.1.0-alpha.1`

## Release Artifact Boundary

Recommended public release contents:

- calculator source code
- tests
- build script and static bundle pipeline
- final theorem reports that support the public calculator outputs
- citation metadata
- installation instructions

Recommended private/internal only:

- Roseta Smash
- failed-route audits not needed to understand a released claim
- scratch scripts and abandoned probes
- review memos whose purpose is internal adversarial iteration rather than public reproducibility

## Public Links

Website:

- Calculator: https://dfife.github.io/calculator.html
- Theorem dictionary: https://dfife.github.io/calculator-theorems.html
- Scorecard: https://dfife.github.io/scorecard.html
- Lithium page: https://dfife.github.io/lithium.html

Zenodo / papers:

- Interior Observer community / latest records: https://zenodo.org/communities/interior-observer
- Lithium paper (Paper 24): https://zenodo.org/records/19219282/latest
- Bridge paper: https://zenodo.org/records/19440227/latest
- Hubble paper: https://zenodo.org/records/19558163/latest
- Four-problems paper: https://zenodo.org/records/19561708/latest

## Citation

Citation metadata should ship with the repo as `CITATION.cff`.

Draft citation guidance:

- cite the calculator source repository for executable results
- cite the relevant Zenodo paper(s) for the theorem chain behind a given output
- for website-facing review, link the scorecard and theorem dictionary pages alongside the code citation

Current author metadata used elsewhere in the public IO release surface:

- David Fife
- ORCID: https://orcid.org/0009-0001-0090-5825

## License

License decision pending review.

Suggested final wording once chosen:

- Code license: `<MIT | Apache-2.0 | GPL-3.0>`
- Data/report license: keep distinct if needed

Do not finalize this section until David picks the release license.

## Claim Discipline

This calculator uses explicit claim labels:

- `derived`
- `verified`
- `conditional`
- `reconstruction`
- `speculative`

Numerical agreement is not derivation. Open frontiers remain explicit in the code, the theorem dictionary, and the output payloads.

## Non-claims

This release draft does **not** claim:

- theorem-grade closure of the full `C_ell` spectrum
- theorem-grade closure of the physical TT high-`ell` tail
- a published particle-physics Paper 36 or Paper 37
- unconditional closure of every local theorem now housed under the calculator namespace
