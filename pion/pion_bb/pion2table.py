#!/usr/bin/env python


import numpy as np
# from matplotlib import pyplot as pl
# from shutil import move
import os
import subprocess
import multiprocessing as mp



# xi is in 1e-9 Wm, pretty sure this converts exactly to erg units...
logxi_vals=np.linspace(2,5,7)
# Density in 10^20/m^-3, want 10^8-10^12/cm^-3...
col_density_vals=np.logspace(-4,0,9)
# Might want to set temperature manually instead of solving for it?
# T_vals=np.logspace(5,7,5)
kT_vals=np.logspace(-2,0,5)
v_vals=np.logspace(np.log10(100),np.log10(10000),5)
# A_O_vals=np.logspace(np.log10(0.5),np.log10(2),3)
# A_Fe_vals=np.logspace(np.log10(0.5),np.log10(2),3)


def jobsub_call(fname):
    subprocess.call(["bash %s" % (fname)], shell=True)
    pass



pool=mp.Pool(mp.cpu_count())
print("Running in parallel on",mp.cpu_count(),"CPUs")
i=0
filenames=[]
for xi in logxi_vals:
    for col_density in col_density_vals:
        for kT in kT_vals:
            for v in v_vals:
                i+=1
                print("submitting job",i)
                modstr="xi%s_nH%s_kT%s_v%s" % (str(xi),str(col_density),str(kT),str(v))
                fname="piongrid_%s.sh" % modstr
                filenames.append(fname)
                spec_fname="piongrid_%s" % modstr
                outfile=open(fname,"w")

                preamble=("#!/usr/bin/env bash\n\nspex<<EOF\n\n")

                components="\n".join(
                                     ["com bb", \
                                      "com etau",\
                                      "com pion",\
                                      "com rel 1 3,2"]
                                     )+"\n\n"


                fixed_pars="\n".join(
                                     ["par 2 a v 0",\
                                      "par 2 tau v 1000",\
                                      "par 3 omeg v 1",\
                                      "par 3 fcov v 0"]
                                    )+"\n"

                variable_pars="\n".join(["par 3 xil v %s" % str(xi),\
                                        "par 3 nh v %s" % str(col_density),\
                                        "par 1 t v %s" % str(kT),\
                                        "par 3 v v %s" % str(v),\
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

                outfile.write(preamble+components+fixed_pars+variable_pars+plotting+post)
                outfile.flush()
                outfile.close()


pool.map(jobsub_call,filenames)


        # exit()
