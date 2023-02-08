import os
import shutil
# import numpy as np

def pathify(*args):
    path = "./"
    for s in args:
        path += s + "/"

    return path

def loadtxt(path,skiprows,maxiter=None):

    data = []
    with open(path,"r") as inFile:
        if maxiter == None: maxiter= len(inFile)
        for i,line in enumerate(inFile):
            if i >= skiprows and i <skiprows+maxiter:
                line = line.strip().split()
                data.append(line)
    return data

def column(data,col):
    return [d[col] for d in data]


M = "Cr,Hf,Mo,Nb,Sc,Ta,Ti,V,W,Y,Zr"
M = M.split(",")
m2xo2,m2x = [],[]                     # Lista con nombres mxene en orden
for i,m in enumerate(M):
    m2xo2.append(M[i]+"2CO2")
    m2xo2.append(M[i]+"2NO2")
    m2x.append(M[i]+"2C")
    m2x.append(M[i]+"2N")

# Listas con directorios 
m2x = m2x
m2xo2 = m2xo2
stacking = ["ABA","ABC"]
hABA = ["H","HMX","HX"]
hABC = ["HM","HMX","HX"]
hollows = [hABA,hABC]



def search_M2XO2():
    target = "DOS/PBE0/DOSCAR"
    target2 = "DOS/PBE0/DOSCAR"
    save_name = "DOSCAR"

    new_folders = ["ABA H","ABA HX","ABA HMX","ABC HM","ABC HMX","ABC HX"]
    for f in new_folders:
        try: os.mkdir(f)
        except FileExistsError: pass

    charges = []

    n_contcarF = 0
    n_total,n_correct,n_incorrect = 0,0,0
    for i,folder in enumerate(m2x):
            for j,stack in enumerate(stacking): 
                for h in hollows[j]:

                    folder_to_save = f"{stack} {h}"
                    name_to_save = f"{save_name} {m2xo2[i]}"
                    destination = pathify(folder_to_save) + name_to_save
                    
                    try:
                        path = pathify(folder,m2xo2[i]) + f"{stack}" + f"/{h}/" + target
                        # path2 = pathify(folder,m2xo2[i]) + f"{stack}" + f"/{h}/" + target2


                        # data = column((loadtxt(path,skiprows=3)),5) # Bader charges
                        # print(f"{m2xo2[i]}_{stack}_{h}",*data)
                        # data_str = [str(d) for d in data]
                        # charges.append([f"{m2xo2[i]}_{stack}_{h}",*data_str])

                        # ef = column((loadtxt(path,skiprows=5,maxiter=1)),3) # Fermi level WF
                        # print(f"{m2xo2[i]}_{stack}_{h}",*ef)
                        
                        
                        print(path)

                        shutil.copy(path,destination)
                        # shutil.copy(path2,destination)
                        n_correct += 1

                    except FileNotFoundError: 
                        try: 
                            path = pathify(folder,m2xo2[i]) + f"{stack}" + f"/{h}/" + target+"f"
                            shutil.copy(path,destination)
                            print("Correct f")
                            n_correct += 1
                            n_contcarF +=1
                        except FileNotFoundError:
                            n_incorrect +=1
                            # print(f"FileNotFound for: {m2xo2[i]} {stack} {h}")
                            pass

                    n_total += 1
                    # print(path)
                    # print(destination)
                    
    print("Total :",n_total)
    print("Correct founds :",n_correct)
    print("Inorrect founds :",n_incorrect)

    # out_file = "charges"
    # with open(out_file,"w") as outFile:
    #     for line in charges:
    #         outFile.write(" ".join(line) + "\n")
    
def search_M2X():
    
    target = "/DOS/DOSCAR"
    target2 = "/DOS/ismear5/DOSCAR"
    save_name = "DOSCAR"

    new_folders = ["ABA","ABC"]
    for f in new_folders:
        try: os.mkdir(f)
        except FileExistsError: pass

    n_contcarF = 0
    n_total,n_correct,n_incorrect = 0,0,0
    for i,folder in enumerate(m2x):
        for j,stack in enumerate(stacking):
            folder_to_save = stack
            name_to_save = f"{save_name} {folder}"
            destination = pathify(folder_to_save) + name_to_save

            path_folder = pathify(folder) + stack
            path_dos = path_folder + "/DOS/"
            try:
                files_dos = os.listdir(path_dos)
                if "ismear5" in files_dos:
                    path = path_folder + target2
                else:
                    path = path_folder + target

                shutil.copy(path,destination)
                n_correct += 1
            except FileNotFoundError:
                n_incorrect +=1
                print(f"FileNotFound for: {folder} {stack}")
                pass
            
            n_total += 1
    
    print("Total :",n_total)
    print("Correct founds :",n_correct)
    print("Inorrect founds :",n_incorrect)

search_M2XO2()



