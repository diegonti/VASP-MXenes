# MXenes
Python scripts used for my chemistry final degree thesis "Bandgap Engineering on MXene Compounds by Structure, Composition, and Surface Termination."
Created to ease and automate the project by making it more efficient. Scripts include DOSCAR and LOCPOT files visualization, VASP input file management and POSCAR/CONTCAR modification and analysis.

## Details:
The file `DOS.py` reads all the spin-polarized DOSCAR files in a input folder, `/DOsin` and generates the Total, atom or orbital Projected DOS plot images in a output file, `/DOSout`. It returns also the bandgap information (E<sub>g</sub>, VBM, CBM). use only for pristine and terminated MXenes with n=1 (M2XT2).
