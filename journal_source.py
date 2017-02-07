#!/usr/bin/env python

#import flask
import requests 
import xmljson, json
import lxml
import utils 
from decimal import Decimal

#uri = "http://icat.sns.gov:2080/icat-rest-ws/experiment/SNS"
#uri = "http://icat.sns.gov:2080/icat-rest-ws/experiment/SNS/NOM"
#uri = "http://icat.sns.gov:2080/icat-rest-ws/experiment/SNS/NOM/IPTS-"+ipts+"/meta"

class icat(object):

    def __init__(self):
        self._data = None
        self._los_data = dict()
        self._meta_ipts_data = dict()
        self._runs = list()
        self._ipts_list = None
        self.key_list = ['ipts', 'duration', 'startTime', 'totalCounts', 'protonCharge', 'title']

    def getIPTSs(self,proposals,**kwargs):
        print "Getting IPTS data...",
        for i, ipts in enumerate(proposals):
            self.getIPTS(ipts,**kwargs)
        print "DONE"

    def _uri2xml(self,uri):
        xml_data = requests.get(uri)
        xml_data = lxml.etree.XML(xml_data.content)
        return xml_data

    def _xml2json(self,xml_data):
        return xmljson.badgerfish.data(xml_data)

    def _uri2xml2json(self,uri):
        xml_data  = self._uri2xml(uri)
        json_data = self._xml2json(xml_data)
        return json_data

    def _getAllIPTS(self):
        uri = "http://icat.sns.gov:2080/icat-rest-ws/experiment/SNS/NOM/"
        json_data = self._uri2xml2json(uri)
        self._ipts_list = [ int(x['$'].split('-')[1]) for x in json_data['proposals']['proposal'] ]

    def getIPTSlist(self):
        print "Building IPTS list...",
        if self._ipts_list is None:
            self._getAllIPTS()
        print "DONE"
        return sorted(self._ipts_list)


    def getIPTS(self,ipts,data='all'):
        uri = "http://icat.sns.gov:2080/icat-rest-ws/experiment/SNS/NOM/IPTS-"+str(ipts)+"/"+data
        xml_data = self._uri2xml(uri)
        runs = self._get_runs_from_ipts(xml_data)
        json_data = self._xml2json(xml_data)
        if data == 'all':
            self._get_los_for_ipts(runs,json_data['proposals']['proposal'])
        if data == 'meta':
            self._get_meta_for_ipts(runs,json_data['proposals']['proposal'])

    def getRun(self,run):
        uri = "http://icat.sns.gov:2080/icat-rest-ws/dataset/SNS/NOM/"+str(run)+"/metaOnly"
        json_data = self._uri2xml2json(uri)
        self._get_los_for_run(run, json_data)

    def _get_xml_data_tree(self,data):
        xml_tree = lxml.etree.tostring(self.data, pretty_print=True)
        return xml_tree

    def _get_runs_from_ipts(self,data):
        return [ element.get('id') for element in data.iter() if element.tag == 'run' ]

    def _get_los_for_run(self,run,json_data):
        
        json_metadata = json_data['metadata']
        try:
            ipts_pulled = json_metadata['proposal']['$'].split('-')[1]
        except:
            ipts_pulled = None

        los_data = dict()
        uid = run
        meta_dict = self._get_meta_for_run(json_metadata)
        meta_dict['ipts'] = ipts_pulled
        los_data[uid] = meta_dict
        self._update_master_los(los_data)

    ''' 
    NOTE: Below, the check for list is specific to IPTSs w/ proposal lists. These are:
            Index       IPTS
            -----       ----
            88          8814
            119         9818
    '''

    def _get_meta_for_ipts(self,runs,proposal_json):

        if type(proposal_json) == list:
            ipts_pulled = proposal_json[0]['@id'].split('-')[1]
            runs_data = utils.procNumbers(proposal_json[0]['runRange']['$'])
            for i, proposal in enumerate(proposal_json[1:]):
                runs_data += utils.procNumbers(proposal_json[0]['runRange']['$'])
            startTime = [(':'.join( proposal_json[0]['createTime']['$'].split(':')[0:3])).split('.')[0]]
            for i, proposal in enumerate(proposal_json[1:]):
                startTime += [(':'.join( proposal_json[i+1]['createTime']['$'].split(':')[0:3])).split('.')[0]]
        else:
            ipts_pulled = proposal_json['@id'].split('-')[1]
            runs_data = utils.procNumbers(proposal_json['runRange']['$'])
            startTime = [(':'.join( proposal_json['createTime']['$'].split(':')[0:3])).split('.')[0]]

        meta_ipts_data = dict()
        meta_ipts_data[ipts_pulled] = {'runs' :  runs_data,
                                        'createtime' :  startTime}
        self._update_master_meta_ipts_data(meta_ipts_data)

    def _update_master_meta_ipts_data(self,meta_ipts_data):
        self._meta_ipts_data.update(meta_ipts_data)

    def _get_los_for_ipts(self,runs,proposal_json):
        
        if type(proposal_json) == list:
            ipts_pulled = proposal_json[0]['@id'].split('-')[1]
            runs_data = proposal_json[0]['runs']['run']
            for i, proposal in enumerate(proposal_json[1:]):
                runs_data += proposal_json[i+1]['runs']['run']
        else:
            ipts_pulled = proposal_json['@id'].split('-')[1]
            runs_data = proposal_json['runs']['run']

        los_data = dict()


        # Get run data. If only one run, just get the one run by id.
        if len(runs) == 1:
            uid = proposal_json['runs']['run']['@id']
            x = proposal_json['runs']['run']
            meta_dict = self._get_meta_for_run(x)
            meta_dict['ipts'] = ipts_pulled
            los_data[uid] = meta_dict
           
        else: 
            for x in runs_data:
                uid = x['@id']
                meta_dict = self._get_meta_for_run(x)
                meta_dict['ipts'] = ipts_pulled
                los_data[uid] = meta_dict
        self._update_master_los(los_data)

    def _update_master_los(self,los_data):
        self._los_data.update(los_data)
            


    def _get_meta_for_run(self,metadata):
        meta = dict.fromkeys(self.key_list)

        for key in self.key_list:
            if key in metadata:
                if key == 'duration':
                    meta[key] =  str(int(float(metadata[key]['$'])/60.))+'min'
                elif key == 'startTime':
                    meta[key] = (':'.join( metadata[key]['$'].split(':')[0:3])).split('.')[0] 
                elif key == 'totalCounts':
                    meta[key] = '{:.2E}'.format(Decimal(metadata[key]['$']))
                elif key == 'protonCharge':
                    meta[key] = float("{0:.2f}".format(metadata[key]['$'] / 1e12) )
                else:
                    meta[key] =  metadata[key]['$']
        return meta 

    def get_meta_ipts_data(self):
        return self._meta_ipts_data

    def get_los(self):
        return self._los_data

    def print_runs(self):
        if self._runs is None:
            self._get_runs()
        for run in self._runs:
            print run

    def print_los(self):
        if self._los_data is None:
            print self._los_data, "( No data yet in los dictionary. )"
        los_data = self._los_data
        print "#Scan IPTS  time   starttime         totalCounts     PC/C          title"
        for run in sorted(los_data.keys()):
            print run, 
            for key in self.key_list:
                print los_data[run][key], 
            print

if __name__ == "__main__":
    jv = icat()
    ipts_list = jv.getIPTSlist()
    jv.getIPTSs(ipts_list,data='meta')
    #jv.getIPTSs(ipts_list)
    #jv.getIPTS('10310')
    #jv.getRun(str(run))
    #jv.print_runs()
    jv.print_los()

