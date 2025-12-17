from typing import List, Dict, Optional, TYPE_CHECKING, Union
from urllib.parse import urljoin

from .base import AsyncBase
from .map import AsyncMap
from .vectorlayer import AsyncVectorLayer
from .view import AsyncVectorLayerView
from .file import AsyncFile
from ..utils import clean_data

if TYPE_CHECKING:
    from . import AsyncGeoboxClient 
    from .feature import Feature
    from ..api import GeoboxClient
    from ..attachment import Attachment


class AsyncAttachment(AsyncBase):

    BASE_ENDPOINT = 'attachments/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        attachment_id: str,
        data: Optional[Dict] = {}):
        """
        Initialize an Attachment instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            attachment_id (str): The id for the attachment.
            data (Dict, optional): The data of the attachment.
        """
        super().__init__(api, data=data)
        self.attachment_id = attachment_id
        self.endpoint = f"{self.BASE_ENDPOINT}{str(self.attachment_id)}/"


    def __repr__(self) -> str:
        """
        Return a string representation of the attachment.

        Returns:
            str: The string representation of the attachment.
        """
        return f"AsyncAttachment(id={self.attachment_id}, name={self.name})"


    @property
    def file(self) -> 'AsyncFile':
        """
        Attachment file property

        Returns:
            File: the file object
        """
        return AsyncFile(self.api, self.data['file'].get('uuid'), self.data['file'])


    @classmethod
    async def get_attachments(cls, 
        api: 'AsyncGeoboxClient', 
        resource: Union['AsyncMap', 'AsyncVectorLayer', 'AsyncVectorLayerView'], 
        **kwargs) -> Union[List['AsyncAttachment'], int]:
        """
        [async] Get list of attachments with optional filtering and pagination.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
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
            >>> from geobox.aio.attachment import AsyncAttachment
            >>> async with AsyncGeoboxClient() as client:
            >>>     maps = await client.get_maps()
            >>>     map = maps[0]
            >>>     attachments = await AsyncAttachment.get_attachments(client, resource=map, q="name LIKE '%My attachment%'")
            or  
            >>>     attachments = await client.get_attachments(resource=map, q="name LIKE '%My attachment%'")
        """
        if type(resource) == AsyncVectorLayer:
            resource_type = 'vector'

        elif type(resource) == AsyncVectorLayerView:
            resource_type = 'view'

        elif type(resource) == AsyncMap:
            resource_type = 'map'

        else:
            raise TypeError('resource must be a vectorlayer or view or map object')


        params = {
           'resource_type': resource_type,
           'resource_uuid': resource.uuid,
           'element_id': kwargs.get('element_id'),
           'search': kwargs.get('search'),
           'order_by': kwargs.get('order_by'),
           'skip': kwargs.get('skip', 0),
           'limit': kwargs.get('limit', 10),
           'return_count': kwargs.get('return_count')
        }
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncAttachment(api, item['id'], item))
    

    @classmethod
    async def create_attachment(cls, 
        api: 'AsyncGeoboxClient', 
        name: str, 
        loc_x: int,
        loc_y: int,
        resource: Union['AsyncMap', 'AsyncVectorLayer', 'AsyncVectorLayerView'],
        file: 'File',
        feature: 'Feature' = None,
        display_name: str = None, 
        description: str = None, ) -> 'AsyncAttachment':
        """
        [async] Create a new Attachment.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the scene.
            loc_x (int): x parameter of the attachment location.
            loc_y (int): y parameter of the attachment location.
            resource (AsyncMap | AsyncVectorLayer | AsyncVectorLayerView): the resource object.
            file (File): the file object.
            feature (Feature, optional): the feature object.
            display_name (str, optional): The display name of the scene.
            description (str, optional): The description of the scene.

        Returns:
            AsyncAttachment: The newly created Attachment instance.

        Raises:
            ValidationError: If the Attachment data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.attachment import AsyncAttachment
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(feature_id=1)
            >>>     file = await client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>>     attachment = await AsyncAttachment.create_attachment(client, 
            ...         name="my_attachment", 
            ...         loc_x=30, 
            ...         loc_y=50, 
            ...         resource=layer, 
            ...         file=file, 
            ...         feature=feature, 
            ...         display_name="My Attachment", 
            ...         description="Attachment Description")
            or  
            >>>     attachment = await client.create_attachment(name="my_attachment", 
            ...         loc_x=30, 
            ...         loc_y=50, 
            ...         resource=layer, 
            ...         file=file, 
            ...         feature=feature, 
            ...         display_name="My Attachment", 
            ...         description="Attachment Description")
        """
        if isinstance(resource, AsyncVectorLayer):
            resource_type = 'vector'

        if isinstance(resource, AsyncVectorLayerView):
            resource_type = 'view'

        if isinstance(resource, AsyncMap):
            resource_type = 'map'

        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "loc_x": loc_x,
            "loc_y": loc_y,
            "resource_type": resource_type,
            "resource_uuid": resource.uuid,
            "element_id": feature.id if feature else None,
            "file_id": file.id
            }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncAttachment(api, item['id'], item))


    @classmethod
    async def update_attachment(cls, api: 'AsyncGeoboxClient', attachment_id: int, **kwargs) -> Dict:
        """
        [async] Update the attachment.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
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
            >>> from geobox.aio.attachment import AsyncAttachment
            >>> async with AsyncGeoboxClient() as client:
            >>>     await AsyncAttachment.update_attachment(client, attachment_id=1, display_name="New Display Name")
            or  
            >>>     await client.update_attachment(attachment_id=1, display_name="New Display Name")
        """
        data = clean_data({
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
            "loc_x": kwargs.get('loc_x'),
            "loc_y": kwargs.get('loc_y')
        })
        endpoint = urljoin(cls.BASE_ENDPOINT, str(attachment_id))
        response = await api.put(endpoint, data)
        return response
    

    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the attachment.

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
            >>> from geobox.aio.attachment import AsyncAttachment
            >>> async with AsyncGeoboxClient() as client:
            >>>     attachment = await AsyncAttachment.get_attachments(client)[0]
            >>>     await attachment.update(display_name="New Display Name")
        """
        data = clean_data({
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
            "loc_x": kwargs.get('loc_x'),
            "loc_y": kwargs.get('loc_y')
        })
        response = await self.api.put(self.endpoint, data)
        self._update_properties(response)
        return response
    

    async def delete(self) -> None:
        """
        [async] Delete the scene.

        Returns:
            None

        Raises:
            ApiRequestError: If the API request fails.
            ValidationError: If the scene data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.attachment import AsyncAttachment
            >>> async with AsyncGeoboxClient() as client:
            >>>     attachment = await AsyncAttachment.get_attachments(client)[0]
            >>>     await attachment.delete()
        """
        await super()._delete(self.endpoint)
        self.attachment_id = None


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the attachment.

        Returns:
            str: The thumbnail of the scene.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.attachment import AsyncAttachment
            >>> async with AsyncGeoboxClient() as client:
            >>>     attachment = await AsyncAttachment.get_attachment(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     attachment.thumbnail
        """
        return super()._thumbnail(format='')
    

    def to_sync(self, sync_client: 'GeoboxClient') -> 'Attachment':
        """
        Switch to sync version of the attachment instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Attachment: the sync instance of the attachment.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.attachment import AsyncAttachment
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     attachment = await AsyncAttachment.get_attachment(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_attachment = attachment.to_sync(client)
        """
        from ..attachment import Attachment

        return Attachment(api=sync_client, attachment_id=self.attachment_id, data=self.data)