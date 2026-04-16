"""Checks for the theorem-grade strict-bare selector module."""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator import (  # noqa: E402
    STRICT_BARE_J_THETA,
    certify_strict_bare_selector_domain,
    observer_theta_to_phase_equivalent_redshift,
    select_phase_equivalent_redshift,
    strict_bare_bulk_theta_derivative_deg_per_redshift,
    strict_bare_bulk_theta_deg,
    strict_bare_monotonicity_margin,
)


def test_selector_domain_certificate_stays_strictly_monotone() -> None:
    """The carried recombination interval should remain a valid inverse map."""

    cert = certify_strict_bare_selector_domain()
    assert cert.theta_max_deg > cert.theta_min_deg
    assert cert.monotonicity_margin_lower_bound > 25.0
    assert cert.dm_over_rs_lower_bound > 60.0
    assert cert.cs_over_c_lower_bound > 0.43
    assert cert.cos_psi_lower_bound < 0.0


def test_strict_bare_derivative_is_negative_on_the_carried_interval() -> None:
    """The analytic derivative margin should force strict decrease."""

    for z in (900.0, 1100.0, 1300.0):
        assert strict_bare_monotonicity_margin(z) > 0.0
        assert strict_bare_bulk_theta_derivative_deg_per_redshift(z) < 0.0


def test_phase_equivalent_selector_round_trips_bulk_angles() -> None:
    """Inverting the strict-bare bulk angle should recover the input leaf."""

    for z in (950.0, 1100.0, 1250.0):
        theta_bare = strict_bare_bulk_theta_deg(z)
        recovered = select_phase_equivalent_redshift(theta_bare)
        assert math.isclose(recovered, z, rel_tol=0.0, abs_tol=1.0e-6)


def test_observer_theta_selector_round_trips_self_consistently() -> None:
    """Observer-side angles should invert after dividing by the exact `J_theta`."""

    z = 1102.826411201581
    theta_obs = STRICT_BARE_J_THETA * strict_bare_bulk_theta_deg(z)
    recovered = observer_theta_to_phase_equivalent_redshift(theta_obs)
    assert math.isclose(recovered, z, rel_tol=0.0, abs_tol=1.0e-6)
