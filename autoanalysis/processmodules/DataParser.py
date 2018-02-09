# -*- coding: utf-8 -*-
"""
Auto Data class
    1. Read INPUTFILE as CSV or Excel (sheet, skiprows, headers)

Created on 7 Feb 2018

@author: Liz Cooper-Williams, QBI
"""

import logging
import pandas as pd
from os.path import join, basename, splitext


class AutoData():
    def __init__(self, datafile, sheet=0, skiprows=0, headers=None):
        self.datafile = datafile
        (self.bname, self.extension) = splitext(basename(datafile))
        self.headers = headers
        self.sheet = sheet
        self.skiprows = skiprows
        # Load data
        self.data = self.load_data()



    def load_data(self):
        """
        Load data into pandas DataFrame
        :param datafile: Input data as csv or excel
        :return: dataframe
        """
        data = pd.DataFrame()
        try:
            if '.xls' in self.extension:
                if self.headers is None:
                    data = pd.read_excel(self.datafile, skiprows=self.skiprows, sheet_name=self.sheet,skip_blank_lines=True)
                else:
                    data = pd.read_excel(self.datafile, skiprows=self.skiprows, sheet_name=self.sheet,skip_blank_lines=True, header=self.headers)
            elif self.extension == '.csv':
                data = pd.read_csv(self.datafile, skip_blank_lines=True)
            # Check loaded
            if data.empty:
                raise ValueError("Data not loaded - check datafile")
            else:
                msg = "... loaded complete"
                self.logandprint(msg)
        except Exception as e:
            print(e)
            logging.error(e)
        return data


    def logandprint(self, msg, info=True):
        """
        Utility method to enable both logging and printing - can update for Python2 or 3
        :param msg:
        :param info:
        :return:
        """
        print(msg)
        if info:
            logging.info(msg)
        else:
            logging.error(msg)
        
