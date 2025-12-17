from typing import List, Dict, Optional, TYPE_CHECKING
from urllib.parse import urljoin, urlencode

from .base import AsyncBase
from ..exception import NotFoundError
from ..utils import clean_data

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from ..api import GeoboxClient
    from ..basemap import Basemap


class AsyncBasemap(AsyncBase):

    BASE_ENDPOINT = 'basemaps/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        data: Optional[Dict] = {}):
        """
        Initialize a basemap instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            data (Dict): The data of the basemap.
        """
        super().__init__(api, data=data)
        self.endpoint = f"{self.BASE_ENDPOINT}{self.data.get('name')}/"


    @classmethod
    async def get_basemaps(cls, api: 'AsyncGeoboxClient') -> List['AsyncBasemap']:
        """
        [async] Get a list of basemaps

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

        Returns:
            List[AsyncBaseMap]: list of basemaps.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.basemap import AsyncBasemap
            >>> async with AsyncGeoboxClient() as client:
            >>>     basemaps = await AsyncBasemap.get_basemaps(client)
            or  
            >>>     basemaps = await client.get_basemaps()
        """
        response = await api.get(cls.BASE_ENDPOINT)
        if not response:
            return []

        items = []
        for item in response:
            response[item]['name'] = item
            items.append(response[item])

        return [cls(api, item) for item in items]


    @classmethod
    async def get_basemap(cls, api: 'AsyncGeoboxClient', name: str) -> 'AsyncBasemap':
        """
        [async] Get a basemap object

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name: the basemap name

        Returns:
            AsyncBasemap: the basemap object

        Raises:
            NotFoundError: if the base,ap with the specified name not found

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.basemap import Basemap
            >>> async with AsyncGeoboxClient() as client:
            >>>     basemap = await Basemap.get_basemap(client, name='test')
            or  
            >>>     basemap = await client.get_basemap(name='test')
        """
        response = await cls.get_basemaps(api)
        basemap = [basemap for basemap in response if basemap.name == name]
        if not basemap:
            raise NotFoundError(f'Basemap with name "{name}" not found.')

        return basemap[0]


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail url of the basemap

        Returns:
            str: the thumbnail url
        """
        return super()._thumbnail()
    

    @property
    def wmts(self) -> str:
        """
        Get the wmts url of the basemap

        Returns:
            str: the wmts url
        """
        endpoint = urljoin(self.api.base_url, f'{self.endpoint}wmts/')

        if not self.api.access_token and self.api.apikey:
            endpoint = f"{endpoint}?apikey={self.api.apikey}"
            
        return endpoint
    

    @property
    async def server_url(self) -> str:
        """
        [async] Get the server url of the basemap

        Returns:
            str: the server url
        """
        endpoint = f'{self.api.base_url}{self.BASE_ENDPOINT}server_url'
        return await self.api.get(endpoint)
    

    @property
    async def proxy_url(self) -> str:
        """
        [async] Get the proxy url of the basemap

        Returns:
            str: the proxy url
        """
        endpoint = f'{self.api.base_url}{self.BASE_ENDPOINT}proxy_url'
        return await self.api.get(endpoint)
    

    @classmethod
    async def proxy_basemap(cls, api: 'response', url: str) -> None:
        """
        [async] Proxy the basemap

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            url (str): the proxy server url.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.basemap import Basemap
            >>> async with AsyncGeoboxClient() as client:
            >>>     await Basemap.proxy_basemap(client, url='proxy_server_url')
            or  
            >>>     await client.proxy_basemap(url='proxy_server_url')
        """
        param = clean_data({
            'url': url
        })
        query_string = urlencode(param)
        endpoint = urljoin(cls.BASE_ENDPOINT, f"?{query_string}")
        await api.get(endpoint)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Basemap':
        """
        Switch to sync version of the basemap instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Basemap: the sync instance of the basemap.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.basemap import AsyncBasemap
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     basemap = await AsyncBasemap.get_basemap(async_client, name='test')
            or  
            >>>     basemap = await async_client.get_basemap(name='test')
            >>>     sync_basemap = basemap.to_sync(client)
        """
        from ..basemap import Basemap

        return Basemap(api=sync_client, data=self.data)