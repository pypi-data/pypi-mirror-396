import json
import os
import urllib

import petl.io.json
import petl.io.sources
from pyairtable import Api

api = Api(os.environ['AIRTABLE_ACCESS_TOKEN'])


class Airtable(object):
    '''
    Encapsulates an Airtable table

    Expects to have environment variable AIRTABLE_ACCESS_TOKEN which requires
    data.records:read permissions to access the data.

    NB May be useful to add schema.bases:read permission to enable searching for bases and tables.

    Usage:

    table = Airtable('base_id', 'table_name')
    data = table.query().unpackdict('fields')
    '''

    def __init__(self, base_id, table_name):
        self._table = api.table(base_id, table_name)

    def source(self, *args, **kwargs) -> petl.io.sources.MemorySource:
        '''
        Run query against the specified table

        Args are passed to the all function

        The result is returned 
        '''
        data = self._table.all(*args, **kwargs)
        return petl.io.sources.MemorySource(bytes(json.dumps(data), encoding='utf-8'))
    
    def get(self, *args, **kwargs) -> petl.io.json.JsonView:
        try:
            return petl.io.json.fromjson(self.source(*args, **kwargs)).unpackdict('fields')
        except urllib.error.HTTPError as err:
            raise err
