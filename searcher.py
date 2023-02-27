"""
General path searcher for the cluster folders. It searches in a tree-style
structure such as the one given by VASP.py file generator.

Diego Ontiveros
"""

import os

home = os.path.expanduser("~")

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
    
    if target.lower().startswith("dos") and not target.endswith("0"): extras = ["DOS/DOSCAR"]
    elif target.lower().startswith("dos") and target.endswith("0"): extras = ["DOS/PBE0/DOSCAR"]
    elif target.lower().startswith("cont"): extras = ["CONTCAR"]
    elif target.lower().startswith("loc"): extras = ["WF/LOCPOT"]
    elif target.lower().startswith("bader"): extras = ["bader/ACF.dat"]

    return extras

class SEARCH():

    def __init__(self) -> None:
        """    
        General Searcher class that allows to find files and move them in a path three
        similar to the one generated with VASP.py.

        """
        self.n = None
        self.T = None
        self.pristine = None
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
                        data.append([mx,stack]) # data.append([mx,stack,""])

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

        self.target = target
        T, pristine = parseTermination(T)

        paths, data = self.path_tree(n,T)

        extras = parseTarget(target)

        counter = 0
        search_paths = []
        for path in paths:
            if os.path.exists(path): 
                counter += 1
                search_paths.append(path + extras)
            else: print(f"{path} : Path not found.")
        print(f"Found {counter} files from the total {len(paths)}")

        self.search_paths = search_paths
        return paths

    def move(self,destination:str,n:int=None,T:str=None,name:str=None):

        search_paths = self.search_paths
        if name is None: name = self.target

        
        if destination.lower().startswith("home"):
        
            pass
        if destination.lower().startswith("mx"):pass

        # for folder in new_folders:
        #   try: os.mkdir(folder)
        #   except FileExistsError: pass

        # for path in move_paths:pass
            ## asegurarse que sean el mismo MX


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