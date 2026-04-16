"""Theorem-grade active-branch theta-star closure from the carried selector leaf.

This module is separate from `theorem_cmb.py` on purpose.

- `derived / scoped`:
  Calculator.OU15 closes numeric `theta_*` on the fixed active branch package by
  evaluating the exact strict-bare selector backbone at the carried physical
  selector leaf.
- `not a transport solver`:
  this module does not synthesize a full CMB spectrum or replace the exact
  open Stage-2/source operator. It exposes the already-derived active-branch
  scalar closure only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import ACTIVE_BRANCH, ACTIVE_BRANCH_THETA_STAR_SELECTOR_Z
from .selector import (
    STRICT_BARE_J_THETA,
    observer_theta100_to_phase_equivalent_redshift,
    strict_bare_bulk_theta_deg,
)


@dataclass(frozen=True)
class ActiveBranchThetaStar:
    """Theorem-grade active-branch acoustic-angle payload."""

    branch_label: str
    claim_status: str
    selector_leaf_z: float
    theta_bare_deg: float
    theta_obs_deg: float
    theta_star_100: float
    selector_roundtrip_error: float

    def as_dict(self) -> dict[str, float | str]:
        return asdict(self)


def compute_active_branch_theta_star() -> ActiveBranchThetaStar:
    """Return the theorem-grade active-branch `theta_*` closure.

    Status: `derived / scoped`
    Authority: Calculator.OU15 plus the Calculator selector backbone.
    """

    z_sel = ACTIVE_BRANCH_THETA_STAR_SELECTOR_Z
    theta_bare_deg = strict_bare_bulk_theta_deg(z_sel)
    theta_obs_deg = STRICT_BARE_J_THETA * theta_bare_deg
    theta_star_100 = theta_obs_deg * 3.141592653589793 / 180.0 * 100.0
    roundtrip = observer_theta100_to_phase_equivalent_redshift(theta_star_100)
    return ActiveBranchThetaStar(
        branch_label=ACTIVE_BRANCH.label,
        claim_status="derived / scoped theorem-grade active-branch theta_* closure",
        selector_leaf_z=z_sel,
        theta_bare_deg=theta_bare_deg,
        theta_obs_deg=theta_obs_deg,
        theta_star_100=theta_star_100,
        selector_roundtrip_error=roundtrip - z_sel,
    )


__all__ = [
    "ActiveBranchThetaStar",
    "compute_active_branch_theta_star",
]
