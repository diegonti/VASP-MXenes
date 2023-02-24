"""
Runs over all paths to do electornic calculations (DOS, BS, WF) for each case.
Run after optimization. Copies CONTCAR to BS7DOS/WF files and sends job to queue.

Diego Ontiveros
"""

import os
import sys
import shutil

def calculateMXT(n:int,T:str):
    """Performs optimization for all cases of terminated MXenes (Mn+1XnTx).

    Parameters
    ----------
    `n` : MXene index.
    `T` : Termination.
    """
    # For Terminated cases
    for mx,mxt in zip(MX,MXT):
        for j,stack in enumerate(stacking):
            for k,hollow in enumerate(hollows[j]):

                path = f"{home}/M{n+1}X{n}/{mx}/{mxt}/{stack}/{hollow}/"
                os.chdir(path)
                print(path)

                dirs = ["DOS/","DOS/PBE0/","BS/PBE/","BS/PBE0/","BS/PBE/BS2/","BS/PBE0/BS2/","WF/"]

                for dir in dirs: 
                    shutil.copy("CONTCAR",dir+"POSCAR")
                    
                    os.chdir(dir)
                    start = dir.split("/")[0].lower()
                    os.system(f"qsub -N {start}{mxt}_{j}{k} script")
                    os.chdir(path)

      
def calculateMX(n:int):
    """
    Performs optimization for all cases of pristine MXenes (Mn+1Xn).
    `n` : MXene index.
    """    
    # For pristine cases
    for mx in MX:
        for j,stack in enumerate(stacking):
                
                path = f"{home}/M{n+1}X{n}/{mx}/{stack}/"
                os.chdir(path)
                print(path)

                dirs = ["DOS/","DOS/PBE0/","BS/"]

                for dir in dirs: 
                    shutil.copy("CONTCAR",dir+"POSCAR")
                    
                    os.chdir(dir)
                    start = dir.split("/")[0].lower()
                    os.system(f"qsub -N {start}{mx}_{j} script")
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
            shutil.copy("CONTCAR",dir+"POSCAR")
            
            os.chdir(dir)
            start = dir.split("/")[0].lower()
            os.system(f"qsub -N {start}_{i} script")
            os.chdir(path)

############################ MAIN PROGRAM #####################

home = os.path.expanduser("~")

if sys.argv[1].startswith("-p"): 
    paths = sys.argv[2:]
    general_calculation = True
else:
    general_calculation = False
    if sys.argv[1].startswith("-m"): pos = 1
    else: pos = 0

    # MXene n index input (thickness)
    try: n = int(sys.argv[1+pos])
    except IndexError: raise IndexError("Add the index (n) and termination (T) as arguments. (for pristine don't add T or T=None, for terminated, T=O2)")

    # MXene termination input
    try: T = sys.argv[2+pos]
    except IndexError: T = ""
    if T == "None": T = ""

    # n = 2                               # MXene n number (thickness)
    # T = "O2"                            # Termination

    # MXene cases
    M = ["Cr","Hf","Mo","Nb","Sc","Ta","Ti","V","W","Y","Zr"]
    mc = [m + str(n+1) + "C" + str(n) for m in M]   # X = C cases
    mn = [m + str(n+1) + "N" + str(n) for m in M]   # X = N cases
    MX = mc + mn                                    # All studied MXenes (pristine)
    MXT = [i + T for i in MX if i != ""]            # All studied MXenes (temrinated)

    # Structure cases
    stacking = ["ABA","ABC"]
    hABA = ["H","HMX","HX"]
    hABC = ["HM","HMX","HX"]
    hollows = [hABA,hABC]

if general_calculation: calculateGeneral(paths)
else:
    if T == "": 
        accept = input(f"Are you sure you want to calculate pristine MXenes with n = {n}? (Y/n): ")
        if accept == "Y": calculateMX(n)
        else: print("Closing...")
    else: 
        accept = input(f"Are you sure you want to calculate terminated MXenes with n = {n} and T = {T}? (Y/n): ")
        if accept == "Y": calculateMXT(n,T)
        else: print("Closing...")