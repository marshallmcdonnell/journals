#!/usr/bin/env python

import unittest

from journals.databases.icat.sns.communicate import SnsICat

remove_list = ['FNPB','NSE']

class TestSnsComm(unittest.TestCase):

    def test_instruments(self):
        comm = SnsICat()
        data_json = comm.get_instruments()
        self.assertNotEqual( data_json, None )
        self.assertTrue( 'instrument' in data_json )
        data_json_str = [ x for x in data_json['instrument'] ]
        target = [  'ARCS',
                    'BSS',
                    'CNCS',
                    'CORELLI',
                    'EQSANS',
                    'FNPB',
                    'HYS',
                    'HYSA',
                    'MANDI',
                    'NOM',
                    'NSE',
                    'PG3',
                    'REF_L',
                    'REF_M',
                    'SEQ',
                    'SNAP',
                    'TOPAZ',
                    'USANS',
                    'VIS',
                    'VULCAN']
        self.assertEqual(data_json_str, target)

    def test_NOM_experiment(self):
        comm = SnsICat()
        data_json = comm.get_experiments('NOM')
        self.assertTrue( 'proposal' in data_json )
        self.assertEqual( data_json['proposal'][0], 'IPTS-10040' )

    def test_non_empty_instruments_for_experiments(self):
        comm = SnsICat()
        instruments = comm.get_instruments()
        # remove instruments with no known proposals
        for x in remove_list:
            instruments['instrument'].remove(x)
        for x in instruments['instrument']:
            experiments = comm.get_experiments(x)
            experiments_meta = comm.get_experiments_meta(x)
            self.assertNotEqual(experiments,None)
            self.assertNotEqual(experiments_meta,None)

    def test_get_user_experiments(self):
        comm = SnsICat()
        ntm_experiments = comm.get_user_experiments('ntm')
        ntm_experiments_subset = ntm_experiments['proposals'][0:5]
        target = [ {u'IPTS' : v} for v in [16214,16391,17210,17360,17463] ]
        self.assertEqual(ntm_experiments_subset,target)

    def test_run_ranges_exist_for_one_experiment(self):
        comm = SnsICat()
        instruments = comm.get_instruments()
        # remove instruments with no known proposals
        for x in remove_list:
            instruments['instrument'].remove(x)
        for x in instruments['instrument']:
            experiments = comm.get_experiments(x)
            runs = comm.get_run_ranges(x,experiments['proposal'][0])
            self.assertTrue('runRange' in runs)
        
    def test_run_ranges_meta_for_one_experiment(self):
        comm = SnsICat()
        instruments = comm.get_instruments()
        # remove instruments with no known proposals
        for x in remove_list:
            instruments['instrument'].remove(x)
        for x in instruments['instrument']:
            experiments = comm.get_experiments(x)
            ipts_experiments = [ exp for exp in experiments['proposal'] if exp.startswith('IPTS') ]
            runs = comm.get_run_ranges_meta(x,ipts_experiments[0])
            self.assertTrue('proposal' in runs)
            runs_meta = runs['proposal']
            self.assertTrue('title' in runs_meta)
            self.assertTrue('createTime' in runs_meta)
            self.assertTrue('runRange' in runs_meta)

    def test_run_info_for_one_experiment(self):
        run_to_check = 15500
        comm = SnsICat()
        instruments = comm.get_instruments()
        # remove instruments with no known proposals
        remove_list.extend(['CNCS','HYSA','MANDI'])
        for x in remove_list:
            instruments['instrument'].remove(x)
        for x in instruments['instrument']:
            info_lite = comm.get_run_info_lite(x,run_to_check)
            info_meta = comm.get_run_info_meta_only(x,run_to_check)
            self.assertTrue('locations' in info_lite)
            self.assertTrue('title' in info_meta)
        
    def test_last_run_and_remove_list_validity(self):
        comm = SnsICat()
        data_json = comm.get_instruments()
        for x in remove_list:
            lastRun = comm.get_last_run(x)
            self.assertEqual(int(lastRun['number']),0)

    def test_run_files_preNexus(self):
        comm = SnsICat()
        files = comm.get_run_files('NOM',10000)
        target =    [u'/SNS/NOM/IPTS-7234/shared/autoreduce/NOM_10000.getn',
                     u'/SNS/NOM/IPTS-7234/shared/autoreduce/NOM_10000.gsa',
                     u'/SNS/NOM/IPTS-7234/0/10000/NOM_10000.meta.xml',
                     u'/SNS/NOM/IPTS-7234/shared/autoreduce/NOM_10000.py',
                     u'/SNS/NOM/IPTS-7234/0/10000/preNeXus/NOM_10000_bmon_histo.dat',
                     u'/SNS/NOM/IPTS-7234/0/10000/preNeXus/NOM_10000_cvinfo.xml',
                     u'/SNS/NOM/IPTS-7234/0/10000/NeXus/NOM_10000_event.nxs',
                     u'/SNS/NOM/IPTS-7234/0/10000/NeXus/NOM_10000_histo.nxs',
                     u'/SNS/NOM/IPTS-7234/0/10000/preNeXus/NOM_10000_neutron_event.dat',
                     u'/SNS/NOM/IPTS-7234/0/10000/preNeXus/NOM_10000_pulseid.dat',
                     u'/SNS/NOM/IPTS-7234/0/10000/preNeXus/NOM_10000_runinfo.xml']
        self.assertEqual(files['location'],target )

    def test_run_files_nexus(self):
        comm = SnsICat()
        files = comm.get_run_files('NOM',80000)
        target =    [u'/SNS/NOM/IPTS-16513/adara/NOM_80000.adara',
                     u'/SNS/NOM/IPTS-16513/shared/autoreduce/NOM_80000.getn',
                     u'/SNS/NOM/IPTS-16513/shared/autoreduce/NOM_80000.gsa',
                     u'/SNS/NOM/IPTS-16513/nexus/NOM_80000.nxs.h5',
                     u'/SNS/NOM/IPTS-16513/shared/autoreduce/reduction_log/NOM_80000.nxs.h5.pdfgetn.log',
                     u'/SNS/NOM/IPTS-16513/shared/autoreduce/reduction_log/NOM_80000.nxs.h5.report.log',
                     u'/SNS/NOM/IPTS-16513/shared/autoreduce/reduction_log/NOM_80000.nxs.h5.rietveld.log',
                     u'/SNS/NOM/IPTS-16513/shared/autoreduce/NOM_80000.py']
        self.assertEqual(files['location'],target )


if __name__ == '__main__':
    unittest.main()
