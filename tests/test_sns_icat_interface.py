#!/usr/bin/env python

import unittest

from journals.databases.icat.sns.interface import SnsICatInterface

class TestSnsInterface(unittest.TestCase):
    conn = SnsICatInterface()

    def test_instruments(self):
        target =    [u'ARCS',
                     u'BSS',
                     u'CNCS',
                     u'CORELLI',
                     u'EQSANS',
                     u'FNPB',
                     u'HYS',
                     u'HYSA',
                     u'MANDI',
                     u'NOM',
                     u'NSE',
                     u'PG3',
                     u'REF_L',
                     u'REF_M',
                     u'SEQ',
                     u'SNAP',
                     u'TOPAZ',
                     u'USANS',
                     u'VIS',
                     u'VULCAN']
        self.assertEqual(self.conn.get_instruments(),target)

    def test_experiments_meta(self):
        print(self.conn.get_experiments_meta('NOM'))
        

       
if __name__ == '__main__':
    unittest.main() 
