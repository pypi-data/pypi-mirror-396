import os
import mimetypes
import requests
import sys
from urllib.parse import urljoin, urlencode
from typing import Optional, Dict, List, Optional, Union, TYPE_CHECKING

from .base import AsyncBase
from .task import AsyncTask
from ..utils import clean_data, join_url_params

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from ..api import GeoboxClient
    from ..raster import Raster


class AsyncRaster(AsyncBase):

    BASE_ENDPOINT: str = 'rasters/'

    def __init__(self,
        api: 'AsyncGeoboxClient',
        uuid: str,
        data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Raster object.

        Args:
            api (AsyncGeoboxClient): The API instance.
            uuid (str): The UUID of the raster.
            data (Dict, optional): The raster data.
        """ 
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    async def get_rasters(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncRaster'], int]:
        """
        [async] Get all rasters.

        Args:
            api (AsyncGeoboxClient): The API instance.

        Keyword Args:
            terrain (bool): whether to get terrain rasters.
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.        
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): whether to return the total count of rasters. default is False.
            skip (int): number of rasters to skip. minimum is 0.
            limit (int): number of rasters to return. minimum is 1.
            user_id (int): user id to show the rasters of the user. privileges required.
            shared (bool): whether to return shared rasters. default is False.

        Returns:
            List[AsyncRaster] | int: A list of Raster objects or the total count of rasters.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     rasters = await AsyncRaster.get_rasters(client, terrain=True, q="name LIKE '%GIS%'")
            or  
            >>>     rasters = await client.get_rasters(terrain=True, q="name LIKE '%GIS%'")
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
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncRaster(api, item['uuid'], item))
    


    @classmethod
    async def get_rasters_by_ids(cls, api: 'AsyncGeoboxClient', ids: List[str], user_id: int = None) -> List['AsyncRaster']:
        """
        [async] Get rasters by their IDs.

        Args:
            api (AsyncGeoboxClient): The API instance.
            ids (List[str]): The IDs of the rasters.
            user_id (int, optional): specific user. privileges required.

        Returns:
            List['AsyncRaster']: A list of Raster objects.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     rasters = await AsyncRaster.get_rasters_by_ids(client, ids=['123', '456'])
            or  
            >>>     rasters = await client.get_rasters_by_ids(ids=['123', '456'])
        """ 
        params = {
            'ids': ids,
            'user_id': user_id,
        }
        endpoint = urljoin(cls.BASE_ENDPOINT, 'get-rasters/')

        return await super()._get_list_by_ids(api, endpoint, params, factory_func=lambda api, item: AsyncRaster(api, item['uuid'], item))


    @classmethod
    async def get_raster(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncRaster':
        """
        [async] Get a raster by its UUID.

        Args:
            api (AsyncGeoboxClient): The API instance.
            uuid (str): The UUID of the raster.
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncRaster: A Raster object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncRaster(api, item['uuid'], item))


    @classmethod
    async def get_raster_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncRaster', None]:
        """
        [async] Get a raster by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the raster to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncRaster | None: returns the raster if a raster matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster_by_name(client, name='test')
            or  
            >>>     raster = await client.get_raster_by_name(name='test')
        """
        rasters = await cls.get_rasters(api, q=f"name = '{name}'", user_id=user_id)
        if rasters and rasters[0].name == name:
            return rasters[0]
        else:
            return None
    
    
    async def update(self, **kwargs) -> None:
        """
        [async] Update the raster.

        Keyword Args:
            name (str): The name of the raster.
            display_name (str): The display name of the raster.
            description (str): The description of the raster.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.update(name="new_name")
        """ 
        params = {
            'name': kwargs.get('name'),
            'display_name': kwargs.get('display_name'),
            'description': kwargs.get('description')
        }
        return await super()._update(self.endpoint, params)
    

    async def delete(self) -> None:
        """
        [async] Delete the raster.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.delete()
        """
        await super()._delete(self.endpoint)
    

    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail of the raster.

        Returns:
            str: The url of the thumbnail.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     raster.thumbnail
        """
        return super()._thumbnail(format='')
    
    
    @property
    async def info(self) -> Dict:
        """
        [async] Get the info of the raster.

        Returns:
            Dict: The info of the raster.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.info
        """
        endpoint = urljoin(self.endpoint, 'info/')
        return await self.api.get(endpoint)
    

    async def get_statistics(self, indexes: str = None) -> Dict:
        """
        [async] Get the statistics of the raster.

        Args:
            indexes (str): list of comma separated band indexes. e.g. 1, 2, 3

        Returns:
            Dict: The statistics of the raster.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.get_statistics(indexes='1, 2, 3')
        """
        params = clean_data({
            'indexes': indexes,
        })
        query_string = urlencode(params)
        endpoint = urljoin(self.endpoint, f'statistics/?{query_string}')
        return await self.api.get(endpoint)
    

    async def get_point(self, lat: float, lng: float) -> Dict:
        """
        [async] Get the point of the raster.

        Args:
            lat (float): The latitude of the point. minimum is -90, maximum is 90.
            lng (float): The longitude of the point. minimum is -180, maximum is 180.

        Returns:
            Dict: The point of the raster.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.get_point(lat=60, lng=50)
        """
        if lat < -90 or lat > 90:
            raise ValueError("lat must be between -90 and 90")
        if lng < -180 or lng > 180:
            raise ValueError("lng must be between -180 and 180")
        
        params = clean_data({
            'lat': lat,
            'lng': lng,
        })
        query_string = urlencode(params)
        endpoint = urljoin(self.endpoint, f'point?{query_string}')
        return await self.api.get(endpoint)
    

    def _get_save_path(self, save_path: str = None) -> str:
        """
        Get the path where the file should be saved.

        Args:
            save_path (str, optional): The path to save the file.

        Returns:
            str: The path where the file is saved.
        
        Raises:
            ValueError: If save_path does not end with a '/'.
        """
        # If save_path is provided, check if it ends with a '/'
        if save_path and save_path.endswith('/'):
            return f'{save_path}'
        
        if save_path and not save_path.endswith('/'):
            raise ValueError("save_path must end with a '/'")
        
        return os.getcwd()
    
    
    def _get_file_name(self, response: requests.Response) -> str:
        """
        Get the file name from the response.

        Args:
            response (requests.Response): The response of the request.

        Returns:
            str: The file name 
        """
        if 'Content-Disposition' in response.headers and 'filename=' in response.headers['Content-Disposition']:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1].strip().strip('"')

        else:
            content_type = response.headers.get("Content-Type", "")
            file_name = f'{self.name}{mimetypes.guess_extension(content_type.split(";")[0])}'

        return file_name


    def _create_progress_bar(self) -> 'tqdm':
        """Creates a progress bar for the task."""
        try:
            from tqdm.auto import tqdm
        except ImportError:
            from .api import logger
            logger.warning("[tqdm] extra is required to show the progress bar. install with: pip insatll geobox[tqdm]")
            return None

        return tqdm(unit="B", 
                        total=int(self.size), 
                        file=sys.stdout,
                        dynamic_ncols=True,
                        desc="Downloading",
                        unit_scale=True,
                        unit_divisor=1024, 
                        ascii=True
                )


    async def download(self, save_path: str = None, progress_bar: bool = True) -> str:
        """
        [async] Download the raster.

        Args:
            save_path (str, optional): Path where the file should be saved. 
                                    If not provided, it saves to the current working directory
                                    using the original filename and appropriate extension.
            progress_bar (bool, optional): Whether to show a progress bar. default: True
        
        Returns:
            str: The path to save the raster.

        Raises:
            ValueError: If file_uuid is not set
            OSError: If there are issues with file operations        

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.download(save_path="path/to/save/")
        """
        if not self.uuid:
            raise ValueError("Raster UUID is required to download the raster file")
        
        save_path = self._get_save_path(save_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        endpoint = urljoin(self.api.base_url, f"{self.endpoint}download/")

        async with self.api.session.session.get(endpoint) as response:
            file_name = self._get_file_name(response)
            full_path = f"{save_path}/{file_name}"
            with open(full_path, 'wb') as f:
                pbar = self._create_progress_bar() if progress_bar else None
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                        pbar.refresh()
                if pbar:
                    pbar.close()

        return os.path.abspath(full_path)


    async def get_content_file(self, save_path: str = None, progress_bar: bool = True) -> str: 
        """
        [async] Get Raster Content URL

        Args:
            save_path (str, optional): Path where the file should be saved. 
                                    If not provided, it saves to the current working directory
                                    using the original filename and appropriate extension.
            progress_bar (bool, optional): Whether to show a progress bar. default: True
        
        Returns:
            str: The path to save the raster.

        Raises:
            ValueError: If uuid is not set
            OSError: If there are issues with file operations   

        Examples:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     raster_tiff = await raste.get_content_file()
        """
        if not self.uuid:
            raise ValueError("Raster UUID is required to download the raster content")
        
        save_path = self._get_save_path(save_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        endpoint = urljoin(self.api.base_url, f"{self.endpoint}content/")
        
        async with self.api.session.session.get(endpoint) as response:
            file_name = self._get_file_name(response)
            full_path = f"{save_path}/{file_name}"
            with open(full_path, 'wb') as f:
                pbar = self._create_progress_bar() if progress_bar else None
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                        pbar.refresh()
                if pbar:
                    pbar.close()

        return os.path.abspath(full_path)


    def get_render_png_url(self, x: int, y: int, z: int, **kwargs) -> str:
        """
        Get the PNG URL of the raster.

        Args:
            x (int): The x coordinate of the tile.
            y (int): The y coordinate of the tile.
            z (int): The zoom level of the tile.

        Keyword Args:
            indexes (str, optional): list of comma separated band indexes to be rendered. e.g. 1, 2, 3
            nodata (int, optional)
            expression (str, optional): band math expression. e.g. b1*b2+b3
            rescale (List, optional): comma (',') separated Min,Max range. Can set multiple time for multiple bands.
            color_formula (str, optional): Color formula. e.g. gamma R 0.5
            colormap_name (str, optional)
            colormap (str, optional): JSON encoded custom Colormap. e.g. {"0": "#ff0000", "1": "#00ff00"} or [[[0, 100], "#ff0000"], [[100, 200], "#00ff00"]]

        Returns:
            str: The PNG Render URL of the raster.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     raster.get_tile_render_url(x=10, y=20, z=1)
        """
        params = clean_data({
            'indexes': kwargs.get('indexes'),
            'nodata': kwargs.get('nodata'),
            'expression': kwargs.get('expression'),
            'rescale': kwargs.get('rescale'),
            'color_formula': kwargs.get('color_formula'),
            'colormap_name': kwargs.get('colormap_name'),
            'colormap': kwargs.get('colormap')
        })
        query_string = urlencode(params)
        endpoint = f'{self.api.base_url}{self.endpoint}render/{z}/{x}/{y}.png'
        if query_string:
            endpoint = f'{endpoint}?{query_string}'

        if not self.api.access_token and self.api.apikey:
            endpoint = join_url_params(endpoint, {"apikey": self.api.apikey})
            
        return endpoint
    

    def get_tile_pbf_url(self, x: int = '{x}', y: int = '{y}', z: int = '{z}', indexes: str = None) -> str:
        """
        Get the URL of the tile.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optional): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.
            indexes (str, optional): list of comma separated band indexes to be rendered. e.g. 1, 2, 3

        Returns:
            str: The URL of the tile.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     raster.get_tile_pbf_url(x=10, y=20, z=1)
        """
        params = clean_data({
            'indexes': indexes
        })
        query_string = urlencode(params)
        endpoint = urljoin(self.api.base_url, f'{self.endpoint}tiles/{z}/{x}/{y}.pbf')
        endpoint = urljoin(endpoint, f'?{query_string}')

        if not self.api.access_token and self.api.apikey:
            endpoint = join_url_params(endpoint, {"apikey": self.api.apikey})

        return endpoint
    

    def get_tile_png_url(self, x: int = 'x', y: int = 'y', z: int = 'z') -> str:
        """
        Get the URL of the tile.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optional): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.

        Returns:
            str: The URL of the tile.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     raster.get_tile_png_url(x=10, y=20, z=1)
        """
        endpoint = f'{self.api.base_url}{self.endpoint}tiles/{z}/{x}/{y}.png'
            
        if not self.api.access_token and self.api.apikey:
            endpoint = f'{endpoint}?apikey={self.api.apikey}'

        return endpoint


    async def get_tile_json(self) -> Dict:
        """
        [async] Get the tile JSON of the raster.

        Returns:
            Dict: The tile JSON of the raster.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.get_tile_json()
        """
        endpoint = urljoin(self.endpoint, 'tilejson.json')
        return await self.api.get(endpoint)


    def wmts(self, scale: int = None) -> str:
        """
        Get the WMTS URL

        Args:
            scale (int, optional): The scale of the raster. values are: 1, 2

        Returns:
            str: the raster WMTS URL

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     raster.wmts(scale=1)
        """ 
        endpoint = urljoin(self.api.base_url, f'{self.endpoint}wmts/')
        if scale:
            endpoint = f"{endpoint}?scale={scale}"

        if not self.api.access_token and self.api.apikey:
            endpoint = join_url_params(endpoint, {"apikey": self.api.apikey})

        return endpoint


    @property
    async def settings(self) -> Dict:
        """
        [async] Get the settings of the raster.

        Returns:
            Dict: The settings of the raster.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.settings
        """
        return await super()._get_settings(self.endpoint)
    

    async def update_settings(self, settings: Dict) -> Dict:
        """
        [async] Update the settings

        settings (Dict): settings dictionary

        Returns:
            Dict: updated settings

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster1 = client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     raster2 = client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     raster1.update_settings(raster2.settings)
        """
        return await super()._set_settings(self.endpoint, settings)  


    async def set_settings(self, **kwargs) -> None:
        """
        [async] Set the settings of the raster.

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


        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.set_settings(nodata=0, 
            ...                             indexes=[1], 
            ...                             rescale=[[0, 10000]], 
            ...                             colormap_name='gist_rainbow', 
            ...                             color_formula='Gamma R 0.5', 
            ...                             expression='b1 * 2', 
            ...                             exaggeraion=10, 
            ...                             min_zoom=0, 
            ...                             max_zoom=22, 
            ...                             use_cache=True, 
            ...                             cache_until_zoom=17)
        """
        visual_settings = {
            'nodata', 'indexes', 'rescale', 'colormap_name', 
            'color_formula', 'expression', 'exaggeraion'
        }
        tile_settings = {
            'min_zoom', 'max_zoom', 'use_cache', 'cache_until_zoom'
        }

        settings = await self.settings

        for key, value in kwargs.items():
            if key in visual_settings:
                settings['visual_settings'][key] = value
            elif key in tile_settings:
                settings['tile_settings'][key] = value


        return await super()._set_settings(self.endpoint, settings)


    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the raster with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to share the raster with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search="John")
            >>>     await raster.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the raster with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to unshare the raster with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search="John")
            >>>     await raster.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the raster is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[AsyncUser]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    async def seed_cache(self, from_zoom: int = None, to_zoom: int = None, extent: List[int] = None, workers: int = 1) -> List['AsyncTask']:
        """
        [async] Seed the cache of the raster.

        Args:
            from_zoom (int, optional): The from zoom of the raster.
            to_zoom (int, optional): The to zoom of the raster.
            extent (List[int], optional): The extent of the raster.
            workers (int, optional): The number of workers to use. default is 1.

        Returns:
            AsyncTask: The task of the seed cache.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await raster.seed_cache(from_zoom=0, to_zoom=22, extent=[0, 0, 100, 100], workers=1)
        """
        data = {
            'from_zoom': from_zoom,
            'to_zoom': to_zoom,
            'extent': extent,
            'workers': workers
        }
        return await super()._seed_cache(self.endpoint, data)


    async def clear_cache(self) -> None:
        """
        [async] Clear the cache of the raster.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.clear_cache()
        """
        await super()._clear_cache(self.endpoint)
        

    @property
    async def cache_size(self) -> int:
        """
        [async] Get the size of the cache of the raster.

        Returns:
            int: The size of the cache of the raster.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await AsyncRaster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await raster.cache_size
        """
        return await super()._cache_size(self.endpoint)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Raster':
        """
        Switch to sync version of the raster instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Raster: the sync instance of the raster.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster import AsyncRaster
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     raster = await AsyncRaster.get_raster(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_raster = raster.to_sync(client)
        """
        from ..raster import Raster

        return Raster(api=sync_client, uuid=self.uuid, data=self.data)


    async def profile(self,
        polyline: List,
        number_of_samples: int = 100,
        output_epsg: Optional[int] = None,
        include_distance: bool = True,
        treat_nodata_as_null: bool = True) -> Dict:
        """
        [async] Create a profile form a raster along a path

        Args:
            polyline (List): Path coordinates as [x, y] pairs. Use raster CRS unless `output_epsg` is provided.
            number_of_samples (int, optional): Number of samples along the path. default: 100.
            output_epsg (int, optional): EPSG code for output coordinates. If None, use raster CRS.
            include_distance (bool, optional): Include cumulative distance for each sample. default: True.
            treat_nodata_as_null (bool, optional): Treat NoData pixels as null values. default: True.

        Returns:
            Dict: the profile result as geojson

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await raster.profile(polyline=[[0, 0], [10, 10]], number_of_samples=200)
        """
        endpoint = f"{self.endpoint}profile/"

        data = clean_data({
            'polyline': polyline,
            'number_of_samples': number_of_samples,
            'output_epsg': output_epsg,
            'include_distance': include_distance,
            'treat_nodata_as_null': treat_nodata_as_null
        })

        response = await self.api.post(endpoint=endpoint, payload=data)
        return response
