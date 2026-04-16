"""Conditional exact Stage-2 dynamic-network history builders.

This module closes the remaining Stage-2 connector at the scope that is
actually available today:

- `conditional / scoped`: a standalone inherited-FULL history builder on the
  active IO local background, exporting the exact extended state
  `Y_rec(z) = (x_e(z), T_m(z), D_-(q;z), L_-(z))`
- `derived / scoped`: reduction of that exact sampled state to the smaller
  `Stage2History` carrier already consumed by the current scalar hierarchy code

What is still not claimed here:

- a universal IO-native renormalization theorem replacing inherited FULL atomic
  and radiative-transfer physics
- a finite-dimensional compression of `D_-(q;z)` to one preferred scalar
  without an explicit caller choice
"""

from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .constants import (
    ACTIVE_BARYON_SLOTS,
    ACTIVE_BRANCH,
    ACTIVE_IO_CONSTANTS,
    BranchParameters,
    CALCULATOR_ROOT,
    HYREC_ROOT,
    IO_SCHWARZSCHILD_RADIUS_M,
)
from .recombination import ExactStage2Solver, Stage2History


DRIVER_TEMPLATE = Path(__file__).with_name("stage2_dynamic_network_driver.c.in")
DEFAULT_BUILD_DIR = CALCULATOR_ROOT / ".hyrec_stage2_build"
LINE_LABELS = ("Ly_alpha", "Ly_beta", "Ly_gamma")


def _float_tuple(values: Sequence[float], *, name: str) -> tuple[float, ...]:
    """Validate a non-empty finite float tuple."""

    coerced = tuple(float(value) for value in values)
    if not coerced:
        raise ValueError(f"{name} must not be empty")
    if any(not math.isfinite(value) for value in coerced):
        raise ValueError(f"{name} must contain only finite values")
    return coerced


def _strictly_increasing(values: Sequence[float], *, name: str) -> tuple[float, ...]:
    """Require a non-empty strictly increasing finite float tuple."""

    coerced = _float_tuple(values, name=name)
    if any(value < 0.0 for value in coerced):
        raise ValueError(f"{name} must be non-negative")
    if any(b <= a for a, b in zip(coerced, coerced[1:])):
        raise ValueError(f"{name} must be strictly increasing")
    return coerced


def _matrix_tuple(
    rows: Sequence[Sequence[float]],
    *,
    row_length: int,
    name: str,
) -> tuple[tuple[float, ...], ...]:
    """Validate a finite row-major matrix of explicit history values."""

    coerced = tuple(_float_tuple(row, name=f"{name}[{index}]") for index, row in enumerate(rows))
    if any(len(row) != row_length for row in coerced):
        raise ValueError(f"every row in {name} must match the z-grid length")
    return coerced


def _driver_constants(
    *,
    branch: BranchParameters,
    omega_b_geom_h2: float,
) -> dict[str, str]:
    """Return the branch/package constants inserted into the C driver template."""

    h = branch.h
    omega_b_geom = omega_b_geom_h2 / (h * h)
    replacements = {
        "@HYREC_PATH@": f"{HYREC_ROOT}/",
        "@ZMAX@": f"{3000.0:.17g}",
        "@X_IO@": f"{ACTIVE_IO_CONSTANTS.x:.17g}",
        "@GAMMA_IO@": f"{ACTIVE_IO_CONSTANTS.gamma_bi:.17g}",
        "@T_CMB_OBS@": f"{branch.T_cmb:.17g}",
        "@OMEGA_B_GEOM@": f"{omega_b_geom:.17g}",
        "@OMEGA_M@": f"{branch.Omega_m:.17g}",
        "@OMEGA_K@": f"{branch.Omega_k:.17g}",
        "@OMEGA_LAMBDA@": f"{branch.Omega_lambda:.17g}",
        "@H@": f"{h:.17g}",
        "@YHE@": f"{branch.YHe:.17g}",
        "@NEFF@": f"{branch.N_eff:.17g}",
        "@RS_OS_M@": f"{IO_SCHWARZSCHILD_RADIUS_M:.17g}",
    }
    return replacements


def _patched_history_source() -> str:
    """Return the exact standalone HyRec history source with the grid fix applied."""

    history_src = (HYREC_ROOT / "history.c").read_text()
    replacements = {
        "  double Nz = data->Nz, dz = data->zmax/Nz;\n": (
            "  double Nz = data->Nz, dz = data->zmax/(Nz-1.) * (1.0 + 1e-12);\n"
        ),
        "  dz = zstart/Nz;\n": "  dz = zstart/(Nz-1.) * (1.0 + 1e-12);\n",
    }
    for needle, replacement in replacements.items():
        if needle not in history_src:
            raise RuntimeError(
                "Could not find the expected HyRec history-grid line while preparing "
                "the standalone exact Stage-2 driver."
            )
        history_src = history_src.replace(needle, replacement, 1)
    return history_src


@dataclass(frozen=True)
class ExactStage2DynamicHistory:
    """Exact sampled extended Stage-2 state on an observer-redshift grid."""

    z_obs: tuple[float, ...]
    x_e: tuple[float, ...]
    T_m_loc_K: tuple[float, ...]
    H_loc_s_inv: tuple[float, ...]
    T_r_loc_K: tuple[float, ...]
    history_activation_z: float
    dlna: float
    characteristic_energy_eV: tuple[float, ...]
    D_minus: tuple[tuple[float, ...], ...]
    line_labels: tuple[str, ...]
    L_minus: tuple[tuple[float, ...], ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        size = len(self.z_obs)
        if size < 2:
            raise ValueError("ExactStage2DynamicHistory requires at least two redshift samples")
        if len(self.x_e) != size or len(self.T_m_loc_K) != size:
            raise ValueError("x_e and T_m_loc_K must match the z-grid length")
        if len(self.H_loc_s_inv) != size or len(self.T_r_loc_K) != size:
            raise ValueError("H_loc_s_inv and T_r_loc_K must match the z-grid length")
        if any(value < 0.0 for value in self.x_e):
            raise ValueError("x_e values must stay non-negative")
        if len(self.line_labels) != len(self.L_minus):
            raise ValueError("line_labels and L_minus must have the same length")
        if any(len(row) != size for row in self.D_minus):
            raise ValueError("every D_minus row must match the z-grid length")
        if any(len(row) != size for row in self.L_minus):
            raise ValueError("every L_minus row must match the z-grid length")

    def characteristic_series(self, index: int) -> tuple[float, ...]:
        """Return one explicit `D_-(q;z)` series on the sampled z-grid."""

        return self.D_minus[int(index)]

    def line_series(self, index: int) -> tuple[float, ...]:
        """Return one explicit line-handoff series `L_-(z)` on the sampled z-grid."""

        return self.L_minus[int(index)]

    def reduce_to_stage2_history(
        self,
        *,
        characteristic_bin: int | None = None,
        line_channel: int | None = None,
    ) -> Stage2History:
        """Reduce the exact sampled state to the smaller calculator Stage-2 carrier.

        No preferred scalar compression of the characteristic field is imposed.
        If the caller wants a one-dimensional `D_minus_norm` or `L_minus` series
        carried into `Stage2History`, the choice must be explicit.
        """

        d_minus = None if characteristic_bin is None else self.characteristic_series(characteristic_bin)
        l_minus = None if line_channel is None else self.line_series(line_channel)
        return Stage2History.from_sequences(
            self.z_obs,
            self.x_e,
            self.T_m_loc_K,
            D_minus_norm=d_minus,
            L_minus=l_minus,
        )


@dataclass(frozen=True)
class InheritedFullStage2DynamicHistoryBuilder(ExactStage2Solver):
    """Conditional exact Stage-2 builder using standalone inherited FULL physics."""

    build_dir: Path = DEFAULT_BUILD_DIR
    zmax: float = 3000.0
    branch: BranchParameters = ACTIVE_BRANCH
    omega_b_geom_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2

    @property
    def driver_source(self) -> Path:
        return self.build_dir / "stage2_dynamic_network_driver.c"

    @property
    def driver_binary(self) -> Path:
        return self.build_dir / "stage2_dynamic_network_driver"

    @property
    def patched_history_source(self) -> Path:
        return self.build_dir / "history_patched.c"

    def _render_driver_source(self) -> str:
        source = DRIVER_TEMPLATE.read_text()
        for token, value in _driver_constants(
            branch=self.branch,
            omega_b_geom_h2=self.omega_b_geom_h2,
        ).items():
            source = source.replace(token, value)
        return source

    def _ensure_driver(self) -> None:
        if shutil.which("gcc") is None:
            raise RuntimeError("gcc is required to build the standalone Stage-2 exact-history driver")

        self.build_dir.mkdir(parents=True, exist_ok=True)
        rendered_source = self._render_driver_source()
        source_dependencies = (
            DRIVER_TEMPLATE,
            HYREC_ROOT / "history.c",
            HYREC_ROOT / "hydrogen.c",
            HYREC_ROOT / "helium.c",
            HYREC_ROOT / "hyrectools.c",
            HYREC_ROOT / "energy_injection.c",
        )
        needs_rebuild = not self.driver_binary.exists()
        if not needs_rebuild and (
            not self.driver_source.exists()
            or self.driver_source.read_text() != rendered_source
        ):
            needs_rebuild = True
        if not needs_rebuild:
            binary_mtime = self.driver_binary.stat().st_mtime
            needs_rebuild = any(path.stat().st_mtime > binary_mtime for path in source_dependencies)
        if not needs_rebuild:
            return

        self.driver_source.write_text(rendered_source)
        self.patched_history_source.write_text(_patched_history_source())
        compile_cmd = [
            "gcc",
            "-O2",
            "-std=c99",
            "-D_GNU_SOURCE",
            f"-I{HYREC_ROOT}",
            str(self.driver_source),
            str(self.patched_history_source),
            str(HYREC_ROOT / "hydrogen.c"),
            str(HYREC_ROOT / "helium.c"),
            str(HYREC_ROOT / "hyrectools.c"),
            str(HYREC_ROOT / "energy_injection.c"),
            "-lm",
            "-o",
            str(self.driver_binary),
        ]
        subprocess.run(
            compile_cmd,
            cwd=CALCULATOR_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def _run_driver(self, z_obs: tuple[float, ...]) -> ExactStage2DynamicHistory:
        self._ensure_driver()
        with tempfile.TemporaryDirectory(dir=self.build_dir) as tmpdir:
            tmp = Path(tmpdir)
            query_path = tmp / "query_z.txt"
            output_path = tmp / "stage2_history.dat"
            query_path.write_text("".join(f"{value:.17e}\n" for value in z_obs))
            subprocess.run(
                [str(self.driver_binary), str(query_path), str(output_path)],
                cwd=CALCULATOR_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            return _parse_exact_history(output_path)

    def solve_exact_history(self, z_obs: Sequence[float]) -> ExactStage2DynamicHistory:
        """Return the full inherited-FULL sampled state `Y_rec(z)`."""

        z_obs_t = _strictly_increasing(z_obs, name="z_obs")
        if z_obs_t[-1] > self.zmax:
            raise ValueError(f"z_obs must stay within the standalone HyRec range z <= {self.zmax}")
        return self._run_driver(z_obs_t)

    def solve_history(self, z_obs: Sequence[float]) -> Stage2History:
        """Return the reduced calculator Stage-2 carrier on the requested grid."""

        return self.solve_exact_history(z_obs).reduce_to_stage2_history()


def _parse_exact_history(path: Path) -> ExactStage2DynamicHistory:
    """Parse the standalone inherited-FULL history file."""

    meta: dict[str, object] = {}
    rows: list[list[float]] = []
    for line in path.read_text().splitlines():
        if not line:
            continue
        if line.startswith("#"):
            content = line[1:].strip()
            if content.startswith("mode "):
                meta["mode"] = content.split(maxsplit=1)[1]
            elif content.startswith("dlna "):
                meta["dlna"] = float(content.split(maxsplit=1)[1])
            elif content.startswith("history_activation_z "):
                meta["history_activation_z"] = float(content.split(maxsplit=1)[1])
            elif content.startswith("line_labels "):
                meta["line_labels"] = tuple(content.split()[1:])
            elif content.startswith("characteristic_energy_eV "):
                meta["characteristic_energy_eV"] = tuple(
                    float(value) for value in content.split()[1:]
                )
            continue
        rows.append([float(value) for value in line.split()])

    if "characteristic_energy_eV" not in meta or "line_labels" not in meta:
        raise RuntimeError("standalone Stage-2 output is missing characteristic-grid metadata")
    characteristic_energy_eV = tuple(meta["characteristic_energy_eV"])  # type: ignore[arg-type]
    line_labels = tuple(meta["line_labels"])  # type: ignore[arg-type]
    if not rows:
        raise RuntimeError("standalone Stage-2 driver returned no sampled rows")

    column_count = 5 + len(characteristic_energy_eV) + len(line_labels)
    if any(len(row) != column_count for row in rows):
        raise RuntimeError("standalone Stage-2 output row has an unexpected column count")

    z_obs = tuple(row[0] for row in rows)
    x_e = tuple(row[1] for row in rows)
    T_m_loc_K = tuple(row[2] for row in rows)
    H_loc_s_inv = tuple(row[3] for row in rows)
    T_r_loc_K = tuple(row[4] for row in rows)
    d_minus_rows = tuple(
        tuple(row[5 + index] for row in rows)
        for index in range(len(characteristic_energy_eV))
    )
    l_minus_rows = tuple(
        tuple(row[5 + len(characteristic_energy_eV) + index] for row in rows)
        for index in range(len(line_labels))
    )

    return ExactStage2DynamicHistory(
        z_obs=_strictly_increasing(z_obs, name="z_obs"),
        x_e=_float_tuple(x_e, name="x_e"),
        T_m_loc_K=_float_tuple(T_m_loc_K, name="T_m_loc_K"),
        H_loc_s_inv=_float_tuple(H_loc_s_inv, name="H_loc_s_inv"),
        T_r_loc_K=_float_tuple(T_r_loc_K, name="T_r_loc_K"),
        history_activation_z=float(meta["history_activation_z"]),
        dlna=float(meta["dlna"]),
        characteristic_energy_eV=_float_tuple(
            characteristic_energy_eV,
            name="characteristic_energy_eV",
        ),
        D_minus=_matrix_tuple(
            d_minus_rows,
            row_length=len(z_obs),
            name="D_minus",
        ),
        line_labels=line_labels,
        L_minus=_matrix_tuple(
            l_minus_rows,
            row_length=len(z_obs),
            name="L_minus",
        ),
        claim_status="conditional / scoped",
        provenance_node_ids=(
            "premise.2",
            "paper31.stage2_markov_state",
            "local.inherited_full_stage2_dynamic_history_builder",
        ),
        scope_boundary=(
            "Conditional exact inherited-FULL Stage-2 state on the active IO local background only.",
            "Uses standalone FULL HyRec radiative-transfer and chemistry physics under Premise 2 instead of a new universal IO-native renormalization theorem.",
            "Does not select a preferred one-dimensional compression of `D_-(q;z)` unless the caller chooses one explicitly.",
        ),
    )


def build_inherited_full_exact_stage2_history(
    z_obs: Sequence[float],
    *,
    builder: InheritedFullStage2DynamicHistoryBuilder | None = None,
) -> ExactStage2DynamicHistory:
    """Convenience wrapper returning the full sampled inherited-FULL state."""

    active_builder = (
        InheritedFullStage2DynamicHistoryBuilder()
        if builder is None
        else builder
    )
    return active_builder.solve_exact_history(z_obs)


def build_inherited_full_stage2_history(
    z_obs: Sequence[float],
    *,
    builder: InheritedFullStage2DynamicHistoryBuilder | None = None,
) -> Stage2History:
    """Convenience wrapper returning the reduced calculator Stage-2 carrier."""

    active_builder = (
        InheritedFullStage2DynamicHistoryBuilder()
        if builder is None
        else builder
    )
    return active_builder.solve_history(z_obs)


__all__ = [
    "ExactStage2DynamicHistory",
    "InheritedFullStage2DynamicHistoryBuilder",
    "build_inherited_full_exact_stage2_history",
    "build_inherited_full_stage2_history",
]
