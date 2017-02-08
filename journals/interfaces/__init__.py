from journals.interfaces.icat import ICAT

class Interface:

    def __init__(self,database):
        interfaces = { "ICAT" : ICAT() }
        self.db = interfaces[database]

    def initialize(self):
        self.db.initializeMetaIptsData()


    def get_meta_data(self):
        return self.db.getMetaIptsData()



    def apply_ipts_filter(self,ipts_list):
        self.db.applyIptsFilter(ipts_list)


    def get_dataframe(self):
        return self.db.getDataFrame()

        
