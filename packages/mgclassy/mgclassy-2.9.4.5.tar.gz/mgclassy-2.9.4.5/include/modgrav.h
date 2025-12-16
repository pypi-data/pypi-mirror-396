/** @file modgrav.h Includes for modgrav module */

#include "background.h"

struct modgrav
{
  /** @name - return values of MG functions. */
  double mu;
  double mu_dot;
  double mu_dot_dot;
  double gamma;
  double gamma_dot;
  double gamma_dot_dot;

  double mu_0;
  double mu_dot_0;
  double gamma_0;
  double gamma_dot_0;

  
  
  double A_MG; // A_MG = (9/2) (aH)^2 Omega_M(a) \tilde{mu} \gamma
}; // end struct modgrav

/* C++ wrapping */
#ifdef __cplusplus
extern "C" {
#endif

int modgrav_bckg_test(
                 int * mg_bckg_test_enabled
                 );

int modgrav_test(
                 int * mg_test_enabled
                 );

int modgrav_init(
                 struct background * pba,
                 struct modgrav * pmg
                 );

int modgrav_functions(
                 struct background * pba,
                 double * pvecback,
                 double k,
                 double tau,
                 struct modgrav * pmg
                 );

/* End C++ wrapping */
#ifdef __cplusplus
}
#endif
