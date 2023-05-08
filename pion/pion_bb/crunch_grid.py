#!/usr/bin/env python

import numpy as np
import multiprocessing as mp
from subprocess import call
import os

def jobsub_call(infile):
    os.rename("inputfiles/%s" % infile, infile)
    call(["./jobsubmit.sh %s" % infile],shell=True)


if __name__ == '__main__':
    infile='reflionx_simplHD_spec1'
    # jobsub_call(infile)

    # n_spectra=8*10*5*800
    n_spectra=100
    # print(n_spectra)

    pool=mp.Pool(mp.cpu_count())

    filenames=["reflionx_simplHD_spec"+str(i) for i in range(0,n_spectra)]

    pool.map(jobsub_call,filenames)
    # print(mp.cpu_count())
