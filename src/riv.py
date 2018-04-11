#!/usr/bin/env python

import sys
import fileinput
import os, subprocess
    
    	
def run_lammps(fname,core_nr, lammps_name='lammps-daily'):
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
        
def main():
    setup_name = 'setup.in'
    amorph_name = 'amorph.in'
    biax_name = 'biax_recoil.in'
    recoil1_name = 'recoil1.in'
    recoil2_name = 'recoil2.in'
    
    tmp_name = 'riv_tmp.in'
    
    core_nr = 8
    
    #amorphization
    prepand_variables(tmp_name, amorph_name, setup_name)
    run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')
    
    #biaxial deformation
    prepand_variables(tmp_name, biax_name, setup_name)
    run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')
    
    #recoil insertion1
    prepand_variables(tmp_name, recoil1_name, setup_name)
    run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')
    
    #recoil insertion2
    prepand_variables(tmp_name, recoil2_name, setup_name)
    run_lammps(tmp_name, core_nr)#, lammps_name='lmp_jpeg')
    
    
if __name__ == '__main__':
    main()
        
