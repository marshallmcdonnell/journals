#!/usr/bin/env python

import unittest

from journals.databases.icat.sns.test_interface import SnsICatInterface

class TestSnsInterface(unittest.TestCase):

    def test_instruments(self):
        conn = SnsICatInterface()
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
        self.assertEqual(conn.get_instruments(),target)
       
if __name__ == '__main__':
    unittest.main() 
