# -*- coding: utf-8 -*-
"""
Auto Filter class
    1. Read INPUTFILE as CSV or Excel (sheet, skiprows, headers)
    2. Select COLUMN
    3. Filter on MIN, MAX limits
    4. Output to OUTPUTDIR


Created on 7 Feb 2018

@author: Liz Cooper-Williams, QBI
"""

import argparse
import logging
from os.path import join, basename, splitext

import pandas as pd

from autoanalysis.processmodules.DataParser import AutoData



class AutoFilter(AutoData):
    """
    Filter class for filtering a dataset based on a single column of data between min and max limits
    """

    def __init__(self, datafile,outputdir, column_name, outputall=True, minlimit=-5.0, maxlimit=1.0, sheet=0, skiprows=0, headers=None):
        super().__init__(datafile, sheet, skiprows, headers)
        self.column = column_name
        self.outputall = outputall
        self.minlimit = float(minlimit)
        self.maxlimit = float(maxlimit)
        # Load data
        self.outputdir = outputdir
        msg = "Filter: Loading data from %s ..." % self.datafile
        self.logandprint(msg)
        self.data = self.load_data()


    def runFilter(self):
        """
        Run filter over datasets and save to file
        :return:
        """
        if not self.data.empty:
            pre_data = len(self.data)
            minfilter = self.data[self.column] > self.minlimit
            maxfilter = self.data[self.column] < self.maxlimit
            mmfilter = minfilter & maxfilter
            filtered = self.data[mmfilter]
            msg = "Rows after filtering %s values between %d and %d: \t%d of %d\n" % (
            self.column, self.minlimit, self.maxlimit, len(filtered), pre_data)
            self.logandprint(msg)

            # Save files
            fdata = join(self.outputdir, self.bname + "_FILTERED.csv")

            try:
                if self.outputall:
                    filtered.to_csv(fdata, index=False)
                else:
                    filtered.to_csv(fdata, columns=[self.column], index=False)  # with or without original index numbers
                msg = "Filtered Data saved: %s" % fdata
                self.logandprint(msg)
            except IOError as e:
                raise e


####################################################################################################################
if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Reads data file and filters data in column between min and max with output into outputdir

             ''')
    parser.add_argument('--datafile', action='store', help='Data file', default="Brain11_Image.csv")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="sampledata")
    parser.add_argument('--minlimit', action='store', help='Min filter', default="10")
    parser.add_argument('--maxlimit', action='store', help='Max filter', default="200")
    parser.add_argument('--column', action='store', help='Column header to be filtered',
                        default="Count_ColocalizedGAD_DAPI_Objects")
    args = parser.parse_args()

    outputdir = join("..\\..\\", args.outputdir)
    datafile = join(outputdir, args.datafile)

    print("Input:", datafile)
    print("Output:", outputdir)

    try:
        fmsd = AutoFilter(datafile, outputdir, args.column, minlimit=args.minlimit, maxlimit=args.maxlimit)
        if fmsd.data is not None:
            fmsd.runFilter()

    except Exception as e:
        print("Error: ", e)
