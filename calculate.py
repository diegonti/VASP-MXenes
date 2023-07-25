"""
Runs over all paths to do electornic calculations (DOS, BS, WF) for each case.
Run after optimization. Copies CONTCAR to BS/DOS/WF files and sends job to queue.

To use, specify the n (index) and T (termination) of the MXene:
python3 calculate.py [-h] -n N_INDEX [-T TERMINATION]

OR input a specific path: 
python3 calculate.py [-h] -p PATH

If both -n and -p falgs are used. The -p one has preference.

Diego Ontiveros
"""

import os
import shutil
from argparse import ArgumentParser

from VASPread import OUTCAR
from DOS import DOSCAR
from structure import CONTCAR

def calculateMXT(n:int,T:str,calcError=True):
    """Performs optimization for all cases of terminated MXenes (Mn+1XnTx).

    Parameters
    ----------
    `n` : MXene index from the formula Mn+1XnT2.
    `T` : Termination with the index (e.g 'O2').
    `calcError` : To recalculate job if OUTCAR presents error.
    """
    # For Terminated cases
    for mx,mxt in zip(MX,MXT):
        for j,stack in enumerate(stacking):
            for k,hollow in enumerate(hollows[j]):

                # Go to the MXT path
                path = f"{home}/M{n+1}X{n}/{mx}/{mxt}/{stack}/{hollow}/"
                os.chdir(path)

                dirs = ["DOS/","DOS/PBE0/","BS/PBE/","BS/PBE0/"]
                aimsBS_dirs = ["aBS/PBE/","aBS/PBE0/"]

                # extra_dirs = ["BS/PBE/BS2/","BS/PBE0/BS2/","WF/"]

                # Do the calculation in each calculation directory (DOS, BS)
                for dir in dirs: 

                    # In case tha calculation is already done
                    if os.path.exists(path+dir+"vasp.out"): 

                        # And in case there has been an Error
                        if os.path.exists(path+dir+"OUTCAR") and calcError:
  
                            outcar = OUTCAR(path+dir+"OUTCAR")
                            info = outcar.getOpt()
                            if info[-1] == "error":
                                os.chdir(dir)
                                start = dir.split("/")[0].lower()

                                os.system(rf"sed -i '/-pe smp/c\#$ -pe smp 6' script")
                                os.system(rf"sed -i '/--ntasks/c\#SBATCH --ntasks=24' script")
                                os.system(f"{queue} {start}{mxt}_{j}{k} script")
                                os.chdir(path)
                        continue
                    
                    # Move the CONTCAR and send the job to queue
                    try: shutil.copy("CONTCAR",dir+"POSCAR")
                    except FileNotFoundError: print(f"Passing {mxt}_{stack}_{hollow}"); break
                    
                    os.chdir(dir)
                    start = dir.split("/")[0].lower()
                    os.system(f"{queue} {start}{mxt}_{j}{k} script")
                    os.chdir(path)

                for dir in aimsBS_dirs:

                    # In case tha calculation is already done
                    if os.path.exists(path+dir+"fhi-aims.out"): 
                        # Check Error
                        continue
                    
                    # Move the CONTCAR and send the job to queue
                    try: 
                        contcar = CONTCAR("CONTCAR")
                        contcar.toAIMS(dir+"geometry.in")

                    except FileNotFoundError: print(f"Passing {mxt}_{stack}_{hollow}"); break
                    
                    os.chdir(dir)
                    start = dir.split("/")[0].lower()
                    os.system(f"{queue} {start}{mxt}_{j}{k} script")
                    os.chdir(path)


      
def calculateMX(n:int,calcError=True):
    """
    Performs optimization for all cases of pristine MXenes (Mn+1Xn).
    `n` : MXene index from the formula Mn+1Xn.
    `calcError` : To recalculate job if OUTCAR presents error.
    """    
    # For pristine cases
    for mx in MX:
        for j,stack in enumerate(stacking):
                
                path = f"{home}/M{n+1}X{n}/{mx}/{stack}/"
                os.chdir(path)

                dirs = ["DOS/","DOS/PBE0/","BS/"]

                for dir in dirs: 

                    # In case tha calculation is already done
                    if os.path.exists(path+dir+"vasp.out"): 

                        # And in case there has been an Error
                        if os.path.exists(path+dir+"OUTCAR") and calcError:
  
                            outcar = OUTCAR(path+dir+"OUTCAR")
                            info = outcar.getOpt()
                            if info[-1] == "error":
                                os.chdir(dir)
                                start = dir.split("/")[0].lower()

                                os.system(rf"sed -i '/-pe smp/c\#$ -pe smp 6' script")
                                os.system(rf"sed -i '/--ntasks/c\#SBATCH --ntasks=24' script")
                                os.system(f"{queue} {start}{mx}_{j} script")
                                os.chdir(path)
                        continue

                    try: shutil.copy("CONTCAR",dir+"POSCAR")
                    except FileNotFoundError: print(f"Passing {mx}_{stack}"); break
                    
                    # Move the CONTCAR and send the job to queue
                    os.chdir(dir)
                    start = dir.split("/")[0].lower()
                    os.system(f"{queue} {start}{mx}_{j} script")
                    os.chdir(path)


def calculateGeneral(paths):
    """
    Performs optimizations for a given list of paths.
    """
    for i,path in enumerate(paths):

        os.chdir(path)
        print(path)

        if any(h in path for h in ["/H/", "/HM/","/HMX/","/HX/"]): 
            dirs = ["DOS/","DOS/PBE0/","BS/PBE/","BS/PBE0/","BS/PBE/BS2/","BS/PBE0/BS2/","WF/"]
        else: dirs = ["DOS/","DOS/PBE0/","BS/"]

        for dir in dirs: 
            if os.path.exists(path+dir+"vasp.out"): continue # --force
            try: shutil.copy("CONTCAR",dir+"POSCAR")
            except FileNotFoundError: print(f"Passing {i}"); break
            # see also if OUTCAR in file
            
            os.chdir(dir)
            start = dir.split("/")[0].lower()
            os.system(f"{queue} {start}_{i} script")
            os.chdir(path)


def calculateWF(n:int,T:str,limit=1.23,calcError=True):
    """Performs optimization for all cases of terminated MXenes (Mn+1XnTx).

    Parameters
    ----------
    `n` : MXene index from the formula Mn+1XnT2.
    `T` : Termination with the index (e.g 'O2').
    `calcError` : To recalculate job if OUTCAR presents error.
    """
    # For Terminated cases
    for mx,mxt in zip(MX,MXT):
        for j,stack in enumerate(stacking):
            for k,hollow in enumerate(hollows[j]):

                # Go to the MXT path
                path = f"{home}/M{n+1}X{n}/{mx}/{mxt}/{stack}/{hollow}/"
                os.chdir(path)

                dir = "WF/"

                # see DOS0
                dos = DOSCAR(path+"DOS/PBE0/DOSCAR",short=True)
                Eg,VBM,CBM = dos.getBandgap()

                if Eg >= limit: 
                    # print(f"{mxt} {stack} {hollow} : {Eg} {VBM} Correct.")
                    print(path,Eg,VBM,CBM,flush=True)
                else: continue


                # In case tha calculation is already done
                if os.path.exists(path+dir+"vasp.out"): 

                    # And in case there has been an Error
                    if os.path.exists(path+dir+"OUTCAR") and calcError:

                        outcar = OUTCAR(path+dir+"OUTCAR")
                        info = outcar.getOpt()
                        if info[-1] == "error":
                            os.chdir(dir)
                            start = dir.split("/")[0].lower()

                            os.system(rf"sed -i '/-pe smp/c\#$ -pe smp 6' script")
                            os.system(rf"sed -i '/--ntasks/c\#SBATCH --ntasks=24' script")
                            os.system(f"{queue} {start}{mxt}_{j}{k} script")
                            os.chdir(path)
                    continue
                
                # Move the CONTCAR and send the job to queue
                try: shutil.copy("CONTCAR",dir+"POSCAR")
                except FileNotFoundError: print(f"Passing {mxt}_{stack}_{hollow}"); break
                
                os.chdir(dir)
                start = dir.split("/")[0].lower()
                # os.system(rf"sed -i '/-pe smp/c\#$ -pe smp 6' script")
                # os.system(rf"sed -i '/-q iqtc/c\#$ -q iqtc06.q' script")
                os.system(f"{queue} {start}{mxt}_{j}{k} script")
                os.chdir(path)

############################ MAIN PROGRAM #####################

# Cluster PATHS
cluster_home = os.path.realpath(os.path.expanduser("~"))
if "gpfs/" in cluster_home or "/ub" in cluster_home: queue = "sbatch -J"
else: queue = "qsub -N"
home = os.path.abspath("..")

# User arguments parsing
parser = ArgumentParser(description="Runs over all paths to do electronic calculations (DOS, BS, WF) for each case.\
    Run this scripts after optimization (opt.py). It copies CONTCAR to the BS/DOS/WF folders and sends job to queue.",
    usage="\n To use, specify the n (index) and T (termination) of the MXene: \n    python3 calculate.py [-h] -n N_INDEX [-T TERMINATION]\n\
 OR input a specific path: \n    python3 calculate.py [-h] -p PATH\n\
 If both -n and -p falgs are used. The -p one has preference.\n\
 Moreover, to do LOCPOT calculations for WF, use the -WF flag and optionally the -l flag, along the specified -n and -T:\n\
    python3 calculate.py [-h] -n N_INDEX [-T TERMINATION] [-WF] [-l LIMITWF]")

parser.add_argument("-p","--path",type=str,default=None,help="Individual MXene structure folder where the calculation will be done. Optional. Has preference over -n.")
parser.add_argument("-n","--n_index",type=int,help="MXene n index (int) from the formula Mn+1XnT2.")
parser.add_argument("-T","--termination",type=str,default="",help="MXene termination (str) from the formula Mn+1XnT2. Specifyit with the index, i.e 'O2'. \
                    For pristine MXenes, don't use this or use None. Defaults to None.")
parser.add_argument("-WF","--workfunction",action="store_true",help="To send LOCPOT calculations. Use the -l flag to send only for a specified bandgap limit.")
parser.add_argument("-l","--limitWF",type=float,default=1.23,help="The structures with bandgap > limit will be calculated. Defaults to 0.")

args = parser.parse_args()
paths, n, T = args.path, args.n_index, args.termination
calc_wf, limitWF = args.workfunction, args.limitWF


if calc_wf and n is None: parser.error("-WF requires -n flag and optinally -T.")
elif paths is None and n is None: parser.error(f"Some arguments are needed. For help, run python3 calculate.py -h.")


if not paths is None: calculateGeneral(paths)
else:

    # n = 2                               # MXene n number (thickness)
    # T = "O2"                            # Termination

    # MXene cases
    M = ["Cr","Hf","Mo","Nb","Sc","Ta","Ti","V","W","Y","Zr"]
    mc = [m + str(n+1) + "C" + str(n) for m in M]   # X = C cases
    mn = [m + str(n+1) + "N" + str(n) for m in M]   # X = N cases
    MX = mc + mn                                    # All studied MXenes (pristine)
    MXT = [i + T for i in MX if i != ""]            # All studied MXenes (terminated)

    # Structure cases
    stacking = ["ABC","ABA"]
    hABA = ["H","HMX","HX"]
    hABC = ["HM","HMX","HX"]
    hollows = [hABC,hABA]

    if calc_wf:
        calculateWF(n,T,limitWF)
    else:
        if T == "": 
            accept = input(f"Are you sure you want to calculate pristine MXenes with n = {n}? (Y/n): ")
            if accept == "Y": calculateMX(n)
            else: print("Closing...")
        else: 
            accept = input(f"Are you sure you want to calculate terminated MXenes with n = {n} and T = {T}? (Y/n): ")
            if accept == "Y": calculateMXT(n,T)
            else: print("Closing...")

#! Changes:
# import general searcher that provides paths and use general calculator.
# get mx/stack/hollows from name path or function gives it
# try except if mx/stack/hollows not found