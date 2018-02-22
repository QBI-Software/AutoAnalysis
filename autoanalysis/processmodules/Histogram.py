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
from collections import OrderedDict

from autoanalysis.processmodules.DataParser import AutoData


class AutoHistogram(AutoData):
    def __init__(self, datafile, outputdir, sheet=0, skiprows=0, headers=None, showplots=False):
        super().__init__(datafile, sheet, skiprows, headers)
        self.showplots = showplots
        self.outputdir = outputdir
        # Load data
        self.data = self.load_data()
        self.fig = None


    def getConfigurables(self):
        '''
        List of configurable parameters in order with defaults
        :return:
        '''
        cfg = OrderedDict()
        cfg['COLUMN']=''
        cfg['BINWIDTH']=1
        cfg['HISTOGRAM_FILENAME'] = 'HISTOGRAM.csv'
        cfg['HISTOGRAM_FREQ_TYPE'] = 0
        return cfg

    def setConfigurables(self,cfg):
        if 'COLUMN' in cfg.keys() and cfg['COLUMN'] is not None:
            self.column = cfg['COLUMN']
        else:
            self.column =''
        if 'BINWIDTH' in cfg.keys() and cfg['BINWIDTH'] is not None:
            self.binwidth = cfg['BINWIDTH']
        else:
            self.binwidth = 1
        if 'HISTOGRAM_FILENAME' in cfg.keys() and cfg['HISTOGRAM_FILENAME'] is not None:
            self.suffix = cfg['HISTOGRAM_FILENAME']
            if self.suffix.startswith("*"):
                self.suffix=self.suffix[1:]
        else:
            self.suffix = 'HISTOGRAM.csv'

        if 'HISTOGRAM_FREQ_TYPE' in cfg.keys() and cfg['HISTOGRAM_FREQ_TYPE'] is not None:
            self.freq = int(cfg['HISTOGRAM_FREQ_TYPE'])
        else:
            self.freq = 0


    def run(self):
        """
        Generate histogram and save to outputdir
        :param outputdir: where to save csv and png files to
        :param freq: 0=relative freq, 1=density, 2=cumulative
        :return:
        """

        n_bins = 10
        # Data column
        xdata = self.data[self.column]  # Series
        minv = int(min(xdata)/100) * n_bins
        maxv = int(np.ceil(max(xdata) / n_bins)) * n_bins

        bins = [x for x in range(minv,maxv,n_bins)]
        if self.freq == 1:
            hist_title = self.bname + "_DENSITY_" + self.suffix
            n, bin_edges = np.histogram(xdata, bins=bins,density=True)
            if self.showplots:
                xdata.plot.density()
        else:
            n, bin_edges = np.histogram(xdata, bins=bins,density=False)
            hist_title = self.bname + "_" + self.suffix
            if self.showplots:
                xdata.plot.hist()
        # histogram data
        histdata = pd.DataFrame()
        histdata['bins']=bin_edges[0:-1]
        histdata[self.column]= n

        # filenames
        outputfile = join(self.outputdir, hist_title)
        # outputplot = outputfile.replace(".csv",".html")
        histdata.to_csv(outputfile, index=False)
        print("Saved histogram data to ", outputfile)
        return outputfile


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
        fd = AutoHistogram(args.datafile, args.outputdir, args.showplots)
        cfg = fd.getConfigurables()
        cfg['COLUMN'] = args.column
        cfg['BINWIDTH'] = args.binwidth
        for c in cfg.keys():
            print("config set: ", c, "=", cfg[c])
        fd.setConfigurables(cfg)

        # Run through different types of histo
        #freq: 0=relative freq, 1=density, 2=cumulative
        for t in [0,1]:
            fd.freq = t
            fd.run()

    except ValueError as e:
        print("Error:", e)
