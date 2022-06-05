import os
import shutil
import math as m

def splitNums(string):
    """Para un string con letras y numeros, devuelve una lista con palabras y numeros separados,
    en orden de como aparecen."""

    previous_character = string[0]
    groups = [] #donde iran las partes
    newword = string[0] 
    for x, i in enumerate(string[1:]): #crea iterable con cada caracter enumerado ((0,s0),(1,s2),...) (empezando a partir de s1)
        if i.isalpha() and previous_character.isalpha():
            newword += i #si son del mismo tipo(str) se añade a la palabra
        elif i.isnumeric() and previous_character.isnumeric():
            newword += i #si son del mismo tipo(numero) se añade al numero
        else:
            if newword.isdigit():
                groups.append(int(newword)) #añadimos palabra o numero a la lista
            else:
                groups.append(newword)
            newword = i #pasamos al siguiente carcater

        previous_character = i

        if x == len(string) - 2:
            if newword.isdigit():
                groups.append(int(newword)) #añadimos palabra o numero a la lista
            else:
                groups.append(newword)
            newword = ''
    return groups


class MX():
    
    #Que pseudopotenciales utilizar para cada metal (nombre carpeta) (si no, cojera el normal)
    pp = ['Sc_sv', 'Ti_pv', 'V_pv', 'Cr_pv', 'Y_sv', 'Zr_sv', 'Nb_pv', 'Mo_pv', 'Hf_pv', 'Ta_pv', 'W_pv']

    def __init__(self, name):

        self.name = name #Nombre del MXene 
        self.mxName = self.name.replace("1","") #Nombre del MXene "bonito" (sin 1)
        
        #lista con sublista del MXene separado por atomo,indice
        self.cparts = splitNums(self.name)

        #lista con atomos del MXene
        self.atoms = [a for a in self.cparts if type(a) == str]

        #lista con indices de los atomos del MXene
        self.index = [j for j in self.cparts if type(j) == int]

        #Determina si el MXene tiene terminaciones
        if len(self.atoms) >= 3 and len(self.index) >= 3:
            self.terminal = True
        else: self.terminal = False
        
        if self.atoms[-2]+self.atoms[-1] == "OH":
            self.OH = True
        else: self.OH = False

        
        self.n = self.index[0] - 1 #n del MXeno (1,2,3)
        self.do = 2.5 #distancia inicial de cada capa de MXene (no la total)
        self.v = 10 #distancia de vacio
        self.ab = 3 #parámetro de celda a b
        self.lp = 1

        if self.terminal: self.shift = 1
        else: self.shift = 0

        self.stacking = "ABA"
        self.hollows = "HM"


        self.pdir = f"./MXenes/{self.mxName}/"     

        if self.terminal:
            dirsM2XT2 = ["opt","opt/PBE","opt/PBE0","opt/PBE/isif3","opt/PBE/isif4","opt/PBE/isif27",
                    "opt/PBE0/isif3","opt/PBE0/isif4","opt/PBE0/isif27",
                    "DOS", "DOS/PBE0", "BS","BS/PBE","BS/PBE0","BS/PBE/BS2","BS/PBE0/BS2"]
            self.dirs = [self.pdir + i +"/" for i in dirsM2XT2]
        else:
            dirsM2X = ["opt","opt/isif3","opt/isif4","opt/isif27","DOS", "BS1","BS1/BS2"]
            self.dirs = [self.pdir + i +"/" for i in dirsM2X]



    def positions(self): #n=1, do=2.5, v=10, shift=0
        """Devuelve las coordenadas directas de un MXene para la n indicada."""
        
        #Parámetros de ancho de capa (do) y vacío entre capas (v)
        n = self.n
        do,v = self.do, self.v
        shift = self.shift
        stacking = self.stacking
        hollows = self.hollows
        
        f = ".15f" #numero decimales
        
        #Listas de los valores que toman las coordenadas x y y en los atomos
        if stacking == "ABC":
            a = [1,3,2] #coordenada x (a)
            b = [2,0,1] #coordenada y (b)
        elif stacking == "ABA":
            a = [1,0] #coordenada x (a)
            b = [2,0] #coordenada y (b)
        den = n*do+v+2*shift

        j = 0 #iterable de valores a, b
        M, X, T = [], [], [] #listas donde iran las posiciones de los átomos de M y de X y T.
        zero = [0,0,0+shift/(n*do+v+2*shift)]
        zero = [format(i,f) for i in zero]
        M.append(zero) #El primer átomo de M se coloca en el centro (0,0,0)

        for i in range(n): #por cada capa 

            if stacking == "ABA": j=0

            #Coordenadas del Metal (M)
            aM = format(round(a[j-1]/3,15),f)
            bM = format(round(b[j-1]/3,15),f)
            cM = format(round((do*(i+1) + shift)/(n*do + v + 2*shift), 15),f)
            posM = [aM,bM,cM]
            M.append(posM)

            #Coordenadas del C o N (X)
            aX = format(round(a[j]/3,15),f)
            bX = format(round(b[j]/3,15),f)
            cX = format(round((do/2*(2*(i+1)-1) + shift)/(n*do + v + 2*shift), 15),f)
            posX = [aX,bX,cX]
            X.append(posX)         

            j += 1 #Para que se repita la lista a y b.
            if j == 3: j = 0

        if self.terminal:
            if hollows == "HM": #en HM (modelo 2)
                a=[2,3]; b=[1,0]
            if hollows == "HX": #en HM (modelo 4)
                a=[1,1]; b=[2,2]
            if hollows == "HMX": #en HM (modelo 3)
                a=[2,1]; b=[1,2]

            #Coordenadas de Terminales (T) 
            for i in range(2):
                if n == 1: a=[2,3]; b=[1,0] #en HM (modelo 2)
                if n == 2: a=[1,3]; b=[2,0] #modelo 4
                if n >= 3: pass

                aT = format(round(a[i]/3,15),f)
                bT = format(round(b[i]/3,15),f)
                cT = format(round(i*(n*do+2*shift)/(n*do+v+2*shift),15),f)
                posT = [aT,bT,cT]
                T.append(posT)
            
        return M, X, T        

    def POSCAR(self): #ab=3, do=2.5, v=10, lp=1
        """Crea el fichero POSCAR inicial para un MXene. A partir de sus átomos y su n.\n
        Contiene nombre, parámetros celda y posiciones átomos.\n
        Se puede especificar parámetros celda (a=b, ab), distancia capa (do), vacio(v) y lattice parameter (lp).\n
        Por defecto ab=3 do=2.5 v=10 lp=1."""

        n = self.n
        do,v = self.do,self.v
        ab = self.ab
        lp = self.lp
        shift = self.shift

        f1 = ".10f"
        
        #Cálculos de parámetros de celda
        lp = format(lp,".14f")
        a = [format(ab,f1), format(0,f1), format(0,f1)]                                                     #(ab,0,0)
        b = [format(round(-ab*m.sin(m.pi/6),10),f1), format(round(ab*m.cos(m.pi/6),10)), format(0,f1)]      #(-ab*sin(30),ab*cos(30),0)
        c = [format(0,f1), format(0,f1), format(n*do+v+2*shift,f1)]                                                 #(0,0,n*do+v)

        #Lineas de atomos y índices
        strAtoms = "".join([a + " " for a in self.atoms])
        strIndex = "".join([str(i) + " " for i in self.index])
        
        #Lineas de posiciones de átomos
        posM, posX, posT = self.positions() #positions(self.n,do,v)
        p = ""
        for pos in posM:
            p += f"  {pos[0]}  {pos[1]}  {pos[2]}  T T T\n" #podria ponerse el primer M como FFF?
        for pos in posX:
            p += f"  {pos[0]}  {pos[1]}  {pos[2]}  T T T\n"
        if self.terminal:
            for pos in posT:
                p += f"  {pos[0]}  {pos[1]}  {pos[2]}  T T T\n"

        #Escribe todo en el POSCAR, con el formato de always
        for dir in self.dirs:
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
        """Crea el fichero POSCAR con los PP de los átomos del MXene concatenados."""

        with open(self.pdir + "POTCAR", 'w') as outfile:
                    first = True
                    for at in self.atoms: #por cada atomo de la lista
                        
                        for p in self.pp: #para cojer el pp adecuado
                            if self.atoms[0] in p and first: #Si es la primera vez y el atomo esta en la lista pp
                                file = p
                                first = False
                                break
                            else: file = at #sino coje el normal

                        with open("./PP/{}/POTCAR".format(file), "r") as infile:
                            for line in infile:
                                outfile.write(line)

        #Envia el fichero a las carpetas siguientes de cellOpt y DOS.
        source = self.pdir + "POTCAR"
        for dir in self.dirs:
            shutil.copy(source,dir)
        
    def KPOINTS(self,p1=7,p2=7,p3=1):
        """Crea el fichero KPOINTS con los puntos-k indicados.\n
        Por defecto, los puntos son  7  7  1."""

        with open(self.pdir + "KPOINTS", 'w') as outfile:
            with open("./car/KPOINTS", 'r') as infile:
                n = 1
                for line in infile:
                    if n == 4:
                        line = f" {p1}  {p2}  {p3}\n"
                    outfile.write(line)
                    n += 1
        
        #Envia el fichero a las carpetas siguientes de cellOpt y DOS.
        source = self.pdir + "KPOINTS"
        source2 = "./car/KPOINTS3"
        for dir in self.dirs:
            if dir.endswith("BS2/"): shutil.copy(source2,dir+"KPOINTS")
            else: shutil.copy(source,dir)

    def INCAR(self,style=1,**kwargs):
        """Crea el fichero INCAR para un MXene.\n
        Acepta parametros con valores del estilo: param = value."""

        # params = [key for key in kwargs.keys()] #Parámetro
        # values = [val for val in kwargs.values()] #Valor de parámetro
        
        for dir in self.dirs: #que parametros pone en el incar segun el cálculo
            params,values = [],[]
            if "isif3" in dir:
                params.append("ISIF"); values.append("3")
            if "isif4" in dir:
                params.append("ISIF"); values.append("4")
            if "isif27" in dir:
                params.append("ISIF"); values.append("2")
            if "DOS" in dir or "BS" in dir:
                params.append("IBRION"); values.append("-1")
                params.append("NSW"); values.append("0")
            if "DOS" in dir: 
                params.append("ISMEAR"); values.append("-5")
                params.append("LORBIT"); values.append("11")
                params.append("EMIN"); values.append("-10")
                params.append("EMAX"); values.append("10")
                params.append("NEDOS"); values.append("9999")
            if "BS1" in dir or "BS/PBE" in dir: pass
            if "BS2" in dir: 
                params.append("ICHARG"); values.append("11")
                params.append("LORBIT"); values.append("11")
            if "PBE0" in dir: 
                params.append("IALGO"); values.append("58")
                params.append("LHFCALC"); values.append(".TRUE.")


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
    
    def script(self):
        source = "./car/script"
        destination1 = self.pdir
        shutil.copy(source, destination1)
        for dir in self.dirs:
            shutil.copy(source,dir)


### ----------------------------------------- INICIO PROGRAMA ---------------------------------------------------- ###
###--------------------------------------------------------------------------------------------------------------- ###

#Lista con maxenos a estudiar. Deben incluir subindice TODOS los átomos! (Ti2C2O2H2 == Ti2C2(OH)2)
# mx = ["Ti2C1O2","Sc2C1O2","Y2C1O2","Zr2C1O2","Hf2C1O2","V2C1O2","Nb2C1O2","Ta2C1O2","Cr2C1O2","Mo2C1O2","W2C1O2",
#    "Ti2N1O2","Sc2N1O2","Y2N1O2","Zr2N1O2","Hf2N1O2","V2N1O2","Nb2N1O2","Ta2N1O2","Cr2N1O2","Mo2N1O2","W2N1O2"]

mx = ["Ti2C1","Sc2C1","Y2C1","Zr2C1","Hf2C1","V2C1","Nb2C1","Ta2C1","Cr2C1","Mo2C1","W2C1",
    "Ti2N1","Sc2N1","Y2N1","Zr2N1","Hf2N1","V2N1","Nb2N1","Ta2N1","Cr2N1","Mo2N1","W2N1"]
T = "O2"

mx = [i + T for i in mx]
lenMX = len(mx)

MXenes = [MX(mx[i]) for i in range(lenMX)]

if __name__ == "__main__":
    #Crea carpeta de MXenes
    cwd = os.getcwd()
    try: os.mkdir("MXenes") 
    except FileExistsError: pass

    #Genera los 4 archivos input + script
    for mx in MXenes: #para cada compuesto MXene de la lista

        #Crea directorios-subdirectorios
        try: os.mkdir(mx.pdir) #Carpeta con nombre del Mxene
        except FileExistsError: pass
        for dir in mx.dirs:
            try: os.mkdir(dir)
            except FileExistsError: pass


        #Cambios de los parámetros de mx han de ser aqui!

        #mx.POSCAR()  #Escribe archivo POSCAR
        mx.POTCAR()   #Coje los archivos POTCAR de la base PP y los concatena para cada compuetso    
        mx.KPOINTS()  #Escribe archivo KPOINTS
        mx.INCAR()    #Escribe archivo INCAR
        mx.script()   #Copia el script en la carpeta
