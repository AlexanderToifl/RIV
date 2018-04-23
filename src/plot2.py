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

def eta_exp(ndpa, Ebi,eta ):
    # Ebi.. biaxial module a-Si
    # ndpa ... number of displacements per target atom
    # eta.. RIV
    return np.exp(-Ebi/(6. * eta) * ndpa)
    

def extract_plot(crvfile, outname, dump_frequency, Er, Ed, Ebi, recoil_relaxation_time = 30000,  start_timeoffset= 500):
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
    
     #reduce timeaxis to recoil axis    (every 20 timesteps - 1 recoil)
    for i in range(len(x)/dump_factor):
        nrecoils.append( (x[i*dump_factor] - start_timeoffset) /float(recoil_relaxation_time))
        pxx.append(abs(pyy[i*dump_factor]/pyy[0]))
        
    #number of displacements per target atom
    ndpa = np.multiply(nrecoils, (Er/(2.5 * Ed * n_atoms)))
    
    #fit
    popt, pcov = opt.curve_fit( lambda ndpa,eta: eta_exp(ndpa,Ebi,eta), ndpa, pxx,p0=2e8)
    
    #anotate to add value to plot
    print 'RIV = {:.4e}'.format(popt[0])
    
    # npa interpolated
    ndpa_interp = np.linspace(0, ndpa[-1]*5, 1000) 
        
        
    fig = plt.figure(1, figsize=fsize)

    plt.xlim(0, ndpa_interp[-1])
    plt.ylim(0.95*pxx[-1] , 1)
    plt.grid()
    
    plt.plot(ndpa, pxx, 'bs', markeredgecolor = 'blue',  markerfacecolor= 'None', markeredgewidth=mew,  markersize = ms,  label = 'MD Simulation')
    plt.plot(ndpa_interp, eta_exp(ndpa_interp,Ebi,*popt),'r-', linewidth = lw, label='Fit')
    plt.xlabel('Number of displacements per atom')
    plt.ylabel(r'$ \frac{\sigma}{\vert \sigma_0 \vert} $')
    
    legtitle  = r'$ \eta_{ri} = $' + '{:.4e}'.format(popt[0]) + ' $ Pa \cdot dpa $' + '\n' + r'$ E_{bi} = $' + '{:.3e}'.format(Ebi) + ' $ Pa $' + '\n' + r'$ E_D = $' + '{:.1e}'.format(Ed) + ' $ eV $'+ '\n' + r'$ E_R = $' + '{:.1e}'.format(Er) + ' $ eV $'
    
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
    if len(sys.argv) <= 6:
        print ('required arguments:\n\tcrv file\n\tpng output name\n\tdumptime for logging (try 500)\n\tEr\n\tEd\n\tEbi')
        
    else:
        crvfile = sys.argv[1]
        outname = sys.argv[2]
        timestep = int(sys.argv[3])
        Er = float(sys.argv[4])
        Ed = float(sys.argv[5])
        Ebi = float(sys.argv[6])
        
        
        extract_plot(crvfile, outname, timestep, Er, Ed, Ebi)
        
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
        






