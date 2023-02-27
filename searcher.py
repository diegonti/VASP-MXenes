"""
General path searcher for the cluster folders. It searches in a tree-style
structure such as the one given by VASP.py file generator.

Diego Ontiveros
"""

import os

home = os.path.expanduser("~")

dirsMXT = ["DOS/","DOS/PBE0/","BS/PBE/","BS/PBE0/","BS/PBE/BS2/","BS/PBE0/BS2/","WF/"]
dirsMXT = ["DOS/","DOS/PBE0/","BS/"]

def path_tree(n:int,T:str=None):
    """Performs optimization for all cases of terminated MXenes (Mn+1XnTx).

    Parameters
    ----------
    `n` : MXene index.
    `T` : Termination. '' or None indicate pristine MXenes. 'T2' for terminated.

    Returns
    ----------
    `paths` : List of paths.
    `data`  : extra info of the MXene. (name, stacking, hollows).
    """
    if T == "" or T == None: pristine = True
    else: pristine = False
    
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

    paths, data = [], []

    # For Pristine cases
    if pristine:
        for mx in MX:
            for j,stack in enumerate(stacking):
                    
                    path = f"{home}/M{n+1}X{n}/{mx}/{stack}/"
                    paths.append(path)
                    data.append([mx,stack]) # data.append([mx,stack,""])

    # For Terminated cases
    else:
        for mx,mxt in zip(MX,MXT):
            for j,stack in enumerate(stacking):
                for k,hollow in enumerate(hollows[j]):

                    path = f"{home}/M{n+1}X{n}/{mx}/{mxt}/{stack}/{hollow}/"
                    paths.append(path)
                    data.append([mxt,stack,hollow])


    return paths, data


def search(target:str,n:int,T:str):

    if T == "" or T == None: pristine = True
    else: pristine = False

    if pristine: paths = path_tree(n,None)
    else: paths = path_tree(n,T)

    if target.lower().startswith("dos") and not target.endswith("0"): extras = ["DOS/DOSCAR"]
    elif target.lower().startswith("dos") and target.endswith("0"): extras = ["DOS/PBE0/DOSCAR"]
    elif target.lower().startswith("cont"): extras = ["CONTCAR"]
    elif target.lower().startswith("loc"): extras = ["WF/LOCPOT"]
    elif target.lower().startswith("bader"): extras = ["bader/ACF.dat"]

    for path in paths:
        for extra in extras:
            pass

    pass

