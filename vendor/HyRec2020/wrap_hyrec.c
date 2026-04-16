/**
 * Small wrapper file for the hyrec code to be used in thermodynamics
 * Nils Schoeneberg Feb 2019
 * */

#include "common.h"
#include "thermodynamics.h"
#include "wrap_hyrec.h"

static int thermodynamics_hyrec_gamma_active(const struct thermodynamics * pth) {
  return pth->io_recombination_gamma != 0.0;
}

static double thermodynamics_hyrec_tio_factor(const struct thermodynamics * pth) {
  if (thermodynamics_hyrec_gamma_active(pth) == _FALSE_) {
    return 1.0;
  }
  return 1.0 / pow(pth->io_recombination_x, log(1.0 + pth->io_recombination_gamma * pth->io_recombination_gamma));
}

static double thermodynamics_hyrec_local_hubble(const struct thermodynamics * pth, double z) {
  double y = pth->io_recombination_x * (1.0 + z);
  return _c_ * pth->io_recombination_x * (1.0 + z) * sqrt(y - 1.0) / pth->io_recombination_rs_m;
}

static double thermodynamics_hyrec_interp_table(double z, double * table, HYREC_DATA * data) {
  double dlna;
  if (z > data->zmax) return table[0];
  if (z < data->zmin) return table[data->Nz-1];
  dlna = data->cosmo->dlna;
  return rec_interp1d(-log(1.+data->zmax), dlna, table, data->Nz, -log(1.+z), &data->error, data->error_message);
}

static double thermodynamics_hyrec_interp_table_dz(double z, double * table, HYREC_DATA * data) {
  double u = -log(1. + z);
  double h = data->cosmo->dlna;
  double u_min = -log(1. + data->zmax);
  double u_max = -log(1. + data->zmin);
  double u_lo = u - h;
  double u_hi = u + h;
  double z_lo, z_hi;
  double f_lo, f_hi;

  if (u_lo < u_min) {
    u_lo = u;
    u_hi = MIN(u + h, u_max);
  }
  else if (u_hi > u_max) {
    u_lo = MAX(u - h, u_min);
    u_hi = u;
  }

  z_lo = exp(-u_lo) - 1.;
  z_hi = exp(-u_hi) - 1.;
  f_lo = thermodynamics_hyrec_interp_table(z_lo, table, data);
  f_hi = thermodynamics_hyrec_interp_table(z_hi, table, data);

  if (fabs(z_hi - z_lo) < 1e-30) {
    return 0.;
  }

  return (f_hi - f_lo) / (z_hi - z_lo);
}

static int thermodynamics_hyrec_check_parameter_bounds(struct background * pba,
                                                       struct thermohyrec * phy) {
  class_test((isfinite(pba->H0) == 0) || (pba->H0 <= 0.) || (pba->H0 > 200.),
             phy->error_message,
             "HyRec wrapper sanity bound failed: H0=%g is outside the accepted range (0,200].",
             pba->H0);

  class_test((isfinite(pba->Omega0_k) == 0) || (fabs(pba->Omega0_k) > 1.0),
             phy->error_message,
             "HyRec wrapper sanity bound failed: Omega_k=%g is outside the accepted range [-1,1].",
             pba->Omega0_k);

  class_test((isfinite(phy->data->cosmo->T0) == 0) || (phy->data->cosmo->T0 <= 0.),
             phy->error_message,
             "HyRec wrapper sanity bound failed: T0=%g K must be positive and finite.",
             phy->data->cosmo->T0);

  class_test((isfinite(phy->data->cosmo->obh2) == 0) ||
             (phy->data->cosmo->obh2 <= 0.) ||
             (phy->data->cosmo->obh2 >= 1.0),
             phy->error_message,
             "HyRec wrapper sanity bound failed: obh2=%g must lie in (0,1).",
             phy->data->cosmo->obh2);

  class_test((isfinite(phy->data->cosmo->ocbh2) == 0) ||
             (phy->data->cosmo->ocbh2 <= 0.) ||
             (phy->data->cosmo->ocbh2 >= 2.0),
             phy->error_message,
             "HyRec wrapper sanity bound failed: ocbh2=%g must lie in (0,2).",
             phy->data->cosmo->ocbh2);

  return _SUCCESS_;
}

static int thermodynamics_hyrec_check_clean_injection_state(struct thermodynamics * pth,
                                                            struct thermohyrec * phy,
                                                            const char * stage) {
  const double tol = 1e-14;
  double expected_odmh2;
  INJ_PARAMS * inj = phy->data->cosmo->inj_params;

  if (pth->has_exotic_injection == _TRUE_) {
    return _SUCCESS_;
  }

  expected_odmh2 = phy->data->cosmo->ocbh2 - phy->data->cosmo->obh2;

  class_test(fabs(inj->pann) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: pann=%g should be zero without exotic injection.",
             stage,
             inj->pann);
  class_test(fabs(inj->pann_halo) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: pann_halo=%g should be zero without exotic injection.",
             stage,
             inj->pann_halo);
  class_test(fabs(inj->decay) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: decay=%g should be zero without exotic injection.",
             stage,
             inj->decay);
  class_test(fabs(inj->fpbh) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: fpbh=%g should be zero without exotic injection.",
             stage,
             inj->fpbh);
  class_test(fabs(inj->ion) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: ion=%g should be zero without exotic injection.",
             stage,
             inj->ion);
  class_test(fabs(inj->exclya) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: exclya=%g should be zero without exotic injection.",
             stage,
             inj->exclya);
  class_test(fabs(inj->ann_z - 1.0) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: ann_z=%g should equal 1.",
             stage,
             inj->ann_z);
  class_test(fabs(inj->ann_zmax - 1.0) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: ann_zmax=%g should equal 1.",
             stage,
             inj->ann_zmax);
  class_test(fabs(inj->ann_zmin - 1.0) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: ann_zmin=%g should equal 1.",
             stage,
             inj->ann_zmin);
  class_test(fabs(inj->ann_var - 1.0) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: ann_var=%g should equal 1.",
             stage,
             inj->ann_var);
  class_test(fabs(inj->ann_z_halo - 1.0) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: ann_z_halo=%g should equal 1.",
             stage,
             inj->ann_z_halo);
  class_test(fabs(inj->Mpbh - 1.0) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: Mpbh=%g should equal 1.",
             stage,
             inj->Mpbh);
  class_test(inj->on_the_spot != 1,
             phy->error_message,
             "HyRec clean-state check failed at %s: on_the_spot=%d should equal 1.",
             stage,
             inj->on_the_spot);
  class_test(fabs(inj->odmh2 - expected_odmh2) > tol,
             phy->error_message,
             "HyRec clean-state check failed at %s: odmh2=%g disagrees with ocbh2-obh2=%g.",
             stage,
             inj->odmh2,
             expected_odmh2);

  return _SUCCESS_;
}


/**
 * Initialize the thermohyrec structure, and in particular HyRec 2020.
 *
 * @param ppr   Input: pointer to precision structure
 * @param pba   Input: pointer to background structure
 * @param pth   Input: pointer to thermodynamics structure
 * @param phy Input/Output: pointer to thermohyrec structure
 * @return the error status
 */
int thermodynamics_hyrec_init(struct precision* ppr, struct background * pba, struct thermodynamics * pth, double Nnow, double T_cmb, double fHe, double zstart_hyrec, struct thermohyrec* phy){

  /** Summary: */
  int runtime_model = (pth->io_recombination_use_full_hyrec == _TRUE_) ? FULL : MODEL;

  if(phy->thermohyrec_verbose > 0){
    printf(" -> Using the hyrec wrapper programmed by Nils Sch. (Oct2020)\n");
    printf("    implements HyRec2 version Oct 2020 by Yacine Ali-Haimoud, Chris Hirata, and Nanoom Lee\n");
  }

  /** - allocate necessary data structures */
  class_alloc(phy->data,
              sizeof(HYREC_DATA),
              phy->error_message);

  phy->zend = 0.;
  phy->zstart = zstart_hyrec;
  phy->full_history_ready = _FALSE_;

  if(phy->thermohyrec_verbose > 1){
    printf("    Starting HyRec at z = %.10e until z = %.10e\n",phy->zstart, phy->zend);
  }

  /** - pass the path to the hyrec files */
  class_sprintf(phy->path_to_hyrec,"%s%s",ppr->base_path,ppr->hyrec_path);
  phy->data->path_to_hyrec = phy->path_to_hyrec; // Just a pointer assignment
  /** - allocate hyrec internally */
  hyrec_allocate(phy->data, phy->zstart, phy->zend, runtime_model);
  /* Error during allocation */
  if(phy->data->error != 0){
    class_call_message(phy->error_message,"hyrec_allocate",phy->data->error_message);
    return _FAILURE_;
  }

  /** - set cosmological parameters for hyrec */
  phy->data->cosmo->T0 = T_cmb;
  phy->data->cosmo->obh2 = pba->Omega0_b*pba->h*pba->h;
  phy->data->cosmo->ocbh2 = pba->Omega0_nfsm*pba->h*pba->h;

  phy->data->cosmo->YHe = pth->YHe;
  phy->data->cosmo->Neff = pba->Neff;
  phy->data->cosmo->fHe = fHe; /* abundance of helium relative to hydrogen by number */
  phy->data->cosmo->fsR = 1.;
  phy->data->cosmo->meR = 1.;
  phy->data->cosmo->nH0 = Nnow*1e-6;
  phy->data->cosmo->dlna = (runtime_model == FULL) ? DLNA_HYREC : DLNA_SWIFT;
  phy->data->cosmo->inj_params->pann = 0.;
  phy->data->cosmo->inj_params->pann_halo = 0.;
  phy->data->cosmo->inj_params->ann_z = 1.;
  phy->data->cosmo->inj_params->ann_zmax = 1.;
  phy->data->cosmo->inj_params->ann_zmin = 1.;
  phy->data->cosmo->inj_params->ann_var = 1.;
  phy->data->cosmo->inj_params->ann_z_halo = 1.;
  phy->data->cosmo->inj_params->decay = 0.;
  phy->data->cosmo->inj_params->Mpbh = 1.;
  phy->data->cosmo->inj_params->fpbh = 0.;
  phy->data->cosmo->inj_params->on_the_spot = 1;
  phy->data->cosmo->inj_params->ion = 0.;
  phy->data->cosmo->inj_params->exclya = 0.;
  phy->data->cosmo->inj_params->odmh2 = (phy->data->cosmo->ocbh2 - phy->data->cosmo->obh2);

  class_call(thermodynamics_hyrec_check_parameter_bounds(pba, phy),
             phy->error_message,
             phy->error_message);
  class_call(thermodynamics_hyrec_check_clean_injection_state(pth, phy, "hyrec_init"),
             phy->error_message,
             phy->error_message);

  if (runtime_model == FULL) {
    /* Mirror the native HYREC initialization of the radiative-transfer history
       grid so the wrapper can address the stored distortion arrays coherently. */
    phy->data->rad->iz_rad_0 =
      (long) floor(1. + log(kBoltz*phy->data->cosmo->T0/square(phy->data->cosmo->fsR)/phy->data->cosmo->meR*(1.+phy->zstart)/TR_MAX)/phy->data->cosmo->dlna);
    phy->data->rad->z0 =
      (1.+phy->zstart)*exp(-phy->data->rad->iz_rad_0 * phy->data->cosmo->dlna) - 1.;
  }

  /** - set other parameters for hyrec */
  /* XEII_MIN = 1e-6 defined in history.h
     HYREC-2 calculates Helium recombinations only until xHeII ~ XEII_MIN */
  phy->xHeII_limit = XHEII_MIN;

  return _SUCCESS_;
}


/**
 * Free all memory space allocated by thermodynamics_hyrec_init
 *
 * @param pth Input/Output: pointer to thermohyrec structure (to be freed)
 * @return the error status
 */
int thermodynamics_hyrec_free(struct thermohyrec* phy){

  /* We just need to free hyrec (without error management) */
  hyrec_free(phy->data);
  free(phy->data);

  return _SUCCESS_;
}

int thermodynamics_hyrec_prepare_full_history(struct precision* ppr,
                                              struct background * pba,
                                              struct thermodynamics * pth,
                                              struct thermohyrec* phy) {

  long i;
  int last_index_back = 0;
  double *pvecback;
  double *hubble_array;
  double z, dz, H_phys, original_T0;

  if (phy->data->runtime_model != FULL) {
    return _SUCCESS_;
  }

  class_alloc(pvecback,
              pba->bg_size * sizeof(double),
              phy->error_message);

  class_alloc(hubble_array,
              phy->data->Nz * sizeof(double),
              phy->error_message);

  dz = phy->zstart / phy->data->Nz;

  for (i=0; i<phy->data->Nz; i++) {
    z = i * dz;
    class_call(background_at_z(pba,
                               z,
                               long_info,
                               inter_normal,
                               &last_index_back,
                               pvecback),
               pba->error_message,
               phy->error_message);

    H_phys = pvecback[pba->index_bg_H] * _c_ / _Mpc_over_m_;
    if ((z > ppr->reionization_z_start_max) &&
        (pth->io_recombination_local_hubble == _TRUE_) &&
        (thermodynamics_hyrec_gamma_active(pth) == _TRUE_)) {
      H_phys = thermodynamics_hyrec_local_hubble(pth, z);
    }
    hubble_array[i] = H_phys;
  }

  phy->data->error = 0;
  class_sprintf(phy->data->error_message, "\n**** ERROR HAS OCCURRED in HYREC-2 ****\n");

  class_call(thermodynamics_hyrec_check_clean_injection_state(pth, phy, "pre_full_history_build"),
             phy->error_message,
             phy->error_message);

  original_T0 = phy->data->cosmo->T0;
  if ((pth->io_recombination_use_tio_temperature == _TRUE_) &&
      (thermodynamics_hyrec_gamma_active(pth) == _TRUE_)) {
    phy->data->cosmo->T0 = original_T0 * thermodynamics_hyrec_tio_factor(pth);
  }

  class_call_message(phy->error_message,
                     "rec_build_history",
                     rec_build_history(phy->data, FULL, hubble_array));

  phy->data->cosmo->T0 = original_T0;

  if (phy->data->error != 0) {
    free(hubble_array);
    free(pvecback);
    class_call_message(phy->error_message, "rec_build_history", phy->data->error_message);
    return _FAILURE_;
  }

  phy->full_history_ready = _TRUE_;

  class_call(thermodynamics_hyrec_check_clean_injection_state(pth, phy, "post_full_history_build"),
             phy->error_message,
             phy->error_message);

  free(hubble_array);
  free(pvecback);

  return _SUCCESS_;
}

int thermodynamics_hyrec_get_full_state(struct thermohyrec * phy,
                                        double z,
                                        double * x_H,
                                        double * x_He,
                                        double * x_e,
                                        double * T_m) {
  class_test(phy->full_history_ready == _FALSE_,
             phy->error_message,
             "requested FULL HyRec state interpolation before precomputing the FULL history");

  if (x_H != NULL) {
    *x_H = hyrec_xHII(z, phy->data);
  }
  if (x_He != NULL) {
    *x_He = hyrec_xHeII(z, phy->data);
  }
  if (x_e != NULL) {
    *x_e = hyrec_xe(z, phy->data);
  }
  if (T_m != NULL) {
    *T_m = hyrec_Tm(z, phy->data);
  }

  return _SUCCESS_;
}

int thermodynamics_hyrec_get_full_derivs(struct thermohyrec * phy,
                                         double z,
                                         double * dx_H_dz,
                                         double * dx_He_dz,
                                         double * dx_e_dz,
                                         double * dT_m_dz) {
  class_test(phy->full_history_ready == _FALSE_,
             phy->error_message,
             "requested FULL HyRec derivative interpolation before precomputing the FULL history");

  if (dx_H_dz != NULL) {
    *dx_H_dz = thermodynamics_hyrec_interp_table_dz(z, phy->data->xH_output, phy->data);
  }
  if (dx_He_dz != NULL) {
    *dx_He_dz = thermodynamics_hyrec_interp_table_dz(z, phy->data->xHe_output, phy->data);
  }
  if (dx_e_dz != NULL) {
    *dx_e_dz = thermodynamics_hyrec_interp_table_dz(z, phy->data->xe_output, phy->data);
  }
  if (dT_m_dz != NULL) {
    *dT_m_dz = thermodynamics_hyrec_interp_table_dz(z, phy->data->Tm_output, phy->data);
  }

  return _SUCCESS_;
}

/**
 * Calculate the derivative of the hydrogen HII ionization fraction
 *
 * @param pth   Input: pointer to thermodynamics structure
 * @param phy   Input: pointer to thermohyrec structure
 * @param x_H   Input: hydrogen HII ionization fraction
 * @param x_He  Input: helium HeIII ionization fraction
 * @param nH    Input: comoving total number of hydrogen atoms
 * @param z     Input: current cosmological redshift
 * @param Hz    Input: current value of hubble parameter in 1/s
 * @param Tmat  Input: temperature of baryons in Kelvin
 * @param Trad  Input: temperature of photons in Kelvin
 * @param alpha Input: fine structure constant relative to today
 * @param me    Input: effective electron mass relative to today
 * @param dx_H_dz        Output: change in ionization fraction of hydrogen HII
 * @return the error status
 */
int hyrec_dx_H_dz(struct thermodynamics* pth, struct thermohyrec* phy, double x_H, double x_He, double xe, double nH, double z, double Hz, double Tmat, double Trad, double alpha, double me, double *dx_H_dz) {

  /** Summary: */

  /** - define local variables */
  struct injection* pin = &(pth->in);
  long iz = 0;
  int model;
  double Trad_phys;

  if (phy->full_history_ready == _TRUE_) {
    class_call(thermodynamics_hyrec_get_full_derivs(phy,
                                                    z,
                                                    dx_H_dz,
                                                    NULL,
                                                    NULL,
                                                    NULL),
               phy->error_message,
               phy->error_message);
    return _SUCCESS_;
  }

  /** - assign variables */
  if (pth->has_exotic_injection == _TRUE_) {
    phy->data->cosmo->inj_params->ion = pin->pvecdeposition[pin->index_dep_ionH]/nH/(_E_H_ion_*_eV_);
    phy->data->cosmo->inj_params->exclya = pin->pvecdeposition[pin->index_dep_lya]/nH/(_E_H_lya_*_eV_);
  }
  else{
    phy->data->cosmo->inj_params->ion = 0.;
    phy->data->cosmo->inj_params->exclya = 0.;
  }
  if (pth->has_varconst == _TRUE_) {
    phy->data->cosmo->fsR = alpha;
    phy->data->cosmo->meR = me;
  }

  Trad_phys = Trad*kBoltz;
  if (pth->has_varconst == _TRUE_) {
    Trad_phys /= phy->data->cosmo->fsR*phy->data->cosmo->fsR*phy->data->cosmo->meR; //According to 1705.03925
  }

  if (Trad_phys <= TR_MIN || Tmat/Trad <= T_RATIO_MIN) { model = PEEBLES; }
  else { model = phy->data->runtime_model; }

  if (model == FULL) {
    /* FULL mode carries a one-decade distortion-history buffer indexed relative
       to the redshift z0 where radiative transfer starts. The wrapper used to
       hard-code iz=0, which collapsed the history interpolation to its thermal
       fallback branch. Use the causal history index instead. */
    double raw_iz;
    long iz_max;

    if (z <= phy->data->rad->z0) {
      raw_iz = log((1.+phy->data->rad->z0)/(1.+z))/phy->data->cosmo->dlna;
      /* The thermodynamics ODE solver evaluates between the native HYREC
         history slices. FULL radiative transfer needs enough stored history to
         cover the current redshift, so round upward rather than downward. */
      iz = (long) ceil(raw_iz - 1.e-12);
      if (iz < 0) iz = 0;
      iz_max = (long) (log(10.)/phy->data->cosmo->dlna) - 1;
      if (iz > iz_max) iz = iz_max;
    }
  }

  /** - convert to correct units, and retrieve derivative */
  *dx_H_dz = -1./(1.+z)* rec_dxHIIdlna(phy->data, model, xe, x_H, nH*1e-6, Hz, Tmat*kBoltz, Trad*kBoltz, iz, z);

  /** - do error management */
  if(phy->data->error != 0){
    class_call_message(phy->error_message,"rec_dxHIIdlna",phy->data->error_message);
    return _FAILURE_;
  }

  return _SUCCESS_;
}

/**
 * Calculate the derivative of the helium HeIII ionization fraction
 *
 * @param pth   Input: pointer to thermodynamics structure
 * @param phy   Input: pointer to thermohyrec structure
 * @param x_H   Input: hydrogen HII ionization fraction
 * @param x_He  Input: helium HeIII ionization fraction
 * @param xe    Input: sum total ionization fraction
 * @param nH    Input: comoving total number of hydrogen atoms
 * @param z     Input: current cosmological redshift
 * @param Hz    Input: current value of hubble parameter in 1/s
 * @param Tmat  Input: temperature of baryons in Kelvin
 * @param Trad  Input: temperature of photons in Kelvin
 * @param alpha Input: fine structure constant relative to today
 * @param me    Input: effective electron mass relative to today
 * @param dx_He_dz       Output: change in ionization fraction of helium HeIII
 * @return the error status
 */
int hyrec_dx_He_dz(struct thermodynamics* pth, struct thermohyrec* phy, double x_H, double x_He, double xe, double nH, double z, double Hz, double Tmat, double Trad, double alpha, double me, double *dx_He_dz) {

  /** Summary: */

  /** - define local variables */
  struct injection* pin = &(pth->in);
  double xHeII = x_He*phy->data->cosmo->fHe;    // Different definitions between CLASS and HYREC-2

  if (phy->full_history_ready == _TRUE_) {
    class_call(thermodynamics_hyrec_get_full_derivs(phy,
                                                    z,
                                                    NULL,
                                                    dx_He_dz,
                                                    NULL,
                                                    NULL),
               phy->error_message,
               phy->error_message);
    return _SUCCESS_;
  }

  /** - assign variables */
  if (pth->has_exotic_injection == _TRUE_) {
    phy->data->cosmo->inj_params->ion = pin->pvecdeposition[pin->index_dep_ionHe]/nH/(_E_H_ion_*_eV_);
    phy->data->cosmo->inj_params->exclya = pin->pvecdeposition[pin->index_dep_lya]/nH/(_E_H_lya_*_eV_);
  }
  else{
    phy->data->cosmo->inj_params->ion = 0.;
    phy->data->cosmo->inj_params->exclya = 0.;
  }
  if (pth->has_varconst == _TRUE_) {
    phy->data->cosmo->fsR = alpha;
    phy->data->cosmo->meR = me;
  }

  if (xHeII<phy->xHeII_limit) {
    /** - don't evolve He below the limit */
    *dx_He_dz=0;
  }
  else {

    /** - convert to correct units, and retrieve derivative */
    *dx_He_dz = -1./(1.+z)* rec_helium_dxHeIIdlna(phy->data, z, 1.-x_H, xHeII, Hz) / phy->data->cosmo->fHe;

    /** - do error management */
    if(phy->data->error != 0){
      class_call_message(phy->error_message,"rec_helium_dxHeIIdlna",phy->data->error_message);
      return _FAILURE_;
    }
  }

  return _SUCCESS_;
}
