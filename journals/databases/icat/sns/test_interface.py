from journals.databases.icat.sns.communicate import SnsICat

class SnsICatInterface(object):
    def __init__(self):
        self.icat = SnsICat()

    def get_instruments(self):
        data_json = self.icat.get_instruments()
        if data_json is not None and 'instrument' in data_json:
            return data_json['instrument']
        else:
            return None
