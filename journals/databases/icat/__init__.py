import requests
import json
HEADERS = {"Accept": "application/json"}


class ICat(object):
    def __init__(self,url_prefix):
        self.url_prefix = url_prefix

    def __del__(self):
        pass

    def _request(self,url_suffix=''):
        request = self.url_prefix + url_suffix
        response = requests.get(request, headers=HEADERS)
        return response.json()
