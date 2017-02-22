#!/usr/bin/env python

import unittest

from journals.databases.icat.sns.interface import SnsICatInterface

if __name__=="__main__":
    conn = SnsICatInterface()
    #print(conn.get_instruments())

    print(conn.get_experiments('NOM'))
    #print(conn.get_experiments_meta('NOM'))
    #print(conn.get_experiments_id_and_title('NOM'))
    #print(conn.get_experiments_id_and_date('NOM'))

    #print(conn.get_runs_all('NOM','IPTS-17210'))
    #print(conn.get_runs('NOM','IPTS-17210'))
    #print(conn.get_runs_meta('NOM','IPTS-17210'))
    #print(conn.get_run_number_and_title('NOM','IPTS-17210'))

    #print(conn.get_user_experiments('ntm'))

    #print(conn.get_runs_meta('NOM', 'IPTS-8814'))
