/** @file modgrav.c Modified gravity functions module
 *
 * Phil Bull, 19.02.2015
 * Ziad Sakr, 2021
 *
 * Modified gravity function definitions and MG utilities.
 *
 * This module defines the modified gravity functions, mutilde(k, a) and 
 * gamma(k, a), which parametrise modifications to the Poisson equation 
 * and slip relation respectively. Both are general functions of scale and 
 * redshift that can be chosen essentially arbitrarily.
 *
 * The modgrav_functions() function returns the MG functions and their 
 * derivatives w.r.t. conformal time.
 *
 */

#include "modgrav.h"

int modgrav_bckg_test(int * mg_bckg_test_enabled) {
  * mg_bckg_test_enabled = 1;
  return _SUCCESS_;
}


int modgrav_test(int * mg_test_enabled) {
  * mg_test_enabled = 1;
  return _SUCCESS_;
}

int modgrav_init(struct background * pba,
                 struct modgrav * pmg
                 ){


double omegaDEdot_0, rho_tot_0;

  rho_tot_0 = (pba->Omega0_g +pba->Omega0_b +pba->Omega0_cdm +pba->Omega0_ncdm_tot) * pow(pba->H0,2); 
  omegaDEdot_0 = -2.0* 1.0 * (-1.5*rho_tot_0) / pba->H0; 

// calculated as if c1 = c2 = 1 but even if not, equations behave as if they were for low k.
 
if (pba->mg_ansatz == plk_early) {

      if (pba->mg_bckg == _TRUE_){

              pmg->mu_0 = 1.0 + pba->mg_E11 ;
    	      pmg->gamma_0 = 1.0 + pba->mg_E21 ;
              pmg->mu_dot_0 = - pba->mg_E12 * pba->H0;
              pmg->gamma_dot_0 = - pba->mg_E22 * pba->H0;

             }

}

else if (pba->mg_ansatz == plk_norm_late) { 

          if (pba->mg_bckg == _TRUE_){

              pmg->mu_0 = 1.0 +pba->mg_E11 ;
              pmg->gamma_0 = 1.0 +pba->mg_E22 ;
              pmg->mu_dot_0 = pba->mg_E11 * omegaDEdot_0;
              pmg->gamma_dot_0 = pba->mg_E22 * omegaDEdot_0;

             }    
    
   }

else if (pba->mg_ansatz == z_flex_early) { 
     
	
      if (pba->mg_bckg == _TRUE_){

              pmg->mu_0 = 1.0  ;
    	      pmg->gamma_0 = 1.0  ;
              pmg->mu_dot_0 = 0.0;
              pmg->gamma_dot_0 = 0.0;

             }
   }

else if (pba->mg_ansatz == z_xpans_early) { 
     
	
      if (pba->mg_bckg == _TRUE_){

              pmg->mu_0 = 1.0  ;
    	      pmg->gamma_0 = 1.0  ;
              pmg->mu_dot_0 = 0.0;
              pmg->gamma_dot_0 = 0.0;

             }
   }


else if (pba->mg_ansatz == z_flex_norm_late) { 
     
	if (pba->mg_bckg == _TRUE_){

              pmg->mu_0 = 1.0  ;
    	      pmg->gamma_0 = 1.0  ;
              pmg->mu_dot_0 = -pba->mg_muz*omegaDEdot_0*pba->mg_zzn;
              pmg->gamma_dot_0 = -pba->mg_gamz*omegaDEdot_0*pba->mg_zzn;

             }
     
   }


}

/*
 * Return values of modified gravity functions mu and gamma and their 
 * derivatives w.r.t. conformal time at given (tau, k).
 * 
 * @param pba               Input : Pointer to background structure
 * @param pvecback          Input : Pointer to (initialised) vector of 
                                    background quantities
 * @param k                 Input : Wavenumber, k
 * @param tau               Input : Conformal time, tau
 * @param pmg               Output: Struct containing values of MG functions
 * @return the error status
 */
int modgrav_functions(
                 struct background * pba,
                 double * pvecback,
                 double k,
                 double tau,
                 struct modgrav * pmg
                 ) {
  
  // Useful background quantities
  double a, H, aH, aHdot, Hdot, Ez, rho_m, rho_r,omegaM, omegaMdot,omegaDE, omegaDEdot, omegaDEdotdot, Hdotdot,omegaDEz, omegaDEzdot;
  double p1, p2, q2, t1, t2, M0, kappa2, M2_over_k2;
  double x, y, fz_mu, fz_gam, gk, gkdot_over_gk, cutoff, cutoffdot_over_cutoff;
  double CUTOFF_ZMAX, CUTOFF_WIDTH,mu_scale_part,mu_scale_part_dot,mu_scale_part_dot_dot,gamma_scale_part,gamma_scale_part_dot,gamma_scale_part_dot_dot,mgSigma_scale_part,mgSigma_scale_part_dot,mgSigma,mgSigmadot;
  
  double  M2_over_k2_dot, A6,A6_dot,B6,B6_dot,B7,B7_dot,B8,D9,D9_dot,a_M,a_M_dot,a_b,a_b_dot,a_b_dlna,a_b_dlna_dot,M_star,mu_Mstarderiv,mu_notMstarderiv;
  double  A1,A2,QR_kc,FRm0,MGM,dMGModt,Beta,Betadot,beta0,dt1odt,dt2odt,wJBD,phi_jbd,b_nDGP,rc,g0xphi0,d_JBD,ga,phi_jbd_dot,A_kmfl,X_kmfl,k_prime_mfl,epsl1_kmfl,X_kmfl_dot;
  //double pba->Omega0_lambda ;
  double Omega0_ncdm = 0.0 ;
 
  // Set high-z cutoff properties
  CUTOFF_ZMAX = 6.0;
  CUTOFF_WIDTH = 5e-3;
  
  // Define useful background quantities
  a = pvecback[pba->index_bg_a];
  H = pvecback[pba->index_bg_H]; // H = H/c, i.e. it's in units of Mpc^-1
  Hdot = pvecback[pba->index_bg_H_prime]; // dH/d(eta)
  aHdot = aH*aH + a*Hdot; // d(aH)/d(eta)
  
  Ez = H / pba->H0;
  aH = a * H;
  
  // Get total matter density in H^2 units, i.e. 'rho_m' = 8piG/3 rho_m(t_i)
  rho_m = pvecback[pba->index_bg_rho_b];
  if (pba->has_cdm == _TRUE_) { rho_m += pvecback[pba->index_bg_rho_cdm]; }
  if (pba->has_dcdm == _TRUE_){ rho_m += pvecback[pba->index_bg_rho_dcdm];}
  if (pba->has_ncdm == _TRUE_){ 
      int n_ncdm ;
      for(n_ncdm=0; n_ncdm<pba->N_ncdm; n_ncdm++){rho_m += pvecback[pba->index_bg_rho_ncdm1+n_ncdm]- pvecback[pba->index_bg_p_ncdm1+n_ncdm]; Omega0_ncdm += pba->Omega0_ncdm[n_ncdm];}} 
  rho_r = pvecback[pba->index_bg_rho_g]+pvecback[pba->index_bg_rho_ur];
  

  Hdotdot = ((3./2.) * (rho_m ) + (4./2.) * (rho_r ) )*pvecback[pba->index_bg_H]*a -2.*pvecback[pba->index_bg_H_prime]*pvecback[pba->index_bg_H];

  omegaDE = 1. / Ez / Ez; // = Omega_DE(a) / Omega_DE(a=1)
  omegaDEdot = -2.0* omegaDE * Hdot / H;
  omegaDEdotdot =  ( -2.0*H* (omegaDEdot*Hdot + omegaDE*Hdotdot  ) + 2.0* omegaDE*Hdot*Hdot   )/ (H*H);


  // Get Omega_DE(a) / Omega_DE(a=1)
  // FIXME: assumes Lambda only for now (i.e. Omega_fld is ignored)
  /*omegaDE = 0.; omegaDEdot = 0.;
  if (pba->has_lambda == _TRUE_) {
    omegaDE = 1. / Ez / Ez; // = Omega_DE(a) / Omega_DE(a=1)
    omegaDEdot = -2* omegaDE * Hdot / H;
  }*/
    
  // Calculate modified gravity functions (choose which ansatz to use)
  
  if (pba->mg_ansatz == EFT_alpha_QSL) { // based on 1404.3713 and 2003.10453

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

    // EFT alpha -inspired ansatz
    a_M = pba->mg_EFT_alpha_M*omegaDE;
    M_star = exp((log(pba->Omega0_cdm+pba->Omega0_lambda)/(6.0*pba->Omega0_lambda))*pba->mg_EFT_alpha_M);

    if (pba->mg_no_lens == _TRUE_) { a_b = (0.25 *(-2.0 + 4.0 *(M_star*M_star) - a_M - 4.0 *(M_star*M_star) *a_M - sqrt(pow((2.0 - 4.0 *(M_star*M_star) + a_M + 4.0 *(M_star*M_star) *a_M),2.0) - 8.0 *(M_star*M_star)* (2.0 *a_b_dlna - 4.0 *a_b_dlna *(M_star*M_star) + 4.0 *a_M - 8.0 *(M_star*M_star) *a_M + 2.0 *a_M*a_M))))/(M_star*M_star); pba->mg_EFT_alpha_b = a_b /omegaDE  ; }

    a_M_dot = pba->mg_EFT_alpha_M*omegaDEdot; 
    a_b = pba->mg_EFT_alpha_b*omegaDE;
    a_b_dot = pba->mg_EFT_alpha_b*omegaDEdot;
    a_b_dlna = pba->mg_EFT_alpha_b*omegaDEdot/aH;
    a_b_dlna_dot = pba->mg_EFT_alpha_b*(omegaDEdotdot/aH -(aHdot/(aH*aH))*omegaDEdot);
    
    // mu and gamma
    pmg->mu    = 2.0*(a_b+2.0*a_M+a_b_dlna)
                 /((2.0-a_b)*(a_b+2.0*a_M)+2.0*a_b_dlna);
    pmg->mu    *= 1.0/(M_star*M_star);
     
    pmg->gamma = ((2.0+2.0*a_M)*(a_b+2.0*a_M)+2.0*a_b_dlna) 
                /((2.0)*(a_b+2.0*a_M)+2.0*a_b_dlna);

    mu_Mstarderiv    = - (H/(3.0*pba->Omega0_lambda)*pba->mg_EFT_alpha_M *  M_star) /  pow(M_star,4.0);  
    mu_notMstarderiv = (a_b_dlna_dot+a_b_dot+2.0*a_M_dot)/(2.0* a_b_dlna+(2.0-a_b)*(a_b+2.0*a_M))
-((a_b_dlna+a_b+2.0*a_M)* (2.0*a_b_dlna_dot-(a_b+2.0*a_M)*a_b_dot+ (2.0-a_b)*(a_b_dot+2.0* a_M_dot)))
/(pow(2.0*a_b_dlna+(2-a_b)*(a_b+2.0*a_M),2.0));
    mu_notMstarderiv *= 2.0;

    pmg->mu_dot =  mu_Mstarderiv * (pmg->mu*(M_star*M_star) ) + mu_notMstarderiv * 1.0/(M_star*M_star);    
 
   
    pmg->gamma_dot = -(2.0*a_b_dlna+(2.0+2.0*a_M)* (a_b+2.0*a_M)) *(2.0* a_b_dlna_dot + (2.0)*(a_b_dot+2.0*a_M_dot))
/pow(2.0*a_b_dlna+(2.0)*(a_b+2.0*a_M),2.0)
+(2.0*a_b_dlna_dot+2.0*(a_b+2.0*a_M)* a_M_dot+(2.0+2.0*a_M) *(a_b_dot+2.0*a_M_dot))
/(2.0*a_b_dlna+(2.0)*(a_b+2.0*a_M));
  
    
  }
  else if (pba->mg_ansatz == EFT_alpha_QSE) { // based on 1404.3713 and 2003.10453

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

    // EFT alpha -inspired ansatz
    a_M = pba->mg_EFT_alpha_M*(1.0-a+1.e-6);
    M_star = exp((log(a)-a)*0.5*pba->mg_EFT_alpha_M);
   
    if (pba->mg_no_lens == _TRUE_) { a_b = (0.25 *(-2.0 + 4.0 *(M_star*M_star) - a_M - 4.0 *(M_star*M_star) *a_M - sqrt(pow((2.0 - 4.0 *(M_star*M_star) + a_M + 4.0 *(M_star*M_star) *a_M),2.0) - 8.0 *(M_star*M_star) *(2.0 *a_b_dlna - 4.0 *a_b_dlna *(M_star*M_star) + 4.0 *a_M - 8.0 *(M_star*M_star) *a_M + 2.0 *a_M*a_M))))/(M_star*M_star) ; 
pba->mg_EFT_alpha_b = a_b /(1.0-a+1.e-6)  ; }

    a_M_dot = - pba->mg_EFT_alpha_M*H*a*a; 
    a_b = pba->mg_EFT_alpha_b*(1.0-a+1.e-6);
    a_b_dot = - pba->mg_EFT_alpha_b*H*a*a;
    a_b_dlna = - pba->mg_EFT_alpha_b*a;
    a_b_dlna_dot = - pba->mg_EFT_alpha_b*H*a*a ;
    
    // mu and gamma
    pmg->mu    = 2.0*(a_b+2.0*a_M+a_b_dlna)
                 /((2.0-a_b)*(a_b+2.0*a_M)+2.0*a_b_dlna);
    pmg->mu    *= 1.0/(M_star*M_star);
     
         
    pmg->gamma = ((2.0+2.0*a_M)*(a_b+2.0*a_M)+2.0*a_b_dlna) 
                /((2.0)*(a_b+2.0*a_M)+2.0*a_b_dlna);

    mu_Mstarderiv = - 0.5*(H-aH)*pba->mg_EFT_alpha_M*M_star /  pow(M_star,4.0);
    mu_notMstarderiv = (a_b_dlna_dot+a_b_dot+2.0*a_M_dot)/(2.0* a_b_dlna+(2.0-a_b)*(a_b+2.0*a_M))
-((a_b_dlna+a_b+2.0*a_M)* (2.0*a_b_dlna_dot-(a_b+2.0*a_M)*a_b_dot+ (2.0-a_b)*(a_b_dot+2.0* a_M_dot)))
/(pow(2.0*a_b_dlna+(2-a_b)*(a_b+2.0*a_M),2.0));
    mu_notMstarderiv *= 2.0;

    pmg->mu_dot = mu_Mstarderiv * (pmg->mu*(M_star*M_star) ) + mu_notMstarderiv * 1.0/(M_star*M_star);
    
       
 
    pmg->gamma_dot = -(2.0*a_b_dlna+(2.0+2.0*a_M)* (a_b+2.0*a_M)) *(2.0* a_b_dlna_dot + (2.0)*(a_b_dot+2.0*a_M_dot))
/pow(2.0*a_b_dlna+(2.0)*(a_b+2.0*a_M),2.0)
+(2.0*a_b_dlna_dot+2.0*(a_b+2.0*a_M)* a_M_dot+(2.0+2.0*a_M) *(a_b_dot+2.0*a_M_dot))
/(2.0*a_b_dlna+(2.0)*(a_b+2.0*a_M));
  
    
  }
  else if (pba->mg_ansatz == horndeski) { // based on 1210.0439 and 1302.1193

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

if (pba->mg_no_lens == _TRUE_) 

class_stop(pba->error_message,"mg_no_lens option is not yet implemented for this model.");
    
    // Horndeski-inspired ansatz
    p1 = pba->mg_horndeski_p1; p2 = pba->mg_horndeski_p2;
    t1 = pba->mg_horndeski_t1; t2 = pba->mg_horndeski_t2;
    q2 = pba->mg_horndeski_q2; M0 = pba->mg_horndeski_M;
    M2_over_k2 = M0 * M0 * aH * aH / k / k;
    kappa2 = k / (a * M0 * pba->H0); // Note: H0 includes factor of C
    kappa2 *= kappa2;
    
    // mu and gamma
    pmg->mu    = (1. + q2 * omegaDE * M2_over_k2) 
               / (t1 + t2 * omegaDE * M2_over_k2);
    pmg->gamma = (p1 + p2 * omegaDE * M2_over_k2) 
               / (1. + q2 * omegaDE * M2_over_k2);
    
    // Conformal time derivatives of mu and gamma (need to handle zeros carefully)
    pmg->mu_dot = 0.; pmg->gamma_dot = 0.;
    if (q2 != 0.){
        pmg->mu_dot    +=  1. / ( 1. + kappa2/q2 );
        pmg->gamma_dot += -1. / ( 1. + kappa2/q2 );
    }
    if (p2 != 0.) pmg->gamma_dot +=  1. / (1. + (p1/p2)*kappa2);
    if (t2 != 0.) pmg->mu_dot    += -1. / (1. + (t1/t2)*kappa2);
    pmg->mu_dot *= 2.*aH*pmg->mu; pmg->gamma_dot *= 2.*aH*pmg->gamma;
    
  } 

else if (pba->mg_ansatz == mgtanh) { // based on 1501.03119

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");
    
    // Ansatz where mu and gamma are given by a tanh function, interpolating 
    // between large and small scales
    
    // Arguments of geometric functions
    p1 = (aH - k) / pba->mg_tanh_Wmu;
    p2 = (aH - k) / pba->mg_tanh_Wgam;
    
    // mu, gamma
    pmg->mu    = 1. + pba->mg_tanh_Bmu  * omegaDE * ( 1. + tanh(p1) );
    pmg->gamma = 1. + pba->mg_tanh_Bgam * omegaDE * ( 1. + tanh(p2) );
    
    // Conformal time derivatives
    pmg->mu_dot    = pba->mg_tanh_Bmu * ( 
                       omegaDEdot * ( 1. + tanh(p1) )
                     + omegaDE * (Hdot / pba->mg_tanh_Wmu / cosh(p1) / cosh(p1))
                     );
    pmg->gamma_dot = pba->mg_tanh_Bgam * ( 
                       omegaDEdot * ( 1. + tanh(p2) )
                     + omegaDE * (Hdot / pba->mg_tanh_Wgam / cosh(p2) / cosh(p2))
                     );
  
  } else if (pba->mg_ansatz == omegade) { // based on 1506.00641 and 1502.01590 and the introduction of the cutoff from 1109.4583
    
if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

    // Ansatz where mu and gamma have a simplified Horndeski scale dependence, 
    // and a redshift evolution proportional to Omega_DE(a). There is also a 
    // cutoff tanh function at high redshift.
    
    // Horndeski-like scale dependent function
    x = pba->mg_lambda * aH / k;
    gk = x*x / (1. + x*x);
    gkdot_over_gk = 2.*aHdot/aH * (1. - gk); // [dg(k,eta)/d(eta)] / g(k,eta)
    
    // High-z cutoff (tanh step function approximation)
    y = (a - 1./(1. + CUTOFF_ZMAX)) / CUTOFF_WIDTH;
    cutoff = 0.5 * ( 1. + tanh(y) );
    cutoffdot_over_cutoff = a * aH * (1. - tanh(y)) / CUTOFF_WIDTH;
    
    // mu, gamma
    pmg->mu    = 1. + pba->mg_mu_lambda  * omegaDE * gk * cutoff;
    pmg->gamma = 1. + pba->mg_gam_lambda * omegaDE * gk * cutoff;
    
    // Conformal time derivatives
    pmg->mu_dot = (pmg->mu - 1.) * 
                  (omegaDEdot/omegaDE + gkdot_over_gk + cutoffdot_over_cutoff);
    
    pmg->gamma_dot = (pmg->gamma - 1.) * 
                  (omegaDEdot/omegaDE + gkdot_over_gk + cutoffdot_over_cutoff);
  
  } else if (pba->mg_ansatz == cpl) { // based on 1506.00641 and 1502.01590 and the introduction of the cutoff from 1109.4583
    
    if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

    // Ansatz where mu and gamma have a simplified Horndeski scale dependence, 
    // and a redshift evolution proportional to a CPL-like Taylor expansion. 
    // There is also a cutoff tanh function at high redshift.
    
    // Horndeski-like scale dependent function
    x = pba->mg_lambda * aH / k;
    gk = x*x / (1. + x*x);
    gkdot_over_gk = 2.*aHdot/aH * (1. - gk); // [dg(k,eta)/d(eta)] / g(k,eta)
    
    // High-z cutoff (tanh step function approximation)
    y = (a - 1./(1. + CUTOFF_ZMAX)) / CUTOFF_WIDTH;
    cutoff = 0.5 * ( 1. + tanh(y) );
    cutoffdot_over_cutoff = a * aH * (1. - tanh(y)) / CUTOFF_WIDTH;
    
    // CPL-like redshift dependence
    fz_mu = pba->mg_mu0 + pba->mg_mu1 * (1. - a);
    fz_gam = pba->mg_gam0 + pba->mg_gam1 * (1. - a);
    
    // mu, gamma
    pmg->mu    = 1. + fz_mu * gk * cutoff;
    pmg->gamma = 1. + fz_gam * gk * cutoff;
    
    // Conformal time derivatives (1e-6 in denom. to prevent DIV/0 in GR case)
    pmg->mu_dot = (pmg->mu - 1.) * (-1. * pba->mg_mu1 * a * aH / (fz_mu + 1e-6)
                                    + gkdot_over_gk + cutoffdot_over_cutoff);
    pmg->gamma_dot = (pmg->gamma - 1.) * (-1. * pba->mg_gam1 * a * aH / (fz_gam + 1e-6)
                                    + gkdot_over_gk + cutoffdot_over_cutoff);
    
  } 


  else if (pba->mg_ansatz == plk_late) { // based on 1502.01590 and 1901.05956

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");
  
     pmg->mu = 1.0 + (pba->mg_E11 * omegaDE * pba->Omega0_lambda)*((1.0+pba->mg_c1*pow(H/k,2.0))/(1.0+pow(H/k,2.0)));
     pmg->gamma = 1.0 + (pba->mg_E22 * omegaDE * pba->Omega0_lambda)*((1.0+pba->mg_c2*pow(H/k,2.0))/(1.0+pow(H/k,2.0)));

     mu_scale_part     = (1.0+pba->mg_c1*pow(H/k,2.0))/(1.0+pow(H/k,2.0));
     mu_scale_part_dot = ( 2.0*pba->mg_c1*H/k/k*Hdot*(1.0+pow(H/k,2.0))  - 2.0*H/k*Hdot/k*(1.0+pba->mg_c1*pow(H/k,2.0)) )   /   pow(1.0+pow(H/k,2.0),2.0);
     mu_scale_part_dot_dot = (  (-2.0 +2.0*pba->mg_c1 + (6.0 -6.0*pba->mg_c1)*pow(H/k,2.0))*pow(Hdot,2.0) + (-2.0 +2.0*pba->mg_c1)*(H+k*pow(H/k,3.0))* Hdotdot ) / ( k*k*pow(1.0+pow(H/k,2.0),3.0));

     gamma_scale_part     = (1.0+pba->mg_c2*pow(H/k,2.0))/(1.0+pow(H/k,2.0));
     gamma_scale_part_dot = ( 2.0*pba->mg_c2*H/k*Hdot/k*(1.0+pow(H/k,2.0))  - 2.0*H/k*Hdot/k*(1.0+pba->mg_c2*pow(H/k,2.0)) )   /   pow(1.0+pow(H/k,2.0),2.0);
     gamma_scale_part_dot_dot = (  (-2.0 +2.0*pba->mg_c2 + (6.0 -6.0*pba->mg_c2)*pow(H/k,2.0))*pow(Hdot,2.0) + (-2.0 +2.0*pba->mg_c2)*(H+k*pow(H/k,3.0))* Hdotdot ) / ( k*k*pow(1.0+pow(H/k,2.0),3.0));

     
     pmg->mu_dot = (pba->mg_E11 * omegaDE * pba->Omega0_lambda)*mu_scale_part_dot 
                   + (pba->mg_E11 * omegaDEdot * pba->Omega0_lambda)*mu_scale_part;
     pmg->mu_dot_dot = (pba->mg_E11 * omegaDEdot * pba->Omega0_lambda)*mu_scale_part_dot 
                     + (pba->mg_E11 * omegaDE * pba->Omega0_lambda)*mu_scale_part_dot_dot
                     + (pba->mg_E11 * omegaDEdotdot * pba->Omega0_lambda)*mu_scale_part
                     + (pba->mg_E11 * omegaDEdot * pba->Omega0_lambda)*mu_scale_part_dot;

     pmg->gamma_dot = (pba->mg_E22 * omegaDE * pba->Omega0_lambda)*gamma_scale_part_dot 
                   + (pba->mg_E22 * omegaDEdot * pba->Omega0_lambda)*gamma_scale_part;
     pmg->gamma_dot_dot = (pba->mg_E22 * omegaDEdot * pba->Omega0_lambda)*gamma_scale_part_dot 
                     + (pba->mg_E22 * omegaDE * pba->Omega0_lambda)*gamma_scale_part_dot_dot
                     + (pba->mg_E22 * omegaDEdotdot * pba->Omega0_lambda)*gamma_scale_part
                     + (pba->mg_E22 * omegaDEdot * pba->Omega0_lambda)*gamma_scale_part_dot;

      
   }


else if (pba->mg_ansatz == plk_norm_late) { // based on 1502.01590 and 1901.05956
  
     pmg->mu = 1.0 + (pba->mg_E11 * omegaDE )*((1.0+pba->mg_c1*pow(H/k,2.0))/(1.0+pow(H/k,2.0)));
     pmg->gamma = 1.0 + (pba->mg_E22 * omegaDE )*((1.0+pba->mg_c2*pow(H/k,2.0))/(1.0+pow(H/k,2.0)));

     mu_scale_part     = (1.0+pba->mg_c1*pow(H/k,2.0))/(1.0+pow(H/k,2.0));
     mu_scale_part_dot = ( 2.0*pba->mg_c1*H/k/k*Hdot*(1.0+pow(H/k,2.0))  - 2.0*H/k*Hdot/k*(1.0+pba->mg_c1*pow(H/k,2.0)) )   /   pow(1.0+pow(H/k,2.0),2.0);
     mu_scale_part_dot_dot = (  (-2.0 +2.0*pba->mg_c1 + (6.0 -6.0*pba->mg_c1)*pow(H/k,2.0))*pow(Hdot,2.0) + (-2.0 +2.0*pba->mg_c1)*(H+k*pow(H/k,3.0))* Hdotdot ) / ( k*k*pow(1.0+pow(H/k,2.0),3.0));

     gamma_scale_part     = (1.0+pba->mg_c2*pow(H/k,2.0))/(1.0+pow(H/k,2.0));
     gamma_scale_part_dot = ( 2.0*pba->mg_c2*H/k*Hdot/k*(1.0+pow(H/k,2.0))  - 2.0*H/k*Hdot/k*(1.0+pba->mg_c2*pow(H/k,2.0)) )   /   pow(1.0+pow(H/k,2.0),2.0);
     gamma_scale_part_dot_dot = (  (-2.0 +2.0*pba->mg_c2 + (6.0 -6.0*pba->mg_c2)*pow(H/k,2.0))*pow(Hdot,2.0) + (-2.0 +2.0*pba->mg_c2)*(H+k*pow(H/k,3.0))* Hdotdot ) / ( k*k*pow(1.0+pow(H/k,2.0),3.0));

     
     pmg->mu_dot = (pba->mg_E11 * omegaDE )*mu_scale_part_dot 
                   + (pba->mg_E11 * omegaDEdot )*mu_scale_part;
     pmg->mu_dot_dot = (pba->mg_E11 * omegaDEdot )*mu_scale_part_dot 
                     + (pba->mg_E11 * omegaDE )*mu_scale_part_dot_dot
                     + (pba->mg_E11 * omegaDEdotdot )*mu_scale_part
                     + (pba->mg_E11 * omegaDEdot )*mu_scale_part_dot;

     pmg->gamma_dot = (pba->mg_E22 * omegaDE )*gamma_scale_part_dot 
                   + (pba->mg_E22 * omegaDEdot )*gamma_scale_part;
     pmg->gamma_dot_dot = (pba->mg_E22 * omegaDEdot )*gamma_scale_part_dot 
                     + (pba->mg_E22 * omegaDE )*gamma_scale_part_dot_dot
                     + (pba->mg_E22 * omegaDEdotdot )*gamma_scale_part
                     + (pba->mg_E22 * omegaDEdot )*gamma_scale_part_dot;

         
   }
   
   else if (pba->mg_ansatz == plk_musigma_norm_late) {
   
   if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");
   
     mu_scale_part     = (1.0+pba->mg_c1*pow(H/k,2.0))/(1.0+pow(H/k,2.0));
     mu_scale_part_dot = ( 2.0*pba->mg_c1*H/k*Hdot/k*(1.0+pow(H/k,2.0))  - 2.0*H/k*Hdot/k*(1.0+pba->mg_c1*pow(H/k,2.0)) )   /   pow(1.0+pow(H/k,2.0),2.0);

     mgSigma_scale_part     = (1.0+pba->mg_c2*pow(H/k,2.0))/(1.0+pow(H/k,2.0));
     mgSigma_scale_part_dot = ( 2.0*pba->mg_c2*H/k*Hdot/k*(1.0+pow(H/k,2.0))  - 2.0*H/k*Hdot/k*(1.0+pba->mg_c2*pow(H/k,2.0)) )   /   pow(1.0+pow(H/k,2.0),2.0);

     pmg->mu = 1. + pba->mg_E11 * omegaDE *mu_scale_part;

     pmg->mu_dot = (pba->mg_E11 * omegaDEdot )*mu_scale_part+(pba->mg_E11 * omegaDE *mu_scale_part_dot);

     mgSigma = 1. + pba->mg_E22 * omegaDE *mgSigma_scale_part;

     mgSigmadot = (pba->mg_E22 * omegaDEdot )*mgSigma_scale_part+(pba->mg_E22 * omegaDE *mgSigma_scale_part_dot);     

     if (pmg->mu == 0.0){pmg->mu = 1e-6;};
     if (mgSigma == 0.0){mgSigma = 1e-6;};

     pmg->gamma = (2*mgSigma/pmg->mu)-1;

     pmg->gamma_dot = 2*(mgSigmadot*pmg->mu-mgSigma*pmg->mu_dot)/pow(pmg->mu,2.0);

  }

  
  else if (pba->mg_ansatz == plk_early) { // based on 1502.01590
       
         
     pmg->mu = 1.0 + (pba->mg_E11 + pba->mg_E12 *(1.0-a))*((1.0+pba->mg_c1*pow(H/k,2.0))/(1.0+pow(H/k,2.0)));
 
     pmg->gamma = 1.0 + (pba->mg_E21 + pba->mg_E22 *(1.0-a))*((1.0+pba->mg_c2*pow(H/k,2.0))/(1.0+pow(H/k,2.0)));

     

     mu_scale_part     = (1.0+pba->mg_c1*pow(H/k,2.0))/(1.0+pow(H/k,2.0));
     mu_scale_part_dot = ( 2.0*pba->mg_c1*H/k/k*Hdot*(1.0+pow(H/k,2.0))  - 2.0*H/k*Hdot/k*(1.0+pba->mg_c1*pow(H/k,2.0)) )   /   pow(1.0+pow(H/k,2.0),2.0);
     mu_scale_part_dot_dot = (  (-2.0 +2.0*pba->mg_c1 + (6.0 -6.0*pba->mg_c1)*pow(H/k,2.0))*pow(Hdot,2.0) + (-2.0 +2.0*pba->mg_c1)*(H+k*pow(H/k,3.0))* Hdotdot ) / ( k*k*pow(1.0+pow(H/k,2.0),3.0));

     gamma_scale_part     = (1.0+pba->mg_c2*pow(H/k,2.0))/(1.0+pow(H/k,2.0));
     gamma_scale_part_dot = ( 2.0*pba->mg_c2*H/k*Hdot/k*(1.0+pow(H/k,2.0))  - 2.0*H/k*Hdot/k*(1.0+pba->mg_c2*pow(H/k,2.0)) )   /   pow(1.0+pow(H/k,2.0),2.0);
     gamma_scale_part_dot_dot = (  (-2.0 +2.0*pba->mg_c2 + (6.0 -6.0*pba->mg_c2)*pow(H/k,2.0))*pow(Hdot,2.0) + (-2.0 +2.0*pba->mg_c2)*(H+k*pow(H/k,3.0))* Hdotdot ) / ( k*k*pow(1.0+pow(H/k,2.0),3.0));


     pmg->mu_dot = pba->mg_E11*mu_scale_part_dot + pba->mg_E12 * mu_scale_part_dot - pba->mg_E12 * (H*a*a*mu_scale_part + a*mu_scale_part_dot)  ;
     pmg->mu_dot_dot = pba->mg_E11*mu_scale_part_dot_dot + pba->mg_E12 * mu_scale_part_dot_dot - pba->mg_E12 * ((aHdot*a+H*a*H*a*a)*mu_scale_part + H*a*a*mu_scale_part_dot  + H*a*a*mu_scale_part_dot + a*mu_scale_part_dot_dot)  ;

     pmg->gamma_dot = pba->mg_E21*gamma_scale_part_dot + pba->mg_E22 * gamma_scale_part_dot - pba->mg_E22 * (H*a*a*gamma_scale_part + a*gamma_scale_part_dot)  ;
     pmg->gamma_dot_dot = pba->mg_E21*gamma_scale_part_dot_dot + pba->mg_E22 * gamma_scale_part_dot_dot - pba->mg_E22 *  ((aHdot*a+H*a*H*a*a)*gamma_scale_part + H*a*a*gamma_scale_part_dot  + H*a*a*gamma_scale_part_dot + a*gamma_scale_part_dot_dot)  ;

   }

 else if (pba->mg_ansatz == BZ) { // based on 0801.2431 and 0809.3791 and 1106.4543 and 1509.05034

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

     A1 = pba->mg_lambda1_2 * k*k * pow(a,pba->mg_ss);
     A2 = pba->mg_lambda2_2 * k*k * pow(a,pba->mg_ss);
  
     
     pmg->mu = (1.0 + pba->mg_B1 * A1)/(1.0 + A1);
          
     pmg->mu_dot = ((pba->mg_B1 - 1.0) * H * pba->mg_ss * A1) / (pow((1.0+A1),2.0));
     pmg->mu_dot *= a;

     pmg->gamma = (1.0 + pba->mg_B2 * A2)/(1.0 +A2);

     

     pmg->gamma_dot = ((pba->mg_B2 -1.0)* H * pba->mg_ss* A2)/(pow((1.0+A2),2.0));
     pmg->gamma_dot *= a;

   }

else if (pba->mg_ansatz == Geff) { // based on 1703.10538

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");
          
     pmg->mu = 1.0 + pba->mg_ga*pow((1.0-a),pba->mg_gn)-pba->mg_ga*pow((1.0-a),2.0*pba->mg_gn);
     pmg->mu_dot = pba->mg_ga*H*a*a*pba->mg_gn*pow((1.0-a),pba->mg_gn-1.0) -pba->mg_ga*H*a*a*2.0*pba->mg_gn*pow((1.0-a),2.0*pba->mg_gn-1.0);

     if (pba->mg_no_lens == _TRUE_) 
     {pmg->mu = 1.0; pmg->mu_dot = 0.0;
     printf("warning : choosing no_lens option for this model is equivalent to GR");}
     
     pmg->gamma = 1.0;
     pmg->gamma_dot = 0.0;
     
   }

else if (pba->mg_ansatz == z_flex_early) { 
     
	pmg->mu = 1.0 + pba->mg_muz*pow((1.0-a+1.e-4),pba->mg_zzn)-pba->mg_muz*pow((1.0-a+1.e-4),2.0*pba->mg_zzn);
	pmg->mu_dot = - pba->mg_muz*H*a*a*pba->mg_zzn*pow((1.0-a+1.e-4),pba->mg_zzn-1.0) +pba->mg_muz*H*a*a*2.0*pba->mg_zzn*pow((1.0-a+1.e-4),2.0*pba->mg_zzn-1.0);
        pmg->mu_dot_dot = - pba->mg_muz*(aHdot*a+H*H*a*a*a)*pba->mg_zzn*pow(1.0-a+1.e-4,pba->mg_zzn-1.0) 
                        + pba->mg_muz*H*a*a*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_muz*H*a*a*pow(1.0-a+1.e-4,pba->mg_zzn-2.0)
                        + pba->mg_muz*(aHdot*a+H*H*a*a*a)*2.0*pba->mg_zzn*pow(1.0-a+1.e-4,2.0*pba->mg_zzn-1.0)
                        - pba->mg_muz*H*a*a*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_muz*H*a*a*pow(1.0-a+1.e-4,2.0*pba->mg_zzn-2.0);
		     
	pmg->gamma = 1.0 + pba->mg_gamz*pow((1.0-a+1.e-4),pba->mg_zzn)-pba->mg_gamz*pow((1.0-a+1.e-4),2.0*pba->mg_zzn);
	pmg->gamma_dot = - pba->mg_gamz*H*a*a*pba->mg_zzn*pow((1.0-a+1.e-4),pba->mg_zzn-1.0) +pba->mg_gamz*H*a*a*2.0*pba->mg_zzn*pow((1.0-a+1.e-4),2.0*pba->mg_zzn-1.0);
        pmg->gamma_dot_dot = - pba->mg_gamz*(aHdot*a+H*H*a*a*a)*pba->mg_zzn*pow(1.0-a+1.e-4,pba->mg_zzn-1.0) 
                        + pba->mg_gamz*H*a*a*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_gamz*H*a*a*pow(1.0-a+1.e-4,pba->mg_zzn-2.0)
                        + pba->mg_gamz*(aHdot*a+H*H*a*a*a)*2.0*pba->mg_zzn*pow(1.0-a+1.e-4,2.0*pba->mg_zzn-1.0)
                        - pba->mg_gamz*H*a*a*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_gamz*H*a*a*pow(1.0-a+1.e-4,2.0*pba->mg_zzn-2.0);

   }

else if (pba->mg_ansatz == z_flex_late) { 

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");
     
	pmg->mu = 1.0 + pba->mg_muz*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn)-pba->mg_muz*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn);
	pmg->mu_dot = pba->mg_muz*omegaDEdot*pba->Omega0_lambda*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-1.0) -pba->mg_muz*omegaDEdot*pba->Omega0_lambda*2.0*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-1.0);
        pmg->mu_dot_dot = + pba->mg_muz*omegaDEdotdot*pba->Omega0_lambda*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-1.0) 
                        + pba->mg_muz*omegaDEdot*pba->Omega0_lambda*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_muz*omegaDEdot*pba->Omega0_lambda*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-2.0)
                        - pba->mg_muz*omegaDEdotdot*pba->Omega0_lambda*2.0*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-1.0)
                        - pba->mg_muz*omegaDEdot*pba->Omega0_lambda*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_muz*omegaDEdot*pba->Omega0_lambda*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-2.0);

		     
	pmg->gamma = 1.0 + pba->mg_gamz*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn)-pba->mg_gamz*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn);
	pmg->gamma_dot = pba->mg_gamz*omegaDEdot*pba->Omega0_lambda*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-1.0) -pba->mg_gamz*omegaDEdot*pba->Omega0_lambda*2.0*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-1.0);
        pmg->gamma_dot_dot = + pba->mg_gamz*omegaDEdotdot*pba->Omega0_lambda*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-1.0) 
                        + pba->mg_gamz*omegaDEdot*pba->Omega0_lambda*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_gamz*omegaDEdot*pba->Omega0_lambda*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-2.0)
                        - pba->mg_gamz*omegaDEdotdot*pba->Omega0_lambda*2.0*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-1.0)
                        - pba->mg_gamz*omegaDEdot*pba->Omega0_lambda*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_gamz*omegaDEdot*pba->Omega0_lambda*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-2.0);

     
   }

else if (pba->mg_ansatz == z_flex_norm_late) { 
     
	pmg->mu = 1.0 + pba->mg_muz*pow(omegaDE,pba->mg_zzn)-pba->mg_muz*pow(omegaDE,2.0*pba->mg_zzn);
	pmg->mu_dot = pba->mg_muz*omegaDEdot*pba->mg_zzn*pow(omegaDE,pba->mg_zzn-1.0) -pba->mg_muz*omegaDEdot*2.0*pba->mg_zzn*pow(omegaDE,2.0*pba->mg_zzn-1.0);
        pmg->mu_dot_dot = + pba->mg_muz*omegaDEdotdot*pba->mg_zzn*pow(omegaDE,pba->mg_zzn-1.0) 
                        + pba->mg_muz*omegaDEdot*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_muz*omegaDEdot*pow(omegaDE,pba->mg_zzn-2.0)
                        - pba->mg_muz*omegaDEdotdot*2.0*pba->mg_zzn*pow(omegaDE,2.0*pba->mg_zzn-1.0)
                        - pba->mg_muz*omegaDEdot*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_muz*omegaDEdot*pow(omegaDE,2.0*pba->mg_zzn-2.0);

		     
	pmg->gamma = 1.0 + pba->mg_gamz*pow(omegaDE,pba->mg_zzn)-pba->mg_gamz*pow(omegaDE,2.0*pba->mg_zzn);
	pmg->gamma_dot = pba->mg_gamz*omegaDEdot*pba->mg_zzn*pow(omegaDE,pba->mg_zzn-1.0) -pba->mg_gamz*omegaDEdot*2.0*pba->mg_zzn*pow(omegaDE,2.0*pba->mg_zzn-1.0);
        pmg->gamma_dot_dot = + pba->mg_gamz*omegaDEdotdot*pba->mg_zzn*pow(omegaDE,pba->mg_zzn-1.0) 
                        + pba->mg_gamz*omegaDEdot*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_gamz*omegaDEdot*pow(omegaDE,pba->mg_zzn-2.0)
                        - pba->mg_gamz*omegaDEdotdot*2.0*pba->mg_zzn*pow(omegaDE,2.0*pba->mg_zzn-1.0)
                        - pba->mg_gamz*omegaDEdot*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_gamz*omegaDEdot*pow(omegaDE,2.0*pba->mg_zzn-2.0);

       
   }

else if (pba->mg_ansatz == z_xpans_early) { 
     
	pmg->mu = 1.0 + pba->mg_T1*pow((1.0-a+1.e-4),pba->mg_zzn)+pba->mg_T2*pow((1.0-a+1.e-4),2.0*pba->mg_zzn);
	pmg->mu_dot = - pba->mg_T1*H*a*a*pba->mg_zzn*pow((1.0-a+1.e-4),pba->mg_zzn-1.0) -pba->mg_T2*H*a*a*2.0*pba->mg_zzn*pow((1.0-a+1.e-4),2.0*pba->mg_zzn-1.0);
        pmg->mu_dot_dot = + pba->mg_T1*(aHdot*a+H*H*a*a*a)*pba->mg_zzn*pow(1.0-a+1.e-4,pba->mg_zzn-1.0) 
                        - pba->mg_T1*H*a*a*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_T1*H*a*a*pow(1.0-a+1.e-4,pba->mg_zzn-2.0)
                        + pba->mg_T2*(aHdot*a+H*H*a*a*a)*2.0*pba->mg_zzn*pow(1.0-a+1.e-4,2.0*pba->mg_zzn-1.0)
                        - pba->mg_T2*H*a*a*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_T2*H*a*a*pow(1.0-a+1.e-4,2.0*pba->mg_zzn-2.0);
		     
	pmg->gamma = 1.0 + pba->mg_T3*pow((1.0-a+1.e-4),pba->mg_zzn)+pba->mg_T4*pow((1.0-a+1.e-4),2.0*pba->mg_zzn);
	pmg->gamma_dot = - pba->mg_T3*H*a*a*pba->mg_zzn*pow((1.0-a+1.e-4),pba->mg_zzn-1.0) -pba->mg_T4*H*a*a*2.0*pba->mg_zzn*pow((1.0-a+1.e-4),2.0*pba->mg_zzn-1.0);
        pmg->gamma_dot_dot = + pba->mg_T3*(aHdot*a+H*H*a*a*a)*pba->mg_zzn*pow(1.0-a+1.e-4,pba->mg_zzn-1.0) 
                        - pba->mg_T3*H*a*a*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_T3*H*a*a*pow(1.0-a+1.e-4,pba->mg_zzn-2.0)
                        + pba->mg_T4*(aHdot*a+H*H*a*a*a)*2.0*pba->mg_zzn*pow(1.0-a+1.e-4,2.0*pba->mg_zzn-1.0)
                        - pba->mg_T4*H*a*a*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_T4*H*a*a*pow(1.0-a+1.e-4,2.0*pba->mg_zzn-2.0);

   }

else if (pba->mg_ansatz == z_xpans_late) { 

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");
     
	pmg->mu = 1.0 + pba->mg_T1*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn)+pba->mg_T2*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn);
	pmg->mu_dot = pba->mg_T1*omegaDEdot*pba->Omega0_lambda*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-1.0) +pba->mg_T2*omegaDEdot*pba->Omega0_lambda*2.0*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-1.0);
        pmg->mu_dot_dot = + pba->mg_T1*omegaDEdotdot*pba->Omega0_lambda*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-1.0) 
                        + pba->mg_T1*omegaDEdot*pba->Omega0_lambda*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_T1*omegaDEdot*pba->Omega0_lambda*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-2.0)
                        + pba->mg_T2*omegaDEdotdot*pba->Omega0_lambda*2.0*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-1.0)
                        + pba->mg_T2*omegaDEdot*pba->Omega0_lambda*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_T2*omegaDEdot*pba->Omega0_lambda*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-2.0);

		     
	pmg->gamma = 1.0 + pba->mg_T3*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn)+pba->mg_T4*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn);
	pmg->gamma_dot = pba->mg_T3*omegaDEdot*pba->Omega0_lambda*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-1.0) +pba->mg_T4*omegaDEdot*pba->Omega0_lambda*2.0*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-1.0);
        pmg->gamma_dot_dot = + pba->mg_T3*omegaDEdotdot*pba->Omega0_lambda*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-1.0) 
                        + pba->mg_T3*omegaDEdot*pba->Omega0_lambda*pba->mg_zzn*(pba->mg_zzn-1.0)*pba->mg_T3*omegaDEdot*pba->Omega0_lambda*pow(omegaDE*pba->Omega0_lambda,pba->mg_zzn-2.0)
                        + pba->mg_T4*omegaDEdotdot*pba->Omega0_lambda*2.0*pba->mg_zzn*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-1.0)
                        + pba->mg_T4*omegaDEdot*pba->Omega0_lambda*2.0*pba->mg_zzn*(2.0*pba->mg_zzn-1.0)*pba->mg_T4*omegaDEdot*pba->Omega0_lambda*pow(omegaDE*pba->Omega0_lambda,2.0*pba->mg_zzn-2.0);

              
   }

else if (pba->mg_ansatz == QR) { // based on 1002.4197 

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

     QR_kc = 0.01;

     

     pmg->mu = 1.0 + (1.0*exp(-k/QR_kc)+pba->mg_Q*(1.0-exp(-k/QR_kc))-1.0)*pow(a,pba->mg_QRss);
     pmg->gamma = 1.0 +  (1.0*exp(-k/QR_kc)+pba->mg_R*(1.0-exp(-k/QR_kc))-1.0)*pow(a,pba->mg_QRss);
  
     
     
     pmg->mu_dot = (1.0*exp(-k/QR_kc)+pba->mg_Q*(1.0-exp(-k/QR_kc))-1.0)*H*pba->mg_QRss* pow(a,pba->mg_QRss);
     pmg->mu_dot *= a;
     pmg->gamma_dot =  (1.0*exp(-k/QR_kc)+pba->mg_R*(1.0-exp(-k/QR_kc))-1.0)*H*pba->mg_QRss*pow(a,pba->mg_QRss);   
     pmg->mu_dot *= a;

   }

else if (pba->mg_ansatz == GI) {

    if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is implicitely implemented for this model.");

    if (pba->mg_no_lens == _TRUE_) 

class_stop(pba->error_message,"mg_no_lens option is not implemented for this model.");
    
    omegaM    = (1. / Ez / Ez)*pow(a,-3.0)*(pba->Omega0_cdm+pba->Omega0_dcdmdr+pba->Omega0_b+Omega0_ncdm);
    omegaMdot = -omegaM*(3.*aH+2.*Hdot/H);
    omegaDEz = (1. / Ez / Ez)*(1.-pba->Omega0_cdm-pba->Omega0_dcdmdr-pba->Omega0_b-Omega0_ncdm)*pow(a,-3.0*(1.+pba->w0_fld+pba->wa_fld)*exp(-3.*pba->wa_fld*a)); 
    
    omegaDEzdot = -omegaDE*((3.*(1.+pba->w0_fld+pba->wa_fld)-3.*a*pba->wa_fld)*aH+2.*Hdot/H);
    
    pmg->mu = (2.0/3.0)*pow(omegaM,pba->gamGI-1.0)*(pow(omegaM,pba->gamGI)+2.0-3.0*pba->gamGI+3.0*(pba->gamGI-0.5)*(omegaM+(1.+pba->w0_fld+pba->wa_fld-a*pba->wa_fld)*omegaDEz));
    
    pmg->mu_dot =(pba->gamGI-1.0)*(omegaMdot/omegaM)*pmg->mu+
                  (2./3.)*pow(omegaM,pba->gamGI-1.0)*
(omegaMdot*(pba->gamGI*pow(omegaM,pba->gamGI-1.0)+3.0*(pba->gamGI-0.5))+
              3.0*(pba->gamGI-0.5)*((1.+pba->w0_fld+pba->wa_fld-a*pba->wa_fld)*omegaDEzdot-pba->wa_fld*aH*a*omegaDEz));
    
     pmg->gamma=1;
     pmg->gamma_dot =0;    
  
}

else if (pba->mg_ansatz == FR) { // based on 1305.5647

 if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

if (pba->mg_no_lens == _TRUE_) 

class_stop(pba->error_message,"mg_no_lens option is not yet implemented for this model.");
    
// FR-inspired ansatz 

beta0 = 1./sqrt(6.);

FRm0 = (pba->H0)*sqrt((4.0*(1-pba->Omega0_cdm-pba->Omega0_b) + pba->Omega0_cdm+pba->Omega0_b+Omega0_ncdm)/((pba->FRn+1.0)*pba->F_R0));
//here Note: H0 includes factor of C

MGM = FRm0 *pow( (4.0 * (1-pba->Omega0_cdm-pba->Omega0_b) + (pba->Omega0_cdm+pba->Omega0_b+Omega0_ncdm)*pow(a,-3.0))/(4.0 * (1-pba->Omega0_cdm-pba->Omega0_b+Omega0_ncdm) + pba->Omega0_cdm+pba->Omega0_b+Omega0_ncdm),pba->FRn/2.0+1.0);

       
dMGModt = MGM / (4.0 * (1-pba->Omega0_cdm-pba->Omega0_b+Omega0_ncdm) + (pba->Omega0_cdm+pba->Omega0_b+Omega0_ncdm)*pow(a,-3.0)) * (-3.0* pba->FRn / 2.0 - 3.0) *((pba->Omega0_cdm+pba->Omega0_b+Omega0_ncdm)* pow(a,-3.0) * aH ) ;
    
t1 = (2.0*pow(beta0,2.0))*k*k;
t2 = pow(MGM,2.0)*pow(a,2.0);

pmg->gamma = (k*k - t1 + t2)/(k*k + t1 + t2);

dt1odt = 0.0 ;
dt2odt = (2.0*pow(a,2.0))*(MGM*dMGModt + pow(MGM,2.0) *aH);

pmg->gamma_dot = 2.0*(t1*dt2odt-dt1odt*(k*k + t2))/(pow(k*k + t1 + t2,2.0));  

pmg->mu = (k*k + t1 + t2)/(k*k + t2);
pmg->mu_dot = (dt1odt*(k*k + t2) - t1*dt2odt)/(pow(k*k + t2,2.0));


  }
else if (pba->mg_ansatz == diL) { // based on 1206.3568

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

if (pba->mg_no_lens == _TRUE_) 

class_stop(pba->error_message,"mg_no_lens option is not yet implemented for this model.");

MGM = (pba->H0) /(pba->xi0) * pow(a,-pba->DilR) ;
       
dMGModt =  - pba->DilR * MGM * H ;

Beta = pba->beta0 * exp( (pba->DilS)/(2.0* pba->DilR - 3.0)*(pow(a,(2.0* pba->DilR - 3.0))-1.0) );

Betadot = Beta * (pba->DilS * pow(a,(2.0* pba->DilR - 3.0)) * aH);
    
t1 = (2.0*pow(Beta,2.0))*k*k;
t2 = pow(MGM,2.0)*pow(a,2.0);

pmg->gamma = (k*k - t1 + t2)/(k*k + t1 + t2);

dt1odt = 4.0*Beta*Betadot*k*k;
dt2odt = (2.0*pow(a,2.0))*(MGM*dMGModt + pow(MGM,2.0) *aH);

pmg->gamma_dot = 2.0*(t1*dt2odt-dt1odt*(k*k + t2))/(pow(k*k + t1 + t2,2.0));


pmg->mu = (k*k + t1 + t2)/(k*k + t2);

pmg->mu_dot = (dt1odt*(k*k + t2) - t1*dt2odt)/(pow(k*k + t2,2.0));
 

}
else if (pba->mg_ansatz == syM) {  // based on 1206.3568

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");

if (pba->mg_no_lens == _TRUE_) 

class_stop(pba->error_message,"mg_no_lens option is not yet implemented for this model.");

MGM = (pba->H0) / (pba->xi_star) * sqrt(1.0-pow((pba->a_star/a),3.0)) ;
       
dMGModt = 1.5*(pba->H0)/(pba->xi_star)*(pow((pba->a_star/a),3.0)*aH)/(sqrt(1.0-pow((pba->a_star/a),3.0)))  ;

Beta = pba->beta_star * sqrt(1.0-pow((pba->a_star/a),3.0)) ;

Betadot = 1.5 * (pba->beta_star) * (pow((pba->a_star/a),3.0) * aH) /( sqrt(1.0-pow((pba->a_star/a),3.0)));
    
t1 = (2.0*pow(Beta,2.0))*k*k;
t2 = pow(MGM,2.0)*pow(a,2.0);

pmg->gamma = (k*k - t1 + t2)/(k*k + t1 + t2);

dt1odt = 4.0*Beta*Betadot*k*k;
dt2odt = (2.0*pow(a,2.0))*(MGM*dMGModt + pow(MGM,2.0) *aH);

pmg->gamma_dot = 2.0*(t1*dt2odt-dt1odt*(k*k + t2))/(pow(k*k + t1 + t2,2.0));

pmg->mu = (k*k + t1 + t2)/(k*k + t2);
pmg->mu_dot = (dt1odt*(k*k + t2) - t1*dt2odt)/(pow(k*k + t2,2.0));
 
 
}else if (pba->mg_ansatz == JBD) { // based on gr-gc/0001066 and 1506.07771

if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not implemented because this is already a designer model.");

if (pba->mg_no_lens == _TRUE_) 

class_stop(pba->error_message,"mg_no_lens option is not implemented because this is already a sigma = 1 model.");

    wJBD = pba->w_JBD;


  omegaM    = (1. / Ez / Ez)*pow(a,-3.0)*(pba->Omega0_cdm+pba->Omega0_dcdmdr+pba->Omega0_b);
  omegaMdot = -omegaM*(3.*aH+2.*Hdot/H);
  d_JBD = 2.0*wJBD + 3.0;
  g0xphi0 = (4.0+2.0*wJBD)/(3.0+2.0*wJBD) * 1./pow((2.-(pba->Omega0_cdm+pba->Omega0_dcdmdr+pba->Omega0_b)),2./(3.*d_JBD)) ;
  ga =  pow(a,2./d_JBD)*pow(2.*pow(a,3.)*(1.-omegaM)+omegaM,2./(3.*d_JBD)) ;

    phi_jbd = g0xphi0*ga;
    phi_jbd_dot = g0xphi0 *( 2./d_JBD*H*ga + ga*1./(2.*pow(a,3.)*(1.-omegaM)+omegaM)* 2./(3.*d_JBD)*(6.*H*pow(a,3.)*(1.-omegaM)-2.*pow(a,3.)*omegaMdot+omegaMdot)   );


    pmg->mu    = (4.0+2.0*wJBD)/(3.0+2.0*wJBD)   *    1./ phi_jbd    ;
    pmg->gamma = (1.0+wJBD)/(2.0+wJBD);
    
    pmg->mu_dot = (4.0+2.0*wJBD)/(3.0+2.0*wJBD)   *  (- 1./pow(phi_jbd,2.)) * phi_jbd_dot*a ;
    pmg->gamma_dot = 0.0;
  }

else if (pba->mg_ansatz == nDGP) { // based on ph/0511634
    
if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not implemented because this is already a designer model.");

if (pba->mg_no_lens == _TRUE_) 

class_stop(pba->error_message,"mg_no_lens option is not implemented because this is already a sigma = 1 model.");
    

rc = pba->rc;

// mu, gamma
    b_nDGP = 1.+ 2.*H*rc*(1.+(Hdot/a)/(3.*pow(H,2.)));
    
    pmg->mu    = 1.+1./(3.*b_nDGP)  ;
    
    pmg->gamma = (1.-1./(3.*b_nDGP))/ (1.+1./(3.*b_nDGP));
    
    pmg->mu_dot = (-1./(3.*pow(b_nDGP,2.)))*2.*rc*(Hdot+(Hdotdot*H-pow(Hdot,2.))/(3.*pow(H,2.)));
    pmg->gamma_dot = (   pmg->mu_dot*(1.+1./(3.*b_nDGP))   -(1./(3.*pow(b_nDGP,2.)))*2.*rc*(Hdot+(Hdotdot*H-pow(Hdot,2.))/(3.*pow(H,2.)))  *pmg->mu    )/   pow(1.+1./(3.*b_nDGP),2.);
    
  }
else if (pba->mg_ansatz == kmoufl) { // based on 1403.5420 and 1809.09958 and 1403.5424 
    
if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not implemented because this is already a designer model.");

if (pba->mg_no_lens == _TRUE_) 

class_stop(pba->error_message,"mg_no_lens option is not implemented because this is already a sigma = 1 model.");
    

// mu, gamma
    A_kmfl = 1.0 + pba->beta_kmfl*a;
    X_kmfl = 0.5 * pow(A_kmfl,2.0) * pow(H*a,2.0) /  pvecback[pba->index_bg_rho_lambda];
    k_prime_mfl = 1.0 + 2.0*pba->k0_kmfl * X_kmfl;
    epsl1_kmfl = 2.0*pow(pba->beta_kmfl,2.0)/k_prime_mfl;    
    X_kmfl_dot = 0.5 * pow(A_kmfl,2.0) /  pvecback[pba->index_bg_rho_lambda] * 2.0*H*a*(H*H*a+Hdot*a);

    pmg->mu    = 1.+ epsl1_kmfl ;
    
    pmg->gamma = (1.- epsl1_kmfl)/ (1.+ epsl1_kmfl);
    
    pmg->mu_dot = -2.0*pba->beta_kmfl*pow(k_prime_mfl,-2.0)* 2.0*pba->k0_kmfl*X_kmfl_dot*a;
    pmg->gamma_dot = ( -pmg->mu_dot/a * (1.+ epsl1_kmfl)  - pmg->mu_dot/a * (1.- epsl1_kmfl) )/pow(1.+ epsl1_kmfl,2.0)*a;
    
  }
else if (pba->mg_ansatz == simple ) {

   if (pba->mg_bckg == _TRUE_) 

class_stop(pba->error_message,"mg_bckg option is not yet implemented for this model.");
    
    // Simple ansatz where mu, gamma are constant with redshift and scale
    pmg->mu    = pba->mg_A_mu;
    pmg->gamma = pba->mg_A_gamma;
    
    // Conformal time derivatives
    pmg->mu_dot = 0.;
    pmg->gamma_dot = 0.;
    
  } // end ansatz check

  if (pba->mg_no_lens == _TRUE_ && pba->mg_ansatz != EFT_alpha_QSE && pba->mg_ansatz != EFT_alpha_QSL) {

    pmg->gamma=-1.0+2.0/pmg->mu;
    pmg->gamma_dot=-2.0*pmg->mu_dot/pow(pmg->mu,2.0);

    }

  if (pmg->mu == 0.0)
  pmg->mu += 1.e-6;
  if (pmg->gamma == 0.0)
  pmg->gamma += 1.e-6;
  
  // Calculate ULS amplitude factor with MG corrections
  // OmegaM(a) = rho_m(a) / H^2(a)
  //pmg->A_MG = 4.5 * (a*H*a*H) * OmegaM_a * pmg->mu * pmg->gamma;
  pmg->A_MG = 4.5 * rho_m * (a*a) * pmg->mu * pmg->gamma;
  
  // Return success
  return _SUCCESS_;
}
