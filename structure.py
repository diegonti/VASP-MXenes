from VASP import MX
import os


def toZero(data):
    
    """Shifts positions of atoms to start at zero."""
    
    len = sum([int(i) for i in data[6]]) #Capas MXene a partir de indices átomos.

    posz = []
    for i in range(len):
        posz.append(float(data[9+i][2])) #lista con posiciones de z

    if len == 3: #para M2X
        zoindex,zo = 0,posz[0]
    if len == 5:  #para M2XT2
        zoindex,zo = 3,posz[3]

    if zo == max(posz) or zo>0.5: #si la posición minima esta por encima de todas
        for i in range(len):
            if i == zoindex: pass
            else: 
                posz[i] = posz[i]+(1-zo)
                if posz[i]>1: posz[i] = posz[i] -1

    if zo == min(posz) or zo<0.5: #si la posición minima esta por debajo de todas
        for i in range(len):
            if i == zoindex: pass
            else: posz[i] = posz[i]-zo

    if len == 3: posz[0] = zo-zo
    if len == 5: posz[3] = zo-zo
    
    posz = [str(format(posz[i],".16f")) for i in range(len)]

    for i in range(len):
        data[9+i][2] = posz[i]

    
    return data

def addVacuum(data,v = 10):
    """Rescales the z positions to add the indicated vacuum."""
    data = toZero(data)
    len = sum([int(i) for i in data[6]]) #Capas MXene a partir de indices átomos.

    co = float(data[4][2])
    posz = []
    for i in range(len):
        posz.append(float(data[9+i][2])) #lista con posiciones de z

    do = abs(max(posz)-min(posz))*co #distancia capa
    cf = do + v #nueva altura
    
    posz = [posz[i]*co/cf for i in range(len)] #reescalado

    cf = str(format(cf,".16f"))
    posz = [str(format(posz[i],".16f")) for i in range(len)]

    data[4][2] = cf
    for i in range(len):
        data[9+i][2] = posz[i]

    return data

def shift(data,shift = 1):
    """Shifts MXene a given distance"""


    len = sum([int(i) for i in data[6]]) #Capas MXene a partir de indices átomos.
    co = float(data[4][2])

    posz=[]
    for i in range(len):
        posz.append(float(data[9+i][2])) #lista con posiciones de z

    posz = [posz[i]+shift/co for i in range(len)]
    posz = [str(format(posz[i],".16f")) for i in range(len)]

    for i in range(len):
        data[9+i][2] = posz[i]

    return data

def addT(data,T="O",stack = None, hollows="HM"):
    """Adds single-atom termination (T) to the pristine MXene in the indicated hole position (hollows=HM/H,HMX,HX).\n
    Stacking can be indicated as stack=ABC/ABA, if not the program will guess it."""

    data = addVacuum(data, v=10) #pone a zero, añade vacio de 10 y reescala
    data = shift(data, shift=1) #levanta la capa 1A

    data[5].append(T)
    data[6].append("2")

    co = float(data[4][2])
    z1,z2,z3 = float(data[9][2]),float(data[10][2]),float(data[11][2])
    do = abs(z2-z1)*co

    if stack is not None: stacking = stack
    else:
        M1,M2 = data[9][0:2],data[10][0:2]
        if M1 == M2: stacking = "ABA"
        elif M1 != M2: stacking = "ABC"

    if stacking == "ABC": a,b = [2,0,2,1,1,1],[1,3,1,2,2,2]
    elif stacking == "ABA": a,b = [2,2,2,1,1,1],[1,1,1,2,2,2]

    if hollows == "HM" or hollows == "H": #Coloca T en Huecos Metálicos (HM) o en Huecos (H) (model 2)
        t1 = [str(format(a[0]/3,".16f")),str(format(b[0]/3,".16f")), str(format(0,".16f"))]
        t2 = [str(format(a[1]/3,".16f")),str(format(b[1]/3,".16f")), str(format((do+2)/co,".16f"))]
    elif hollows == "HMX": #Coloca T en Huecos Metálicos o Huecos y Huecos de X (model 3)
        t1 = [str(format(a[2]/3,".16f")),str(format(b[2]/3,".16f")), str(format(0,".16f"))]
        t2 = [str(format(a[3]/3,".16f")),str(format(b[3]/3,".16f")), str(format((do+2)/co,".16f"))]
    elif hollows == "HX": #Coloca T en Huecos de X (model 4)
        t1 = [str(format(a[4]/3,".16f")),str(format(b[4]/3,".16f")), str(format(0,".16f"))]
        t2 = [str(format(a[5]/3,".16f")),str(format(b[5]/3,".16f")), str(format((do+2)/co,".16f"))]


    data.insert(12,t1)
    data.insert(13,t2)

    data = addVacuum(data, v=10) #añade vacio de 10A y reescala
    
    return data


def getGeom(data):
    """Returns MXene lattice parameter a and width d in Armstrongs. \n
    For terminated n=1 MXenes, returns also d(M-T) for each surface."""
    data = toZero(data)
    nAtoms = sum([int(i) for i in data[6]]) #Capas MXene a partir de indices átomos.

    posz = []
    for i in range(nAtoms):
        posz.append(float(data[9+i][2])) #lista con posiciones de z

    a = float(data[2][0])
    bx,by = float(data[3][0]),float(data[3][1])
    b = float((bx**2+by**2)**0.5)
    c = float(data[4][2])
    d = max(posz)*c

    if len(posz) == 5:
        dMO1 = (posz[4]-posz[1])*c #Top surface (HMX)
        dMO2 = (posz[0]-posz[3])*c #Bottom surface (HM)
        return a, d, dMO1, dMO2
    else: return a,d

def writeCON(data,name):
    """Rewrites the CONTCAR file."""

    path = "./CONTCARout/{}".format(name)

    if len(data[5]) >= 3: #Si es un M2XT2
        lp = data[1][0]
        a,b,c = data[2],data[3],data[4]
        strAtoms = "".join([a + " " for a in data[5]])
        strIndex = "".join([str(i) + " " for i in data[6]])
        pos1,pos2,pos3,pos4,pos5 = data[9],data[10],data[11],data[12],data[13]

        with open(path,"w") as outfile:
            outfile.write(
                f"{mx.mxName}\n"
                f"   {lp}\n"
                f"     {a[0]}    {a[1]}    {a[2]}\n"
                f"    {b[0]}    {b[1]}    {b[2]}\n"
                f"     {c[0]}    {c[1]}   {c[2]}\n"
                f"  {strAtoms}\n"
                f"  {strIndex}\n"
                "Selective Dynamics\n"
                "Direct\n"
                f"  {pos1[0]}  {pos1[1]}  {pos1[2]}   T   T   T\n"
                f"  {pos2[0]}  {pos2[1]}  {pos2[2]}   T   T   T\n"
                f"  {pos3[0]}  {pos3[1]}  {pos3[2]}   T   T   T\n"
                f"  {pos4[0]}  {pos4[1]}  {pos4[2]}   T   T   T\n"
                f"  {pos5[0]}  {pos5[1]}  {pos5[2]}   T   T   T\n"
                "\n"
                "  0.00000000E+00  0.00000000E+00  0.00000000E+00\n"
                "  0.00000000E+00  0.00000000E+00  0.00000000E+00\n"
                "  0.00000000E+00  0.00000000E+00  0.00000000E+00\n"
                "  0.00000000E+00  0.00000000E+00  0.00000000E+00\n"
                "  0.00000000E+00  0.00000000E+00  0.00000000E+00\n"
            )
   
    else: #Si es un M2X

        lp = data[1][0]
        a,b,c = data[2],data[3],data[4]
        strAtoms = "".join([a + " " for a in data[5]])
        strIndex = "".join([str(i) + " " for i in data[6]])
        pos1,pos2,pos3 = data[9],data[10],data[11]

        with open(path,"w") as outfile:
            outfile.write(
                f"{mx.mxName}\n"
                f"   {lp}\n"
                f"     {a[0]}    {a[1]}    {a[2]}\n"
                f"    {b[0]}    {b[1]}    {b[2]}\n"
                f"     {c[0]}    {c[1]}   {c[2]}\n"
                f"  {strAtoms}\n"
                f"  {strIndex}\n"
                "Selective Dynamics\n"
                "Direct\n"
                f"  {pos1[0]}  {pos1[1]}  {pos1[2]}   T   T   T\n"
                f"  {pos2[0]}  {pos2[1]}  {pos2[2]}   T   T   T\n"
                f"  {pos3[0]}  {pos3[1]}  {pos3[2]}   T   T   T\n"
                "\n"
                "  0.00000000E+00  0.00000000E+00  0.00000000E+00\n"
                "  0.00000000E+00  0.00000000E+00  0.00000000E+00\n"
                "  0.00000000E+00  0.00000000E+00  0.00000000E+00\n"
            )

def posAIMS(data):
    path = "./CONTCARout/{}".format(name)
    lattice = data[2:5]
    atNames,indeces = data[5],[int(data[6][i]) for i in range(len(data[6]))]
    nAtoms = (sum([int(indeces[i]) for i in range(len(indeces))]))
    atoms = []
    for i in range(len(atNames)):
        for j in range(indeces[i]):
            atoms.append(atNames[i])
    positions = data[9:9+nAtoms+1]
    positions = [list(filter(lambda x: x!="T",positions[i])) for i in range(nAtoms)]
    lattice = ["lattice_vector   " + "   ".join(lattice[i]) for i in range(3)]

    positions = ["atom_frac   " + "   ".join(positions[i]) + "   " +atoms[i] for i in range(nAtoms)]

    with open(path,"w") as outfile:
        for i in lattice: outfile.write(i + "\n")
        for i in positions: outfile.write(i + "\n")


### Main Program - Chose which modifications are applied to the input CONTCAR/POSCAR

contcars = os.listdir("CONTCARin")
paths = [f"./CONTCARin/{c}" for c in contcars]

try: os.mkdir("CONTCARout")
except FileExistsError: pass

n = 0
for contcar in paths:
    name = contcars[n]
    file = contcar

    with open(file,"r") as infile:
        contIN = infile.readlines()
        contIN = [line.strip() for line in contIN]
        contIN = [line.split() for line in contIN]

    mxAtoms,mxIndex = contIN[5],contIN[6]
    mxName = ""
    for i in range(len(mxAtoms)): mxName += mxAtoms[i] + mxIndex[i]
    mx = MX(mxName)

    ## Adds Vaccum to optimized M2X or M2XT2 CONTCAR.
    # data = addVacuum(contIN,v=10)
    # writeCON(data,name)

    ## Adds Termination to optimized M2X CONTCAR.
    # data = addT(contIN, hollows="HMX")
    # writeCON(data,name)

    ## Shifts to zero/origin all the atoms 
    # data = toZero(contIN)
    # writeCON(data,name)

    ##Transforms POSCAR to geometry.in for 
    #posAIMS(contIN)

    ##Prints cell parameters for input CONTCARs
    print(contcar)
    print(f"{mx.mxName}: {getGeom(contIN)[2:]}")

    n += 1 

#for line in data: print(line)
