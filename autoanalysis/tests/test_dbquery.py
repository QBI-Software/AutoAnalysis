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
        configid = 'general'
        data = self.dbi.getConfig(configid)
        expected = 4
        self.assertEqual(len(data),expected)

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
        self.assertEqual(data,expected)

    def test_getConfigIds(self):
        data = self.dbi.getConfigIds()
        print('IDS:', data)
        self.assertGreater(len(data),0)

    def test_updateConfig(self):
        configid='general'
        configlist = [('BINWIDTH',10,'general'),('COLUMN','TestData','general'),('MINRANGE',0,'general'),('MAXRANGE',100,'general')]
        cnt = self.dbi.addConfig(configid,configlist)
        expected = len(configlist)
        self.assertEqual(expected,cnt)

    def test_updateConfig_Secondset(self):
        configid = 'test'
        configlist = [('BINWIDTH', 10, configid), ('COLUMN', 'TestData', configid), ('MINRANGE', 0, configid),('MAXRANGE', 100, configid)]
        cnt = self.dbi.addConfig(configid, configlist)
        expected = len(configlist)
        self.assertEqual(expected, cnt)

    def test_updateConfig_duplicate(self):
        configid='general'
        configlist = [('BINWIDTH',20,'general'),('COLUMN','TestData2','general'),('MINRANGE',0,'general'),('MAXRANGE',100,'general')]
        cnt = self.dbi.addConfig(configid,configlist)
        expected = len(configlist)
        self.assertEqual(expected,cnt)