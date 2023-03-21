"""
Runs over all paths to optimize (using optimizer.py) each case.
Uses shell commands and nohup to run the processes in the background.

To use, specify the n (index) and T (termination) of the MXene:
python3 opt.py [-h] -n N_INDEX [-T TERMINATION]

Diego Ontiveros
"""

import os
from argparse import ArgumentParser

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
                # print(path)
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
                # print(path)
                os.system(f"nohup python3 optimizer.py {path} &")

def optimizeGeneral(paths):
    """
    Performs optimizations for a given list of paths.
    """
    for path in paths:
        os.system(f"nohup python3 optimizer.py {path} &")


######################### MAIN PROGRAM #########################

# Inputs in program, if needed
# n = 2                               # MXene n index (thickness)
# T = "O2"                            # MXene Termination

# Parsing user arguments
parser = ArgumentParser(description="Runs over all specified paths (with n and T) to run a background optimization proces. \
                        More precisely, uses nohup to run the optimization.py script for each MXene structure folder.")
parser.add_argument("-n","--n_index",type=int,help="MXene n index (int) from the formula Mn+1XnT2.",required=True)
parser.add_argument("-T","--termination",type=str,default="",help="MXene termination (str) from the formula Mn+1XnT2. Specifyit with the index, i.e 'O2'. \
                    For pristine MXenes, don't use this or use None. Defaults to None.")
args = parser.parse_args()
n,T = args.n_index, args.termination
if T == "None": T = ""

# MXene cases
M = ["Cr","Hf","Mo","Nb","Sc","Ta","Ti","V","W","Y","Zr"]
mc = [m + str(n+1) + "C" + str(n) for m in M]   # X = C cases
mn = [m + str(n+1) + "N" + str(n) for m in M]   # X = N cases
MX = mc + mn                                    # All studied MXenes (pristine)
MXT = [i + T for i in MX if i != ""]            # All studied MXenes (temrinated)

# Structure cases
stacking = ["ABC","ABA"]
hABA = ["H","HMX","HX"]
hABC = ["HM","HMX","HX"]
hollows = [hABC,hABA]

# home = os.path.expanduser("~")
home = os.path.abspath("..")

if T == "": 
    accept = input(f"Are you sure you want to optimize pristine MXenes with n = {n}? (Y/n): ")
    if accept == "Y": optimizeMX(n)
    else: print("Closing...")
else: 
    accept = input(f"Are you sure you want to optimize terminated MXenes with n = {n} and T = {T}? (Y/n): ")
    if accept == "Y": optimizeMXT(n,T)
    else: print("Closing...")

