MGCLASS: Cosmic Linear Anisotropy Solving System for Modified Gravity (MG)
========================================================================

Authors: Ziad Sakr and Matteo Martinelli

MGCLASS is a set of modifications to CLASS that add the ability to calculate relativistic large-scale structure observables in the presence of certain modifications to GR following (https://arxiv.org/abs/2112.14175).

It is based on the existing code by Baker and Bull (gitlab link: https://gitlab.com/philbull/mgclass) which implements the equations of Baker & Bull (2015) (https://arxiv.org/abs/1506.00641) to the public CLASS code by Julien Lesgourgues and Thomas Tram (http://class-code.net )

Compiling MGCLASS and getting started
-----------------------------------

Clone the code from https://gitlab.com/zizgitlab/mgclass--ii. 
Go to the mgclass directory (cd mgclass/) and compile (make clean; make class). 
If the first compilation attempt fails, you may need to open the Makefile
and adapt the name of the compiler (default: gcc),
of the optimization flag (default: -O4 -ffast-math) and of the OpenMP
flag (default: -fopenmp; this flag is facultative, you are free to
compile without OpenMP if you don't want parallel execution; note that
you need the version 4.2 or higher of gcc to be able to compile with
-fopenmp). Many more details on the compilation are given on the
wiki page https://github.com/lesgourg/class_public/wiki/Installation
(in particular, for compiling on Mac >= 10.9 despite of the clang
incompatibility with OpenMP).

To check that the code runs, type:

    ./class modgrav.ini

The modgrav.ini file is the reference input file, containing and
explaining the use of all possible MG models input parameters. You
can create for your own purposes some shorter input files, containing 
only the input lines which are useful for you. Input files must have 
a *.ini extension. 
Note that you should keep the 
gauge entry set to newtonian and perturb_sampling_stepsize set to 0.05 
for the code to run and give the accurate output in MG mode.

For further information you can check the documentation on the CLASS webpage 
but also check the automatic generated one located in

    doc/manual/html/index.html
    doc/manual/CLASS_manual.pdf

On top of that, we provide a jupyter notebook in order to offer a walkthrough 
for users on how to use the different models and options implemented  

    ./Example_MGCLASS.ipynb

MGCLASS is easily interfaced with cosmological data analysis codes 
that make use of the standard code CLASS, e.g., MontePython 
(https://arxiv.org/abs/1210.7183) and Cobaya (https://arxiv.org/abs/2005.05290)

Note: recent updates allow to install MGCLASS alongside CLASS

Python
------

To use CLASS from python, or ipython notebooks, or from the Monte
Python or Cobaya parameter extraction code, you need to compile not 
only the code, but also its python wrapper. This can be done by typing 
just 'make' instead of 'make class'. More details on the wrapper and 
its compilation are found on the wiki page

https://github.com/lesgourg/class_public/wiki

Note: recent updates allow to import mgclassy (MGCLASS) and classy (CLASS) in the same python script

Developing the code
--------------------

If you want to develop the code, as we describe in more detail in (https://arxiv.org/abs/2112.14175) or release_notes.pdf, the modified equations for perturbations and background evolution that are implemented are fairly general; this has the advantage to allow you to implement new models or parameterizations in a very simple way, by just adding new possible options for the calculation of the functions mu(z,k), eta(z,k) that encode MG modifications to the Poisson and anisotropic stress equations in modgrav.c, and the corresponding parameters in input.c

Using the code (support info at the end)
--------------

You can use MGCLASS freely, provided that in your publications, you cite
at the following papers in order of priority if you are limited by the number of pages e.g. by a conference proceedings rules

`Cosmological Constraints on sub-horizon scales modified gravity theories with MGCLASS II <http://arxiv.org/abs/2112.14175>`.

`Observational signatures of modified gravity on ultra-large scales <http://arxiv.org/abs/1104.2933>`.

`CLASS II: Approximation schemes <http://arxiv.org/abs/1104.2933>`.

Works where MGCLASS was used 
----------------------------

- Euclid ... Extensions beyond the standard modelling of theoretical probes and systematic effects <http://arxiv.org/abs/2510.09147>

- Dark energy constraints in light of theoretical priors <http://arxiv.org/abs/2507.19450>

- Euclid ... Constraining parameterised models of modifications of gravity with the spectroscopic and photometric primary probes <http://arxiv.org/abs/2506.03008>

- Preference for evolving dark energy in light of the galaxy bispectrum <http://arxiv.org/abs/2503.04602>

- Neural Networks for cosmological model ... using Cosmic Microwave Background data <http://arxiv.org/abs/2410.05209>

- Efficient Compression of Redshift-Space Distortion Data for Late-Time Modified Gravity Models <http://arxiv.org/abs/2408.16388>

- Analytical Emulator for the Linear Matter Power Spectrum from Physics-Informed Machine Learning <http://arxiv.org/abs/2407.16640>

- Constrain the linear scalar perturbation theory of Cotton gravity <http://arxiv.org/abs/2405.07209>

- Investigating the Hubble Tension and σ8 Discrepancy in f(Q) Cosmology <http://arxiv.org/abs/2405.03627>

- Constraining f(R) gravity with cross-correlation of galaxies and cosmic microwave background lensing <http://arxiv.org/abs/2311.09936>

- Machine learning unveils the linear matter power spectrum of modified gravity <http://arxiv.org/abs/2307.03643>

- Euclid: Constraints on f(R) cosmologies from the spectroscopic and photometric primary probes <http://arxiv.org/abs/2306.11053>

- A trium test on beyond ΛCDM triggering parameters <http://arxiv.org/abs/2305.02817>

- Constraining extended cosmologies with GW×LSS cross-correlations <http://arxiv.org/abs/2306.03031>

- Extensions to ΛCDM at Intermediate Redshifts to Solve the Tensions ? <http://arxiv.org/abs/2305.02913>

- Asevolution: a relativistic N-body implementation of the (a)symmetron <http://arxiv.org/abs/2302.07857> (private communication)

- Measuring dark energy with expansion and growth <http://arxiv.org/abs/2206.12375>

- Cosmological Constraints on sub-horizon scales modified gravity theories with MGCLASS II <http://arxiv.org/abs/2112.14175>

- Observational signatures of modified gravity on ultra-large scales <http://arxiv.org/abs/1104.2933>

Updates, revisions & minor issues till 23/10/2025
-------------------------------------------------

- allow installation along with other versions of CLASS - usage of import mgclassy instead of classy

- a zero imputation value for \mu & \Sigma parameterization

- Fixed some display bugs.

- Implemented \mu & \Sigma parameterization compatible with DES MG model.

- Allowed calling the Weyl transfer function.

- fixed a typo bug in the Symmetron Model thanks to Øyvind Christiansen who spotted it while further validating part of his code in 2302.07857

- Attention: typo in equation 4.10 in the release paper 2112.14175 aH -> H and a missing \mu multiplying each \eta in the numerator. 



Support
-------

To get support, please open a new issue on the

https://gitlab.com/zizgitlab/mgclass--ii   webpage.

or drop us an email

ziad.sakr@net.usj.edu.lb
