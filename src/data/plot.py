#!/usr/bin/env python2

import numpy as np
import pylab as plt
import myPyCRV as CRV
import math as m
import scipy.optimize as opt

def eta_exp(h,s0,Ebi,Ed,Er,eta):
	# h ... Nr of timesteps - divide by 10000 to get recoil nr. --> calc ndpa
	# s0 .. initial stress
	# Ebi.. biaxial module a-Si
	# Ed .. displace energy
	# Er .. Recoil Energy
	# eta.. RIV
	ndpa = Er/(2.5*Ed)*h	#/10000.
	return s0*np.exp(-Ebi/(6.*eta)*ndpa)
	
if __name__ == '__main__':
	## CRV File - renamed to .crv and manually changed header (crv format) from extracted data file
	crvfile = 'mayr.crv'
	## PNG output
	outname = 'mayr.png'
	## timestep used in recoil.in during recoil insertion --> datapoint after each recoil
	timestep = 1 #500
	
	Er = 500.		#eV
	Ed = 10.		#eV
	Ebi = 199.75e9	#Pa
	
	crv = CRV.CRV(crvfile)[0]
	#extract mech. stress tensor in x or y
	pyy = crv['pyy']
	x_n = crv['n_r']
	#calc timeaxis out of pxx or pyy size
	x = np.arange(0,len(pyy)*timestep,timestep)
	
	#reduce timeaxis to recoil axis	(every 20 timesteps - 1 recoil)
	x_new = []
	pxx_new = []
	
	#for i in range(len(x)/20):
	#	x_new.append(x[i*20])
	#	pxx_new.append(pyy[i*20])
	
	for i in range(len(x)/1):
		x_new.append(x[i*1])
		pxx_new.append(pyy[i*1])
		
	#remove first entry
	x_new.pop()
	#pxx_new.pop()

	#fit to 
	popt, pcov = opt.curve_fit(lambda l,eta: eta_exp(l,pxx_new[0],Ebi,Ed,Er,eta) , x_n, pxx_new, p0 = [6.e13], bounds = [0.,np.inf])
	
	#anotate to add value to plot
	print 'RIV = {:.4e}'.format(popt[0])
	
	#plot fit 
	Pfit = []
	for i in range(len(x_n)):
		Pfit.append(eta_exp(x_n[i],pxx_new[0],Ebi,Ed,Er,popt[0]))
	

	fig = plt.figure(1)

	plt.rc('text', usetex=True)  
	plt.rc('font', family='serif') 
	plt.rcParams.update({'font.size': 22})

	plt.axis([0, 100 , 0, 1],log=False)
	plt.grid()
	plt.plot(x_n,np.abs(pxx_new),'bo')
	plt.plot(x_n,np.abs(Pfit),'r-')
	plt.xlabel('Nr. of Recoils', fontsize=14)
	plt.ylabel(r'$ \frac{\sigma}{\vert \sigma_0 \vert} $', fontsize=18)
	plt.legend(loc='upper right', shadow=False, fontsize=12)
	plt.annotate('RIV = {:.4e} Pa dpa'.format(popt[0]) ,xy = (0, 0), textcoords='figure fraction', xytext=(0.6, 0.85), fontsize = 14)
	plt.annotate('Ebi = {:.3e} Pa'.format(Ebi) ,xy = (0, 0), textcoords='figure fraction', xytext=(0.6, 0.8), fontsize = 14)
	plt.annotate('ED = {:.1e} eV'.format(Ed) ,xy = (0, 0), textcoords='figure fraction', xytext=(0.6, 0.75), fontsize = 14)
	plt.annotate('ER = {:.1e} eV'.format(Er) ,xy = (0, 0), textcoords='figure fraction', xytext=(0.6, 0.7), fontsize = 14)
	plt.show()
	fig.savefig(outname)
	plt.close("all")		
	

	






