import os 

target = "./ABA H/"

dirs = os.listdir()
dirs.remove("names.py")

print(dirs)

M = "Cr,Hf,Mo,Nb,Sc,Ta,Ti,V,W,Y,Zr"
M = M.split(",")
mxenes = []
for i,m in enumerate(M):
    mxenes.append(M[i]+"2CO2")
    mxenes.append(M[i]+"2NO2")

dirs2 = os.listdir(target)
for i,c in enumerate(dirs2):
    path = target+c
    print(path)
    os.rename(target+c,target+mxenes[i])