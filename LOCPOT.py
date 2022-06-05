import matplotlib.pyplot as plt
import os
import itertools
import numpy as np


def WF(file,name,incwd=False):
    """Takes a LOCPOT file and returns a WorkFunction plot along the z axis, also returning the vacuum energy (Vvacuum).\n
    The program can take a LOCPOT file from the same directory and return the plot in the same path or\n
    do a loop over all the LOCPOT files in /WFin and return the plots in /WFout."""

    ##Reads LOCPOT and gathers some important variaboles from the file
    data = []                   #Where the splitted lines of raw data go
    n = 0                       #Line counter
    nAtoms=5                    #Initial value for nAtoms
    with open(file,"r") as inFile:
        for line in inFile:
            line = line.strip() #Removes leading and trailing whitespaces
            line = line.split() #Splits line by the spaces into list

            for i,e in enumerate(line):
                try: e=float(e)
                except ValueError: pass
                line[i] = e

            if n == 4: latticeZ = line[2]       #c lattice parameter
            if n == 5: atoms = line             #Atom symbols
            if n == 6: nAtoms = int(sum(line))  #nAtoms = sum of atom indeces
            if n == 12: d = line[2]*latticeZ    #d = c*z(O) == MXene thickness
            if n == 7+nAtoms+2:                 #Grid points (x,y,z)
                x,y,z = int(line[0]),int(line[1]),int(line[2])

            data.append(line)
            n += 1

    ##Gets the energy points from the raw data list
    points = data[7+nAtoms+3:]                              #Only the point secction
    points = list(itertools.chain.from_iterable(points))    #Concatenates all the lists into one
    grid = x*y                                              #Slab grid of points to iterate

    ##Spin polarized (ISPIN=2) or non-polaarized (ISPIN=1)
    if len(points) >= 2*grid*z:          #In theory polarized would give double the points for non-polarized, 
        spin,z = True, 2*z               #but it seems that sometimes some extra points are there, hence the >=.
    elif len(points) == grid*z: 
        spin = False

    ##Separates the points in xy slabs    
    slabs = []
    for k in range(z):
        slabs.append(points[k*grid:(k+1)*grid])

    ##Calculates the mean of a xy slab and saves it into means array
    means= []            
    for k in range(z):
        m = sum(slabs[k])/len(slabs[k])
        means.append(m)
    means = np.array(means)
    
    ##If spin polarized, the mean is also done between α (1º half of points) and β (2º half) parts
    if spin: means = sum([means[:int(z/2)],means[int(z/2):]])/2 #/2???

    ##Vacuum Energy calculation
    t=np.linspace(0,latticeZ, len(means)) #z axis vector along the c lattice parameter
    low,high = d+3,latticeZ-3             #Limits to do the mean for calculating Vvaccum
    Vcalc = []
    for i,m in enumerate(means):          #Takes the energies in the vaccum region from low to high
        if t[i]>low and t[i]<high:        #and averages them to estimate the Vvaccum
            Vcalc.append(m)
    Vv = np.mean(Vcalc)
    print(f"{name} = {Vv}")

    ##Plot settings 
    plt.rcParams.update({'font.size': 12})
    plt.rcParams["font.family"] = "Times New Roman"   #Cooler and more formal font

    plt.plot(t,means,color = "black", label = "WF")
    plt.axhline(y = Vv, color = "r", linestyle = "--", label = "$V_{vacuum}$")
    plt.xlabel("z axis (Å)")
    plt.ylabel("Energy (eV)")
    plt.xlim(xmin=0,xmax=latticeZ)
    plt.ylim(ymax=5)
    plt.legend(frameon=False)
    Vv = format(Vv,".2f")
    plt.text(14,0,s= "$V_{vacuum}$ = " + f"{Vv} eV" ,fontsize = 12)

    if incwd: plt.savefig(f"{name}.png",format="png",dpi=1200)
    else: plt.savefig(f"./WFout/{name}.png",format="png",dpi=1200)

    plt.close()
    #plt.show()
    

### MAIN program

cwd = os.listdir()
if "LOCPOT" in cwd:
    WF("LOCPOT","LOCPOTplt",incwd = True)

elif "WFin" in cwd and "LOCPOT" not in cwd:

    ##Reads LOCPOTs from WFin folder and returns the plots in WFout
    try: os.mkdir("WFout")
    except FileExistsError: pass
    inFiles = os.listdir("./WFin")
    inFiles.remove("INCAR")
    fileNames = [f for f in inFiles if os.path.isfile("./WFin/"+f)]
    inFiles = ["./WFin/" + f for f in inFiles if os.path.isfile("./WFin/"+f)]

    for file,name in zip(inFiles,fileNames):
        WF(file,name)

