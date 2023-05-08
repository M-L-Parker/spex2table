#!/usr/bin/env python


import numpy as np
# from matplotlib import pyplot as pl
# from shutil import move
import os
import subprocess


# xi is in 1e-9 Wm, pretty sure this converts exactly to erg units...
logxi_vals=np.linspace(-2,3,11)
# Density in 10^20/m^-3, want 10^8-10^12/cm^-3...
# density_vals=np.logspace(-6,-2,9)
nh_vals=np.logspace(-4,0,9)
# Might want to set temperature manually instead of solving for it?
# T_vals=np.logspace(5,7,5)
gamma_vals=np.linspace(1.5,3,4)
# v_vals=np.logspace(np.log10(50),np.log10(5000),5)
# A_O_vals=np.logspace(np.log10(0.5),np.log10(2),3)
# A_Fe_vals=np.logspace(np.log10(0.5),np.log10(2),3)

i=0
for xi in logxi_vals:
    for nh in nh_vals:
        for gamma in gamma_vals:
            i+=1
            print("submitting job",i)

            modstr="xi%s_nh%s_gamma%s" % (str(xi),str(nh),str(gamma))

            spec_fname="piongrid_%s.qdp" % modstr
            fname="piongrid_%s.sh" % modstr
            outfile=open(fname,"w")

            preamble=("#!/usr/bin/env bash\n\nspex<<EOF\n\n")

            components="\n".join(
                                 ["com po", \
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
                                    "par 3 nh v %s" % str(nh),\
                                    "par 1 gamm v %s" % str(gamma),\
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

            subprocess.call(["bash %s" % (fname)], shell=True)
# exit()
