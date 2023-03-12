"""
Searches DOSCARs in the directory tree, calculates DOS and returns plots.

Diego Ontiveros
"""

import os

from searcher import SEARCH, getStructure, parseTermination, mx_folders,mxt_folders
from DOS import DOSCAR


home = ".."
searcher = SEARCH()
target = "DOSCAR"
T = ""

T, pristine = parseTermination(T)



for n in [2,3]:

    # Creating folders
    path_folders = f"{home}/searcher_dos{n}/"
    
    try: os.mkdir(path_folders)
    except FileExistsError: pass
    os.chdir(path_folders)

    if pristine: folders = mx_folders
    else: folders = mxt_folders
    for folder in folders:
        try: os.mkdir(folder)
        except FileExistsError: pass


    paths,data = searcher.search("DOSCAR",n=n,T=T)

    for path in paths:
        dos = DOSCAR(path)
        stack,hollows = getStructure(path)

        # Select out folder
        if pristine: out_folder = stack+"/"
        else: out_folder = stack+"_"+hollows+"/"

        dos.plot(
            ["M","red"],["X","blue"],["Term","green"],
            spc = False,
            out_path = out_folder
        )

        # Plots spin contributions (if spin polarized)
        if dos.spin=="sp":
            dos.plot(
                ["Ma","orange"], ["Mb","cyan"],["Xa","pink"],["Xb","violet"], 
                ["Terma","yellow"],["Termb","grey"],
                spc = True,
                out_path = out_folder
            )
