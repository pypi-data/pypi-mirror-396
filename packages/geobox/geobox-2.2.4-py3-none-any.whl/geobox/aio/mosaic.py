from urllib.parse import urljoin, urlencode
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from ..utils import clean_data
from .raster import AsyncRaster

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from .task import AsyncTask
    from ..api import GeoboxClient
    from ..mosaic import Mosaic


class AsyncMosaic(AsyncRaster):

    BASE_ENDPOINT: str = 'mosaics/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str, 
        data: Optional[Dict] = {}):
        """
        Initialize a Mosaic instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The unique identifier for the mosaic.
            data (Dict, optional): The data of the mosaic.
        """
        super().__init__(api, uuid, data)
    

    @classmethod
    async def get_mosaics(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncMosaic'], int]:
        """
        [async] Get a list of mosaics.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'".
            seacrh (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if true, the number of mosaics will be returned.
            skip (int): number of mosaics to skip. minimum value is 0.
            limit (int): maximum number of mosaics to return. minimum value is 1.
            user_id (int): specific user. privileges required.
            shared (bool): Whether to return shared mosaics. default is False.

        Returns:
            List[AsyncMosaic] | int: A list of Mosaic instances or the number of mosaics.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaics = await AsyncMosaic.get_mosaics(client, q="name LIKE '%GIS%'")
            or  
            >>>     mosaics = await client.get_mosaics(q="name LIKE '%GIS%'")
        """
        params = {
            'terrain': kwargs.get('terrain', None),
            'f': 'json',
            'q': kwargs.get('q', None),
            'search': kwargs.get('search', None),
            'search_fields': kwargs.get('search_fields', None),
            'order_by': kwargs.get('order_by', None),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 100),
            'user_id': kwargs.get('user_id', None),
            'shared': kwargs.get('shared', False)
        }
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncMosaic(api, item['uuid'], item))
    
    
    @classmethod
    async def get_mosaics_by_ids(cls, api: 'AsyncGeoboxClient', ids: List[str], user_id: int = None) -> List['AsyncMosaic']:
        """
        [async] Get mosaics by their IDs.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            ids (List[str]): The IDs of the mosaics.
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[AsyncMosaic]: A list of Mosaic instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaics = await AsyncMosaic.get_mosaics_by_ids(client, ids=['1, 2, 3'])
            or  
            >>>     mosaics = await client.get_mosaics_by_ids(ids=['1, 2, 3'])
        """
        params = {
            'ids': ids,
            'user_id': user_id
        }
        endpoint = urljoin(cls.BASE_ENDPOINT, 'get-mosaics/')
        return await super()._get_list_by_ids(api, endpoint, params, factory_func=lambda api, item: AsyncMosaic(api, item['uuid'], item))

    
    @classmethod
    async def create_mosaic(cls,
        api: 'AsyncGeoboxClient',
        name:str,
        display_name: str = None,
        description: str = None,
        pixel_selection: str = None,
        min_zoom: int = None,
        user_id: int = None) -> 'AsyncMosaic':
        """
        [async] Create New Raster Mosaic

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the mosaic.
            display_name (str, optional): The display name of the mosaic.
            description (str, optional): The description of the mosaic.
            pixel_selection (str, optional): The pixel selection of the mosaic.
            min_zoom (int, optional): The minimum zoom of the mosaic.
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncMosaic: The created mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.create_mosaic(client, name='mosaic_name')
            or  
            >>>     mosaic = await client.create_mosaic(name='mosaic_name')
        """
        data = {
            'name': name,
            'display_name': display_name,
            'description': description,
            'pixel_selection': pixel_selection,
            'min_zoom': min_zoom,
            'user_id': user_id
        }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncMosaic(api, item['uuid'], item))
    

    @classmethod
    async def get_mosaic(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncMosaic':
        """
        [async] Get a mosaic by uuid.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the mosaic.
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncMosaic: The mosaic object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     mosaic = await client.get_mosaic(uuid="12345678-1234-5678-1234-567812345678")
        """      
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncMosaic(api, item['uuid'], item))


    @classmethod
    async def get_mosaic_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncMosaic', None]:
        """
        [async] Get a mosaic by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the mosaic to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncMosaic | None: returns the mosaic if a mosaic matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic_by_name(client, name='test')
            or  
            >>>     mosaic = await client.get_mosaic_by_name(name='test')
        """
        mosaics = await cls.get_mosaics(api, q=f"name = '{name}'", user_id=user_id)
        if mosaics and mosaics[0].name == name:
            return mosaics[0]
        else:
            return None


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update a mosaic.

        Keyword Args:
            name (str): The name of the mosaic.
            display_name (str): The display name of the mosaic.
            description (str): The description of the mosaic.
            pixel_selection (str): The pixel selection of the mosaic.
            min_zoom (int): The minimum zoom of the mosaic.

        Returns:
            Dict: the updated data

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.update(name='new_name', display_name='new_display_name', description='new_description', pixel_selection='new_pixel_selection', min_zoom=10)
        """
        data = {
            'name': kwargs.get('name'),
            'display_name': kwargs.get('display_name'),
            'description': kwargs.get('description'),
            'pixel_selection': kwargs.get('pixel_selection'),
            'min_zoom': kwargs.get('min_zoom')
        }
        return await super()._update(self.endpoint, data)


    async def delete(self) -> None:
        """
        [async] Delete the mosaic.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.delete()
        """
        await super()._delete(self.endpoint)
    

    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail of the mosaic.

        Returns:
            str: The thumbnail url of the mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     mosaic.thumbnail
        """
        return super()._thumbnail(format="")


    async def get_point(self, lat: float, lng: float) -> List[float]:
        """
        [async] Get the points of the mosaic.

        Args:
            lat (float): The latitude of the point.
            lng (float): The longitude of the point.

        Returns:
            List[float]: The points of the mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.get_point(lat=60, lng=50)
        """
        return await super().get_point(lat, lng)


    def get_render_png_url(self, x: int = '{x}', y: int = '{y}', z: int = '{z}', **kwargs) -> str:
        """
        Get the tile render URL of the mosaic.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optional): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.

        Keyword Args:
            indexes (str, optional): list of comma separated band indexes to be rendered. e.g. 1, 2, 3
            nodata (int, optional)
            expression (str, optional): band math expression. e.g. b1*b2+b3
            rescale (List, optional): comma (',') separated Min,Max range. Can set multiple time for multiple bands.
            color_formula (str, optional): Color formula. e.g. gamma R 0.5
            colormap_name (str, optional)
            colormap (str, optional): JSON encoded custom Colormap. e.g. {"0": "#ff0000", "1": "#00ff00"} or [[[0, 100], "#ff0000"], [[100, 200], "#00ff00"]]

        Returns:
            str: The tile render URL of the mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     mosaic.get_tile_render_url(x=1, y=1, z=1)
        """
        return super().get_render_png_url(x, y, z, **kwargs)
    

    def get_tile_png_url(self, x: int = '{x}', y: int = '{y}', z: int = '{z}') -> str:
        """
        Get the tile PNG URL of the mosaic.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optional): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.

        Returns:
            str: The tile PNG URL of the mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     mosaic.get_tile_png_url(x=1, y=1, z=1)
        """
        return super().get_tile_png_url(x, y, z)
    

    async def get_tile_json(self) -> str:
        """
        [async] Get the tile JSON of the raster.

        Returns:
            str: The tile JSON of the raster.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.get_tile_json()
        """
        return await super().get_tile_json()
    

    def wmts(self, scale: int = None) -> str:
        """
        Get the WMTS URL

        Args:
            scale (int, optional): The scale of the raster. values are: 1, 2

        Returns:
            str: The WMTS URL of the mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     mosaic.wmts(scale=1)
        """
        return super().wmts(scale)

    @property
    async def settings(self) -> Dict:
        """
        [async] Get the settings of the mosaic.

        Returns:
            Dict: The settings of the mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.settings
        """
        return await super().settings
    

    async def update_settings(self, settings: Dict) -> Dict:
        """
        [async] Update the settings

        settings (Dict): settings dictionary

        Returns:
            Dict: updated settings

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic1 = await client.get_mosaic(uuid="12345678-1234-5678-1234-567812345678")
            >>>     mosaic2 = await client.get_mosaic(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic1.update_settings(mosaic2.settings)
        """
        return await super().update_settings(settings)  
    
    
    async def set_settings(self, **kwargs) -> None:
        """
        [async] Set the settings of the mosaic.

        Keyword Args:
            nodata (int): The nodata value of the raster.
            indexes (list[int]): The indexes of the raster.
            rescale (list[int]): The rescale of the raster.
            colormap_name (str): The colormap name of the raster.
            color_formula (str): The color formula of the raster.
            expression (str): The expression of the raster.
            exaggeraion (int): The exaggeraion of the raster.
            min_zoom (int): The min zoom of the raster.
            max_zoom (int): The max zoom of the raster.
            use_cache (bool): Whether to use cache of the raster.
            cache_until_zoom (int): The cache until zoom of the raster.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.set_settings(nodata=0, 
            ...                                 indexes=[1], 
            ...                                 rescale=[[0, 10000]], 
            ...                                 colormap_name='gist_rainbow', 
            ...                                 color_formula='Gamma R 0.5', 
            ...                                 expression='b1 * 2', 
            ...                                 exaggeraion=10, 
            ...                                 min_zoom=0, 
            ...                                 max_zoom=22, 
            ...                                 use_cache=True, 
            ...                                 cache_until_zoom=17)
        """
        return await super().set_settings(**kwargs)


    async def get_rasters(self, user_id: int = None) -> List[AsyncRaster]:
        """
        [async] Get the rasters of the mosaic

        Args:
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[AsyncRaster]: The rasters of the mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     rasters = await mosaic.get_rasters()
        """
        params = clean_data({
            'user_id': user_id
        })
        query_string = urlencode(params)
        endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/rasters?{query_string}')
        response = await self.api.get(endpoint)
        return [AsyncRaster(self.api, raster_data['uuid'], raster_data) for raster_data in response]
    

    async def add_rasters(self, rasters: List['AsyncRaster']) -> None:
        """
        [async] Add a raster to the mosaic.

        Args:
            rasters (List[Raster]): list of raster objects to add

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     rasters = await client.get_rasters()
            >>>     await mosaic.add_raster(rasters=rasters)
        """
        data = clean_data({
            'raster_ids': [raster.id for raster in rasters]
        })
        endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/rasters/')
        await self.api.post(endpoint, data, is_json=False)
    

    async def remove_rasters(self, rasters: List['AsyncRaster']) -> None:
        """
        [async] Remove a raster from the mosaic.

        Args:
            rasters (List[AsyncRaster]): list of raster objects to remove

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     rasters = await client.get_raster()
            >>>     await mosaic.remove_rasters(rasters=rasters)
        """
        param = clean_data({
            'raster_ids': [raster.id for raster in rasters]
        })
        query_string = urlencode(param)
        endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/rasters/?{query_string}')
        await self.api.delete(endpoint, is_json=False)


    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the mosaic with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to share the mosaic with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await mosaic.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the mosaic with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to unshare the mosaic with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await mosaic.unshare(users=users)
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
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.get_shared_users(search='John', skip=0, limit=10)
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
                   extent: List[int] = None, 
                   workers: int = 1) -> List['AsyncTask']:
        """
        [async] Seed the cache of the mosaic.

        Args:
            from_zoom (int, optional): The from zoom of the mosaic.
            to_zoom (int, optional): The to zoom of the mosaic.
            extent (list[int], optional): The extent of the mosaic.
            workers (int, optional): The number of workers to use. default is 1.

        Returns:
            List[AsyncTask]: The task of the seed cache.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await mosaic.seed_cache(from_zoom=0, to_zoom=22, extent=[0, 0, 100, 100], workers=1)
        """
        data = {
            'from_zoom': from_zoom,
            'to_zoom': to_zoom,
            'extent': extent,
            'workers': workers
        }
        return await super()._seed_cache(endpoint=self.endpoint, data=data)


    async def clear_cache(self) -> None:
        """
        [async] Clear the cache of the mosaic.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.clear_cache()
        """
        return await super().clear_cache()


    @property
    async def cache_size(self) -> int:
        """
        [async] Get the size of the cache of the mosaic.

        Returns:
            int: The size of the cache of the mosaic.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await mosaic.cache_size
        """
        return await super().cache_size


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Mosaic':
        """
        Switch to sync version of the mosaic instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Mosiac: the sync instance of the mosaic.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.mosaic import AsyncMosaic
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     mosaic = await AsyncMosaic.get_mosaic(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_mosaic = mosaic.to_sync(client)
        """
        from ..mosaic import Mosaic

        return Mosaic(api=sync_client, uuid=self.uuid, data=self.data)