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

import os

import numpy as np
import uncertainties as un
from uncertainties import umath, ufloat

from astropy import constants as const
from astropy.stats import sigma_clip
from astropy.io import fits

from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.fftpack import fft,fftfreq,ifft
from scipy.special import wofz
from scipy.integrate import simpson, trapezoid
from scipy.stats import linregress


from matplotlib import pyplot as plt

from csaps import csaps as smooth_spline

ckms = const.c.to('km/s').value



###############################
#  Read the stellar spectrum  #
###############################
def read_spectrum(filename, unit='a', wavecol=1, fluxcol=2, nfluxcol=0, snrcol=0, echcol=0):
    """
    Read the spectrum from an ASCII or FITS file.
    filename = name of the ASCII/FITS file of the spectrum.
               If FITS, it may be either 1d:
                  a. the flux if the data hdu[0].data
                  b. the wavelength is in the header (CRVAL1, CDELT1, NAXIS1)
               Or 2d, with all the data in the second hdu:
                  1. data = hdu[1].data
                  2. wavelength in data.field(wavecol-1)
                  3. flux in data.field(fluxcol-1)
                  4. snr, echelle e normalised flux optional. Not present if the col = 0
               If ASCII, it must have at least 2 columns:
                  1 - wavelength
                  2 - flux
                  OPTIONAL
                  3 - normalised flux
                  4 - signal-to-noise ratio
                  5 - echelle orders
               To normalise the spectrum and save them in the correct format,
               use norm_spectrum on the original data with the flag output=True
    unit  = wavelength units, choose between:
            'a': Angstrom (default)
            'n': nanometer
            'm': micron
    """
    adjust = {'a': 1, 'n':10, 'm': 10000}

    # Check first if it is a FITS file:
    try:
        with fits.open(filename) as hdu:
            try:
                data = hdu[1].data
                head = hdu[0].header
                wave = data.field(int(wavecol-1))
                flux = data.field(int(fluxcol-1))
                if snrcol:
                    snr = data.field(int(snrcol-1))
                else:
                    with np.errstate(all='ignore'):
                        snr = np.sqrt(flux)
                    snr = np.nan_to_num(snr)
                if echcol:
                    echelle = data.field(int(echcol-1))
                else:
                    echelle = False
                if nfluxcol:
                    nflux = data.field(int(nfluxcol-1))
                else:
                    nflux = flux
                # Check if the data is 1d arrays or matrix, sort the wavelength and adjust
                if len(wave.shape) > 1:
                    o_echelle = np.zeros(wave.shape)
                    for n, o_wave in enumerate(wave):
                        idx_sort = np.argsort(o_wave)
                        o_wave = o_wave[idx_sort]
                        flux[n] = flux[n][idx_sort]
                        snr[n] = snr[n][idx_sort]
                        nflux[n] = nflux[n][idx_sort]
                        if echcol:
                            if len(echelle.shape) == 1:
                                o_echelle[n] = o_echelle[n]+echelle[n]
                            else:
                                echelle[n] = echelle[n][idx_sort]
                    if np.sum(o_echelle):
                        echelle = o_echelle
                    if wave[0][0] > wave[-1][-1]:
                        wave = np.concatenate(np.flipud(wave))
                        flux = np.concatenate(np.flipud(flux))
                        snr = np.concatenate(np.flipud(snr))
                        nflux = np.concatenate(np.flipud(nflux))
                        if echcol:
                            echelle = np.concatenate(np.flipud(echelle))
                    else:
                        wave = np.concatenate(wave)
                        flux = np.concatenate(flux)
                        snr = np.concatenate(snr)
                        nflux = np.concatenate(nflux)
                        if echcol:
                            echelle = np.concatenate(echelle)
                                
            except IndexError:
                flux = hdu[0].data
                head = hdu[0].header
                try:
                    start = head['CRVAL1']
                    step = head['CDELT1']
                    length = head['NAXIS1']
                    end = start + (step*length) - step
                    wave = np.linspace(start, end, length)
                except KeyError:
                    wave = np.arange(len(flux))
                with np.errstate(all='ignore'):
                    snr = np.sqrt(flux)
                snr = np.nan_to_num(snr)
                echelle = False
                nflux = flux

    except OSError:       
        all_data = np.loadtxt(filename, unpack=True)
        wave = all_data[int(wavecol-1)]
        flux = all_data[int(fluxcol-1)]
        if snrcol:
            snr = all_data[int(snrcol-1)]
        else:
            with np.errstate(all='ignore'):
                snr = np.sqrt(flux)
            snr = np.nan_to_num(snr)
        if echcol:
            echelle = all_data[int(echcol-1)]
        else:
            echelle = False
        if nfluxcol:
            nflux = all_data[int(nfluxcol-1)]
        else:
            nflux = flux            

        head = fits.PrimaryHDU().header
            
    wave = wave*adjust[unit]
    spectrum = {'wave': wave, 'flux': flux, 'nflux': nflux, 'snr': snr, 'echelle': echelle, 'header': head}

    return spectrum



#############################
#  Normalise the spectrum   #
#############################
def norm_spectrum(wave, flux, snr=False, echelle=False, deg=2, \
    n_ord=False, refine=False, output=False):
    """
    Automatically normalise a stellar spectrum:
    wave = wavelength array
    flux = flux array
    snr = snr array (optional)
    echelle = echelle order number array (optional)
    deg = degree of the polynomials used to normalise the spectrum
    n_ord = if the echelle array is not given, the outpu spectrum may be split in
    this arbitrary integer number of fake echelle orders (default = False)
    refine = if either echelle or n_ord are given, the normalisation may
    be refined by ensuring a smooth variation of the polynomial coefficients
    along the orders
    output = the results are saved in an ASCII file with this name
    """

    if not np.sum(snr):
        with np.errstate(all='ignore'):
            snr = np.sqrt(flux)
        snr = np.nan_to_num(snr)

    if not np.sum(echelle):
        echelle = np.zeros(wave.shape)


    if n_ord:
        if n_ord > 1:
            n_ord = int(n_ord)
            chunk = int(len(flux)/(10*n_ord))
            o_wave = np.array_split(wave, n_ord)
            o_flux = np.array_split(flux, n_ord)
            o_snr = np.array_split(snr, n_ord)

            new_wave = []
            new_flux = []
            new_snr = []
            new_ord = []

            for n, ordine in enumerate(o_wave):
                if n>0:
                    new_wave.extend(o_wave[n-1][-chunk:])
                    new_flux.extend(o_flux[n-1][-chunk:])
                    new_snr.extend(o_snr[n-1][-chunk:])
                    new_ord.extend(np.ones(chunk)*(n+1))
                new_wave.extend(o_wave[n])
                new_flux.extend(o_flux[n])
                new_snr.extend(o_snr[n])
                new_ord.extend(np.ones(len(o_snr[n]))*(n+1))
                try:
                    new_wave.extend(o_wave[n+1][:chunk])
                    new_flux.extend(o_flux[n+1][:chunk])
                    new_snr.extend(o_snr[n+1][:chunk])
                    new_ord.extend(np.ones(chunk)*(n+1))
                except IndexError:
                    pass

            wave = np.asarray(new_wave)
            flux = np.asarray(new_flux)
            snr = np.asarray(new_snr)
            echelle = np.asarray(new_ord)

    fnor = np.zeros(flux.shape)
    wave = np.nan_to_num(wave)
    flux = np.nan_to_num(flux)
    snr = np.nan_to_num(snr, posinf=0, neginf=0)

    echelle = echelle.astype(int)
    start_o = echelle[0]
    end_o = echelle[-1]
    if end_o > start_o:
        end_o = end_o+1
        step = 1
    else:
        end_o = end_o-1
        step = -1

    #orange = abs(end_o-start_o)+1
    orange = len(echelle)
    # create array for the polynomial variables
    coeffs = np.zeros((deg+1,orange))
    w_ord = np.zeros(orange)
    i = 0

    # First normalisation

    for o in np.unique(echelle):
        ordine = np.nonzero(echelle==o)
        owave = wave[ordine]
        oflux = flux[ordine]
        osnr = snr[ordine]

        split_flux = np.array_split(oflux,3)
        split_snr = np.array_split(osnr,3)

        for k, subregion in enumerate(split_flux):
            length = len(subregion)
            idxs_fixed = np.argsort(subregion)
            flush = -int(length/50)
            enhance = -int(length/20)
            enhance0 = -int(2*flush)
            split_snr[k][idxs_fixed[flush:]] = 0.0
            split_snr[k][idxs_fixed[enhance0+enhance:enhance0]] =\
                 osnr[idxs_fixed[enhance0+enhance:enhance0]] * 1000
        osnr = np.concatenate(split_snr)

        # 1st fit
        try:
            f_coeffs = np.polyfit(owave,oflux,deg, w=osnr)
            func = np.poly1d(f_coeffs)
            fit = True
        except np.linalg.LinAlgError:
            fit = False
            
        it_wave = owave.copy()
        it_flux = oflux.copy()
        it_snr = osnr.copy()
        if fit:
            residuals = np.fabs(oflux-func(owave))
        else:
            residuals = np.zeros(oflux.shape)
        f_res = np.mean(residuals)

        # iterative fit until it converges:
        # - remove points where flux-fit > 3*res
        # - fit again, re-compute residuals
        # - iterate until no points satisfy condition flux-fit > 3*res
        while fit:
            idxs = np.nonzero(residuals > 3*f_res)

            if idxs[0].size:
                it_flux = np.delete(it_flux, idxs)
                it_wave = np.delete(it_wave, idxs)
                it_snr = np.delete(it_snr, idxs)


                f_coeffs = np.polyfit(it_wave,it_flux,deg, w=it_snr)
                func = np.poly1d(f_coeffs)
                residuals = np.fabs(it_flux-func(it_wave))
                f_res = np.mean(residuals)

            else:
                break

        if fit:
            fnor[ordine] = np.true_divide(oflux , func(owave))
            coeffs[:,i] = f_coeffs
        else:
            fnor[ordine] = oflux
        w_ord[i] = np.average(it_snr)
        i = i+1


    if np.logical_and(fit, refine):
        print('Adjust coefficients')
        # check all coefficients, they must be similar. If not, substitute them.
        deg_check = int(np.sqrt(orange))-1
        for o in range(deg):
            fit_coeff, fit_res, _, _, _ = np.polyfit(np.arange(orange),coeffs[o],\
                                          deg_check , full=True, w=w_ord)
            func_coeff = np.poly1d(fit_coeff)
            idxs_fit = np.nonzero( np.fabs( coeffs[o] - func_coeff(np.arange(orange))) > 3*fit_res)

            if idxs_fit[0].size:
                coeffs[o,idxs_fit] = func_coeff(idxs_fit)
                print(f"wrong fit in order {idxs_fit[0]}")

        # normalise and save result
        i = 0
        for o in np.unique(echelle):
            ordine = np.nonzero(echelle==o)
            owave = wave[ordine]
            oflux = flux[ordine]
            func = np.poly1d(coeffs[:,i])

            fnor[ordine] = np.true_divide(oflux , func(owave))
            i = i+1

    result = np.vstack(( wave , flux , fnor , snr , echelle ))
    if output:
        np.savetxt(output, np.transpose(result), fmt='%10.3f  %15.8f  %15.8f  %10.2f  %i')
    return {'wave': wave, 'flux': flux, 'nflux': fnor, 'snr': snr, 'echelle': echelle}


#######################################################
#  Read the stellar mask, select elements and depths  #
#######################################################
def read_mask(maskname, unit='a', ele=False, no_ele=False, depths=(0.01,1),\
              balmer=True, tellurics=True, wmin=False, wmax=False, absorption=False):
    """
    Read stellar mask (either binary mask, VALD file, or absorption spectrum/model)
    maskname = name of the mask ASCII/FITS file
    unit  = wavelength units, choose between:
            'a': Angstrom (default)
            'n': nanometer
            'm': micron
    ele/no_ele = select elements to use or the exclude in a VALD mask
                 passing the elements as a character string in
                 VALD format, e.g. eles="Fe 1,Fe 2,H 1"
    depths = use only elements with depth between these values
             default = 0.01,1, change it by passing a list, e.g. [0.2,0.8]
    balmer = do not use wavelength regions with Balmer lines
             if True, the mask lines inside those regions will not be used
    tellurics = do not use wavelength regions with tellurics lines
             if True, the mask lines inside those regions will not be used
    wmin = minimum wavelength length to consider, in the SAME units as the mask.
           Lines with wavelength < wmin will not be used
    wmax = maximum wavelength length to consider, in the SAME units as the mask.
           Lines with wavelength > wmax will not be used
    absorption = the mask is a *normalised* absorption spectrum (e.g. a stellar 
           spectrum or a model with absorption lines). Once read, the flux values 
           will be changed to: 
           depths = 1.0 - fluxes
    """
    adjust = {'a': 1, 'n':10, 'm': 10000}
    balmer_regions =[(6460, 6660), (4805, 4925), (3840, 4840)]
    tellurics_regions = [(5880,6050) , (6270, 6330), (6450, 6590), (6860, 7100), \
                 (7160, 7400), (7590, 7700), (7890, 8050),\
                 (9400,10000) , (11100,11700) , (13100,15300) , (17800,20800)]

    #Read a mask: first try read a VALD file, then an ASCII or FITS file
    # Only in the VALD case, use the elements selection
    try:
        with open(maskname,'r') as maskfile:
            row1 = maskfile.readline().split(',')
        ndata = int(row1[2])
        els, wmask, dmask = np.genfromtxt(maskname, dtype=str,\
                 delimiter=',', skip_header=3, max_rows=ndata, \
                 usecols=(0, 1, 9), unpack=True, invalid_raise=False)
        wmask = wmask.astype(float)
        dmask = dmask.astype(float)

        if wmin:
            imin = np.searchsorted(wmask, wmin)
            wmask = wmask[imin:]
            dmask = dmask[imin:]
        if wmax:
            imax = np.searchsorted(wmask, wmax)
            wmask = wmask[:imax]
            dmask = dmask[:imax]

        # Select only lines with the given elements (if ele is given)
        if ele:
            idxs = np.full(els.shape, False, dtype=bool)
            for element in ele:
                element = element.strip("'")
                element = element.strip()
                element = ''.join(("'",element,"'"))
                idxs[np.nonzero(element==els)] = True
            wmask = wmask[idxs]
            dmask = dmask[idxs]
            els = els[idxs]

        # Select only lines without the given elements (if no_ele is given)
        if no_ele:
            idxs = np.full(els.shape, True, dtype=bool)
            for element in no_ele:
                element = element.strip("'")
                element = element.strip()
                element = ''.join(("'",element,"'"))
                idxs[np.nonzero(element==els)] = False
            wmask = wmask[idxs]
            dmask = dmask[idxs]
            els = els[idxs]
    # Try ASCII/FITS file
    except (IndexError, ValueError, UnicodeDecodeError):
        all_mask = read_spectrum(maskname, unit=unit)
        wmask = all_mask['wave']
        dmask = all_mask['flux']
        if absorption:
            dmask = 1.0 - dmask
            #dmask[dmask<0] = 0
        if wmin:
            imin = np.searchsorted(wmask, wmin*adjust[unit])
            wmask = wmask[imin:]
            dmask = dmask[imin:]
        if wmax:
            imax = np.searchsorted(wmask, wmax*adjust[unit])
            wmask = wmask[:imax]
            dmask = dmask[:imax]
        unit = 'a'


    # Select lines base on depths
    depth1 = float(depths[0])
    depth2 = float(depths[1])
    dmax = max(depth1,depth2)
    dmin = min(depth1,depth2)
    idxs = np.nonzero(np.logical_and(dmask >= dmin, dmask <= dmax))
    wmask = wmask[idxs]
    dmask = dmask[idxs]

    wmask = wmask*adjust[unit]

    if balmer:
        for region in balmer_regions:
            idxs = np.nonzero(np.logical_or(wmask < region[0], wmask > region[1]))
            wmask = wmask[idxs]
            dmask = dmask[idxs]
    if tellurics:
        for region in tellurics_regions:
            idxs = np.nonzero(np.logical_or(wmask < region[0], wmask > region[1]))
            wmask = wmask[idxs]
            dmask = dmask[idxs]

    mask = {'wave': wmask, 'depths': dmask}

    return mask

#####################################
#    Auxiliary LDS/CCF functions    #
#####################################

def split_spectrum(spectrum):
    """
    Split the spectrum (dictionary format) according to gaps or
    overlaps in the wavelength
    """
    res0 = np.mean(np.diff(spectrum['wave'][0:50]))
    res1 = np.mean(np.diff(spectrum['wave'][-50:]))
    res = (res0+res1)/2.
    idxs = np.nonzero(np.logical_or(np.diff(spectrum['wave']) > 10*res,\
                          np.diff(spectrum['wave'])<0))[0] + 1
    split_wave = np.array_split(spectrum['wave'], idxs)
    split_flux = np.array_split(spectrum['flux'], idxs)
    for n_split, o_split in enumerate(split_flux):
        split_flux[n_split] = np.nan_to_num(o_split)
    split_nflux = np.array_split(spectrum['nflux'], idxs)
    split_snr = np.array_split(spectrum['snr'], idxs)
    for n_split, s_snr in enumerate(split_snr):
        s_snr[np.isinf(s_snr)] = 0.01
        s_snr[np.isnan(s_snr)] = 0.01
        s_snr[s_snr<=0] = 0.01
        s_snr = np.true_divide(split_flux[n_split], s_snr)

    return split_wave, split_flux, split_nflux, split_snr

def rebin_spectrum(o_wave, o_flux, o_nflux, o_snr, wave_step):
    """
    Rebin the spectrum on the wave_step array
    """

    n_step = int((np.log10(o_wave[-1]/o_wave[0]) + np.log10(wave_step))\
                 /np.log10(wave_step)) + 1
    new_wave = o_wave[0] * np.power(np.full(n_step, wave_step),\
                          np.arange(n_step))
    intflux = interp1d(o_wave, o_flux, kind='cubic', \
                  fill_value=(o_flux[0], o_flux[-1]),\
                  bounds_error=False)
    o_split_flux = intflux(new_wave)
    intnflux = interp1d(o_wave, o_nflux, kind='cubic', \
                  fill_value=(0, 0),\
                  bounds_error=False)
    o_split_nflux = intnflux(new_wave)
    intsnr = interp1d(o_wave, o_snr, kind='cubic', \
                  fill_value=(1.0, 1.0),\
                  bounds_error=False)
    o_split_snr = intsnr(new_wave)

    o_split_snr[np.isinf(o_split_snr)] = 1.0
    o_split_snr[np.isnan(o_split_snr)] = 1.0
    o_split_snr[o_split_snr<=0] = 1.0

    return new_wave, o_split_flux, o_split_nflux, o_split_snr

def remove_cosmics(len_vrange, o_split_nflux, sigma):
    """
    Remove cosmics via sigma clipping
    """
    chunk = max(len_vrange*2, len(o_split_nflux)/20)
    n_chunks = max(int(len(o_split_nflux)/chunk),2)
    subregions = np.array_split(o_split_nflux,n_chunks)
    for sub in subregions:
        sub_masked = sigma_clip(sub, sigma=sigma, masked=True)
        mask = ~sub_masked.mask
        x_range = np.arange(len(sub))
        intflux = interp1d(x_range[mask], sub[mask], kind='linear',\
                          fill_value='extrapolate', \
                          bounds_error=False)
        sub[sub_masked.mask] = intflux(x_range[sub_masked.mask])
    o_split_nflux = np.concatenate(subregions)

    return o_split_nflux

def smooth_spectrum(new_wave, o_split_nflux, fine_step=10):
    """
    Clean the spectrum with a smoothing spline
    """
    smooth_wave = np.linspace(new_wave[0],new_wave[-1], num = int(len(new_wave)*fine_step), endpoint=True)
    smooth_flux = smooth_spline(new_wave, o_split_nflux, smooth_wave)[0]
    intflux = interp1d(smooth_wave, smooth_flux, kind='cubic', \
                  fill_value=(smooth_flux[0], smooth_flux[-1]),\
                  bounds_error=False)
    smooth_flux = intflux(new_wave)

    return smooth_flux

#########################################
#  Compute Least-Squares Deconvolution  #
#########################################
def compute_lsd(spectrum, mask_data, vrange=(-200,200), \
     step=1., cosmic=False, sigma=10, clean=False, verbose=False, output=False):
    """
    Compute Least-Squares Deconvolution
    spectrum: input spectrum as given by read_spectrum
              dictionary with keys "wave", "flux", "nflux", "snr"
    mask_data: input spectrum as given by read_mask
          dictionary with keys "wave", "depths"
    vrange: velocity range in km/s of the resulting profile, given as tuple
    step: velocity step in km/s of the resulting profile
    cosmic: remove cosmic rays from the spectra
    sigma: sigma clipping value for cosmic rays removal
    clean: clean the spectra to reduce noise and improve the profile
    verbose: print descriptive messages
    output: name of the ASCII output file
    """

    v_up = max(vrange[0], vrange[1])
    v_low = min(vrange[0], vrange[1])
    len_vrange = (v_up-v_low)/step
    if len_vrange % 1:
        v_up = v_low + step*(int(len_vrange)+1)

    rv_range = np.arange(v_low, v_up+0.5*step, step)
    v_low = rv_range[0]
    v_up = rv_range[-1]
    len_vrange = len(rv_range)
    wave_step = 1. + (step / ckms)

    # split the spectrum in echelle orders (if any) by looking for changes
    # in the wavelength step
    split_wave, split_flux, split_nflux, split_snr = split_spectrum(spectrum)

    wmask = mask_data['wave']
    dmask = mask_data['depths']

    lsd_results = []
    lsd_errs = []
    lsd_weights = []

    # work on the single orders
    for o, o_wave in enumerate(split_wave):
    # rebin the spectral wavelength array with constant step in velocity
    # and consequently all the other spectral arrays

        if not split_flux[o].any():
            if verbose:
                print(f"Order {o+1}: flux equal to zero, skipped.")
            continue

        new_wave, o_split_flux, o_split_nflux, o_split_snr = rebin_spectrum(o_wave, split_flux[o], split_nflux[o], split_snr[o], wave_step)

        # clean the spectra by removing outliers

        if cosmic:
            o_split_nflux = remove_cosmics(len_vrange, o_split_nflux, sigma)
        if clean:
            o_split_nflux = smooth_spectrum(new_wave, o_split_nflux, 10)


        # select mask lines in the wavelength range of the order
        idxs = np.nonzero(np.logical_and(wmask*(1 + v_low/ckms) > new_wave[5],\
               wmask*(1 + v_up/ckms) < new_wave[-5]))
        mask_wave = wmask[idxs]
        mask_depths = dmask[idxs]
        if len(mask_wave) < 1:
            if verbose:
                print(f"Order {o+1}: not enough mask lines, skipped.")
            continue

        # select only regions of spectra and snr around the mask lines
        profile = np.zeros(rv_range.shape)
        den = np.zeros(rv_range.shape)
        for num_line, line in enumerate(mask_wave):
            line0 = line*(1 + v_low/ckms)
            line1 = line*(1 + v_up/ckms)
            find0 = np.searchsorted(new_wave, line0) - 1
            find1 = np.searchsorted(new_wave, line1, side='right')
            line_spectrum = o_split_nflux[find0:find1+1]
            profile += line_spectrum[:len(profile)]*mask_depths[num_line]
            den += mask_depths[num_line]

        profile /= den
        if not profile.any():
            print(f"Empty profile. Skipped.")
            continue
        ymin = np.amin(profile)
        ymax = np.amax(profile)
        idx_range = np.nonzero(profile < ymax - 0.5*(ymax - ymin))[0]
        broad = max((rv_range[idx_range[-1]] - rv_range[idx_range[0]])/10., 5*step)
        vmin = max(rv_range[idx_range[0]] - broad, rv_range[0])
        vmax = min(rv_range[idx_range[-1]] + broad, rv_range[-1])

        # re-select mask lines in the wavelength range of the order
        idxs = np.nonzero(np.logical_and(wmask*(1 + vmin/ckms) > new_wave[5],\
               wmask*(1 + vmax/ckms) < new_wave[-5]))
        mask_wave = wmask[idxs]
        mask_depths = dmask[idxs]
        if len(mask_wave) < 1:
            if verbose:
                print(f"Order {o+1}: not enough mask lines, skipped.")
            continue

        # adjust mask weights to account for blending
        for num_depth, depth in enumerate(mask_depths):
            idx = np.nonzero(np.fabs(1-(mask_wave/mask_wave[num_depth]))*ckms < 5)
            ptot = np.sum(mask_depths[idx]) - depth
            if ptot > 1:
                mask_depths[idx] = 1./ptot

        # create the mask matrix
        m_col = len(new_wave)
        m_row = len_vrange
        mask_matrix = np.zeros(( m_col,m_row ))
        for num_line, line in enumerate(mask_wave):
            line_range = m_row
            vel_i = False
            find_i = 0
            for v_step in rv_range:
                line0 = line*(1 + v_step/ckms)
                i = np.searchsorted(new_wave, line0)
                if i > 0:
                    if not vel_i:
                        i_start = i
                        vel_i = ckms*(new_wave[i]-line)/line
                    if i > len(new_wave) - 2:
                        line_range += -1
                else:
                    line_range += -1
                    if not vel_i:
                        find_i += 1

            block_diag1 = np.full(line_range, mask_depths[num_line]*(rv_range[find_i+1] - vel_i)/ \
                     (rv_range[find_i+1] - rv_range[find_i]))
            block_diag2 = np.full(line_range-1, mask_depths[num_line]*\
                          (vel_i - rv_range[find_i])/ \
                          (rv_range[find_i+1] - rv_range[find_i]))

            diag1 = (np.array(np.arange(line_range)+i_start-1, dtype=int),\
                     np.array(np.arange(line_range), dtype=int))
            diag2 = (np.array(np.arange(line_range-1)+i_start-1, dtype=int),\
                     np.array(np.arange(line_range-1)+1,dtype=int))

            mask_matrix[diag1] += block_diag1
            mask_matrix[diag2] += block_diag2

        if verbose:
            print(f"Order {o+1}: computed mask matrix")

        # Select only non-zero columns of the mask matrix
        msum = np.sum(mask_matrix, axis=1)
        icols = np.nonzero(msum)
        mask_matrix = mask_matrix[icols]
        o_split_nflux = o_split_nflux[icols]
        o_split_snr = o_split_snr[icols]
        if verbose:
            print(f"Order {o+1}: selected data where the mask matrix columns are not zero")

        # create the SNR matrix
        snr_matrix = np.diag(o_split_snr)

        if verbose:
            print(f"Order {o+1}: computed SNR matrix")

        # compute inverse autocorrelation
        inverse_autocorrelation = np.linalg.inv(np.dot(np.dot(np.transpose\
                                  (mask_matrix), snr_matrix), mask_matrix))

        # compute weighted crosscorrelation
        weighted_crosscorrelation = np.dot(np.dot(np.transpose(mask_matrix), \
                                    (snr_matrix)), \
                                    1. - o_split_nflux)

        # compute LSD and SNR
        lsd_order = np.dot(inverse_autocorrelation, weighted_crosscorrelation)
        lsd_err = np.diag(inverse_autocorrelation)

        lsd_results.append(lsd_order)
        lsd_errs.append(lsd_err)
        lsd_weights.append(np.sum(mask_matrix)*len(mask_wave))
        if verbose:
            print(f"Computed profile for order {o+1}")

    lsd_results = np.asarray(lsd_results)
    lsd_errs = np.asarray(lsd_errs)
    lsd_weights = np.asarray(lsd_weights)
    lsd_results = np.nan_to_num(lsd_results)
    lsd_errs = np.nan_to_num(lsd_errs)
    lsd_errs_mean = np.nanmean(lsd_errs, axis=1)    
    
    LSD = np.average(lsd_results, axis=0, weights=lsd_weights/(lsd_errs_mean**2)) #weighted considering the number of mask lines and the SNR of the order
    LSD_ERR = np.average(lsd_errs, axis=0, weights=lsd_weights/lsd_errs_mean**2)
    LSD = 1. - LSD
    profile = {'rv_range':rv_range, 'profile': LSD, 'error': LSD_ERR}
    if verbose:
        print("Mean line profile computed")

    if output:
        outdata = np.vstack((profile['rv_range'], profile['profile'], profile['error']))
        np.savetxt(output, np.transpose(outdata), fmt='%10.2f %15.10f  %15.10f')
        if verbose:
            print(f"Profile saved in file {output}")
    return profile


########################################
#  Compute Cross-Correlation Function  #
########################################
def compute_ccf(spectrum, mask_data, vrange=(-200,200), step=1., mask_spectrum=False, \
     cosmic=False, sigma=10, clean=False, weights=False, verbose=False, output=False):
    """
    Compute Cross-Correlation Function
    spectrum: input spectrum as given by read_spectrum
              dictionary with keys "wave", "flux", "nflux", "snr"
    mask_data: input spectrum as given by read_mask
          dictionary with keys "wave", "depths"
    vrange: velocity range in km/s of the resulting profile, given as tuple
    step: velocity step in km/s of the resulting profile
    mask_spectrum: if False, the mask is a list of Dirac delta (wavelength and weight/depths)
                   if True, the mask is a spectrum, with continuum and lines
                     --> remember to flag the mask as absorption in the read_mask procedure
                         to switch the continuum from 1 to 0, and the lines from absorption
                         to peaks
    cosmic: remove cosmic rays from the spectra
    sigma: sigma clipping value for cosmic rays removal
    clean: clean the spectra to reduce noise and improve the profile
    weights: if True, use SNR to weight the data
    verbose: print descriptive messages
    output: name of the ASCII output file
    """

    v_up = max(vrange[0], vrange[1])
    v_low = min(vrange[0], vrange[1])
    len_vrange = (v_up-v_low)/step
    if len_vrange % 1:
        v_up = v_low + step*(int(len_vrange)+1)

    rv_range = np.arange(v_low, v_up+0.5*step, step)
    v_low = rv_range[0]
    v_up = rv_range[-1]
    len_vrange = len(rv_range)
    # Do a finer step: fine_step = step/10.0
    fine_step = 0.1*step
    wave_step = 1. + (fine_step / ckms)

    # split the spectrum in echelle orders (if any) by looking for changes
    # in the wavelength step
    split_wave, split_flux, split_nflux, split_snr = split_spectrum(spectrum)

    wmask = mask_data['wave']
    dmask = mask_data['depths']

    ccf_results = []
    ccf_errs = []
    ccf_weights = []

    # work on the single orders
    for o, o_wave in enumerate(split_wave):
    # rebin the spectral wavelength array with constant step in velocity
    # and consequently all the other spectral arrays

        if not split_flux[o].any():
            if verbose:
                print(f"Order {o+1}: flux equal to zero, skipped.")
            continue

        # clean the spectra by removing outliers
        if cosmic:
            split_nflux[o] = remove_cosmics(len_vrange, split_nflux[o], sigma)
        if clean:
            split_nflux[o] = smooth_spectrum(o_wave, split_nflux[o], 10)

        # Interpolate spectrum on finer wavelength range
        new_wave, o_split_flux, o_split_nflux, o_split_snr = rebin_spectrum(o_wave, split_flux[o], split_nflux[o], split_snr[o], wave_step)
        o_split_snr[o_split_snr<=0.1] = 0.1
        o_split_errs = o_split_nflux/o_split_snr
        

        # select mask lines in the wavelength range of the order
        idxs = np.nonzero(np.logical_and(wmask*(1 + v_low/ckms) > new_wave[5],\
               wmask*(1 + v_up/ckms) < new_wave[-5]))
        mask_wave = wmask[idxs]
        mask_depths = dmask[idxs]
        if len(mask_wave) < 1:
            if verbose:
                print(f"Order {o+1}: not enough mask lines, skipped.")
            continue

        
        mask_weight = len(mask_wave)
        ccf_weights.append(np.sum(mask_depths)*mask_weight)

        # Interpolate mask on finer wavelength range

        idxs_wave = np.searchsorted(new_wave, mask_wave)
        o_mask = np.zeros(new_wave.shape)
        o_mask[idxs_wave] = mask_depths
        o_mask_wave = new_wave.copy()
        o_mask_wave[idxs_wave] = mask_wave
        mask_wave = o_mask_wave
        mask_depths = o_mask


        ccf = np.zeros(len(rv_range))
        e_ccf = np.zeros(len(rv_range))
        
        for n, rv in enumerate(rv_range):
            if not weights:
                o_weights = np.ones(o_split_nflux.shape)
            else:
                o_weights = np.nan_to_num(o_split_snr, nan=0.1, posinf=0.1, neginf=0.1)
                o_weights = o_weights/np.nanmax(o_weights)


            rv_mask_wave = mask_wave*(1.0 + rv/ckms)
            rv_mask_depths = np.zeros(len(o_split_nflux))
            where = np.searchsorted(new_wave,rv_mask_wave)
            right = np.minimum(where, len(new_wave) - 1)
            left = np.maximum(where-1, 0)
            
            right_diff = rv_mask_wave - new_wave[right]
            left_diff  = rv_mask_wave - new_wave[left ]
            rv_idxs = np.where(np.abs(right_diff) <= left_diff, right, left)
            rv_mask_depths[rv_idxs] = mask_depths

            inv_nflux = 1.0 - o_split_nflux

            inv_nflux[inv_nflux<0] = 0
            ccf[n] = np.nansum((inv_nflux) * rv_mask_depths * o_weights)/mask_weight
            e_ccf[n] = (np.nansum((o_split_errs) * rv_mask_depths * o_weights)/mask_weight)/np.sqrt(mask_weight)
           
        ccf_results.append(ccf)
        ccf_errs.append(e_ccf)
        
    ccf_errs = np.asarray(ccf_errs)
    ccf_errs = np.nan_to_num(ccf_errs)
    ccf_errs_mean = np.nanmean(ccf_errs, axis=1)
        
    ccf_results = np.asarray(ccf_results)
    ccf_results = np.nan_to_num(ccf_results)
    CCF = np.average(ccf_results, axis=0, weights=ccf_weights/(ccf_errs_mean**2))
    CCF = 1. - CCF
    
    CCF_ERR = np.average(ccf_errs, axis=0, weights=ccf_weights/(ccf_errs_mean**2))
    
    profile = {'rv_range':rv_range, 'profile': CCF, 'error': CCF_ERR}
    if verbose:
        print("Cross-correlation profile computed")

    if output:
        outdata = np.vstack((profile['rv_range'], profile['profile'], profile['error']))
        np.savetxt(output, np.transpose(outdata), fmt='%10.2f %15.10f %15.10f')
        if verbose:
            print(f"Profile saved in file {output}")

    return profile        
        

#########################################
#  Plot profile and define line limits  #
#########################################
def show_ccf(rvs,ccfs):
    """
    Plot line profiles and define line limits
    rvs: array with n radial velocities ranges
    ccfs: array with n mean line profiles
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i, ccf in enumerate(ccfs):
        ax.plot(rvs[i],ccf/np.mean(ccf))
    ax.set_title('Click on the figure to define the line region')

    coords = []

    def onclick(event):
        ix = event.xdata
        print('x = %f'%(ix))
        ax.axvline(x=ix)
        fig.canvas.draw()

        coords.append(ix)

        if len(coords) == 2:
            fig.canvas.mpl_disconnect(cid)
            plt.close()

    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    print("Click on the figure to define the line region.")

    plt.show()

    return coords


#########################################################
#  Convert a single line to a pseudo mean line profile  #
#########################################################
def extract_line(spectrum, unit='a', w0=6562.801, vrange=(-200,200), step=0.5, verbose=False, output=False):
    """
    Extract a single line from a spectrum at w0 as a mean line profile
    convert the wavelength to RVs using w0 as RV=0
    extract only the region inside vrange, with the required step
    Input:
        spectrum = input spectrum as given by read_spectrum
              dictionary with keys "wave", "flux", "nflux", "snr"
        unit  = wavelength units, choose between:
            'a': Angstrom (default)
            'n': nanometer
            'm': micron
        w0 = wavelength of the line to be extracted (default: halpha_air = 6562.801)
            if needed: halpha_vacuum = 6564.614
            IMPORTANT: must be in the same unit as "unit"
        vrange = region of the spectrum to be extracted around w0 (RV=0)
        step = RV step of the extracted profile
        verbose: print descriptive messages
        output: name of the ASCII output file
    Output:
        the profile as a dcitionary (same format as compute_lsd and compute_ccf)
           -->  profile = {'rv_range':rv_range, 'profile': data, 'error': error}
        if output=filename the profile is saved as an ASCII file with the name "filename"
    """

    # read the input on RV range and step, 
    # adjust the RV range in the correct order of start-end RV 
    v_up = max(vrange[0], vrange[1])
    v_low = min(vrange[0], vrange[1])
    len_vrange = (v_up-v_low)/step
    if len_vrange % 1:
        v_up = v_low + step*(int(len_vrange)+1)

    # create RV range of the extracted profile
    rv_range = np.arange(v_low, v_up+0.5*step, step)
    v_low = rv_range[0]
    v_up = rv_range[-1]

    # define a spectral regione wider than the vrange
    start_extraction = v_low - (0.2*abs(v_up-v_low))
    end_extraction = v_up + (0.2*abs(v_up-v_low))
    
    step_low = 1. + (start_extraction / ckms)
    step_up = 1. + (end_extraction / ckms)
    # convert RV start and end of the wider region in wavelength 
    wave_low = w0*step_low
    wave_up = w0*step_up
    
    # prepare the wavelength range for the extracted profile
    # with wavelength width and step equivalent to the RV range 
    step_range = 1. + (rv_range / ckms)
    wave_range = w0*step_range
    
    # read spectrum arrays
    wave = spectrum['wave']
    flux = spectrum['nflux']
    snr = spectrum['snr']
    
    # define the region needed
    idx_low = np.searchsorted(wave,wave_low)
    idx_up = np.searchsorted(wave,wave_up)
    
    # interpolate the extracted flux and SNR to the RV range
    intnflux = interp1d(wave[idx_low:idx_up], flux[idx_low:idx_up], kind='cubic', \
                  fill_value=(0, 0),\
                  bounds_error=False)
    new_line = intnflux(wave_range)
    intsnr = interp1d(wave[idx_low:idx_up], snr[idx_low:idx_up], kind='cubic', \
                  fill_value=(1.0, 1.0),\
                  bounds_error=False)

    new_snr = intsnr(wave_range)
    new_snr = np.nan_to_num(new_snr,nan=0.1, posinf=0.1, neginf=0.1)
    new_snr[new_snr<=0] = 0.1
    new_err = new_line/new_snr

    profile = {'rv_range':rv_range, 'profile': new_line, 'error': new_err, 'wave_range': wave_range}
    if verbose:
        print("Line extracted")

    if output:
        outdata = np.vstack((profile['rv_range'], profile['profile'], profile['error'], profile['wave_range']))
        np.savetxt(output, np.transpose(outdata), fmt='%10.2f %15.10f %15.10f %15.10f ')
        if verbose:
            print(f"Profile saved in file {output}")

    return profile

##############################################
#  Normalise the profile(s) from ASCII/FITS  #
##############################################
def norm_profile(profiles, rvcol=1, prfcol=2, errcol=0, sfx='pfn', std='line_mean_std', limits=False):
    """
    Normalise the profiles to account for continuum problems.
    profiles : list of profile ASCII filenames (rv, flux, [error])
               or FITS BinTable (RV_RANGE, PROFILE, ERROR)
    *col: column/field of the data (value-1), if 0 the data is missing
    sfx : suffix of the normalised profiles. If False/0/None, no file will be created
    std : if present, the mean of the normalised profiles and the standard
          deviation are computed and saved both as ASCII file and PNG
          If False/0/None, it will be skipped
    limits: line limits, given as a tuple (rv_min,rv_max)
    """
    rvs = []
    ccfs = []
    errs = []
    heas = []
    nors = []
    stds = []


    try:
        for name in profiles:
            name = name.strip()
            try:
                with fits.open(name) as hdu:
                    data = hdu[1].data
                    head = hdu[0].header
                rvs.append(data.field(int(rvcol-1)))
                ccfs.append(data.field(int(prfcol-1)))
                if errcol:
                    errs.append(data.field(int(errcol-1)))
                else:
                    errs.append(np.zeros(data[rvcol-1].shape))

            except OSError:
                head = fits.PrimaryHDU().header
                data = np.loadtxt(name, unpack=True)
                rvs.append(data[rvcol-1])
                ccfs.append(data[prfcol-1])
                if errcol:
                    errs.append(data[errcol-1])
                else:
                    errs.append(np.zeros(data[rvcol-1].shape))
            heas.append(head)        
    except OSError:
        name = profiles
        profiles = [profiles]
        try:
            with fits.open(name) as hdu:
                data = hdu[1].data
                head = hdu[0].header
            rvs.append(data.field(int(rvcol-1)))
            ccfs.append(data.field(int(prfcol-1)))
            errs.append(data.field(int(errcol-1)))
        except OSError:
            head = fits.PrimaryHDU().header
            data = np.loadtxt(name, unpack=True)
            rvs.append(data[rvcol-1])
            ccfs.append(data[prfcol-1])
            if errcol:
                errs.append(data[errcol-1])
            else:
                errs.append(np.zeros(data[rvcol-1].shape)) 
        heas.append(head)        
    rvs = np.asarray(rvs)
    ccfs = np.asarray(ccfs)
    errs = np.asarray(errs)
    norccfs = np.zeros(ccfs.shape)

    if not limits:
        limits = show_ccf(rvs,ccfs)

    for idx, ccf in enumerate(ccfs):
        # normalise line
        x_1 = np.searchsorted(rvs[idx],float(limits[0]))
        x_2 = np.searchsorted(rvs[idx],float(limits[1]))
        x1 = min(x_1,x_2)
        x2 = max(x_1,x_2)
        x2 = min(x2+1, len(rvs[idx])-1)

        idxarray = np.zeros(ccf.shape, dtype=bool)
        idxarray[0:x1-1] = True
        idxarray[x2+1:-1] = True

        linfit = np.poly1d(np.polyfit(rvs[idx][idxarray],ccf[idxarray],1))
        fitvalues = linfit(rvs[idx])
        norccfs[idx] = ccf/fitvalues

        nors.append({'rv_range':rvs[idx], 'nprofile' : norccfs[idx], 'error': errs[idx], 'profile': ccfs[idx], 'header' : head})
        if sfx:
            pfn = '.'.join((os.path.splitext(profiles[idx])[0], sfx))
            outpfn = np.vstack((rvs[idx], norccfs[idx] , errs[idx]))
            np.savetxt( pfn , np.transpose(outpfn))

    if std:
        outname = '.'.join((std,'txt'))
        outpng = '.'.join((std,'png'))
        if len(norccfs) > 1:
            ccf_mean = np.nanmean(norccfs, axis=0)
            rv_mean = np.nanmean(rvs, axis=0)
            std_dev = np.nanstd(norccfs, axis=0)
        else:
            ccf_mean = norccfs[0]
            rv_mean = rvs[0]
            std_dev = np.zeros(norccfs[0].shape)

        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        ax1.plot(rv_mean, ccf_mean, 'k-')
        ax1.set_ylabel('Normalised flux')
        ax1.set_title('CCF mean')
        ax2 = fig.add_subplot(212)
        ax2.plot(rv_mean, std_dev, 'k-')
        ax2.set_xlabel('Doppler velocity (km/s)')
        ax2.set_ylabel('Standard deviation')
        plt.savefig(outpng)
        plt.close()

        output = np.vstack((rv_mean, ccf_mean, std_dev))

        np.savetxt( outname, np.transpose(output))
        stds = {'rv_mean': rv_mean, 'ccf_mean': ccf_mean, 'std_dev': std_dev}

    return nors, stds


############################
# Define fitting functions #
############################
def func_rot(x,c,a,x0,xl,ld=0.6):
    """
    Rotational broadening function, from:
    Gray, D. F. 2008, The Observation and Analysis of Stellar Photospheres
    x: dataset
    c: continuum level
    a: depth of the line (initial guess value)
    x0: center of the line (RV, initial guess value)
    xl: width of the line (vsini, initial guess value))
    ld: linear limb darkening, default value 0.6
    """
    condlist = [(x-x0)**2 < xl**2, (x-x0)**2 > xl**2]

    funclist = [lambda x:c+a*( 2*(1-ld)*(np.sqrt(1-((x-x0)/(xl))**2)) + \
        0.5*np.pi*ld*(1-((x-x0)/(xl))**2))/(np.pi*xl*(1-ld/3)), lambda x:c]

    return np.piecewise(x, condlist, funclist)

def gaussian(x,x0,s,F0,K):
    """
    Gaussian function
    x: dataset
    x0: center of the line (RV, initial guess value)
    s: Gaussian sigma (initial guess value))
    F0: depth of the line (initial guess value)
    K: continuum mean value (initial guess value)
    NOTE: FWHM of the Gaussian is 2*np.sqrt(2*np.log(2))*s
    """
    return K - F0*np.exp(-((x-x0)**2)/(2*(s**2)))


def lorentzian(x, x0, g, F0, K):
    """
    Lorentzian function
    x: dataset
    x0: center of the line (RV, initial guess value)
    g: Lorentzian width (initial guess value))
    F0: depth of the line (initial guess value)
    K: continuum mean value (initial guess value)
    NOTE: FWHM of the Lorentzian is 2*g
    Equation taken from https://www.linkedin.com/pulse/fitting-spectral-lines-gaussian-versus-lorentzian-voigt-aulin
    """
    return K + F0 * g**2 / ( g**2 + ( x - x0 )**2)  
    

def voigt_function(x, x0, g, s, F0, K):    
    """
    Voigt function
    x: dataset
    x0: center of the line (RV, initial guess value)
    g: Lorentzian width (initial guess value))
    s: Gaussian sigma (initial guess value))
    F0: depth of the line (initial guess value)
    K: continuum mean value (initial guess value)
    NOTE: FWHM of the Voigt is 0.5346 * fL  + np.sqrt( 0.2166 * fL**2 + fG**2)
    where fL = 2*g
    and fG = 2*np.sqrt(2*np.log(2))*s
    Equation taken from https://www.linkedin.com/pulse/fitting-spectral-lines-gaussian-versus-lorentzian-voigt-aulin
    """

    return K + F0 * np.real(wofz((x - x0 + 1j*g)/s/np.sqrt(2))) / s /np.sqrt(2*np.pi) 

##################################
# Fitting the mean line profiles #
##################################
def fit_profile(vrad, flux, errs=0, gauss=True, lorentz=True, voigt=True, rot=True, rv0=0, width=10, ld=0.6):
    """
    Fit a mean line profile
    vrad: vrad range of the profile
    flux: profile values
    gauss: fit with a Gaussian
    lorentz: fit with a Lorentzian
    voigt: fit with a Voigt profile
    rot: fit with a rotational profile
    rv0: initial guess value of RV in km/s
    width = initial guess value of vsini in km/s
    ld = linear limb darkening (for rotational fit)
    Gaussian fit: compute also the EW of the normalised Gaussian
    READ THIS: https://www.linkedin.com/pulse/fitting-spectral-lines-gaussian-versus-lorentzian-voigt-aulin
    """
    massimo = np.amax(flux)
    minimo = np.amin(flux)
    f_0 = massimo-minimo
    

    if np.sum(errs):
        best = np.nanmin(errs[errs>0])
        worst = np.nanmax(errs[errs>0])*10
        errs[errs<=0] = best
        errs = np.nan_to_num(errs, nan=worst, posinf=worst, neginf=worst)
        err_abs=True
    else:
        errs = np.ones(len(flux))
        err_abs=False


    p_rot = [0.,f_0,rv0,width,ld]
    p_gauss = [rv0,width,f_0,massimo]
    p_voigt = [rv0,width,width,f_0,massimo]    
    if rot:
        try:
            popt_rot,pcov_rot = curve_fit(func_rot, vrad, 1-flux, p0=p_rot, sigma=errs, absolute_sigma=err_abs)
        except (ValueError, RuntimeError):
            popt_rot = np.zeros(len(p_rot))
            pcov_rot = np.zeros((len(p_rot),len(p_rot)))
        error_rot = np.sqrt(np.diag(pcov_rot))

        x_1 = np.searchsorted(vrad,popt_rot[2]-popt_rot[3])
        x_2 = np.searchsorted(vrad,popt_rot[2]+popt_rot[3], side='right')
        x_2 = min(x_2,len(vrad)-1)

        r_EW = simpson(func_rot(vrad[x_1:x_2], *popt_rot), x=vrad[x_1:x_2]) # equivalent width   
        
        std_r_EW = np.nanstd(1-flux[x_1:x_2] - func_rot(vrad[x_1:x_2], *popt_rot))
        h = abs(np.nanmean(np.diff(vrad)))
        e_r_EW = h*np.sqrt(len(vrad[x_1:x_2]))*std_r_EW
        r_fit = {'profile': 1.-func_rot(vrad, *popt_rot),
                 'rv': popt_rot[2], 'e_rv': error_rot[2],\
                 'vsini': popt_rot[3], 'e_vsini': error_rot[3],\
                 'EW': r_EW, \
                 'e_EW': e_r_EW}
    else:
        r_fit = {'profile': np.ones(flux.shape),
                 'rv': 0, 'e_rv': 0,\
                 'vsini': 0, 'e_vsini': 0,\
                 'EW': 0, \
                 'e_EW': 0}
    if gauss:
        try:
            popt_gauss,pcov_gauss = curve_fit(gaussian, vrad, flux, p0=p_gauss, bounds=((-np.inf,0,-np.inf,-np.inf),(np.inf,np.inf,np.inf,np.inf)), sigma=errs, absolute_sigma=err_abs)
        except (ValueError, RuntimeError):
            popt_gauss = np.zeros(len(p_gauss))
            pcov_gauss = np.zeros((len(p_gauss),len(p_gauss)))
        error_gauss = np.sqrt(np.diag(pcov_gauss))
        gauss_center = ufloat(popt_gauss[0],error_gauss[0])
        gauss_sigma = ufloat(popt_gauss[1],error_gauss[1])
        gauss_depth = ufloat(popt_gauss[2],error_gauss[2])
        gauss_continuum = ufloat(popt_gauss[3],error_gauss[3])
        
        # Compute EW
        # 1. normalise the Gaussian F0 --> F0/K

        u_Hg = gauss_depth/gauss_continuum
        un_Hg = ufloat(abs(u_Hg.n),u_Hg.s)
        # 2. Compute the area: Hg*sigma*sqrt(2*np.pi)

        un_Ag = un_Hg*gauss_sigma*np.sqrt(2*np.pi)


        g_fit = {'profile': gaussian(vrad, *popt_gauss),
                 'rv': popt_gauss[0], 'e_rv': error_gauss[0],\
                 'fwhm': popt_gauss[1]*np.sqrt(8*np.log(2)), \
                 'e_fwhm': error_gauss[1]*np.sqrt(8*np.log(2)), \
                 'EW': un_Ag.n, \
                 'e_EW': un_Ag.s}

    else:
        g_fit = {'profile': np.ones(flux.shape),
                 'rv': 0, 'e_rv': 0,\
                 'fwhm': 0, \
                 'e_fwhm': 0, \
                 'EW': 0, \
                 'e_EW': 0}
    if lorentz:
        try:
            popt_lor,pcov_lor = curve_fit(lorentzian, vrad, flux, p0=p_gauss, bounds=((-np.inf,0,-np.inf,-np.inf),(np.inf,np.inf,np.inf,np.inf)), sigma=errs, absolute_sigma=err_abs)
        except (ValueError, RuntimeError):
            popt_lor = np.zeros(len(p_gauss))
            pcov_lor = np.zeros((len(p_gauss),len(p_gauss)))
        error_lor = np.sqrt(np.diag(pcov_lor))
        lor_center = ufloat(popt_lor[0],error_lor[0])
        lor_gamma = ufloat(popt_lor[1],error_lor[1])
        lor_depth = ufloat(popt_lor[2],error_lor[2])
        lor_continuum = ufloat(popt_lor[3],error_lor[3])        
        
        # Compute EW
        # 1. normalise the Lorentzian F0 --> F0/K
        Hl =  np.fabs(popt_lor[2]/popt_lor[3])
        e_Hl = Hl*np.sqrt( (error_lor[2]/popt_lor[2])**2 + (error_lor[3]/popt_lor[3])**2 )
        u_Hl = lor_depth/lor_continuum
        un_Hl = ufloat(abs(u_Hl.n), u_Hl.s)
        # 2. Compute the area: (np.pi/2)*Hf*fwhm
        Al = (np.pi/2) * Hl * 2*popt_lor[1]
        # 3. Propagate fit error on area
        Al_err = Al*np.sqrt( ((np.pi/2)*(2*error_lor[1]/popt_lor[1])**2 + (e_Hl/Hl)**2 ))
        un_Al = (np.pi/2) * un_Hl * 2*lor_gamma

        l_fit = {'profile': lorentzian(vrad, *popt_lor),
                 'rv': popt_lor[0], 'e_rv': error_lor[0],\
                 'fwhm': 2*popt_lor[1], \
                 'e_fwhm': 2*error_lor[1], \
                 'EW': un_Al.n, \
                 'e_EW': un_Al.s}

    else:
        l_fit = {'profile': np.ones(flux.shape),
                 'rv': 0, 'e_rv': 0,\
                 'fwhm': 0, \
                 'e_fwhm': 0, \
                 'EW': 0, \
                 'e_EW': 0}
                 
    if voigt:
        try:
            popt_voigt,pcov_voigt = curve_fit(voigt_function, vrad, flux, p0=p_voigt, bounds=((-np.inf,0,0,-np.inf,-np.inf),(np.inf,np.inf,np.inf,np.inf,np.inf)), sigma=errs, absolute_sigma=err_abs)
        except (ValueError, RuntimeError):
            popt_voigt = np.zeros(len(p_voigt))
            pcov_voigt = np.zeros((len(p_voigt),len(p_voigt)))
        error_voigt = np.sqrt(np.diag(pcov_voigt))
        voigt_center = ufloat(popt_voigt[0],error_voigt[0])
        voigt_sigma = ufloat(popt_voigt[1],error_voigt[1])
        voigt_gamma = ufloat(popt_voigt[2],error_voigt[2])
        voigt_depth = ufloat(popt_voigt[3],error_voigt[3])
        voigt_continuum = ufloat(popt_voigt[4],error_voigt[4])          
               
        fL = 2*popt_voigt[2]
        fG = np.sqrt(8*np.log(2))*popt_voigt[1]
        fwhm_voigt = 0.5346 * fL  + np.sqrt( 0.2166 * fL**2 + fG**2)
        e_fwhm_voigt = 0
        un_fL = 2*voigt_gamma
        un_fG = np.sqrt(8*np.log(2))*voigt_sigma
        un_fwhm_voigt = 0.5346 * un_fL  + umath.sqrt( 0.2166 * un_fL**2 + un_fG**2)
        
        # Compute EW

        v_EW = simpson(popt_voigt[4]-voigt_function(vrad, *popt_voigt), x=vrad) # equivalent width
        
        std_v_EW = np.nanstd(flux - voigt_function(vrad, *popt_voigt))
        h_v = abs(np.nanmean(np.diff(vrad)))
        Av_err = h_v*np.sqrt(len(vrad))*std_v_EW

        v_fit = {'profile': voigt_function(vrad, *popt_voigt),
                 'rv': popt_voigt[0], 'e_rv': error_voigt[0],\
                 'fwhm': un_fwhm_voigt.n, \
                 'e_fwhm': un_fwhm_voigt.s, \
                 'EW': v_EW, \
                 'e_EW': Av_err}
        
    else:
        v_fit = {'profile': np.ones(flux.shape),
                 'rv': 0, 'e_rv': 0,\
                 'fwhm': 0, \
                 'e_fwhm': 0, \
                 'EW': 0, \
                 'e_EW': 0}

    return {'gaussian': g_fit, 'rotational': r_fit, 'lorentzian': l_fit, 'voigt': v_fit}

############################
# Compute the line moments #
############################
def moments(rvs, ccf, errs=0, limits=False, normalise=True):
    """
    Compute the line moments
    rvs: array with radial velocity range
    ccf: array with mean line profile
    errs: is given, the real errors are used to compute the error on the moments
          otherwise the StDev of the continuum will be used
    limits: line limits, given as a tuple (rv_min,rv_max)
            if not given, they will be selected on an interactive plot
    normalise: the line will be normalised using the limits
    """

    if not limits:
        limits = show_ccf([rvs],[ccf])

    x1 = np.searchsorted(rvs,float(limits[0]))
    x2 = np.searchsorted(rvs,float(limits[1]))
    x_1 = min(x1,x2)
    x_2 = max(x1,x2)
    x_2 = min(x_2+1, len(rvs)-2)
    x_1 = max(x1,2)

    idxarray = np.zeros(ccf.shape, dtype=bool)
    idxarray[1:x_1] = True
    idxarray[x_2+1:-1] = True

    # 1. normalise line
    if normalise:
        linfit = np.poly1d(np.polyfit(rvs[idxarray],ccf[idxarray],1))
        fitvalues = linfit(rvs)
        norccf = 1.0 - (ccf/fitvalues)
    else:
        norccf = 1.0 - ccf



    # 2. compute moments (https://www.aanda.org/articles/aa/full/2003/05/aa3122/node2.html)
    # https://spectral-cube.readthedocs.io/en/latest/moments.html
    # https://en.wikipedia.org/wiki/Moment_(mathematics)
    # m0 = EW
    # m1 = radial velocity
    # m2 = variance (velocity dispersion: width of the spectral line, sigma = sqrt(m2), FWHM = sqrt(8*ln(2))*sigma)
    # m3 = seed for skewness
    # m4 = seed for kurtosis

    eqw = simpson(norccf[x_1:x_2], x=rvs[x_1:x_2]) # equivalent width, m0
    m_1 = np.true_divide(simpson(np.multiply(rvs[x_1:x_2],norccf[x_1:x_2]), x=rvs[x_1:x_2]), eqw)
    m_2 = np.true_divide( simpson( np.multiply( (rvs[x_1:x_2]-m_1)**2 , norccf[x_1:x_2] ) \
                          , x=rvs[x_1:x_2]), eqw)
    m_3 = np.true_divide(simpson(np.multiply( (rvs[x_1:x_2]-m_1)**3,norccf[x_1:x_2]), \
               x=rvs[x_1:x_2] ), eqw)
    m_4 = np.true_divide(simpson(np.multiply( (rvs[x_1:x_2]-m_1)**4,norccf[x_1:x_2]), \
               x=rvs[x_1:x_2] ), eqw)

    # 3. compute statistical uncertainties on moments
    # https://iopscience.iop.org/article/10.3847/2515-5172/ab2125

    if np.sum(errs):
        sigma_i = errs[x_1:x_2]
    else:
        sigma = np.nanstd(norccf[idxarray])
        sigma_i = np.ones(norccf[x_1:x_2].shape)*sigma
    

    deltav02 = simpson(np.power(sigma_i,2), x=rvs[x_1:x_2])
    errm0 = np.sqrt( deltav02 )
    
    deltav12 = simpson(np.multiply(sigma_i**2, (rvs[x_1:x_2]-m_1)**2), x=rvs[x_1:x_2])
    errm1 = np.sqrt( abs(deltav12) )
        
    deltav22 = simpson(np.multiply(sigma_i**2, ((((rvs[x_1:x_2]-m_1)**2) - m_2)**2)), x=rvs[x_1:x_2])
    errm2 = np.sqrt( abs(deltav22) )

    deltav32 = simpson(np.multiply(sigma_i**2, ((((rvs[x_1:x_2]-m_1)**3) - m_3)**2)), x=rvs[x_1:x_2])
    errm3 = np.sqrt( abs(deltav32) )
    
    deltav42 = simpson(np.multiply(sigma_i**2, ((((rvs[x_1:x_2]-m_1)**4) - m_4)**2)), x=rvs[x_1:x_2])
    errm4 = np.sqrt( abs(deltav42) )

    u_sigma = ufloat(np.sqrt(abs(m_2)), 0.5*errm2/np.sqrt(abs(m_2)))
    u_m2_fwhm = u_sigma*np.sqrt(8*np.log(2))
    u_m3 = ufloat(m_3, errm3)
    u_m3_skewness = u_m3/u_sigma**3
    u_m4 = ufloat(m_4, errm4)
    u_m4_kurtosis = u_m4/u_sigma**4
  

    return {'m0': eqw, 'e_m0': errm0, 'm1': m_1, 'e_m1': errm1, \
            'm2': m_2, 'e_m2': errm2, 'm3': m_3, 'e_m3': errm3,  'm4': m_4, 'e_m4': errm4, \
            'fwhm' : u_m2_fwhm.n, 'e_fwhm' : u_m2_fwhm.s, 'skewness' : u_m3_skewness.n, \
            'e_skewness' : u_m3_skewness.s, 'kurtosis' : u_m4_kurtosis.n, 'e_kurtosis' : u_m4_kurtosis.s}

#############################
# Compute the line bisector #
#############################
def bisector(rv_range, flux, errs=0, limits=False):
    """
    Compute the bisector of a stellar line profile
    rv_range: radial velocity array
    flux: line profile flux
    limits: line limits, given as a tuple (rv_min,rv_max)
    Errors and definition from: https://www.aanda.org/articles/aa/full_html/2011/11/aa17740-11/aa17740-11.html
    """

    if not limits:
        limits = show_ccf([rv_range],[flux])


    # 1. normalise line
    x1 = np.searchsorted(rv_range,float(limits[0]))
    x2 = np.searchsorted(rv_range,float(limits[1]))
    x_1 = min(x1,x2)
    x_2 = max(x1,x2)
    x_2 = min(x_2+1, len(rv_range)-1)

    # If no errors are given, define them from the continuum of the line
    if not np.sum(errs):
        idxarray = np.zeros(flux.shape, dtype=bool)
        idxarray[0:x_1] = True
        idxarray[x_2+1:] = True

        errs = np.ones(flux.shape)*np.nanstd(flux[idxarray])


    # Define the line (depth and width) and compute the bisector
    line_flux = flux[x_1:x_2]
    line_rv = rv_range[x_1:x_2]
    line_errs = errs[x_1:x_2]

    f_min = np.amin(line_flux)
    f_max = np.amax(line_flux)
    imin = np.argmin(line_flux)

    rv_left = np.flip(line_rv[:imin+1])
    f_left = np.flip(line_flux[:imin+1])
    e_left = np.flip(line_errs[:imin+1])

    rv_right = line_rv[imin:]
    f_right = line_flux[imin:]
    e_right = line_errs[imin:]

    f_range = np.linspace(f_min, f_max, 100)

    bisvel = []
    err_bisvel = []

    for n, f_step in enumerate(f_range):
        left = np.nonzero(f_left >= f_step)[0]
        try:
            left=left[0]
        except IndexError:
            f_range = f_range[:n]
            break
                
        res = linregress(rv_left[max(left-1,0):min(len(rv_left-1),left+2)],f_left[max(left-1,0):min(len(rv_left-1),left+2)])
        #res.intercept + res.slope
        #f_step = res.intercept + res.slope*v_left
        v_left = (f_step - res.intercept)/res.slope
        with np.errstate(invalid='ignore'):
            err_left = (1/np.sqrt(2)) * e_left[left] * (1/(res.slope))
        

        right = np.nonzero(f_right >= f_step)[0]
        try:
            right=right[0]
        except IndexError:
            f_range = f_range[:n]
            break

        res = linregress(rv_right[max(right-1,0):min(len(rv_right-1),right+2)],f_right[max(right-1,0):min(len(rv_right-1),right+2)])
        #res.intercept + res.slope
        #f_step = res.intercept + res.slope*v_right
        v_right = (f_step - res.intercept)/res.slope
        with np.errstate(invalid='ignore'):
            err_right = (1/np.sqrt(2)) * e_right[right] * (1/(res.slope))            

        bisvel.append(0.5*(v_right + v_left))
        
        with np.errstate(invalid='ignore'):
            err_bisvel.append(0.5*np.sqrt(err_left**2 + err_right**2))

    bisvel = np.asarray(bisvel)
    err_bisvel = np.asarray(err_bisvel)
    bispan = np.nanmean(bisvel[10:41]) - np.nanmean(bisvel[55:91])
    err_bispan = 0.5*np.sqrt((np.sum(err_bisvel[10:41])/len(err_bisvel[10:41])**2) + (np.sum(err_bisvel[55:91])/len(err_bisvel[55:91])**2))

    bis_results = {'bisvel' : bisvel, 'bisflux' : f_range, 'biserr' : err_bisvel, 'bispan' : bispan, 'e_bispan' : err_bispan}

    return bis_results

######################################################
# Find the shift between 2 curves (using in fourier) #
######################################################
def find_shift_fft(y1, y2):
    """
    Obtained from AI Overview (as long as it works...)
    """
    # Ensure y1 and y2 have same length for FFT correlation
    # Pad the shorter one if necessary, or resample
    N = len(y1)
    X = fft(y1, N)
    Y = fft(y2, N)
    cross_corr = ifft(X * np.conj(Y))
    shift = np.argmax(np.abs(cross_corr))
    # Adjust shift if it wraps around (negative shift)
    if shift > N // 2:
        shift -= N
    return shift


###########################################
# Compute the Fourier transform and vsini #
###########################################
def fourier(rv_range, flux, errs=False, limits=False, ld=0.6):
    """
    https://www.great-esf.eu/AstroStats13-Python/numpy/scipy_fft.html
    Compute the Fourier transform
    rv_range: array with radial velocity range
    flux: array with mean line profile
    errs: array with errors (if not given, the errors will be computed)
    limits: line limits, given as a tuple (rv_min,rv_max)
    ld: linear limb darkening coefficient (for vsini estimation)
    """

    # Empiric formula for vsini estimation taken from:
    # Dravins, D., Lindegren, L., & Torkelsson, U. 1990, A&A, 237, 137
    q1=0.61 + 0.062*ld + 0.027*ld**2 + 0.012*ld**3 + 0.004*ld**4
    q2=1.117 + 0.048*ld + 0.029*ld**2 + 0.024*ld**3 + 0.012*ld**4
    q3=1.619 + 0.039*ld + 0.026*ld**2 + 0.031*ld**3 + 0.020*ld**4

    q = [q1,q2,q3]

    if not limits:
        limits = show_ccf([rv_range],[flux])

    x_1 = np.searchsorted(rv_range,float(limits[0]))
    x_2 = np.searchsorted(rv_range,float(limits[1]))
    x1 = min(x_1,x_2)
    x2 = max(x_1,x_2)
    x2 = min(x2+1, len(rv_range)-1)

    # Extract the line
    rv_line = rv_range[x1:x2]
    line = flux[x1:x2]
    ori_step = rv_line[1]- rv_line[0]

    if np.nansum(errs):
        err_medio = np.nanmean(errs)
    else:
        # Define the continuum region
        idxarray = np.zeros(flux.shape, dtype=bool)
        idxarray[0:x1-1] = True
        idxarray[x2+1:] = True
        err_medio = np.std(flux[idxarray])

    # Interpolate the line and the error on a finer step (x10)
    finestep = len(rv_line)*10
    if not finestep % 2:
        finestep = finestep+1
    rv_fine, step_fine = np.linspace(rv_line[0], rv_line[-1], finestep, retstep=True)
    intflux = interp1d(rv_line, line, kind='cubic', fill_value=1.0)
    line_fine = intflux(rv_fine)
    rv_middle = rv_fine[int(finestep/2)]

    # Create a mirror line
    fine_line = line_fine[::-1]

    # Find the center of the line
    shift = find_shift_fft(line_fine, fine_line)

    # Combine line and mirror line to symmetrize the line
    fine_rv = rv_fine + shift

    # recover original step
    v_low = min(rv_fine[0], fine_rv[0])
    v_up = max(rv_fine[-1], fine_rv[-1])
    n_step = int((v_up-v_low)/ori_step)
    rv_def, step = np.linspace(v_low, v_up, n_step+1, retstep=True)
    intline = interp1d(rv_fine, line_fine, kind='cubic', fill_value=1.0, bounds_error=False)
    line_fine = intline(rv_def)
    intiline = interp1d(fine_rv, fine_line, kind='cubic', fill_value=1.0, bounds_error=False)
    fine_line = intiline(rv_def)

    # Create the symmetric line
    line = 0.5*(line_fine + fine_line)

    line = 1. - line
    new_length = 100*len(line)
    line_fft = np.abs(fft(line,n=new_length))**2

    x_fft = fftfreq(len(line_fft),d=step)
    keep = x_fft>=0 # only positive frequencies
    x_fft, line_fft = x_fft[keep], line_fft[keep]

    neg_to_pos = (np.diff(line_fft[:-1])<=0) & (np.diff(line_fft[1:])>=0)
    minima = x_fft[1:-1][neg_to_pos]
    m_idx = np.nonzero(neg_to_pos)[0]
    check_fft = line_fft/line_fft.max()

    vsini = q/minima[:3]
    e_vsini = np.ones(3)
    e_minima = np.ones(3)
    for n in range(len(e_vsini)):
        for k in range(m_idx[n],1,-1):
            if check_fft[1:-1][k] > err_medio**2:
                fr_left = x_fft[1:-1][k]
                break
        for k in range(m_idx[n],len(line_fft[1:-1]),1):
            if check_fft[1:-1][k] > err_medio**2:
                fr_right = x_fft[1:-1][k]
                break
        try:
            e_vsini[n] = 0.5*np.fabs(q[n]/fr_right - q[n]/fr_left)
            e_minima[n] = 0.5*np.fabs(fr_right - fr_left)
        except NameError:
            e_vsini[n] = np.nan
            e_minima[n] = np.nan

    e_vsini[e_vsini==0] = max(e_vsini)*10
    e_vsini[e_vsini==0] = 0.1*vsini[e_vsini==0]
    mean_vsini = np.average(vsini, weights=(1./e_vsini**2))
    mean_error = np.sqrt(np.nansum(e_vsini**2))

    ratio = minima[1]/minima[0]
    e_ratio = np.sqrt((e_minima[1]/minima[0])**2 + ((minima[1]*e_minima[0])/minima[0]**2)**2)

    result = {'FFT_fr': x_fft, 'FFT_pow': line_fft/line_fft.max(), 'FFT_err': err_medio**2,\
            'vsini': vsini, 'e_vsini': e_vsini, 'mean_vsini': mean_vsini, \
            'e_mean_vsini': mean_error, 'ratio': ratio, 'e_ratio': e_ratio, \
            'zeros' : minima, 'e_zeros' : e_minima, 'rv' : rv_middle+(shift*step_fine)}

    return result
            
