#!/usr/bin/env python


import numpy as np
from matplotlib import pyplot as pl
import pyfits as pf

# xi is in 1e-9 Wm, pretty sure this converts exactly to erg units...
logxi_vals=np.linspace(2,5,11)
# Density in 10^20/m^-3, want 10^8-10^12/cm^-3...
# density_vals=np.logspace(-6,-2,9)
nh_vals=np.logspace(-4,0,9)
# Might want to set temperature manually instead of solving for it?
# T_vals=np.logspace(5,7,5)
gamma_vals=np.linspace(1.5,3,4)
v_vals=np.logspace(np.log10(100),np.log10(10000),5)
# A_O_vals=np.logspace(np.log10(0.5),np.log10(2),3)
# A_Fe_vals=np.logspace(np.log10(0.5),np.log10(2),3)


outfil="pion_highxi.fits"


Nvars=3
varnames=["logxi","nh","gamma"]
lengths=[11,9,4]
nmodels=np.prod(lengths)
nmax=max(lengths)

parray=[]
spec_array=[]

for xi in logxi_vals:
    for nh in nh_vals:
        for gamma in gamma_vals:


            modstr="xi%s_nh%s_gamma%s" % (str(xi),str(nh),str(gamma))

            spec_fname="piongrid_%s.qdp" % modstr

            # print(spec_fname)

            pars=[xi,density,nh]
            parray.append(pars)

            temp_data=np.loadtxt(spec_fname,skiprows=1)

            spec_array.append(temp_data[:,3])

parray=np.array(parray)
spec_array=np.array(spec_array)




###### SET UP PRIMARY HEADER #######


prihdu = pf.PrimaryHDU()
prihd =prihdu.header
prihd.extend([('MODLNAME','PIONTABLE'),('MODLUNIT','PHOTONS/CM2/S'),\
                  ('REDSHIFT',True),('ADDMODEL',True),('HDUCLASS','OGIP'),\
                  ('HDUCLAS1','XSPEC TABLE MODEL'),('HDUVERS','1.0.0'),\
                  ('AUTHOR','M L PARKER'),\
                  ('COMMENT','BASED ON PION MODEL IN SPEX')])



#### SET UP PARAMETERS TABLE



pcnames = ['NAME','METHOD','INITIAL','DELTA','MINIMUM','BOTTOM',\
               'TOP','MAXIMUM','NUMBVALS','VALUE']
pcformats = ['12A','J','E','E','E','E','E','E','J','%sE' % nmax]


# All arrays have to have the same length, so make empty arrays and set the first few values
density_array=np.empty(nmax)
for i,d in enumerate(density_vals):
    density_array[i]=d

gamma_array=np.empty(nmax)
for i,g in enumerate(gamma_vals):
    gamma_array[i]=g

v_array=np.empty(nmax)
for i,v in enumerate(v_vals):
    v_array[i]=v

A_O_array=np.empty(nmax)
for i, A_O in enumerate(A_O_vals):
    A_O_array[i]=A_O

A_Fe_array=np.empty(nmax)
for i, A_Fe in enumerate(A_Fe_vals):
    A_Fe_array[i]=A_Fe

p1=['logxi',0,0,0.01,min(logxi_vals),min(logxi_vals),max(logxi_vals),max(logxi_vals),len(logxi_vals),logxi_vals]
p2=['density',1,np.median(density_vals),0.01,min(density_vals),min(density_vals),max(density_vals),max(density_vals),len(density_vals),density_array]
p3=['gamma',0,2,0.01,min(gamma_vals),min(gamma_vals),max(gamma_vals),max(gamma_vals),len(gamma_vals),gamma_array]
p4=['v',0,100,0.01,min(v_vals),min(v_vals),max(v_vals),max(v_vals),len(v_vals),v_array]
p5=['A_O',1,1,0.01,min(A_O_vals),min(A_O_vals),max(A_O_vals),max(A_O_vals),len(A_O_vals),A_O_array]
p6=['A_Fe',1,1,0.01,min(A_Fe_vals),min(A_Fe_vals),max(A_Fe_vals),max(A_Fe_vals),len(A_Fe_vals),A_Fe_array]


pars=[p1,p2,p3,p4,p5,p6]

parcols=[]
for c in range(0,len(pars[0])):
    col=[]
    for p in range(0,Nvars):
        par = pars[p]
        col.append(par[c])
    # print(col)
    parcols.append(pf.Column(name=pcnames[c],format=pcformats[c],array=col))

pcdefs = pf.ColDefs(parcols)
partb = pf.new_table(pcdefs)
partb.name='Parameters'
parhd = partb.header
parhd.extend([('NINTPARM',Nvars),('NADDPARM',0),('HDUCLASS','OGIP'),\
                  ('HDUCLAS1','XSPEC TABLE MODEL'),\
                  ('HDUCLAS2','PARAMETERS'),('HDUVERS','1.0.0')])



######## SET UP ENERGIES TABLE ########

elow=temp_data[:,0]+temp_data[:,2]
ehigh=temp_data[:,0]+temp_data[:,1]

energ_lo = pf.Column(name='ENERG_LO', format='E', array=elow)
energ_hi = pf.Column(name='ENERG_HI', format='E', array=ehigh)

energtb = pf.new_table([energ_lo,energ_hi])
energtb.name = 'Energies'
energhd = energtb.header
energhd.extend([('HDUCLASS','OGIP'),('HDUCLAS1','XSPEC TABLE MODEL'),\
                  ('HDUCLAS2','ENERGIES'),('HDUVERS','1.0.0')])



####### SET UP SPECTRUM TABLE ##########



parcol = pf.Column(name = 'PARAMVAL',format='%sE' %Nvars ,array = parray)
speccol = pf.Column(name = 'INTPSPEC',format='%sE' % len(spec_array[0]),\
                        unit='photons/cm2/s',array = spec_array)

spectb = pf.new_table([parcol,speccol],tbtype='BinTableHDU')
spectb.name = 'Spectra'
spechd = spectb.header
spechd.extend([('HDUCLASS','OGIP'),('HDUCLAS1','XSPEC TABLE MODEL'),\
                  ('HDUCLAS2','MODEL SPECTRA'),('HDUVERS','1.0.0')])


thdulist = pf.HDUList([prihdu, partb, energtb, spectb])

thdulist.writeto(outfil)
