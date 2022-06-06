from VASP import MX
import matplotlib.pyplot as plt
import numpy as np
import os

def getBandGap(E,T,Ef):
    """Takes Energy and Total DOS arrays and returns BandGap, VBM and CBM"""
    
    E = E+Ef
    Ef = round(Ef,3)
    
    searchVBM,searchCBM = False, False
    for i,e in enumerate(E):
        if e == round(Ef-0.01,3):
            searchVBM = True
        if searchVBM:
            if T[i] == 0:
                VBM = round(E[i-1],3)
                searchCBM, searchVBM = True, False
            if T[i] != 0 and e > Ef+0.002: searchVBM = False
        if searchCBM:
            if T[i] != 0:
                CBM = round(E[i],3)
                searchCBM = False
                break
        else: VBM,CBM = Ef,Ef
            

    bandgap = round(CBM-VBM,3) 
 
    return bandgap, VBM, CBM

def DOSCAR(dos, *args, spin=False, invertE = False, show = False):
    """Plots DOS of MXene from a spin-polarized DOSCAR file and returns Bandgap, VBM and CVM.\n
    Make sure the file contains SYSTEM name as Mn+1XnT2! (i.e. Ti2C1O2)\n
    Specify if you want the plot with spin contribution (α/β) or total (spin = False).\n
    Args: Specify list with which lines you want to see plotted and color [line,color].\n
    Lines: M,Ma,Mb Ms,Mp,Md Msa/Msb,Mpa/Mpb,Mda,Mdb (total lines are always drawn)."""

    fname = dos.replace("./DOSin/","") #Initial File Name

    ##Gathering of the parameters to plot and their respective colour
    toPlot = []
    colors = []
    if spin == True: 
        toPlot.append("Ta"); toPlot.append("Tb")
        colors.append("red");colors.append("blue")
    if spin == False: toPlot.append("T"); colors.append("black")
    for p,c in args:
        toPlot.append(p)
        colors.append(c)


    ##Reads the DOSCAR file, gathers important information (nAtoms,NEDOS,Ef,...) and puts the splitted lines in the out list
    out = []
    with open(dos,"r") as infile:

        for n,line in enumerate(infile):
            rline = line.strip() #Removes inecessary whitespaces at the begining and end of line
            line = rline.split() #Splits the line by the whitespaces into sublists

            for i,nl in enumerate(line):   #Floating the numbers of the lines,
                try: nl = float(nl)        #except when tey are strings
                except ValueError: pass
                line[i] = nl

            if n == 0: nAtoms = int(line[0])   #Number of atoms in cell
            if n == 4: mx = MX(rline)          #Name of the MXene, specified by SYSTEM = Mn+1XnT2 in the INCAR
            if n == 5: EMAX, EMIN, NEDOS, Ef = line[0], line[1], int(line[2]), line[3]

            out.append(line)
    print(f"{mx.mxName}: Ef = {Ef}eV")         #Prints the Fermi level of the MXene studied
    

    ##List with embeded lists of each atom information [Total,At1,At2,At3,...]
    data = [] #Gathers the points for each section of the data in diferent lists
    for at in range(nAtoms+1):
        data.append(out[(at)*NEDOS+6+(at):(at+1)*NEDOS+6+(at)])

    ##Loop for obtaining the Total DOS data, taking into account that in the DOSCAR are distributed as E|Tα|Tβ|iTa|iTb
    E,T,iT,Ta,Tb,iTb,iTa = [np.array([]) for i in range(7)]          #Each paramater goes to a dedicated list with its name
    for line in data[0][1:]:
        E = np.append(E,line[0]-Ef)                                  #Energy points (corrected by the fermi level, Ef)
        Ta = np.append(Ta,line[1]); Tb = np.append(Tb,line[2])       #Total α (Ta) and Total β (Tb) DOS contributions
        iTa = np.append(iTa,line[3]); iTb = np.append(iTb,line[4])   #Total DOS integrations for a and b
        T = np.append(T,line[1]+line[2])                             #Total DOS (Ta+Tb)
        iT = np.append(iT,line[3]+line[4])                           #Total integration (iTa,iTb)

    bandgap, VBM, CBM = getBandGap(E,T,Ef)
    print(f"{fname}: Eg = {bandgap:.3f}   VBM = {VBM:.3f}   CBM = {CBM:.3f}")
    
    ##Loop for obtaining the orbitalic contribution to DOS for each atom. In DOSCAR distributed as the variables order
    #sa,sb, pya,pyb,pza,pzb,pxa,pxb, dxya,dxyb,dyza,dyzb,dxza,dxzb,dz2a,dz2b,dx2y2a,dx2y2b (18 OA)
    #All the orbitals are generated in the orb list, for easier manipulation
    orb = [[[] for i in range(nAtoms)] for j in range(18)]

    #Separates coulumns by their orbitalic components
    for i,atom in enumerate(data[1:]):           #For each atom DOS dataset
        for line in atom[1:]:                    #For every line in each atom dataset
            for oa in range(len(orb)):           #For every atomic orbital (oa) in orb
                orb[oa][i].append(line[oa+1])    #Appends DOS coumn to its corresponding OA
    for oa in range(18): orb[oa] = np.array(orb[oa])   #Transforma las listas en arrays de numpy for better manipulation

    #Each orbital will be a list with the contributions of each atom for that orbital
    #It is important to namme the variables, as they will serve as the general name to use in the *args for which parameters to plot
    sa,sb, pya,pyb,pza,pzb,pxa,pxb, dxya,dxyb,dyza,dyzb,dxza,dxzb,dz2a,dz2b,dx2y2a,dx2y2b = [orb[i] for i in range(18)]

    ##Viariable assignment for the different general orbital components (s,p,d). a and b mean alpha and beta
    pa,pb = pya+pza+pxa,pyb+pzb+pxb                                   #Since numpy arrays are used, the embeded lists can
    da,db = dxya+dyza+dz2a+dxza+dx2y2a,dxyb+dyzb+dz2b+dxzb+dx2y2b     #be added up and each list component will be added to
    s,p,d = sa+sb,pa+pb,da+db                                         #the corresponding one in the adjacent list (only if the
    atTa = sa+pa+da     #Total DOSa for each atom                     #lists have the same range)
    atTb = sb+pb+db     #Total DOSb for each atom
    atT = sum(orb)      #Total DOS for each atom

    ##Creates arrays for the metal (M) contributions
    M,Ma,Mb, Ms,Mp,Md, Msa,Mpa,Mda,Msb,Mpb,Mdb = [np.zeros(NEDOS-1) for i in range(12)]
    for i in range(mx.n+1):          #To take the first n+1 lists (where the M data is)
        M += atT[i]                                 
        Ma += atTa[i]; Mb += atTb[i]
        Ms += s[i]; Mp += p[i]; Md += d[i]
        Msa += sa[i]; Mpa += pa[i]; Mda += da[i]
        Msb += sb[i]; Mpb += pb[i]; Mdb += db[i]

    ##Creates arrays for the carbide/nitride (X) contributions
    X,Xa,Xb, Xs,Xp,Xd, Xsa,Xpa,Xda,Xsb,Xpb,Xdb = [np.zeros(NEDOS-1) for i in range(12)]
    for i in range(mx.n+1,2*mx.n+1): #To take the n+1 to 2n+1 lists (where the X data is)
        X += atT[i]
        Xa += atTa[i]; Xb += atTb[i]
        Xs += s[i]; Xp += p[i]; Xd += d[i]
        Xsa += sa[i]; Xpa += pa[i]; Xda += da[i]
        Xsb += sb[i]; Xpb += pb[i]; Xdb += db[i]

    ##Creates arrays for the termination (Term) contributions (only if there is termination)
    Term,Terma,Termb, Terms,Termp,Termd, Termsa,Termpa,Termda,Termsb,Termpb,Termdb = [np.zeros(NEDOS-1) for i in range(12)]
    if mx.terminal:
        if mx.OH: pass #OH termination not implemented. Works for single atom terminations
        else: #To take the last two lists (where the Term data is)
            for i in range(-2,0):
                Term += atT[i]
                Terma += atTa[i]; Termb += atTb[i]
                Terms += s[i]; Termp += p[i]; Termd += d[i]
                Termsa += sa[i]; Termpa += pa[i]; Termda += da[i]
                Termsb += sb[i]; Termpb += pb[i]; Termdb += db[i]


    ##Loop that draws each specified line (contribution) in *args
    plt.rcParams["figure.figsize"] = (4.8,2)         #In case to give a fized image size (in inches)
    #plt.rcParams["figure.autolayout"] = True         #To autoajust plot if figsize is changed
    plt.rcParams["font.family"] = "Times New Roman"   #Cooler and more formal font

    fig,plot = plt.subplots()

    for i,param in enumerate(toPlot): 

        #locals()[p] searches local variables of the name p and returns its value, in this case returning the DOS lists
        pname = param                                   #Paramater name
        if pname[-1] == "b": param = -locals()[param]   #For spin b parameters
        else: param = locals()[param]                   #For spin a parameters

        #Label assesment for legend. Changing M,X,T for their corresponding element
        pname = pname.replace("a","α")
        pname = pname.replace("b","β")
        if pname == "T": pname = "Total"
        if pname == "Tα": pname = "Total α"
        if pname == "Tβ": pname = "Total β"
        if "M" in pname: pname = pname.replace("M",mx.atoms[0]+" ")
        if "X" in pname: pname = pname.replace("X",mx.atoms[1]+" ")
        if mx.terminal:
            if "Term" in pname: pname = pname.replace("Term",mx.atoms[2]+" ")
        
        #PLOT. Plots the corresponding parameter introduced in *args with the energy
        plot.plot(E,param, label = f"{pname}", color = colors[i], linewidth = 1)

    #Plot configuration (title, axis, x inversion, ...)
    plot.axhline(0,color = "black", lw = 1) 
    plot.axvline(0,color = "black", lw = 1, linestyle = "--")
    # plot.set_title(f"DOS {mx.mxName}")
    plot.set_xlabel("Energy (eV)")
    plot.set_ylabel("DOS")
    plot.set_xlim([-10,10])
    if not spin: plot.set_ylim(ymin=0,ymax=20)
    # elif spin: plot.set_ylim([-15,15])
    if invertE: plot.invert_xaxis()
    plot.legend(frameon=False,fontsize = "x-small")

    #Saves Plot as .png
    outFiles = os.listdir("./DOSout") + ["LAST"]
    outFiles = ["./DOSout/" + outFiles[i] for i in range(len(outFiles))]
    fileName = f"./DOSout/{fname}.png"
    if fileName in outFiles: #In case there are repeated names
        fileName = fileName.replace(".png","(d).png")
        plt.savefig(fileName,format="png",dpi=1200)
    else: plt.savefig(f"./DOSout/{fname}.png",format="png",dpi=1200)

    if show: plt.show() #In case the plots want to be shown on screen as they are created


### -------------------------------------------- MAIN PROGRAM ---------------------------------------------------- ###
###--------------------------------------------------------------------------------------------------------------- ###

# Creates DOSout folder where the plots will save
try: os.mkdir("DOSout")
except FileExistsError: pass
#List of input files to open, in DOS in folder
inFiles = os.listdir("./DOSin")
inFiles = ["./DOSin/" + f for f in inFiles if os.path.isfile("./DOSin/"+f)]

#Loop for each input file in DOSin
for dos in inFiles:

    #Quick read to see if the MXene is terminal 
    with open(dos,"r") as f: conents = f.readlines()
    mx = conents[4].split()[0]
    mx = MX(mx)

    if mx.terminal:   #DOS (sp and nsp) for M2XT2
        #DOSCAR(dos,["Ma","orange"], ["Mb","cyan"],["Xa","pink"],["Xb","violet"], ["Terma","yellow"],["Termb","grey"],spin = True, show=False)
        DOSCAR(dos,["M","red"],["X","blue"],["Term","green"],spin = False, show=False)
    else:   #DOS (sp and nsp) for M2X
        DOSCAR(dos,["Ma","orange"], ["Mb","cyan"],["Xa","pink"],["Xb","violet"],spin = True, show=False)
        DOSCAR(dos,["M","red"],["X","blue"],spin = False, show=False)
