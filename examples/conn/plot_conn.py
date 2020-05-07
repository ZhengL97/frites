"""
Estimate connectivity using MI
==============================

This example illustrates how to compute the connectivity using mutual
information between pairwise ROI and also perform statistics.
"""
import numpy as np
from itertools import product

from frites.simulations import sim_multi_suj_ephy, sim_mi_cc
from frites.dataset import DatasetEphy
from frites.workflow import WfConn

import matplotlib.pyplot as plt
plt.style.use('seaborn-white')


###############################################################################
# Simulate electrophysiological data
# ----------------------------------
#
# Let's start by simulating MEG / EEG electrophysiological data coming from
# multiple subjects using the function
# :func:`frites.simulations.sim_multi_suj_ephy`. As a result, the `x` output
# is a list of length `n_subjects` of arrays, each one with a shape of
# n_epochs, n_sites, n_times

modality = 'meeg'
n_subjects = 5
n_epochs = 50
n_times = 100
x, roi, _ = sim_multi_suj_ephy(n_subjects=n_subjects, n_epochs=n_epochs,
                               n_times=n_times, modality=modality,
                               random_state=0, n_roi=4)
times = np.linspace(-1, 1, n_times)

###############################################################################
# Simulate spatial correlations
# -----------------------------
#
# Bellow, we start by simulating some distant correlations by injecting the
# activity of an ROI to another
for k in range(n_subjects):
    x[k][:, [1], slice(20, 40)] += x[k][:, [0], slice(20, 40)]
    x[k][:, [2], slice(60, 80)] += x[k][:, [3], slice(60, 80)]
print(f'Corr 1 : {roi[0][0]}-{roi[0][1]} between [{times[20]}-{times[40]}]')
print(f'Corr 2 : {roi[0][2]}-{roi[0][3]} between [{times[60]}-{times[80]}]')

sl = slice(40, 60)
y = [x[k][..., sl].mean(axis=(1, 2)) for k in range(len(x))]

###############################################################################
# Define the electrophysiological dataset
# ---------------------------------------
#
# Now we define an instance of :class:`frites.dataset.DatasetEphy`

dt = DatasetEphy(x, y, roi, times=times)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

###############################################################################
# Compute the pairwise connectivity
# ---------------------------------
#
# Once we have the dataset instance, we can then define an instance of workflow
# :class:`frites.workflow.WfConn`. This instance is then used to compute the
# pairwise connectivity

n_perm = 100  # number of permutations to compute
kernel = np.hanning(10)  # used for smoothing the MI

wf = WfConn(kernel=kernel)
mi, pv = wf.fit(dt, output_type='dataarray', n_perm=n_perm, n_jobs=1)
print(mi)

###############################################################################
# Plot the result of the DataArray
# --------------------------------

# set to NaN everywhere it's not significant
is_signi = pv.data < .05
pv.data[~is_signi] = np.nan
pv.data[is_signi] = 1.02 * mi.data.max()

# plot each pair separately
for s, t in product(mi.source.data, mi.target.data):
    if s == t: continue
    color = np.random.rand(3,)
    plt.plot(times, mi.sel(source=s, target=t), label=f"{s}-{t}", color=color)
    plt.plot(times, pv.sel(source=s, target=t), color=color, lw=4)
plt.legend()
plt.show()
