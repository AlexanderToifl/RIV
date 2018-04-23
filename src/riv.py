#!/usr/bin/env python

import sys
import fileinput
from tempfile import NamedTemporaryFile
import os, subprocess
import myPyCRV as crv
import plot as plot


def change_var(fname, variable, value):

	name = "variable " + variable + " equal "

	with open(fname) as fin, NamedTemporaryFile(dir='.', delete=False) as fout:
		for line in fin:
			if line.startswith(name):
				line = name + str(value) + "\n"
				print "Change variable " + variable +" to " + str(value)
			fout.write(line.encode('utf8'))
		os.rename(fout.name, fname)    
    	
def run_lammps(fname,core_nr, lammps_name='lmp_jpeg'):
    call = "mpirun -np %s %s -in %s" %(core_nr, lammps_name,fname)
    print "Calling \"" + call + "\""
    #command as you type it incmd line 
    #split() is necessary for subprocess
    ret = subprocess.call((call).split())
    print "\n"
	#always do something if call fails                    
    if ret != 0: #simulation failed
        print "Simulation failed"
        return 1
    return 0

def prepand_variables(oname, fname, vfname):
    with open(oname,'w') as o, open(fname) as f, open(vfname) as v:
        content_f = f.read()
        content_v = v.read()
        
        o.write(content_v  + "\n\n" + content_f)

def save_data(logname,ekin,seed):
	outputname = 'data/rec_e' + str(ekin) + '_s_' + str(seed) + '.crv'
	with NamedTemporaryFile(dir='.', delete=False) as fout:
		#write crv head
		fout.write('#b 16 \n#p 1\n#n  step strainx strainy pxx pyy pzz atoms dt temp lx ly lz\n#u  1  1  1  bar  bar  bar  1  ps  K  1  1  1\n#t  0  0  0  0  0  0  0  0  0  0  0  0\n')
		for line in fileinput.input([logname]):
			if not fileinput.isfirstline():
				fout.write(line.encode('utf8'))
		os.rename(fout.name,outputname)
	return outputname
		
def write_crv(outname, seeds, riv):

	crvOUT = crv.newCrvFile()
		
	crvOUT[0].addColumn(name = 'Seed', unit = '1', vals = seeds) 	
	crvOUT[0].addColumn(name = 'Riv', unit = 'Pa dpa', vals = riv)			
	crvOUT.writefile(outname)
        
def main():
	setup_name = 'setup.in'
	amorph_name = 'amorph.in'
	biax_name = 'biax_recoil.in'
	recoil1_name = 'recoil1.in'
	recoil2_name = 'recoil2.in'
    
	logname = 'recoil1.txt'
	tmp_name = 'riv_tmp.in'
	dafi_name = 'recoil1.dat'
	lofi_name = 'log.lammps'
    
	timestep = 500	#dumptime for logging
	
	Ed = 10.		#eV
	Ebi = 111.2e9	#Pa
        
	core_nr = 12
	recoil_nr = 25														#Nr of recoils inserted
	base_cell = 6
	at_per_ev = 1
		
	Ekin = [10]													#Set1 (Alex) kinetic Energy set in eV
	#Ekin = [100,500,1000]												#Set2 (Christian) kinetic Energy set in eV
	seeds = [10516]	 	

	size_auto = False
	cell_size = 18													#fixed cell_size in lattice units
	
    #set Variables 
    
    #amorphization
	#prepand_variables(tmp_name, amorph_name, setup_name)
	#run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')
    
	#biaxial deformation
	#prepand_variables(tmp_name, biax_name, setup_name)
	#run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')
    
	RIV = []

	change_var(setup_name,'i_max',recoil_nr)
	change_var(setup_name,'unit_cell',base_cell)
	change_var(setup_name,'eng_cell_k',at_per_ev)
    
	for i in range(len(Ekin)):
		
		if size_auto == True:
			cell_size = int((((Ekin[i]*recoil_nr*at_per_ev)/8.)^(1./3.)) + base_cell) + 1	
		
		change_var(setup_name,'cell_size',cell_size)
		change_var(setup_name,'ekin',Ekin[i])
		#amorphization
		#prepand_variables(tmp_name, amorph_name, setup_name)
		#run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')
		
		#biaxial deformation
		prepand_variables(tmp_name, biax_name, setup_name)
		run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')
        
		exit(0)
		
		for j in range(len(seeds)):
			
			change_var(setup_name,'seed',seeds[j])
   
			#recoil insertion1
			prepand_variables(tmp_name, recoil1_name, setup_name)
			run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')

			#recoil insertion2
			#prepand_variables(tmp_name, recoil2_name, setup_name)
			#run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')

    
			crvname = save_data(logname,Ekin[i],seeds[j])
			outname = 'data/png/rec_e' + str(Ekin[i]) + '_s_' + str(seeds[j]) + '.png'
			
			#secure dat file
			dataf = 'data/dat/rec_e' + str(Ekin[i]) + '_s_' + str(seeds[j]) + '.dat' 		
			os.rename(dafi_name,dataf)
			
			#secure log file
			logf = 'data/log/log.lammps_rec_e' + str(Ekin[i]) + '_s_' + str(seeds[j])
			os.rename(lofi_name,logf)
			
			#extracten and plotten
			
			RIV.append(plot.extract_plot(crvname,outname,timestep,Ekin[i],Ed,Ebi))

			datname = 'data/riv/recoil_e_' + str(Ekin[i]) + 'seed_' + str(seeds[j]) + '.crv'
			write_crv(datname,seeds,RIV)	
				
		
if __name__ == '__main__':
    main()
        
