from typing import List, Dict, Optional, TYPE_CHECKING
from urllib.parse import urljoin

from .base import AsyncBase
from ..utils import clean_data

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from ..api import GeoboxClient
    from ..apikey import ApiKey


class AsyncApiKey(AsyncBase):

    BASE_ENDPOINT = 'apikeys/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        key_id: int,
        data: Optional[Dict] = {}):
        """
        Initialize an apikey instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            key_id (int): The unique identifier for the apikey.
            data (Dict, optional): The data of the apikey.
        """
        super().__init__(api, data=data)
        self.key_id = key_id
        self.endpoint = urljoin(self.BASE_ENDPOINT, str(self.id))


    def __repr__(self) -> str:
        """
        Return a string representation of the attachment.

        Returns:
            str: The string representation of the attachment.
        """
        return f'AsyncApiKey(id={self.key_id}, name={self.name}, revoked={self.revoked})'


    @classmethod
    async def get_apikeys(cls, api: 'AsyncGeoboxClient', **kwargs) -> List['AsyncApiKey']:
        """
        [async] Get a list of apikeys

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

        Keyword Args:
            search (str): search term for keyword-based searching among all textual fields.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of layers to skip. default is 0.
            limit (int): Maximum number of layers to return. default is 10.
            user_id (int): Specific user. privileges required.
        
        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikeys = await AsyncApiKey.get_apikeys(client)
            or  
            >>>     apikeys = await client.get_apikeys()
        """
        params = {
            'search': kwargs.get('search'),
            'order_by': kwargs.get('order_by'),
            'skip': kwargs.get('skip'),
            'limit': kwargs.get('limit'),
            'user_id': kwargs.get('user_id')
        }
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncApiKey(api, item['id'], item))
    

    @classmethod
    async def create_apikey(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> 'AsyncApiKey':
        """
        [async] Create an ApiKey

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): name of the key.
            user_id (int, optional): Specific user. privileges required.

        Returns: 
            ApiKey: the apikey object

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await AsyncApiKey.create_apikey(client, name='test')
            or  
            >>>     apikey = await client.create_apikey(name='test')
        """
        data = clean_data({
            'name': name,
            'user_id': user_id
        })
        response = await api.post(cls.BASE_ENDPOINT, payload=data, is_json=False)
        return AsyncApiKey(api, response['id'], response)
    

    @classmethod
    async def get_apikey(cls, api: 'AsyncGeoboxClient', key_id: int) -> 'AsyncApiKey':
        """
        [async] Get an ApiKey

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            key_id (str): the id of the apikey.

        Returns:
            ApiKey: the ApiKey object

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await AsyncApiKey.get_apikey(client, key_id=1)
            or  
            >>>     apikey = await client.get_apikey(key_id=1) 
        """
        params = {
            'f': 'json'
        }
        return await super()._get_detail(api=api,
            endpoint=cls.BASE_ENDPOINT,
            uuid=key_id, 
            params=params, 
            factory_func=lambda api, item: AsyncApiKey(api, item['id'], item))


    @classmethod
    async def get_apikey_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> 'AsyncApiKey':
        """
        [async] Get an ApiKey by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the key to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            ApiKey | None: returns the key if a key matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await AsyncApiKey.get_apikey_by_name(client, name='test')
            or  
            >>>     apikey = await client.get_apikey_by_name(name='test')
        """
        apikeys = await cls.get_apikeys(api, search=name, user_id=user_id)
        if apikeys and apikeys[0].name == name:
            return apikeys[0]
        else:
            return None
    

    async def update(self, name: str, user_id: int = None) -> Dict:
        """
        [async] Update an ApiKey

        Args:
            name (str): the name of the key
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Dict: Updated ApiKey data

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await AsyncApiKey.get_apikey(client, key_id=1)
            >>>     await apikey.update(name="updated_name")
        """
        data = clean_data({
            "name": name,
            "user_id": user_id
        })

        response = await self.api.put(self.endpoint, data, is_json=False)
        self._update_properties(response)
        return response


    async def delete(self) -> None:
        """
        [async] Delete the ApiKey.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await AsyncApiKey.get_apikey(client, key_id=1)
            >>>     await apikey.delete()
        """
        await super()._delete(self.endpoint)
        self.key_id = None


    async def revoke(self) -> None:
        """
        [async] Revoke an ApiKey

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await AsyncApiKey.get_apikey(client, key_id=1)
            >>>     await apikey.revoke()
        """
        endpoint = f"{self.endpoint}/revoke"
        await self.api.post(endpoint)
        self.data['revoked'] = True


    async def grant(self) -> None:
        """
        [async] Grant an ApiKey

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await AsyncApiKey.get_apikey(client, key_id=1)
            >>>     await apikey.grant()
        """
        endpoint = f"{self.endpoint}/grant"
        await self.api.post(endpoint)
        self.data['revoked'] = False


    def to_sync(self, sync_client: 'GeoboxClient') -> 'ApiKey':
        """
        Switch to sync version of the apikey instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            ApiKey: the sync instance of the apikey.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.apikey import AsyncApiKey
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     apikey = await AsyncApiKey.get_apikey(async_client, key_id=1)
            >>>     sync_apikey = apikey.to_sync(client)
        """
        from ..apikey import ApiKey

        return ApiKey(api=sync_client, key_id=self.key_id, data=self.data)