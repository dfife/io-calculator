"""Fixed constants, authority paths, and carried branch values.

This module is intentionally declarative. It should answer:

- which local paper outputs the public calculator is allowed to depend on
- which numerical branch values are carried into the calculator surface
- which unit conventions are used by the late-time background engine
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path


CALCULATOR_ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = CALCULATOR_ROOT.parent if (CALCULATOR_ROOT.parent / "AGENTS.md").exists() else None
ROOT = LAB_ROOT or CALCULATOR_ROOT
VENDOR_ROOT = CALCULATOR_ROOT / "vendor"


def _vendor_path(repo_relative: str, lab_relative: str | None = None) -> Path:
    """Resolve one vendored third-party source tree with lab fallback."""

    repo_path = VENDOR_ROOT / repo_relative
    if repo_path.exists():
        return repo_path
    if LAB_ROOT is not None and lab_relative is not None:
        lab_path = LAB_ROOT / lab_relative
        if lab_path.exists():
            return lab_path
    return repo_path if lab_relative is None or LAB_ROOT is None else LAB_ROOT / lab_relative


CLASS_PUBLIC_ROOT = _vendor_path("class_public", "src/class_public")
HYREC_ROOT = _vendor_path("HyRec2020", "src/class_public/external/HyRec2020")


def _authority_path(repo_relative: str, lab_relative: str | None = None) -> Path:
    """Resolve one authority file with a repo-local first preference.

    The public source release must be runnable outside `/opt/cosmology-lab`, so
    authority files prefer repo-local copies when present. The private lab tree
    remains a fallback during the migration period.
    """

    repo_path = CALCULATOR_ROOT / repo_relative
    if repo_path.exists():
        return repo_path
    if LAB_ROOT is not None and lab_relative is not None:
        lab_path = LAB_ROOT / lab_relative
        if lab_path.exists():
            return lab_path
    return repo_path if lab_relative is None or LAB_ROOT is None else LAB_ROOT / lab_relative

AUTHORITY_PATHS = {
    "lab_premises": _authority_path("docs/PREMISES.md", "AGENTS.md"),
    "paper12_baryon_dictionary": _authority_path(
        "docs/zenodo/Interior_Observer_Paper12_v3_9.docx",
        "results/Full Papers/Interior_Observer_Paper12_v3_9.docx",
    ),
    "paper17_gttp": _authority_path(
        "docs/zenodo/Interior_Observer_Paper17_v1_4.docx",
        "results/Full Papers/Interior_Observer_Paper17_v1_4.docx",
    ),
    "paper21_tio_branch_assignment": _authority_path(
        "reports/paper21/paper21_tio_branch_assignment_theorem_report.txt",
        "results/paper21/paper21_tio_branch_assignment_theorem_report.txt",
    ),
    "paper27_visibility_slot": _authority_path(
        "reports/paper27/paper27_av1_c1b_round2_memo.md",
        "results/paper27/paper27_av1_c1b_round2_memo.md",
    ),
    "paper29_sound_speed_selector": _authority_path(
        "reports/paper29/paper29_sound_speed_baryon_selector_audit_report.md",
        "results/paper29/paper29_sound_speed_baryon_selector_audit_report.md",
    ),
    "paper22_spatial_hodge_complex": _authority_path(
        "reports/paper22/paper22_spatial_hodge_complex_report.txt",
        "results/paper22/paper22_spatial_hodge_complex_report.txt",
    ),
    "paper23_scalar_perturbations": _authority_path(
        "reports/paper23/paper23_scalar_perturbations_report.txt",
        "results/paper23/paper23_scalar_perturbations_report.txt",
    ),
    "paper23_bridge_uniqueness": _authority_path(
        "reports/paper23/paper23_bridge_uniqueness_report.txt",
        "results/paper23/paper23_bridge_uniqueness_report.txt",
    ),
    "paper28_closed_s3_power_definition": _authority_path(
        "reports/paper28/paper28_closed_s3_power_definition_report.md",
        "results/paper28/paper28_closed_s3_power_definition_report.md",
    ),
    "paper28_scalar_tilt": _authority_path(
        "docs/zenodo/Interior_Observer_Paper28_v1_3.docx",
        "results/Full Papers/Interior_Observer_Paper28_v1_3.docx",
    ),
    "paper30_legacy_recompute": _authority_path(
        "reports/paper30/paper30_full_recompute_legacy_branch_results.json",
        "results/paper30/paper30_full_recompute_legacy_branch_results.json",
    ),
    "paper30_published": _authority_path(
        "docs/zenodo/Interior_Observer_Paper30_v1_3.docx",
        "results/Full Papers/Interior_Observer_Paper30_v1_3.docx",
    ),
    "paper30_master_clock_correction": _authority_path(
        "reports/paper30/paper30_master_clock_correction_report.txt",
        "results/paper30/paper30_master_clock_correction_report.txt",
    ),
    "paper30_deuterium_scorecard": _authority_path(
        "reports/paper30/paper30_funrun_r_isw_deuterium_schur_report.txt",
        "results/paper30/paper30_funrun_r_isw_deuterium_schur_report.txt",
    ),
    "paper30_helium_scorecard": _authority_path(
        "reports/paper30/paper30_funrun_yp_21cm_nanograv_schur_report.txt",
        "results/paper30/paper30_funrun_yp_21cm_nanograv_schur_report.txt",
    ),
    "paper31_baryon_assignment": _authority_path(
        "reports/paper31/paper31_baryon_assignment_theorems.md",
        "results/paper31/paper31_baryon_assignment_theorems.md",
    ),
    "paper31_clock_transport": _authority_path(
        "reports/paper31/paper31_recombination_clock_transport_theorem.md",
        "results/paper31/paper31_recombination_clock_transport_theorem.md",
    ),
    "paper31_local_background_state_map": _authority_path(
        "reports/paper31/paper31_stage2_local_background_state_map_theorem.md",
        "results/paper31/paper31_stage2_local_background_state_map_theorem.md",
    ),
    "paper31_stage2_markov_state": _authority_path(
        "reports/paper31/paper31_stage2_lossless_characteristic_markov_theorem.md",
        "results/paper31/paper31_stage2_lossless_characteristic_markov_theorem.md",
    ),
    "paper31_legacy_recompute": _authority_path(
        "reports/paper31/paper31_full_recompute_legacy_branch_results.json",
        "results/paper31/paper31_full_recompute_legacy_branch_results.json",
    ),
    "paper32_s3_solver_spec": _authority_path(
        "reports/paper32/paper32_s3_native_solver_specification_theorem.md",
        "results/paper32/paper32_s3_native_solver_specification_theorem.md",
    ),
    "paper24_lithium_paper": _authority_path(
        "docs/zenodo/Interior_Observer_Paper24_v2_1.docx",
        "results/Full Papers/Interior_Observer_Paper24_v2_1.docx",
    ),
    "paper32_modular_dtn_field_transfer": _authority_path(
        "reports/paper32/paper32_modular_dtn_field_transfer_theorem.md",
        "results/paper32/paper32_modular_dtn_field_transfer_theorem.md",
    ),
    "paper32_hidden_identification_repair": _authority_path(
        "reports/paper32/paper32_hidden_identification_repair_theorem.md",
        "results/paper32/paper32_hidden_identification_repair_theorem.md",
    ),
    "calculator_photosphere_theta_star": _authority_path(
        "reports/calculator/calculator_premise2_photosphere_theta_star_theorem_report.md",
        "results/calculator/calculator_premise2_photosphere_theta_star_theorem_report.md",
    ),
    "calculator_phase_selector": _authority_path(
        "reports/calculator/calculator_phase_equivalent_selector_theorem_report.md",
        "results/calculator/calculator_phase_equivalent_selector_theorem_report.md",
    ),
    "paper32_typed_projection": _authority_path(
        "reports/paper32/paper32_typed_boundary_to_bulk_projection_theorem.md",
        "results/paper32/paper32_typed_boundary_to_bulk_projection_theorem.md",
    ),
    "calculator_packet_coefficient_fixing": _authority_path(
        "reports/calculator/calculator_effectc_packet_coefficient_fixing_theorem_report.md",
        "results/calculator/calculator_effectc_packet_coefficient_fixing_theorem_report.md",
    ),
    "calculator_packet1500_support_promotion": _authority_path(
        "reports/calculator/calculator_effectc_packet1500_support_promotion_theorem_report.md",
        "results/calculator/calculator_effectc_packet1500_support_promotion_theorem_report.md",
    ),
    "calculator_highz_tail_slaving": _authority_path(
        "reports/calculator/calculator_effectc_highz_tail_slaving_theorem_report.md",
        "results/calculator/calculator_effectc_highz_tail_slaving_theorem_report.md",
    ),
    "calculator_peak_window_tail_profile_audit": _authority_path(
        "reports/calculator/calculator_effectc_peak_window_tail_profile_audit_report.md",
        "results/calculator/calculator_effectc_peak_window_tail_profile_audit_report.md",
    ),
    "calculator_selector_support_promotion": _authority_path(
        "reports/calculator/calculator_effectc_selector_support_promotion_theorem_report.md",
        "results/calculator/calculator_effectc_selector_support_promotion_theorem_report.md",
    ),
    "calculator_active_theta_star": _authority_path(
        "reports/calculator/calculator_active_branch_theta_star_theorem_report.md",
        "results/calculator/calculator_active_branch_theta_star_theorem_report.md",
    ),
    "calculator_thomson_history_realization": _authority_path(
        "reports/calculator/calculator_thomson_history_realization_theorem_report.md",
        "results/calculator/calculator_thomson_history_realization_theorem_report.md",
    ),
    "calculator_peak_functional_separation": _authority_path(
        "reports/calculator/calculator_peak_functional_separation_theorem_report.md",
        "results/calculator/calculator_peak_functional_separation_theorem_report.md",
    ),
    "calculator_null_family_readout": _authority_path(
        "reports/calculator/calculator_null_family_readout_theorem_report.md",
        "results/calculator/calculator_null_family_readout_theorem_report.md",
    ),
    "calculator_closed_scalar_acoustic_generator": _authority_path(
        "reports/calculator/calculator_closed_scalar_acoustic_generator_theorem_report.md",
        "results/calculator/calculator_closed_scalar_acoustic_generator_theorem_report.md",
    ),
    "calculator_typed_r_operator": _authority_path(
        "reports/calculator/calculator_typed_r_operator_theorem_report.md",
        "results/calculator/calculator_typed_r_operator_theorem_report.md",
    ),
    "calculator_typed_r_site_uniqueness": _authority_path(
        "reports/calculator/calculator_typed_r_site_uniqueness_theorem_report.md",
        "results/calculator/calculator_typed_r_site_uniqueness_theorem_report.md",
    ),
    "calculator_typed_thomson_split_history_audit": _authority_path(
        "reports/calculator/calculator_typed_thomson_split_history_implementation_audit_report.md",
        "results/calculator/calculator_typed_thomson_split_history_implementation_audit_report.md",
    ),
    "calculator_tt_first_peak_support": _authority_path(
        "reports/calculator/calculator_tt_first_peak_support_theorem_report.md",
        "results/calculator/calculator_tt_first_peak_support_theorem_report.md",
    ),
    "paper35_dark_energy": _authority_path(
        "reports/paper35/paper35_desi_dark_energy_investigation_results.json",
        "results/paper35/paper35_desi_dark_energy_investigation_results.json",
    ),
    "paper35_eta_closure": _authority_path(
        "reports/paper35/paper35_eta_io_gap_closure_results.json",
        "results/paper35/paper35_eta_io_gap_closure_results.json",
    ),
    "public_paper_index": _authority_path(
        "data/papers.json",
        "tmp/dfife.github.io/data/papers.json",
    ),
}

# Unit and physical constants used by the late-time background engine.
C_KM_S = 299792.458
C_SI = 299792458.0
G_SI = 6.67430e-11
HBAR_SI = 1.054571817e-34
K_B_SI = 1.380649e-23
M_ELECTRON_KG = 9.1093837015e-31
MPC_M = 3.0856775814913673e22
YEAR_S = 365.25 * 24.0 * 3600.0
GYR_S = 1.0e9 * YEAR_S
SIGMA_T_SI = 6.6524587321e-29
ZETA3 = 1.202056903159594

# Standard hydrogen microphysics used under Premise 2 in the local chemistry
# layer. The recombination module uses the direct ionization energy in joules
# so the Saha seed stays transparent in SI units.
HYDROGEN_IONIZATION_ENERGY_J = 2.1798723611035e-18

# Standard thermal reference values used in radiation-density and eta
# conversions. `T_OBS_ETA_K` keeps the preferred Paper 35 late-time convention.
T_CMB_REF_K = 2.7255
OMEGA_GAMMA_H2_REF = 2.469e-5
NEUTRINO_RELATIVISTIC_FACTOR = (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0)
T_OBS_ETA_K = 2.7253048490552736

# Mass conventions carried by the eta closure work. The calculator currently
# uses `MEAN_BARYON_MASS_YP_KG` by default because that is the preferred late-
# time Paper 35 convention.
PROTON_MASS_KG = 1.67262192369e-27
HYDROGEN_ATOM_MASS_KG = 1.673532838e-27
MEAN_BARYON_MASS_YP_KG = 1.6705903034252064e-27


@dataclass(frozen=True)
class BranchParameters:
    """Curved observer-side branch quantities used by the public calculator."""

    label: str
    H0: float
    Omega_m: float
    Omega_k: float
    Omega_lambda: float
    Omega_r: float
    T_cmb: float
    N_eff: float
    rd_mpc: float
    A_s: float
    n_s: float
    YHe: float

    @property
    def h(self) -> float:
        return self.H0 / 100.0

    def as_dict(self) -> dict[str, float | str]:
        return asdict(self) | {"h": self.h}


@dataclass(frozen=True)
class BaryonSlots:
    """Carried active-branch baryon slots exposed on the calculator surface."""

    omega_b_geom_h2: float
    omega_b_eff_h2: float
    omega_b_clustering_h2: float
    omega_b_struct_h2: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class PerturbationBranchPackage:
    """Background/slot package carried by the perturbation-side solver stack."""

    label: str
    branch: BranchParameters
    baryon_slots: BaryonSlots
    t_io_ref_k: float
    scope_note: str

    def as_dict(self) -> dict[str, float | str | dict[str, float]]:
        return {
            "label": self.label,
            "branch": self.branch.as_dict(),
            "baryon_slots": self.baryon_slots.as_dict(),
            "t_io_ref_k": self.t_io_ref_k,
            "scope_note": self.scope_note,
        }


@dataclass(frozen=True)
class IOConstants:
    """Framework constants carried into the active public calculator."""

    x: float
    gamma_bi: float
    K_gauge: float
    eta_bao: float
    sigma_io: float
    f_b: float
    f_gamma: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


ACTIVE_BRANCH = BranchParameters(
    label="active_paper10_legacy_projected_branch",
    H0=67.57585653582628,
    Omega_m=0.34868395067621694,
    Omega_k=-0.04579112576013168,
    Omega_lambda=0.69701575761593,
    Omega_r=9.141746798467538e-05,
    T_cmb=2.7253,
    N_eff=3.044,
    rd_mpc=144.01351425392883,
    A_s=2.0072459972737347e-9,
    n_s=0.9639,
    YHe=0.2477,
)

MASTER_CLOCK_BARE_BRANCH = BranchParameters(
    label="paper30_bare_master_clock_branch",
    H0=58.4,
    Omega_m=0.197,
    Omega_k=-0.13,
    Omega_lambda=0.933,
    Omega_r=0.00012259146481569604,
    T_cmb=2.7253,
    N_eff=3.044,
    rd_mpc=0.0,
    A_s=2.0072459972737347e-9,
    n_s=0.9639,
    YHe=0.2477,
)

STRICT_BARE_OS_BRANCH = BranchParameters(
    label="strict_bare_os_cycloid_branch",
    H0=15.146030624476964,
    Omega_m=2.9268193992,
    Omega_k=-1.9268193992,
    Omega_lambda=-0.0016628069,
    Omega_r=0.0016628069,
    T_cmb=2.6635,
    N_eff=3.044,
    rd_mpc=0.0,
    A_s=2.0072459972737347e-9,
    n_s=0.9639,
    YHe=0.2477,
)

STRICT_BARE_OMEGA_B_GEOM_H2 = 0.02102461376506758

ACTIVE_BARYON_SLOTS = BaryonSlots(
    omega_b_geom_h2=0.020995719061702847,
    omega_b_eff_h2=0.02898917105671435,
    omega_b_clustering_h2=0.01703545264427447,
    omega_b_struct_h2=0.02143434229616185,
)

# Reconstruct the reduced-stack constants from the carried gamma / f_b pair
# rather than hardcoding duplicated decimal approximations.
_GAMMA = 0.2375
_Q = 1.0 + _GAMMA**2
_K_GAUGE = math.log(_Q)
_F_B = 0.3127083362150252
_X = 2.0 * _GAMMA / _F_B

ACTIVE_IO_CONSTANTS = IOConstants(
    x=_X,
    gamma_bi=_GAMMA,
    K_gauge=_K_GAUGE,
    eta_bao=0.036124605346983495,
    sigma_io=0.8113774333810703,
    f_b=_F_B,
    f_gamma=math.exp(-_K_GAUGE),
)

# Calculator active-branch acoustic-angle closure.
ACTIVE_BRANCH_THETA_STAR_SELECTOR_Z = 1092.2670386731625

# IO background constants needed by the theorem-grade local recombination map.
# The radius is the Schwarzschild / horizon scale carried by the active IO
# branch; `T_IO_REF_K` is reconstructed from the derived thermal readout law
# `T_obs = T_IO * x^K_gauge`.
IO_SCHWARZSCHILD_RADIUS_M = 6.6835e26
T_IO_REF_K = ACTIVE_BRANCH.T_cmb / (
    ACTIVE_IO_CONSTANTS.x ** ACTIVE_IO_CONSTANTS.K_gauge
)

STRICT_BARE_T_IO_REF_K = STRICT_BARE_OS_BRANCH.T_cmb / (
    ACTIVE_IO_CONSTANTS.x ** ACTIVE_IO_CONSTANTS.K_gauge
)

ACTIVE_PERTURBATION_PACKAGE = PerturbationBranchPackage(
    label="active_projected_perturbation_package",
    branch=ACTIVE_BRANCH,
    baryon_slots=ACTIVE_BARYON_SLOTS,
    t_io_ref_k=T_IO_REF_K,
    scope_note=(
        "Projected active-branch perturbation package used by the current published calculator."
    ),
)

STRICT_BARE_PERTURBATION_PACKAGE = PerturbationBranchPackage(
    label="strict_bare_geom_scoped_perturbation_package",
    branch=STRICT_BARE_OS_BRANCH,
    baryon_slots=BaryonSlots(
        omega_b_geom_h2=STRICT_BARE_OMEGA_B_GEOM_H2,
        omega_b_eff_h2=STRICT_BARE_OMEGA_B_GEOM_H2,
        omega_b_clustering_h2=STRICT_BARE_OMEGA_B_GEOM_H2,
        omega_b_struct_h2=STRICT_BARE_OMEGA_B_GEOM_H2,
    ),
    t_io_ref_k=STRICT_BARE_T_IO_REF_K,
    scope_note=(
        "Scoped strict-bare perturbation package. Only the geometric baryon slot is theorem-grade here; "
        "the other slots are intentionally carried on the same geometric value until a bare-sector typed-slot theorem is derived."
    ),
)
