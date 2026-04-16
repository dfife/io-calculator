"""Checks for the closed-`S^3` LOS carrier and explicit shell assembly."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.los_transfer import (  # noqa: E402
    OpenClosedS3LineOfSightOperator,
    TransferObservable,
    assemble_closed_s3_angular_power_spectrum,
    build_closed_s3_los_history,
    build_closed_s3_transfer_packet,
    project_closed_s3_line_of_sight,
    weight_closed_s3_transfer_packet,
)
from aio_calculator.recombination import OpenTheoremBoundaryError  # noqa: E402
from aio_calculator.s3_modes import scalar_mode  # noqa: E402


def test_transfer_packet_enforces_closed_support_rule() -> None:
    """No packet may carry multipoles outside the closed support `ell < nu`."""

    packet = build_closed_s3_transfer_packet(
        TransferObservable.TEMPERATURE,
        scalar_mode(4),
        curvature_K=1.0,
        q=5.0,
        ell_values=[0, 2, 4],
        delta_l=[1.0, 2.0, 3.0],
    )
    assert packet.ell_values == (0, 2, 4)
    with pytest.raises(ValueError):
        build_closed_s3_transfer_packet(
            TransferObservable.TEMPERATURE,
            scalar_mode(4),
            curvature_K=1.0,
            q=5.0,
            ell_values=[0, 5],
            delta_l=[1.0, 2.0],
        )


def test_auto_spectrum_assembly_uses_only_explicit_shell_weights() -> None:
    """`C_l` should be the explicit shell-weighted sum over supplied packets."""

    first = weight_closed_s3_transfer_packet(
        build_closed_s3_transfer_packet(
            "T",
            scalar_mode(4),
            curvature_K=1.0,
            q=5.0,
            ell_values=[0, 1, 2],
            delta_l=[1.0, 2.0, 3.0],
        ),
        shell_weight=2.0,
    )
    second = weight_closed_s3_transfer_packet(
        build_closed_s3_transfer_packet(
            "T",
            scalar_mode(5),
            curvature_K=1.0,
            q=6.0,
            ell_values=[1, 2, 3],
            delta_l=[4.0, 5.0, 6.0],
        ),
        shell_weight=3.0,
    )
    spectrum = assemble_closed_s3_angular_power_spectrum([first, second])
    assert spectrum.observable_pair == "TT"
    assert spectrum.ell_values == (0, 1, 2, 3)
    assert spectrum.c_ell == (
        2.0,
        56.0,
        93.0,
        108.0,
    )


def test_cross_spectrum_requires_matching_shells_and_weights() -> None:
    """Cross-spectra should pair the same shell family on both observables."""

    left = weight_closed_s3_transfer_packet(
        build_closed_s3_transfer_packet(
            "T",
            scalar_mode(4),
            curvature_K=1.0,
            q=5.0,
            ell_values=[1, 2],
            delta_l=[1.0, 2.0],
        ),
        shell_weight=2.0,
    )
    right = weight_closed_s3_transfer_packet(
        build_closed_s3_transfer_packet(
            "E",
            scalar_mode(4),
            curvature_K=1.0,
            q=5.0,
            ell_values=[1, 2],
            delta_l=[3.0, 4.0],
        ),
        shell_weight=2.0,
    )
    spectrum = assemble_closed_s3_angular_power_spectrum([left], right_packets=[right])
    assert spectrum.observable_pair == "TE"
    assert spectrum.c_ell == (6.0, 16.0)


def test_open_los_projector_refuses_to_fake_hyperspherical_projection() -> None:
    """The hierarchy-to-transfer seam should raise until the exact operator exists."""

    history = build_closed_s3_los_history(
        "T",
        scalar_mode(4),
        curvature_K=1.0,
        q=5.0,
        tau=[1.0, 2.0],
        source_samples=[1.0, 2.0],
    )
    with pytest.raises(OpenTheoremBoundaryError):
        project_closed_s3_line_of_sight(history)
    with pytest.raises(OpenTheoremBoundaryError):
        OpenClosedS3LineOfSightOperator().project(history)
