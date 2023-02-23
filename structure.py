"""
Module for modifying CONTCARS and extracting the information in an automatic way.
This program works for VASP CONTCAR output files.

Diego Ontiveros
"""

from VASP import MX
import warnings
import os

def test_data(data):
    print()
    for line in data:
        print(line)

class CONTCAR():
    def __init__(self,path:str) -> None:
        """Creates a contcar object with the information of the given CONTCAR file.
        Allows to modify its geometry with different functions and get parameters.
        Optimized for MXene compounds.

        `path` : path for the CONTCAR file
        """

        self.path = path
        self.filename = path.split("/")[-1]

        self.data,self.atoms,self.index,self.name = self.getData(self.path)
        self.nAtoms = sum(self.index)
        self.mx = MX(self.name)

        

    def getData(self,path):
        """Reads the data from a CONTCAR file and sets the initial attributes."""

        with open(path,"r") as inFile:
            data = inFile.readlines()
            data = [line.strip().split() for line in data]

        atoms,index = data[5],data[6]
        name = "".join([a+i for a,i in zip(atoms,index)])
        index = [int(i) for i in index]

        self.data,self.atoms,self.index,self.name = data, atoms,index,name

        return data, atoms,index,name
    
    def updateData(self,data=None):
        """Updates the class atributes when the data is changed."""
        if data == None: data = self.data
        
        atoms,index = data[5],data[6]
        name = "".join([a+i for a,i in zip(atoms,index)])
        index = [int(i) for i in index]

        self.data,self.atoms,self.index,self.name = data, atoms,index,name
        self.nAtoms = sum(self.index)

    def toAIMS(self):
        """Transforms a CONTCAR from VASP to a geometry.in readable for FHI-AIMS."""

        data = self.data
        path = out_path + f"geometry.in.{self.filename}"
        nAtoms = self.nAtoms
        lattice = data[2:5]
        positions = data[9:9+nAtoms+1]
        atoms, indeces = self.atoms, self.index
        atNames = []
        for i,atom in enumerate(atoms):
            for _ in range(indeces[i]):
                atNames.append(atom)
        positions = [list(filter(lambda x: x!="T",positions[i])) for i in range(nAtoms)]
        lattice = ["lattice_vector   " + "   ".join(lattice[i]) for i in range(3)]

        positions = ["atom_frac   " + "   ".join(positions[i]) + "   " + atNames[i] for i in range(nAtoms)]

        with open(path,"w") as outfile:
            for line in lattice: outfile.write(line + "\n")
            for line in positions: outfile.write(line + "\n")

    def write(self):
        """Rewrites the modified CONTCAR file."""

        data = self.data
        path = f"./CONTCARout/{self.filename}"

        # gets lattice and positions part of the CONTCAR #!(ponerlo en funcion aparte?)
        lattice = data[:5]
        positions = data[5:]
        
        with open(path,"w") as outFile:
            # for line in data:
            #     str_line = "  ".join([l for l in line]) + "\n"
            #     outFile.write(str_line)

            for line in lattice:
                str_line = "  ".join([l for l in line]) + "\n"
                outFile.write(str_line)
                pass
            for line in positions:
                str_line = "  ".join([l for l in line]) + "\n"
                outFile.write(str_line)
                pass

    def getGeom(self):
        """Returns MXene lattice parameter a and width d in Armstrongs. \n
        For terminated n=1 MXenes, returns also d(M-T) for each surface."""
        
        data = self.toZero()
        nAtoms = self.nAtoms
        lattice = data[:5]
        positions = data[5:]

        posz = []   # List with the z fractional positions
        for i in range(nAtoms): posz.append(float(data[9+i][2]))

        # Getting the length of each lattice parameters
        lattice_params = []
        for i in range(3):
            l = sum([float(li)**2 for li in data[2+i]])**0.5
            lattice_params.append(l)
        a,b,c = lattice_params

        d = max(posz)*c     # Width of the slab

        # if len(posz) == 5:
        #     # GENERALIZAR PARA N>2 --> self.posM ?
        #     dMO1 = (posz[4]-posz[1])*c  # Top surface (HMX)
        #     dMO2 = (posz[0]-posz[3])*c  # Bottom surface (HM)
        #     return a, d, dMO1, dMO2
        # else: return a,d

        return a,d

    def toZero(self):
        """Shifts positions of atoms to start at zero."""
        
        data = self.data
        lattice = data[:5]
        positions = data[5:]
        
        nAtoms = self.nAtoms

        posz = []   # List with the z fractional positions
        for i in range(nAtoms): posz.append(float(data[9+i][2]))

        for i,pos in enumerate(posz):
            if pos > 0.75: posz[i] = pos - 1
        zo = min(posz)

        for i,pos in enumerate(posz): posz[i] -= zo

        posz = [str(format(posz[i],".16f")) for i in range(nAtoms)]

        for i in range(nAtoms): data[9+i][2] = posz[i]
            
        self.data = data

        return data

    def addVacuum(self,v=30):
        """Rescales the z positions to add the indicated vacuum."""
        data = self.toZero()
        nAtoms = self.nAtoms

        posz = []   # List with the z fractional positions
        for i in range(nAtoms): posz.append(float(data[9+i][2]))

        co = float(data[4][2])              # initial lattice c
        do = abs(max(posz)-min(posz))*co    # initial width
        cf = do + v                         # new lattice c
        
        posz = [posz[i]*co/cf for i in range(nAtoms)] # reescale positions

        cf = str(format(cf,".16f"))
        posz = [str(format(posz[i],".16f")) for i in range(nAtoms)]

        data[4][2] = cf
        for i in range(nAtoms): data[9+i][2] = posz[i]
        
        self.data = data

        return data
    
    def shift(self,shift=1):
        """Shifts MXene a given distance"""

        data = self.data
        nAtoms = self.nAtoms
        co = float(data[4][2])

        posz = []   # List with the z fractional positions
        for i in range(nAtoms): posz.append(float(data[9+i][2]))

        posz = [posz[i]+shift/co for i in range(nAtoms)]
        posz = [str(format(posz[i],".16f")) for i in range(nAtoms)]

        for i in range(nAtoms): data[9+i][2] = posz[i]

        self.data = data
        return data

    def addT(self,T:str,stack:str=None,hollows:str=None):
        """Adds single-atom termination (T) to the pristine MXene in the indicated hole position (hollows=HM/H,HMX,HX).\n
        Stacking can be indicated as stack=ABC/ABA, if not the program will guess it."""

        init = 8
        f = ".16f"
        n = self.mx.n
        data = self.addVacuum(v=30)   # shifts to zero and reescales to get vacuum == 30
        data = self.shift(shift=1)    # shifts the layer by 1 Ang

        data[5].append(T)
        data[6].append("2")

        M = data[9:9+n+1]
        X = data[9+n+1:9+2*n+1]

        nAtoms = self.nAtoms
        co = float(data[4][2])

        posz = []   # List with the z fractional positions
        for i in range(nAtoms): posz.append(float(data[9+i][2]))

        zmax,zmin = max(posz), min(posz)
        do = abs(zmin-zmax)*co

        if stack is not None: stacking = stack
        else:   #!better stacking detection?
            M1,M2 = data[9][0:2],data[10][0:2]
            if M1 == M2: stacking = "ABA"
            elif M1 != M2: stacking = "ABC"

        aH = format(round(2/3,16),f)
        bH = format(round(1/3,16),f)
        if hollows == "HM" and stacking == "ABA":
            warnings.warn("Warning: Using HM for ABA stacking, changing to H ...")
            hollows = "H" 
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

        posT = []
        for i in range(2):
            aT = a[i] #format(round(a[i],16),f)
            bT = b[i] #format(round(b[i],16),f)
            cT = str(format(i*(do+2)/co,".16f"))
            posTi = [aT,bT,cT,"T","T","T"]
            posT.append(posTi)
        t1,t2 = posT


        data.insert(9+2*n+1,t1)
        data.insert(9+2*n+2,t2)
        self.updateData(data)
        self.data = data

        data = self.addVacuum(v=30) #añade vacio de 10A y reescala
        
        return data


##########################  MAIN PROGRAM  ########################
# Chose which modifications are applied to the input CONTCAR/POSCAR

if __name__ == "__main__":
    contcars = os.listdir("CONTCARin")
    paths = [f"./CONTCARin/{c}" for c in contcars]
    out_path = "./CONTCARout/"

    try: os.mkdir("CONTCARout")
    except FileExistsError: pass

    for i,cont in enumerate(paths):
        name = contcars[i]
        if name.startswith("_"): continue

        contcar = CONTCAR(cont)
        mx = contcar.mx ##!

        ## Adds Vaccum to optimized M2X or M2XT2 CONTCAR.
        # contcar.addVacuum(v=30)
        # contcar.write()

        ## Adds Termination to optimized M2X CONTCAR.
        # contcar.addT("O",hollows="HMX")
        # contcar.write()

        ## Shifts the slab a certain amount
        # contcar.shift(3)
        # contcar.write()

        ## Shifts to zero/origin all the atoms 
        # contcar.toZero()
        # contcar.write()

        ##Transforms POSCAR to geometry.in for 
        # contcar.toAIMS()

        ##Prints cell parameters for input CONTCARs
        print(cont)
        print(f"{contcar.mx.mxName}: {contcar.getGeom()}")

