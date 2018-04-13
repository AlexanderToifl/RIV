#!/usr/bin/env python2

import numpy as np
import pylab as plt
import myPyCRV as CRV
import math as m
import scipy.optimize as opt

def eta_exp(h,s0,Ebi,Ed,Er,eta,n_a):
	# h ... Nr of timesteps - divide by 10000 to get recoil nr. --> calc ndpa
	# s0 .. initial stress
	# Ebi.. biaxial module a-Si
	# Ed .. displace energy
	# Er .. Recoil Energy
	# eta.. RIV
	ndpa = Er/(2.5*Ed)*h/10000./n_a
	return s0*np.exp(-Ebi/(6.*eta)*ndpa)
	

def extract_plot(crvfile, outname, timestep, Er, Ed, Ebi):
	## CRV File - renamed to .crv and manually changed header (crv format) from extracted data file
	
	## PNG output
	
	## timestep used in recoil.in during recoil insertion --> datapoint after each recoil

	#n_atoms = 54872 # aus crvfile lesen!!!!!
	
	crv = CRV.CRV(crvfile)[0]
	#extract mech. stress tensor in x or y
	pyy = crv['pyy']
	x = crv['step']
	n_atoms = crv['atoms'][0]
	#calc timeaxis out of pxx or pyy size
	#x = np.arange(0,len(pyy)*timestep,timestep)
	
	#reduce timeaxis to recoil axis	(every 20 timesteps - 1 recoil)
	x_new = []
	pxx_new = []
	
	for i in range(len(x)/20):
		x_new.append(x[i*20])
		pxx_new.append(pyy[i*20])
	
	#remove first entry
	#x_new.pop()
	#pxx_new.pop()
	
	pxx_new = np.divide(pxx_new, pxx_new[0])
	x_new = np.subtract(x_new, timestep)
	
	#fit to 
	popt, pcov = opt.curve_fit(lambda l,eta: eta_exp(l,pxx_new[0],Ebi,Ed,Er,eta,n_atoms) , x_new, pxx_new, p0 = [6.e13], bounds = [0.,np.inf])
	
	#anotate to add value to plot
	print 'RIV = {:.4e}'.format(popt[0])
	
	#plot fit 
	Pfit = []
	for i in range(len(x_new)):
		Pfit.append(eta_exp(x_new[i],pxx_new[0],Ebi,Ed,Er,popt[0],n_atoms))
	

	fig = plt.figure(1)

	plt.rc('text', usetex=True)  
	plt.rc('font', family='serif') 
	plt.rcParams.update({'font.size': 22})

	plt.axis([0, 100 , 0, 1],log=False)
	plt.grid()
	plt.plot(np.divide(x_new,10000.),np.abs(pxx_new),'bo')
	plt.plot(np.divide(x_new,10000.),np.abs(Pfit),'r-')
	plt.xlabel('Nr. of Recoils', fontsize=14)
	plt.ylabel(r'$ \frac{\sigma}{\vert \sigma_0 \vert} $', fontsize=18)
	plt.legend(loc='upper right', shadow=False, fontsize=12)
	plt.annotate(r'$ RIV = $' + '{:.4e}'.format(popt[0]) + ' $ Pa \cdot dpa $' ,xy = (0, 0), textcoords='figure fraction', xytext=(0.6, 0.85), fontsize = 14)
	plt.annotate(r'$ E_{bi} = $' + '{:.3e}'.format(Ebi) + ' $ Pa $' ,xy = (0, 0), textcoords='figure fraction', xytext=(0.6, 0.8), fontsize = 14)
	plt.annotate(r'$ E_D = $' + '{:.1e}'.format(Ed) + ' $ eV $' ,xy = (0, 0), textcoords='figure fraction', xytext=(0.6, 0.75), fontsize = 14)
	plt.annotate(r'$ E_R = $' + '{:.1e}'.format(Er) + ' $ eV $' ,xy = (0, 0), textcoords='figure fraction', xytext=(0.6, 0.7), fontsize = 14)
	#plt.show()
	fig.savefig(outname)
	plt.close("all")
	
	return popt[0]		
	
	
	

	






