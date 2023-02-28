"""
General path searcher for the cluster folders. It searches in a tree-style
structure such as the one given by VASP.py file generator.

Diego Ontiveros
"""

import os
import shutil

home = os.path.expanduser("~")
os.chdir(home)

dirsMXT = ["DOS/","DOS/PBE0/","BS/PBE/","BS/PBE0/","BS/PBE/BS2/","BS/PBE0/BS2/","WF/"]
dirsMXT = ["DOS/","DOS/PBE0/","BS/"]

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
    elif target.lower().startswith("bader"): extras = "bader/ACF.dat"

    return extras

# def selectOut(path,pristine):
#     if pristine:
#         if "ABA" in
#         pass
#     else:
#         pass

#     return out_folder

class SEARCH():

    def __init__(self) -> None:
        """    
        General Searcher class that allows to find files and move them in a path three
        similar to the one generated with VASP.py.

        """
        self.n = None
        self.T = None
        self.pristine = None
        self.data = None
        self.search_paths = None
        self.target = None

        self.M = ["Cr","Hf","Mo","Nb","Sc","Ta","Ti","V","W","Y","Zr"]
        self.stacking = ["ABC","ABA"]
        hABA = ["H","HMX","HX"]
        hABC = ["HM","HMX","HX"]
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

        T, pristine = parseTermination(T)
        self.n, self.T = n,T

        paths, data = self.path_tree(n,T)

        extras = parseTarget(target)
        self.target = extras.split("/")[-1]

        counter = 0
        search_paths, search_data = [], []
        for i,path in enumerate(paths):
            if os.path.exists(path): 
                counter += 1
                search_paths.append(path + extras)
                search_data.append(data[i])
            else: print(f"{path} : Path not found.")
        print(f"Searched n = {n} T = {T}: Found {counter} files from the total {len(paths)}.")

        self.search_paths = search_paths
        self.search_data = search_data
        return paths, search_data 

    def move(self,destination:str,n:int,T:str=None,name:str=None):

        search_paths = self.search_paths
        T, pristine = parseTermination(T)
        if name is None: name = self.target

        
        if destination.lower().startswith("home"): self.moveHome()

        if destination.lower().startswith("mx"):
            destination_paths,data = self.path_tree(n,T)

        # for folder in new_folders:
        #   try: os.mkdir(folder)
        #   except FileExistsError: pass

        # for path in move_paths:pass
            ## asegurarse que sean el mismo MX

    def moveHome(self,path_folders:str=None,name:str=None):
        n = self.n
        T, pristine = parseTermination(self.T)
        if name is None: name = self.target
        search_paths = self.search_paths
        search_data = self.search_data

        if path_folders is None: path_folders = f"{home}/searcher/"

        try: os.mkdir(path_folders)
        except FileExistsError: pass
        os.chdir(path_folders)

        # Creating folders
        if pristine: folders = mx_folders
        else: folders = mxt_folders
        for folder in folders:
            try: os.mkdir(folder)
            except FileExistsError: pass

        for path,data in zip(search_paths, search_data):

            # Selct out folder
            if pristine: out_folder = data[1]+" "+data[2]+"/"
            else: out_folder = data[1]+" "+data[2]+"/"

            # copy from search path to destination
            shutil.copy(path,f"{out_folder}/{name}_{data[0]}")
            


############################### MAIN PROGRAM ###############################

mxt_folders = ["ABC HM","ABC HMX","ABC HX","ABA H","ABA HMX","ABA HX"]
mx_folders = ["ABC","ABA"]

if __name__ == "__main__":
    
    # new_folders = mx_folders
    # for f in new_folders:
    #     try: os.mkdir(f)
    #     except FileExistsError: pass

    paths,data = SEARCH().path_tree(2,"O2")
    print(paths)