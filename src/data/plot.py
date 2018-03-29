#!/usr/bin/env python2

import numpy as np
import pylab as plt
import myPyCRV as CRV

n_seeds = 30
width =	 1.			#bin width

def plot_hist(outname, data, width, lo_x, hi_x, lo_y, hi_y):

	mean = (np.asarray(data)).mean()

	bins = np.arange(lo_x,hi_x,width)
	histo,bins1 = np.histogram(data,bins=bins,density = False)
	bins2 = np.delete(bins1,len(bins1)-1)
	width_a = np.multiply(np.ones(len(bins1)-1),width)

	fig = plt.figure(1)

	plt.rc('text', usetex=True)  
	plt.rc('font', family='serif') 
	plt.rcParams.update({'font.size': 22})

	plt.text(6,20, 'Mean Yield = {:.2}'.format(mean), backgroundcolor='white')

	plt.axis([lo_x, hi_x , lo_y, hi_y],log=False)
	plt.bar(bins2, histo ,width_a, align='center', alpha=0.9, color='blue',label='yield distribution')
	plt.axvline(x=mean, ymin=0, ymax = 1, linewidth=2, color='green', label='mean')
	plt.grid()
	plt.xlabel('Sputteryield', fontsize=12)
	plt.ylabel('\# of Experiments', fontsize=12)
	plt.legend(loc='upper right', shadow=False, fontsize=12)
	
	print 'Mean Value of Yield: ' + str(mean)
    
	fig.savefig(outname)
	plt.close("all")

if __name__ == '__main__':
	## CRV File - all seeds for all angles with 1 atom
	crvfile = 'recoil_20_10516_1.crv'
	outname = 'rec_50eV_20_10516_y.png'
	timestep = 500

	crv = CRV.CRV(crvfile)[0]
	pyy = crv['pyy']
	
	x = np.arange(0,len(pyy)*timestep,timestep)
	
	x_new = []
	pxx_new = []
	
	print len(x)
	print len(pyy)
	
	x_new.append(x[0])
	pxx_new.append(pyy[0])
	
	for i in range(len(x)/20):
		x_new.append(x[i*20])
		pxx_new.append(pyy	[i*20])
		
	print len(x_new)
	print len(pxx_new)

	fig = plt.figure(1)

	plt.rc('text', usetex=True)  
	plt.rc('font', family='serif') 
	plt.rcParams.update({'font.size': 22})

	#plt.text(6,20, 'Mean Yield = {:.2}'.format(mean), backgroundcolor='white')

	plt.axis([0, 200000 , 0, 0.3],log=False)
	plt.grid()
	plt.plot(x_new,np.abs(pxx_new),'b-')
	plt.xlabel('Timestep', fontsize=12)
	plt.ylabel('Pyy', fontsize=12)
	plt.legend(loc='upper right', shadow=False, fontsize=12)
	 
	plt.show()
	fig.savefig(outname)
	plt.close("all")		
	

	






