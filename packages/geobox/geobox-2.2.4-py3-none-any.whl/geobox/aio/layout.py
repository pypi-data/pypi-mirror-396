from typing import List, Dict, Optional, TYPE_CHECKING, Union

from .base import AsyncBase

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from ..api import GeoboxClient
    from ..layout import Layout


class AsyncLayout(AsyncBase):

    BASE_ENDPOINT = 'layouts/'

    def __init__(self, 
                 api: 'AsyncGeoboxClient', 
                 uuid: str,
                 data: Optional[Dict] = {}):
        """
        Initialize a layout instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The unique identifier for the layout.
            data (Dict): The data of the layout.
        """
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    async def get_layouts(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncLayout'], int]:
        """
        Get list of layouts with optional filtering and pagination.

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
            shared (bool): Whether to return shared layouts. default is False.

        Returns:
            List[AsyncLayout] | int: A list of layout instances or the total number of layouts.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layouts = await AsyncLayout.get_layout(client, q="name LIKE '%My layout%'")
            or  
            >>>     layouts = await client.get_layout(q="name LIKE '%My layout%'")
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
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncLayout(api, item['uuid'], item))
    

    @classmethod
    async def create_layout(cls, 
                     api: 'AsyncGeoboxClient', 
                     name: str, 
                     display_name: str = None, 
                     description: str = None, 
                     settings: Dict = {}, 
                     thumbnail: str = None, 
                     user_id: int = None) -> 'AsyncLayout':
        """
        Create a new layout.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the Layout.
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
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.create_layout(client, name="my_layout")
            or  
            >>>     layout = await client.create_layout(name="my_layout")
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "settings": settings,
            "thumbnail": thumbnail,
            "user_id": user_id,
        }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncLayout(api, item['uuid'], item))

    
    @classmethod
    async def get_layout(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncLayout':
        """
        Get a layout by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the layout to get.
            user_id (int): Specific user. privileges required.

        Returns:
            AsyncLayout: The layout object.

        Raises:
            NotFoundError: If the layout with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.get_layout(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     layout = await client.get_layout(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncLayout(api, item['uuid'], item))


    @classmethod
    async def get_layout_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncLayout', None]:
        """
        Get a layout by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the layout to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncLayout | None: returns the layout if a layout matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.get_layout_by_name(client, name='test')
            or  
            >>>     layout = await client.get_layout_by_name(name='test')
        """
        layouts = await cls.get_layouts(api, q=f"name = '{name}'", user_id=user_id)
        if layouts and layouts[0].name == name:
            return layouts[0]
        else:
            return None


    async def update(self, **kwargs) -> Dict:
        """
        Update the layout.

        Keyword Args:
            name (str): The name of the layout.
            display_name (str): The display name of the layout.
            description (str): The description of the layout.
            settings (Dict): The settings of the layout.
            thumbnail (str): The thumbnail of the layout.

        Returns:
            Dict: The updated layout data.

        Raises:
            ValidationError: If the layout data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.get_layout(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await layout.update(display_name="New Display Name")
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
            "settings": kwargs.get('settings'),
            "thumbnail": kwargs.get('thumbnail')
        }
        return await super()._update(self.endpoint, data)
    

    async def delete(self) -> None:
        """
        Delete the Layout.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.get_layout(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await layout.delete()
        """
        await super()._delete(self.endpoint)


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the Layout.

        Returns:
            str: The thumbnail of the Layout.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.get_layout(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     layout.thumbnail
        """
        return super()._thumbnail()
    

    async def share(self, users: List['AsyncUser']) -> None:
        """
        Shares the layout with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to share the layout with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.get_layout(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await users = client.search_users(search='John')
            >>>     await layout.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        Unshares the layout with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to unshare the layout with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.get_layout(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await layout.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        Retrieves the list of users the layout is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> async with AsyncGeoboxClient() as client:
            >>>     layout = await AsyncLayout.get_layout(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await layout.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Layout':
        """
        Switch to sync version of the layout instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Layout: the sync instance of the layout.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.layout import AsyncLayout
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     layout = await AsyncLayout.get_layout(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_layout = layout.to_sync(client)
        """
        from ..layout import Layout

        return Layout(api=sync_client, uuid=self.uuid, data=self.data)