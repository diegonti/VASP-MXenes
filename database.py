"""
Collects structural and electronic data from all calculations performed following the general workflow
and saves it to a database file.

Diego Ontiveros
"""

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import gc
from pymatgen.core import periodic_table
import numpy as np
from argparse import ArgumentParser

from searcher import SEARCH
from structure import CONTCAR
from DOS import DOSCAR
from VASP import MX


def make_histogram(E,DOS:np.ndarray,n_bins=100,E_min=-5,E_max=5):
    sites = np.logical_and( E>=E_min , E<=E_max)
    E_slice = E[sites]
    dos_slice = DOS[sites]

    bin_width = (E_max-E_min)/n_bins
    bin_width_idx = len(E_slice)/n_bins

    dos_hist = np.zeros(n_bins)
    E_hist = np.zeros(n_bins)
    for bin in range(n_bins):
        start_idx = round(bin*bin_width_idx)
        finish_idx = round((bin+1)*bin_width_idx)
        DOS_bin = dos_slice[start_idx:finish_idx]
        E_bin = E_slice[start_idx:finish_idx]
        dos_hist[bin] = DOS_bin.mean()
        E_hist[bin] = E_bin.mean()
    return dos_hist,E_hist


def make_database(n,T,out_name):
    """Main function to make the database for a given MXene n and T.

    Parameters
    ----------
    `n` : MXene index n.
    `T` : MXene termination.
    `out_name` : Output file name.
    """
    with open(out_name,"a") as outFile:
            searcher = SEARCH()
            paths, datas = searcher.path_tree(n,T)

            for path,data in zip(paths,datas):

                c_path = path+"CONTCAR"             # Optimized terminated CONTCAR
                p_path = path+"opt/POSCAR"          # POSCAR with pristine information

                d_path = path+"DOS/DOSCAR"          # PBE DOSCAR
                d0_path = path+"DOS/PBE0/DOSCAR"    # PBE0 DOSCAR

                # Reading files 
                contcar = CONTCAR(c_path)
                try: poscar = CONTCAR(p_path)
                except FileNotFoundError: 
                    try: poscar = CONTCAR(path+"opt/PBE/isif27/POSCAR")
                    except FileNotFoundError: poscar = CONTCAR(path+"opt/isif27/POSCAR")
                
                doscar = DOSCAR(d_path,short=True)
                doscar0 = DOSCAR(d0_path,short=True)

                # Getting data
                geom = contcar.getGeom(extra_dist=True)
                geom_p = poscar.getGeom(extra_dist=True)
                *bandgap,E,DOS = doscar.getBandgap(return_arrays=True)
                bandgap0 = doscar0.getBandgap()

                DOS_hist,E_hist = make_histogram(E,DOS)

                delattr(doscar,"out")
                delattr(doscar0,"out")

                
                mxt,stack,hollow = data
                a, d, hMT1, hMT2, dMT1, dMT2, dXT1,dXT2, dMX1,dMX2 = geom
                a_p, d_p = geom_p[:2]
                dMX1_p,dMX2_p = geom_p[-2:]

                Eg, VBM, CBM = bandgap
                Eg0, VBM0, CBM0 = bandgap0

                mx = MX(mxt)
                M,X,T_name = mx.atoms if not mx.T_AB else [mx.atoms[0],mx.atoms[1],mx.atoms[2]+mx.atoms[3]]
                
                M_el = periodic_table.get_el_sp(M)
                X_el = periodic_table.get_el_sp(X)
                T_el = periodic_table.get_el_sp(T_name if T_name!="OH" else "O")

                # Writing data to file
                outFile.write(f"  {mxt}    {n}    {M}    {X}    {T_name}    {stack}    {hollow}    {a}    {d}    {hMT1}    {hMT2}    \
                            {dMT1}    {dMT2}    {dXT1}    {dXT2}    {dMX1}    {dMX2}    {a_p}    {d_p}    {dMX1_p}    {dMX2_p}\
                            {M_el.Z}    {M_el.group}    {M_el.row}    {M_el.X}    {M_el.electron_affinity}    {M_el.van_der_waals_radius}    {M_el.atomic_radius.real}\
                            {X_el.Z}    {X_el.group}    {X_el.row}    {X_el.X}    {X_el.electron_affinity}    {X_el.van_der_waals_radius}    {X_el.atomic_radius.real}\
                            {T_el.Z}    {T_el.group}    {T_el.row}    {T_el.X}    {T_el.electron_affinity}    {T_el.van_der_waals_radius}    {T_el.atomic_radius.real}\
                            {VBM}   {CBM}    {Eg}    {VBM0}   {CBM0}    {Eg0} ")
                for bin in DOS_hist: outFile.write(str(bin)+" ")
                outFile.write("\n")
                outFile.flush()

                del doscar; del doscar0
                gc.collect()


# Parsing user arguments
parser = ArgumentParser(description="Runs over all specified paths (with n and T) to gather data and construct database.")
parser.add_argument("-n","--n_index",type=int,help="MXene n index (int) from the formula Mn+1XnT2.",required=True)
parser.add_argument("-T","--termination",type=str,default="",help="MXene termination (str) from the formula Mn+1XnT2. Specifyit with the index, i.e 'O2'. \
                    For pristine MXenes, don't use this or use None. Defaults to None.")
parser.add_argument("-o","--out_name",type=str,help="Putput file name. Defaults to database_[n]_[T].log",default=None)

args = parser.parse_args()
n,T,out_name = args.n_index, args.termination, args.out_name
if T == "None": T = ""
if out_name is None: out_name = f"database_{n}_{T}.log"

# make_database(n,T,out_name)

# Since this script opens many files and most of them generate large lists, variables, etc.
# it sometimes gets killed by the kernel, I don't exactly know why (probably OOM killer).
# Instead of doing all cases at one, try doing it for a given n and T (less memory used).