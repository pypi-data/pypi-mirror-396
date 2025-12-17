from typing import List, Dict, Optional, TYPE_CHECKING, Union

from .base import AsyncBase

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from ..api import GeoboxClient
    from ..workflow import Workflow


class AsyncWorkflow(AsyncBase):

    BASE_ENDPOINT = 'workflows/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str,
        data: Optional[Dict] = {}):
        """
        Initialize an async workflow instance. 

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the workflow.
            data (Dict): The data of the workflow.
        """
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    async def get_workflows(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncWorkflow'], int]:
        """
        [async] Get list of workflows with optional filtering

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
            shared (bool): Whether to return shared workflows. default is False.

        Returns:
            List[AsyncWorkflow] | int: A list of workflow instances or the total number of workflows.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflows = await AsyncWorkflow.get_workflows(client, q="name LIKE '%My workflow%'")
            or
            >>>     workflows = await client.get_workflows(q="name LIKE '%My workflow%'")
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
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncWorkflow(api, item['uuid'], item))
    

    @classmethod
    async def create_workflow(cls, 
        api: 'AsyncGeoboxClient', 
        name: str, 
        display_name: str = None, 
        description: str = None, 
        settings: Dict = {}, 
        thumbnail: str = None, 
        user_id: int = None) -> 'AsyncWorkflow':
        """
        [async] Create a new workflow.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the Workflow.
            display_name (str): The display name of the workflow.
            description (str): The description of the workflow.
            settings (Dict): The settings of the workflow.
            thumbnail (str): The thumbnail of the workflow.
            user_id (int): Specific user. privileges required.

        Returns:
            AsyncWorkflow: The newly created workflow instance.

        Raises:
            ValidationError: If the workflow data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.create_workflow(client, name="my_workflow")
            or
            >>>     workflow = await client.create_workflow(name="my_workflow")
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "settings": settings,
            "thumbnail": thumbnail,
            "user_id": user_id,
        }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncWorkflow(api, item['uuid'], item))

    
    @classmethod
    async def get_workflow(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncWorkflow':
        """
        [async] Get a workflow by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the workflow to get.
            user_id (int): Specific user. privileges required.

        Returns:
            AsyncWorkflow: The workflow object.

        Raises:
            NotFoundError: If the workflow with the specified UUID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>>     workflow = await client.get_workflow(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncWorkflow(api, item['uuid'], item))


    @classmethod
    async def get_workflow_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncWorkflow', None]:
        """
        [async] Get a workflow by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the workflow to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncWorkflow | None: returns the workflow if a workflow matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.get_workflow_by_name(client, name='test')
            or
            >>>     workflow = await client.get_workflow_by_name(name='test')
        """
        workflows = await cls.get_workflows(api, q=f"name = '{name}'", user_id=user_id)
        if workflows and workflows[0].name == name:
            return workflows[0]
        else:
            return None


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the workflow.

        Keyword Args:
            name (str): The name of the workflow.
            display_name (str): The display name of the workflow.
            description (str): The description of the workflow.
            settings (Dict): The settings of the workflow.
            thumbnail (str): The thumbnail of the workflow.

        Returns:
            Dict: The updated workflow data.

        Raises:
            ValidationError: If the workflow data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await workflow.update_workflow(display_name="New Display Name")
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
        [async] Delete the Workflow.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await workflow.delete()
        """
        await super()._delete(self.endpoint)


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the Workflow.

        Returns:
            str: The thumbnail of the Workflow.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     workflow.thumbnail
        """
        return super()._thumbnail()
    

    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the workflow with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to share the workflow with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await workflow.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the workflow with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to unshare the workflow with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await workflow.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the workflow is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[AsyncUser]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> async with AsyncGeoboxClient() as client:
            >>>     workflow = await AsyncWorkflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await workflow.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Workflow':
        """
        Switch to sync version of the workflow instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Workflow: the sync instance of the workflow.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.workflow import AsyncWorkflow
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     workflow = await AsyncWorkflow.get_workflow(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_workflow = workflow.to_sync(client)
        """
        from ..workflow import Workflow

        return Workflow(api=sync_client, uuid=self.uuid, data=self.data)