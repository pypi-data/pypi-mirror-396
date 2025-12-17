from typing import Dict, List, Optional, Union, TYPE_CHECKING
from urllib.parse import urljoin, urlencode

from .base import AsyncBase
from .model3d import AsyncModel
from .file import AsyncFile
from .feature import AsyncFeature
from ..utils import clean_data, join_url_params

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from .task import AsyncTask
    from .attachment import AsyncAttachment
    from ..api import GeoboxClient
    from ..map import Map


class AsyncMap(AsyncBase):
    
    BASE_ENDPOINT = 'maps/'
    
    def __init__(self, 
        api: 'AsyncGeoboxClient',
        uuid: str,
        data: Optional[Dict] = {}):
        """
        Initialize a Map instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the map.
            uuid (str): The unique identifier for the map.
            data (Dict, optional): The data of the map.
        """
        self.map_layers = {
            'layers': []
        }
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    async def get_maps(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncMap'], int]:
        """
        [async] Get list of maps with optional filtering and pagination.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared maps. default is False.

        Returns:
            List[AsyncMap] | int: A list of Map instances or the total number of maps.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     maps = await AsyncMap.get_maps(client, q="name LIKE '%My Map%'")
            or  
            >>>     maps = await client.get_maps(q="name LIKE '%My Map%'")
        """
        params = {
           'f': 'json',
           'q': kwargs.get('q'),
           'search': kwargs.get('search'),
           'search_fields': kwargs.get('search_fields'),
           'order_by': kwargs.get('order_by'),
           'return_count': kwargs.get('return_count', False),
           'skip': kwargs.get('skip', 0),
           'limit': kwargs.get('limit', 10),
           'user_id': kwargs.get('user_id'),
           'shared': kwargs.get('shared', False)
        }
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncMap(api, item['uuid'], item))
    

    @classmethod
    async def create_map(cls, 
        api: 'AsyncGeoboxClient', 
        name: str, 
        display_name: str = None, 
        description: str = None,
        extent: List[float] = None,
        thumbnail: str = None,
        style: Dict = None,
        user_id: int = None) -> 'AsyncMap':
        """
        [async] Create a new map.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the map.
            display_name (str, optional): The display name of the map.
            description (str, optional): The description of the map.
            extent (List[float], optional): The extent of the map.
            thumbnail (str, optional): The thumbnail of the map.
            style (Dict, optional): The style of the map.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncMap: The newly created map instance.

        Raises:
            ValidationError: If the map data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.create_map(client, name="my_map", display_name="My Map", description="This is a description of my map", extent=[10, 20, 30, 40], thumbnail="https://example.com/thumbnail.png", style={"type": "style"})
            or  
            >>>     map = await client.create_map(name="my_map", display_name="My Map", description="This is a description of my map", extent=[10, 20, 30, 40], thumbnail="https://example.com/thumbnail.png", style={"type": "style"})
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "extent": extent,
            "thumbnail": thumbnail,
            "style": style,
            "user_id": user_id,
        }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncMap(api, item['uuid'], item))


    @classmethod
    async def get_map(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncMap':
        """
        [async] Get a map by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the map to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncMap: The map object.

        Raises:
            NotFoundError: If the map with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     map = await client.get_map(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncMap(api, item['uuid'], item))


    @classmethod
    async def get_map_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncMap', None]:
        """
        [async] Get a map by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the map to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncMap | None: returns the map if a map matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map_by_name(client, name='test')
            or  
            >>>     map = await client.get_map_by_name(name='test')
        """
        maps = await cls.get_maps(api, q=f"name = '{name}'", user_id=user_id)
        if maps and maps[0].name == name:
            return maps[0]
        else:
            return None
    

    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the map.

        Keyword Args:
            name (str): The name of the map.
            display_name (str): The display name of the map.
            description (str): The description of the map.
            extent (List[float]): The extent of the map.
            thumbnail (str): The thumbnail of the map.
            style (Dict): The style of the map.

        Returns:
            Dict: The updated map data.

        Raises:
            ValidationError: If the map data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.update(display_name="New Display Name")
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
            "extent": kwargs.get('extent'),
            "thumbnail": kwargs.get('thumbnail'),
            "style": kwargs.get('style'),
        }
        return await super()._update(self.endpoint, data)
    

    async def delete(self) -> None:
        """
        [async] Delete the map.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.delete()
        """
        await super()._delete(self.endpoint)


    @property
    async def style(self) -> Dict:
        """
        [async] Get the style of the map.

        Returns:
            Dict: The style of the map.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.style
        """
        endpoint = urljoin(self.endpoint, 'style/')
        response = await self.api.get(endpoint)
        return response
    
    
    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the map.

        Returns:
            str: The thumbnail of the map.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     map.thumbnail
        """
        return super()._thumbnail()
    

    async def set_readonly(self, readonly: bool) -> None:
        """
        [async] Set the readonly status of the map.

        Args:
            readonly (bool): The readonly status of the map.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.set_readonly(True)
        """
        data = clean_data({
            'readonly': readonly
        })
        endpoint = urljoin(self.endpoint, 'setReadonly/')
        response = await self.api.post(endpoint, data, is_json=False)
        self._update_properties(response)


    async def set_multiuser(self, multiuser: bool) -> None:
        """
        [async] Set the multiuser status of the map.

        Args:
            multiuser (bool): The multiuser status of the map.

        Returns:
            None
            
        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.set_multiuser(True)
        """
        data = clean_data({
            'multiuser': multiuser
        })
        endpoint = urljoin(self.endpoint, 'setMultiuser/')
        response = await self.api.post(endpoint, data, is_json=False)
        self._update_properties(response)



    def wmts(self, scale: int = None) -> str:
        """
        Get the WMTS URL of the map.

        Args:
            scale (int): The scale of the map. value are: 1, 2

        Returns:
            str: The WMTS URL of the map.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     map.wmts(scale=1)
        """
        endpoint = urljoin(self.api.base_url, f'{self.endpoint}wmts/')
        if scale:
            endpoint = f"{endpoint}?scale={scale}"

        if not self.api.access_token and self.api.apikey:
            endpoint = join_url_params(endpoint, {"apikey": self.api.apikey})

        return endpoint

    
    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the map with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to share the map with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await map.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the map with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to unshare the map with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await users = client.search_users(search='John')
            >>>     await map.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the map is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[AsyncUser]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    async def seed_cache(self, 
        from_zoom: int = None, 
        to_zoom: int = None, 
        extent: List[float] = None, 
        workers: int = 1, 
        user_id: int = None, 
        scale: int = None) -> List['AsyncTask']:
        """
        [async] Seed the cache of the map.

        Args:
            from_zoom (int, optional): The zoom level to start caching from.
            to_zoom (int, optional): The zoom level to stop caching at.
            extent (List[float], optional): The extent of the map.
            workers (int, optional): The number of workers to use. default is 1.
            user_id (int, optional): Specific user. privileges required.
            scale (int, optional): The scale of the map.

        Returns:
            List[AsyncTask]: The task instance of the cache seeding operation.

        Raises:
            ValueError: If the workers is not in [1, 2, 4, 8, 12, 16, 20, 24].
            ValueError: If the cache seeding fails.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await map.seed_cache(from_zoom=0, to_zoom=10, extent=[10, 20, 30, 40], workers=1, scale=1)
        """
        data = {
            'from_zoom': from_zoom,
            'to_zoom': to_zoom,
            'extent': extent,
            'workers': workers,
            'user_id': user_id,
            'scale': scale
        }
        return await super()._seed_cache(self.endpoint, data)


    async def update_cache(self, 
                     from_zoom: int = None, 
                     to_zoom: int = None, 
                     extent: List[float] = None, 
                     user_id: int = None, 
                     scale: int = None) -> List['AsyncTask']:
        """
        [async] Update the cache of the map.

        Args:
            from_zoom (int, optional): The zoom level to start caching from.
            to_zoom (int, optional): The zoom level to stop caching at.
            extent (List[float], optional): The extent of the map.
            user_id (int, optional): Specific user. privileges required.
            scale (int, optional): The scale of the map.

        Returns:
            List[AsyncTask]: The task instance of the cache updating operation.

        Raises:
            ValueError: If the cache updating fails.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.update_cache(from_zoom=0, to_zoom=10, extent=[10, 20, 30, 40], scale=1)
        """
        data = {
            'from_zoom': from_zoom,
            'to_zoom': to_zoom,
            'extent': extent,
            'user_id': user_id,
            'scale': scale
        }
        return await super()._update_cache(self.endpoint, data)


    async def clear_cache(self) -> None:
        """
        [async] Clear the cache of the map.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.clear_cache()
        """
        return await super()._clear_cache(self.endpoint)


    @property
    async def cache_size(self) -> int:
        """
        [async] Get the size of the cache of the map.

        Returns:
            int: The size of the cache of the map.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.cache_size
        """
        return await super()._cache_size(self.endpoint)


    @property
    def settings(self) -> Dict:
        """
        Get the settings of the map

        Returns:
            Dict: the settings of the map.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(uuid="12345678-1234-5678-1234-567812345678")
            >>>     map.settings
        """
        return self.json.get('settings', {
            'general_settings': {},
            'edit_settings': {},
            'snap_settings': {},
            'controls': [],
            'search_settings': {},
            'marker_settings': {},
            'terrain_settings': {},
            'grid_settings': {},
            'view_settings': {},
            'toc_settings': []
        })
    

    async def update_settings(self, settings: Dict) -> Dict:
        """
        [async] Update the settings

        settings (Dict): settings dictionary

        Returns:
            Dict: updated settings

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     map1 = await client.get_map(uuid="12345678-1234-5678-1234-567812345678")
            >>>     map2 = await client.get_map(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map1.update_settings(map2.settings)
        """
        return await super()._set_settings(self.endpoint, settings)    


    async def set_settings(self, **kwargs) -> Dict:
        """
        [async] Set the settings of the map using keywords

        Keyword Args:
            map_unit (str): 'latlng' | 'utm'.
            base_map (str): 'OSM' | 'google' | 'blank'.
            flash_color (str): 'rgb(255,0,0)' (rgb color or rgba color or hex color ).
            highlight_color (str): 'rgb(255,0,0)' (rgb color or rgba color or hex color ).
            selection_color (str): 'rgb(255,0,0)' (rgb color or rgba color or hex color ).
            selectable_layers (str): 'ALL' | null | Comma separated list of layers.
            calendar_type (str): The type of the calendar.
            edit_settings (dict): The settings of the edit.
            snap_tolerance (int): number of pixels for snap tolerance.
            snap_unit (str): pixels.
            snap_mode (str): 'both' | 'edge' | 'vertex'.
            snap_cache (int): number of total features for snap cache.
            controls (List[str]): The controls of the map.
            search_mode (str): 'both' | 'markers' | 'layers'.
            search_layers (str): 'ALL' | null | Comma separated list of layers.
            geosearch (bool): The geosearch of the map.
            remove_unused_tags (bool): The remove unused tags of the map.
            terrain_layer (str): The terrain layer of the map.
            exaggeration (int): The exaggeration of the terrain.
            enable_grid (bool): The enable grid of the map.
            grid_unit (str): The unit of the grid.
            grid_width (int): The width of the grid.
            grid_height (int): The height of the grid.
            grid_minzoom (int): The minzoom of the grid.
            grid_maxzoom (int): The maxzoom of the grid.
            bearing (int): The bearing of the map.
            pitch (int): The pitch of the map.
            center (List[float]): The center of the map.
            zoom (int): The zoom of the map.
            toc_settings (List): The settings of the toc.
            custom_basemaps (List[str]): The custom basemaps of the map.
            show_maptip_on (str): 'ALL' | null | Comma separated list of layers.
            snappable_layers (str): 'ALL' | null | Comma separated list of layers.

        Returns:
            Dict: The response of the API.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.set_settings(zoom=10)
        """
        general_settings = {'map_unit', 'base_map', 'flash_color', 'highlight_color', 
                            'selection_color', 'selectable_layers', 'calendar_type', 'custom_basemaps', 'show_maptip_on'}
        edit_settings = {'editable_layers', 'target_layer'}
        snap_settings = {'snap_tolerance', 'snap_unit', 'snap_mode', 'snap_cache', 'snappable_layers'}
        search_settings = {'search_mode', 'search_layers', 'geosearch'}
        marker_settings = {'remove_unused_tags'}
        terrain_settings = {'terrain_layer', 'exaggeration'}
        grid_settings = {'enable_grid', 'grid_unit', 'grid_width', 'grid_height', 'grid_minzoom', 'grid_maxzoom'}
        view_settings = {'bearing', 'pitch', 'center', 'zoom'}

        settings = self.settings

        for key, value in kwargs.items():
            if key in general_settings:
                settings['general_settings'][key] = value
            elif key in edit_settings:
                settings['edit_settings'][key] = value
            elif key in snap_settings:
                settings['snap_settings'][key] = value
            elif key == 'controls':
                settings['controls'] = value
            elif key in search_settings:
                settings['search_settings'][key] = value
            elif key in marker_settings:
                settings['marker_settings'][key] = value
            elif key in terrain_settings:
                settings['terrain_settings'][key] = value
            elif key in grid_settings:
                settings['grid_settings'][key] = value
            elif key in view_settings:
                settings['view_settings'][key] = value
            elif key == 'toc_settings':
                settings['toc_settings'] = value

        return await super()._set_settings(self.endpoint, settings)    


    async def get_markers(self) -> Dict:
        """
        [async] Get the markers of the map.

        Returns:
            Dict: The markers of the map.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.get_markers()
        """
        endpoint = urljoin(self.endpoint, 'markers/')
        return await self.api.get(endpoint)
    

    async def set_markers(self, data: Dict) -> Dict:
        """
        [async] Set the markers of the map.

        Args:
            data (dict): The data of the markers.

        Returns:
            Dict: The response of the API.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     data = {
            ...         'tags': {
            ...             '#general': {
            ...                 'color': '#ff0000',
            ...             }
            ...         },
            ...         'locations': [
            ...             {
            ...                 'id': 1,
            ...                 'tag': '#general',
            ...                 'name': 'test',
            ...                 'geometry': [
            ...                     51.13162784422988,
            ...                     35.766603814763045
            ...                 ],
            ...                 'description': 'string'
            ...             }
            ...         ]
            ...     }
            >>>     await map.set_markers(data)
        """
        endpoint = urljoin(self.endpoint, 'markers/')
        response = await self.api.put(endpoint, data)
        return response
    

    async def get_models(self, json=False) -> Union[List['AsyncModel'], Dict]:
        """
        [async] Get the map models.

        Args:
            json (bool, optional): If True, return the response as a dictionary.

        Returns:
            List[AsyncModel] | Dict: map models objects or the response.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.get_models(json=True)
        """
        endpoint = urljoin(self.endpoint, 'models/')
        response = await self.api.get(endpoint)
        if not response or json:
            return response
        else:
            return [AsyncModel(self.api, model['obj'], model) for model in response['objects'] if response.get('objects')]
    

    async def set_models(self, data: Dict) -> List['AsyncModel']:
        """
        [async] Set multiple models on the map.

        Args:
            data (Dict): the data of the models and their location on the map. check the example for the data structure.

        Returns:
            List[AsyncModel]: the map models objects

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(uuid="12345678-1234-5678-1234-567812345678")
            >>>     data = {'objects': [
            ...         {
            ...             "name": "transmission_tower",
            ...             "alias": None,
            ...             "desc": None,
            ...             "obj": "12345678-1234-5678-1234-567812345678",
            ...             "loc": [53.1859045261684, 33.37762747390032, 0.0],
            ...             "rotation": [0.0, 0.0, 0.0],
            ...             "scale": 1.0,
            ...             "min_zoom": 0,
            ...             "max_zoom": 22
            ...         }
            ...     ]}
            >>>     await map.set_models(data)
        """
        endpoint = urljoin(self.endpoint, 'models/')
        response = await self.api.put(endpoint, data)
        return [AsyncModel(self.api, model['obj'], model) for model in response['objects'] if response.get('objects')]


    async def add_model(self, 
        model: 'AsyncModel', 
        location: List[float], 
        rotation: List[float] = [0.0, 0.0, 0.0],
        scale: float = 1.0,
        min_zoom: int = 0,
        max_zoom: int = 22,
        alias: str = None,
        description: str = None) -> List['AsyncModel']:
        """
        [async] Add a model the map.

        Args:
            model (Model): The model object.
            location (List[float]): location of the model on the map. a list with three float values.
            rotation (List[float], optional): rotation of the model on the map. a list with three float vlaues. default is [0.0, 0.0, 0.0].
            scale (float, optional): the scale of the model on the map.
            min_zoom (int, optional): minimum zoom level.
            max_zoom (int, optional): maximum zoom level.
            alias (str, optional): alias of the model on the map.
            description (str, optional): the description of the model on the map.

        Returns:
            List['AsyncModel']: The map model objects

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     model = await client.get_model(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.add_model(model=model,
            ...                     location=[53.53, 33.33, 0.0],
            ...                     rotation=[0.0, 0.0, 0.0],
            ...                     scale=1.0,
            ...                     min_zoom=0,
            ...                     max_zoom=22,
            ...                     alias=None,
            ...                     description=None)
        """
        data = await self.get_models(json=True)
        if data and data.get('objects') and isinstance(data['objects'], list):
            data.get('objects').append({
                        'name': model.name,
                        'alias': alias,
                        'desc': description,
                        'obj': model.uuid,
                        'loc': location,
                        'rotation': rotation,
                        'scale': scale,
                        'min_zoom': min_zoom,
                        'max_zoom': max_zoom
                    })
        else:
            data = {'objects':[
                    {
                        'name': model.name,
                        'alias': alias,
                        'desc': description,
                        'obj': model.uuid,
                        'loc': location,
                        'rotation': rotation,
                        'scale': scale,
                        'min_zoom': min_zoom,
                        'max_zoom': max_zoom
                    }
                ]
            }

        endpoint = urljoin(self.endpoint, 'models/')
        response = await self.api.put(endpoint, data)
        return [AsyncModel(self.api, model['obj'], model) for model in response['objects']]


    def image_tile_url(self, x: str = '{x}', y: str = '{y}', z: str = '{z}', format='.png') -> str:
        """
        Get map image tile url

        Returns:
            str: the image tile url

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     map.image_tile_url()
            >>>     map.image_tile_url(x=1, y=2, z=3, format='.pbf')
        """
        endpoint = f"{self.api.base_url}{self.endpoint}tiles/{z}/{x}/{y}{format}"

        if not self.api.access_token and self.api.apikey:
            endpoint = f'{endpoint}?apikey={self.api.apikey}'

        return endpoint
    

    async def export_map_to_image(self, bbox: List, width: int, height: int) -> 'AsyncTask':
        """
        [async] Export the map to image

        Args:
            bbox (List): e.g. [50.275, 35.1195, 51.4459, 36.0416]
            width (int): minimum: 10, maximum: 10000
            height (int): minimum: 10, maximum: 10000

        Returns:
            Task: the task object

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await map.export_map_to_image(bbox=[50.275, 35.1195, 51.4459, 36.0416],
            ...                                         width=1024,
            ...                                         height=1024)
        """
        data = clean_data({
            'uuid': self.uuid,
            'bbox': bbox,
            'width': width,
            'height': height
        })
        query_string = urlencode(data)
        endpoint = urljoin(self.endpoint, 'export/')
        endpoint = f"{endpoint}?{query_string}"
        response = await self.api.post(endpoint)
        return await self.api.get_task(response['task_id'])


    async def get_attachments(self, **kwargs) -> List['AsyncAttachment']:
        """
        [async] Get the resouces attachments

        Keyword Args:
            element_id (str): the id of the element with attachment.
            search (str): search term for keyword-based searching among all textual fields.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            return_count (bool): Whether to return total count. default is False.

        Returns:
            List[Attachment] | int: A list of attachments instances or the total number of attachments.

        Raises:
            TypeError: if the resource type is not supported

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await map.get_attachments()
        """
        from .attachment import AsyncAttachment

        return await AsyncAttachment.get_attachments(self.api, resource=self, **kwargs)
    
    
    async def create_attachment(self, 
        name: str, 
        loc_x: int,
        loc_y: int,
        file: 'AsyncFile',
        feature: 'AsyncFeature' = None,
        display_name: str = None, 
        description: str = None) -> 'AsyncAttachment':
        """
        [async] Create a new Attachment.

        Args:
            name (str): The name of the scene.
            loc_x (int): x parameter of the attachment location.
            loc_y (int): y parameter of the attachment location.
            file (File): the file object.
            feature (Feature, optional): the feature object.
            display_name (str, optional): The display name of the scene.
            description (str, optional): The description of the scene.

        Returns:
            Attachment: The newly created Attachment instance.

        Raises:
            ValidationError: If the Attachment data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await AsyncMap.get_map(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     files = await client.get_files()
            >>>     file = files[0]
            >>>     await map.create_attachment(name='test', loc_x=10, loc_y=10, file=file)
        """
        from .attachment import AsyncAttachment

        return await AsyncAttachment.create_attachment(self.api,
            name=name,
            loc_x=loc_x,
            loc_y=loc_y,
            resource=self,
            file=file,
            feature=feature,
            display_name=display_name,
            description=description)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Map':
        """
        Switch to sync version of the map instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Map: the sync instance of the map.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.map import AsyncMap
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     map = await AsyncMap.get_map(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_map = map.to_sync(client)
        """
        from ..map import Map

        return Map(api=sync_client, uuid=self.uuid, data=self.data)