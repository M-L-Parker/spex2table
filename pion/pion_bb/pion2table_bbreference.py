#!/usr/bin/env python


import numpy as np
# from matplotlib import pyplot as pl
# from shutil import move
import os
import subprocess
import multiprocessing as mp



# xi is in 1e-9 Wm, pretty sure this converts exactly to erg units...
# logxi_vals=np.linspace(0,5,11)
# Density in 10^20/m^-3, want 10^8-10^12/cm^-3...
# col_density_vals=np.logspace(-4,0,9)
# Might want to set temperature manually instead of solving for it?
# T_vals=np.logspace(5,7,5)
kT_vals=np.logspace(-2,1,7)
# v_vals=np.logspace(np.log10(100),np.log10(100000),7)
# A_O_vals=np.logspace(np.log10(0.5),np.log10(2),3)
# A_Fe_vals=np.logspace(np.log10(0.5),np.log10(2),3)


def jobsub_call(fname):
    subprocess.call(["bash %s" % (fname)], shell=True)
    pass



pool=mp.Pool(int(mp.cpu_count()/2))
print("Running in parallel on",mp.cpu_count(),"CPUs")
i=0
filenames=[]
for kT in kT_vals:
    modstr="kT%s" % str(kT)
    fname="piongrid_bbref_%s.sh" % modstr
    spec_fname="piongrid_bbref_%s" % modstr
    if not os.path.exists(spec_fname+'.qdp'):
        i+=1
        print("submitting job",i)
        print(spec_fname+'.qdp')
        # exit()
        filenames.append(fname)
        outfile=open(fname,"w")

        preamble=("#!/usr/bin/env bash\n\nspex<<EOF\n\n")

        components="\n".join(
                             ["com bb"]
                             )+"\n\n"


        # fixed_pars="\n".join(
        #                      ["par 2 omeg v 0",\
        #                       "par 2 fcov v 1"]
        #                     )+"\n"

        variable_pars="\n".join(["par 1 t v %s" % str(kT),\
                                "calc"])+"\n"

        plotting="\n".join(
                    ["pl dev ps %s.ps" % spec_fname,\
                     "pl ty mo",\
                     "pl ux ke",\
                     "pl uy cou",\
                     "p rx 0.1 10",\
                     "p ry 0 0.01",\
                     "p x  lin",\
                     "p y  lin",\
                     "p fil dis f",\
                     "p",\
                     "plot adum %s over" % spec_fname])+"\n"

        post="q\nEOF"

        outfile.write(preamble+components+variable_pars+plotting+post)
        outfile.flush()
        outfile.close()


pool.map(jobsub_call,filenames)


        # exit()
