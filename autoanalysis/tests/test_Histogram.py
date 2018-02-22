import unittest2 as unittest
import argparse
from os.path import join
from os import access,R_OK
from autoanalysis.processmodules.Histogram import AutoHistogram, create_parser

class TestHistogram(unittest.TestCase):
    def setUp(self):
        parser = create_parser()
        args = parser.parse_args()
        fd = AutoHistogram(args.datafile, args.outputdir, args.showplots)
        cfg = fd.getConfigurables()
        cfg['COLUMN'] = args.column
        cfg['BINWIDTH'] = args.binwidth
        for c in cfg.keys():
            print("config set: ", c, "=", cfg[c])
        fd.setConfigurables(cfg)
        self.fd = fd

    def test_histogram(self):
        self.fd.freq = 0 #'Relative freq'
        data = self.fd.run()
        outputfile = self.fd.run()
        self.assertFalse(outputfile.endswith('DENSITY_HISTOGRAM.csv'))

    def test_histogram_density(self):
        self.fd.freq = 1 #'Density'
        outputfile = self.fd.run()
        self.assertTrue(outputfile.endswith('DENSITY_HISTOGRAM.csv'))
