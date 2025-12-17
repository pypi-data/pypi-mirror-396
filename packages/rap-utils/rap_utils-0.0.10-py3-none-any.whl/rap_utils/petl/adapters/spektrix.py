import json
import os
import urllib.parse

import petl.io.sources
from spektrixpython import SpektrixCredentials, SpektrixRequest

credentials = SpektrixCredentials(client_name=os.environ.get('SPEKTRIX_CLIENT_NAME'),
                                  api_user=os.environ.get('SPEKTRIX_API_USER'),
                                  api_key=os.environ.get('SPEKTRIX_API_KEY'))


class SpektrixAdapter(object):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def source(self, query={}):
        queryString = urllib.parse.urlencode(query)
        data = SpektrixRequest(
            endpoint=f'{self.endpoint}?{queryString}',
            credentials=credentials
        ).get()
        return petl.io.sources.MemorySource(
            bytes(
                json.dumps(data),
                encoding='utf-8'
            )
        )
