# VASP - MXenes scripts
Python scripts used for my chemistry final degree thesis [_Bandgap Engineering on MXene Compounds by Structure, Composition, and Surface Termination_](http://hdl.handle.net/2445/189371) and subsequent masters degree work. Created to ease and automate the project for making it more efficient. The following are a group of scripts that allow to work with the VASP program in a more batched way, generating, sending calculations and analyzing, not just one by one (boring) but in high amounts of cases at the same time. As a lazy guy myself, it's better if a program can do it for you...

The scripts are divided into 3 parts:

- [General Workflow](#general-workflow): Scripts to create the input data, optimize the structures, calculate and analyze the results in batches and heavily automatized.

- [File management](#file-management): Scripts for managin and analyze output files, search through the paths, etc.

- [Graphic Representation](#graphic-representation): Scripts to visualize DOSCAR and LOCPOT files.


In here you will find also some [Utilities](#utilities), (PP/ and car/) folders, that contain data files and templates needed for the scripts.

Finally, for any doubts or concerns go to the [Help](#help) section.

<br>
<p align="center">
<img src="car/graphical_abstract%20(v4).png" alt= "MXene Photocatalytic Water Splitting" width=600>
</p>
<br>


## General Workflow

These scripts follow the general workflow that I as a researcher would use for calculating the electronic properties (DOS and Band Structure) of different compounds, here focused on MXenes ($M_{n+1}X_nT_2$): <br><br>

- ### 1. Generate input files:

Here, the file `VASP.py` is used. Its main purpuse is [VASP](https://www.vasp.at/) input file management, it generates a tree of folders for a given MXene width $n$ and termination $T_x$, considering stackings ($ABC$ and $ABA$) and termination hollow position ($H_M$, $H_{MX}$ and $H_X$ for $ABC$,  and $H$, $H_{MX}$ and $H_X$ for $ABA$), and containing each folder different subfolders for the calculations needed (optimization opt/, density of states DOS/, band structures BS/, and workfunction WF/). Each subfolder has its necessary files (INCAR, POTCAR, KPOINTS, script and POSCAR), which the right parameters for the given MXene and calculation case. Moreover, it also has the principal MXene class, `MX()`, that contains the MXene information (n, atoms, indices, termination, name,...), which is used by other scripts.

To create the folders for pristine MXenes with $n=2$, simply set $n=2$ and $T=""$ in the code and run the script. The tree of folders will be generated in a MXenes/ folder, which can be send to the cluster (or generated righ there).
<br><br>

- ### 2. Optimize:

For pristine and terminated MXenes, an initial POSCAR file is generated in the `opt/` folder. For pristine MXenes, it is a good starting point, but for the terminated ones, is better to use the optimized pristine structure and add the termination to the hollows, and use that as the initial geometry. For that, the `searcher.py` script (more in depth later) has a function that allows to automatically take the already optimized pristine CONTCARS, add the specified termination (using the `structure.py` script) and place it in the right terminated MXene folder as the initial POSCAR.

Once the right POSCAR is in each MXene `opt/` folder, the optimization of the structures can be done automatically with the `opt.py` and `optimizer.py` script. 

The `optimizer.py` script is essentialy a bot that takes a path as an argument, moves to the path, and starts performing optimization calculations until the geometry is optimized. It sends a calculation to queue, waits until finished, reads the OUTCAR (with `VASPread.py`) and decides what to do next, and iterates between isif2 and isif7 until the forces and pressure of the cell are optimized. Finally, once optimized, appends the energy to an `energy.dat` file and the lattice parameter and width to a `geom.dat` file, both created in the home directoy. Being slab models, isif3 calculations tend reduce the vacuum, so a combination of isif2 and isif7 has better results in general. This scripts can also handle non-converged calculations or EDDDAV error cases.

The `opt.py` script is just a sender of `optimizer.py`. It runs the `optimizer.py` script for all the MXene cases for a given $n$ and $T$ (44 for pristine and 132 for terminated) in the background and in parallel as an independent job using the nohup command. This allows to automatically have a swarm of "bots" sending optimization calculations and optimizing the structures at the same time for all cases at once, and gathering their optimized energies and geometries. Much more easy and fun than doing it manually one by one...

You can optimize a full batch of MXenes for a given $n$ and $T$ by running:
```
$ python3 opt.py -n N_INDEX [-T TERMINATION] 
```

Once optimized, the optimized CONTCAR and OUTCAR are placed in the parent folder of each MXene structure, to be ready for subsequent electronic calculations. 
<br><br>

- ### 3. Calculate 

With the optimized geometries, DOS and BS calculations can be send with the `calculate.py` script, which moves over all the tree subfolders of the specified $n$ and $T$ and sends PBE and PBE0 BS and DOS calculations (each calculation has its own subfolder, as generated with the `VASP.py` script).

To send to calculate a full batch of MXenes for a given $n$ and $T$, run:
```
$ python3 calculate.py -n N_INDEX [-T TERMINATION] 
```
OR, it you want to send calculations for a specific MXene case, run:
```
$ python3 calculate.py -p PATH
```
If both -n and -p falgs are used. The -p one has preference.
<br><br>

- ### 4. Analyze

Once the DOSCAR files are generated in the last step. They can be analyzed with the `analyzer.py` script, which uses a target to search for the PBE (target = dos) or PBE0 (target = dos0) DOSCAR files . Again, the script runs over all paths for a given $n$ and $T$, and uses the `DOS.py` script to make a plot of the DOS, which is placed in its correspondent folder (depending on stacking and hollows) in the home directoy, and to compute the bandgap ($E_g$), $VBM$ and $CBM$, which can be appended to a specific file. The before mentioned can be done in the background with the following command:

```
$ nohup python3 analyzer.py > output_filename.dat &
```
Note that in many cases, generating that many number of plots needs a lot of memory and the process can be killed by the system. If that happens, try to modify the code by doing only ABC or ABA strucutres at a time.
<br><br>

And with this four steps, the road for calculating a group of MXenes is done! With a large HPC cluster, all the data for all the structures of a terminated MXene with its 3 widths can be generated in a few days!
<br><br>


## File Management

Several scripts have been developed for managin and analyzing VASP output files and navigating through the paths tree in an easier way:

The `searcher.py` script is a general path searcher for the cluster folders. It searches in a tree-style path structure such as the one given by the `VASP.py` file generator. It has different internal functions that allow several tasks, such as:
1. Given a $n$ and $T$, and a target (DOSCAR, CONTCAR, etc), searches for that target in the list of all possible paths for all MXene cases for that $n$ and $T$, and counts how many files are found. If any is not found, returns where it's missing.
2. Move CONTCARS from pristine MXenes to its corresponent terminated one, with the specified termination.
3. Removes the specified files (e.g. 'CHG*') for a specified $n$ and $T$ batch of MXenes.

To run the desired task, modify the main part of the code.

The `VASPRead.py` script quickly gets information from an OUTCAR file. It has a general file searcher and functions to get the optimization information (OUTCAR.getOpt()) and energies (OUTCAR.getEnergy()). It is used internally by the `optimizer.py` script, to analyze the OUTCAR and decide the next step of the optimization.

The `structure.py` script has different functions that allow the modification and analysis of POSCAR/CONTCAR files, for example:
1. To shift the atoms to the origin after an optimization (or any amount). CONTCAR.toZero() and CONTCAR.shift()
2. To add a certain amount of vacuum and rescale the atom fractional coordinates. CONTCAR.addVaccum(v)
3. To add a termination to the different hollow sites in the pristine MXene optimized CONTCAR. CONTCAR.addT(T,stack,hollow)
4. To read POSCAR/CONTCAR files and return the cell parameter $a$ and width $d$. CONTCAR.getGeom()

It is internally used by the `optimizer.py` and `searcher.py` scripts.
<br><br>


## Graphic Representation

To create plots of the data, two scripts have been developed:

The `DOS.py` file reads a given spin- or non-spin- polarized DOSCAR file and generates the Total, atom or orbital Projected DOS plot images in the specified output path. It also returns the bandgap information ($E_g$, Valence Band Minimum $VBM$ and Condunction Band Minimum $CBM$). This script is optimized for pristine and terminated MXenes ($M_{n+1}X_nT_2$), and assumes M > X > T as the input order of the atoms (which is the order given in the input files by the `VASP.py` script).

The `LOCPOT.py` file reads a given LOCPOT file (or searches for one in the current folder) and generates a local potential plot along the vacuum direction of the MXene slab ($z$) in an output file. It also returns the vacuum energy $V_{vaccum}$ or energies if its a Janus material.

The avobe scripts are used internally by the scripts in the general workflow, mainly in `analyzer.py`.
<br><br>


## Utilities 

The `/PP` folder contains the pseudopotentials (POTCAR) files for each atom, from where the POTCAR file of the structure will be created. The `/car` folder has different input files models. Both are used by the `VASP.py` script for creating the input files.
<br><br>


## Help

In many cases, the scripts themnselves are well documented and will have a header of explanation and usage. The General Workflow scripts, have a [-h] and [--help] flag that indicates also usage and flags.

Take in mind that this are script developed by a learning master student (myself), and may not serve for general pourpuse calculations.

For any doubts or questions, contact [Diego Ontiveros](https://github.com/diegonti) ([Mail](mailto:diegonti.doc@gmail.com)).

<br><br>
