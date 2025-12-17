from urllib.parse import urljoin
from typing import Optional, Dict, List, Union, TYPE_CHECKING
import os
import mimetypes
from geobox.exception import ValidationError
import aiohttp
import sys

from .base import AsyncBase
from .task import AsyncTask
from .feature import AsyncFeature
from ..enums import FileFormat, PublishFileType, InputGeomType, FileType
from ..utils import clean_data, get_save_path, get_unique_filename
from ..exception import ApiRequestError

if TYPE_CHECKING:
    from . import AsyncGeoboxClient 
    from .user import AsyncUser
    from ..api import GeoboxClient
    from ..file import File


class AsyncFile(AsyncBase):

    BASE_ENDPOINT: str = 'files/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str, 
        data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the File object.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance.
            uuid (str): The UUID of the file.
            data (Dict, optional): The data of the file.
        """
        super().__init__(api, uuid=uuid, data=data)


    def __repr__(self) -> str:
        """
        Return a string representation of the File object.

        Returns:
            str: A string representation of the File object.
        """
        return f"AsyncFile(uuid={self.uuid}, file_name={self.name}, file_type={self.file_type.value})"


    @property
    def layers(self) -> List[Dict]:
        """
        Get the layers of the file.

        Returns:
            List[Dict]: The layers of the file.
        
        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file.layers
        """
        return self.data.get('layers', {}).get('layers', [])


    @property
    def file_type(self) -> 'FileType':
        """
        Get the file type

        Returns:
            FileType: the file type enumeration

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     file.file_type
        """
        return FileType(self.data.get('file_type'))


    @classmethod
    async def upload_file(cls, api: 'AsyncGeoboxClient', path: str, user_id: int = None, scan_archive: bool = True) -> 'AsyncFile':
        """
        [async] Upload a file to the GeoBox API.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance.
            path (str): The path to the file to upload.
            user_id (int, optional): specific user. privileges required.
            scan_archive (bool, optional): Whether to scan the archive for layers. default: True

        Returns:
            AsyncFile: The uploaded file instance.

        Raises:
            ValueError: If the file type is invalid.
            FileNotFoundError: If the file does not exist.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await AsyncFile.upload_file(client, path='path/to/file.shp')
            or  
            >>>     file = await client.upload_file(path='path/to/file.shp')
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        FileFormat(os.path.splitext(path)[1])

        endpoint = cls.BASE_ENDPOINT


        with open(path, 'rb') as f:
            f = open(path, "rb")
            files = {'file': f}
            file_data = await api.post(endpoint, files=files, is_json=False)
        return cls(api, file_data['uuid'], file_data)
        

    @classmethod
    async def get_files(cls, api:'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncFile'], int]:
        """
        [async] Retrieves a list of files.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D.NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if true, the total number of results will be returned. default is False.
            skip (int): number of results to skip. default is 0.
            limit (int): number of results to return. default is 10.
            user_id (int): filter by user id.
            shared (bool): Whether to return shared files. default is False.
            
        Returns:
            List[AsyncFile] | int: A list of File objects or the total number of results.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     files = await AsyncFile.get_files(client, search_fields='name', search='GIS', order_by='name', skip=10, limit=10)
            or  
            >>>     files = await client.get_files(search_fields='name', search='GIS', order_by='name', skip=10, limit=10)
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
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: cls(api, item['uuid'], item))


    @classmethod
    async def get_file(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncFile':
        """
        [async] Retrieves a file by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance.
            uuid (str): The UUID of the file.
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncFile: The retrieved file instance.

        Raises:
            NotFoundError: If the file with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await AsyncFile.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     file = await client.get_file(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, f'{uuid}/info', params, factory_func=lambda api, item: AsyncFile(api, item['uuid'], item))


    @classmethod
    async def get_files_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> List['AsyncFile']:
        """
        [async] Get files by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the file to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[AsyncFile]: returns files that matches the given name

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     files = await AsyncFile.get_files_by_name(client, name='test')
            or  
            >>>     files = await client.get_files_by_name(name='test')
        """
        return await cls.get_files(api, q=f"name = '{name}'", user_id=user_id)


    def _get_file_name(self, response: aiohttp.ClientResponse) -> str:
        """
        Get the file name from the response.

        Args:
            response (aiohttp.ClientResponse): The response of the request.

        Returns:
            str: The file name 
        """
        if 'Content-Disposition' in response.headers and 'filename=' in response.headers['Content-Disposition']:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1].strip().strip('"')
        else:
            content_type = response.headers.get("Content-Type", "")
            file_name = f'{self.name}.{mimetypes.guess_extension(content_type.split(";")[0])}'

        return file_name


    def _create_progress_bar(self) -> 'tqdm':
        """Creates a progress bar for the task."""
        try:
            from tqdm.auto import tqdm
        except ImportError:
            from .api import logger
            logger.warning("[tqdm] extra is required to show the progress bar. install with: pip install geobox[tqdm]")
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


    async def download(self, save_path: str = None, progress_bar: bool = True, file_name: str = None, overwrite: bool = False) -> str:
        """
        [async] Download a file and save it to the specified path.
        
        Args:
            save_path (str, optional): Path where the file should be saved. 
                                    If not provided, it saves to the current working directory
                                    using the original filename and appropriate extension.
            progress_bar (bool, optional): Whether to show a progress bar. default: True
            file_name (str, optional): the downloaded file name.
            overwrite (bool, optional): whether to overwrite the downloaded file if it exists on the save path. default is False.
        
        Returns:
            str: Path where the file was saved
            
        Raises:
            ValueError: If uuid is not set
            OSError: If there are issues with file operations

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await AsyncFile.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await file.download(save_path='path/to/save/')
        """
        if not self.uuid:
            raise ValueError("File UUID is required to download the file")
        
        save_path = get_save_path(save_path)
        os.makedirs(save_path, exist_ok=True)

        # Use the aiohttp session directly for streaming
        endpoint = urljoin(self.api.base_url, f"{self.endpoint}download/")
        
        async with self.api.session.session.get(endpoint) as response:
            if response.status != 200:
                raise ApiRequestError(f"Failed to download file: {response.status}")
            
            file_name = self._get_file_name(response)
            full_path = os.path.join(save_path, file_name)
            if os.path.exists(full_path) and not overwrite:
                full_path = get_unique_filename(save_path, file_name)
            with open(full_path, 'wb') as f:
                pbar = self._create_progress_bar() if progress_bar else None
                
                # Use aiohttp's streaming method
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                        pbar.refresh()
                
                if pbar:
                    pbar.close()

        return os.path.abspath(full_path)


    async def delete(self) -> None:
        """
        [async] Deletes the file.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await AsyncFile.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await file.delete()
        """
        return await super()._delete(self.endpoint)


    async def publish(self, 
        name: str, 
        publish_as: 'PublishFileType' = None, 
        input_geom_type: 'InputGeomType' = None, 
        input_layer: str = None, 
        input_dataset: str = None, 
        user_id: int = None, 
        input_srid: int = AsyncFeature.BASE_SRID, 
        file_encoding: str = "UTF-8", 
        replace_domain_codes_by_values: bool = False, 
        report_errors: bool = True, 
        as_terrain: bool = False) -> 'AsyncTask':
        """
        [async] Publishes a file as a layer.

        Args:
            name (str): The name of the layer.
            publish_as (PublishFileType, optional): The type of layer to publish as.
            input_geom_type (InputGeomType, optional): The geometry type of the layer.
            input_layer (str, optional): The name of the input layer.
            input_dataset (str, optional): The name of the input dataset.
            user_id (int, optional): Specific user. privileges required.
            input_srid (int, optional): The SRID of the layer. default is: 3857
            file_encoding (str, optional): The encoding of the file. default is "utf-8".
            replace_domain_codes_by_values (bool, optional): Whether to replace domain codes by values. default is False.
            report_errors (bool, optional): Whether to report errors. default is True.
            as_terrain (bool, optional): Whether to publish as terrain. default is False.

        Returns:
            Task: The task object.

        Raises:
            ValueError: If the publish_as is not a valid PublishFileType.
            ValidationError: if the zipped file doesn't have any layers to publish.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await AsyncFile.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await file.publish(publish_as=PublishFileType.VECTOR, 
            ...                         layer_name='my_layer', 
            ...                         input_geom_type=InputGeomType.POINT, 
            ...                         input_layer='layer1', 
            ...                         input_dataset='dataset1', 
            ...                         input_srid=4326, 
            ...                         file_encoding='UTF-8')
        """
        if not publish_as:
            # checks the file format or file first layer format to dynamically set the publish_as
            if self.file_type.value in ['GeoJSON', 'GPKG', 'DXF', 'GPX', 'Shapefile', 'KML', 'CSV', 'FileGDB'] or \
                (self.file_type.value in ['Complex'] and self.layers and \
                    FileType(self.layers[0]['format']).value in ['GeoJSON', 'GPKG', 'DXF', 'GPX', 'Shapefile', 'KML', 'CSV', 'FileGDB']):
                publish_as = PublishFileType.VECTOR

            elif self.file_type.value in ['GeoTIFF'] or \
                    (self.file_type.value in ['Complex'] and self.layers and \
                        FileType(self.layers[0]['format']).value in ['GeoTIFF']):
                publish_as = PublishFileType.RASTER

            elif self.file_type.value in ['GLB'] or \
                    (self.file_type.value in ['Complex'] and self.layers and \
                        FileType(self.layers[0]['format']).value in ['GLB']):
                publish_as = PublishFileType.MODEL3D

            elif self.file_type.value in ['ThreedTiles']:
                publish_as = PublishFileType.Tiles3D

            else:
                raise ValidationError('Unknown format')

        data = clean_data({
            "publish_as": publish_as.value if isinstance(publish_as, PublishFileType) else publish_as,
            "layer_name": name,
            "input_layer": self.layers[0]['layer'] if not input_layer and self.layers else input_layer,
            "input_geom_type": input_geom_type.value if isinstance(input_geom_type, InputGeomType) else input_geom_type,
            "replace_domain_codes_by_values": replace_domain_codes_by_values,
            "input_dataset": self.layers[0]['dataset'] if not input_layer and self.layers else input_dataset,
            "user_id": user_id,
            "input_srid": input_srid,
            "file_encoding": file_encoding,
            "report_errors": report_errors,
            "as_terrain": as_terrain
        })
        endpoint = urljoin(self.endpoint, 'publish/')
        response = await self.api.post(endpoint, data, is_json=False)
        task = await AsyncTask.get_task(self.api, response.get('task_id'))
        return task


    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the file with specified users.

        Args:
            users (List[User]): The list of users objects to share the file with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await AsyncFile.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await file.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the file with specified users.

        Args:
            users (List[AsyncUser]): The list of users objects to unshare the file with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await AsyncFile.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await users = client.search_users(search='John')
            >>>     await file.unshare(users=users)
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
            >>> from geobox.aio.file import AsyncFile
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await AsyncFile.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await file.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'File':
        """
        Switch to sync version of the file instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            File: the async instance of the file.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.file import AsyncFile
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     file = await AsyncFile.get_file(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_file = file.to_sync(client)
        """
        from ..file import File

        return File(api=sync_client, uuid=self.uuid, data=self.data)