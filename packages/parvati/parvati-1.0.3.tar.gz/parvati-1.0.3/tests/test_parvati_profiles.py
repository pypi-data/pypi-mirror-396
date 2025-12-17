import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt

import os, sys

import parvati as pa

star = 'fast'
#star = 'red'

if star == 'fast':
    testfile = 'fast_rotator.fits'
    nor_output = 'fast_rotator.nor'
    outccf = 'fast_rotator_ccf.prf'
    outlsd = 'fast_rotator_lsd.prf'
    outext = 'fast_rotator_ext.prf'
    maskfile = 'VALD_T10000G43P00'
    vrange = (-250,200)

else:
    testfile = 'red_dwarf.txt'
    nor_output = 'red_dwarf.nor'
    outccf = 'red_dwarf_ccf.prf'
    outlsd = 'red_dwarf_lsd.prf'
    outext = 'red_dwarf_ext.prf'
    maskfile = 'VALD_T4000G40P00'
    vrange = (-50,50)


mask = pa.read_mask(maskfile)
print(f'Read mask {maskfile}')

spectrum = pa.read_spectrum(testfile)
print(f'Read spectrum {testfile}')

if star == 'fast':
    norspectrum = pa.norm_spectrum(spectrum['wave'], spectrum['flux'], snr=spectrum['snr'], n_ord=40, output=nor_output)
else:
    norspectrum = pa.norm_spectrum(spectrum['wave'], spectrum['flux'], snr=spectrum['snr'], echelle=spectrum['echelle'], output=nor_output)
    
ccf_profile = pa.compute_ccf(norspectrum, mask, verbose=True, cosmic=True, vrange=vrange, output=outccf)
lsd_profile = pa.compute_lsd(norspectrum, mask, verbose=True, cosmic=True, vrange=vrange, output=outlsd)
ext_profile = pa.extract_line(norspectrum, vrange=vrange, output=outext)

plt.title("CCF")
plt.plot(ccf_profile['rv_range'], ccf_profile['profile'])
plt.xlabel('RV')
plt.ylabel('Flux')
plt.show()
plt.close()

plt.title("LSD")
plt.plot(lsd_profile['rv_range'], lsd_profile['profile'])
plt.xlabel('RV')
plt.ylabel('Flux')
plt.show()
plt.close()

plt.title("Single Line")
plt.plot(ext_profile['rv_range'], ext_profile['profile'])
plt.xlabel('RV')
plt.ylabel('Flux')
plt.show()
plt.close()


