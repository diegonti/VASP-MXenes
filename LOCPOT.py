import matplotlib.pyplot as plt
import os
import itertools
import numpy as np

def isJanus(means,t,low,high,e):
    """Searches the vacucum region of the slab [low,high] and returns True in the case for Janus materials (with a e% of tolerance)."""
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
    if spin: means = sum([means[:int(z/2)],means[int(z/2):]])/2 

    ##Vacuum Energy calculation
    t=np.linspace(0,latticeZ, len(means)) #z axis vector along the c lattice parameter
    low,high = d+3,latticeZ-3             #Limits to do the mean for calculating Vvaccum
    mid = np.mean((low,high))
    Vcalc,Vcalc_sf1,Vcalc_sf2 = [],[],[]
    janus = isJanus(means,t,low,high,5)

    if janus:
        for i,m in enumerate(means):
            if t[i]>low and t[i]<mid-1: Vcalc_sf1.append(m)
            elif t[i]>mid+1 and t[i]<high: Vcalc_sf2.append(m)
        Vvsf1 = np.mean(Vcalc_sf1)
        Vvsf2 = np.mean(Vcalc_sf2)
        print(f"{name}: Vvsf1 = {Vvsf1}   Vvsf2 = {Vvsf2}")
    
    else:
        for i,m in enumerate(means):          #Takes the energies in the vaccum region from low to high
            if t[i]>low and t[i]<high:        #and averages them to estimate the Vvaccum
                Vcalc.append(m)
        Vv = np.mean(Vcalc)
        print(f"{name} = {Vv}")

    ##Plot settings 
    plt.rcParams.update({'font.size': 12})
    plt.rcParams["font.family"] = "Times New Roman"   #Cooler and more formal font

    plt.plot(t,means,color = "black", label = "WF")
    if janus:
        plt.axhline(y = Vvsf1, color = "r", linestyle = "--", label = "$V_{v,surf1}$")
        plt.axhline(y = Vvsf2, color = "b", linestyle = "--", label = "$V_{v,surf2}$")
        plt.text(5,0,s= "$V_{v,surf1}$ = " + f"{Vvsf1:.2f} eV", color = "r",fontsize = 12)
        plt.text(20,0,s= "$V_{v,surf2}$ = " + f"{Vvsf2:.2f} eV", color = "b", fontsize = 12)

    else:
        plt.axhline(y = Vv, color = "r", linestyle = "--", label = "$V_{vacuum}$")
        plt.text(14,0,s= "$V_{vacuum}$ = " + f"{Vv:.2f} eV" ,fontsize = 12)

    plt.xlabel("z axis (Å)")
    plt.ylabel("Energy (eV)")
    plt.xlim(xmin=0,xmax=latticeZ)
    plt.ylim(ymax=5)
    plt.legend(frameon=False)

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
    fileNames = [f for f in inFiles if os.path.isfile("./WFin/"+f)]
    inFiles = ["./WFin/" + f for f in inFiles if os.path.isfile("./WFin/"+f)]

    for file,name in zip(inFiles,fileNames):
        WF(file,name)

