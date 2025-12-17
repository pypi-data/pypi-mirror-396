from urllib.parse import urljoin
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from .base import AsyncBase
from .vectorlayer import AsyncVectorLayer
from .view import AsyncVectorLayerView
from .task import AsyncTask

if TYPE_CHECKING:
    from . import AsyncGeoboxClient 
    from .user import AsyncUser 
    from ..api import GeoboxClient
    from ..tileset import Tileset

class AsyncTileset(AsyncBase):

    BASE_ENDPOINT: str = 'tilesets/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str, 
        data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Tilesets object.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the tileset.
            data (Dict, optional): The data of the tileset.
        """
        super().__init__(api=api, uuid=uuid, data=data)


    @classmethod
    async def create_tileset(cls, 
        api: 'AsyncGeoboxClient', 
        name: str, 
        layers: List[Union['AsyncVectorLayer', 'AsyncVectorLayerView']], 
        display_name: str = None, 
        description: str = None,
        min_zoom: int = None, 
        max_zoom: int = None, 
        user_id: int = None) -> 'AsyncTileset':
        """
        [async] Create a new tileset.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the tileset.
            layers (List[VectorLayer | VectorLayerView]): list of vectorlayer and view objects to add to tileset.
            display_name (str, optional): The display name of the tileset.
            description (str, optional): The description of the tileset.
            min_zoom (int, optional): The minimum zoom level of the tileset.
            max_zoom (int, optional): The maximum zoom level of the tileset.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncTileset: The created tileset instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     view = await client.get_view(uuid="12345678-1234-5678-1234-567812345678")
            >>>     tileset = await AsyncTileset.create_tileset(client, 
            ...                                             name="your_tileset_name", 
            ...                                             display_name="Your Tileset", 
            ...                                             description="Your description", 
            ...                                             min_zoom=0, 
            ...                                             max_zoom=14, 
            ...                                             layers=[layer, view])
            or  
            >>>     tileset = await client.create_tileset(name="your_tileset_name", 
            ...                                             display_name="Your Tileset", 
            ...                                             description="Your description", 
            ...                                             min_zoom=0, 
            ...                                             max_zoom=14, 
            ...                                             layers=[layer, view])
        """
        formatted_layers = []
        for item in layers:
            if type(item) == AsyncVectorLayer:
                item_type = 'vector'

            elif type(item) == AsyncVectorLayerView:
                item_type = 'view'

            else:
                continue

            formatted_layers.append({
                'layer_type': item_type,
                'layer_uuid': item.uuid
            })

        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "min_zoom": min_zoom,
            "max_zoom": max_zoom,
            "layers": formatted_layers,
            "user_id": user_id
        }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncTileset(api, item['uuid'], item))


    @classmethod
    async def get_tilesets(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncTileset'], int]:
        """
        [async] Retrieves a list of tilesets.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
        
        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if True, returns the total number of tilesets matching the query. default is False.
            skip (int): number of records to skip. default is 0.
            limit (int): number of records to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared tilesets. default is False.

        Returns:
            List[AsyncTileset] | int: A list of Tileset instances or the total number of tilesets

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tilesets = await AsyncTileset.get_tilesets(client,
            ...         q="name LIKE '%your_tileset_name%'",
            ...         order_by="name A",
            ...         skip=0,
            ...         limit=10,
            ...     )
            or  
            >>>     tilesets = await client.get_tilesets(q="name LIKE '%your_tileset_name%'",
            ...         order_by="name A",
            ...         skip=0,
            ...         limit=10,
            ...     )
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q', None),
            'search': kwargs.get('search', None),
            'search_fields': kwargs.get('search_fields', None),
            'order_by': kwargs.get('order_by', None),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id', None),
            'shared': kwargs.get('shared', False)
        }
        return await super()._get_list(api=api, endpoint=cls.BASE_ENDPOINT, params=params, factory_func=lambda api, item: AsyncTileset(api, item['uuid'], item))
    

    @classmethod
    async def get_tilesets_by_ids(cls, api: 'AsyncGeoboxClient', ids: List[str], user_id: int = None) -> List['AsyncTileset']:
        """
        [async] Retrieves a list of tilesets by their IDs.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            ids (List[str]): The list of tileset IDs.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            List[AsyncTileset]: A list of Tileset instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tilesets = await AsyncTileset.get_tilesets_by_ids(client, ids=['123', '456'])
            or  
            >>>     tilesets = await client.get_tilesets_by_ids(ids=['123', '456'])
        """
        params = {
            'ids': ids,
            'user_id': user_id
        }
        return await super()._get_list_by_ids(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncTileset(api, item['uuid'], item))


    @classmethod
    async def get_tileset(cls, api: 'AsyncGeoboxClient', uuid: str) -> 'AsyncTileset':
        """
        [async] Retrieves a tileset by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the tileset.

        Returns:
            AsyncTileset: The retrieved tileset instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     tileset = await client.get_tileset(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, factory_func=lambda api, item: AsyncTileset(api, item['uuid'], item))


    @classmethod
    async def get_tileset_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncTileset', None]:
        """
        [async] Get a tileset by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the tileset to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncTileset | None: returns the tileset if a tileset matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await VectorLayer.get_tileset_by_name(client, name='test')
            or  
            >>>     tileset = await client.get_tileset_by_name(name='test')
        """
        tilesets = await cls.get_tilesets(api, q=f"name = '{name}'", user_id=user_id)
        if tilesets and tilesets[0].name == name:
            return tilesets[0]
        else:
            return None


    async def update(self, **kwargs) -> None:
        """
        [async] Updates the properties of the tileset.

        Keyword Args:
            name (str): The new name of the tileset.
            display_name (str): The new display name of the tileset.
            description (str): The new description of the tileset.
            min_zoom (int): The new minimum zoom level of the tileset.
            max_zoom (int): The new maximum zoom level of the tileset.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.update_tileset(
            ...         name="new_name",
            ...         display_name="New Display Name",
            ...         description="New description",
            ...         min_zoom=0,
            ...         max_zoom=14
            ...     )
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),
            "description": kwargs.get('description'),
            "min_zoom": kwargs.get('min_zoom'),
            "max_zoom": kwargs.get('max_zoom')
        }

        return await super()._update(urljoin(self.BASE_ENDPOINT, f'{self.uuid}/'), data)


    async def delete(self) -> None:
        """
        [async] Deletes the tileset.

        Raises:
            ValueError: if the tileset uuid is not set.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.delete()
        """
        await super()._delete(urljoin(self.BASE_ENDPOINT, f'{self.uuid}/'))
    
    
    async def get_layers(self, **kwargs) -> Union[List['AsyncVectorLayer'], List['AsyncVectorLayerView']]:
        """
        [async] Retrieves the layers of the tileset with optional parameters.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if True, returns the total number of layers matching the query. default is False.
            skip (int): number of records to skip. default is 0.
            limit (int): number of records to return. default is 10.
            user_id (int): specific user. privileges required.
            shared (bool): if True, returns only the layers that has been shared with you. default is False.

        Returns:
            AsyncVectorLayer | AsyncVectorLayerView: A list of VectorLayer or VectorLayerView instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     layers = await tileset.get_layers()
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'seacrh_fields': kwargs.get('seacrh_fields'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)
        }
        endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/layers/')
        return await super()._get_list(self.api, endpoint, params, factory_func=lambda api, item: AsyncVectorLayer(api, item['uuid'], item['layer_type'], item) if not item['is_view'] else \
                                                                                            AsyncVectorLayerView(api, item['uuid'], item['layer_type'], item))


    async def add_layer(self, layer: Union['AsyncVectorLayer', 'AsyncVectorLayerView']) -> None:
        """
        [async] Adds a layer to the tileset.

        Args:
            layer (AsyncVectorLayer | AsyncVectorLayerView): the layer object to add to the tileset

        Returns:
            None

        Raises:
            ValueError: if the layer input is not a 'VectorLayer' or 'VetorLayerview' object

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.add_layer(layer)
        """
        if type(layer) == AsyncVectorLayer:
            layer_type = 'vector'

        elif type(layer) == AsyncVectorLayerView:
            layer_type = 'view'

        else:
            raise ValueError("layer input must be either 'VectorLayer' or 'VetorLayerview' object")

        data = {
            "layer_type": layer_type,
            "layer_uuid": layer.uuid
        }

        endpoint = urljoin(self.endpoint, 'layers/')
        return await self.api.post(endpoint, data, is_json=False)


    async def delete_layer(self, layer: Union['AsyncVectorLayer', 'AsyncVectorLayerView']) -> None:
        """
        [async] Deletes a layer from the tileset.

        Args:
            layer (AsyncVectorLayer | AsyncVectorLayerView): the layer object to delete from the tileset

        Returns:
            None

        Raises:
            ValueError: if the layer input is not a 'VectorLayer' or 'VetorLayerview' object

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.delete_layer(layer)
        """
        if type(layer) == AsyncVectorLayer:
            layer_type = 'vector'

        elif type(layer) == AsyncVectorLayerView:
            layer_type = 'view'

        else:
            raise ValueError("layer input must be either 'VectorLayer' or 'VetorLayerview' object")

        data = {
            "layer_type": layer_type,
            "layer_uuid": layer.uuid
        }

        endpoint = urljoin(self.endpoint, 'layers/')
        return await self.api.delete(endpoint, data, is_json=False)


    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the file with specified users.

        Args:
            users (List[AsyncUser]): The list of user IDs to share the file with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_usesrs(search='John')
            >>>     await tileset.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the file with specified users.

        Args:
            users (List[AsyncUser]): The list of user IDs to unshare the file with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_usesrs(search='John')
            >>>     await tileset.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the file is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[AsyncUser]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)
        

    async def get_tile_json(self) -> Dict:
        """
        [async] Retrieves the tile JSON configuration.

        Returns:
            Dict: The tile JSON configuration.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.get_tile_json()
        """ 
        endpoint = urljoin(self.endpoint, 'tilejson.json/')
        return await self.api.get(endpoint)


    async def update_tileset_extent(self) -> Dict:
        """
        [async] Updates the extent of the tileset.

        Returns:
            Dict: The response from the API.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.update_tileset_extent()
        """
        endpoint = urljoin(self.endpoint, 'updateExtent/')
        return await self.api.post(endpoint)


    def get_tile_pbf_url(self, x: 'int' = '{x}', y: int = '{y}', z: int = '{z}') -> str:
        """
        Retrieves a tile from the tileset.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optioanl): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.

        Returns:
            str: The url of the tile.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.get_tile_tileset(x=1, y=1, z=1)
        """
        endpoint = f'{self.api.base_url}{self.endpoint}tiles/{z}/{x}/{y}.pbf'

        if not self.api.access_token and self.api.apikey:
            endpoint = f'{endpoint}?apikey={self.api.apikey}'

        return endpoint


    async def seed_cache(self, from_zoom: int = 0, to_zoom: int = 14, extent: list = [], workers: int = 1, user_id: int = 0) -> List['AsyncTask']:
        """
        [async] Seeds the cache of the tileset.

        Args:
            from_zoom (int, optional): The starting zoom level.
            to_zoom (int, optional): The ending zoom level.
            extent (list, optional): The extent of the tileset.
            workers (int, optional): The number of workers to use.
            user_id (int, optional): The user ID.

        Returns:
            List[AsyncTask]: list of task objects.

        Raises:
            ValueError: If the number of workers is not one of the following: 1, 2, 4, 8, 12, 16, 20, 24.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.seed_cache(from_zoom=0, to_zoom=14, extent=[], workers=1)
        """
        data = {
            "from_zoom": from_zoom,
            "to_zoom": to_zoom,
            "extent": extent,
            "workers": workers,
            "user_id": user_id
        }
        return await super()._seed_cache(endpoint=self.endpoint, data=data)


    async def update_cache(self, from_zoom: int, to_zoom: int, extents: List[List[float]] = None, user_id: int = 0) -> List['AsyncTask']:
        """
        [async] Updates the cache of the tileset.

        Args:
            from_zoom (int): The starting zoom level.
            to_zoom (int): The ending zoom level.
            extents (List[List[float]], optional): The list of extents to update the cache for.
            user_id (int, optional): The user ID.

        Returns:
            List[Task]: list of task objects.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.update_cache(from_zoom=0, to_zoom=14, extent=[])
        """
        data = {
            "from_zoom": from_zoom,
            "to_zoom": to_zoom,
            "extents": extents,
            "user_id": user_id
        }
        return await super()._update_cache(endpoint=self.endpoint, data=data)


    @property
    async def cache_size(self) -> int:
        """
        [async] Retrieves the size of the cache of the tileset.

        Returns:
            int: The size of the cache of the tileset.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.cache_size
        """
        return await super()._cache_size(endpoint=self.endpoint)


    async def clear_cache(self) -> None:
        """
        [async] Clears the cache of the tileset.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await AsyncTileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await tileset.clear_cache()
        """
        await super()._clear_cache(endpoint=self.endpoint)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Tileset':
        """
        Switch to sync version of the tileset instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Tileset: the sync instance of the tileset.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.tileset import AsyncTileset
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     tileset = await AsyncTileset.get_tileset(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_tileset = tileset.to_sync(client)
        """
        from ..tileset import Tileset

        return Tileset(api=sync_client, uuid=self.uuid, data=self.data)