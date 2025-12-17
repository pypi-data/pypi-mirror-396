from urllib.parse import quote, urlparse, urlunparse

import petl as etl
import requests


class OneDrive(object):
    '''
    Encapsulates access to OneDrive as a source.
    The source only works for group based files at the moment.

    You will need to set up an App in Microsoft Entra admin center under
    **Applications -> App registrations**.

    * You will need to get the tenant and client_id from the App registration homepage.
    * Create a client secret and make a note of it
    * Make sure that the application has the following Application (not User) permissions,
    and that the admin approval has been granted:
        * Files.Read.All
        * Group.Read.All

    Example usage:

        od = OneDrive('TENANT', 'CLIENT_ID', 'CLIENT_SECRET')

    Display a list of groups, with ids, names and descriptions. 

        od.list_groups()

    Pick one of the groups
        
        od.group = 'GROUP_ID'
    
    Get an Excel file from OneDrive

        petl.fromxlsx(od.source('/data/excel data file.xlsx'))
    '''
    def __init__(self, tenant, client_id, client_secret):
        self.session = None
        self._group = None
        self.tenant = tenant
        self._auth_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials',
        }
        self._setup_session()

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, group):
        self._group = group

    def _setup_session(self):
        if self.session is not None:
            return

        self.session = requests.Session()

        token = self.session.post(
            f'https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token', data=self._auth_data).json()

        self.session.headers.update({
            'Authorization': f'{token['token_type']} {token['access_token']}'
        })

    def list_groups(self, columns=['id', 'displayName', 'description']):
        '''List groups available as a PETL table'''
        return etl.fromdicts(
            self.session
            .get('https://graph.microsoft.com/v1.0/groups')
            .json()['value']
        ).cut(*columns)

    def list_files(self, columns=['id', 'name', 'parentReference']):
        '''List files as a PETL table. Requires that the group has been set.'''
        return etl.fromdicts(
            self.session
            .get(f'https://graph.microsoft.com/v1.0/groups/{self.group}/drive/root/children')
            .json()['value']
        ).cut(*columns)

    def source(self, path):
        '''Return the specified path as a PETL MemorySource.'''
        response = self.session.get(
            f'https://graph.microsoft.com/v1.0/groups/{self.group}/drive/root:/{quote(path)}:/content', stream=True)
        return etl.io.sources.MemorySource(response.content)

    def _graph(self, request, **kwargs):
        url = urlparse('https://graph.microsoft.com/v1.0' +
                       quote(request, safe=':/'))
        return self.session.get(urlunparse(url), **kwargs)
