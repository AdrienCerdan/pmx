#!/usr/bin/env python
import sys
import os
import argparse
import tempfile
from copy import deepcopy
from pmx import library
from pmx.model import Model
from pmx.atom import Atom
from pmx.geometry import Rotation
from pmx.ffparser import RTPParser, NBParser
from pmx.parser import kickOutComments, readSection, parseList
from pmx.library import _ext_one_letter

standard_pair_list = [
    ('N','N'),
    ('H','H'),
    ('CA','CA'),
    ('C','C'),
    ('O','O'),
    ('HA','HA'),
    ('CB','CB'),
    ('1HB','1HB'),
    ('2HB','2HB'),
    ('CG','CG')
    ]

standard_pair_list_charmm = [
    ('N','N'),
    ('HN','HN'),
    ('CA','CA'),
    ('C','C'),
    ('O','O'),
    ('HA','HA'),
    ('CB','CB'),
    ('1HB','1HB'),
    ('2HB','2HB'),
    ('CG','CG')
    ]

standard_pair_listB = [
    ('N','N'),
    ('H','H'),
    ('CA','CA'),
    ('C','C'),
    ('O','O'),
    ('HA','HA'),
    ('CB','CB'),
    ('1HB','1HB'),
    ('2HB','2HB')
    ]

standard_pair_list_charmmB = [
    ('N','N'),
    ('HN','HN'),
    ('CA','CA'),
    ('C','C'),
    ('O','O'),
    ('HA','HA'),
    ('CB','CB'),
    ('1HB','1HB'),
    ('2HB','2HB')
    ]

standard_pair_listC = [
    ('N','N'),
    ('H','H'),
    ('CA','CA'),
    ('C','C'),
    ('O','O'),
    ('HA','HA'),
    ('CB','CB')
    ]

standard_pair_list_charmmC = [
    ('N','N'),
    ('HN','HN'),
    ('CA','CA'),
    ('C','C'),
    ('O','O'),
    ('HA','HA'),
    ('CB','CB')
    ]

standard_pair_listD = [
    ('N','N'),
    ('H','H'),
    ('CA','CA'),
    ('C','C'),
    ('O','O')
    ]

standard_pair_list_charmmD = [
    ('N','N'),
    ('HN','HN'),
    ('CA','CA'),
    ('C','C'),
    ('O','O')
    ]

standard_pair_listPro = [
    ('N','N'),
    ('CA','CA'),
    ('HA','HA'),
    ('C','C'),
    ('O','O')
    ]

standard_pair_listGlyPro = [
    ('N','N'),
    ('CA','CA'),
    ('C','C'),
    ('O','O')
    ]

standard_rna_pair_list = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'1','H2\'1'),
    ('O2\'','O2\''),
    ('HO\'2','HO\'2'),
    ('O3\'','O3\''),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'1','H5\'1'),
    ('H5\'2','H5\'2'),
    ('P','P'),
    ('O1P','O1P'),
    ('O2P','O2P'),
    ]

standard_rna_5term_pair_list = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'1','H2\'1'),
    ('O2\'','O2\''),
    ('HO\'2','HO\'2'),
    ('O3\'','O3\''),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'1','H5\'1'),
    ('H5\'2','H5\'2'),
    ('H5T','H5T'),
    ]

standard_rna_3term_pair_list = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'1','H2\'1'),
    ('O2\'','O2\''),
    ('HO\'2','HO\'2'),
    ('O3\'','O3\''),
    ('H3T','H3T'),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'1','H5\'1'),
    ('H5\'2','H5\'2'),
    ('P','P'),
    ('O1P','O1P'),
    ('O2P','O2P'),
    ]

standard_dna_pair_list = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'1','H2\'1'),
    ('H2\'2','H2\'2'),
    ('O3\'','O3\''),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'1','H5\'1'),
    ('H5\'2','H5\'2'),
    ('P','P'),
    ('O1P','O1P'),
    ('O2P','O2P'),
    ]

standard_dna_5term_pair_list = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'1','H2\'1'),
    ('H2\'2','H2\'2'),
    ('O3\'','O3\''),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'1','H5\'1'),
    ('H5\'2','H5\'2'),
    ('H5T','H5T'),
    ]

standard_dna_3term_pair_list = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'1','H2\'1'),
    ('H2\'2','H2\'2'),
    ('O3\'','O3\''),
    ('H3T','H3T'),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'1','H5\'1'),
    ('H5\'2','H5\'2'),
    ('P','P'),
    ('O1P','O1P'),
    ('O2P','O2P'),
    ]

standard_dna_pair_list_charmm = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'','H2\''),
    ('H2\'\'','H2\'\''),
    ('O3\'','O3\''),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'','H5\''),
    ('H5\'\'','H5\'\''),
    ('P','P'),
    ('O1P','O1P'),
    ('O2P','O2P'),
    ]

standard_dna_5term_pair_list_charmm = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'','H2\''),
    ('H2\'\'','H2\'\''),
    ('O3\'','O3\''),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'','H5\''),
    ('H5\'\'','H5\'\''),
    ('H5T','H5T'),
    ]

standard_dna_3term_pair_list_charmm = [
    ('C1\'','C1\''),
    ('C2\'','C2\''),
    ('C3\'','C3\''),
    ('C4\'','C4\''),
    ('O4\'','O4\''),
    ('C5\'','C5\''),
    ('O5\'','O5\''),
    ('H1\'','H1\''),
    ('H2\'','H2\''),
    ('H2\'\'','H2\'\''),
    ('O3\'','O3\''),
    ('H3T','H3T'),
    ('H3\'','H3\''),
    ('H4\'','H4\''),
    ('H5\'','H5\''),
    ('H5\'\'','H5\'\''),
    ('P','P'),
    ('O1P','O1P'),
    ('O2P','O2P'),
    ]

use_standard_pair_list = {
    'PHE': [ 'TRP','HIP','HID','HIE','HSP','HSD','HSE','HIS1','HISH','HISE'],
    'TYR': [ 'TRP','HIP','HID','HIE','HSP','HSD','HSE','HIS1','HISH','HISE'],
    'TRP': [ 'PHE','TYR','HIP','HID','HSE','HSP','HSD','HSE','HIS1','HISH','HISE','HIE'],
    'HID': [ 'PHE','TYR','TRP'], #[ 'PHE','TYR','HIP','TRP','HIE'],
    'HIE': [ 'PHE','TYR','TRP'], #[ 'PHE','TYR','HIP','HID','TRP'],
    'HIP': [ 'PHE','TYR','TRP'], #,'HID','HIE'],
    'HSD': [ 'PHE','TYR','TRP'], #[ 'PHE','TYR','HIP','TRP','HIE'],
    'HSE': [ 'PHE','TYR','TRP'], #[ 'PHE','TYR','HIP','HID','TRP'],
    'HSP': [ 'PHE','TYR','TRP'], #,'HID','HIE'],
    'HIS1': [ 'TRP','PHE','TYR'],
    'HISE': [ 'TRP','PHE','TYR'],
    'HISH': [ 'TRP','PHE','TYR']
    }

use_standard_rna_pair_list = {
    'RA': [ 'RC','RU'],
    'RG': [ 'RC','RU'],
    'RC': [ 'RA','RG'],
    'RU': [ 'RA','RG'],
    }

use_standard_rna_5term_pair_list = {
    'RA5': [ 'RC5','RU5'],
    'RG5': [ 'RC5','RU5'],
    'RC5': [ 'RA5','RG5'],
    'RU5': [ 'RA5','RG5'],
    }

use_standard_rna_3term_pair_list = {
    'RA3': [ 'RC3','RU3'],
    'RG3': [ 'RC3','RU3'],
    'RC3': [ 'RA3','RG3'],
    'RU3': [ 'RA3','RG3'],
    }

use_standard_dna_pair_list = {
    'DA': [ 'DC','DT'],
    'DG': [ 'DC','DT'],
    'DC': [ 'DA','DG'],
    'DT': [ 'DA','DG'],
    }

use_standard_dna_5term_pair_list = {
    'DA5': [ 'DC5','DT5'],
    'DG5': [ 'DC5','DT5'],
    'DC5': [ 'DA5','DG5'],
    'DT5': [ 'DA5','DG5'],
    }

use_standard_dna_3term_pair_list = {
    'DA3': [ 'DC3','DT3'],
    'DG3': [ 'DC3','DT3'],
    'DC3': [ 'DA3','DG3'],
    'DT3': [ 'DA3','DG3'],
    }

res_with_rings = ['HIS','HID','HIE','HIP','HISE','HISH','HIS1','HSE','HSD','HSP',
                  'PHE','TYR','TRP']

res_diff_Cb = [ 'THR', 'ALA', 'VAL', 'ILE' ]

res_gly_pro = [ 'GLY', 'PRO' ]

res_pro = [ 'PRO' ]

res_gly = [ 'GLY' ]

merge_by_name_list = {
    'PHE':['TYR'],
    'TYR':['PHE'],
    'HID':['HIP','HIE'],
    'HIE':['HIP','HID'],
    'HIP':['HID','HIE'],
    'HSD':['HSP','HSE'],
    'HSE':['HSP','HSD'],
    'HSP':['HSD','HSE'],
    'HIS1':['HISE','HISH'],
    'HISE':['HIS1','HISH'],
    'HISH':['HIS1','HISE']
}


mol_branch = {
    'ILE':2,
    'VAL':2,
    'LEU':3,
    'GLN':3,
    'GLU':3,
    'GLUH':3,
    'ASP':2,
    'ASN':2,
    'PHE':2,
    'TYR':2,
    'TRP':2,
    'HIS':2,
    'HIS1':2,
    'HISE':2,
    'HISH':2,
    'THR':2,
    'ALA':5,
    'SER':5,
    'GLY':5,
    'CYS':5,
    'MET':5,
    'ARG':5,
    'LYS':5,
    'LYN':5,
    }

dna_names = {
    'DA5_DT5':'D5K',
    'DA5_DC5':'D5L',
    'DA5_DG5':'D5M',
    'DT5_DA5':'D5N',
    'DT5_DC5':'D5O',
    'DT5_DG5':'D5P',
    'DC5_DA5':'D5R',
    'DC5_DT5':'D5S',
    'DC5_DG5':'D5T',
    'DG5_DA5':'D5X',
    'DG5_DT5':'D5Y',
    'DG5_DC5':'D5Z',
    'DA3_DT3':'D3K',
    'DA3_DC3':'D3L',
    'DA3_DG3':'D3M',
    'DT3_DA3':'D3N',
    'DT3_DC3':'D3O',
    'DT3_DG3':'D3P',
    'DC3_DA3':'D3R',
    'DC3_DT3':'D3S',
    'DC3_DG3':'D3T',
    'DG3_DA3':'D3X',
    'DG3_DT3':'D3Y',
    'DG3_DC3':'D3Z',
    }

# ==============================================================================
# Functions
# ==============================================================================
def _dna_mutation_naming(aa1, aa2):
    rr_name = 'D'+aa1[-1]+aa2[-1]
    dict_key = aa1+'_'+aa2
    if dict_key in dna_names.keys():
        rr_name = dna_names[dict_key]
    return(rr_name)


def _rna_mutation_naming(aa1, aa2):
    rr_name = 'R'+aa1[-1]+aa2[-1]
    dict_key = aa1+'_'+aa2
    if dict_key in dna_names.keys():
        rr_name = dna_names[dict_key]
    return(rr_name)


def max_rotation(dihedrals):
    m = 0
    for d in dihedrals:
        if d[-2] == 1 and d[-1] > 0:
            m = d[-1]
        if d[-2] == 0 and d[-1] != -1:
            return d[-1]
    return m+1


# this could be incorporated into Model
def _rename_atoms_nucleic_acids(m):
    for atom in m.atoms:
        aname = atom.name
        if len(aname) == 4:
            if aname[0].isdigit() is True or aname[0] == '\'':
                first = aname[0]
                rest = aname[1:]
                new = rest+first
                atom.name = new


def get_dihedrals(resname):
    return library._aa_dihedrals[resname]


def set_dihedral(atoms, mol, phi):
    print atoms[0].name, atoms[1].name, atoms[2].name
    a1 = atoms[0]
    a2 = atoms[1]
    a3 = atoms[2]
    a4 = atoms[3]
    # a1,a2,a3,a4 = atoms
    d = a1.dihedral(a2, a3, a4)
    r = Rotation(a2.x, a3.x)
    rot = d-phi
    # print a2.name, a3.name
    for atom in mol.atoms:
        if atom.order > a3.order:
            if a3.long_name[3] == ' ':
                # print 'rotating', atom.name
                atom.x = r.apply(atom.x, -rot)
            else:
                if atom.long_name[3] == a3.long_name[3] \
                   or atom.long_name[3] == ' ':
                    # print 'rotating', atom.name
                    atom.x = r.apply(atom.x, -rot)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def do_fit(m1, dihed1, m2, dihed2):
    bonds = []
    diheds = []
    # if not diheds: we take the chi's
    diheds = []
    for dih in dihed1:
        chi = dih[-1]
        if chi > 0:
            for dih2 in dihed2:
                if dih2[-1] == chi and dih2[-2] == 1:
                    diheds.append((dih, dih2))
    for dih1, dih2 in diheds:
        atoms1 = m1.fetchm(dih1)
        print "fetching"
        atoms2 = m2.fetchm(dih2)
        print dih2
        print atoms2
        a1, a2, a3, a4 = atoms1
        if (a2.name, a3.name) not in bonds:
            phi = a1.dihedral(a2, a3, a4)
            # print phi
            # print 'rot1', a1.name,a2.name,a3.name,a4.name
            set_dihedral(atoms2, m2, phi)

    op = open('check.pdb', 'w')
    for atom in m2.atoms:
        print >>op, atom


def tag(atom):
    s = '%s|%s|%s|%s' % (atom.resname, atom.name, atom.atomtype, atom.atype)
    return '%-20s' % s


def align_sidechains(r1, r2):
    # if you add new force field, check pmx/molecule.py, make sure res is
    # correctly set into get_real_resname
    for i in range(r1.nchi()):
        phi = r1.get_chi(i+1, degree=True)
        r2.set_chi(i+1, phi)


def assign_rtp_entries(mol, rtp):
    entr = rtp[mol.resname]
    neigh = []
    # atoms
    for atom_entry in entr['atoms']:
        atom_name = atom_entry[0]
        atom_type = atom_entry[1]
        atom_q    = atom_entry[2]
        atom_cgnr = atom_entry[3]
        atom = mol.fetch(atom_name)[0]
        atom.atomtype = atom_type
        atom.q = atom_q
        atom.cgnr = atom_cgnr
    # bonds
    for a1, a2 in entr['bonds']:
        # charmm uses next residue in bonds (+), amber previous (-)
        # also write rtp is affected now, since normally -C N is added
        # charmm used C +N, problem is that you run into trouble on the
        # termini
        bmin = '-' not in a1 and '-' not in a2
        bplus = '+' not in a1 and '+' not in a2
        if bmin and bplus:
            atom1, atom2 = mol.fetchm([a1, a2])
            atom1.bonds.append(atom2)
            atom2.bonds.append(atom1)
        else:
            neigh.append([a1, a2])
    return neigh


def assign_branch(mol):
    for atom in mol.atoms:
        if atom.long_name[-1] == ' ':
            atom.branch = 0
        elif atom.long_name[-1] == '1':
            atom.branch = 1
        else:
            atom.branch = 2


def get_atoms_by_order(mol, order):
    res = []
    for atom in mol.atoms:
        if atom.order == order:
            res.append(atom)
    return res


def get_atoms_by_order_and_branch(mol, order, branch, merged_atoms):
    res = []
    for atom in mol.atoms:
        if atom.order == order and atom not in merged_atoms:
            if atom.branch in [0, branch] or atom.branch < mol_branch[mol.real_resname] + 1:
                res.append(atom)
    return res


def last_atom_is_morphed(atom, merged_list):
    for at in atom.bonds:
        if at.order < atom.order and at in merged_list:
            return True
    return False


def cmp_mol2_types(type1, type2):
    if type1 == type2:
        return True
    if type1 == 'H' or type2 == 'H':
        return True
    tp1_ext = type1.split('.')[1]
    tp2_ext = type2.split('.')[1]
    if tp1_ext in ['2', '3'] and tp2_ext in ['2', '3']:
        return False
    elif tp1_ext in ['am', 'co2'] and tp2_ext in ['am', 'co2']:
        return True
    elif type1 in ['O.2', 'O.co2'] and type2 in ['O.2', 'O.co2']:
        return True
    elif (type1[0] == 'S' and type2[0] != 'S') or (type1[0] != 'S' and type2[0] == 'S'):
        return False
    else:
        return False


def find_closest_atom(atom1, atom_list, merged_atoms, bH2heavy=True):
    min_d = 0.55
    idx = 99
    for i, atom in enumerate(atom_list):
        if atom not in merged_atoms:
            if bH2heavy is False:
                # check for H2heavy morphe
                if (atom1.atomtype.startswith('H') and (not atom.atomtype.startswith('H'))):
                    continue
                if (atom.atomtype.startswith('H') and (not atom1.atomtype.startswith('H'))):
                    continue

            d = atom1 - atom
            print "%s %s %f" % (atom1.name, atom.name, d)
            if d < min_d:
                min_d = d
                idx = i
    if idx != 99:
        return atom_list[idx], min_d
    else:
        return None, None


def make_predefined_pairs(mol1, mol2, pair_list):
    # make main chain + cb pairs
    print 'Making atom pairs.........'
    atom_pairs = []
    merged_atoms1 = []
    merged_atoms2 = []
    for name1, name2 in pair_list:
        try:
            at1 = mol1.fetch(name1)[0]
        except IndexError:
            at1 = mol1.fetch(reformat_atom_name(name1))[0]
        try:
            at2 = mol2.fetch(name2)[0]
        except IndexError:
            at2 = mol2.fetch(reformat_atom_name(name2))[0]

        at1.name = reformat_atom_name(name1)
        at2.name = reformat_atom_name(name2)
        at1.atomtypeB = at2.atomtype
        at1.qB = at2.q
        at1.mB = at2.m
        at1.nameB = at2.name
        merged_atoms1.append(at1)
        merged_atoms2.append(at2)
        atom_pairs.append([at1, at2])

    dummies = mol2.fetch_atoms(map(lambda a: a.name, merged_atoms1), inv=True)
    return atom_pairs, dummies


def merge_by_names(mol1, mol2):
    print 'Making atom pairs.........MERGE BY NAMES......'
    atom_pairs = []
    merged_atoms1 = []
    merged_atoms2 = []
    for at1 in mol1.atoms:
        try:
            at2 = mol2.fetch(at1.name)[0]
            at1.atomtypeB = at2.atomtype
            at1.qB = at2.q
            at1.mB = at2.m
            at1.nameB = at2.name
            merged_atoms1.append(at1)
            merged_atoms2.append(at2)
            atom_pairs.append([at1, at2])
        except:
            pass
    dummies = mol2.fetch_atoms(map(lambda a: a.name, merged_atoms1), inv=True)
    return atom_pairs, dummies


def make_pairs(mol1, mol2, bCharmm, bH2heavy=True, bDNA=False, bRNA=False):
    # make main chain + cb pairs
    print 'Making atom pairs.........'
    mol1.batoms = []
    merged_atoms1 = []
    merged_atoms2 = []
    atom_pairs = []
    if bDNA or bRNA:
        mc_list = []
    elif bCharmm:
        mc_list = ['N', 'CA', 'C', 'O', 'HN', 'HA', 'CB']
        gly_mc_list = ['N', 'CA', 'C', 'O', 'HN', '1HA', '2HA']
    else:
        mc_list = ['N', 'CA', 'C', 'O', 'H', 'HA', 'CB']
        gly_mc_list = ['N', 'CA', 'C', 'O', 'H', '1HA', '2HA']

    if mol1.resname == 'GLY':
        atoms1 = mol1.fetchm(gly_mc_list)
    else:
        atoms1 = mol1.fetchm(mc_list)
    if mol2.resname == 'GLY':
        atoms2 = mol2.fetchm(gly_mc_list)
    else:
        atoms2 = mol2.fetchm(mc_list)

    for at1, at2 in zip(atoms1, atoms2):
        at1.atomtypeB = at2.atomtype
        at1.qB = at2.q
        at1.mB = at2.m
        at1.nameB = at2.name
        mol1.batoms.append(at2)
        merged_atoms1.append(at1)
        merged_atoms2.append(at2)
        atom_pairs.append([at1, at2])
    # now go for the rest of the side chain

    if bDNA or bRNA:
        # identify atom morphes by distances
        atoms1 = mol1.atoms
        atoms2 = mol2.atoms
        for at1 in atoms1:
            print '-- Checking atom...', at1.name
            aa, d = find_closest_atom(at1, atoms2, merged_atoms2, bH2heavy)
            if aa:
                merged_atoms2.append(aa)
                merged_atoms1.append(at1)
                atom_pairs.append([at1, aa])
                print "here ", at1.name, aa.name
    else:
        for k in [1, 2]:
            print '-- Searching branch', k
            done_branch = False
            for i in range(2, 8):
                if done_branch:
                    break
                print '-- Searching order', i

                atoms1 = get_atoms_by_order_and_branch(mol1, i, k, merged_atoms1)
                atoms2 = get_atoms_by_order_and_branch(mol2, i, k, merged_atoms2)
                for at1 in atoms1:
                    if last_atom_is_morphed(at1, merged_atoms1):
                        print '-- Checking atom...', at1.name
                        candidates = []
                        for at2 in atoms2:
                            # if cmp_mol2_types( at1.atype, at2.atype):
                            candidates.append(at2)
                        aa, d = find_closest_atom(at1, candidates, merged_atoms2, bH2heavy)
                        if aa:
                            merged_atoms2.append(aa)
                            merged_atoms1.append(at1)
                            atom_pairs.append([at1, aa])
                            print '--> Define atom pair: ', tag(at1), '- >', tag(aa),  '(d = %4.2f A)' % d
                        else:
                            print 'No partner found for atom ', at1.name

    for at1, at2 in atom_pairs:
        print at1, at2
        at1.atomtypeB = at2.atomtype
        at1.qB = at2.q
        at1.mB = at2.m
        at1.nameB = at2.name
        mol1.batoms.append(at2)
    # now make list of dummies
    dummies = []
    for atom in mol2.atoms:
        if atom not in merged_atoms2:
            dummies.append(atom)
    return atom_pairs, dummies


def check_double_atom_names(r):
    for atom in r.atoms:
        alist = r.fetch_atoms(atom.name)
        if len(alist) != 1:
            if atom.name.startswith('HV'):
                alist = r.fetch_atoms(atom.name)
            else:
                alist = r.fetch_atoms(atom.name[:-1], wildcard=True)
            print 'Renaming atoms (%s)' % alist[0].name[:-1]
            start = 1
            for atom in alist:
                atom.name = atom.name[:3]+str(start)
                start += 1
            return False
    return True


def merge_molecules(r1, dummies):

    for atom in dummies:
        new_atom = atom.copy()
        new_atom.atomtypeB = new_atom.atomtype
        new_atom.qB = new_atom.q
        new_atom.mB = new_atom.m
        new_atom.typeB = new_atom.type
        new_atom.atomtype = 'DUM_'+new_atom.atomtype
        new_atom.q = 0
        new_atom.nameB = new_atom.name
        # hydrogen dummies are special
        if new_atom.name.startswith('H') or (new_atom.name[0].isdigit() and new_atom.name[1] == 'H'):
            new_atom.name = 'HV'
        else:
            if len(new_atom.name) == 4:
                new_atom.name = 'D'+new_atom.name[:3]
                if new_atom.name[1].isdigit():
                    new_atom.name = new_atom.name[0] + new_atom.name[2:] + new_atom.name[1]
            else:
                new_atom.name = 'D'+atom.name
        r1.append(new_atom)


def make_bstate_dummies(r1):
    for atom in r1.atoms:
        if not hasattr(atom, "nameB"):
            atom.nameB = atom.name+'.gone'
            atom.atomtypeB = 'DUM_'+atom.atomtype
            atom.qB = 0
            atom.mB = atom.m


def make_transition_dics(atom_pairs, r1):
    abdic = {}
    badic = {}
    for a1, a2 in atom_pairs:
        abdic[a1.name] = a2.name
        badic[a2.name] = a1.name
    for atom in r1.atoms:
        if (atom.name[0] == 'D') or (atom.name.startswith('HV')):
            abdic[atom.name] = atom.name
            badic[atom.name] = atom.name
    return abdic, badic


def find_atom_by_nameB(r, name):
    for atom in r1.atoms:
        if atom.nameB == name:
            return atom
    return None


def update_bond_lists(r1, badic):

    print 'Updating bond lists...........'
    for atom in r1.atoms:
        if (atom.name[0] == 'D') or atom.name.startswith('HV'):
            print 'atom', atom.name
            print '  |  '
            new_list = []
            while atom.bonds:
                at = atom.bonds.pop(0)
                print atom.name, '->', at.name
                if at.name in badic:
                    aa = r1.fetch(badic[at.name])[0]
                    new_list.append(aa)
                else:
                    aa = find_atom_by_nameB(r1, at.name)
                    if aa is not None:
                        new_list.append(aa)
                    else:
                        print 'Atom not found', at.name, at.nameB
                        sys.exit(1)
            atom.bonds = new_list
            for at in atom.bonds:
                if atom not in at.bonds:
                    at.bonds.append(atom)
                print('----bond--->', at.name)
            print


def improp_entries_match(lst1, lst2):
    res = True
    for a1, a2 in zip(lst1, lst2):
        if a1.name != a2.name:
            res = False
    if res is True:
        return res
    res = True
    for a1, a2 in zip(lst1, list(reversed(lst2))):
        if a1.name != a2.name:
            res = False
    return res


def generate_dihedral_entries(im1, im2, r, pairs):
    print 'Updating dihedrals...........'
    new_ii = []
    done_i1 = []
    done_i2 = []
    # ILDN dihedrals
    for i1 in im1:
        for i2 in im2:
            if improp_entries_match(i1[:4], i2[:4]) and (i2 not in done_i2):
                im_new = i1[:4]
                if i1[4] == '':
                    im_new.append('default-A')
                else:
                    im_new.append(i1[4])
                if i2[4] == '':
                    im_new.append('default-B')
                else:
                    im_new.append(i2[4])
                done_i1.append(i1)
                done_i2.append(i2)
                new_ii.append(im_new)
                break

    for i1 in im1:
        if i1 not in done_i1:
            im_new = i1[:4]
            if i1[4] == '':
                im_new.append('default-A')
                if (('gone' in i1[0].nameB) or ('gone' in i1[1].nameB) or
                   ('gone' in i1[2].nameB) or ('gone' in i1[3].nameB)):
                    im_new.append('default-A')
                else:
                    im_new.append('un')
            else:
                if (('gone' in i1[0].nameB) or ('gone' in i1[1].nameB) or
                   ('gone' in i1[2].nameB) or ('gone' in i1[3].nameB)):
                    im_new.append(i1[4])
                    im_new.append(i1[4])
                else:
                    im_new.append(i1[4])
                    if 'torsion' in i1[4]:  # ildn
                        tors = deepcopy(i1[4])
                        tors = tors.replace('torsion', 'tors')
                        foo = 'un' + tors
                        im_new.append(foo)
                    elif 'dih_' in i1[4]:  # opls
                        foo = 'un' + i1[4]
                        im_new.append(foo)
                    else:
                        im_new.append('un')
            new_ii.append(im_new)
    for i2 in im2:
        if i2 not in done_i2:
            im_new = i2[:4]
            if i2[4] == '':
                if ((i2[0].name.startswith('D')) or (i2[1].name.startswith('D')) or
                   (i2[2].name.startswith('D')) or (i2[3].name.startswith('D')) or
                   (i2[0].name.startswith('HV')) or (i2[1].name.startswith('HV')) or
                   (i2[2].name.startswith('HV')) or (i2[3].name.startswith('HV'))):
                    im_new.append('default-B')
                else:
                    im_new.append('un')
                im_new.append('default-B')
            else:
                if ((i2[0].name.startswith('D')) or (i2[1].name.startswith('D')) or
                   (i2[2].name.startswith('D')) or (i2[3].name.startswith('D')) or
                   (i2[0].name.startswith('HV')) or (i2[1].name.startswith('HV')) or
                   (i2[2].name.startswith('HV')) or (i2[3].name.startswith('HV'))):
                    im_new.append(i2[4])
                    im_new.append(i2[4])
                else:
                    if 'torsion' in i2[4]:  # ildn
                        tors = deepcopy(i2[4])
                        tors = tors.replace('torsion', 'tors')
                        foo = 'un' + tors
                        im_new.append(foo)
                    elif 'dih_' in i2[4]:  # opls
                        foo = 'un' + i2[4]
                        im_new.append(foo)
                    else:
                        im_new.append('un')
                    im_new.append(i2[4])
            new_ii.append(im_new)

    return new_ii


def generate_improp_entries(im1, im2, r):
    print 'Updating impropers...........'

    new_ii = []
    done_i1 = []
    done_i2 = []
    # common impropers
    for i1 in im1:
        print("improper: ", i1[0].name, i1[1].name, i1[2].name, i1[3].name)
        for i2 in im2:
            if improp_entries_match(i1[:4], i2[:4]):
                print('matched impropers: ', i1[0].name, i1[1].name,
                      i1[2].name, i1[3].name)
                im_new = i1[:4]
                if i1[4] == '':
                    im_new.append('default-A')
                elif i1[4] == '105.4':  # star
                    im_new.append('default-star')
                else:
                    im_new.append(i1[4])
                if i2[4] == '':
                    im_new.append('default-B')
                elif i2[4] == '105.4':  # star
                    im_new.append('default-star')
                else:
                    im_new.append(i2[4])
                done_i1.append(i1)
                done_i2.append(i2)
                new_ii.append(im_new)
    for i1 in im1:
        if i1 not in done_i1:
            print("unmatched impropers A: ", i1[0].name, i1[1].name,
                  i1[2].name, i1[3].name)
            im_new = i1[:4]
            if i1[4] == '':
                im_new.append('default-A')
                # this construct with if and continue statements is for PRO
                # impropers: for proline -C and +N containing impropers are
                # different to those of the other residues therefore these
                # impropers will remain unmatched. however, at the same time
                # -C and +N will not have a B state, i.e. atom.nameB
                # attribute not existing
                bFound = False
                if hasattr(i1[0], 'nameB'):
                    if 'gone' in i1[0].nameB:
                        im_new.append('default-A')
                        bFound = True
                if bFound is False and hasattr(i1[1], 'nameB'):
                    if 'gone' in i1[1].nameB:
                        im_new.append('default-A')
                        bFound = True
                if bFound is False and hasattr(i1[2], 'nameB'):
                    if 'gone' in i1[2].nameB:
                        im_new.append('default-A')
                        bFound = True
                if bFound is False and hasattr(i1[3], 'nameB'):
                    if 'gone' in i1[3].nameB:
                        im_new.append('default-A')
                        bFound = True
                if bFound is False:
                    im_new.append('un')
                    print 'undefined'
            elif i1[4] == '105.4':  # star
                im_new.append('default-star')
                im_new.append('un')
                print 'undefined'
            else:
                im_new.append(i1[4])
                bFound = False
                if hasattr(i1[0], 'nameB'):
                    if 'gone' in i1[0].nameB:
                        im_new.append(i1[4])
                        bFound = True
                if bFound is False and hasattr(i1[1], 'nameB'):
                    if 'gone' in i1[1].nameB:
                        im_new.append(i1[4])
                        bFound = True
                if bFound is False and hasattr(i1[2], 'nameB'):
                    if 'gone' in i1[2].nameB:
                        im_new.append(i1[4])
                        bFound = True
                if bFound is False and hasattr(i1[3], 'nameB'):
                    if 'gone' in i1[3].nameB:
                        im_new.append(i1[4])
                        bFound = True
                if bFound is False:
                    im_new.append('un')
                    print 'undefined'
            new_ii.append(im_new)

    for i2 in im2:
        if i2 not in done_i2:
            print("unmatched impropers B: ", i2[0].name, i2[1].name,
                  i2[2].name, i2[3].name)
            im_new = i2[:4]
            if i2[4] == '':
                if ((i2[0].name.startswith('D')) or (i2[1].name.startswith('D')) or
                   (i2[2].name.startswith('D')) or (i2[3].name.startswith('D')) or
                   (i2[0].name.startswith('HV')) or (i2[1].name.startswith('HV')) or
                   (i2[2].name.startswith('HV')) or (i2[3].name.startswith('HV'))):
                    im_new.append('default-B')
                else:
                    im_new.append('un')
                    print 'undefined'
                im_new.append('default-B')
            elif i2[4] == '105.4':  # star
                im_new.append('un')
                im_new.append('default-star')
                print 'undefined'
            else:
                if ((i2[0].name.startswith('D')) or (i2[1].name.startswith('D')) or
                   (i2[2].name.startswith('D')) or (i2[3].name.startswith('D')) or
                   (i2[0].name.startswith('HV')) or (i2[1].name.startswith('HV')) or
                   (i2[2].name.startswith('HV')) or (i2[3].name.startswith('HV'))):
                    im_new.append(i2[4])
                else:
                    im_new.append('un')
                    print 'undefined'
                im_new.append(i2[4])
            new_ii.append(im_new)

    return new_ii


def write_rtp(fp, r, ii_list, dihi_list, neigh_bonds, cmap):
    print >>fp, '\n[ %s ] ; %s -> %s\n' % (r.resname, r.resnA, r.resnB)
    print >>fp, ' [ atoms ]'
    cgnr = 1
    for atom in r.atoms:
        print >>fp, "%6s   %-15s  %8.5f  %d" % (atom.name, atom.atomtype, atom.q, cgnr)
        cgnr += 1
    print >>fp, '\n [ bonds ]'
    for atom in r.atoms:
        for at in atom.bonds:
            if atom.id < at.id:
                print >>fp, "%6s  %6s ; (%6s  %6s)" % (atom.name, at.name, atom.nameB, at.nameB)
    # here there will have to be a check for FF, since for charmm we need to add C N
    # save those bonds with previous and next residue as a seperate entry
    for i in neigh_bonds:
        print >>fp, "%6s  %6s  " % (i[0], i[1])

    print >>fp, '\n [ impropers ]'
    for ii in ii_list:
        if not ii[4].startswith('default'):
            print >>fp, "%6s  %6s  %6s  %6s  %-25s" % (ii[0].name, ii[1].name, ii[2].name, ii[3].name, ii[4])
        else:
            print >>fp, "%6s  %6s  %6s  %6s " % (ii[0].name, ii[1].name, ii[2].name, ii[3].name)

    print >>fp, '\n [ dihedrals ]'
    for ii in dihi_list:
        if not ii[4].startswith('default'):
            print >>fp, "%6s  %6s  %6s  %6s  %-25s" % (ii[0].name, ii[1].name, ii[2].name, ii[3].name, ii[4])
        else:
            print >>fp, "%6s  %6s  %6s  %6s " % (ii[0].name, ii[1].name, ii[2].name, ii[3].name)
    if cmap:
        print >>fp, '\n [ cmap ]'
    for i in cmap:
        print >>fp, "%s  " % (i)


def write_mtp(fp, r, ii_list, rotations, dihi_list):
    print >>fp, '\n[ %s ] ; %s -> %s\n' % (r.resname, r.resnA, r.resnB)
    print >>fp, '\n [ morphes ]'
    for atom in r.atoms:
        print >>fp, "%6s %10s -> %6s %10s" % (atom.name, atom.atomtype, atom.nameB, atom.atomtypeB)
    print >>fp, '\n [ atoms ]'
    cgnr = 1
    for atom in r.atoms:
        ext = ' ; '
        if atom.atomtype != atom.atomtypeB:
            ext += ' types != '
        else:
            ext += ' types == '
        if atom.q != atom.qB:
            ext += '| charge != '
        else:
            ext += '| charge == '

        print >>fp, "%8s %10s %10.6f %6d %10.6f %10s %10.6f %10.6f  %-10s" % \
              (atom.name, atom.atomtype, atom.q, cgnr, atom.m,
               atom.atomtypeB, atom.qB, atom.mB, ext)
    print >>fp, '\n [ coords ]'
    for atom in r.atoms:
        print >>fp, "%8.3f %8.3f %8.3f" % (atom.x[0], atom.x[1], atom.x[2])

    print >>fp, '\n [ impropers ]'
    for ii in ii_list:
        print >>fp, " %6s %6s %6s %6s     %-25s %-25s  " % \
              (ii[0].name, ii[1].name, ii[2].name, ii[3].name, ii[4], ii[5])
    print

    print >>fp, '\n [ dihedrals ]'
    for ii in dihi_list:
        print >>fp, " %6s %6s %6s %6s     %-25s %-25s  " % \
              (ii[0].name, ii[1].name, ii[2].name, ii[3].name, ii[4], ii[5])
    print

    if rotations:
        print >>fp, '\n [ rotations ]'
        for rot in rotations:
            print >>fp, '  %s-%s %s' % (rot[0].name, rot[1].name, ' '.join(map(lambda a: a.name, rot[2:])))
        print >>fp


def primitive_check(atom, rot_atom):
    if atom in rot_atom.bonds:
        return True
    else:
        return False


def find_higher_atoms(rot_atom, r, order, branch):
    res = []
    for atom in r.atoms:
        print "1level: %s %s %s" % (atom.name, atom.order, atom.branch)
        if (('gone' in rot_atom.nameB) and (atom.name.startswith('D') or
           atom.name.startswith('HV'))):
            continue
        if atom.order >= order:
            print "2level: %s %s %s" % (atom.name, atom.order, atom.branch)
            if atom.order == rot_atom.order+1:
                print "3level: %s %s %s" % (atom.name, atom.order, atom.branch)
                if primitive_check(atom, rot_atom):
                    print "4level: %s %s %s" % (atom.name, atom.order, atom.branch)
                    res.append(atom)
            else:
                res.append(atom)
    return res


def make_rotations(r, resn1_dih, resn2_dih):
    dihed1 = get_dihedrals(resn1_dih)
    dihed2 = get_dihedrals(resn2_dih)  # FIXME: unused variable?
    rots = []
    done = []
    for d in dihed1:
        if d[-2] != 0 and d[-1] > 0:
            key = d[1]+'-'+d[2]
            if key not in done:
                rots.append(d)
                done.append(key)
    for d in dihed1:
        if d[-2] != 0 and d[-1] != 0 and d[2] not in ['N', 'C', 'CA']:
            key = d[1]+'-'+d[2]
            if key not in done:
                rots.append(d)
                done.append(key)

    rotations = []
    for chi in rots:
        rot_list = []
        atom1 = r.fetchm(chi)[1]
        atom2 = r.fetchm(chi)[2]
        rot_list.append(atom1)
        rot_list.append(atom2)
        oo = atom2.order
        bb = atom2.branch
        print "AAAAAAAAA %s %s %s" % (atom2, oo+1, bb)
        atoms_to_rotate = []
        atoms_to_rotate = find_higher_atoms(atom2,  r, oo+1, bb)
        for atom in atoms_to_rotate:
            rot_list.append(atom)
        rotations.append(rot_list)
    return rotations


def parse_ffnonbonded_charmm(ffnonbonded, f):
    ifile = open(ffnonbonded, 'r')
    lines = ifile.readlines()
    # now clean the heavy atom entries from file and write it to temp file
    bAdd = True
    for line in lines:
        if line.strip() == '#ifdef HEAVY_H':
            bAdd = False
        if bAdd and line[0] != '#':
            f.write(line)
        if line.strip() == '#else':
            bAdd = True
        if line.strip() == '#endif':
            bAdd = True


def assign_mass(r1, r2, ffnonbonded, bCharmm, ff):
    # open ffnonbonded, remove HEAVY_H, pass it to NBParser
    if bCharmm:
        f = tempfile.NamedTemporaryFile(delete=False)
        parse_ffnonbonded_charmm(ffnonbonded, f)
        print f.name
        NBParams = NBParser(f.name, 'new', ff)
        f.close()
    else:
        NBParams = NBParser(ffnonbonded, 'new', ff)
    for atom in r1.atoms+r2.atoms:
        atom.m = NBParams.atomtypes[atom.atomtype]['mass']


def assign_mass_atp(r1, r2, ffatomtypes):
    fp = open(ffatomtypes, "r")
    lst = fp.readlines()
    lst = kickOutComments(lst, ';')
    fp.close()
    mass = {}
    for l in lst:
        foo = l.split()
        mass[foo[0]] = float(foo[1])
    for atom in r1.atoms+r2.atoms:
        atom.m = mass[atom.atomtype]


def rename_to_gmx(r):
    for atom in r1.atoms:
        if atom.name[0].isdigit():
            atom.name = atom.name[1:]+atom.name[0]
        if atom.nameB[0].isdigit():
            atom.nameB = atom.nameB[1:]+atom.nameB[0]
        if atom.name[0] == 'D' and atom.name[1].isdigit():
            atom.name = atom.name[0]+atom.name[2:]+atom.name[1]
        if atom.nameB[0] == 'D' and atom.nameB[1].isdigit():
            atom.nameB = atom.nameB[0]+atom.nameB[2:]+atom.nameB[1]
    res = False
    while not res:
        res = check_double_atom_names(r)


def rename_to_match_library(m, bCharmm=False):
    name_hash = {}
    for atom in m.atoms:
        foo = atom.name
        if atom.name[0].isdigit():
            atom.name = atom.name[1:]+atom.name[0]
        if bCharmm:
            print atom.name
            if atom.resname == 'CYS' and atom.name == 'HG1':
                atom.name = 'HG'
            if atom.resname == 'SER' and atom.name == 'HG1':
                atom.name = 'HG'
        name_hash[atom.name] = foo
    return name_hash


def rename_back(m, name_hash):
    for atom in m.atoms:
        atom.name = name_hash[atom.name]


def reformat_atom_name(name):
    if name[0].isdigit():
        name = name[1:]+name[0]
    return name


def improps_as_atoms(im, r, use_b=False):
    im_new = []
    for ii in im:
        atom_names = ii[:4]
        new_ii = []
        for name in atom_names:
            if name[0] in ['+', '-']:
                a = Atom(name=name)
            else:
                if use_b:
                    for atom in r.atoms:
                        if atom.nameB == name:
                            a = atom
                else:
                    print name
                    a = r.fetch(name)[0]
            new_ii.append(a)
        new_ii.extend(ii[4:])
        im_new.append(new_ii)
    return im_new


def read_nbitp(fn):
    lines = open(fn, 'r').readlines()
    lines = kickOutComments(lines, ';')
    lines = kickOutComments(lines, '#')
    lines = readSection(lines, '[ atomtypes ]', '[')
    lines = parseList('ssiffsff', lines)
    dic = {}
    for entry in lines:
        dic[entry[0]] = entry[1:]
    return dic


def write_atp_fnb(fn_atp, fn_nb, r, ff, ffpath):
    types = []
    if os.path.isfile(fn_atp):
        ifile = open(fn_atp, 'r')
        for line in ifile:
            line = line.lstrip()
            if (not (line.startswith(';') or line.startswith('#') or (line.strip() == ''))):
                sp = line.split()
                types.append(sp[0])
        ifile.close()
    if os.path.isfile(fn_atp):
        ofile = open(fn_atp, 'a')
    else:
        ofile = open(fn_atp, 'w')

    for atom in r.atoms:
        if atom.atomtype[0:3] == 'DUM':
            if atom.atomtype not in types:
                ofile.write("%-6s  %10.6f\n" % (atom.atomtype, atom.m))
                types.append(atom.atomtype)
        if atom.atomtypeB[0:3] == 'DUM':
            if atom.atomtypeB not in types:
                ofile.write("%-6s  %10.6f\n" % (atom.atomtypeB, atom.mB))
                types.append(atom.atomtypeB)
    ofile.close()

    types = []
    if os.path.isfile(fn_nb):
        ifile = open(fn_nb, 'r')
        for line in ifile:
            line = line.lstrip()
            if (not (line.startswith(';') or line.startswith('#') or (line.strip() == ''))):
                sp = line.split()
                types.append(sp[0])
        ifile.close()
    if os.path.isfile(fn_nb):
        ofile = open(fn_nb, 'a')
    else:
        ofile = open(fn_nb, 'w')
    print types

    # for opls need to extract the atom name
    ffnamelower = ff.lower()
    if 'opls' in ffnamelower:
        dum_real_name = read_nbitp(os.path.join(ffpath, 'ffnonbonded.itp'))

    for atom in r.atoms:
        if atom.atomtype[0:3] == 'DUM':
            if atom.atomtype not in types:
                if 'opls' in ffnamelower:
                    foo = dum_real_name['opls_'+atom.atomtype.split('_')[2]]
                    ofile.write("%-13s\t\t%3s\t0\t%4.2f\t   0.0000  A   0.00000e+00 0.00000e+00\n" \
                                % (atom.atomtype, foo[0], atom.m))
                else:
                    ofile.write("%-10s\t0\t%4.2f\t   0.0000  A   0.00000e+00 0.00000e+00\n" \
                                % (atom.atomtype, atom.m))
                types.append(atom.atomtype)
        if atom.atomtypeB[0:3] == 'DUM':
            if atom.atomtypeB not in types:
                if 'opls' in ffnamelower:
                    foo = dum_real_name['opls_'+atom.atomtypeB.split('_')[2]]
                    ofile.write("%-13s\t\t%3s\t0\t%4.2f\t   0.0000  A   0.00000e+00 0.00000e+00\n" \
                                % (atom.atomtypeB, foo[0], atom.mB))
                else:
                    ofile.write("%-10s\t0\t%4.2f\t   0.0000  A   0.00000e+00 0.00000e+00\n" \
                                % (atom.atomtypeB, atom.mB))
                types.append(atom.atomtypeB)
    ofile.close()


# charmm uses HN instead of H for backbone H on N
def rename_atoms_charmm(m):
    for atom in m.atoms:
        if atom.name == 'H':
            atom.name = 'HN'
        if atom.name == 'HG' and atom.resname == 'CYS':
            atom.name = '1HG'
        if atom.name == 'HG' and atom.resname == 'SER':
            atom.name = '1HG'


def rename_res_charmm(m):
    rename = {'HIE': 'HSE', 'HID': 'HSD', 'HIP': 'HSP', 'ASH': 'ASPP',
              'GLH': 'GLUP', 'LYN': 'LSN'}
    for res in m.residues:
        if res.resname in rename:
            res.resname = rename[res.resname]
            for atom in res.atoms:
                atom.resname = res.resname


# =============
# Input Options
# =============
def parse_options():
    parser = argparse.ArgumentParser(description='''
The script creates hybrid structure and topology database entries (mtp and rtp).
Input: two pdb files aligned on the backbone and path to the force field files.
Output: hybrid structure, hybrid topology entries as .rtp and .mtp files.
Also, atomtype and non-bonded parameter files for the introduced dummies are generated
''')

    parser.add_argument('-pdb1',
                        metavar='pdb1',
                        dest='pdb1',
                        type=str,
                        help='',
                        default='a1.pdb')
    parser.add_argument('-pdb2',
                        metavar='pdb2',
                        dest='pdb2',
                        type=str,
                        help='',
                        default='a2.pdb')
    parser.add_argument('-opdb1',
                        metavar='opdb1',
                        dest='opdb1',
                        type=str,
                        help='',
                        default='r1.pdb')
    parser.add_argument('-opdb2',
                        metavar='opdb2',
                        dest='opdb2',
                        type=str,
                        help='',
                        default='r2.pdb')
    parser.add_argument('-ff',
                        metavar='ff',
                        dest='ff',
                        type=str,
                        help='path to mutation forcefield',
                        default='')
    parser.add_argument('-fatp',
                        metavar='fatp',
                        dest='fatp',
                        type=str,
                        help='',
                        default='types.atp')
    parser.add_argument('-fnb',
                        metavar='fnb',
                        dest='fnb',
                        type=str,
                        help='',
                        default='fnb.itp')
    # Options
    parser.add_argument('--moltype',
                        metavar='moltype',
                        dest='moltype',
                        type=str.lower,
                        help='protein, dna, rna',
                        choices=['protein', 'dna', 'rna'],
                        default='protein')
    parser.add_argument('--noalign',
                        dest='align',
                        help='',
                        default=True,
                        action='store_false')
    parser.add_argument('--cbeta',
                        dest='cbeta',
                        help='',
                        default=False,
                        action='store_true')
    parser.add_argument('--noH2H',
                        dest='h2heavy',
                        help='',
                        default=True,
                        action='store_false')

    args, unknown = parser.parse_known_args()
    return args


#
# MAIN
#
# TODO list:
# 1) try simplify functions args
# 2) make main a func
# 3) automate generation of whole library
#

args = parse_options()

align = args.align
cbeta = args.cbeta
bH2heavy = args.h2heavy
moltype = args.moltype
ffpath = args.ff  # relative path of force field folder
# infer name of ff from the folder name
ffname = os.path.abspath(args.ff).split('/')[-1].split('.')[0]

if "charmm" in ffname:
    bCharmm = True
else:
    bCharmm = False

if moltype == 'dna':
    rtpfile = os.path.join(ffpath, 'dna.rtp')
elif moltype == 'rna':
    rtpfile = os.path.join(ffpath, 'rna.rtp')
elif moltype == 'protein':
    rtpfile = os.path.join(ffpath, 'aminoacids.rtp')

# Create Models
m1 = Model(args.pdb1)
m2 = Model(args.pdb2)
# check models
assert len(m1.residues) == 1
assert len(m2.residues) == 1
# Get 3-letter resname from models
nm1 = m1.residues[0].resname
nm2 = m2.residues[0].resname
# Convert 3-letter names to 1-letter ones
aa1 = _ext_one_letter[nm1]
aa2 = _ext_one_letter[nm2]


if moltype == 'protein':
    rr_name = aa1 + '2' + aa2
elif moltype == 'dna':
    rr_name = _dna_mutation_naming(aa1, aa2)
elif moltype == 'rna':
    rr_name = _rna_mutation_naming(aa1, aa2)

# Get element of all atoms in models
m1.get_symbol()
m2.get_symbol()

# get order (number of bonds away from mainchain) if protein library
if moltype == 'protein':
    m1.get_order()
    m2.get_order()

# rename atoms
if moltype == 'protein':
    m1.rename_atoms()
    m2.rename_atoms()
elif moltype in ['dna', 'rna']:
    _rename_atoms_nucleic_acids(m1)
    _rename_atoms_nucleic_acids(m2)

if bCharmm is True:
    rename_atoms_charmm(m1)
    rename_atoms_charmm(m2)
    rename_res_charmm(m1)
    rename_res_charmm(m2)

r1 = m1.residues[0]
r2 = m2.residues[0]

if moltype not in ['dna', 'rna']:
    r1.get_mol2_types()
    r2.get_mol2_types()
r1.get_real_resname()
r2.get_real_resname()

if align is True:
    align_sidechains(r1, r2)

r1.resnA = r1.resname[0] + r1.resname[1:].lower()
r1.resnB = r2.resname[0] + r2.resname[1:].lower()

rtp = RTPParser(rtpfile)
bond_neigh = assign_rtp_entries(r1, rtp)
assign_rtp_entries(r2, rtp)
assign_mass_atp(r1, r2, os.path.join(ffpath, 'atomtypes.atp'))


# ------------------------------
# figure out degenerate resnames
# ------------------------------

# TODO: these apply only to proteins, no need to go through this for DNA/RNA
resn1_dih = m1.residues[0].resname
if (resn1_dih == 'HIS' or resn1_dih == 'HID' or resn1_dih == 'HIE' or
   resn1_dih == 'HIP' or resn1_dih == 'HISE' or resn1_dih == 'HISD' or
   resn1_dih == 'HISH' or resn1_dih == 'HIS1' or resn1_dih == 'HSD' or
   resn1_dih == 'HSE' or resn1_dih == 'HSP'):
    resn1_dih = 'HIS'
elif resn1_dih == 'LYN' or resn1_dih == 'LYSH' or resn1_dih == 'LSN':
    resn1_dih = 'LYS'
elif resn1_dih == 'ASH' or resn1_dih == 'ASPH' or resn1_dih == 'ASPP':
    resn1_dih = 'ASP'
elif resn1_dih == 'GLH' or resn1_dih == 'GLUH' or resn1_dih == 'GLUP':
    resn1_dih = 'GLU'
elif resn1_dih == 'CYSH':
    resn1_dih = 'CYS'

resn2_dih = m2.residues[0].resname
if (resn2_dih == 'HIS' or resn2_dih == 'HID' or resn2_dih == 'HIE' or
   resn2_dih == 'HIP' or resn2_dih == 'HISE' or resn2_dih == 'HISD' or
   resn2_dih == 'HISH' or resn2_dih == 'HIS1' or resn2_dih == 'HSD' or
   resn2_dih == 'HSE' or resn2_dih == 'HSP'):
    resn2_dih = 'HIS'
elif resn2_dih == 'LYN' or resn2_dih == 'LYSH' or resn2_dih == 'LSN':
    resn2_dih = 'LYS'
elif resn2_dih == 'ASH' or resn2_dih == 'ASPH' or resn2_dih == 'ASPP':
    resn2_dih = 'ASP'
elif resn2_dih == 'GLH' or resn2_dih == 'GLUH' or resn2_dih == 'GLUP':
    resn2_dih = 'GLU'
elif resn2_dih == 'CYSH':
    resn2_dih = 'CYS'
#######################

hash1 = {}
hash2 = {}
if align is True and moltype not in ['dna', 'rna']:
    dihed1 = get_dihedrals(resn1_dih)
    dihed2 = get_dihedrals(resn2_dih)
    max_rot = max_rotation(dihed2)
    max_rot1 = max_rotation(dihed1)

    for atom in m2.atoms:
        atom.max_rot = max_rot
    for atom in m1.atoms:
        atom.max_rot = max_rot1
    hash1 = rename_to_match_library(m1, bCharmm)
    hash2 = rename_to_match_library(m2, bCharmm)
    do_fit(m1.residues[0], dihed1, m2.residues[0], dihed2)
    rename_back(m1, hash1)
    rename_back(m2, hash2)

r1.write(args.opdb1)
r2.write(args.opdb2)

assign_branch(r1)
assign_branch(r2)


# ==============================================================================
#                            selecting pair lists
# ==============================================================================

# -------------
# nucleic acids
# -------------
if moltype == 'dna':
    if ((('5' in r1.resname) and ('5' not in r2.resname)) or
       (('3' in r1.resname) and ('3' not in r2.resname)) or
       (('5' in r2.resname) and ('5' not in r1.resname)) or
       (('3' in r2.resname) and ('3' not in r1.resname))):
        print("Cannot mutate terminal nucleic acid to non-terminal or a "
              "terminal of the other end (e.g. 5' to 3')")
        sys.exit(0)
    if r1.resname in use_standard_dna_pair_list and r2.resname in use_standard_dna_pair_list[r1.resname]:
        print "PURINE <-> PYRIMIDINE"
        if bCharmm:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_dna_pair_list_charmm)
        else:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_dna_pair_list)
    elif r1.resname in use_standard_dna_5term_pair_list and r2.resname in use_standard_dna_5term_pair_list[r1.resname]:
        print "PURINE <-> PYRIMIDINE: 5term"
        if bCharmm:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_dna_5term_pair_list_charmm)
        else:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_dna_5term_pair_list)
    elif r1.resname in use_standard_dna_3term_pair_list and r2.resname in use_standard_dna_3term_pair_list[r1.resname]:
        print "PURINE <-> PYRIMIDINE: 3term"
        if bCharmm:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_dna_3term_pair_list_charmm)
        else:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_dna_3term_pair_list)
    else:
        print "PURINE <-> PURINE	PYRIMIDINE <-> PYRIMIDINE"
        atom_pairs, dummies = make_pairs(r1, r2, bCharmm, bH2heavy, bDNA=True)

elif moltype == 'rna':
    if ((('5' in r1.resname) and ('5' not in r2.resname)) or
       (('3' in r1.resname) and ('3' not in r2.resname)) or
       (('5' in r2.resname) and ('5' not in r1.resname)) or
       (('3' in r2.resname) and ('3' not in r1.resname))):
        print "Cannot mutate terminal nucleic acid to non-terminal or a terminal of the other end (e.g. 5' to 3')"
        sys.exit(0)
    if r1.resname in use_standard_rna_pair_list and r2.resname in use_standard_rna_pair_list[r1.resname]:
        print "PURINE <-> PYRIMIDINE"
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_rna_pair_list)
    elif r1.resname in use_standard_rna_5term_pair_list and r2.resname in use_standard_rna_5term_pair_list[r1.resname]:
        print "PURINE <-> PYRIMIDINE: 5term"
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_rna_5term_pair_list)
    elif r1.resname in use_standard_rna_3term_pair_list and r2.resname in use_standard_rna_3term_pair_list[r1.resname]:
        print "PURINE <-> PYRIMIDINE: 3term"
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_rna_3term_pair_list)
    else:
        print "PURINE <-> PURINE	PYRIMIDINE <-> PYRIMIDINE"
        atom_pairs, dummies = make_pairs(r1, r2, bCharmm, bH2heavy, bDNA=False, bRNA=True)

# -------------
# nucleic acids
# -------------

# ring-res 2 ring-res
elif r1.resname in use_standard_pair_list and r2.resname in use_standard_pair_list[r1.resname]:
    print "ENTERED STANDARD"
    if bCharmm:
        if cbeta:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmmC)
        else:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmm)
    else:
        if cbeta:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listC)
        else:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list)

# ring-res 2 non-ring-res: T,A,V,I
elif (r1.resname in res_with_rings and r2.resname in res_diff_Cb) or \
     (r2.resname in res_with_rings and r1.resname in res_diff_Cb):
    print "ENTERED T,A,V,I"
    if bCharmm:
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmmC)
    else:
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listC)

# proline
elif (r1.resname in res_pro) or (r2.resname in res_pro):
    print "ENTERED P"
    if (r1.resname in res_gly) or (r2.resname in res_gly):
        print "subENTERED G"
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listGlyPro)
    else:
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listPro)
# glycine
elif r1.resname in res_gly or r2.resname in res_gly:
    print "ENTERED G"
    if bCharmm:
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmmD)
    else:
        atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listD)

# ringed residues by atom names
elif r1.resname in merge_by_name_list and r2.resname in merge_by_name_list[r1.resname]:
    if cbeta:
        if bCharmm:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmmC)
        else:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listC)
    else:
        print "ENTERED MERGE BY NAMES"
        atom_pairs, dummies = merge_by_names(r1, r2)

# ring-res 2 non-ring-res
elif r1.resname in res_with_rings or r2.resname in res_with_rings:
    print "ENTERED RINGS"
    if bCharmm:
        if cbeta:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmmC)
        else:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmmB)
    else:
        if cbeta:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listC)
        else:
            atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listB)
else:
    print "ENTERED SIMPLE"
    if cbeta:
        if r1.resname == 'GLY' or r2.resname == 'GLY':
            if bCharmm:
                atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmmD)
            else:
                atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listD)
        else:
            if bCharmm:
                atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_list_charmmC)
            else:
                atom_pairs, dummies = make_predefined_pairs(r1, r2, standard_pair_listC)
    else:
        atom_pairs, dummies = make_pairs(r1, r2, bCharmm, bH2heavy)
# ==============================================================================


merge_molecules(r1, dummies)
make_bstate_dummies(r1)

write_atp_fnb(args.fatp, args.fnb, r1, ffname, ffpath)
abdic, badic = make_transition_dics(atom_pairs, r1)

update_bond_lists(r1, badic)

# CMAP for charmm
# dihedrals are necessary for ILDN
dih_1 = rtp[r1.resname]['diheds']
dih_2 = rtp[r2.resname]['diheds']

dih1 = improps_as_atoms(dih_1, r1)  # it's alright, can use improper function
dih2 = improps_as_atoms(dih_2, r1, use_b=True)

# here go impropers
im_1 = rtp[r1.resname]['improps']
im_2 = rtp[r2.resname]['improps']

im1 = improps_as_atoms(im_1, r1)
im2 = improps_as_atoms(im_2, r1, use_b=True)

# cmap
cmap = []
if bCharmm:
    cmap = rtp[r1.resname]['cmap']

# dihedrals
dihi_list = generate_dihedral_entries(dih1, dih2, r1, atom_pairs)

# impropers
ii_list = generate_improp_entries(im1, im2, r1)

if moltype not in ['dna', 'rna']:
    rot = make_rotations(r1, resn1_dih, resn2_dih)

r1.set_resname(rr_name)
rename_to_gmx(r1)

rtp_out = open(rr_name+'.rtp', 'w')
write_rtp(rtp_out, r1, ii_list, dihi_list, bond_neigh, cmap)
r1.write(rr_name + '.pdb')
mtp_out = open(rr_name+'.mtp', 'w')

if moltype in ['dna', 'rna']:
    write_mtp(mtp_out, r1, ii_list, False, dihi_list)
else:
    write_mtp(mtp_out, r1, ii_list, rot, dihi_list)
