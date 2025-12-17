from typing import List, Dict, Callable, TYPE_CHECKING, Union
from urllib.parse import urljoin, urlencode

from ..utils import clean_data
from ..base import Base

if TYPE_CHECKING:
    from .user import AsyncUser
    from .task import AsyncTask
    from . import AsyncGeoboxClient


class AsyncBase(Base):
    BASE_ENDPOINT = ''
    
    def __init__(self, api, **kwargs):
        """
        Initialize the Base class.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient client
            uuid (str, optional): The UUID of the resource
            data (dict, optional): The data of the resource
        """
        super().__init__(api, **kwargs)


    @classmethod
    async def _get_list(cls, api: 'AsyncGeoboxClient',  endpoint: str, params: dict = {}, factory_func: Callable = None, geojson: bool = False) -> Union[List['Base'], int]:
        """Get a list of resources with optional filtering and pagination"""
        query_string = urlencode(clean_data(params)) if params else ''
        endpoint = urljoin(endpoint, f'?{query_string}')
        response = await api.get(endpoint)

        if params.get('return_count'):
            return cls._get_count(response)
        
        if not response:
            return []
            
        if geojson:
            return cls._handle_geojson_response(api, response, factory_func)
            
        return [factory_func(api, item) for item in response]
    

    @classmethod
    async def _get_list_by_ids(cls, api: 'AsyncGeoboxClient', endpoint: str, params: dict = None, factory_func: Callable = None) -> List['Base']:
        """
        Internal method to get a list of resources by their IDs.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient client
            endpoint (str): The endpoint of the resource
            params (dict): Additional parameters for filtering and pagination
            factory_func (Callable): A function to create the resource object

        Returns:
            List[Base]: The list of resource objects
        """
        params = clean_data(params)
        query_string = urlencode(params)
        endpoint = urljoin(endpoint, f'?{query_string}')
        response = await api.get(endpoint)
        return [factory_func(api, item) for item in response]


    @classmethod
    async def _get_detail(cls, api: 'AsyncGeoboxClient', endpoint: str, uuid: str, params: dict = {}, factory_func: Callable = None) -> 'Base':
        """
        Internal method to get a single resource by UUID.
        
        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient client
            uuid (str): The UUID of the resource
            params (dict): Additional parameters for filtering and pagination
            factory_func (Callable): A function to create the resource object

        Returns:
            Base: The resource object
        """
        query_strings = urlencode(clean_data(params))
        endpoint = urljoin(endpoint, f'{uuid}/?{query_strings}')
        response = await api.get(endpoint)
        return factory_func(api, response)
    

    @classmethod
    async def _create(cls, api: 'AsyncGeoboxClient', endpoint: str, data: dict, factory_func: Callable = None) -> 'Base':
        """
        Internal method to create a resource.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient client
            data (dict): The data to create the resource with
            factory_func (Callable): A function to create the resource object

        Returns:
            Base: The created resource object
        """
        data = clean_data(data)
        response = await api.post(endpoint, data)
        return factory_func(api, response)
    

    async def _update(self, endpoint: str, data: dict, clean: bool = True) -> Dict:
        """
        Update the resource.

        Args:
            data (dict): The data to update the resource with
        """
        if clean:
            data = clean_data(data)

        response = await self.api.put(endpoint, data)
        self._update_properties(response)
        return response
    

    async def _delete(self, endpoint: str) -> None:
        """
        Delete the resource.
        """
        await self.api.delete(endpoint)
        self.uuid = None
        self.endpoint = None
        

    async def _share(self, endpoint: str, users: List['AsyncUser']) -> None:
        """
        Internal method to share the resource with the given user IDs.

        Args:
            users (List[AsyncUser]): The user objects to share the resource with
        """
        data = {"user_ids": [user.user_id for user in users]}
        endpoint = urljoin(endpoint, f'share/')
        await self.api.post(endpoint, data, is_json=False)


    async def _unshare(self, endpoint: str, users: List['AsyncUser']) -> None:
        """
        Internal method to unshare the resource with the given user IDs.

        Args:
            users (List[AsyncUser]): The user objects to unshare the resource with
        """
        data = {"user_ids": [user.user_id for user in users]}
        endpoint = urljoin(endpoint, f'unshare/')
        await self.api.post(endpoint, data, is_json=False)


    async def _get_shared_users(self, endpoint: str, params: dict = None) -> List['AsyncUser']:
        """
        Internal method to get the users that the resource is shared with.

        Args:
            endpoint (str): resource endpoint
            params (dict): Additional parameters for filtering and pagination

        Returns:
            List[AsyncUser]: The users that the resource is shared with
        """
        from .user import AsyncUser

        params = clean_data(params)
        query_strings = urlencode(params)
        endpoint = urljoin(endpoint, f'shared-with-users/?{query_strings}')
        response = await self.api.get(endpoint)
        return [AsyncUser(self.api, item['id'], item) for item in response]
    

    async def _get_settings(self, endpoint: str) -> Dict:
        """
        Internal method to get the settings of the resource.

        Args:
            endpoint (str): The endpoint of the resource
        """
        endpoint = urljoin(endpoint, f'settings/?f=json')
        return await self.api.get(endpoint)
    

    async def _set_settings(self, endpoint: str, data: dict) -> None:
        """
        Internal method to set the settings of the resource.

        Args:
            endpoint (str): The endpoint of the resource
            data (dict): The data to set the settings with
        """
        endpoint = urljoin(endpoint, f'settings/')
        return await self.api.put(endpoint, data)


    async def _get_task(self, response, error_message: str) -> List['AsyncUser']:
        from .task import AsyncTask  # avoid circular dependency

        if len(response) == 1 and isinstance(response, list) and response[0].get('task_id'):
            result = [await self.api.get_task(response[0].get('task_id'))]
        elif len(response) == 2 and isinstance(response, list) and (response[0].get('task_id') and response[1].get('task_id')):
            result = [await self.api.get_task(item.get('task_id')) for item in response]
        elif len(response) == 1 and isinstance(response, dict) and response.get('task_id'):
            result = [await self.api.get_task(response.get('task_id'))]
        else:
            raise ValueError(error_message)

        return result


    async def _seed_cache(self, endpoint: str, data: dict) -> List['AsyncTask']:
        """
        Internal method to cache seed the resource.

        Args:
            endpoint (str): The endpoint of the resource
            data (dict): The data to cache seed with
        """
        if data['workers'] not in [1, 2, 4, 8, 12, 16, 20, 24]:
            raise ValueError("workers must be in [1, 2, 4, 8, 12, 16, 20, 24]")
        
        data = clean_data(data)
        endpoint = urljoin(endpoint, f'cache/seed/')
        response = await self.api.post(endpoint, data)
        return await self._get_task(response, 'Failed to seed cache')


    async def _clear_cache(self, endpoint: str) -> None:
        """
        Internal method to clear the cache of the resource.

        Args:
            endpoint (str): The endpoint of the resource
        """
        endpoint = urljoin(endpoint, f'cache/clear/')
        await self.api.post(endpoint)


    async def _cache_size(self, endpoint: str) -> int:
        """
        Internal method to get the size of the cache of the resource.

        Args:
            endpoint (str): The endpoint of the resource
        """
        endpoint = urljoin(endpoint, f'cache/size/')
        return await self.api.post(endpoint)
    

    async def _update_cache(self, endpoint: str, data: Dict = {}) -> List['AsyncTask']:
        """
        Internal method to update the cache of the resource.

        Args:
            endpoint (str): The endpoint of the resource
        """
        data = clean_data(data)
        endpoint = urljoin(endpoint, 'cache/update/')
        response = await self.api.post(endpoint, data)
        return await self._get_task(response, 'Failed to update cache')
