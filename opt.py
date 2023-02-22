import os

# M = "Cr,Hf,Mo,Nb,Sc,Ta,Ti,V,W,Y,Zr"
# M = M.split(",")
# m2xo2,m2x = [],[]
# for i,m in enumerate(M):
#     m2xo2.append(M[i]+"2CO2")
#     m2xo2.append(M[i]+"2NO2")
#     m2x.append(M[i]+"2C")
#     m2x.append(M[i]+"2N")

# INPUTS
n = 2                               # MXene n number (thickness)
T = "O2"                            # Termination

# MXene cases
M = ["Sc","Y","Ti","Zr","Hf","V","Nb","Ta","Cr","Mo","W"]
mc = [m + str(n+1) + "C" + str(n) for m in M]   # X = C cases
mn = [m + str(n+1) + "N" + str(n) for m in M]   # X = N cases
MX = mc + mn                                    # All studied MXenes (pristine)
MXT = [i + T for i in MX if i != ""]            # All studied MXenes (temrinated)

# Structure cases
stacking = ["ABA","ABC"]
hABA = ["H","HMX","HX"]
hABC = ["HM","HMX","HX"]
hollows = [hABA,hABC]

home = os.path.expanduser("~")

# For Terminated cases
for mx,mxt in zip(MX,MXT):
    for j,stack in enumerate(stacking):
        for hollow in hollows[j]:
            path = f"{home}/M{n+1}X{n}/{mx}/{mxt}/{stack}/{hollow}/"
        
# For pristine cases
for mx in MX:
    for stack in stacking:
            path = f"{home}/M{n+1}X{n}/{mx}/{stack}/"