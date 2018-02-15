# -*- coding: utf-8 -*-
"""
Auto Histogram class
    1. Read INPUTFILE as CSV or Excel (sheet, skiprows, headers)
    2. Select COLUMN
    3. Generate Relative Frequency Histogram data and plot/s
    4. Output to OUTPUTDIR

Created on 7 Feb 2018

@author: Liz Cooper-Williams, QBI
"""

import argparse
from os.path import join

# #maintain this order of matplotlib
# import matplotlib
# matplotlib.use('TkAgg')
# plt.style.use('seaborn-paper')
import numpy as np
import pandas as pd

from autoanalysis.processmodules.DataParser import AutoData


class AutoHistogram(AutoData):
    def __init__(self, datafile, outputdir, column_name, binwidth, sheet=0, skiprows=0, headers=None, showplots=False):
        super().__init__(datafile, sheet, skiprows, headers)
        self.showplots = showplots
        self.binwidth = binwidth
        self.column = column_name
        self.outputdir = outputdir

        # Load data
        self.data = self.load_data()
        self.fig = None
        self.histogramid = "%s_%s" % (self.bname, self.column)

    def histo_types(self):
        types = {0: 'Relative freq', 1: 'Density'} #, 2: 'Cumulative freq'}
        return types



    def generateHistogram(self, freq=0):
        """
        Generate histogram and save to outputdir
        :param outputdir: where to save csv and png files to
        :param freq: 0=relative freq, 1=density, 2=cumulative
        :return:
        """
        ftype = '_HISTOGRAM'
        n_bins = 10
        # Data column
        xdata = self.data[self.column]  # Series
        minv = int(min(xdata)/100) * n_bins
        maxv = int(np.ceil(max(xdata) / n_bins)) * n_bins

        bins = [x for x in range(minv,maxv,n_bins)]
        if freq == 1:
            ftype = ftype + '_density'
            n, bin_edges = np.histogram(xdata, bins=bins,density=True)
            if self.showplots:
                xdata.plot.density()
        else:
            n, bin_edges = np.histogram(xdata, bins=bins,density=False)
            if self.showplots:
                xdata.plot.hist()
        # histogram data
        histdata = pd.DataFrame()
        histdata['bins']=bin_edges[0:-1]
        histdata[self.column]= n

        # filenames
        outputfile = join(self.outputdir, self.histogramid + ftype + ".csv")
        # outputplot = join(self.outputdir, self.histogramid + ftype +".html")
        histdata.to_csv(outputfile, index=False)
        print("Saved histogram data to ", outputfile)
        return histdata


def create_parser():
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
                Generates frequency histogram from datafile to output directory

                 ''')
    parser.add_argument('--datafile', action='store', help='Initial data file',
                        default="..\\..\\sampledata\\Brain11_Image_FILTERED.csv")
    parser.add_argument('--outputdir', action='store', help='Output directory (must exist)',
                        default="..\\..\\sampledata")
    parser.add_argument('--column', action='store', help='Column header to be analysed',
                        default="Count_ColocalizedGAD_DAPI_Objects")
    parser.add_argument('--binwidth', action='store', help='Binwidth for relative frequency', default='1')
    parser.add_argument('--showplots', action='store_true', help='Display popup plots', default=True)

    return parser


############### MAIN ############################
if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    print("Input:", args.datafile)
    print("Output:", args.outputdir)
    try:
        fd = AutoHistogram(args.datafile, args.outputdir, args.column, args.binwidth, args.showplots)
        histo_types = fd.histo_types()
        for t in histo_types.keys():
            print(histo_types[t])
            fd.generateHistogram(freq=t)

    except ValueError as e:
        print("Error:", e)
