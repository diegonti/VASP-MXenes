"""
Automatic optimizer for slab models in VASP.
The script starts at the initial optimization folder and optimizes the POSCAR
in subsequent folders until fully optimized (combines isif2 and isif7 until 
the external pressure < 1kB and the forces are <0.01)
It sends a calculations, waits for the OUTCAR, reads it and decides if its optimized 
or a next step is needed.

To get the maximum profist of this script, is better to use a bash script tu run 
this file for each MXene or compund (adding the & at the end will run ath the backgorund)
see optimized.sh

Diego Ontiveros
"""

import os
import sys
import time
import shutil

from VASPread import OUTCAR
from structure import CONTCAR

def cpvasp(next_opt):
    """Copies the input VASP files to the next folder"""
    shutil.copy("KPOINTS",next_opt+"/")
    shutil.copy("POTCAR",next_opt+"/")
    shutil.copy("script",next_opt+"/")
    shutil.copy("CONTCAR",next_opt+"/POSCAR")


home = os.path.expanduser("~")
# path = f"{home}/test/Cr3C2/ABC/"
 
path = sys.argv[1]
path1 = path + "opt/"
original_cwd = os.getcwd()

extension = ""

while True:

    os.chdir(path1 + extension)
    poscar = CONTCAR("POSCAR")

    # See if OUTCAR is already there
    path_outcar = path1 + f"{extension}OUTCAR"
    if os.path.exists(path_outcar): pass
    else: os.system(f"qsub -N {poscar.name} script")

    # Waits until OUTCAR is formed
    while not os.path.exists(path_outcar): time.sleep(1)

    # Reads OUTCAR and gets optimization information
    outcar = OUTCAR("OUTCAR")
    pressures, forces, last_pressure, next_opt = outcar.getOpt()

    # If its optimized, finish the program
    if next_opt == "optimized": 

        shutil.copy("OUTCAR",path)
        shutil.copy("CONTCAR",path)

        # Appends geometry in file
        contcar = CONTCAR("CONTCAR")
        a,d = contcar.getGeom()
        geom = f"{contcar.mx.mxName}: {a} {d}\n"
        with open(path+"geom","a") as outFile: outFile.write(geom)

        # Appends energy in file
        E,energies = outcar.getEnergy()
        energy = f"{contcar.mx.mxName}: {E} eV\n"
        with open(home+"energy","a") as outFile: outFile.write(energy)
        
        print(f"\u2713 {path}: Process optimized")
        break

    try: os.mkdir(next_opt)
    except FileExistsError: pass

    cpvasp(next_opt)

    # Each possible optimization next step
    if next_opt == "isif7": 
        extension += "isif7/"
        os.system(rf"sed '/ISIF/c\ISIF = 7' INCAR | sed '/NSW/c\NSW = 19' > {next_opt}/INCAR")

    elif next_opt == "isif2": 
        extension += "isif2/"
        os.system(rf"sed '/ISIF/c\ISIF = 2' INCAR | sed '/NSW/c\NSW = 101' > {next_opt}/INCAR")

    elif next_opt == "isif7a":
        extension += next_opt + "/"
        os.system(rf"sed '/NSW/c\NSW = 15' INCAR > {next_opt}/INCAR")

    



