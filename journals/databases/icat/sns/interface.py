#!/usr/bin/env python

'''
Original author: Ricardo Ferraz Leal (ORNL)
Current version by: Marshall McDonnell
'''


from __future__ import print_function
import json
import decimal
import pandas

from journals.utilities import parse_datetime
from journals.databases.icat.sns.communicate import SnsICat 

class SnsICatInterface(object):

    def __init__(self):
        self.icat = SnsICat()
        self.key_list = ['ipts', 'duration', 'startTime', 'totalCounts', 'protonCharge', 'title']

    # Utils
    #------
    @staticmethod
    def _hyphen_range(s):
        """ Takes a range in form of "a-b" and generate a list of numbers between a and b inclusive.
        Also accepts comma separated ranges like "a-b,c-d,f" will build a list which will include
        Numbers from a to b, a to d and f"""
        s = "".join(s.split())  # removes white space
        r = set()
        for x in s.split(','):
            t = x.split('-')
            if len(t) not in [1, 2]:
                logger.error("hash_range is given its arguement as " + s + " which seems not correctly formated.")
            r.add(int(t[0])) if len(t) == 1 else r.update(set(range(int(t[0]), int(t[1]) + 1)))
        l = list(r)
        l.sort()
        l_in_str = ','.join(str(x) for x in l)
        return l_in_str

    def _substitute_keys_in_dictionary(self,obj,old_key,new_key):
        if isinstance(obj, dict):
            if old_key in obj:
                obj[new_key]=obj.pop(old_key)
            return {k: self._substitute_keys_in_dictionary(v,old_key,new_key) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_keys_in_dictionary(elem,old_key,new_key) for elem in obj]

    def _convert_to_datetime(self,obj,key):
        if isinstance(obj, dict):
            if key in obj:
                obj[key] = parse_datetime(obj[key])
            return {k: self._convert_to_datetime(v,key) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_datetime(elem,key) for elem in obj]

    # Functions
    #----------
    def get_instruments(self):
        json_data = self.icat.get_instruments()
        if json_data is not None and 'instrument' in json_data:
            return json_data['instrument']
        else:
            raise Exception("ICAT did not return the expected result....")

    def get_experiments(self,instrument):
        json_data = self.icat.get_experiments(instrument)
        return json_data

    def get_experiments_meta(self, instrument):
        json_data = self.icat.get_experiments_meta(instrument)
        if json_data is not None and 'proposal' in json_data:
            json_data = json_data['proposal']
        else:
            raise Exception("ICAT did not return the expected result....")
        self._substitute_keys_in_dictionary(json_data,'@id','id')
        self._convert_to_datetime(json_data,'createTime')
        return json_data

    def get_experiments_id_and_title(self,instrument):
        json_data = self.get_experiments_meta(instrument)
        json_data = { (int(entry['id'].split('-')[1]),  entry['title']) for entry in json_data }
        return json_data
 
    def get_experiments_id_and_date(self,instrument):
        json_data = self.get_experiments_meta(instrument)
        json_data = { (int(entry['id'].split('-')[1]),  entry['createTime']) for entry in json_data }
        return json_data

    def get_runs_all(self,instrument,experiment):
        json_data = self.icat.get_runs_all(instrument,experiment)
        self._substitute_keys_in_dictionary(json_data,'@id','id')
        self._convert_to_datetime(json_data,'createTime')
        self._convert_to_datetime(json_data,'startTime')
        self._convert_to_datetime(json_data,'endTime')
        return json_data
           

    def get_runs(self,instrument,experiment):
        raw_ranges = self.icat.get_run_ranges(instrument,experiment)
        if raw_ranges is not None and 'runRange' in raw_ranges:
            ranges = self._hyphen_range(raw_ranges["runRange"])
        else:
            raise Exception("ICAT did not return the expected result....")
        return json.loads( "[" + ranges + "]" ) 

    def get_runs_meta(self,instrument,experiment):
        raw_ranges = self.icat.get_run_ranges_meta(instrument,experiment)

        # TODO - Need to change to handle IPTS that return mutliple proposals as a list of dictionaries
        if type(raw_ranges['proposal']) ==  list:
            #ranges = ','.join([ self._hyphen_range(item['runRange']) for item in raw_ranges['proposal'] ])
            raw_ranges['proposal'] = raw_ranges['proposal'][0]
        ranges = self._hyphen_range(raw_ranges['proposal']['runRange'])
        raw_ranges['proposal']['runRange'] = ranges
        self._substitute_keys_in_dictionary(raw_ranges,'@id','id')
        self._convert_to_datetime(raw_ranges,'createTime')
        return raw_ranges

           
    def get_run_number_and_title(self,instrument,experiment):
        json_data = self.icat.get_runs_all(instrument,experiment)
        if json_data is not None and 'proposal' in json_data:
            try: 
                json_data = json_data['proposal']['runs']['run']
            except:
                raise Exception("ICAT did not return the expected result....")
        else:
            raise Exception("ICAT did not return the expected result....")
        
        self._substitute_keys_in_dictionary(json_data,'@id','id')
        data_list = list()
        for entry in json_data:
            title = None
            if 'title' in entry:
                title = entry['title']
            data_list.append([entry['id'],title])
        json_data_subset = {"data" : data_list}
        return json_data_subset

    def get_user_experiments(self,uid):
        json_data = self.icat.get_user_experiments(uid)
        if json_data is not None and 'proposals' in json_data:
            return json_data['proposals']
        else:
            raise Exception("ICAT did not return the expected result....")

    # Unit Functions
    #---------------
    def _get_list_of_all_ipts(self):
        uri = self._ipts_uri 
        json_data = self._uri2xml2json(uri)
        for x in json_data['proposals']['proposal']:
            if isinstance(x['$'], str):
                if x['$'].startswith('IPTS'):
                    self._ipts_list.append(int(x['$'].split('-')[1].split('.')[0])) 

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
            ipts_pulled = int(proposal_json[0]['@id'].split('-')[1])
            runs_data = process_numbers(proposal_json[0]['runRange']['$'])
            for i, proposal in enumerate(proposal_json[1:]):
                runs_data += process_numbers(proposal_json[0]['runRange']['$'])
            startTime = [(':'.join( proposal_json[0]['createTime']['$'].split(':')[0:3])).split('.')[0]]
            for i, proposal in enumerate(proposal_json[1:]):
                startTime += [(':'.join( proposal_json[i+1]['createTime']['$'].split(':')[0:3])).split('.')[0]]
        else:
            ipts_pulled = int(proposal_json['@id'].split('-')[1])
            runs_data = process_numbers(proposal_json['runRange']['$'])
            startTime = [(':'.join( proposal_json['createTime']['$'].split(':')[0:3])).split('.')[0]]

        meta_ipts_data = dict()
        meta_ipts_data[ipts_pulled] = {'runs' :  runs_data,
                                        'createtime' :  startTime}
        self._update_master_meta_ipts_data(meta_ipts_data)

    def _update_master_meta_ipts_data(self,meta_ipts_data):
        self._meta_ipts_data.update(meta_ipts_data)

    def _get_los_for_ipts(self,runs,proposal_json):
        
        if type(proposal_json) == list:
            ipts_pulled = int(proposal_json[0]['@id'].split('-')[1])
            runs_data = proposal_json[0]['runs']['run']
            for i, proposal in enumerate(proposal_json[1:]):
                runs_data += proposal_json[i+1]['runs']['run']
        else:
            ipts_pulled = int(proposal_json['@id'].split('-')[1])
            runs_data = proposal_json['runs']['run']

        los_data = dict()

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
                    meta[key] = '{:.2E}'.format(decimal.Decimal(metadata[key]['$']))
                elif key == 'protonCharge':
                    meta[key] = float("{0:.2f}".format(metadata[key]['$'] / 1e12) )
                else:
                    meta[key] =  metadata[key]['$']
        return meta 


    # Main Functions
    #------------------

    def initializeMetaIptsData(self):
        ipts_list = self.getListOfIPTS()
        self.getIPTSs( ipts_list, data='meta')

        
    def getMetaIptsData(self):
        return self._meta_ipts_data


    def applyIptsFilter(self,ipts_list):
        self.reset_los()
        self.getIPTSs(ipts_list)

    def getDataFrame(self):
        data = self.get_los()
        df = pandas.DataFrame.from_dict(data,orient='index')
        df = df.reset_index()
        df = df.rename(columns={'index': '#Scan', 'duration': 'time', 'protonCharge': 'PC/pC'})
        col_order = ['#Scan', 'ipts', 'time', 'startTime', 'totalCounts', 'PC/pC', 'title']
        df = df[col_order]
        return df


    def getListOfIPTS(self):
        if not self._ipts_list:
            self._get_list_of_all_ipts()
        return sorted(self._ipts_list)


    def getIPTSs(self,proposals,**kwargs):
        for i, ipts in enumerate(proposals):
            self.getIPTS(ipts,**kwargs)


    def getIPTS(self,ipts,data='all'):
        uri = self._ipts_uri + "/IPTS-"+str(ipts)+"/"+data
        xml_data = self._uri2xml(uri)
        runs = self._get_runs_from_ipts(xml_data)
        json_data = self._xml2json(xml_data)
        if data == 'all':
            try:
                self._get_los_for_ipts(runs,json_data['proposals']['proposal'])
            except KeyError:
                print(ipts, json_data['proposals'])
        if data == 'meta':
            self._get_meta_for_ipts(runs,json_data['proposals']['proposal'])


    def getRun(self,run):
        uri = self._run_uri+'/'+ str(run)+"/metaOnly"
        json_data = self._uri2xml2json(uri)
        self._get_los_for_run(run, json_data)


    def reset_los(self):
        self._los_data = dict()
    
    def get_los(self):
        return self._los_data

    def print_runs(self):
        if self._runs is None:
            self._get_runs()
        for run in self._runs:
            print(run)

    def print_los(self):
        if self._los_data is None:
            print(self._los_data, "( No data yet in los dictionary. )")
        los_data = self._los_data
        print("#Scan IPTS  time   starttime         totalCounts     PC/C          title")
        for run in sorted(los_data.keys()):
            print(run, end=' ') 
            for key in self.key_list:
                print(los_data[run][key], end=' ') 
            print()


