import aiohttp
import asyncio
import logging
import os
from urllib.parse import urljoin
from typing import Dict, List, Union, Any
from datetime import datetime

from .vectorlayer import AsyncVectorLayer, LayerType
from .feature import AsyncFeature
from .file import AsyncFile
from .task import AsyncTask
from .view import AsyncVectorLayerView
from .tileset import AsyncTileset
from .raster import AsyncRaster
from .mosaic import AsyncMosaic
from .model3d import AsyncModel
from .map import AsyncMap
from .user import AsyncUser, UserRole, UserStatus, AsyncSession
from .query import AsyncQuery
from .workflow import AsyncWorkflow
from .layout import AsyncLayout
from .version import AsyncVectorLayerVersion
from .tile3d import AsyncTile3d
from .settings import AsyncSystemSettings
from .scene import AsyncScene
from .route import AsyncRouting
from .plan import AsyncPlan
from .dashboard import AsyncDashboard
from .basemap import AsyncBasemap
from .attachment import AsyncAttachment
from .apikey import AsyncApiKey
from .log import AsyncLog
from .usage import AsyncUsage, UsageScale, UsageParam
from ..exception import AuthenticationError, ApiRequestError, NotFoundError, ValidationError, ServerError, AuthorizationError
from ..utils import join_url_params


logger = logging.getLogger(__name__)


class HttpMethods:
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    DELETE = 'DELETE'


class AsyncRequestSession:
    """An async session class that maintains headers and authentication state."""
    
    def __init__(self, access_token=None):
        """
        Initialize the session with authentication.
        
        Args:
            access_token (str, optional): Bearer token for authentication
        """
        self.access_token = access_token
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'
        self.session = None


    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()


    def update_access_token(self, access_token: str) -> None:
        """
        Update the access token of the session.

        Args:
            access_token (str): The new access token
        """
        self.access_token = access_token
        self.headers['Authorization'] = f'Bearer {self.access_token}'
        if self.session:
            self.session.headers.update(self.headers)
    

    def _manage_headers_for_request(self, files=None, is_json=True) -> str:
        """
        Manages headers for different types of requests.
        
        Args:
            files (dict, optional): Files to upload
            is_json (bool, optional): Whether payload is JSON
            
        Returns:
            str: Original content type if it was modified
        """
        original_content_type = None
        
        if files:
            # For file uploads, we need to completely avoid setting Content-Type
            # Let aiohttp handle multipart boundary automatically
            original_content_type = self.headers.get('Content-Type')
            if 'Content-Type' in self.headers:
                del self.headers['Content-Type']
        elif not is_json:
            original_content_type = self.headers.get('Content-Type')
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
        return original_content_type


class AsyncGeoboxClient:
    """
    An async class to interact with the Geobox API.
    """
    def __init__(self,
        host: str = 'https://api.geobox.ir',
        ver: str = 'v1/',
        username: str = None,
        password: str = None,
        access_token: str = None, 
        apikey: str = None):
        """
        Constructs all the necessary attributes for the Api object.
        """
        self.username = os.getenv('GEOBOX_USERNAME') if os.getenv('GEOBOX_USERNAME') else username
        self.password = os.getenv('GEOBOX_PASSWORD') if os.getenv('GEOBOX_PASSWORD') else password
        self.access_token = os.getenv('GEOBOX_ACCESS_TOKEN') if os.getenv('GEOBOX_ACCESS_TOKEN') else access_token
        self.apikey = os.getenv('GEOBOX_APIKEY') if os.getenv('GEOBOX_APIKEY') else apikey

        self.session = AsyncRequestSession(access_token=self.access_token)

        host = host.lower()
        self.base_url = urljoin(host, ver)
        

        if not self.access_token and not self.apikey:
            if self.username and self.password:
                pass
            else:
                raise ValueError("Please provide either username/password, apikey or access_token.")


    async def __aenter__(self):
        await self.session.__aenter__()
        # Get access token if needed
        try:
            if not self.access_token and not self.apikey and self.username and self.password:
                self.access_token = await self.get_access_token()
                self.session.update_access_token(self.access_token)
            return self
        except Exception:
            # If get_access_token fails, close the session before re-raising
            await self.session.__aexit__(None, None, None)
            raise


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)


    def __repr__(self) -> str:
        """
        Return a string representation of the AsyncGeoboxClient object.
        """
        if self.access_token and not self.username:
            return f"AsyncGeoboxClient(access_token={self.access_token[:20] + '...' if len(self.access_token) > 20 else self.access_token})"
        elif self.apikey:
            return f"AsyncGeoboxClient(apikey={self.apikey[:20] + '...' if len(self.apikey) > 20 else self.apikey})"
        elif self.username:
            return f"AsyncGeoboxClient(username={self.username[:20] + '...' if len(self.username) > 20 else self.username})"


    async def get_access_token(self) -> str:
        """
        Obtains an access token using the username and password.

        Returns:
            str: The access token.

        Raises:
            AuthenticationError: If there is an error obtaining the access token.
        """
        url = urljoin(self.base_url, "auth/token/")
        data = {"username": self.username, "password": self.password}
        
        try:
            async with aiohttp.ClientSession() as temp_session:
                async with temp_session.post(url, data=data) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return response_data["access_token"]
                    else:
                        raise AuthenticationError(f"Error obtaining access token: {response_data}")
        except Exception as e:
            raise AuthenticationError(f"Error obtaining access token: {e}")


    def _parse_error_message(self, response_data: dict) -> str:
        """
        Parse error message from API response.

        Args:
            response_data (dict): The API response data.

        Returns:
            str: The parsed error message.
        """
        detail = response_data.get('detail')
        
        if not detail:
            return str(response_data)
            
        if isinstance(detail, list) and len(detail) == 1:
            error = detail[0]
            error_msg = error.get('msg', '')
            loc = error.get('loc', [])
            
            if loc and len(loc) >= 2:
                return f'{error_msg}: "{loc[-1]}"'
            return error_msg
            
        if isinstance(detail, dict):
            return detail.get('msg', str(detail))
            
        return str(detail)


    def _handle_error(self, status_code: int, response_data: dict) -> None:
        """
        Handle API error response.

        Args:
            status_code (int): HTTP status code
            response_data (dict): Response data

        Raises:
            Various error exceptions based on status code
        """
        error_msg = self._parse_error_message(response_data)
        
        if status_code == 401:
            raise AuthenticationError(f'Invalid Authentication: {error_msg}')
        elif status_code == 403:
            raise AuthorizationError(f'Access forbidden: {error_msg}')
        elif status_code == 404:
            raise NotFoundError(f'Resource not found: {error_msg}')
        elif status_code == 422:
            raise ValidationError(error_msg)
        elif status_code >= 500:
            raise ServerError(error_msg)
        else:
            raise ApiRequestError(f"API request failed: {error_msg}")


    async def _make_request(self,
                method: str,
                endpoint: str,
                payload=None,
                is_json=True,
                files=None,
                stream=None) -> Any:
        """
        Makes an async HTTP request to the API.
        """
        url = urljoin(self.base_url, endpoint)
        
        if not self.access_token and self.apikey:
            url = join_url_params(url, {'apikey': self.apikey})

        try:
            if files:   
                # For file uploads, use a fresh session to avoid header conflicts
                # This is necessary because multipart uploads require specific Content-Type handling
                file_headers = {}
                if self.access_token:
                    file_headers['Authorization'] = f'Bearer {self.access_token}'
                
                form = aiohttp.FormData()
                for key, value in files.items():
                    if hasattr(value, 'read') and hasattr(value, 'name'):
                        # It's a file object, extract filename
                        filename = os.path.basename(value.name)
                        form.add_field(
                            name=key,
                            value=value,
                            filename=filename,
                            content_type="application/octet-stream"
                        )
                    else:
                        # It's just a value
                        form.add_field(
                            name=key,
                            value=value
                        )
                
                # Use a temporary ClientSession for file uploads to avoid header conflicts
                async with aiohttp.ClientSession() as temp_session:
                    async with temp_session.request(method, url, data=form, headers=file_headers) as response:
                        if stream:
                            response_data = response
                        else:
                            try:
                                response_data = await response.json()
                            except Exception:
                                response_data = None
                        status_code = response.status
                    
            elif is_json:
                # Use the existing session and header management for JSON requests
                original_content_type = self.session._manage_headers_for_request(files, is_json)
                headers = self.session.headers.copy()
                
                try:
                    async with self.session.session.request(method, url, json=payload, headers=headers) as response:
                        if stream:
                            response_data = response
                        else:
                            try:
                                response_data = await response.json()
                            except Exception:
                                response_data = None
                        status_code = response.status
                finally:
                    if original_content_type:
                        self.session.headers['Content-Type'] = original_content_type
                    
            else:
                # Use the existing session and header management for form data
                original_content_type = self.session._manage_headers_for_request(files, is_json)
                headers = self.session.headers.copy()
                
                try:
                    async with self.session.session.request(method, url, data=payload, headers=headers) as response:
                        if stream:
                            response_data = response
                        else:
                            try:
                                response_data = await response.json()
                            except Exception:
                                response_data = None
                        status_code = response.status
                finally:
                    if original_content_type:
                        self.session.headers['Content-Type'] = original_content_type
                    
        except asyncio.TimeoutError as e:
            raise ApiRequestError(f"Request timed out: {e}")
        except aiohttp.ClientError as e:
            raise ApiRequestError(f"Request failed: {e}")

        # Handle error responses
        if status_code in [401, 403, 404, 422, 500]:
            self._handle_error(status_code, response_data if isinstance(response_data, dict) else {})

        # Log success responses
        if status_code == 200:
            logger.info("Request successful: Status code 200")
        elif status_code == 201:
            logger.info("Resource created successfully: Status code 201")
        elif status_code == 202:
            logger.info("Request accepted successfully: Status code 202")
        elif status_code == 203:
            logger.info("Non-authoritative information: Status code 203")
        elif status_code == 204:
            logger.info("Deleted, operation successful: Status code 204")

        return response_data


    async def get(self, endpoint: str, stream: bool = False) -> Dict:
        """
        Sends a GET request to the API.

        Args:
            endpoint (str): The API endpoint.
            stream (bool): Whether to stream the response.

        Returns:
            Dict: The response data.
        """
        return await self._make_request(HttpMethods.GET, endpoint, stream=stream)


    async def post(self, endpoint: str, payload: Dict = None, is_json: bool = True, files=None) -> Dict:
        """
        Sends a POST request to the API.

        Args:
            endpoint (str): The API endpoint.
            payload (Dict, optional): The data to send with the request.
            is_json (bool, optional): Whether the payload is in JSON format.
            files (dict, optional): Files to upload.

        Returns:
            Dict: The response data.
        """
        return await self._make_request(HttpMethods.POST, endpoint, payload, is_json, files=files)


    async def put(self, endpoint: str, payload: Dict, is_json: bool = True) -> Dict:
        """
        Sends a PUT request to the API.

        Args:
            endpoint (str): The API endpoint.
            payload (Dict): The data to send with the request.
            is_json (bool, optional): Whether the payload is in JSON format.

        Returns:
            Dict: The response data.
        """
        return await self._make_request(HttpMethods.PUT, endpoint, payload, is_json)


    async def delete(self, endpoint: str, payload: Dict = None, is_json: bool = True) -> Dict:
        """
        Sends a DELETE request to the API.

        Args:
            endpoint (str): The API endpoint.
            payload (Dict, optional): The data to send with the request.
            is_json (bool, optional): Whether the payload is in JSON format.

        Returns:
            Dict: The response data.
        """
        return await self._make_request(HttpMethods.DELETE, endpoint, payload, is_json)


    @property
    def raster_analysis(self):
        from .raster_analysis import AsyncRasterAnalysis

        return AsyncRasterAnalysis(self)


    @property
    def vector_tool(self):
        from .vector_tool import AsyncVectorTool

        return AsyncVectorTool(self)


    async def get_vectors(self, **kwargs) -> Union[List['AsyncVectorLayer'], int]:
        """
        [async] Get a list of vector layers with optional filtering and pagination.
        
        Keyword Args:
            include_settings (bool): Whether to include layer settings. Default is False.
            temporary (bool): Whether to return temporary layers, default is False
            q (str): Query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): Search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): Comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of layers to skip. default is 0.
            limit (int): Maximum number of layers to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared layers. default is False.
                
        Returns:
            List[AsyncVectorLayer] | int: A list of VectorLayer instances or the layers count if return_count is True.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layers = await client.get_vectors(include_settings=True, 
            ...         skip=0, 
            ...         limit=100, 
            ...         return_count=False, 
            ...         search="my_layer",
            ...         search_fields="name, description",
            ...         order_by="name",
            ...         shared=True)
        """
        return await AsyncVectorLayer.get_vectors(self, **kwargs)
    

    async def get_vector(self, uuid: str, user_id: int = None) -> 'AsyncVectorLayer':
        """
        [async] Get a specific vector layer by its UUID.
        
        Args:
            uuid (str): The UUID of the layer to retrieve.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            VectorLayer: The requested layer instance.
            
        Raises:
            NotFoundError: If the layer with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncVectorLayer.get_vector(self, uuid, user_id)
    

    async def get_vectors_by_ids(self, ids: List[int], user_id: int = None, include_settings: bool = False) -> List['AsyncVectorLayer']:
        """
        [async] Get vector layers by their IDs.

        Args:
            ids (List[int]): The IDs of the layers to retrieve.
            user_id (int, optional): Specific user. privileges required.
            include_settings (bool, optional): Whether to include the layer settings. default is False.

        Returns:
            List[AsyncVectorLayer]: The list of VectorLayer instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layers = await client.get_vectors_by_ids(ids=[1, 2, 3])
        """
        return await AsyncVectorLayer.get_vectors_by_ids(self, ids, user_id, include_settings)


    async def create_vector(self, 
        name: str, 
        layer_type: 'LayerType', 
        display_name: str = None, 
        description: str = None,
        has_z: bool = False,
        temporary: bool = False,
        fields: List = None) -> 'AsyncVectorLayer':
        """
        [async] Create a new vector layer.
        
        Args:
            name (str): The name of the layer.
            layer_type (LayerType): The type of geometry to store.
            display_name (str, optional): A human-readable name for the layer. default is None.
            description (str, optional): A description of the layer. default is None.
            has_z (bool, optional): Whether the layer includes Z coordinates. default is False.
            temporary (bool, optional): Whether to create a temporary layer. temporary layers will be deleted after 24 hours. default is False.
            fields (List, optional): List of field definitions for the layer. default is None.
            
        Returns:
            AsyncVectorLayer: The newly created layer instance.
            
        Raises:
            ValidationError: If the layer data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.create_vector(name="my_layer", 
            ...         layer_type=LayerType.Point,
            ...         display_name="My Layer",
            ...         description="This is a description of my layer",
            ...         has_z=False,
            ...         fields=[{"name": "my_field", "datatype": "FieldTypeString"}])
        """
        return await AsyncVectorLayer.create_vector(self, name=name, layer_type=layer_type, display_name=display_name, description=description, has_z=has_z, temporary=temporary, fields=fields)


    async def get_vector_by_name(self, name: str, user_id: int = None) -> Union['AsyncVectorLayer', None]:
        """
        [async] Get a vector layer by name

        Args:
            name (str): the name of the vector to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncVectorLayer | None: returns the vector if a vector matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector_by_name(name='test')
        """
        return await AsyncVectorLayer.get_vector_by_name(self, name, user_id)
    

    async def get_files(self, **kwargs) -> Union[List['AsyncFile'], int]:
        """
        [async] Retrieves a list of files.

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
            >>> async with AsyncGeoboxClient() as client:
            >>>     files = await client.get_files(search_fields='name', search='GIS', order_by='name', skip=10, limit=10)
        """
        return await AsyncFile.get_files(self, **kwargs)


    async def get_file(self, uuid: str) -> 'AsyncFile':
        """
        [async] Retrieves a file by its UUID.

        Args:
            uuid (str, optional): The UUID of the file.

        Returns:
            AsyncFile: The retrieved file instance.

        Raises:
            NotFoundError: If the file with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await client.get_file(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncFile.get_file(self, uuid=uuid)
    

    async def get_files_by_name(self, name: str, user_id: int = None) -> List['AsyncFile']:
        """
        [async] Get files by name

        Args:
            name (str): the name of the file to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[AsyncFile]: returns files that matches the given name

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     files = await client.get_files_by_name(name='test')
        """
        return await AsyncFile.get_files_by_name(self, name, user_id)


    async def upload_file(self, path: str, user_id: int = None, scan_archive: bool = True) -> 'AsyncFile':
        """
        [async] Upload a file to the GeoBox API.

        Args:
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
            >>> async with AsyncGeoboxClient() as client:
            >>>     file = await client.upload_file(path='path/to/file.shp')
        """
        return await AsyncFile.upload_file(self, path=path, user_id=user_id, scan_archive=scan_archive)


    async def get_tasks(self, **kwargs) -> Union[List['AsyncTask'], int]:
        """
        [async] Get a list of tasks

        Keyword Args:
            state (TaskStatus): Available values : TaskStatus.PENDING, TaskStatus.PROGRESS, TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.ABORTED
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): The count of the tasks. default is False.
            skip (int): The skip of the task. default is 0.
            limit (int): The limit of the task. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared tasks. default is False.

        Returns:
            List[AsyncTask] | int: The list of task objects or the count of the tasks if return_count is True.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     tasks = await client.get_tasks()
        """
        return await AsyncTask.get_tasks(self, **kwargs)


    async def get_task(self, uuid: str) -> 'AsyncTask':
        """
        [async] Gets a task.

        Args:
            uuid (str): The UUID of the task.

        Returns:
            AsyncTask: The task object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await client.get_task(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncTask.get_task(self, uuid)


    async def get_views(self, **kwargs) -> Union[List['AsyncVectorLayerView'], int]:
        """
        [async] Get vector layer views.

        Keyword Args:
            layer_id(int): The id of the layer.
            include_settings(bool): Whether to include the settings of the layer. default is False.
            q(str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search(str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields(str): Comma separated list of fields for searching.
            order_by(str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count(bool): Whether to return the count of the layer views. default is False.
            skip(int): The number of layer views to skip. minimum is 0.
            limit(int): The maximum number of layer views to return. minimum is 1. default is 10.
            user_id(int): Specific user. privileges required.
            shared(bool): Whether to return shared views. default is False.

        Returns:
            list[AsyncVectorLayerView] | int: A list of VectorLayerView instances or the layer views count if return_count is True.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     views = await client.get_views(layer_id=1,
            ...         include_settings=True,
            ...         search="test",
            ...         search_fields="name",
            ...         order_by="name A",
            ...         return_count=False,
            ...         skip=0,
            ...         limit=10,
            ...         shared=True)
        """
        return await AsyncVectorLayerView.get_views(self, **kwargs)


    async def get_views_by_ids(self, ids: List[int], user_id: int = None, include_settings: bool = False) -> List['AsyncVectorLayerView']:
        """
        [async] Get vector layer views by their IDs.

        Args:
            ids (List[int]): list of comma separated layer ids to be returned. e.g. 1, 2, 3
            user_id (int, optional): specific user. privileges required.
            include_settings (bool, optional): Whether to include the settings of the vector layer views. default is False.

        Returns:
            List[AsyncVectorLayerView]: A list of VectorLayerView instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     views = await client.get_views_by_ids(ids=[1,2,3])
        """
        return await AsyncVectorLayerView.get_views_by_ids(self, ids, user_id, include_settings)
    

    async def get_view(self, uuid: str, user_id: int = None) -> 'AsyncVectorLayerView':
        """
        [async] Get a specific vector layer view by its UUID.

        Args:
            uuid (str): The UUID of the vector layer view.
            user_id (int, optional): Specific user. privileges required.

        Returns:    
            AsyncVectorLayerView: A VectorLayerView instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await client.get_view(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncVectorLayerView.get_view(self, uuid, user_id)


    async def get_view_by_name(self, name: str, user_id: int = None) -> Union['AsyncVectorLayerView', None]:
        """
        [async] Get a view by name

        Args:
            name (str): the name of the view to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncVectorLayerView | None: returns the view if a view matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await client.get_view_by_name(name='test')
        """
        return await AsyncVectorLayerView.get_view_by_name(self, name, user_id)


    async def create_tileset(self, name: str, layers: List[Union['AsyncVectorLayer', 'AsyncVectorLayerView']], display_name: str = None, description: str = None,
                        min_zoom: int = None, max_zoom: int = None, user_id: int = None) -> 'AsyncTileset':
        """
        [async] Create a new tileset.

        Args:
            name (str): The name of the tileset.
            layers (List['VectorLayer' | 'VectorLayerView']): list of vectorlayer and view objects to add to tileset.
            display_name (str, optional): The display name of the tileset.
            description (str, optional): The description of the tileset.
            min_zoom (int, optional): The minimum zoom level of the tileset.
            max_zoom (int, optional): The maximum zoom level of the tileset.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncTileset: The created tileset instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     view = await client.get_view(uuid="12345678-1234-5678-1234-567812345678")
            >>>     tileset = await client.create_tileset(name="your_tileset_name", 
            ...        display_name="Your Tileset", 
            ...        description="Your description", 
            ...        min_zoom=0, 
            ...        max_zoom=14, 
            ...        layers=[layer, view])
        """
        return await AsyncTileset.create_tileset(api=self, 
            name=name, 
            layers=layers, 
            display_name=display_name, 
            description=description, 
            min_zoom=min_zoom, 
            max_zoom=max_zoom, 
            user_id=user_id)


    async def get_tilesets(self, **kwargs) -> Union[List['AsyncTileset'], int]:
        """
        [async] Retrieves a list of tilesets.

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
            >>> async with AsyncGeoboxClient() as client:
            >>>     tilesets = await client.get_tilesets(q="name LIKE '%your_tileset_name%'",
            ...         order_by="name A",
            ...         skip=0,
            ...         limit=10,
            ...     )
        """
        return await AsyncTileset.get_tilesets(self, **kwargs)


    async def get_tilesets_by_ids(self, ids: List[int], user_id: int = None) -> List['AsyncTileset']:
        """
        [async] Retrieves a list of tilesets by their IDs.

        Args:
            ids (List[str]): The list of tileset IDs.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            List[AsyncTileset]: A list of Tileset instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     tilesets = await client.get_tilesets_by_ids(ids=['123', '456'])
        """
        return await AsyncTileset.get_tilesets_by_ids(self, ids, user_id)


    async def get_tileset(self, uuid: str) -> 'AsyncTileset':
        """
        [async] Retrieves a tileset by its UUID.

        Args:
            uuid (str): The UUID of the tileset.

        Returns:
            AsyncTileset: The retrieved tileset instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await client.get_tileset(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncTileset.get_tileset(self, uuid)


    async def get_tileset_by_name(self, name: str, user_id: int = None) -> Union['AsyncTileset', None]:
        """
        [async] Get a tileset by name

        Args:
            name (str): the name of the tileset to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncTileset | None: returns the tileset if a tileset matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     tileset = await client.get_tileset_by_name(name='test')
        """
        return await AsyncTileset.get_tileset_by_name(self, name, user_id)
    

    async def get_rasters(self, **kwargs) -> Union[List['AsyncRaster'], int]:
        """
        [async] Get all rasters.

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
            >>> async with AsyncGeoboxClient() as client:
            >>>     rasters = await client.get_rasters(terrain=True, q="name LIKE '%GIS%'")
        """
        return await AsyncRaster.get_rasters(self, **kwargs)


    async def get_rasters_by_ids(self, ids: List[int], user_id: int = None) -> List['AsyncRaster']:
        """
        [async] Get rasters by their IDs.

        Args:
            ids (List[str]): The IDs of the rasters.
            user_id (int, optional): specific user. privileges required.

        Returns:
            List['AsyncRaster']: A list of Raster objects.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     rasters = await client.get_rasters_by_ids(ids=['123', '456'])
        """ 
        return await AsyncRaster.get_rasters_by_ids(self, ids, user_id)


    async def get_raster(self, uuid: str) -> 'AsyncRaster':
        """
        [async] Get a raster by its UUID.

        Args:
            uuid (str): The UUID of the raster.
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncRaster: A Raster object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncRaster.get_raster(self, uuid)    


    async def get_raster_by_name(self, name: str, user_id: int = None) -> Union['AsyncRaster', None]:
        """
        [async] Get a raster by name

        Args:
            name (str): the name of the raster to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncRaster | None: returns the raster if a raster matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster_by_name(name='test')
        """
        return await AsyncRaster.get_raster_by_name(self, name, user_id)


    async def get_mosaics(self, **kwargs) -> Union[List['AsyncMosaic'], int]:
        """
        [async] Get a list of mosaics.

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
            List['AsyncMosaic'] | int: A list of Mosaic instances or the number of mosaics.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaics = await client.get_mosaics(q="name LIKE '%GIS%'")
        """
        return await AsyncMosaic.get_mosaics(self, **kwargs)


    async def get_mosaics_by_ids(self, ids: List[int], user_id: int = None) -> List['AsyncMosaic']:
        """
        [async] Get mosaics by their IDs.

        Args:
            ids (List[str]): The IDs of the mosaics.
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[AsyncMosaic]: A list of Mosaic instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaics = await client.get_mosaics_by_ids(ids=['1, 2, 3'])
        """
        return await AsyncMosaic.get_mosaics_by_ids(self, ids, user_id)


    async def create_mosaic(self, 
        name:str,
        display_name: str = None,
        description: str = None,
        pixel_selection: str = None,
        min_zoom: int = None,
        user_id: int = None) -> 'AsyncMosaic':
        """
        [async] Create New Raster Mosaic

        Args:
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
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await client.create_mosaic(name='mosaic_name')
        """
        return await AsyncMosaic.create_mosaic(self, name, display_name, description, pixel_selection, min_zoom, user_id)


    async def get_mosaic(self, uuid: str, user_id: int = None) -> 'AsyncMosaic':
        """
        [async] Get a mosaic by uuid.

        Args:
            uuid (str): The UUID of the mosaic.
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncMosaic: The mosaic object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await client.get_mosaic(uuid="12345678-1234-5678-1234-567812345678")
        """      
        return await AsyncMosaic.get_mosaic(self, uuid, user_id)


    async def get_mosaic_by_name(self, name: str, user_id: int = None) -> Union['AsyncMosaic', None]:
        """
        [async] Get a mosaic by name

        Args:
            name (str): the name of the mosaic to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncMosaic | None: returns the mosaic if a mosaic matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     mosaic = await client.get_mosaic_by_name(name='test')
        """
        return await AsyncMosaic.get_mosaic_by_name(self, name, user_id)


    async def get_models(self, **kwargs) -> Union[List['AsyncModel'], int]:
        """
        [async] Get a list of models with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'".
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): whether to return total count. default is False.
            skip (int): number of models to skip. default is 0.
            limit (int): maximum number of models to return. default is 10.
            user_id (int): specific user. privileges required.
            shared (bool): Whether to return shared models. default is False.

        Returns:
            List[AsyncModel] | int: A list of Model objects or the count number.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     models = await client.get_models(search="my_model",
            ...         search_fields="name, description",
            ...         order_by="name A",
            ...         return_count=True,
            ...         skip=0,
            ...         limit=10,
            ...         shared=False)
        """
        return await AsyncModel.get_models(self, **kwargs)
    

    async def get_model(self, uuid: str, user_id: int = None) -> 'AsyncModel':
        """
        [async] Get a model by its UUID.

        Args:
            uuid (str): The UUID of the model to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncModel: The model object.

        Raises:
            NotFoundError: If the model with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     model = await client.get_model(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncModel.get_model(self, uuid, user_id)


    async def get_model_by_name(self, name: str, user_id: int = None) -> Union['AsyncModel', None]:
        """
        [async] Get a model by name

        Args:
            name (str): the name of the model to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncModel | None: returns the model if a model matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     model = await client.get_model_by_name(name='test')
        """
        return await AsyncModel.get_model_by_name(self, name, user_id)
    
    
    async def get_maps(self, **kwargs) -> Union[List['AsyncMap'], int]:
        """
        [async] Get list of maps with optional filtering and pagination.

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
            >>> async with AsyncGeoboxClient() as client:
            >>>     maps = await client.get_maps(q="name LIKE '%My Map%'")
        """
        return await AsyncMap.get_maps(self, **kwargs)
    

    async def create_map(self, 
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
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await client.create_map(name="my_map", display_name="My Map", description="This is a description of my map", extent=[10, 20, 30, 40], thumbnail="https://example.com/thumbnail.png", style={"type": "style"})
        """
        return await AsyncMap.create_map(self, name, display_name, description, extent, thumbnail, style, user_id)
    

    async def get_map(self, uuid: str, user_id: int = None) -> 'AsyncMap':
        """
        [async] Get a map by its UUID.

        Args:
            uuid (str): The UUID of the map to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncMap: The map object.

        Raises:
            NotFoundError: If the map with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await client.get_map(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncMap.get_map(self, uuid, user_id)


    async def get_map_by_name(self, name: str, user_id: int = None) -> Union['AsyncMap', None]:
        """
        [async] Get a map by name

        Args:
            name (str): the name of the map to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncMap | None: returns the map if a map matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     map = await client.get_map_by_name(name='test')
        """
        return await AsyncMap.get_map_by_name(self, name, user_id)
    

    async def get_queries(self, **kwargs) -> Union[List['AsyncQuery'], int]:
        """
        [async] Get Queries

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of queries to skip. default is 0.
            limit(int): Maximum number of queries to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared queries. default is False.

        Returns:
            List[AsyncQuery] | int: list of queries or the number of queries.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     queries = await client.get_queries()
        """
        return await AsyncQuery.get_queries(self, **kwargs)
    

    async def create_query(self, name: str, display_name: str = None, description: str = None, sql: str = None, params: List = None) -> 'AsyncQuery':
        """
        [async] Creates a new query.

        Args:
            name (str): The name of the query.
            display_name (str, optional): The display name of the query.
            description (str, optional): The description of the query.
            sql (str, optional): The SQL statement for the query.
            params (list, optional): The parameters for the SQL statement.

        Returns:
            AsyncQuery: The created query instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await client.create_query(name='query_name', display_name='Query Name', sql='SELECT * FROM some_layer')
        """
        return await AsyncQuery.create_query(self, name, display_name, description, sql, params)
    

    async def get_query(self, uuid: str, user_id: int = None) -> 'AsyncQuery':
        """
        [async] Retrieves a query by its UUID.

        Args:
            uuid (str): The UUID of the query.
            user_id (int, optional): specific user ID. privileges required.

        Returns:
            AsyncQuery: The retrieved query instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await client.get_query(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncQuery.get_query(self, uuid, user_id)


    async def get_query_by_name(self, name: str, user_id: int = None) -> Union['AsyncQuery', None]:
        """
        [async] Get a query by name

        Args:
            name (str): the name of the query to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncQuery | None: returns the query if a query matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await client.get_query_by_name(name='test')
        """
        return await AsyncQuery.get_query_by_name(self, name, user_id)
    

    async def get_system_queries(self, **kwargs) -> List['AsyncQuery']:
        """
        [async] Returns the system queries as a list of Query objects.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'".
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): whether to return the total count of queries. default is False.
            skip (int): number of queries to skip. minimum is 0. default is 0.
            limit (int): number of queries to return. minimum is 1. default is 100.
            user_id (int): specific user. privileges required.
            shared (bool): whether to return shared queries. default is False.
        
        Returns:
            List[AsyncQuery]: list of system queries.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     queries = await client.get_system_queries()
        """
        return await AsyncQuery.get_system_queries(self, **kwargs)
    

    async def get_users(self, **kwrags) -> Union[List['AsyncUser'], int]:
        """
        [async] Retrieves a list of users (Permission Required)

        Keyword Args:
            status (UserStatus): the status of the users filter.
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
            List[AsyncUser] | int: list of users or the count number.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     users = await client.get_users()
        """
        return await AsyncUser.get_users(self, **kwrags)
    

    async def create_user(self,
                    username: str, 
                    email: str, 
                    password: str, 
                    role: 'UserRole',
                    first_name: str,
                    last_name: str,
                    mobile: str,
                    status: 'UserStatus') -> 'AsyncUser':
        """
        [async] Create a User (Permission Required)

        Args:
            username (str): the username of the user.
            email (str): the email of the user.
            password (str): the password of the user.
            role (UserRole): the role of the user.
            first_name (str): the firstname of the user.
            last_name (str): the lastname of the user.
            mobile (str): the mobile number of the user. e.g. "+98 9120123456".
            status (UserStatus): the status of the user.

        Returns:
            AsyncUser: the user object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     user = await client.create_user(username="user1",
            ...         email="user1@example.com",
            ...         password="P@ssw0rd",
            ...         role=UserRole.ACCOUNT_ADMIN,
            ...         first_name="user 1",
            ...         last_name="user 1",
            ...         mobile="+98 9120123456",
            ...         status=UserStatus.ACTIVE)
        """
        return await AsyncUser.create_user(self, username, email, password, role, first_name, last_name, mobile, status)
    

    async def search_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Get list of users based on the search term.

        Args:
            search (str, optional): The Search Term.
            skip (int, optional): Number of items to skip. default is 0.
            limit (int, optional): Number of items to return. default is 10.

        Returns:
            List[AsyncUser]: A list of User instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     users = await client.get_users(search="John")
        """
        return await AsyncUser.search_users(self, search, skip, limit)
    

    async def get_user(self, user_id: str = 'me') -> 'AsyncUser':
        """
        [async] Get a user by its id (Permission Required)

        Args:
            user_id (int, optional): Specific user. don't specify a user_id to get the current user.

        Returns:
            User: the user object.

        Raises:
            NotFoundError: If the user with the specified id is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     user = await client.get_user(user_id=1)
            get the current user
            >>>     user = await client.get_user()
        """
        return await AsyncUser.get_user(self, user_id)
    

    async def get_my_sessions(self) -> List['AsyncSession']:
        """
        [async] Get a list of user available sessions (Permission Required)

        Returns:
            List[AsyncSession]: list of user sessions.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     await client.get_my_sessions()
        """
        user = await self.get_user()
        return await user.get_sessions()
    

    async def get_workflows(self, **kwargs) -> Union[List['AsyncWorkflow'], int]:
        """
        [async] Get list of workflows with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared workflows. default is False.

        Returns:
            List[AsyncWorkflow] | int: A list of workflow instances or the total number of workflows.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflows = await client.get_workflows(q="name LIKE '%My workflow%'")
        """
        return await AsyncWorkflow.get_workflows(self, **kwargs)
    

    async def create_workflow(self,
        name: str, 
        display_name: str = None, 
        description: str = None, 
        settings: Dict = {}, 
        thumbnail: str = None, 
        user_id: int = None) -> 'AsyncWorkflow':
        """
        [async] Create a new workflow.

        Args:
            name (str): The name of the Workflow.
            display_name (str): The display name of the workflow.
            description (str): The description of the workflow.
            settings (Dict): The settings of the workflow.
            thumbnail (str): The thumbnail of the workflow.
            user_id (int): Specific user. privileges workflow.

        Returns:
            AsyncWorkflow: The newly created workflow instance.

        Raises:
            ValidationError: If the workflow data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await client.create_workflow(name="my_workflow")
        """
        return await AsyncWorkflow.create_workflow(self, name, display_name, description, settings, thumbnail, user_id)


    async def get_workflow(self, uuid: str, user_id: int = None) -> 'AsyncWorkflow':
        """
        [async] Get a workflow by its UUID.

        Args:
            uuid (str): The UUID of the workflow to get.
            user_id (int): Specific user. privileges required.

        Returns:
            AsyncWorkflow: The workflow object.

        Raises:
            NotFoundError: If the workflow with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await client.get_workflow(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncWorkflow.get_workflow(self, uuid, user_id)


    async def get_workflow_by_name(self, name: str, user_id: int = None) -> Union['AsyncWorkflow', None]:
        """
        [async] Get a workflow by name

        Args:
            name (str): the name of the workflow to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncWorkflow | None: returns the workflow if a workflow matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await client.get_workflow_by_name(name='test')
        """
        return await AsyncWorkflow.get_workflow_by_name(self, name, user_id)
    

    async def get_versions(self, **kwargs) -> Union[List['AsyncVectorLayerVersion'], int]:
        """
        [async] Get list of versions with optional filtering and pagination.

        Keyword Args:
            layer_id (str): the id of the vector layer.
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared versions. default is False.

        Returns:
            List[AsyncVectorLayerVersion] | int: A list of vector layer version instances or the total number of versions.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     versions = await client.get_versions(q="name LIKE '%My version%'")
        """
        return await AsyncVectorLayerVersion.get_versions(self, **kwargs)
    

    async def get_version(self, uuid: str, user_id: int = None) -> 'AsyncVectorLayerVersion':
        """
        [async] Get a version by its UUID.

        Args:
            uuid (str): The UUID of the version to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncVectorLayerVersion: The vector layer version object.

        Raises:
            NotFoundError: If the version with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await client.get_version(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncVectorLayerVersion.get_version(self, uuid, user_id)


    async def get_version_by_name(self, name: str, user_id: int = None) -> 'AsyncVectorLayerVersion':
        """
        [async] Get a version by name

        Args:
            name (str): the name of the version to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncVectorLayerVersion | None: returns the version if a version matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await client.get_version_by_name(name='test')
        """
        return await AsyncVectorLayerVersion.get_version_by_name(self, name, user_id)
    

    async def get_layouts(self, **kwargs) -> Union[List['AsyncLayout'], int]:
        """
        [async] Get list of layouts with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared layouts. default is False.

        Returns:
            List[AsyncLayout] | int: A list of layout instances or the total number of layouts.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layouts = await client.get_layouts(q="name LIKE '%My layout%'")
        """
        return await AsyncLayout.get_layouts(self, **kwargs)
    

    async def create_layout(self,
        name: str, 
        display_name: str = None, 
        description: str = None, 
        settings: Dict = {}, 
        thumbnail: str = None, 
        user_id: int = None) -> 'AsyncLayout':
        """
        [async] Create a new layout.

        Args:
            name (str): The name of the layout.
            display_name (str): The display name of the layout.
            description (str): The description of the layout.
            settings (Dict): The settings of the layout.
            thumbnail (str): The thumbnail of the layout.
            user_id (int): Specific user. privileges layout.

        Returns:
            AsyncLayout: The newly created layout instance.

        Raises:
            ValidationError: If the layout data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await client.create_layout(name="my_layout")
        """
        return await AsyncLayout.create_layout(self, name, display_name, description, settings, thumbnail, user_id)


    async def get_layout(self, uuid: str, user_id: int = None) -> 'AsyncLayout':
        """
        [async] Get a layout by its UUID.

        Args:
            uuid (str): The UUID of the layout to get.
            user_id (int): Specific user. privileges required.

        Returns:
            AsyncLayout: The layout object.

        Raises:
            NotFoundError: If the layout with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await client.get_layout(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncLayout.get_layout(self, uuid, user_id)


    async def get_layout_by_name(self, name: str, user_id: int = None) -> Union['AsyncLayout', None]:
        """
        [async] Get a layout by name

        Args:
            name (str): the name of the layout to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncLayout | None: returns the layout if a layout matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await client.get_layout_by_name(name='test')
        """
        return await AsyncLayout.get_layout_by_name(self, name, user_id)


    async def get_3dtiles(self, **kwargs) -> Union[List['AsyncTile3d'], int]:
        """
        [async] Get list of 3D Tiles with optional filtering and pagination.

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
            List[AsyncTile3d] | int: A list of 3D Tile instances or the total number of 3D Tiles.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     tiles = await client.get_3dtiles(q="name LIKE '%My tile%'")
        """ 
        return await AsyncTile3d.get_3dtiles(self, **kwargs)
    

    async def get_3dtile(self, uuid: str, user_id: int = None) -> 'AsyncTile3d':
        """
        [async] Get a 3D Tile by its UUID.

        Args:
            uuid (str): The UUID of the map to 3D Tile.
            user_id (int): Specific user. privileges required.

        Returns:
            AsyncTile3d: The 3D Tile object.

        Raises:
            NotFoundError: If the 3D Tile with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     tile = await client.get_3dtile(uuid="12345678-1234-5678-1234-567812345678")
        """ 
        return await AsyncTile3d.get_3dtile(self, uuid, user_id)


    async def get_3dtile_by_name(self, name: str, user_id: int = None) -> Union['AsyncTile3d', None]:
        """
        [async] Get a 3dtile by name

        Args:
            name (str): the name of the 3dtile to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncTile3d | None: returns the 3dtile if a 3dtile matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     tile3d = await client.get_3dtile_by_name(name='test')
        """
        return await AsyncTile3d.get_3dtile_by_name(self, name, user_id)
    

    async def get_system_settings(self) -> 'AsyncSystemSettings':
        """
        [async] Get System Settings object (Permission Required).

        Returns:
            AsyncSystemSetting: the system settings object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     setting = await client.get_system_settings()
        """
        return await AsyncSystemSettings.get_system_settings(self)


    async def get_scenes(self, **kwargs) -> Union[List['AsyncScene'], int]:
        """
        [async] Get list of scenes with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared scenes. default is False.

        Returns:
            List[AsyncScene] | int: A list of scene instances or the total number of scenes.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     scenes = await client.get_scenes(q="name LIKE '%My scene%'")
        """
        return await AsyncScene.get_scenes(self, **kwargs)
    

    async def create_scene(self, 
        name: str, 
        display_name: str = None, 
        description: str = None, 
        settings: Dict = {}, 
        thumbnail: str = None, 
        user_id: int = None) -> 'AsyncScene':
        """
        [async] Create a new scene.

        Args:
            name (str): The name of the scene.
            display_name (str, optional): The display name of the scene.
            description (str, optional): The description of the scene.
            settings (Dict,optional): The settings of the scene.
            thumbnail (str, optional): The thumbnail of the scene.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncScene: The newly created scene instance.

        Raises:
            ValidationError: If the scene data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     scene = await client.create_scene(name="my_scene")
        """
        return await AsyncScene.create_scene(self, 
            name, 
            display_name, 
            description, 
            settings, 
            thumbnail, 
            user_id)
    

    async def get_scene(self, uuid: str, user_id: int = None) -> 'AsyncScene':
        """
        [async] Get a scene by its UUID.

        Args:
            uuid (str): The UUID of the scene to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncScene: The scene object.

        Raises:
            NotFoundError: If the scene with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     scene = await client.get_scene(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncScene.get_scene(self, uuid, user_id)


    async def get_scene_by_name(self, name: str, user_id: int = None) -> Union['AsyncScene', None]:
        """
        [async] Get a scene by name

        Args:
            name (str): the name of the scene to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncScene | None: returns the scene if a scene matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     scene = await client.get_scene_by_name(name='test')
        """
        return await AsyncScene.get_scene_by_name(self, name, user_id)


    async def route(self, stops: str, **kwargs) -> Dict:
        """
        [async] Find best driving routes between coordinates and return results.

        Args:
            stops (str): Comma-separated list of stop coordinates in the format lon,lat;lon,lat.

        Keyword Args:
            alternatives (bool): Whether to return alternative routes. Default value : False.
            steps (bool): Whether to include step-by-step navigation instructions. Default value : False.
            geometries (RoutingGeometryType): Format of the returned geometry.
            overview (RoutingOverviewLevel): Level of detail in the returned geometry.
            annotations (bool): Whether to include additional metadata like speed, weight, etc.

        Returns:
            Dict: the routing output

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     route = await client.route(stops="53,33;56,36",
            ...         alternatives=True,
            ...         steps=True,
            ...         geometries=RoutingGeometryType.geojson,
            ...         overview=RoutingOverviewLevel.full,
            ...         annotations=True)
        """
        return await AsyncRouting.route(self, stops, **kwargs)
    

    async def get_plans(self, **kwargs) -> Union[List['AsyncPlan'], int]:
        """
        [async] Get list of plans with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared plans. default is False.

        Returns:
            List[AsyncPlan] | int: A list of plan instances or the total number of plans.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     plans = await client.get_plans(q="name LIKE '%My plan%'")
        """
        return await AsyncPlan.get_plans(self, **kwargs)
    

    async def create_plan(self,
        name: str,
        plan_color: str,
        storage: int,
        concurrent_tasks: int,
        daily_api_calls: int,
        monthly_api_calls: int,
        daily_traffic: int,
        monthly_traffic: int,
        daily_process: int,
        monthly_process: int,
        number_of_days: int = None,
        display_name: str = None,
        description: str = None) -> 'AsyncPlan':
        """
        [async] Create a new plan.

        Args:
            name (str): The name of the plan.
            plan_color (str): hex value of the color. e.g. #000000.
            storage (int): storage value in bytes. must be greater that 1.
            concurrent_tasks (int): number of concurrent tasks. must be greater that 1.
            daily_api_calls (int): number of daily api calls. must be greater that 1.
            monthly_api_calls (int): number of monthly api calls. must be greater that 1.
            daily_traffic (int): number of daily traffic. must be greater that 1.
            monthly_traffic (int): number of monthly traffic. must be greater that 1.
            daily_process (int): number of daily processes. must be greater that 1.
            monthly_process (int): number of monthly processes. must be greater that 1.
            number_of_days (int, optional): number of days. must be greater that 1.
            display_name (str, optional): display name of the plan.
            description (str, optional): description of the plan.

        Returns:
            AsyncPlan: The newly created plan instance.

        Raises:
            ValidationError: If the plan data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     plan = await client.create_plan(name="new_plan",
            ...         display_name=" New Plan",
            ...         description="new plan description",
            ...         plan_color="#000000",
            ...         storage=10,
            ...         concurrent_tasks=10,
            ...         daily_api_calls=10,
            ...         monthly_api_calls=10,
            ...         daily_traffic=10,
            ...         monthly_traffic=10,
            ...         daily_process=10,
            ...         monthly_process=10,
            ...         number_of_days=10)
        """
        return await AsyncPlan.create_plan(self,
            name,
            plan_color,
            storage,
            concurrent_tasks,
            daily_api_calls,
            monthly_api_calls,
            daily_traffic,
            monthly_traffic,
            daily_process,
            monthly_process,
            number_of_days,
            display_name,
            description)
    

    async def get_plan(self, plan_id: int) -> 'AsyncPlan':
        """
        [async] Get a plan by its id.

        Args:
            plan_id (int): The id of the plan to get.

        Returns:
            AsyncPlan: The plan object

        Raises:
            NotFoundError: If the plan with the specified id is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     plan = await client.get_plan(plan_id=1)
        """
        return await AsyncPlan.get_plan(self, plan_id)
    

    async def get_plan_by_name(self, name: str) -> Union['AsyncPlan', None]:
        """
        [async] Get a plan by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the plan to get

        Returns:
            AsyncPlan | None: returns the plan if a plan matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     plan = await client.get_plan_by_name(name='test')
        """
        return await AsyncPlan.get_plan_by_name(self, name)
    

    async def get_dashboards(self, **kwargs) -> Union[List['AsyncDashboard'], int]:
        """
        [async] Get list of Dashboards

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared Dashboards. default is False.

        Returns:
            List[AsyncDashboard] | int: A list of Dashboard instances or the total number of Dashboards.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboards = await client.get_dashboards()
        """
        return await AsyncDashboard.get_dashboards(self, **kwargs)
    

    async def create_dashboard(self,
        name: str, 
        display_name: str = None, 
        description: str = None, 
        settings: Dict = {}, 
        thumbnail: str = None, 
        user_id: int = None) -> 'AsyncDashboard':
        """
        [async] Create a new Dashboard.

        Args:
            name (str): The name of the Dashboard.
            display_name (str, optional): The display name of the Dashboard.
            description (str, optional): The description of the Dashboard.
            settings (Dict, optional): The settings of the sceDashboarde.
            thumbnail (str, optional): The thumbnail of the Dashboard.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncDashboard: The newly created Dashboard instance.

        Raises:
            ValidationError: If the Dashboard data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await client.create_dashboard(name="my_dashboard")
        """
        return await AsyncDashboard.create_dashboard(self,
            name,
            display_name,
            description,
            settings,
            thumbnail,
            user_id)
    

    async def get_dashboard(self, uuid: str, user_id: int = None) -> 'AsyncDashboard':
        """
        [async] Get a Dashboard by its UUID.

        Args:
            uuid (str): The UUID of the Dashboard to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncDashboard: The dashboard object.

        Raises:
            NotFoundError: If the Dashboard with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await client.get_dashboard(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await AsyncDashboard.get_dashboard(self, uuid, user_id)


    async def get_dashboard_by_name(self, name: str, user_id: int = None) -> Union['AsyncDashboard', None]:
        """
        [async] Get a dashboard by name

        Args:
            name (str): the name of the dashboard to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncDashboard | None: returns the dashboard if a dashboard matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await client.get_dashboard_by_name(name='test')
        """
        return await AsyncDashboard.get_dashboard_by_name(self, name, user_id)
    

    async def get_basemaps(self) -> List['AsyncBasemap']:
        """
        [async] Get a list of basemaps

        Returns:
            List[AsyncBaseMap]: list of basemaps.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     basemaps = await client.get_basemaps()
        """
        return await AsyncBasemap.get_basemaps(self)
    

    async def get_basemap(self, name: str) -> 'AsyncBasemap':
        """
        [async] Get a basemap object

        Args:
            name: the basemap name

        Returns:
            AsyncBasemap: the basemap object

        Raises:
            NotFoundError: if the base,ap with the specified name not found

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     basemap = await client.get_basemap(name='test')
        """
        return await AsyncBasemap.get_basemap(self, name)
    

    async def proxy_basemap(self, url: str) -> None:
        """
        [async] Proxy the basemap

        Args:
            url (str): the proxy server url.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     await client.proxy_basemap(url='proxy_server_url')
        """
        return await AsyncBasemap.proxy_basemap(self, url)
    

    async def get_attachments(self, resource: Union['AsyncMap', 'AsyncVectorLayer', 'AsyncVectorLayerView'], **kwargs) -> List['AsyncAttachment']:
        """
        [async] Get the resouces attachments

        Args:
            resource (AsyncMap | AsyncVectorLayer | AsyncVectorLayerView): options are: Map, Vector, View objects

        Keyword Args:
            element_id (str): the id of the element with attachment.
            search (str): search term for keyword-based searching among all textual fields.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            return_count (bool): Whether to return total count. default is False.

        Returns:
            List[AsyncAttachment] | int: A list of attachments instances or the total number of attachments.

        Raises:
            TypeError: if the resource type is not supported

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     maps = await client.get_maps()
            >>>     map = maps[0]
            >>>     attachments = await client.get_attachments(resource=map)
        """
        return await AsyncAttachment.get_attachments(self, resource=resource, **kwargs)
    

    async def create_attachment(self,
        name: str, 
        loc_x: int,
        loc_y: int,
        resource: Union['AsyncMap', 'AsyncVectorLayer', 'AsyncVectorLayerView'],
        file: 'AsyncFile',
        feature: 'AsyncFeature' = None,
        display_name: str = None, 
        description: str = None, ) -> 'AsyncAttachment':
        """
        [async] Create a new Attachment.

        Args:
            name (str): The name of the scene.
            loc_x (int): x parameter of the attachment location.
            loc_y (int): y parameter of the attachment location.
            resource (AsyncMap | AsyncVectorLayer | AsyncVectorLayerView): the resource object.
            file (AsyncFile): the file object.
            feature (AsyncFeature, optional): the feature object.
            display_name (str, optional): The display name of the scene.
            description (str, optional): The description of the scene.

        Returns:
            Attachment: The newly created Attachment instance.

        Raises:
            ValidationError: If the Attachment data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(feature_id=1)
            >>>     file = await client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>>     attachment = await client.create_attachment(name="my_attachment", 
            ...         loc_x=30, 
            ...         loc_y=50, 
            ...         resource=layer, 
            ...         file=file, 
            ...         feature=feature, 
            ...         display_name="My Attachment", 
            ...         description="Attachment Description")
        """
        return await AsyncAttachment.create_attachment(self,
            name,
            loc_x,
            loc_y,
            resource,
            file,
            feature,
            display_name,
            description)
    

    async def update_attachment(self, attachment_id: int, **kwargs) -> Dict:
        """
        [async] Update the attachment.

        Args:
            attachment_id (int): the attachment id.

        Keyword Args:
            name (str): The name of the attachment.
            display_name (str): The display name of the attachment.
            description (str): The description of the attachment.
            loc_x (int): x parameter of the attachment location.
            loc_y (int): y parameter of the attachment location.

        Returns:
            Dict: The updated attachment data.

        Raises:
            ValidationError: If the attachment data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     await client.update_attachment(attachment_id=1, display_name="New Display Name")
        """
        return await AsyncAttachment.update_attachment(self, attachment_id, **kwargs)
    

    async def get_apikeys(self, **kwargs) -> List['AsyncApiKey']:
        """
        [async] Get a list of apikeys

        Keyword Args:
            search (str): search term for keyword-based searching among all textual fields.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of layers to skip. default is 0.
            limit (int): Maximum number of layers to return. default is 10.
            user_id (int): Specific user. privileges required.
        
        Returns: 
            AsyncApiKey: list of apikey objects
    
        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikeys = await client.get_apikeys()
        """
        return await AsyncApiKey.get_apikeys(self, **kwargs)
    

    async def create_apikey(self, name: str, user_id: int = None) -> 'AsyncApiKey':
        """
        [async] Create an ApiKey

        Args:
            name (str): name of the key.
            user_id (int, optional): Specific user. privileges required.

        Returns: 
            AsyncApiKey: the apikey object

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await client.create_apikey(name='test')
        """
        return await AsyncApiKey.create_apikey(self, name, user_id)
    

    async def get_apikey(self, key_id: int) -> 'AsyncApiKey':
        """
        [async] Get an ApiKey

        Args:
            key_id (str): the id of the apikey.

        Returns:
            AsyncApiKey: the ApiKey object

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await client.get_apikey(key_id=1) 
        """
        return await AsyncApiKey.get_apikey(self, key_id)


    async def get_apikey_by_name(self, name: str, user_id: int = None) -> 'AsyncApiKey':
        """
        [async] Get an ApiKey by name

        Args:
            name (str): the name of the key to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncApiKey | None: returns the key if a key matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     apikey = await client.get_apikey_by_name(name='test')
        """
        return await AsyncApiKey.get_apikey_by_name(self, name, user_id)


    async def get_logs(self, **kwargs) -> List['AsyncLog']:
        """
        [async] Get a list of Logs

        Keyword Args:
            search (str): search term for keyword-based searching among all textual fields
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. Privileges required.
            from_date (datetime): datetime object in this format: "%Y-%m-%dT%H:%M:%S.%f". 
            to_date (datetime): datetime object in this format: "%Y-%m-%dT%H:%M:%S.%f". 
            user_identity (str): the user identity in this format: username - firstname lastname - email .
            activity_type (str): the user activity type.

        Returns:
            List[AsyncLog]: a list of logs

        Example: 
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     logs = await client.get_logs() 
        """ 
        return await AsyncLog.get_logs(self, **kwargs)


    async def get_api_usage(self, 
        resource: Union['AsyncUser', 'AsyncApiKey'], 
        scale: 'UsageScale',
        param: 'UsageParam',
        from_date: 'datetime' = None,
        to_date: 'datetime' = None,
        days_before_now: int = None,
        limit: int = None) -> List:
        """
        [async] Get the api usage of a user

        Args:
            resource (AsyncUser | AsyncApiKey): User or ApiKey object.
            scale (UsageScale): the scale of the report.
            param (UsageParam): traffic or calls.
            from_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            to_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            days_before_now (int, optional): number of days befor now.
            limit (int, optional): Number of items to return. default is 10.

        Raises:
            ValueError: one of days_before_now or from_date/to_date parameters must have value
            ValueError: resource must be a 'user' or 'apikey' object

        Returns:
            List: usage report

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     user = await client.get_user() # gets current user
            >>>     usage = await client.get_api_usage(resource=user, 
            ...                                         scale=UsageScale.Day, 
            ...                                         param=UsageParam.Calls, 
            ...                                         days_before_now=5)
        """
        return await AsyncUsage.get_api_usage(self,
            resource=resource, 
            scale=scale,
            param=param,
            from_date=from_date,
            to_date=to_date,
            days_before_now=days_before_now,
            limit=limit)


    async def get_process_usage(self, 
        user_id: int = None, 
        from_date: datetime = None, 
        to_date: datetime = None, 
        days_before_now: int = None) -> float:
        """
        [async] Get process usage of a user in seconds

        Args:
            user_id (int, optional): the id of the user. leave blank to get the current user report.
            from_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            to_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            days_before_now (int, optional): number of days befor now.

        Raises:
            ValueError: one of days_before_now or from_date/to_date parameters must have value

        Returns:
            float: process usage of a user in seconds

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     process_usage = await client.get_process_usage(days_before_now=5)
        """
        return await AsyncUsage.get_process_usage(self,
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            days_before_now=days_before_now)


    async def get_usage_summary(self, user_id: int = None) -> Dict:
        """
        [async] Get the usage summary of a user

        Args:
            user_id (int, optional): the id of the user. leave blank to get the current user report.

        Returns:
            Dict: the usage summery of the users

        Returns:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     usage_summary = await client.get_usage_summary()
        """
        return await AsyncUsage.get_usage_summary(self, user_id=user_id)


    async def update_usage(self, user_id: int = None) -> Dict:
        """
        [async] Update usage of a user

        Args:
            user_id (int, optional): the id of the user. leave blank to get the current user report.
            
        Returns:
            Dict: the updated data

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     await client.update_usage()
        """
        return await AsyncUsage.update_usage(self, user_id=user_id)
