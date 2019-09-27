import os, sys

import numpy as np
from scipy.optimize import fmin

from bridge import *
from rrgm_functions import *
from two_particle_functions import *
from lit_plots import *
from readLITsource import *

os.chdir(av18path)

costr = ''
for nn in range(14):
    costr += '%12.7f' % 1.0 if (nn != 6) else '%12.7f\n' % 1.0

os.chdir(av18path)

h2_inlu(nfrag=nzf0)
os.system(BINBDGpath + 'LUDW_CN.exe')
h2_inob(nfrag=nzf0)
os.system(BINBDGpath + 'KOBER.exe')
h2_inqua(rw0, pots)
os.system(BINBDGpath + 'QUAFL_N.exe')

h2_inen_bs(
    relw=rw0,
    costr=costr,
    j=int(boundstatekanal[-1]),
    ch=rechtekanaele[boundstatekanal],
    nfrag=nzf0)

os.system(BINBDGpath + 'DR2END_AK.exe')

exit()
purge_basis(
    max_coeff=11000,
    min_coeff=150,
    nbr_cycles=20,
    max_diff=0.1,
    dr2executable=BINBDGpath + 'DR2END_AK.exe')

clean_wrels, clean_inen_indices = purged_width_set(infil='INEN', w0=rw0)

nzf0p = int(np.ceil(len(clean_wrels) / 20.0))

if (nzf0 != nzf0p):
    print('NZF0 (after purge) != NZF0 (before purge)', nzf0, nzf0p)
    h2_inlu(nfrag=nzf0p)
    os.system(BINBDGpath + 'LUDW_CN.exe')
    h2_inob(nfrag=nzf0p)
    os.system(BINBDGpath + 'KOBER.exe')

h2_inqua(clean_wrels, pots)
for ind_set in range(len(clean_inen_indices)):
    istr = ''
    for i in clean_inen_indices[ind_set]:
        istr += '%3s' % str(i)
    istr += '\n'
    repl_line('INEN', int(6 + 2 * ind_set), istr)

print('dim(B_0) = %d' % len(clean_wrels))

os.system(BINBDGpath + 'QUAFL_N.exe')
os.system(BINBDGpath + 'DR2END_AK.exe')

wLIT = sparsifyOnlyOne(winiLIT, clean_wrels, 0.01)
print('dim(B_LIT) = %d' % len(wLIT))

nzfLIT = int(np.ceil(len(wLIT) / 20.0))
nzfTOT = nzf0p + nzfLIT

# consistency check if B0 is the same as in the smaller space
h2_inlu(nfrag=nzfTOT)
os.system(BINBDGpath + 'LUDW_CN.exe')
h2_inob(nfrag=nzfTOT)
os.system(BINBDGpath + 'KOBER.exe')
h2_inqua(wLIT, pots, withhead=False)
os.system(BINBDGpath + 'QUAFL_N.exe')
os.system(BINBDGpath + 'DR2END_AK.exe')

EBDG = get_h_ev()[0]
print(
    '(iv)    LS-scheme: B(2,%s) = %4.4f MeV [' % (boundstatekanal, EBDG),
    get_h_ev(n=4),
    ']')

os.system('cp OUTPUT end_out_b && cp INEN inen_b')
rrgm_functions.parse_ev_coeffs(infil='end_out_b')

BUECO = [cof.strip() for cof in open('COEFF')]
BSRWIDX = get_bsv_rw_idx(chs=2, inen='inen_b')
EBDG = get_h_ev(ifi='end_out_b')[0]

os.chdir(litpath)

lit_inlu(mul=multipolarity, nfrag=nzfTOT)
os.system(BINLITpath + 'luise.exe > dump')
lit_inob(nfrag=nzfTOT)
os.system(BINLITpath + 'obem.exe > dump')

lit_inqua(anzo=11, relw=clean_wrels)
lit_inqua(relw=wLIT, withhead=False, LREG='')

os.system(BINLITpath + 'qual.exe')

leftpar = 1 if streukanal[1] == '-' else 2

#os.system('mv endlitout_* ./old')
os.system('rm endlitout_*')

for mM in mLmJl:
    for streukanalweite in range(1, len(wLIT) + 1):
        lit_inen(
            MREG='  1  0  0  0  0  0  0  0  0  1  1',
            #                   (shifted) QBV                     nr.rw
            KSTREU=[
                int(streukanaele[streukanal][0][-1] + 8 * nzf0p),
                streukanalweite
            ],
            JWSL=int(streukanal[0]),
            JWSLM=mM[1],
            MULM2=mM[0],
            NPARL=leftpar,
            KBND=[[2, BSRWIDX[0]], [5, BSRWIDX[1]]],
            JWSR=1,
            NPARR=2,
            EB=EBDG,
            BUECO=BUECO,
            NZE=anz_phot_e,
            EK0=phot_e_0,
            EKDIFF=phot_e_d)

        os.system(BINLITpath + 'enemb.exe')
        os.system(
            'cp OUTPUT endlitout_%d_%d-%d' % (streukanalweite, mM[1], mM[0]))

print('(iiib)  calculated S_bv^(Jlit,m) for mL,m in:', mLmJl)

print('(ii)    calculating norm/ham in scattering-channel basis')
os.chdir(av18path)

h2_inlu(nfrag=nzfLIT)
os.system(BINBDGpath + 'LUDW_CN.exe')
h2_inob(nfrag=nzfLIT)
os.system(BINBDGpath + 'KOBER.exe')
h2_inqua(wLIT, pots)
os.system(BINBDGpath + 'QUAFL_N.exe')

h2_inen_bs(
    relw=wLIT,
    costr=costr,
    j=int(streukanal[0]),
    ch=streukanaele[streukanal],
    nfrag=nzfLIT)

os.system(BINBDGpath + 'DR2END_AK.exe')

os.system(
    'cp %s/MATOUT %s/norm-ham-litME-%s' % (av18path, av18path, streukanal))

# read uncoupled source ME's
os.chdir(litpath)
RHSofBV, photEn = read_uncoupled_source(basisSET=wLIT)
# couple incoming state with photon multipole to Jlit
RHSofmJ = couple_source(RHSofBV, basisSET=wLIT)

fig = plt.figure()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
ax1.set_title(r'')
ax1.set_xlabel('photon momentum [MeV]')
mM = [0, 0]
[
    ax1.plot(
        photEn, RHSofBV[('%d' % (streukanalweite), '%d' % int(streukanal[0]),
                         '%d' % (2 * mM[1]), '%d' % (2 * multipolarity),
                         '%d' % (2 * mM[0]))])
    for streukanalweite in range(1,
                                 len(wLIT) + 1)
]
[
    ax2.plot(
        photEn, RHSofmJ[('%d' % (streukanalweite), '%d' % int(streukanal[0]),
                         '%d' % (2 * mM[1]), '%d' % (2 * multipolarity))])
    for streukanalweite in range(1,
                                 len(wLIT) + 1)
]
plt.show()