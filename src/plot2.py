#!/usr/bin/env python2


#alternative fit and plot script

import numpy as np
import pylab as plt
import myPyCRV as CRV
import math as m
import scipy.optimize as opt


fsize = (14,12) #publication

plt.rc('text', usetex=True)  

plt.rcParams["font.family"] = 'serif'
#Computer Modern Setup
plt.rcParams['font.serif'] = ['computer modern roman']
plt.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
plt.rcParams.update({'font.size': 30, 'legend.fontsize': 30})
legpropsize = 30

lw = 4 #linewidth
ms = 14 #markersize
mew = 4 #markeredgewidth

def eta_lin(ndpa,sigma0,eta,offset ):
    
    return sigma0*-1./(3*eta)*ndpa #	+ offset

def eta_exp(ndpa, Ebi,eta ):
    # Ebi.. biaxial module a-Si
    # ndpa ... number of displacements per target atom
    # eta.. RIV
    return np.exp(-Ebi/(6. * eta) * ndpa)
    
    
def lin_fit(crvfile, refcrvfile, outname, dump_frequency, Er, Ed, recoil_relaxation_time = 10000,  start_timeoffset= 500):

    crv = CRV.CRV(crvfile)[0]
    eps = crv['lz']
    x = crv['step']
    pyy = crv['pyy']
    n_atoms = crv['atoms'][0]
    
    crv1 = CRV.CRV(refcrvfile)[0]
    eps_ref = crv1['lz']
    
    
  #  eps = np.subtract(eps,eps_ref)
    
    print eps
    
    
    nrecoils = []
    
    #pressure tensor component
    pxx = []
    ezz = []
    ezz_ref = []
    
    dump_factor = int(recoil_relaxation_time / dump_frequency)
    
    pressure_conversion = 1e9 #GPa -> Pa 
    
    #reduce timeaxis to recoil axis 
    for i in range(len(x)/dump_factor):
        nrecoils.append( (x[i*dump_factor] - start_timeoffset) /float(recoil_relaxation_time))
        pxx.append(pyy[i*dump_factor] * pressure_conversion)
       # ezz.append(((eps[i*dump_factor] - eps[0])/eps[0] - (eps_ref[i*dump_factor] - eps_ref[0])/eps_ref[0]))
       # ezz.append(abs( (eps[i*dump_factor] -eps_ref[i*dump_factor])/ (eps[0] - eps_ref[0])))
        ezz.append( ( (-eps[dump_factor] + eps[i*dump_factor]  )))
        ezz_ref.append( ( (-eps_ref[dump_factor] + eps_ref[i*dump_factor] )))
    
    del nrecoils[0]
    del pxx[0]
    del ezz[0]
    del ezz_ref[0]

    #number of displacements per target atom
    ndpa = np.multiply(nrecoils, (Er/(2.5 * Ed * n_atoms)))
    
    fit_start =0
    fit_end = 20

    dezz = np.multiply(np.subtract(ezz, ezz_ref), 1./eps[dump_factor])

    #fit1
    popt1, pcov1 = opt.curve_fit( lambda ndpa,eta,offset: eta_lin(ndpa,pxx[0],eta,offset), ndpa[fit_start:fit_end], dezz[fit_start:fit_end])
    #popt1 = [1,1]
    
    #fit2
   # popt2, pcov2 = opt.curve_fit( lambda ndpa,eta,offset: eta_lin(ndpa,pxx[0],eta,offset), ndpa[0:fit_start], ezz[0:fit_start])
    #popt2 = [1,1]
    #anotate to add value to plot
   # print 'RIV (lin)= {:.4e}'.format(popt1[0])
    
    # npa interpolated
    ndpa_interp = np.linspace(0, ndpa[-1]*1.5, 1000) 
        
        
    fig = plt.figure(1, figsize=fsize)

    plt.xlim(0, ndpa_interp[-1])
    
   # plt.ylim(ezz[-1]*0.8, ezz[-1]*1.1)
    
    plt.grid()
    
    plt.plot(ndpa[fit_start:fit_end], dezz[fit_start:fit_end], 'bs', markeredgecolor = 'blue',  markerfacecolor= 'None', markeredgewidth=mew,  markersize = ms,  label = 'MD Simulation')
   # plt.plot(ndpa, ezz_ref, 'bs', markeredgecolor = 'magenta',  markerfacecolor= 'None', markeredgewidth=mew,  markersize = ms,  label = 'MD Simulation Reference')
    plt.plot(ndpa_interp, eta_lin(ndpa_interp,pxx[0],*popt1),'r-', linewidth = lw, label='Fit')
  #  plt.plot(ndpa_interp, eta_lin(ndpa_interp,pxx[0],*popt2), '-', color = 'black', linewidth = lw, label='Fit2')
    plt.xlabel('Number of displacements per atom')
    plt.ylabel(r'$ \Delta \varepsilon_{zz} $')
    
   # legtitle  = r'$ \eta_{ri,1} = $' + '{:.4e}'.format(popt1[0]) + ' $ \mathrm{Pa \cdot dpa} $' + '\n' +  r'$ \eta_{ri,2} = $' + '{:.4e}'.format(popt2[0]) + ' $ \mathrm{Pa \cdot dpa} $' + '\n'r'$\sigma_0 = $' + '{:.2e}'.format(abs(pxx[0])) + r'$\,\mathrm{Pa}$' + '\n' +  r'$E_D = ' + '{:.1e}'.format(Ed) + 'eV $'+ '\n' + r'$ E_R = $' + '{:.1e}'.format(Er) + ' $ eV $'
    legtitle  = r'$ \eta^\prime = $' + '{:.4e}'.format(popt1[0]) + ' $ \mathrm{Pa \cdot dpa} $' + '\n'r'$\sigma_0 = $' + '{:.2e}'.format(abs(pxx[0])) + r'$\,\mathrm{Pa}$' + '\n' +  r'$E_D = ' + '{:.1e}'.format(Ed) + '\mathrm{eV} $'+ '\n' + r'$ E_R = $' + '{:.1e}'.format(Er) + ' $ \mathrm{eV} $'
    plt.legend(loc='best', shadow=False,title = legtitle, prop = {'size':legpropsize}, numpoints=1)
    
    #every other tick label 
    for label in plt.gca().xaxis.get_ticklabels()[::2]:
            label.set_visible(False)
    
    #plt.show()
    fig.tight_layout()
    fig.savefig(outname)
    print "Png file written to " + outname
    plt.close("all")

def exp_fit(crvfile, outname, dump_frequency, Er, Ed, Ebi, recoil_relaxation_time = 30000,  start_timeoffset= 500):
    ## CRV File - renamed to .crv and manually changed header (crv format) from extracted data file
    
    ## PNG output
    
    ## timestep used in recoil.in during recoil insertion --> datapoint after each recoil


    crv = CRV.CRV(crvfile)[0]
 
    #extract mech. stress tensor in x or y
    pyy = crv['pyy']
    x = crv['step']
    n_atoms = crv['atoms'][0]
    #calc timeaxis out of pxx or pyy size
    #x = np.arange(0,len(pyy)*timestep,timestep)
    
   
    #number of recoils
    nrecoils = []
    
    #pressure tensor component
    pxx = []
    
    dump_factor = int(recoil_relaxation_time / dump_frequency)
    
    print dump_factor
    
     #reduce timeaxis to recoil axis 
    for i in range(len(x)/dump_factor):
        nrecoils.append( (x[i*dump_factor] - start_timeoffset) /float(recoil_relaxation_time))
        pxx.append(abs(pyy[i*dump_factor]/pyy[0]))
        
    #number of displacements per target atom
    ndpa = np.multiply(nrecoils, (Er/(2.5 * Ed * n_atoms)))
    
    #fit
    popt, pcov = opt.curve_fit( lambda ndpa,eta: eta_exp(ndpa,Ebi,eta), ndpa, pxx,p0=2e8)
    
    #anotate to add value to plot
    print 'RIV (exp)= {:.4e}'.format(popt[0])
    
    # npa interpolated
    ndpa_interp = np.linspace(0, ndpa[-1]*5, 1000) 
        
        
    fig = plt.figure(1, figsize=fsize)

    plt.xlim(0, ndpa_interp[-1])
    #plt.ylim(0.95*pxx[-1] , 1)
    plt.grid()
    
    plt.plot(ndpa, pxx, 'bs', markeredgecolor = 'blue',  markerfacecolor= 'None', markeredgewidth=mew,  markersize = ms,  label = 'MD Simulation')
    plt.plot(ndpa_interp, eta_exp(ndpa_interp,Ebi,*popt),'r-', linewidth = lw, label='Fit')
    plt.xlabel('Number of displacements per atom')
    plt.ylabel(r'$ \frac{\sigma}{\vert \sigma_0 \vert} $')
    
    legtitle  = r'$ \eta_{ri} = $' + '{:.4e}'.format(popt[0]) + ' $ Pa \cdot dpa $' + '\n' + r'$ E_{bi} = $' + '{:.3e}'.format(Ebi) + ' $ Pa $' + '\n' + r'$ E_D = $' + '{:.1e}'.format(Ed) + ' $ \mathrm{eV} $'+ '\n' + r'$ E_R = $' + '{:.1e}'.format(Er) + ' $ \mathrm{eV} $'
    
    plt.legend(loc='best', shadow=False,title = legtitle, prop = {'size':legpropsize}, numpoints=1)
    
    #every other tick label 
    for label in plt.gca().xaxis.get_ticklabels()[::2]:
            label.set_visible(False)
    
    #plt.show()
    fig.savefig(outname)
    print "Png file written to " + outname
    plt.close("all")
    
    return popt[0]        
    
    
def main(args):    
    if len(sys.argv) <= 9:
        print ('required arguments:\n\tmode: exp or lin\n\tcrv file\n\treference crv file, only relevant for lin\n\tpng output name\n\tdumptime for logging (try 500)\n\tnumber of recoil relaxation timesteps\n\tEr\n\tEd\n\tEbi (only relevant for exp mode, but give a value nonetheless)')
        
    else:
        mode = sys.argv[1]
        crvfile = sys.argv[2]
        refcrvfile = sys.argv[3]
        outname = sys.argv[4]
        timestep = int(sys.argv[5])
        rectimestep = int(sys.argv[6])
        Er = float(sys.argv[7])
        Ed = float(sys.argv[8])
        Ebi = float(sys.argv[9])
        
        print rectimestep
        
        if mode == 'exp':
            exp_fit(crvfile,outname, timestep, Er, Ed, Ebi,recoil_relaxation_time=rectimestep)
        elif mode == 'lin':
            print crvfile
            print refcrvfile
            lin_fit(crvfile, refcrvfile, outname, timestep, Er, Ed,recoil_relaxation_time=rectimestep)
        else:
            print 'invalid mode, try exp or lin'
            
            
        
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
        






