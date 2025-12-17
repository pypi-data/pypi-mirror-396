from typing import List, Dict, Optional, TYPE_CHECKING, Union

from .base import AsyncBase

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from ..api import GeoboxClient
    from ..dashboard import Dashboard


class AsyncDashboard(AsyncBase):

    BASE_ENDPOINT = 'dashboards/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str,
        data: Optional[Dict] = {}):
        """
        Initialize a Dashboard instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The unique identifier for the Dashboard.
            data (Dict, optional): The data of the Dashboard.
        """
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    async def get_dashboards(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncDashboard'], int]:
        """
        [async] Get list of Dashboards

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
            shared (bool): Whether to return shared Dashboards. default is False.

        Returns:
            List[AsyncDashboard] | int: A list of Dashboard instances or the total number of Dashboards.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboards = await AsyncDashboard.get_dashboards(client)
            or  
            >>>     dashboards = await client.get_dashboards()
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
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncDashboard(api, item['uuid'], item))
    

    @classmethod
    async def create_dashboard(cls, 
        api: 'AsyncGeoboxClient', 
        name: str, 
        display_name: str = None, 
        description: str = None, 
        settings: Dict = {}, 
        thumbnail: str = None, 
        user_id: int = None) -> 'AsyncDashboard':
        """
        [async] Create a new Dashboard.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
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
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.create_dashboard(client, name="my_dashboard")
            or  
            >>>     dashboard = await client.create_dashboard(name="my_dashboard")
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "settings": settings,
            "thumbnail": thumbnail,
            "user_id": user_id,
        }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncDashboard(api, item['uuid'], item))

    
    @classmethod
    async def get_dashboard(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncDashboard':
        """
        [async] Get a Dashboard by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the Dashboard to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            AsyncDashboard: The dashboard object.

        Raises:
            NotFoundError: If the Dashboard with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     dashboard = await client.get_dashboard(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncDashboard(api, item['uuid'], item))


    @classmethod
    async def get_dashboard_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncDashboard', None]:
        """
        [async] Get a dashboard by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the dashboard to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncDashboard | None: returns the dashboard if a dashboard matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.get_dashboard_by_name(client, name='test')
            or  
            >>>     dashboard = await client.get_dashboard_by_name(name='test')
        """
        dashboards = await cls.get_dashboards(api, q=f"name = '{name}'", user_id=user_id)
        if dashboards and dashboards[0].name == name:
            return dashboards[0]
        else:
            return None


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the Dashboard

        Keyword Args:
            name (str): The name of the Dashboard.
            display_name (str): The display name of the Dashboard.
            description (str): The description of the Dashboard.
            settings (Dict): The settings of the Dashboard.
            thumbnail (str): The thumbnail of the Dashboard.

        Returns:
            Dict: The updated Dashboard data.

        Raises:
            ValidationError: If the Dashboard data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await dashboard.update(display_name="New Display Name")
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
        [async] Delete the dashboard.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await dashboard.delete()
        """        
        await super()._delete(self.endpoint)


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the dashboard.

        Returns:
            str: The thumbnail of the dashboard.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     dashboard.thumbnail
        """
        return super()._thumbnail()
    

    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the Dashboard with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to share the Dashboard with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await dashboard.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the Dashboard with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to unshare the Dashboard with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await dashboard.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the dashboard is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> async with AsyncGeoboxClient() as client:
            >>>     dashboard = await AsyncDashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await dashboard.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Dashboard':
        """
        Switch to sync version of the dashboard instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Dashboard: the sync instance of the dashboard.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.dashboard import AsyncDashboard
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     dashboard = await AsyncDashboard.get_dashboard(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_dashboard = dashboard.to_sync(client)
        """
        from ..dashboard import Dashboard

        return Dashboard(api=sync_client, uuid=self.uuid, data=self.data)