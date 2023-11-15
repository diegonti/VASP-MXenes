"""
Calculates local potential from the LOCPOT file by doing plane means along
the directon of the vaccum. Returns plot and Vaccuum potential.

Diego Ontiveros
"""

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import itertools
import numpy as np
import matplotlib.pyplot as plt

from VASP import MX


def isJanus(means,t,low,high,e):
    """Searches the vacuum region of the slab [low,high] and returns True in the case for Janus materials (with a e% of tolerance)."""
    flag1, flag2 = True, True
    for i,m in enumerate(means):
        if t[i] > low+1 and flag1:
            sf1, flag1 = m, False
        elif t[i] > high-1 and flag2:
            sf2, flag2 = m, False
            break
    #tolerance
    diff = abs(sf1-sf2)
    rdiff = diff/np.mean((sf1,sf2))*100
    if rdiff > e: return True
    else: return False


class WF():
    def __init__(self,path:str) -> None:
        """Workfunction object that contains the LOCPOT information and function to compute
        and plot the local potential and vacuum energies. Yakes the path of the LOCPOT file as argument."""

        self.path = path
        self.file = path.split("/")[-1]
        self.data = self.getData()
        self.t,self.means = None,None
        self.Vv, self.Vvsf1, self.Vvsf2 = None, None, None 


    def getData(self): 
        """Reads LOCPOT and gathers some important variables from the file"""

        self.data = []                   # Where the splitted lines of raw data go
        self.nAtoms = 5                    # Initial value for nAtoms
        with open(self.path,"r") as inFile:
            for n,line in enumerate(inFile):
                line = line.strip() # Removes leading and trailing whitespaces
                line = line.split() # Splits line by the spaces into list

                for i,e in enumerate(line):
                    try: e=float(e)
                    except ValueError: pass
                    line[i] = e
                if n == 0: self.mx = MX(line[0])
                if n == 4: self.latticeZ = line[2]       # c lattice parameter
                if n == 5: atoms = line                  # Atom symbols
                if n == 6: self.nAtoms = int(sum(line))  # nAtoms = sum of atom indeces
                if n == 7+self.nAtoms+2:                 # Grid points (x,y,z)
                    self.grid = int(line[0]),int(line[1]),int(line[2])

                self.data.append(line)
        self.first_atom = self.data[7+self.nAtoms-1][2]*self.latticeZ   # position of the lowest atom (T1)
        if self.first_atom > 0.75*self.latticeZ: self.first_atom = self.first_atom - self.latticeZ

        self.d = self.data[7+self.nAtoms][2]*self.latticeZ            # d = c*z(T2) == MXene thickness
        return self.data
        
        
    def calculate(self,tol_janus=5):
        """Calculates the electrostatic potential along the vaccum firection from a LOCPOT file.

        Parameters
        ----------
        `tol_janus` : Optional. Tolerance (in %) for calculating if the material is Janus. By default 5%.

        Returns
        -------
        `t` : z axis array along the vaccum lattice parameter.
        `means` : plane means of the local electrostatic potential along the directon of the vaccum.

        if not Janus:
            `Vv` : Vaccuum potential (in eV) of the structure.
        elif Janus:
            `Vvsf1` : Vaccuum potential (in eV) of the top surface of the structure.
            `Vvsf2` : Vaccuum potential (in eV) of the bottom surface of structure.
        """


        data = self.data
        nAtoms, latticeZ, d, first_atom = self.nAtoms, self.latticeZ, self.d, self.first_atom
        x,y,z = self.grid


        # Gets the energy points from the raw data list
        points = data[7+nAtoms+3:]                              # Only the point secction
        points = list(itertools.chain.from_iterable(points))    # Concatenates all the lists into one
        grid = x*y                                              # Slab grid of points to iterate

        # Spin polarized (ISPIN=2) or non-polaarized (ISPIN=1)
        if len(points) >= 2*grid*z:          # In theory polarized would give double the points for non-polarized, 
            spin,z = True, 2*z               # but it seems that sometimes some extra points are there, hence the >=.
        elif len(points) == grid*z: 
            spin = False

        # Separates the points in xy slabs    
        slabs = []
        for k in range(z): slabs.append(points[k*grid:(k+1)*grid])
        slabs2 = [points[k*grid:(k+1)*grid] for k in range(z)]

        # Calculates the mean of a xy slab and saves it into means array
        means = []            
        for k in range(z):
            m = sum(slabs[k])/len(slabs[k])
            means.append(m)
        means2 = [sum(slabs[k])/len(slabs[k]) for k in range(z)]
        means = np.array(means)
        
        # If spin polarized, the mean is also done between α (1º half of points) and β (2º half) parts
        if spin: means = sum([means[:int(z/2)],means[int(z/2):]])/2 

        # Vacuum Energy calculation
        t = np.linspace(0,latticeZ, len(means))   # z axis vector along the c lattice parameter
        low,high = d+3,latticeZ+self.first_atom-3                 # Limits to do the mean for calculating Vvaccum
        mid = np.mean((low,high))
        Vcalc,Vcalc_sf1,Vcalc_sf2 = [],[],[]
        self.janus = isJanus(means,t,low,high,tol_janus)

        if self.janus:
            for i,m in enumerate(means):
                if t[i]>low and t[i]<mid-1: Vcalc_sf1.append(m)
                elif t[i]>mid+1 and t[i]<high: Vcalc_sf2.append(m)
            Vvsf1 = np.mean(Vcalc_sf1)
            Vvsf2 = np.mean(Vcalc_sf2)
            print(f"{self.mx.mxName}  Vvsf1 = {Vvsf1}   Vvsf2 = {Vvsf2}", flush=True)
            self.t, self.means, self.Vvsf1, self.Vvsf2 = t,means, Vvsf1, Vvsf2
            return t,means, Vvsf1, Vvsf2

        
        else:
            for i,m in enumerate(means):          # Takes the energies in the vaccum region from low to high
                if t[i]>low and t[i]<high:        # and averages them to estimate the Vvaccum
                    Vcalc.append(m)
            Vv = np.mean(Vcalc)
            print(f"{self.mx.mxName}  Vvsf1 = {Vv}   Vvsf2 = {Vv}", flush=True)

            self.t, self.means, self.Vv = t,means, Vv
            return t,means, Vv, Vv
        

    def plot(self,name,show=False,incwd=False):
        """Plots the electrostatic means along the vaccuum direction. 

        Parameters
        ----------
        `show` : Optional. Show plot with plt.show(). By default False.
        `incwd` : Optional. When the LOCPOT is in the current dir. By default False.
        """

        if self.means is None: self.calculate()
        t,means = self.t, self.means
        latticeZ = self.latticeZ
        
        ##Plot settings 
        plt.rcParams.update({'font.size': 12})
        # plt.rcParams["font.family"] = "Times New Roman"   # Cooler and more formal font

        plt.plot(t,means,color="black", label="Local Potential")
        if self.janus:
            Vvsf1,Vvsf2 = self.Vvsf1, self.Vvsf2
            plt.axhline(y = Vvsf1, color = "r", linestyle = "--", label = "$V_{v,surf1}$")
            plt.axhline(y = Vvsf2, color = "b", linestyle = "--", label = "$V_{v,surf2}$")
            plt.text(5,0,s= "$V_{v,surf1}$ = " + f"{Vvsf1:.2f} eV", color = "r",fontsize = 12)
            plt.text(20,0,s= "$V_{v,surf2}$ = " + f"{Vvsf2:.2f} eV", color = "b", fontsize = 12)

        else:
            Vv = self.Vv
            plt.axhline(y = Vv, color = "r", linestyle = "--", label = "$V_{v}$")
            plt.text(14,0,s= "$V_{v}$ = " + f"{Vv:.2f} eV" ,fontsize = 12)

        plt.xlabel("z axis (Å)")
        plt.ylabel("Energy (eV)")
        plt.xlim(xmin=0,xmax=latticeZ)
        plt.ylim(ymax=5)
        plt.legend(frameon=False)

        if incwd: plt.savefig(f"{name}",format="png",dpi=600)
        else: plt.savefig(f"{name}",format="png",dpi=600)

        plt.close()
        #if show = plt.show()


############################## MAIN PROGRAM ###################################

if __name__ == "__main__":
    cwd = os.listdir()
    
    if "LOCPOT" in cwd: WF("LOCPOT").plot(name="LOCPOTplt")

    elif "WFin" in cwd and "LOCPOT" not in cwd:

        # Reads LOCPOTs from WFin folder and returns the plots in WFout
        try: os.mkdir("WFout")
        except FileExistsError: pass
        inFiles = os.listdir("./WFin")
        fileNames = [f for f in inFiles if os.path.isfile("./WFin/"+f)]
        inFiles = ["./WFin/" + f for f in inFiles if os.path.isfile("./WFin/"+f)]

        for file,name in zip(inFiles,fileNames):
            wf = WF(file)
            wf.calculate()
            wf.plot(name=f"./Wfout/{name}.png")

