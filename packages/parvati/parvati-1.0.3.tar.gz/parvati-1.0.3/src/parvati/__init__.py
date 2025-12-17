"""
PARVATI: Profile and Analysis of Radial Velocity using Astronomical Tools for Investigation
A Python package to compute and analyse stellar line profiles
Written by Monica Rainer
Last modified: 2025-12-10

    PARVATI is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY. 
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Functions:
- read_spectrum(filename, unit='a', wavecol=1, fluxcol=2, nfluxcol=0, snrcol=0, echcol=0):
    Read the spectrum from an ASCII or FITS file

- norm_spectrum(wave, flux, snr=False, echelle=False, deg=2, \
    n_ord=False, refine=False, output=False)
    Automatically normalise a stellar spectrum

- read_mask(maskname, unit='a', ele=False, no_ele=False, depths=(0.01,1),\
              balmer=True, tellurics=True, wmin=False, wmax=False, absorption=False)
    Read stellar mask (either binary mask, VALD file, or spectrum)

- split_spectrum(spectrum)
     Auxiliary function for compute_lsd/compute_ccf

- rebin_spectrum(o_wave, o_flux, o_nflux, o_snr, wave_step)
     Auxiliary function for compute_lsd

- remove_cosmics(len_vrange, o_split_nflux, sigma)
     Auxiliary function for compute_lsd/compute_ccf

- smooth_spectrum(new_wave, o_split_nflux, fine_step=10)
     Auxiliary function for compute_lsd/compute_ccf
     
- compute_lsd(spectrum, mask_data, vrange=(-200,200), \
     step=1., cosmic=False, sigma=10, clean=False, verbose=False, output=False)
    Compute the mean line profile using the Least-Squares Deconvolution
    
- compute_ccf(spectrum, mask_data, vrange=(-200,200), step=1., mask_spectrum=False, \
     cosmic=False, sigma=10, clean=False, weights=False, verbose=False, output=False)
    Compute the mean line profile using  Cross-Correlation Function

- show_ccf(rvs,ccfs)
    Auxiliary function
    Plot line profiles and define line limits

- extract_line(spectrum, unit='a', w0=6562.801, vrange=(-200,200), step=0.5, verbose=False, output=False)
    Extract a single line from a spectrum at w0 as a mean line profile

- norm_profile(profiles, rvcol=1, prfcol=2, errcol=0, sfx='pfn', std='line_mean_std', limits=False)
    Normalise the profiles to account for continuum problems.

- func_rot(x,a,x0,xl,LD=0.6)
    Fitting function
    Rotational broadening function, from:
    Gray, D. F. 2008, The Observation and Analysis of Stellar Photospheres

- gaussian(x,x0,s,F0,K):
    Fitting function
    Gaussian function

- lorentzian(x, x0, g, F0, K)
    Fitting function
    Lorentzian function

- voigt_function(x, x0, g, s, F0, K)
    Fitting function
    Voigt function    

- fit_profile(vrad, flux, errs=0, gauss=True, lorentz=True, voigt=True, rot=True, rv0=0, width=10, ld=0.6)
    Fit a mean line profile

- moments(rvs, ccf, errs=0, limits=False, normalise=True)
    Compute the line moments

- bisector(rv_range, flux, errs=0, limits=False)
    Compute the bisector of a stellar line profile

- find_shift_fft(y1, y2)
    Auxiliary function for fourier

- fourier(rv_range, flux, errs=False, limits=False, ld=0.6)
    https://www.great-esf.eu/AstroStats13-Python/numpy/scipy_fft.html
    Compute the Fourier transform

"""

from parvati.parvati import *
