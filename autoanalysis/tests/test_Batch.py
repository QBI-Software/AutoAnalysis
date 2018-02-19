import unittest2 as unittest
import argparse
from os.path import join
from os import access,R_OK
from autoanalysis.processmodules.Batch import AutoBatch, create_parser

class TestBatch(unittest.TestCase):
    def setUp(self):
        parser = create_parser()
        self.args = parser.parse_args()
        datafile = self.args.datafile
        outputdir = self.args.outputdir
        column_name = self.args.column
        inputdir=self.args.inputdir
        showplots = True
        self.batch = AutoBatch(inputdir,outputdir,datafile,column_name,showplots)

    def test_filelist(self):
        data = self.batch.inputfiles
        expected = 1
        self.assertEqual(expected,len(data))

    def test_basedir(self):
        expected = self.args.inputdir
        data = self.batch.base
        self.assertEqual(expected,data)

    def test_generateid(self):
        f = self.batch.inputfiles[0]
        expected = 'c001'
        data = self.batch.generateID(f)
        self.assertEqual(expected, data)

    def test_combinedata(self):
        data = self.batch.combineData()
        expected = 45
        self.assertEqual(len(data),expected)
