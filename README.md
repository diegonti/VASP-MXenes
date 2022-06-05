# MXenes
Python scripts used for my chemistry final degree thesis "Bandgap Engineering on MXene Compounds by Structure, Composition, and Surface Termination."
Created to ease and automate the project by making it more efficient. Scripts include DOSCAR and LOCPOT files visualization, VASP input file management and POSCAR/CONTCAR modification and analysis.

## Details:
The file `DOS.py` reads all the spin-polarized DOSCAR files in the input folder, `/DOsin` and generates the Total, atom or orbital Projected DOS plot images in a output file, `/DOSout`. It also returns the bandgap information (E<sub>g</sub>, VBM, CBM). This script is optimized for pristine and terminated MXenes (M<sub>n+1</sub>X<sub>n</sub>T<sub>2</sub>).
The file `LOCPOT.py` reads all the LOCPOT files in the input folder `/WFin` or a LOCPOT file in the current folder and generates a local potential plot along the vacuum direction of the MXene slab (*z*). It also reutrns the vacuum energy *V<sub>vacuum</sub>*
