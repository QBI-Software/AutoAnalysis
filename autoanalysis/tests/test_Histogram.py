import unittest2 as unittest
import argparse
from os.path import join
from os import access,R_OK
from autoanalysis.processmodules.Histogram import AutoHistogram, create_parser

class TestHistogram(unittest.TestCase):
    def setUp(self):
        parser = create_parser()
        args = parser.parse_args()
        datafile = args.datafile
        outputdir = args.outputdir
        column_name = args.column
        binwidth = args.binwidth
        sheet = 0
        skiprows = 0
        headers = None
        showplots = True
        self.fd = AutoHistogram(datafile, outputdir, column_name, binwidth, sheet, skiprows, headers, showplots)

    def test_histotypes(self):
        data = self.fd.histo_types()
        expected = {0: 'Relative freq', 1: 'Density'} #, 2: 'Cumulative freq'}
        self.assertDictEqual(expected,data)

    def test_histogram(self):
        type = 0 #'Relative freq'
        data = self.fd.generateHistogram(freq=type)
        self.assertGreater(len(data),0)

    def test_histogram_density(self):
        type = 1 #'Density'
        data = self.fd.generateHistogram(freq=type)
        self.assertGreater(len(data),0)

    # def test_histogram_cumulative(self):
    #     type = 2 #'Cumulative'
    #     data = self.fd.generateHistogram(freq=type)
    #     self.assertGreater(len(data),0)