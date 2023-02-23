"""
Runs over all paths to optimize (using optimizer.py) each case.
Uses shell commands and nohup to run the processes in the background.

Diego Ontiveros
"""

import os
import sys

def optimizeMXT(n:int,T:str):
    """Performs optimization for all cases of terminated MXenes (Mn+1XnTx).

    Parameters
    ----------
    `n` : MXene index.
    `T` : Termination.
    """
    # For Terminated cases
    for mx,mxt in zip(MX,MXT):
        for j,stack in enumerate(stacking):
            for hollow in hollows[j]:
                path = f"{home}/M{n+1}X{n}/{mx}/{mxt}/{stack}/{hollow}/"
                print(path)
                os.system(f"nohup python3 optimizer.py {path} &")

      
def optimizeMX(n:int):
    """
    Performs optimization for all cases of pristine MXenes (Mn+1Xn).
    `n` : MXene index.
    """    
    # For pristine cases
    for mx in MX:
        for stack in stacking:
                path = f"{home}/M{n+1}X{n}/{mx}/{stack}/"
                print(path)

                os.system(f"nohup python3 optimizer.py {path} &")

def optimizeGeneral(paths):
    """
    Performs optimizations for a given list of paths.
    """
    for path in paths:
        os.system(f"nohup python3 optimizer.py {path} &")


######################### MAIN PROGRAM #########################

# MXene n index input (thickness)
try: n = int(sys.argv[1])
except IndexError: raise IndexError("Add the index (n) and termination (T) as arguments. (for pristine don't add T or T=None, for terminated, T=O2)")

# MXene termination input
try: T = sys.argv[2]
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

home = os.path.expanduser("~")

if T == "": 
    accept = input(f"Are you sure you want to optimize pristine MXenes with n = {n}? (Y/n): ")
    if accept == "Y": optimizeMX(n)
    else: print("Closing...")
else: 
    accept = input(f"Are you sure you want to optimize terminated MXenes with n = {n} and T = {T}? (Y/n): ")
    if accept == "Y": optimizeMXT(n,T)
    else: print("Closing...")

