# MXenes
Python scripts used for my chemistry final degree thesis "Bandgap Engineering on MXene Compounds by Structure, Composition, and Surface Termination."
Created to ease and automate the project by making it more efficient. Scripts include DOSCAR and LOCPOT files visualization, VASP input file management and POSCAR/CONTCAR modification and analysis.

## Details:
The file `DOS.py` reads all the spin-polarized DOSCAR files in the input folder, `/DOsin` and generates the Total, atom or orbital Projected DOS plot images in a output file, `/DOSout`. It also returns the bandgap information (E<sub>g</sub>, VBM, CBM). This script is optimized for pristine and terminated MXenes (_M<sub>n+1</sub>X<sub>n</sub>T<sub>2</sub>_). The script assumes M > X > T as the input order of atoms.

The file `LOCPOT.py` reads all the LOCPOT files in the input folder `/WFin` or a LOCPOT file in the current folder and generates a local potential plot along the vacuum direction of the MXene slab (_z_) in an output file, `/WFout`. It also returns the vacuum energy _V<sub>vacuum</sub>_.

The file `structure.py` has different functions that allow the modification and analysis of POSCAR/CONTCAR files, for example to shift the atoms to the origin after an optimization, to add a certain amount of vacuum and rescale the atom fractional coordinates, or to add the Oxygen termination to the different hollow sites in the pristine MXene optimized CONTCAR. It also reads POSCAR/CONTCAR files and return the cell parameter _a_ and width _d_. Reads the input files in `/CONTCARin` and returns the modified files in `/CONTCARout`.

The file `VASP.py` is mainly for [VASP](https://www.vasp.at/) input file management, it generates the indicated specific folders containing the necessary input files for the different VASP calculations. It also has the principal MXene class, `MX()`, that contains the MXene information (n, atoms, indices, termination, name,...)

The `/PP` folder contains the pseudopotentials (POTCAR) files for each atom. The `/car` folder has different input files models. Both are used by the `VASP.py` script for creating the input files.
