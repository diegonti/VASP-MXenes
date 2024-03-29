"""
General path searcher for the cluster folders. It searches in a tree-style
structure such as the one given by VASP.py file generator.

Diego Ontiveros
"""

import os
import shutil

from structure import CONTCAR
from VASP import MX


dirsMXT = ["DOS/","DOS/PBE0/","BS/PBE/","BS/PBE0/","BS/PBE/BS2/","BS/PBE0/BS2/","WF/"]
dirsMX = ["DOS/","DOS/PBE0/","BS/"]

def parseTermination(T):
    """Parses the Termination user input. Decides if its Pristine or Terminated"""
    if T == "" or T == None: 
        T = ""
        pristine = True
    else: pristine = False
    return T, pristine

def parseTarget(target:str):
    """Parses the target input to search and decides extensions to search."""
    
    if target.lower().startswith("dos") and not target.endswith("0"): extras = "DOS/DOSCAR"
    elif target.lower().startswith("dos") and target.endswith("0"): extras = "DOS/PBE0/DOSCAR"
    elif target.lower().startswith("cont"): extras = "CONTCAR"
    elif target.lower().startswith("loc"): extras = "WF/LOCPOT"
    elif target.lower().startswith("opt"): extras = "opt/"
    elif target.lower().startswith("wf"): extras = "WF/"
    elif target.lower().startswith("bader"): extras = "bader/ACF.dat"
    else: extras = target

    return extras

def getStructure(path):
    """Gets structure (stacking and hollows) from the folder path."""

    data = path.strip().split("/")

    # n
    if "M2X1" in data: idx = data.index("M2X1")
    elif "M3X2" in data: idx = data.index("M3X2")
    elif "M4X3" in data: idx = data.index("M4X3")
    else: raise ValueError("Could not resolve path")
    mx = MX(data[idx+2])

    # Stacking
    if "/ABA/" in path: stack = "ABA"; stack_i = 1
    elif "/ABC/" in path: stack = "ABC"; stack_i = 0

    # Hollows
    hollows = ""
    h = ["/HM/","/HMX/","/HX/","/H/"]
    h_i = [1,2,3,1]
    for hollow,hollow_i in zip(h,h_i): 
        if hollow in path: 
            hollows = hollow.split("/")[1]
            hollows_i = hollow_i

    if hollow == "": 
        pristine = True
        hollows_i = ""
    else: pristine = False

    queue_name = f"{mx.name}_{stack_i}{hollows_i}"

    return stack, hollows, pristine, queue_name

def pathMX(n,mx,mxt,stack,hollow):
    return f"{home}/M{n+1}X{n}/{mx}/{mxt}/{stack}/{hollow}/"


class SEARCH():

    def __init__(self) -> None:
        """    
        General Searcher class that allows to find files and move them in a path three
        similar to the one generated with VASP.py.

        """
        self.n = None
        self.T = None
        self.pristine = None
        self.search_data = None
        self.search_paths = None
        self.target = None

        self.M = ["Cr","Hf","Mo","Nb","Sc","Ta","Ti","V","W","Y","Zr"]
        self.stacking = ["ABC","ABA"]
        hABC = ["HM","HMX","HX"]
        hABA = ["H","HMX","HX"]
        self.hollows = [hABC,hABA]
        


    def path_tree(self,n:int,T:str=None):
        """Returns a list of all paths for a n and T case.

        Parameters
        ----------
        `n` : MXene index.
        `T` : Termination. '' or None indicate pristine MXenes. 'T2' for terminated.

        Returns
        ----------
        `paths` : List of paths.
        `data`  : extra info of the MXene. (name, stacking, hollows).
        """
        T, pristine = parseTermination(T)
        
        # MXene cases
        M = self.M
        mc = [m + str(n+1) + "C" + str(n) for m in M]   # X = C cases
        mn = [m + str(n+1) + "N" + str(n) for m in M]   # X = N cases
        MX = mc + mn                                    # All studied MXenes (pristine)
        MXT = [i + T for i in MX if i != ""]            # All studied MXenes (terminated)

        # Structure cases
        stacking = self.stacking
        hollows = self.hollows

        paths, data = [], []

        # For Pristine cases
        if pristine:
            for mx in MX:
                for j,stack in enumerate(stacking):
                        
                        path = f"{home}/M{n+1}X{n}/{mx}/{stack}/"
                        paths.append(path)
                        data.append([mx,stack,""]) # data.append([mx,stack,""])

        # For Terminated cases
        else:
            for mx,mxt in zip(MX,MXT):
                for j,stack in enumerate(stacking):
                    for k,hollow in enumerate(hollows[j]):

                        path = f"{home}/M{n+1}X{n}/{mx}/{mxt}/{stack}/{hollow}/"
                        paths.append(path)
                        data.append([mxt,stack,hollow])

        self.paths = paths
        return paths, data


    def search(self,target:str,n:int,T:str=None):
        """Searches target into the tree of folders for a given n and T.

        Parameters
        ----------
        `target` : Target descriptor of the file. (dos, dos0, locpot, WF/, opt/)
        `n` : MXene index (Mn+1XnT2)
        `T` : Optional. MXene termination. By default None.

        Returns
        -------
        `search_paths` : List of the searched and found paths.
        `search_data` : List with the data ([mxt,stack,hollow])

        """

        T, pristine = parseTermination(T)
        self.n, self.T = n,T

        paths, data = self.path_tree(n,T)

        extras = parseTarget(target)
        self.target = extras.split("/")[-1]

        counter = 0
        search_paths, search_data = [], []
        for i,path in enumerate(paths):
            target_path = path+extras
            if os.path.exists(target_path): 
                counter += 1
                search_paths.append(target_path)
                search_data.append(data[i])
            else: print(f"{target_path} : Path not found.")
        print(f"Searched n = {n} T = {T}: Found {counter} files from the total {len(paths)}.")

        self.search_paths = search_paths
        self.search_data = search_data
        return search_paths, search_data 


    def move(self,destination:str,n:int,T:str=None,action="addT",name:str=None):
        """Moves targeted files to the specified destination, for a given batch of n and T MXenes.

        Parameters
        ----------
        `destination` : Type of file movement. 'mx>mxt' using pristine CONTCARS to the correspondent initial POSCARs for terminated cases.
        `n` : MXene index (Mn+1XnT2)
        `T` : Optional. MXene termination. By default None.
        `action` : Action to do when moving, 'addT' for adding a termination to the pristine CONTCAR. By default "addT".
        `name` : Name of the pasted file. By default takes the name of the target.
        """

        search_paths,data = self.search_paths,self.search_data

        T, pristine = parseTermination(T)
        if name is None: name = self.target

        # Options: mx>mxt // contcar>calculate
        if destination.lower().startswith("home"): self.moveHome()

        elif destination.lower().startswith("mx>mxt"):

            # destination_paths,data = self.path_tree(n,T)

            for s_path,s_data in zip(search_paths,data):
                # for hollow and stacking
                mx,stack,hollow = s_data 

                for h in self.hollows[self.stacking.index(stack)]:
                    destination_path = f"{home}/M{n+1}X{n}/{mx}/{mx+T}/{stack}/{h}/"
                    # path exists como en search?
                    if os.path.exists(destination_path):
                        if action=="addT":
                            contcar = CONTCAR(s_path)
                            contcar.addT(T,stack,h)
                            # contcar.addT(T2,stack,h)
                            contcar.write(destination_path+name)
                        else: shutil.copy(s_path,destination_path+name)
                    else: print(f"{destination_path} : Path not found.")


    def moveHome(self,path_folders:str=None,name:str=None,is_folder:bool=False):
        """Moves all the targeted files to their correspondent (stach_hollow/) folder in the hom/searcher_n dir created."""
        n = self.n
        T, pristine = parseTermination(self.T)
        if name is None: name = self.target
        search_paths = self.search_paths
        search_data = self.search_data

        if path_folders is None: path_folders = f"{home}/searcher_{n}_{'p' if pristine else T}/"

        # Creating folders
        try: os.mkdir(path_folders)
        except FileExistsError: pass
        os.chdir(path_folders)

        if pristine: folders = mx_folders
        else: folders = mxt_folders
        for folder in folders:
            try: os.mkdir(folder)
            except FileExistsError: pass

        for path,data in zip(search_paths, search_data):

            # Select out folder
            if pristine: out_folder = data[1]+"/"
            else: out_folder = data[1]+"_"+data[2]+"/"

            # copy from search path to destination
            if not is_folder: shutil.copy(path,f"{out_folder}/{name}_{data[0]}")
            else: os.system(f"cp -r {path} {out_folder}/{data[0]}")

    def remove(self, target:str):
        """Removes the specified files for the searched paths and subfolders."""
        search_paths,data = self.search_paths,self.search_data
        for s_path in search_paths:
            try:
                os.chdir(s_path)
                os.system(f"find . -name '{target}' -type f -delete")
                # os.chdir(original_path)
            except FileNotFoundError: print(f"{s_path} : Path not found.")

    def action(self, target:str):
        """General action to do in the searched paths."""
        search_paths,data = self.search_paths,self.search_data
        for s_path in search_paths:
            try:
                os.chdir(s_path)
                os.system(f"{target}")
                # os.chdir(original_path)
            except FileNotFoundError: print(f"{s_path} : Path not found.")
            

############################### MAIN PROGRAM ###############################

mxt_folders = ["ABC_HM","ABC_HMX","ABC_HX","ABA_H","ABA_HMX","ABA_HX"]
mx_folders = ["ABC","ABA"]
home = os.path.abspath("..")

if __name__ == "__main__":
    
    searcher = SEARCH()

    searcher.search(target="CONTCAR",n=1,T="")

    # searcher.search(target="CONTCAR",n=1,T="")
    # searcher.move(destination="mx>mxt",n=1,T="O2",name="opt/POSCAR")
    
    # searcher.moveHome()

    # searcher.remove("CHG*")