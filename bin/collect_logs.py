#!/usr/bin/env python
# ./collect_logs.py log_foo.txt log_bar.txt ...
#
import sys
from typing import List
# from math import *
from math import pi

#wu_threshold = 1.0 # threshold to show in W.u.
wu_threshold = -0.001

e_data = {}     # e_data[energy] = (log filename, spin, parity, eigenstate number, tt).
n_jnp = {}

e_gs = 0.0


def i2prty(i: int) -> str:
    """
    Convert 1 to '+' and -1 to '-'.

    Parameters
    ----------
    i : int
        Parity in integer representation.

    Returns
    -------
    : str
        The string representation of the parity.
    """
    if i == 1: return '+'
    else: return '-'

def weisskopf_unit(asc, mass):
    # Bohr and Mottelson, Vol.1, p. 389
    l = int(asc[1:])
    if asc[0] in ('e', 'E'):
        wu = 1.2**(2*l) / ( 4.*pi )  * (3./(l+3.))**2 \
            * mass**(2.*l/3.)  
        unit = 'e^2 fm^' + str(2*l)
    elif asc[0] in ('m', 'M'):
        wu = 10. / pi * 1.2**(2*l-2) * (3./(l+3.))**2 \
            * mass**((2.*l-2.)/3.) 
        if l == 1: 
            unit = 'mu_N^2  '
        else:
            unit = 'mu_N^2 fm^' + str(2*l - 2)
    else:
        raise 'weisskopf error'
    return  wu, unit
    
def read_file_ene(filename: str):
    """
    Extract the energy, spin, and parity for each eigenstate and arrange
    the data in a dictionary, e_data, where the keys are the energies
    and the values are tuples of
    (log filename, spin, parity, eigenstate number, tt).

    The transition logs will not be read by this function as they do not
    contain the energy level information. Only the KSHELL logs will be
    read.

    Parameters
    ----------
    filename : str
        The log filename.
    """
    fp = open(filename, 'r')
    while True:
        line = fp.readline()
        if not line: break
        if len(line) >= 11 and line[:11] != "H converged": continue
        if len(line) >= 14 and line[:14] != "H bn converged": continue
        while True:
            line = fp.readline()
            if not line: break
            if line[6:10] == '<H>:':
                """
                Example:
                -------------------------------------------------
                   1  <H>:  -391.71288  <JJ>:    -0.00000  J:  0/2  prty -1     <-- this line will be read
                    <Hcm>:     0.00022  <TT>:     6.00000  T:  4/2              <-- this line will be read
                 <p Nj>  5.944  3.678  1.489  3.267  0.123  0.456  0.043        <-- this line will be skipped
                 <n Nj>  5.993  3.902  1.994  5.355  0.546  0.896  0.314        <-- this line will be skipped
                 hw:  1:1.000                                                   <-- this line will be skipped
                -------------------------------------------------
                NOTE: All this substring indexing seems to be easily
                replaceable with a simple split!
                """
                n_eig = int(line[:5])       # Eigenvalue number. 1, 2, 3, ...
                energy = float(line[11:22])
                spin = int(line[45:48])     # 2*spin actually.
                parity = int(line[57:59])
                parity = i2prty(parity)
                while energy in e_data: energy += 0.000001  # NOTE: To separate energies close together? Else keys may be identical!
                while True:
                    line = fp.readline()
                    if line[42:45] != ' T:': continue
                    tt = int(line[45:48])
                    e_data[ energy ] = (filename, spin, parity, n_eig, tt)
                    break
    fp.close()

def str_JJ(jj):
    if jj < 0:
        return str(jj) #+'  '
    elif jj % 2 == 0: 
        return str(jj/2) # +'  '
    else:
        return str(jj) + '/2'
        
def read_file_tran(filename, asc):
    out_e = {}
    is_r = False
    fp = open(filename, 'r')
    fn_l, fn_r = 'a', 'b'
    mass_save = 0
    while True:
        line = fp.readline()
        if not line: break
        arr = line.split()
        if len(arr) == 0: continue
        if 'mass=' in line:
            """
            Fetch mass number.
            """
            n = line.index('mass=')
            mass = int(line[n + 5:n + 8])
            if not mass_save:
                mass_save = mass
            if mass_save != mass: 
                print('ERROR  mass', mass, mass_save)
            wu, unit = weisskopf_unit(asc, mass)
        
        if arr[0] == 'fn_load_wave_l': 
            fn_l = arr[2]
        
        elif arr[0] == 'fn_load_wave_r': 
            fn_r = arr[2]
        
        if line[:14] != " " + asc + " transition":  continue
        is_r = unit
        arr = line.split()
        prty1, prty2 = i2prty(int(arr[-2])), i2prty(int(arr[-1]))
        if fn_l == fn_r: is_diag = True
        else: is_diag = False
        line = fp.readline()
        while True:
            """
            Extract transition data from log_*_tr_*.txt.  (And maybe
            other data too).
            """
            line = fp.readline().rstrip()
            if not line: break
            if line.startswith("pn="):
                """
                jonkd: I had to add this because 'pn' showed up in the
                middle of the 'log_Ni56_gxpf1a_tr_m0p_m0p.txt' file
                after trying (unsuccessfully) to run on Fram.

                M1 transition  mu_N^2  gl,gs=  1.0000  0.0000  3.9100 -2.6780 parity  1  1
                2xJf      Ef      2xJi     Ei       Ex       Mred.    B(EM )->   B(EM)<-   Mom.
                 4(   2) -200.706 4(   2) -200.706   0.000    1.3570    0.3683    0.3683    1.0141
                 4(   2) -200.706 6(   4) -198.842   1.864    0.0147    0.0000    0.0000    0.0000
                pn= 1   # of mbits=            286
                 4(   2) -200.706 6(  10) -197.559   3.147   -0.0289    0.0002    0.0001    0.0000
                """
                continue
            
            spin_final = int(line[:2])      # J final.
            n1 = int(line[3:7])
            spin_initial = int(line[17:19])   # J initial.
            n2 = int(line[20:24])
            if spin_final == spin_initial and n1 == n2: continue
            
            ex = float(line[34:42]) # Gamma energy.
            if is_diag and ex < 0.0: continue
            v1 = float(line[53:62]) # B(EM )->  NOTE: Why this when b1 below?
            v2 = float(line[63:72]) # B(EM )<-
            
            E1 = float(line[8:17]) - e_gs   # E final.
            E2 = float(line[25:34]) - e_gs  # E initial.
            if abs(E1) < 1.e-3: E1 = 0.
            if abs(E2) < 1.e-3: E2 = 0.
            
            Mred = float(line[43:52])
            b1 = float(line[52:62])
            b2 = float(line[62:72])
            wu1, wu2 = b1/wu, b2/wu
            if max(wu1, wu2) < wu_threshold: continue

            n1 = n_jnp[ (spin_final, prty1, n1) ]
            n2 = n_jnp[ (spin_initial, prty2, n2) ]
            stringformat \
                = "%4s%c(%2d) %6.3f %4s%c(%2d) %6.3f %6.3f " \
                + "%8.1f(%5.1f) %8.1f(%5.1f)\n"
            if asc == 'M1': stringformat \
               = "%4s%c(%2d) %6.3f %4s%c(%2d) %6.3f %6.3f " \
               + "%8.3f(%5.2f) %8.3f(%5.2f)\n"
                
            if ex > 0.0:
                out = stringformat \
                      % (str_JJ(spin_initial), prty2, n2, E2, 
                         str_JJ(spin_final), prty1, n1, E1, 
                         ex,  b2, wu2, b1, wu1)
                ky = E2 + E1 * 1e-5 + spin_initial *1.e-10 + n2*1.e-11 + spin_final*1.e-13 + n1*1.e-14
            else:
                out = stringformat \
                      % (str_JJ(spin_final), prty1, n1, E1, 
                         str_JJ(spin_initial), prty2, n2, E2, 
                         -ex, b1, wu1, b2, wu2)
                ky = E1 + E2 * 1e-5 + spin_final *1.e-10 + n1*1.e-11 + spin_initial*1.e-12 + n2*1.e-14
            out_e[ky] = out
    fp.close()
    return is_r, out_e, mass_save

def main(filename_list: List):
    print("\n Energy levels")
    for filename in filename_list:
        read_file_ene(filename)

    keys = e_data.keys()
    if len(keys) > 0:
        keys = sorted(keys)
        njp = {}
        for e in keys:
            filename, mtot, prty, n_eig, tt = e_data[e]
            mp = (mtot, prty)
            njp[mp] = njp.get(mp, 0) + 1
            n_jnp[ (mtot, prty, n_eig) ] = njp[mp]
            e_data[e] = filename, mtot, prty, njp[mp], tt

        global e_gs
        e_gs = keys[0]
        print('\n    N    J prty N_Jp    T     E(MeV)  Ex(MeV)  log-file\n')
        for i, e in enumerate(keys):
            filename, mtot, prty, n_eig, tt = e_data[e]
            print("%5d %5s %1s %5d %5s %10.3f %8.3f  %s " \
                % (i+1, str_JJ(mtot), prty, n_eig, str_JJ(tt), e, e-e_gs, filename))
        print()


    def print_transition(asc):
        is_show = False
        output_e = {}
        for filename in sys.argv[1:]:
            is_r, out_e, mass = read_file_tran(filename, asc)
            if is_r: is_show = is_r
            output_e.update( out_e )
        wu, unit = weisskopf_unit(asc, mass)
        output = """
B(%s)  ( > %.1f W.u.)  mass = %d    1 W.u. = %.1f %s
                                           %s (W.u.) 
   J_i    Ex_i     J_f    Ex_f   dE        B(%s)->         B(%s)<- 
""" % (asc, wu_threshold,  mass, wu, unit, is_show, asc, asc)
        for e, out in sorted(output_e.items()):
            output += out        
        if is_show: print(output)

    print_transition('E2')
    print_transition('M1')
#    print_transition('E1')
#    print_transition('E3')

if __name__ == "__main__":
    main(sys.argv[1:])