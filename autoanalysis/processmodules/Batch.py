# -*- coding: utf-8 -*-
"""
AutoBatch class
1. Reads in list of files from INPUTDIR
2. Matches files in list to searchtext (filenames)
3. Combines data from columns into single batch file with unique ids generated from files
4. Outputs to output directory as BATCH_filename_searchtext.csv or excel

Created on 19 Feb 2018

@author: Liz Cooper-Williams, QBI
"""

import logging
import re
from glob import iglob
from os import R_OK, access
from os.path import join, isdir, commonpath, sep, basename, splitext

from configobj import ConfigObj
from numpy import unique
import argparse
import pandas as pd
from plotly import offline
from plotly.graph_objs import Layout, Scatter
DEBUG = 1

class AutoBatch:
    def __init__(self, inputfiles, outputdir, datafile_searchtext,column_names, showplots=False):
        (self.base, self.inputfiles) = self.getSelectedFiles(inputfiles, datafile_searchtext)
        self.numcells = len(self.inputfiles)
        self.outputdir = outputdir
        self.outputfilename= join(self.outputdir,"BATCH_" + self.base.split(sep)[-1] + "_"+ datafile_searchtext.split('.')[0] +".csv")
        self.colnames = column_names.split(',')
        self.showplots = showplots
        self.n = 1  # generating id


    def getSelectedFiles(self, inputdir, searchtext):
        """
        Check list or directory contains only datafiles
        tries several methods for detecting files
        :param inputdir: list of files or input directory
        :param searchtext: matching datafile name
        :return: basename and file list
        """
        files = []
        base = ''
        # get list of files from a directory
        if not isinstance(inputdir, list) and isdir(inputdir):
            base = inputdir
            if access(inputdir, R_OK):
                allfiles = [y for y in iglob(join(inputdir, '**'), recursive=True)]
                if len(allfiles) > 0:
                    # Filter on searchtext - match on filename
                    files = [f for f in allfiles if (searchtext in basename(f))]
                    if len(files) <= 0:
                        msg = "Batch: No files found in inputdir for datafile searchtext: %s %s" % (inputdir,searchtext)
                        logging.error(msg)
                        raise ValueError(msg)
                else:
                    msg = "Batch: No files found in inputdir: %s" % inputdir
                    logging.error(msg)
                    raise IOError(msg)

            else:
                raise IOError("Batch: Cannot access directory: %s", inputdir)
        else:
            # assume we have a list as input - exclude duplicates
            if isinstance(inputdir, list):
                allfiles = unique(inputdir).tolist()
            else:
                allfiles = unique(inputdir.tolist()).tolist()
            files = [f for f in allfiles if (searchtext in basename(f))]
            base = commonpath(files)
        print("Total Files Found: ", len(files))
        #generate IDs for each file (based on filename or unique)
        filedict = {}
        basenames = [basename(f) for f in files]
        uids = unique(basenames)
        usefilenames = (len(uids)==len(files))
        for f in files:
            filedict[self.generateID(f, usefilenames)]= f

        return (base, filedict)

    def generateID(self, f,usefilenames=True):
        """
        Generate a unique ID for each file
        :param f: full path filename
        :param usefilenames: use base of filename
        :return: unique ID
        """
        # Generate unique cell ID
        (filename,ext) = splitext(basename(f))

        if usefilenames:
            cell = filename
        else:
            cell = 'c{0:03d}'.format(self.n)
            self.n += 1
        if DEBUG:
            print("Cellid=", cell)
        return cell

    def validHeader(self,colname,df):
        """
        Check column names are in data files
        :param colname: array of colname/s
        :param df: data file as dataframe
        :return: true if present, false if not (all columns)
        """
        matches = []
        for col in colname:
            matches.append(col in df.columns)
        if sum(matches)== len(colname):
            rtn = True
        else:
            rtn = False
        return rtn

    def generatePlots(self,df):
        if len(df)==1:
            df.plot()
        else:
            xi = [str(x) for x in range(len(df) + 1)]
            data = []
            title = 'Batch plots'
            for col in df.columns:
                data.append(Scatter(y=df[col], x=xi,name=col,mode='markers'))

            # Create plotly plot
            pfilename = self.outputfilename.replace('.csv','.html')
            offline.plot({"data": data,
                          "layout": Layout(title=title,
                                           xaxis={'title': self.colnames},
                                           yaxis={'title': ''})},
                         filename=pfilename)

        return pfilename


    def combineData(self,colname=None):
        """
        Combine data from columns specified into batch output file
        Include basic plot if showplots is flagged
        :param colname:
        :return: outputfilename
        """
        df = None
        if colname is None:
            colname = self.colnames
            if colname is None or len(colname) <=0:
                raise ValueError('No columns specified for data extraction')
        batchout = {}
        for fid,f in self.inputfiles.items():
            if basename(f).endswith('.csv'):
                df = pd.read_csv(f)
                if self.validHeader(colname, df):
                    data = [x[0] for x in df[colname].get_values()]
                    batchout[fid] = data
        if len(batchout) > 0:
            df = pd.DataFrame.from_dict(batchout,orient='index').T.fillna('')
            #save to file
            df.to_csv(self.outputfilename,index=False)
            if self.showplots:
                self.generatePlots(df)
        return df

################################################################################
def create_parser():
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
                Combines data from datafiles to output file

                 ''')
    parser.add_argument('--datafile', action='store', help='Search text of filename',
                        default="_Image.csv")
    parser.add_argument('--outputdir', action='store', help='Output directory (must exist)',default="..\\..\\dataoutput")
    parser.add_argument('--inputdir', action='store', help='Input directory',
                        default="..\\..\\sampledata")
    parser.add_argument('--column', action='store', help='Column header/s to be combined',
                        default="Count_ColocalizedGAD_DAPI_Objects")
    parser.add_argument('--showplots', action='store_true', help='Display popup plots', default=True)

    return parser

###############################################################################
if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    datafile = args.datafile
    outputdir = args.outputdir
    column_name = args.column
    inputdir = args.inputdir
    showplots = True
    batch = AutoBatch(inputdir, outputdir, datafile, column_name, showplots)
    for f in batch.inputfiles:
        print("File:",f)
        #print("ID:", batch.generateID(f))
    #Generate output file
    df_out = batch.combineData()
    print("Output: ", batch.outputfilename, " data=", len(df_out))