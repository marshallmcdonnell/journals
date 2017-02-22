#!/usr/bin/env python

'''
Original author: Ricardo Ferraz Leal (ORNL)
Current version by: Marshall McDonnell
'''

from __future__ import print_function
import json

from journals.databases.icat import ICat


class SnsICat(ICat):

    def __init__(self):
        url_prefix = "http://icat.sns.gov:2080"
        super(SnsICat, self).__init__(url_prefix)

    def get_instruments(self):
        return self._request("/icat-rest-ws/experiment/SNS")

    def get_experiments(self,instrument):
        return self._request("/icat-rest-ws/experiment/SNS/" + instrument)

    def get_experiments_meta(self, instrument):
        return self._request("/icat-rest-ws/experiment/SNS/" + instrument + "/meta")

    def get_user_experiments(self,uid):
        return self._request('/prpsl_ws/getProposalNumbersByUser/%s' % (uid))

    def get_run_ranges(self,instrument,experiment):
        return self._request("/icat-rest-ws/experiment/SNS/%s/%s/"%(instrument,experiment))

    def get_run_ranges_meta(self,instrument,experiment):
        return self._request("/icat-rest-ws/experiment/SNS/%s/%s/meta"%(instrument,experiment))

    def get_runs_all(self,instrument,experiment):
        return self._request("/icat-rest-ws/experiment/SNS/%s/%s/all"%(instrument,experiment))

    def get_run_info(self,instrument,run_number):
        return self._request("/icat-rest-ws/dataset/SNS/%s/%s"%(instrument,run_number))

    def get_run_info_lite(self,instrument,run_number):
        return self._request("/icat-rest-ws/dataset/SNS/%s/%s/lite"%(instrument,run_number))

    def get_run_info_meta_only(self,instrument,run_number):
        return self._request("/icat-rest-ws/dataset/SNS/%s/%s/metaOnly"%(instrument,run_number))

    def get_last_run(self,instrument):
        return self._request("/icat-rest-ws/datafile/SNS/%s"%(instrument))

    def get_run_files(self,instrument,run_number):
        return self._request("/icat-rest-ws/datafile/SNS/%s/%s"%(instrument,run_number))


if __name__=="__main__":
    comm = SnsICat()
    print(comm.get_instruments())
