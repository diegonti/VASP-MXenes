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
import time
import shutil

from VASPread import OUTCAR
from structure import CONTCAR
from VASP import MX

path = "~/test/Cr3C2/ABC/"
path1 = path + "opt/"     # change this to the folder 
original_cwd = os.getcwd()

extension = ""

while True:
    # cwd ?

    os.chdir(path1 + extension)
    poscar = CONTCAR("POSCAR")
    os.system(f"qsub -N opt{poscar.name} script")

    path_outcar = path1 + f"{extension}OUTCAR"
    while not os.path.exists(path_outcar):
        time.sleep(1)
    print("File found")

    outcar = OUTCAR("OUTCAR")
    pressures, forces, last_pressure, next_opt = outcar.getOpt()


    if next_opt == "optimized": 

        shutil.copy("OUTCAR",path1)
        shutil.copy("CONTCAR",path1)
        E, = outcar.getEnergy()

        contcar = CONTCAR("CONTCAR")
        geom = f"{contcar.mx.mxName}: {contcar.getGeom()}\n"
        with open(path+"geom","a") as outFile: outFile.write(geom)

        print("Process optimized")
        break

    os.mkdir(next_opt)
    os.system(f"cpvasp {next_opt}")
    if next_opt == "isif7": 
        extension += "isif7/"
        os.system(f"sed '/ISIF/c\ISIF = 7' INCAR | sed '/NSW/c\NSW = 19' > {next_opt}/INCAR")

    elif next_opt == "isif2": 
        extension += "isif2/"
        os.system(f"sed '/ISIF/c\ISIF = 2' INCAR | sed '/NSW/c\NSW = 101' > {next_opt}/INCAR")
    # change INCAR
    



