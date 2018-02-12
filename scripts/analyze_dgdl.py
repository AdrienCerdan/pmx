#!/usr/bin/env python
# pmx  Copyright Notice
# ============================
#
# The pmx source code is copyrighted, but you can freely use and
# copy it as long as you don't change or remove any of the copyright
# notices.
#
# ----------------------------------------------------------------------
# pmx is Copyright (C) 2006-2017 by Daniel Seeliger
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name of Daniel Seeliger not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# DANIEL SEELIGER DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS.  IN NO EVENT SHALL DANIEL SEELIGER BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------

from __future__ import print_function, division
from pmx.parser import read_and_format
from pmx.estimators import Jarz, Crooks, BAR, ks_norm_test
from pmx.analysis import read_dgdl_files, make_cgi_plot
import sys
import os
import time
import re
import numpy as np
import pickle
import argparse

# Constants
kb = 0.00831447215   # kJ/(K*mol)


# ==============================================================================
#                               FUNCTIONS
# ==============================================================================
def _dump_integ_file(outfn, f_lst, w_lst):
    with open(outfn, 'w') as f:
        for fn, w in zip(f_lst, w_lst):
            f.write('{dhdl} {work}\n'.format(dhdl=fn, work=w))


def _data_from_file(fn):
    data = read_and_format(fn, 'sf')
    return map(lambda a: a[1], data)


def _tee(fp, s):
    print(s, file=fp)
    print(s)


def _natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def _time_stats(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


# ==============================================================================
#                      COMMAND LINE OPTIONS AND MAIN
# ==============================================================================
def parse_options():

    parser = argparse.ArgumentParser(description='Calculates free energies '
            'from fast growth thermodynamic integration simulations. '
            'Available methods for free energy estimation: '
            'Crooks Gaussian Intersection (CGI); '
            'Benett Acceptance Ratio (BAR); '
            'Jarzinski equality (JARZ).')

    exclus = parser.add_mutually_exclusive_group()

    parser.add_argument('-fA',
                        metavar='dgdl',
                        dest='filesAB',
                        type=str,
                        help='dgdl.xvg files for the A->B simulations. Use '
                        'wildcard to select multiple xvg files: e.g. "-fa '
                        './forward_results/dgdl*.xvg"',
                        required=True,
                        nargs='+')
    parser.add_argument('-fB',
                        metavar='dgdl',
                        dest='filesBA',
                        type=str,
                        help='dgdl.xvg files for the B->A simulations Use '
                        'wildcard to select multiple xvg files: e.g. "-fb '
                        './backward_results/dgdl*.xvg"',
                        required=True,
                        nargs='+')
    parser.add_argument('-m',
                        metavar='method',
                        type=str.lower,
                        dest='methods',
                        help='Choose one or more estimators to use from the '
                        'available ones: CGI, BAR, JARZ. Default is all.',
                        default=['cgi', 'bar', 'jarz'],
                        nargs='+')
    parser.add_argument('-t',
                        metavar='temperature',
                        dest='temperature',
                        type=float,
                        help='Temperature in Kelvin. Default is 298.15.',
                        default=298.15)
    parser.add_argument('-o',
                        metavar='result file',
                        dest='outfn',
                        type=str,
                        help='Filename of output result file. Default is '
                        '"results.txt."',
                        default='results.txt')
    parser.add_argument('-b',
                        metavar='nboots',
                        dest='nboots',
                        type=int,
                        help='Number of bootstrap samples to use for the '
                        'bootstrap estimate of the standard errors. Default '
                        'is 0 (no bootstrap).',
                        default=0)
    parser.add_argument('-n',
                        metavar='nblocks',
                        dest='nblocks',
                        type=int,
                        help='Number of blocks to divide the data into for '
                        'an estimate of the standard error. You can use this '
                        'when multiple independent equilibrium simulations'
                        'have been run so to estimate the error from the '
                        'repeats. Default is 1 (i.e. no repeats). It assumes '
                        'the dgdl files for each repeat are read in order and '
                        'are contiguous, e.g. dgdl_0 to dgdl_9 is the first '
                        'repeat, dgdl_10 to dgdl_19 is the second one, etc.',
                        default=1)
    parser.add_argument('--integ_only',
                        dest='integ_only',
                        help='Whether to do integration only; the integrated '
                        'values are computed and saved, and the program '
                        'terminated. Default is False.',
                        default=False,
                        action='store_true')
    parser.add_argument('-iA',
                        metavar='work input',
                        dest='iA',
                        type=str,
                        help='Two-column dat file containing the list of input'
                        ' files and their respective integrated work values '
                        'for the forward (A->B) tranformation.')
    parser.add_argument('-iB',
                        metavar='work input',
                        dest='iB',
                        type=str,
                        help='Two-column dat file containing the list of input'
                        ' files and their respective integrated work values '
                        'for the reverse (B->A) tranformation.')
    parser.add_argument('-oA',
                        metavar='work output',
                        dest='oA',
                        type=str,
                        help='File where to save the list of input dgdl'
                        ' files and their respective integrated work values '
                        'for the forward (A->B) tranformation. Default is '
                        '"integA.dat"',
                        default='integA.dat')
    parser.add_argument('-oB',
                        metavar='work output',
                        dest='oB',
                        type=str,
                        help='File where to save the list of input dgdl'
                        ' files and their respective integrated work values '
                        'for the reverse (B->A) tranformation. Default is '
                        '"integB.dat"',
                        default='integB.dat')
    parser.add_argument('--reverseB',
                        dest='reverseB',
                        help='Whether to reverse the work values for the '
                        'backward (B->A) transformation. This is useful '
                        'when in Gromacs both forward and reverse simulations '
                        'were run from lambda zero to one.'
                        'Default is False.',
                        default=False,
                        action='store_true')
    # The following are mutually exclusive options
    exclus.add_argument('--skip',
                        metavar='',
                        dest='skip',
                        type=int,
                        help='Skip files, i.e. pick every nth work value. '
                        'Default is 1 (all); with 2, every other work value '
                        'is discarded, etc.',
                        default=1)
    exclus.add_argument('--slice',
                        metavar='',
                        dest='slice',
                        type=int,
                        help='Subset of trajectories to analyze.'
                        'Provide list slice, e.g. "10 50" will'
                        ' result in selecting dgdl_files[10:50].'
                        ' Default is all.',
                        default=None,
                        nargs=2)
    exclus.add_argument('--rand',
                        metavar='',
                        dest='rand',
                        type=int,
                        help='Take a random subset of trajectories. '
                        'Default is None (do not take random subset)',
                        default=None)
    exclus.add_argument('--index',
                        metavar='',
                        dest='index',
                        type=int,
                        help='Zero-based index of files to analyze (e.g.'
                        ' 0 10 20 50 60). It keeps '
                        'the dgdl.xvg files according to their position in the'
                        ' list, sorted according to the filenames. Default '
                        'is None (i.e. all dgdl are used).',
                        default=None,
                        nargs='+')
    parser.add_argument('--prec',
                        metavar='',
                        dest='precision',
                        type=int,
                        help='The decimal precision of the screen/file output.'
                        ' Default is 2.',
                        default=2)
    parser.add_argument('--units',
                        metavar='',
                        dest='units',
                        type=str.lower,
                        help='The units of the output. Choose from "kJ", '
                        '"kcal", "kT". Default is "kJ."',
                        default='kJ',
                        choices=['kj', 'kcal', 'kt'])
    parser.add_argument('--pickle',
                        dest='pickle',
                        help='Whether to save the free energy results from '
                        'the estimators in pickled files. Default is False.',
                        default=False,
                        action='store_true')
    parser.add_argument('--no_ks',
                        dest='do_ks_test',
                        help='Whether to do a Kolmogorov-Smirnov test '
                        'to check whether the Gaussian assumption for CGI '
                        'holds. Default is True; this flag turns it to False.',
                        default=True,
                        action='store_false')
    parser.add_argument('--cgi_plot',
                        metavar='',
                        dest='cgi_plot',
                        type=str,
                        help='Whether to plot the work histograms along with '
                        'the CGI results. If the flag is used, you also need'
                        'to specify a filename.',
                        default=None)
    parser.add_argument('--nbins',
                        metavar='',
                        dest='nbins',
                        type=int,
                        help='Number of histograms bins for the plot. '
                        'Default is 10.',
                        default=10)
    parser.add_argument('--dpi',
                        metavar='',
                        dest='dpi',
                        type=int,
                        help='Resolution of the plot. Default is 300.',
                        default=300)

    args = parser.parse_args()

    from pmx import __version__
    args.pmx_version = __version__

    return args


# ==============================================================================
#                               FUNCTIONS
# ==============================================================================
def main(args):
    """Run the main script.

    Parameters
    ----------
    args : argparse.Namespace
        The command line arguments
    """

    # start timing
    stime = time.time()

    # input arguments
    out = open(args.outfn, 'w')
    filesAB = _natural_sort(args.filesAB)
    filesBA = _natural_sort(args.filesBA)
    T = args.temperature
    skip = args.skip
    prec = args.precision
    methods = args.methods
    reverseB = args.reverseB
    integ_only = args.integ_only
    nboots = args.nboots
    nblocks = args.nblocks
    do_ks_test = args.do_ks_test

    # -------------------
    # Select output units
    # -------------------
    units = args.units
    if units.lower() == 'kj':
        # kJ is the input from GMX
        unit_fact = 1.
        units = 'kJ/mol'
    elif units == 'kcal':
        unit_fact = 1./4.184
        units = 'kcal/mol'
    elif units.lower() == 'kt':
        unit_fact = 1./(kb*T)
        units = 'kT'
    else:
        exit('No unit type \'%s\' available' % units)

    print("# analyze_crooks.py, pmx version = %s" % args.pmx_version, file=out)
    print("# pwd = %s" % os.getcwd(), file=out)
    print("# %s (%s)" % (time.asctime(), os.environ.get('USER')), file=out)
    print("# command = %s" % ' '.join(sys.argv), file=out)
    _tee(out, "\n")

    # ==========
    # Parse Data
    # ==========

    # If list of dgdl.xvg files are provided, parse dgdl
    if args.iA is None and args.iB is None:
        # If random selection is chosen, do this before reading files and
        # calculating the work values.
        if args.rand is not None:
            filesAB = np.random.choice(filesAB, size=args.rand, replace=False)
            filesBA = np.random.choice(filesBA, size=args.rand, replace=False)
            _tee(out, 'Selected random subset of %d trajectories.' % args.rand)

        # If slice values provided, select the files needed. Again before
        # reading files so speed up the process
        if args.slice is not None:
            first = args.slice[0]
            last = args.slice[1]
            _tee(out, ' First trajectories read: %s and %s'
                 % (filesAB[first], filesBA[first]))
            _tee(out, ' Last trajectories  read: %s and %s'
                 % (filesAB[last-1], filesBA[last-1]))
            _tee(out, '')
            filesAB = filesAB[first:last]
            filesBA = filesBA[first:last]

        # If index values provided, select the files needed
        if args.index is not None:
            # Avoid index out of range error if "wrong" indices are provided
            filesAB = [filesAB[i] for i in args.index if i < len(filesAB)]
            filesBA = [filesBA[i] for i in args.index if i < len(filesBA)]
            # ...but warn if this happens
            if any(i > (len(filesAB) - 1) for i in args.index):
                print('\nWARNING: index out of range for some of your chosen '
                      '\nindices for the forward work values. This means you are'
                      '\ntrying to select input files that are not present.')
            if any(i > (len(filesBA) - 1) for i in args.index):
                print('\nWARNING: index out of range for some of your chosen'
                      '\nindices for the reverse work values. This means you are'
                      '\ntrying to select input files that are not present.')

        # when skipping start count from end: in this way the last frame is
        # always included, and what can change is the first one
        filesAB = list(reversed(filesAB[::-skip]))
        filesBA = list(reversed(filesBA[::-skip]))

        # --------------------
        # Now read in the data
        # --------------------
        print(' ========================================================')
        print('                   PROCESSING THE DATA')
        print(' ========================================================')
        print('  Forward Data')
        res_ab = read_dgdl_files(filesAB, lambda0=0,
                                 invert_values=False)
        print('  Reverse Data')
        res_ba = read_dgdl_files(filesBA, lambda0=1,
                                 invert_values=reverseB)

        _dump_integ_file(args.oA, filesAB, res_ab)
        _dump_integ_file(args.oB, filesBA, res_ba)

    # If work values are given as input instead, read those
    elif args.iA is not None and args.iB is not None:
        res_ab = []
        res_ba = []
        for fn in args.iA:
            print('\t\tReading integrated values (A->B) from', fn)
            res_ab.extend(_data_from_file(fn))
        for fn in args.iB:
            print('\t\tReading integrated values (B->A) from', fn)
            res_ba.extend(_data_from_file(fn))
    else:
        exit('\nERROR: you need to provide either none of both sets of '
             'integrated work values.')

    # If asked to only do the integration of dhdl.xvg, exit
    if integ_only:
        print('\n    Integration done. Skipping analysis.')
        print('\n    ......done........\n')
        sys.exit(0)

    # ==============
    # Begin Analysis
    # ==============
    _tee(out, ' ========================================================')
    _tee(out, '                       ANALYSIS')
    _tee(out, ' ========================================================')
    _tee(out, '  Number of forward (0->1) trajectories: %d' % len(res_ab))
    _tee(out, '  Number of reverse (1->0) trajectories: %d' % len(res_ba))
    _tee(out, '  Temperature : %.2f K' % T)

    # ============================
    # Crooks Gaussian Intersection
    # ============================
    if 'cgi' in methods:
        _tee(out, '\n --------------------------------------------------------')
        _tee(out, '             Crooks Gaussian Intersection     ')
        _tee(out, ' --------------------------------------------------------')

        print('  Calculating Intersection...')
        cgi = Crooks(wf=res_ab, wr=res_ba, nboots=nboots, nblocks=nblocks)
        if args.pickle is True:
            pickle.dump(cgi, open("cgi_results.pkl", "wb"))

        _tee(out, '  CGI: Forward Gauss mean = {m:8.{p}f} {u} '
                  'std = {s:8.{p}f} {u}'.format(m=cgi.mf*unit_fact,
                                                s=cgi.devf*unit_fact,
                                                p=prec, u=units))
        _tee(out, '  CGI: Reverse Gauss mean = {m:8.{p}f} {u} '
                  'std = {s:8.{p}f} {u}'.format(m=cgi.mr*unit_fact,
                                                s=cgi.devr*unit_fact,
                                                p=prec, u=units))

        if cgi.inters_bool is False:
            _tee(out, '\n  Gaussians too close for intersection calculation')
            _tee(out, '   --> Taking difference of mean values')

        _tee(out, '  CGI: dG = {dg:8.{p}f} {u}'.format(dg=cgi.dg*unit_fact,
                                                       p=prec, u=units))
        _tee(out, '  CGI: Std Err (bootstrap:parametric) = {e:8.{p}f} {u}'.format(e=cgi.err_boot1*unit_fact,
                                                                                  p=prec, u=units))

        if nboots > 0:
            _tee(out, '  CGI: Std Err (bootstrap) = {e:8.{p}f} {u}'.format(e=cgi.err_boot2*unit_fact,
                                                                           p=prec, u=units))

        if nblocks > 1:
            _tee(out, '  CGI: Std Err (blocks) = {e:8.{p}f} {u}'.format(e=cgi.err_blocks*unit_fact,
                                                                        p=prec, u=units))

    # --------------
    # Normality test
    # --------------
    if do_ks_test:
        print('\n  Running KS-test...')
        q0, lam00, check0, bOk0 = ks_norm_test(res_ab)
        q1, lam01, check1, bOk1 = ks_norm_test(res_ba)

        _tee(out, '    Forward: gaussian quality = %3.2f' % q0)
        if bOk0:
            _tee(out, '             ---> KS-Test Ok')
        else:
            _tee(out, '             ---> KS-Test Failed. sqrt(N)*Dmax = %4.2f,'
                      ' lambda0 = %4.2f' % (q0, check0))
        _tee(out, '    Reverse: gaussian quality = %3.2f' % q1)
        if bOk1:
            _tee(out, '             ---> KS-Test Ok')
        else:
            _tee(out, '             ---> KS-Test Failed. sqrt(N)*Dmax = %4.2f,'
                      ' lambda0 = %4.2f' % (q1, check1))

    # ========================
    # Bennett Acceptance Ratio
    # ========================
    if 'bar' in methods:
        _tee(out, '\n --------------------------------------------------------')
        _tee(out, '             Bennett Acceptance Ratio     ')
        _tee(out, ' --------------------------------------------------------')

        print('  Running Nelder-Mead Simplex algorithm... ')

        bar = BAR(res_ab, res_ba, T=T, nboots=nboots, nblocks=nblocks)
        if args.pickle:
            pickle.dump(bar, open("bar_results.pkl", "wb"))

        _tee(out, '  BAR: dG = {dg:8.{p}f} {u}'.format(dg=bar.dg*unit_fact, p=prec, u=units))
        _tee(out, '  BAR: Std Err (analytical) = {e:8.{p}f} {u}'.format(e=bar.err*unit_fact, p=prec, u=units))

        if nboots > 0:
            _tee(out, '  BAR: Std Err (bootstrap)  = {e:8.{p}f} {u}'.format(e=bar.err_boot*unit_fact, p=prec, u=units))
        if nblocks > 1:
            _tee(out, '  BAR: Std Err (blocks)  = {e:8.{p}f} {u}'.format(e=bar.err_blocks*unit_fact, p=prec, u=units))

        _tee(out, '  BAR: Conv = %8.2f' % bar.conv)

        if nboots > 0:
            _tee(out, '  BAR: Conv Std Err (bootstrap) = %8.2f' % bar.conv_err_boot)

    # =========
    # Jarzynski
    # =========
    if 'jarz' in methods:
        _tee(out, '\n --------------------------------------------------------')
        _tee(out, '             Jarzynski estimator     ')
        _tee(out, ' --------------------------------------------------------')

        jarz = Jarz(wf=res_ab, wr=res_ba, T=T, nboots=nboots, nblocks=nblocks)
        if args.pickle:
            pickle.dump(jarz, open("jarz_results.pkl", "wb"))

        _tee(out, '  JARZ: dG Forward = {dg:8.{p}f} {u}'.format(dg=jarz.dg_for*unit_fact,
                                                                p=prec, u=units))
        _tee(out, '  JARZ: dG Reverse = {dg:8.{p}f} {u}'.format(dg=jarz.dg_rev*unit_fact,
                                                                p=prec, u=units))
        _tee(out, '  JARZ: dG Mean    = {dg:8.{p}f} {u}'.format(dg=jarz.dg_mean*unit_fact,
                                                                p=prec, u=units))
        if nboots > 0:
            _tee(out, '  JARZ: Std Err Forward (bootstrap) = {e:8.{p}f} {u}'.format(e=jarz.err_boot_for*unit_fact,
                                                                                    p=prec, u=units))
            _tee(out, '  JARZ: Std Err Reverse (bootstrap) = {e:8.{p}f} {u}'.format(e=jarz.err_boot_rev*unit_fact,
                                                                                    p=prec, u=units))

        if nblocks > 1:
            _tee(out, '  JARZ: Std Err Forward (blocks) = {e:8.{p}f} {u}'.format(e=jarz.err_blocks_for*unit_fact,
                                                                                 p=prec, u=units))
            _tee(out, '  JARZ: Std Err Reverse (blocks) = {e:8.{p}f} {u}'.format(e=jarz.err_blocks_rev*unit_fact,
                                                                                 p=prec, u=units))


    _tee(out, ' ========================================================')

    print('\n   Plotting histograms......')
    if 'cgi' in methods and args.cgi_plot is not None:
        make_cgi_plot(args.cgi_plot, res_ab, res_ba, cgi.dg, cgi.err_boot1,
                      args.nbins, args.dpi)

    print('\n   ......done...........\n')

    if args.pickle:
        print('   NOTE: units of results in pickled files are as in the\n'
              '   provided dgdl.xvg or integ.dat files. These are typically\n'
              '   in kJ/mol when using dgdl.xvg files from Gromacs.\n')
    # execution time
    etime = time.time()
    h, m, s = _time_stats(etime-stime)
    print("   Execution time = %02d:%02d:%02d\n" % (h, m, s))


if __name__ == '__main__':
    args = parse_options()
    main(args)
