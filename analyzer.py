"""
Searches DOSCARs in the directory tree, calculates DOS and returns plots.
For a specified n, T, and target (DOSCAR for PBE or DOSCAR0 for PBE0), searches DOSCAR
and creates plot, which is saves in its respective stack_hollow/ folder in the home dir.

Diego Ontiveros
"""

import os
from argparse import ArgumentParser

# os.environ['OPENBLAS_NUM_THREADS'] = '1'
from searcher import SEARCH, getStructure, parseTermination, mx_folders,mxt_folders
from DOS import DOSCAR
from LOCPOT import WF


def analyzeDOS(paths):
    """Analyzes the DOSCAR of the path tree for the given n and T.\n 
    Makes a plot in the correspondent /home folder, and returns bandgap information: Eg, VBM and CBM."""

    for path in paths:
        dos = DOSCAR(path)
        stack,hollows,pristine = getStructure(path)
        # if stack=="ABA":continue
        # Select out folder
        if pristine: out_folder = stack+"/"
        else: out_folder = stack+"_"+hollows+"/"

        print(f"{stack} {hollows} ",end='',flush=True)
        dos.plot(
            ["M","red"],["X","blue"],["Term","green"],["Term2","fuchsia"],
            spc = False,
            out_path = out_folder
        )

        continue
        print(f"{stack} {hollows} ",end='',flush=True)
        # Plots spin contributions (if spin polarized)
        if dos.spin=="sp":
            dos.plot(
                ["Ma","orange"], ["Mb","cyan"],["Xa","pink"],["Xb","violet"], 
                ["Terma","yellow"],["Termb","grey"],["Term2a","fuchsia"],["Term2b","coral"],
                spc = True,
                out_path = out_folder
            )


def analyzeWF(paths,limit=None): 
    """Analyzed the LOCPOT file for all the given paths. 
    Makes a plot in the respective home folder and returns LOCPOT information: vaccuum potential for each surface."""

    for path in paths:
        stack,hollows,pristine = getStructure(path)
        # if stack=="ABA":continue

        # Select out folder
        if pristine: out_folder = stack+"/"
        else: out_folder = stack+"_"+hollows+"/"
        print(f"{stack} {hollows} ",end='',flush=True)

        wf = WF(path)
        wf.calculate(tol_janus=10)
        wf.plot(name=out_folder+f"{wf.file}_{wf.mx.name}.png")


############################# MAIN PROGRAM ####################################

home = os.path.abspath("..")
searcher = SEARCH()

# Parsing user arguments
parser = ArgumentParser(description="Calls the visualization scripts (DOS and LOCPOT) to make plots and return bandgap or Vvsurf for the specified n and T. \
                        Or for a given file of paths.",
    usage= "\n\
        General:        analyzer.py [-h] [-n N_INDEX] [-T TERMINATION] [-f FILE] [-DOS] [-WF]\n\
        DOS analysis:   analyzer.py -DOS[0] [-n N_INDEX] [-T TERMINATION] [-f FILE] \n\
        WF analysis:    analyzer.py -WF [-n N_INDEX] [-T TERMINATION] [-f FILE]")
parser.add_argument("-n","--n_index",type=int,help="MXene n index (int) from the formula Mn+1XnT2.")
parser.add_argument("-T","--termination",type=str,default="",help="MXene termination (str) from the formula Mn+1XnT2. Specifyit with the index, i.e 'O2'. \
                    For pristine MXenes, don't use this or use None. Defaults to None.")
parser.add_argument("-f","--file",type=str,help="Read the paths to do analysis from a specified file.")
parser.add_argument("-DOS","--DOS",action="store_true",help="To analyze DOSCAR (PBE) files (from paths in file or for the given -n and -T).")
parser.add_argument("-DOS0","--DOS0",action="store_true",help="To analyze DOSCAR (PBE0) files (from paths in file or for the given -n and -T).")
parser.add_argument("-WF","--WF",action="store_true",help="To analyze LOCPOT files (from paths in file or for the given -n and -T).")

args = parser.parse_args()
n,T = args.n_index, args.termination # limit?
file,calc_dos,calc_dos0,calc_wf = args.file,args.DOS,args.DOS0,args.WF
if T == "None": T = ""
T, pristine = parseTermination(T)
if file is None and n is None: parser.error(f"Some arguments are needed. Choose -file or -n. For help, run python3 calculate.py -h.")
elif not calc_dos and not calc_wf: parser.error(f"Analysis flag needed. Choose -DOS or -WF. For help, run python3 calculate.py -h.")


# Creating folders
path_folders = f"{home}/searcher_dos{n}/"
file_path = os.path.abspath(file)

try: os.mkdir(path_folders)
except FileExistsError: pass
os.chdir(path_folders)


# All possible combinations
if file is None:

    if pristine: folders = mx_folders
    else: folders = mxt_folders
    for folder in folders:
        try: os.mkdir(folder)
        except FileExistsError: pass
    
    if calc_dos: 
        target = "DOSCAR"
        paths = searcher.search(target,n,T)
        analyzeDOS(paths)

    elif calc_dos0: 
        target = "DOSCAR0"
        paths = searcher.search(target,n,T)
        analyzeDOS(paths)

    elif calc_wf: 
        target = "LOCPOT"
        paths = searcher.search(target,n,T)
        analyzeWF(paths)

else:
    # if pristine: folders = mx_folders
    # else: folders = mxt_folders
    folders = mxt_folders
    for folder in folders:
        try: os.mkdir(folder)
        except FileExistsError: pass

    with open(file_path,"r") as inFile: 
        paths = inFile.readlines()
        # procesing of file here
        # for i,line in enumerate(paths): paths[i] = line.strip().split()[0] + "WF/LOCPOT"

    if calc_dos or calc_dos0: analyzeDOS(paths)
    elif calc_wf: analyzeWF(paths)