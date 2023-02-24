"""
Automatic optimizer for slab models in VASP.
The script starts at the initial optimization folder and optimizes the POSCAR
in subsequent folders until fully optimized (combines isif2 and isif7 until 
the external pressure < 1kB and the forces are <0.01 eV/Ang)
It sends a calculations, waits for the OUTCAR, reads it and decides if its optimized 
or a next step is needed.

To get the maximum profist of this script, is better to use a bash/python script tu run 
this file for each MXene or compound (adding the & at the end will run at the backgorund)
see opt.py

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

def repeated(folders,next_opt):
    """Filters if next_opt is repeated."""

    cases = ["isif7","isif2"]
    try: 
        repeat = next_opt == folders[-1] and next_opt == folders[-2]
    except IndexError: repeat = False

    cases.remove(next_opt)
    if repeat: next_opt = cases[0]

    return next_opt


home = os.path.expanduser("~")
# path = f"{home}/test/Cr3C2/ABC/"
 
path = sys.argv[1]
path1 = path + "opt/"
original_cwd = os.getcwd()
max_iterations = 50

extension = ""
stack,hollows = getStructure(path)

folders = []
counter = 0
while True:

    os.chdir(path1 + extension)
    poscar = CONTCAR("POSCAR")

    # See if OUTCAR is already there
    path_outcar = path1 + f"{extension}OUTCAR"
    if os.path.exists(path_outcar): 
        # go to next folder
        dirs = [d for d in os.listdir() if os.path.isdir(d)]
        try: extension += dirs[0]+"/"; continue
        except IndexError: pass
    else: os.system(f"qsub -N {poscar.name}{stack} script")

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
        geom = f"{contcar.mx.mxName} {stack} {hollows} : {a} {d}\n"
        with open(home+"/geom.out","a") as outFile: outFile.write(geom)

        # Appends energy in file
        E,energies = outcar.getEnergy()
        energy = f"{contcar.mx.mxName} {stack} {hollows} : {E} eV\n"
        with open(home+"/energy.out","a") as outFile: outFile.write(energy)
        
        print(f"\u2713 {path}: Process optimized")
        break

    if counter >= max_iterations:
        print(f"Max iterations ({max_iterations}) surpassed. Case: {path}")
        break


    next_opt = repeated(folders,next_opt)

    try: os.mkdir(next_opt)
    except FileExistsError: pass

    folders.append(next_opt)

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
        os.system(rf"sed '/NSW/c\NSW = {len(pressures)-2}' INCAR > {next_opt}/INCAR")

    elif next_opt == "isif4":
        extension += next_opt + "/"
        os.system(rf"sed '/ISIF/c\ISIF = 4' INCAR | sed '/NSW/c\NSW = 201' > {next_opt}/INCAR")

    counter += 1

    



