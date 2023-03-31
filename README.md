# VASP - MXenes scripts
Python scripts used for my chemistry final degree thesis [_Bandgap Engineering on MXene Compounds by Structure, Composition, and Surface Termination_](http://hdl.handle.net/2445/189371) and subsequent masters degree work. Created to ease and automate the project by making it more efficient. 

The scripts are divided into 3 parts:

- [General Workflow](#general-workflow): Scripts to create the input data, optimize the structures, calculate and analyze the results in batches and heavyly automatized.

- [File management](#file-management): Scripts for managin and analyze output files, search through the paths, etc.

- [Graphic Representation](#graphic-representation): Scripts to visualize DOSCAR and LOCPOT files.

<br>

## General Workflow

These scripts follow the general workflow that I as a researcher would use for calculating the electronic properties (DOS and Band Structure) of different compounds, here focused on MXenes ($M_{n+1}X_nT_2$):

1. Generate the input files:

Here, the file `VASP.py` is used. Its main purpuse is [VASP](https://www.vasp.at/) input file management, it generates a tree of folders for a given MXene width $n$ and termination $T_x$, considering stackings ($ABC$ and $ABA$) and termination hollow position ($H_M$, $H_{MX}$ and $H_X$ for $ABC$,  and $H$, $H_{MX}$ and $H_X$ for $ABA$), and containing each folder different subfolders for the calculations needed (optimization opt/, density of states DOS/, band structures BS/, and workfunction WF/). Each subfolder has its necessary files (INCAR, POTCAR, KPOINTS, script and POSCAR), which the right parameters for the given MXene and calculation case. Moreover, it also has the principal MXene class, `MX()`, that contains the MXene information (n, atoms, indices, termination, name,...), which is used by other scripts.

To create the folders for pristine MXenes with $n=2$, simply set $n=2$ and $T=""$ in the code and run the script. The tree of folders will be generated in a MXenes/ folder, which can be send to the cluster (or generated righ there)

2. Optimize:

For pristine and terminated MXenes, an initial POSCAR file is generated in the `opt/` folder. For pristine MXenes, it is a good starting point, but for the terminated ones, is better to use the optimized pristine structure and add the termination to the hollows, and use that as the initial geometry. For that, the `searcher.py` script (more in depth later) has a function that allows to automatically take the already optimized pristine CONTCARS, add the specified termination (using the `structure.py` script) and place it in the right terminated MXene folder as the initial POSCAR.

Once the right POSCAR is in each MXene `opt/` folder, the optimization of the structures can be done automatically with the `opt.py` and `optimizer.py` script. 

The `optimizer.py` script is essentialy a bot that takes a path as an argument, moves to the path, and starts performing optimization calculations until the geometry is optimized. It sends a calculation to queue, waits until finished, reads the OUTCAR (with `VASPread.py`) and decides what to do next, and iterates between isif2 and isif7 until the forces and pressure of the cell are optimized. Finally, once optimized, appends the energy to an `energy.dat` file and the lattice parameter and width to a `geom.dat` file, both created in the home directoy. Being slab models, isif3 calculations tend reduce the vacuum, so a combination of isif2 and isif7 has better results in general. This scripts can also handle non-converged calculations or EDDDAV error cases.

The `opt.py` script is just a sender of `optimizer.py`. It runs the `optimizer.py` script for all the MXene cases for a given $n$ and $T$ (44 for pristine and 132 for terminated) in the background and in parallel as an independent job using the nohup command. This allows to automatically have a swarm of "bots" sending optimization calculations and optimizing the structures at the same time for all cases at once, and gathering their optimized energies and geometries. Much more easy and fun than doing it manually one by one...

Once optimized, the optimized CONTCAR and OUTCAR are placed in the parent folder of each MXene structure, to be ready for subsequent electronic calculations. 

## Graphic Representation

## File Management

## Details:
The file `DOS.py` reads all the spin-polarized DOSCAR files in the input folder, `/DOsin` and generates the Total, atom or orbital Projected DOS plot images in a output file, `/DOSout`. It also returns the bandgap information (E<sub>g</sub>, VBM, CBM). This script is optimized for pristine and terminated MXenes (_M<sub>n+1</sub>X<sub>n</sub>T<sub>2</sub>_). The script assumes M > X > T as the input order of atoms.

The file `LOCPOT.py` reads all the LOCPOT files in the input folder `/WFin` or a LOCPOT file in the current folder and generates a local potential plot along the vacuum direction of the MXene slab (_z_) in an output file, `/WFout`. It also returns the vacuum energy _V<sub>vacuum</sub>_.

The file `structure.py` has different functions that allow the modification and analysis of POSCAR/CONTCAR files, for example to shift the atoms to the origin after an optimization, to add a certain amount of vacuum and rescale the atom fractional coordinates, or to add the Oxygen termination to the different hollow sites in the pristine MXene optimized CONTCAR. It also reads POSCAR/CONTCAR files and return the cell parameter _a_ and width _d_. Reads the input files in `/CONTCARin` and returns the modified files in `/CONTCARout`.

The file `VASP.py` is mainly for [VASP](https://www.vasp.at/) input file management, it generates the indicated specific folders containing the necessary input files for the different VASP calculations. It also has the principal MXene class, `MX()`, that contains the MXene information (n, atoms, indices, termination, name,...)

The `/PP` folder contains the pseudopotentials (POTCAR) files for each atom, from where the POTCAR file of the structure will be created. The `/car` folder has different input files models. Both are used by the `VASP.py` script for creating the input files.
