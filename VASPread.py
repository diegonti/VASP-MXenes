"""
General VASP parser. Quickly gets information from an OUTCAR file.
Implemented now for OUTCAR files. (CONTCAR in structure.py)

Diego Ontiveros
"""


class OUTCAR():
    def __init__(self,path) -> None:
        """
        Creates OUTCAR object. Allows to quickly get the important information of the OUTCAR.
        `path` : path to the OUTCAR file."""

        self.path = path
        self.data,self.raw_data = self.getData()


    def getData(self):
        """Reads the OUTCAR and returns an out list of the 
        raw lines (raw_data) and the .strip().split() lines (data). """

        data = []
        with open(self.path,"r") as inFile:
            raw_data = inFile.readlines()
            inFile.seek(0)
            for line in inFile:
                line = line.strip().split()
                data.append(line)

        self.data, self.raw_data = data, raw_data
        return data, raw_data
    

    def search(self,target:str,
               after:int=None,
               before:int=None,
               until:str=None,
               repeat:bool=True):
        """Searched for a target in a VASP OUTCAR file.

        Parameters
        ----------
        `target` : String with the desired info to search.
        `after` : Number of lines to add after tehe target. Defaults to 0.
        `before` : Number of lines to add before the target. Defaults to 0.
        `until` : Add lines until another target. Defaults to None
        `repeat`: Allows repeated search. Defaults to True.

        Returns
        -------
        `out` : Targeted lines (with .strip().split())
        `out_raw`: Targeted lines (raw)
        """
        # Selecting default cases
        if before is None: before = 0
        if after is None: after = 0
        if until is None: search_until = False
        else: search_until = True
        found = False
        
        # Main search loop
        out, out_raw = [],[]
        i_line,i_until = [],[]
        for i,line in enumerate(self.raw_data):

            # Save line number when the target is found
            if target in line and not found:
                found = True
                i_line.append(i)

            # Continuation for each search case
            if found and not search_until and not repeat: 
                i_until.append(i_line[-1])
                break
            elif found and not search_until and repeat: 
                found = False
                i_until.append(i_line[-1])
            elif found and search_until:
                if until in line:
                    found = False
                    i_until.append(i)
                    
                    if not repeat: break
                    elif repeat: continue

        # Selecting the pieces of data to gather
        for i,j in zip(i_line,i_until):
            dat = self.data[i-before:j+after+1] 
            raw_dat = self.raw_data[i-before:j+after+1]
            out.append(dat)
            out_raw.append(raw_dat)
        
        if out == []: print(f"Target '{target}' not found. Path: {path}")

        return out, out_raw
    

    def getOpt(self,print_info=False):
        """Gets the optimization data (external pressure and forces) from the OUTCAR file.
        Also, returns the next step of the optimization (if not finished).
        
        Returns
        ---------
        `pressures` : List with the external pressures of each optimization step.
        `forces` : List of the forces of the last optimization step.
        `last_pressure` : External pressure of the last step.
        `next_optimize` : Optimization type to do next (isif2 or isif7). "optimized" if all optimized.  
        """
        # Getting external pressure and forces data
        pressure, pressure_raw = self.search("external pressure")
        force, force_raw = self.search("TOTAL-FORCE",until="total drift")

        # Creating list of pressures
        pressures = []
        for p in pressure:
            pi = float(p[0][3])
            pressures.append(pi)

        # Creating list of forces
        forces = []
        for f in force[-1][2:-2]:
            fi = float(f[-1])
            forces.append(fi)

        # Getting absolute values
        pressures_abs = [abs(p) for p in pressures]
        forces_abs = [abs(f) for f in forces]
        forces_max = [f for f in forces_abs if f>0.01]
        last_pressure = pressures[-1]

        # Optimization criteria
        pressure_optimized = abs(last_pressure) <= 1.00
        forces_optimized = len(forces_max) == 0
        repeat_isif7 = abs(last_pressure)>abs(pressures[-2])<0.2

        # Optimization results depending on each case
        next_optimize = ""
        if pressure_optimized: 
            if print_info: print("\u2713 Pressure optimized.")
        elif repeat_isif7:
            next_optimize = "isif7a"
            if print_info: print("\u2717 Redoing isif7.")
        else: 
            next_optimize = "isif7"
            if print_info: print("\u2717 Pressure NOT optimized. Try isif7.")

        if forces_optimized: 
            if print_info: print("\u2713 Forces optimized.")
        else: 
            next_optimize = "isif2"
            if print_info: print("\u2717 Forces NOT optimized. Try isif2.")

        if not pressure_optimized and not forces_optimized:
            next_optimize = "Random"

        if next_optimize == "": next_optimize = "optimized"

        if print_info:
            print("Pressures (kB):\n", pressures)
            print("Forces (eV/Ang):\n", forces)

        return pressures, forces, last_pressure, next_optimize

    def getEnergy(self):
        """Gets the energies (E0) for each optimization step.
        `final_energy` is the optimized one, while all the energies are found in `energies`.
        """
        energies, energies_raw = self.search("energy(sigma->0)")

        energies = [float(e[0][-1]) for e in energies]
        final_energy = energies[-1]

        return final_energy, energies
        

############################## MAIN PROGRAM #######################

if __name__ == "__main__":
    path = "./car/OUTCAR"

    outcar = OUTCAR(path)
    final_energy,energies = outcar.getEnergy()
    pressures, forces, last_pressure, next_optimize = outcar.getOpt()




