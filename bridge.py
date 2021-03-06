import os, fnmatch
import numpy as np
import sympy as sy
# CG(j1, m1, j2, m2, j3, m3)
from sympy.physics.quantum.cg import CG

from parameters_and_constants import *
from rrgm_functions import *
from two_particle_functions import *

home = os.getenv("HOME")

pathbase = home + '/kette_repo/ComptonLIT'

av18path = pathbase + '/av18_deuteron'
litpathD = pathbase + '/mul_deuteron/'

v18uixpath = pathbase + '/v18uix_helium3'
litpath3He = pathbase + '/mul_helion/'

BINBDGpath = pathbase + '/src_nucl/'
BINLITpath = pathbase + '/src_elma/'

mpii = '137'
potnn = 'AV18'
potnnn = 'urbana9_AK_neu'

# convention: bound-state-expanding BVs: (1-8), i.e., 8 states per rw set => nzf0*8
rechtekanaele = {
    # deuteron
    'np-3SD-J=1': [[1, 1, 2, 2], [1, 1, 2, 6]],
    # helion
    'npp-J=0.5':
    [[
        '000',
        ['he_no1', 'he_no1', 'he_no1', 'he_no1', 'he_no6', 'he_no6', 'he_no6']
    ], ['202', ['he_no2', 'he_no2', 'he_no2', 'he_no2', 'he_no2']],
     ['022', ['he_no2', 'he_no2']], ['222', ['he_no2']], ['221', ['he_no1']],
     ['220', ['he_no1']], ['221', ['he_no2']], ['220', ['he_no6']],
     ['111', ['he_no3']], ['112', ['he_no5']], ['111', ['he_no5']]],
}

# ECCE! bvnr for LIT basis states must be shifted after purge! (A2_lit)
streukanaeleD = {
    #       s1 s2 S  bvnr
    '0^+': [[1, 1, 0, 1]],  #     1S0
    '0^-': [[1, 1, 2, 4]],  #     3P0
    '1^+': [[1, 1, 2, 2], [1, 1, 2, 6]],  # 3S1 3D1
    #'1-': [[1, 1, 0, 3], [1, 1, 2, 4]],  # 1P1 3P1
    '1^-': [[1, 1, 2, 4]],  # 3P1
    '2^+': [[1, 1, 0, 5], [1, 1, 2, 6]],  # 1D2 3D2
    '2^-': [[1, 1, 2, 4], [1, 1, 2, 8]],  # 3P2 3F2
    '2^b-': [[1, 1, 2, 4]],  # 3P2
    #
    '3^+': [[1, 1, 2, 6]],  #     3D3
    '3^-': [[1, 1, 0, 7], [1, 1, 2, 8]],  # 1F3 3F3
    '4^-': [[1, 1, 2, 8]],  #     3F4
}

streukanaele3He = {
    #          [l1l2L,[compatible (iso)spin configurations]]
    '0.5^-': [['101', ['he_no3',
                       'he_no5']], ['011', ['he_no1', 'he_no2', 'he_no6']],
              ['121', ['he_no3', 'he_no5']], ['122', ['he_no5']],
              ['211', ['he_no1', 'he_no2', 'he_no6']], ['212', ['he_no2']]],
    '1.5^-': [['101', ['he_no3',
                       'he_no5']], ['011', ['he_no1', 'he_no2', 'he_no6']],
              ['121', ['he_no3', 'he_no5']], ['122', ['he_no3', 'he_no5']],
              ['123', ['he_no5']], ['211', ['he_no1', 'he_no2', 'he_no6']], [
                  '212', ['he_no1', 'he_no2', 'he_no6']
              ], ['213', ['he_no2']], ['303', ['he_no5']], ['033', ['he_no2']]]
}

streukas = ['0.5^-']  #['0^-', '1^-', '2^-']  #

cal = ['purge']
cal = ['purge', 'construe_fresh_LIT_basis', 'construe_fresh_deuteron']
cal = ['purge', 'construe_fresh_helion', 'construe_fresh_LIT_basis']
cal = []

boundstatekanal = 'npp-J=0.5'  # 'np-3SD-J=1'
J0 = float(boundstatekanal.split('J=')[1])

multipolarity = 1

anz_phot_e = 100
phot_e_0 = 0.2  #  enems_e converts to fm^-1, but HERE the value is in MeV
phot_e_d = 10.  #

# deuteron/initial-state basis -------------------------------------------
basisdim0 = 15

laplace_loc, laplace_scale = 1., .4
wLAPLACE = np.sort(
    np.abs(np.random.laplace(laplace_loc, laplace_scale, basisdim0)))
wini0 = w120  #wLAPLACE[::-1]

addw = 1
addwt = 'middle'
scale = 1.
min_spacing = 0.02
min_spacing_to_LITWs = 0.001

rw0 = wid_gen(
    add=addw, addtype=addwt, w0=wini0, ths=[1e-5, 2e2, 0.2], sca=scale)
rw0 = sparsify(rw0, min_spacing)

nzf0 = int(np.ceil(len(rw0) / 20.0))

#LIT basis ---------------------------------------------------------------

basisdimLIT = 20
wli = 'wd'

if wli == 'wd':
    #scale deuteron
    winiLIT = [ww for ww in 1.1 * rw0 if ((ww < 10) & (ww > 0.01))] + [10.01]

if wli == 'lin':
    #linspace
    w0l, dw = 0.035, 1.4
    winiLIT = np.linspace(
        start=w0l,
        stop=w0l + basisdimLIT * dw,
        num=basisdimLIT,
        endpoint=True,
        dtype=None)
if wli == 'log':
    #logspace
    exp0log, expmaxlog = -1, 1
    winiLIT = np.logspace(
        start=exp0log,
        stop=expmaxlog,
        num=basisdimLIT,
        endpoint=True,
        dtype=None)
if wli == 'geom':
    #geomspace
    wminl, wmaxl = 0.01, 20
    winiLIT = np.geomspace(
        start=wminl, stop=wmaxl, num=basisdimLIT, endpoint=True, dtype=None)
if wli == 'lap':
    #laplace space
    laplace_loc, laplace_scale = .9, .4
    winiLITlaplace = np.sort(
        np.abs(np.random.laplace(laplace_loc, laplace_scale, basisdimLIT)))
    winiLITlaplace = wid_gen(
        add=addw,
        addtype=addwt,
        w0=winiLITlaplace[::-1],
        ths=[1e-5, 2e2, 0.2],
        sca=scale)
    winiLIT = sparsify(winiLITlaplace, min_spacing)

# for the cleaner --------------------------------------------------------

streukanalweiten = range(1, len(winiLIT) + 1)

maxCoef = 10000
minCoef = 1200
ncycl = 30
maxDiff = 0.001
delPcyc = 1