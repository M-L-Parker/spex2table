#!/usr/bin/env python


import numpy as np
from matplotlib import pyplot as pl
import pyfits as pf


# xi is in 1e-9 Wm, pretty sure this converts exactly to erg units...
logxi_vals=np.linspace(0,5,11)
# Density in 10^20/m^-3, want 10^8-10^12/cm^-3...
col_density_vals=np.logspace(-4,0,9)
# Might want to set temperature manually instead of solving for it?
# T_vals=np.logspace(5,7,5)
kT_vals=np.logspace(-2,1,7)
# print(kT_vals)
v_vals=np.logspace(np.log10(100),np.log10(100000),7)
# A_O_vals=np.logspace(np.log10(0.5),np.log10(2),3)
# A_Fe_vals=np.logspace(np.log10(0.5),np.log10(2),3)


outfil="pion_bb_0.5.fits"


Nvars=4
varnames=["logxi","nh","kT","v"]
lengths=[11,9,7,7]
nmodels=np.prod(lengths)
nmax=max(lengths)

parray=[]
spec_array=[]

for xi in logxi_vals:
    for col_density in col_density_vals:
        for kT in kT_vals:
            for v in v_vals:


                modstr="xi%s_nH%s_kT%s_v%s" % (str(xi),str(col_density),str(kT),str(v))

                spec_fname="piongrid_%s.qdp" % modstr

                # print(spec_fname)

                pars=[xi,col_density,kT,v]
                parray.append(pars)

                temp_data=np.loadtxt(spec_fname,skiprows=1)

                spec_array.append(temp_data[:,3])
                # if len(temp_data[:,3])!=8192:
                #     print(spec_fname)
                #     print(temp_data.shape)

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
logxi_array=np.empty(nmax)
for i,xi in enumerate(logxi_vals):
    logxi_array[i]=xi


col_density_array=np.empty(nmax)
for i,d in enumerate(col_density_vals):
    col_density_array[i]=d

kT_array=np.empty(nmax)
for i,kT in enumerate(kT_vals):
    kT_array[i]=kT
# print(kT_array)
# exit()

v_array=np.empty(nmax)
for i,v in enumerate(v_vals):
    v_array[i]=v

p1=['logxi',0,3,0.01,min(logxi_vals),min(logxi_vals),max(logxi_vals),max(logxi_vals),len(logxi_vals),logxi_array]
p2=['nH',1,np.median(col_density_vals),0.01,min(col_density_vals),min(col_density_vals),max(col_density_vals),max(col_density_vals),len(col_density_vals),col_density_array]
p3=['kT',1,0.1,0.01,min(kT_vals),min(kT_vals),max(kT_vals),max(kT_vals),len(kT_vals),kT_array]
p4=['v',1,1000,0.01,min(v_vals),min(v_vals),max(v_vals),max(v_vals),len(v_vals),v_array]

print(p3)

pars=[p1,p2,p3,p4]

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
