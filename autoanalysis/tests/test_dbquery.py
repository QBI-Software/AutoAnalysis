from os.path import join

import unittest2 as unittest

from autoanalysis.db.dbquery import DBI


class TestDBquery(unittest.TestCase):
    def setUp(self):
        configdb = join('..','resources', 'autoconfig_test.db')
        self.dbi = DBI(configdb)
        self.dbi.getconn()

    def tearDown(self):
        self.dbi.conn.close()

    def test_getConfig(self):
        data = self.dbi.getConfig()
        expected = 4
        self.assertEqual(len(data),expected)

    def test_updateConfig(self):
        configlist = [('BINWIDTH',10,'general'),('COLUMN','TestData','general'),('MINRANGE',0,'general'),('MAXRANGE',100,'general')]
        cnt = self.dbi.addConfig(configlist)
        expected = len(configlist)
        self.assertEqual(expected,cnt)

    def test_getConfigByName(self):
        group = 'general'
        test = 'BINWIDTH'
        expected = 10
        data = self.dbi.getConfigByName(group,test)
        self.assertEqual(int(data),expected)

    def test_getConfigByName_None(self):
        group = 'general'
        test = 'BINW'
        expected = None
        data = self.dbi.getConfigByName(group,test)
        self.assertEqual(int(data),expected)


    def test_getConfigByValue(self):
        expected = ['BINWIDTH']
        test = 10
        data = self.dbi.getConfigByValue(test)
        self.assertEqual(data,expected)
