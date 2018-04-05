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
	ndpa = Er/(2.5*Ed)*h/10000.
	return s0*np.exp(-Ebi/(6.*eta)*ndpa)
	
if __name__ == '__main__':
	## CRV File - renamed to .crv and manually changed header (crv format) from extracted data file
	crvfile = 'recoil_40_10516_1.crv'
	## PNG output
	outname = 'rec_50eV_40_10516_y.png'
	## timestep used in recoil.in during recoil insertion --> datapoint after each recoil
	timestep = 500
	
	Er = 50.		#eV
	Ed = 10.		#eV
	Ebi = 150.e9	#Pa
	
	crv = CRV.CRV(crvfile)[0]
	#extract mech. stress tensor in x or y
	pyy = crv['pyy']
	#calc timeaxis out of pxx or pyy size
	x = np.arange(0,len(pyy)*timestep,timestep)
	
	#reduce timeaxis to recoil axis	(every 20 timesteps - 1 recoil)
	x_new = []
	pxx_new = []
	
	for i in range(len(x)/20):
		x_new.append(x[i*20])
		pxx_new.append(pyy[i*20])
		
	#remove first entry
	x_new.pop()
	pxx_new.pop()

	#fit to 
	popt, pcov = opt.curve_fit(lambda l,eta: eta_exp(l,pxx_new[0],Ebi,Ed,Er,eta) , x_new, pxx_new, p0 = [8.e12], bounds = [0.,np.inf])
	
	print popt[0]
	
	#plot fit 
	Pfit = []
	for i in range(len(x_new)):
		Pfit.append(eta_exp(x_new[i],pxx_new[0],Ebi,Ed,Er,popt[0]))
	

	fig = plt.figure(1)

	plt.rc('text', usetex=True)  
	plt.rc('font', family='serif') 
	plt.rcParams.update({'font.size': 22})

	#plt.text(6,20, 'Mean Yield = {:.2}'.format(mean), backgroundcolor='white')

	plt.axis([0, 300000 , 0, 0.3],log=False)
	plt.grid()
	plt.plot(x_new,np.abs(pxx_new),'b-')
	plt.plot(x_new,np.abs(Pfit),'r-')
	plt.xlabel('Timestep', fontsize=12)
	plt.ylabel('Pyy', fontsize=12)
	plt.legend(loc='upper right', shadow=False, fontsize=12)
	 
	plt.show()
	fig.savefig(outname)
	plt.close("all")		
	

	






