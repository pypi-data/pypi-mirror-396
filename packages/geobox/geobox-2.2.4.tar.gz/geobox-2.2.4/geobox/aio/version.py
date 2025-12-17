from typing import TYPE_CHECKING, Dict, List, Optional, Union

from .base import AsyncBase

if TYPE_CHECKING:
    from .api import AsyncGeoboxClient
    from .user import AsyncUser
    from ..api import GeoboxClient
    from ..version import VectorLayerVersion

class AsyncVectorLayerVersion(AsyncBase):

    BASE_ENDPOINT = 'vectorLayerVersions/'

    def __init__(self, 
        api: 'AsyncGeoboxClient',
        uuid: str,
        data: Optional[Dict] = {}):
        """
        Initialize a vector layer version instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The unique identifier for the version.
            data (Dict): The data of the version.
        """
        super().__init__(api, uuid=uuid, data=data)
    

    @classmethod
    async def get_versions(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncVectorLayerVersion'], int]:
        """
        [async] Get list of versions with optional filtering and pagination.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

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
            >>> from geobox.aio.version import AsyncVectorLayerVersion
            >>> async with AsyncGeoboxClient() as client:
            >>>     versions = await AsyncVectorLayerVersion.get_versions(client, q="name LIKE '%My version%'")
            or  
            >>>     versions = await client.get_versions(q="name LIKE '%My version%'")
        """
        params = {
            'layer_id': kwargs.get('layer_id'),
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
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncVectorLayerVersion(api, item['uuid'], item))


    @classmethod
    async def get_version(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncVectorLayerVersion':
        """
        [async] Get a version by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the version to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncVectorLayerVersion: The vector layer version object.

        Raises:
            NotFoundError: If the version with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.version import AsyncVectorLayerVersion
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await AsyncVectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     version = await client.get_version(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncVectorLayerVersion(api, item['uuid'], item))
    

    @classmethod
    async def get_version_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> 'AsyncVectorLayerVersion':
        """
        [async] Get a version by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the version to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncVectorLayerVersion | None: returns the version if a version matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.version import AsyncVectorLayerVersion
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await VectorLayerView.get_version_by_name(client, name='test')
            or  
            >>>     version = await client.get_version_by_name(name='test')
        """
        versions = await cls.get_versions(api, q=f"name = '{name}'", user_id=user_id)
        if versions and versions[0].name == name:
            return versions[0]
        else:
            return None


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the version.

        Args:
            name (str): The name of the version.
            display_name (str): The display name of the version.
            description (str): The description of the version.

        Returns:
            Dict: The updated version data.

        Raises:
            ValidationError: If the version data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.version import AsyncVectorLayerVersion
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await AsyncVectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await version.update_version(display_name="New Display Name")
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
        }
        return await super()._update(self.endpoint, data)


    async def delete(self) -> None:
        """
        [async] Delete the version.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.version import AsyncVectorLayerVersion
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await AsyncVectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await version.delete()
        """
        await super()._delete(self.endpoint)


    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the version with specified users.

        Args:
            users (List[User]): The list of user objects to share the version with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.version import AsyncVectorLayerVersion
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await AsyncVectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await version.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the version with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the version with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.version import AsyncVectorLayerVersion
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await AsyncVectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await version.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the version is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[AsyncUser]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.version import AsyncVectorLayerVersion
            >>> async with AsyncGeoboxClient() as client:
            >>>     version = await AsyncVectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await version.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)

    
    def to_sync(self, sync_client: 'GeoboxClient') -> 'VectorLayerVersion':
        """
        Switch to sync version of the version instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            VectorLayerVersion: the sync instance of the version.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     version = await async_client.get_version(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_version = version.to_sync(client)
        """
        from ..version import VectorLayerVersion

        return VectorLayerVersion(api=sync_client, uuid=self.uuid, data=self.data)