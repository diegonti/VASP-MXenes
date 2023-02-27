"""
Automatic optimizer for slab models in VASP.
The script starts at the initial optimization folder and optimizes the POSCAR
in subsequent folders until fully optimized (combines isif2 and isif7 until 
the external pressure < 1kB and the forces are <0.01 eV/Ang)
It sends a calculations, waits for the OUTCAR, reads it and decides if its optimized 
or a next step is needed.

To get the maximum profist of this script, is better to use a bash/python script tu run 
this file for each MXene or compound (adding the & at the end will run at the backgorund)
see opt.py.

Diego Ontiveros
"""

import os
import sys
import time
import shutil
import random

from VASPread import OUTCAR
from structure import CONTCAR

######################## Functions general pourpuses ########################
def getStructure(path):
    """Gets structure (stacking and hollows) from the folder path."""
    # Stacking
    if "/ABA/" in path: stack = "ABA"
    elif "/ABC/" in path: stack = "ABC"

    # Hollows
    hollows = ""
    h = ["/HM/","/HMX/","/HX/","/H/"]
    for hollow in h: 
        if hollow in path: hollows = hollow.split("/")[1]

    return stack, hollows

######################## Functions for each optimization step ########################
def repeated(folders,next_opt):
    """Filters if next_opt is repeated."""

    cases = ["isif7","isif2","isif4","isif7a"]
    try: 
        repeat = next_opt == folders[-1] and next_opt == folders[-2]
    except IndexError: repeat = False

    cases.remove(next_opt)
    if repeat: next_opt = cases[0]

    return next_opt

def cpvasp(next_opt):
    """Copies the input VASP files to the next folder"""
    shutil.copy("KPOINTS",next_opt+"/")
    shutil.copy("POTCAR",next_opt+"/")
    shutil.copy("script",next_opt+"/")
    shutil.copy("CONTCAR",next_opt+"/POSCAR")

def optimizationRandomStep(counter,vacuum=None):
    """Reduce vacuum if too many iterations have passed. Choose a random isif for the next step."""
    if vacuum is None: vacuum = 10

    if counter > 20:
        contcar = CONTCAR("CONTCAR")
        contcar.addVacuum(v=vacuum)
        os.rename("CONTCAR","CONTCARi")
        contcar.write(path="CONTCAR")
        print(f"{path}: Vaccum to 10 at iteration {counter}")
        vaccuum_reduced = True
    else:
        vaccuum_reduced = False

    next_opt = random.choice(["isif7","isif2","isif4"])
    return next_opt, vaccuum_reduced

def optimizationNextStep(next_opt,extension):
    """Creates the next optimization step depending on next_opt."""
    extension += next_opt + "/"
    
    if next_opt == "isif7": 
        os.system(rf"sed '/ISIF/c\ISIF = 7' INCAR | sed '/NSW/c\NSW = 19' > {next_opt}/INCAR")

    elif next_opt == "isif2": 
        os.system(rf"sed '/ISIF/c\ISIF = 2' INCAR | sed '/NSW/c\NSW = 101' > {next_opt}/INCAR")

    elif next_opt == "isif7a":
        os.system(rf"sed '/NSW/c\NSW = {len(pressures)-2}' INCAR > {next_opt}/INCAR")

    elif next_opt == "isif4":
        os.system(rf"sed '/ISIF/c\ISIF = 4' INCAR | sed '/NSW/c\NSW = 201' > {next_opt}/INCAR")
    
    return extension

######################## Functions once the struture has been optimized ########################
def updateOutFiles(stack, hollows):
    """Appends Geometry and Energy to their designated out files from the optimization."""

    # Appends geometry in file
    a,d = contcar.getGeom()
    geom = f"{contcar.mx.mxName} {stack} {hollows} : {a} {d}\n"
    with open(home+"/geom.out","a") as outFile: outFile.write(geom)

    # Appends energy in file
    E,energies = outcar.getEnergy()
    energy = f"{contcar.mx.mxName} {stack} {hollows} : {E} eV\n"
    with open(home+"/energy.out","a") as outFile: outFile.write(energy)


def copyToParent(vaccuum_reduced:bool,contcar:CONTCAR):
    """Copies optimized OUTCAR and CONTCAR to the parent MXene folder."""
    shutil.copy("OUTCAR",path)
    if vaccuum_reduced:
        shutil.copy("CONTCAR",path+"CONTCARi")
        contcar.addVacuum(30)
        contcar.write(path+"CONTCAR")
    else: 
        shutil.copy("CONTCAR",path)


####################################################################################
################################### MAIN PROGRAM ###################################

home = os.path.expanduser("~")
path = sys.argv[1]
path1 = path + "opt/"
max_iterations = 50

extension = ""
stack,hollows = getStructure(path)

folders = []
counter = 0
vaccuum_reduced = False
while True:

    os.chdir(path1 + extension)
    poscar = CONTCAR("POSCAR")

    # See if OUTCAR is already there
    path_outcar = path1 + f"{extension}OUTCAR"
    if os.path.exists(path_outcar): 
        # go to next folder
        dirs = [d for d in os.listdir() if os.path.isdir(d)]
        try: 
            extension += dirs[0]+"/"
            counter += 1
            continue
        except IndexError: pass
    else: os.system(f"qsub -N {poscar.name}{stack} script")

    # Waits until OUTCAR is formed
    while not os.path.exists(path_outcar): time.sleep(1)

    # Reads OUTCAR and gets optimization information
    outcar = OUTCAR("OUTCAR")
    pressures, forces, last_pressure, next_opt = outcar.getOpt()

    # If its optimized, finish the program
    if next_opt == "optimized": 
        contcar = CONTCAR("CONTCAR")
        updateOutFiles(stack,hollows)
        copyToParent(vaccuum_reduced,contcar)
            
        print(f"\u2713 {path}: Process optimized")
        break

    # Finishig the program when too many iteration pass
    if counter >= max_iterations:
        print(f"Max iterations ({max_iterations}) surpassed. Case: {path}")
        break
    elif counter == 10:
        print(f"{path}: Surpassed 10 iterations!")

    # Case where neither forces or pressure are optimized
    if next_opt == "Random":
        next_opt,vaccuum_reduced = optimizationRandomStep(counter,vacuum=10)

    # Generates next_opt folder and copies necessary files
    next_opt = repeated(folders,next_opt)
    try: os.mkdir(next_opt)
    except FileExistsError: pass
    folders.append(next_opt)
    cpvasp(next_opt)

    # Each possible optimization next step
    optimizationNextStep(next_opt,extension)

    counter += 1

    



