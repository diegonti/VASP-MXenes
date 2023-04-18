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

    if hollow == "": pristine = True
    else: pristine = False

    return stack, hollows, pristine

######################## Functions for each optimization step ########################
def repeated(folders,next_opt):
    """Filters if next_opt is repeated."""

    cases = ["isif7","isif2","isif4","isif7a"]
    try: 
        repeat = next_opt == folders[-1] and next_opt == folders[-2]
    except IndexError: repeat = False

    try: cases.remove(next_opt)
    except ValueError: pass

    if repeat: next_opt = cases[0]

    return next_opt

def cpvasp(next_opt,error_flag):
    """Copies the input VASP files to the next folder"""
    pos_file = "POSCAR" if error_flag else "CONTCAR"
    shutil.copy("KPOINTS",next_opt+"/")
    shutil.copy("POTCAR",next_opt+"/")
    shutil.copy("script",next_opt+"/")
    shutil.copy(pos_file,next_opt+"/POSCAR")

def optimizationRandomStep(counter,vacuum=None):
    """Reduce vacuum if too many iterations have passed. Choose a random isif for the next step."""
    if vacuum is None: vacuum = 10

    if counter > 20:
        contcar = CONTCAR("CONTCAR")
        contcar.addVacuum(v=vacuum)
        os.rename("CONTCAR","CONTCARi")
        contcar.write(path="CONTCAR")
        print(f"{path}: Vaccum to 10 at iteration {counter}",flush=True)
        vaccuum_reduced = True
    else:
        vaccuum_reduced = False

    next_opt = random.choice(["isif7","isif2","isif4"])
    return next_opt, vaccuum_reduced


def optimizationError(next_opt,folders):
    """changes script to less cores if EDDDAV error is found."""
    error_flag = False
    if next_opt == "error":
        error_flag = True
        try: next_opt = folders[-1]
        except IndexError: next_opt = random.choice(["isif7","isif2","isif4"])

        os.system(rf"sed -i '/-pe smp/c\#$ -pe smp 6' script")
        os.system(rf"sed -i '/--ntasks/c\#SBATCH --ntasks=24' script")
            
    return next_opt, error_flag


def optimizationNextStep(next_opt,extension):
    """Creates the next optimization step in INCAR depending on next_opt."""
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

# Cluster PATHS
cluter_home = os.path.realpath(os.path.expanduser("~"))
if "gpfs/" in cluter_home or "/ub" in cluter_home: queue = "sbatch -J"
else: queue = "qsub -N"
home = os.path.abspath("..")
path = sys.argv[1]
if not path.endswith("/"): path += "/"
path1 = path + "opt/"
max_iterations = 50

extension = ""
stack,hollows,pristine = getStructure(path)
stack_indicator = 1 if stack=="ABA" else 0

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
            folders.append(dirs[0])
            continue
        except IndexError: pass
    else: os.system(f"{queue} {poscar.name}_{stack_indicator}{hollows} script")

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
            
        print(f"\u2713 {path}: Process optimized. {counter} iterations.")
        break

    # Finishig the program when too many iteration pass
    if counter >= max_iterations:
        print(f"Max iterations ({max_iterations}) surpassed. Case: {path}")
        break
    elif counter == 10:
        print(f"{path}: Surpassed 10 iterations!",flush=True)

    # Case where neither forces or pressure are optimized
    if next_opt == "Random":
        next_opt,vaccuum_reduced = optimizationRandomStep(counter,vacuum=10)

    # To avaid repeted calculations
    next_opt = repeated(folders,next_opt)
    
    # If EDDDAV Error detected
    next_opt, error_flag = optimizationError(next_opt,folders)

    # Generates next_opt folder and copies necessary files
    try: os.mkdir(next_opt)
    except FileExistsError: pass
    cpvasp(next_opt,error_flag)
    folders.append(next_opt)

    # Each possible optimization next step
    extension = optimizationNextStep(next_opt,extension)

    counter += 1


    



