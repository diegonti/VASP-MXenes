"""
VASP file manager to generate input files for different calculations.
This is centered in MXene compounds (Mn+1XnTx). The script creates a tree of folders
for each MXene (MX (pristine) -> MX (terminated) -> stacking -> hollows -> calculations (opt, DOS, BS, WF)).
The script contains the general MX() class, which by only givin the MXene formula, 
different attributes are gathered.

Diego Ontiveros 
"""

import os
import shutil
import math as m


def mkdir(*dirs):
    """Creates especified directories. Cleaner way."""
    for dir in dirs:
        try: os.mkdir(dir)
        except FileExistsError: pass


def splitNums(string):
    """For a string with letters and numbers, returns a list with characters and numbers separated, 
    in the order as they appear. Ti2C1O2 --> [Ti,2,C,1,O,2]"""

    previous_character = string[0]
    groups = []                         
    newword = string[0] 
    for x, i in enumerate(string[1:]):   # Creates iterable with each index, string pair ((1,s1),(2,s2),...)
        
        # If the current and previous character are the same, it is added to the new word
        if i.isalpha() and previous_character.isalpha(): newword += i
        elif i.isnumeric() and previous_character.isnumeric(): newword += i
        # Else, the newword is added to groups and a new one is started
        else:
            if newword.isdigit(): groups.append(int(newword))
            else: groups.append(newword)
            newword = i

        previous_character = i

        # For the last characters
        if x == len(string) - 2:
            if newword.isdigit(): groups.append(int(newword))
            else: groups.append(newword)
            newword = ''

    return groups


class MX():
    
    #Que pseudopotenciales utilizar para cada metal (nombre carpeta) (si no, cojera el normal)
    pp = ['Sc_sv', 'Ti_pv', 'V_pv', 'Cr_pv', 'Y_sv', 'Zr_sv', 'Nb_pv', 'Mo_pv', 'Hf_pv', 'Ta_pv', 'W_pv']

    def __init__(self, name,stacking="ABC",hollows="HM"):

        self.name = name                        # MXene name "M2X1T2"
        self.mxName = self.name.replace("1","") # "Formal" MXene name (without 1)
        
        self.cparts = splitNums(self.name)                          # [M,n+1,X,n,T,x] 
        self.atoms = [a for a in self.cparts if type(a) == str]     # [M,X,T]        
        self.index = [j for j in self.cparts if type(j) == int]     # [n+1,n,x]
        

        # Establishes if the MXene has termination
        if len(self.atoms) >= 3 and len(self.index) >= 3:
            self.terminal = True
            self.pristine = "".join([str(p) for p in self.cparts[:4]])
        else: 
            self.terminal = False
            self.pristine = self.name
        
        # Establishes if the MXene is OH terminated (special treatment)
        if len(self.atoms)>3: self.T_AB = True
        else: self.T_AB = False

        # self.T_ABC

        # MXene structure
        self.stacking = stacking    # Stacking
        self.hollows = hollows      # T hollow position
        self.n = self.index[0] - 1  # Width, n (1,2,3)
        self.do = 2.5               # Initial distance of each MXene sheet (not total)
        self.v = 30                 # Vacuum distabce
        self.ab = 3                 # Lattice parameter multiplyer
        self.lp = 1

        # INPUT FILES DIRECTORIES
        if self.terminal: 
            self.shift = 1
            self.pdir = f"./MXenes/{self.pristine}/{self.name}/{self.stacking}/{self.hollows}/" 
        else: 
            self.shift = 0
            self.pdir = f"./MXenes/{self.pristine}/{self.stacking}/"     

        if self.terminal:
            dirs_terminated = ["opt","DOS","DOS/PBE0", "BS","BS/PBE","BS/PBE0","BS/PBE/BS2","BS/PBE0/BS2",
                        "WF"]
            # dirs_terminated = ["DOS","DOS/PBE0"]
            self.dirs = [self.pdir + i +"/" for i in dirs_terminated]
            self.extra_dirs = ["bader"]
        else:
            dirs_pristine = ["opt","DOS", "DOS/PBE0", "BS"]
            self.dirs = [self.pdir + i +"/" for i in dirs_pristine]



    def positions(self): #n=1, do=2.5, v=10, shift=0
        """Returns the direct coordinates of a MXene for a given n and structure."""
        
        # Structure parameters
        n = self.n
        do,v = self.do, self.v
        shift = self.shift
        stacking = self.stacking
        hollows = self.hollows
        
        f = ".16f" # Number of decimals
        
        # Values that each atom x (a) and y (b) coordinates take
        if stacking == "ABC":
            a = [1,3,2]
            b = [2,0,1]
        elif stacking == "ABA":
            a = [1,0]
            b = [2,0]
        den = n*do+v+2*shift

        j = 0                                 # Iterates over the a and b values
        M, X, T = [], [], []                  # Where positions will go for each atom type
        zero = [0,0,0+shift/(n*do+v+2*shift)] # Stablishing the reference point
        zero = [format(i,f) for i in zero]    # Formatting
        M.append(zero)                        # The first metal atom

        for i in range(n): # For each layer

            if stacking == "ABA": j = 0

            # Metal coordinates (M) 
            aM = format(round(a[j-1]/3,16),f)
            bM = format(round(b[j-1]/3,16),f)
            cM = format(round((do*(i+1) + shift)/(n*do + v + 2*shift), 16),f)
            posM = [aM,bM,cM]
            M.append(posM)

            # C or N coordinates (X)
            aX = format(round(a[j]/3,16),f)
            bX = format(round(b[j]/3,16),f)
            cX = format(round((do/2*(2*(i+1)-1) + shift)/(n*do + v + 2*shift), 16),f)
            posX = [aX,bX,cX]
            X.append(posX)         

            j += 1
            if j == 3: j = 0

        if self.terminal:
            aH = format(round(2/3,16),f)
            bH = format(round(1/3,16),f)

            if hollows == "HM":
                a = [M[1][0], M[-2][0]] 
                b = [M[1][1], M[-2][1]]
            if hollows == "H":
                a = [aH, aH] 
                b = [bH, bH]
            if hollows == "HX": 
                a = [X[0][0], X[-1][0]] 
                b = [X[0][1], X[-1][1]]
            if hollows == "HMX" and stacking == "ABC": 
                a = [X[0][0], M[-2][0]] 
                b = [X[0][1], M[-2][1]]
            if hollows == "HMX" and stacking == "ABA": 
                a = [X[0][0], aH]
                b = [X[0][1], bH]


            # Termination coordinates (T) 
            for i in range(2):

                aT = a[i] #format(round(a[i],16),f)
                bT = b[i] #format(round(b[i],16),f)
                cT = format(round(i*(n*do+2*shift)/(n*do+v+2*shift),16),f)
                posT = [aT,bT,cT]
                T.append(posT)
            
        return M, X, T        

    def POSCAR(self):
        """Creates initial POSCAR file for MXene. From its atoms and n.\n
        Contains name, cell parameters and atom positions. By default ab=3 do=2.5 v=30 lp=1.\n
        The values can be changed with the MX() object arguments. (or as args in this function --> implement)\n
        """

        n = self.n
        do,v = self.do,self.v
        ab = self.ab
        lp = self.lp
        shift = self.shift

        f1 = ".10f"
        
        # Cell parameter calculation
        lp = format(lp,".14f")
        a = [format(ab,f1), format(0,f1), format(0,f1)]                                                     # (ab,0,0)
        b = [format(round(-ab*m.sin(m.pi/6),10),f1), format(round(ab*m.cos(m.pi/6),10)), format(0,f1)]      # (-ab*sin(30),ab*cos(30),0)
        c = [format(0,f1), format(0,f1), format(n*do+2*shift+v,f1)]                                         # (0,0,n*do+v)

        # Atom labels and indices lines
        strAtoms = " ".join([a for a in self.atoms])
        strIndex = " ".join([str(i) for i in self.index])
        
        # Atom positions lines
        p = ""
        posM, posX, posT = self.positions()
        for pos in posM: p += f"  {pos[0]}  {pos[1]}  {pos[2]}  T T T\n"
        for pos in posX: p += f"  {pos[0]}  {pos[1]}  {pos[2]}  T T T\n"
        if self.terminal:
            for pos in posT: p += f"  {pos[0]}  {pos[1]}  {pos[2]}  T T T\n"

        # Writes POSCAR with the usual format in the specified directories
        for dir in self.dirs:
            if not dir.endswith("opt/"): continue
            with open(dir + "POSCAR", 'w') as outfile:
                outfile.write(
                    f"{self.mxName} (n={n})\n"
                    f"   {lp}\n"
                    f"     {a[0]}   {a[1]}   {a[2]}\n"
                    f"    {b[0]}   {b[1]}   {b[2]}\n"
                    f"     {c[0]}   {c[1]}  {c[2]}\n"
                    f"  {strAtoms}\n"
                    f"  {strIndex}\n"
                    "Selective Dynamics\n"
                    "Direct\n"
                    f"{p}"
                )
  
    def POTCAR(self):
        """Creates POTCAR file with the concatenated PP of the MXene atoms."""

        with open(self.pdir + "POTCAR", 'w') as outfile:
                    first = True
                    for at in self.atoms:
                        
                        for p in self.pp: #para cojer el pp adecuado
                            if self.atoms[0] in p and first: #Si es la primera vez y el atomo esta en la lista pp
                                file = p
                                first = False
                                break
                            else: file = at #sino coje el normal

                        with open("./PP/{}/POTCAR".format(file), "r") as infile:
                            for line in infile: outfile.write(line)

        # Copies file to all input directories
        source = self.pdir + "POTCAR"
        for dir in self.dirs: shutil.copy(source,dir)
        
    def KPOINTS(self,p1=7,p2=7,p3=1):
        """Creates KPOINT file with the specified k-points (mesh).\n
        By default:  7  7  1."""

        with open(self.pdir + "KPOINTS", 'w') as outfile:
            with open("./car/KPOINTS", 'r') as infile:
                n = 1
                for line in infile:
                    if n == 4: line = f" {p1}  {p2}  {p3}\n"
                    outfile.write(line)
                    n += 1
        
        # Copies file to all input directories
        source = self.pdir + "KPOINTS"
        source2 = "./car/KPOINTS3"
        for dir in self.dirs:
            if dir.endswith("BS2/"): shutil.copy(source2,dir+"KPOINTS") # For band structure calculations
            else: shutil.copy(source,dir)                               # For other calculations

    def INCAR(self,**kwargs):
        """ Creates INCAR file for a calculation.\n
        Adapts itself to the path of the directory its in.\n
        Accepts keyword parameters with style: param = value."""

        # params = [key for key in kwargs.keys()] #Parámetro
        # values = [val for val in kwargs.values()] #Valor de parámetro
        
        for dir in self.dirs: #que parametros pone en el incar segun el cálculo
            params,values = [],[]
            if "opt" in dir and dir.endswith("opt/"):
                params.append("ISIF"); values.append("4")
            if "isif7" in dir and not "isif2" in dir:
                params.append("ISIF"); values.append("7")
                params.append("NSW"); values.append("19")
            if "isif2" in dir:
                params.append("ISIF"); values.append("2")
            
            if "DOS" in dir or "BS" in dir or "WF" in dir:
                params.append("IBRION"); values.append("-1")
                params.append("NSW"); values.append("0")
            if "DOS" in dir or "WF" in dir: 
                params.append("ISMEAR"); values.append("-5")
                params.append("LORBIT"); values.append("11")
                params.append("EMIN"); values.append("-10")
                params.append("EMAX"); values.append("10")
                params.append("NEDOS"); values.append("9999")
            if "BS1" in dir or "BS/PBE" in dir: pass
            if "BS2" in dir: 
                params.append("ICHARG"); values.append("11")
                params.append("LORBIT"); values.append("11")
            if "PBE0" in dir or "WF" in dir: 
                params.append("IALGO"); values.append("58")
                params.append("LHFCALC"); values.append(".TRUE.")
            if "WF" in dir:
                params.append("LVTOT"); values.append(".TRUE.")
                params.append("LDIPOL"); values.append(".TRUE.")
                params.append("IDIPOL"); values.append("3")
                params.append("NGXF"); values.append("100")
                params.append("NGYF"); values.append("100")
                params.append("NGZF"); values.append("700")                

            with open(dir + "INCAR",'w') as outfile:
                with open("./car/INCAR", 'r') as infile:
                    for line in infile:
                        for p in params:
                            if p in line:
                                line = f"{p}  =  {values[params.index(p)]}\n"
                                values.pop(params.index(p))
                                params.remove(p)
                                break
                        outfile.write(line)
                    for p in params:
                        line = f"{p}  =  {values[params.index(p)]}\n"
                        outfile.write(line)
                    outfile.write(f"SYSTEM = {self.name}")
    
    def script(self,cluster="iqtc"):
        """Creates a copy of the script file in each directory."""

        if cluster.lower() == "iqtc": source = "./car/scriptIQTC"
        elif cluster.lower() == "bsc": source = "./car/scriptBSC"

        destination1 = self.pdir
        shutil.copy(source, destination1+"script")
        for dir in self.dirs:
            shutil.copy(source,dir+"script")

    def bader(self):
        """Copies the bader script to the bader/ directory"""

        source = "./car/bader"
        destination = None
        shutil.copy(source,destination)


def createDirs(mx:MX):
        try: os.mkdir(f"MXenes/{mx.pristine}/")
        except FileExistsError: pass

        if not mx.terminal: mkdir(f"MXenes/{mx.pristine}/{mx.stacking}/")
        elif mx.terminal: mkdir(
            f"MXenes/{mx.pristine}/{mx.name}/",
            f"MXenes/{mx.pristine}/{mx.name}/{mx.stacking}/",
            f"MXenes/{mx.pristine}/{mx.name}/{mx.stacking}/{mx.hollows}/")
        mkdir(*mx.dirs)
### ----------------------------------------- INICIO PROGRAMA ---------------------------------------------------- ###
###--------------------------------------------------------------------------------------------------------------- ###

# INPUTS
n = 3                               # MXene n number (thickness)
T = "O2H2"                          # Termination ((OH)2==O2H2)

# stacking, hollow = "ABC", "HM"     # Structure

M = ["Sc","Y","Ti","Zr","Hf","V","Nb","Ta","Cr","Mo","W"]

mc = [m + str(n+1) + "C" + str(n) for m in M]   # X = C cases
mn = [m + str(n+1) + "N" + str(n) for m in M]   # X = N cases
mx = mc + mn                                    # All studied MXenes (pristine)
mxt = [i + T for i in mx if i != ""]             # All studied MXenes (temrinated)
lenMX = len(mxt)

stackings = ["ABC","ABA"]
hollows = [["HM","HMX","HX"],["H","HMX","HX"]]


if __name__ == "__main__":

    # Creates /MXene folder
    cwd = os.getcwd()
    try: os.mkdir("MXenes") ###! Change to variable
    except FileExistsError: pass

    for i,stack in enumerate(stackings):
        for hollow in hollows[i]:

            MXenes = [MX(mxt[j],stack,hollow) for j in range(lenMX)]

            # Generates input files for each MXene in list
            for mx in MXenes:

                # Creates dirs-subdirs
                createDirs(mx)

                #Cambios de los parámetros de mx han de ser aqui!

                mx.POSCAR()         # Writes POSCAR (positions)
                mx.POTCAR()         # Writes POTCAR (concatenated PP)    
                mx.KPOINTS()        # Writes KPOINTS (k-mesh or k-path)
                mx.INCAR()          # Writes INCAR (for each calculations)
                mx.script("bsc")    # Writes script (to send calculation)
