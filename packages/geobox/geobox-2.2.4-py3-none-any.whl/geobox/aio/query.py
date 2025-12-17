from urllib.parse import urljoin
from typing import Dict, List, TYPE_CHECKING, Union

from ..utils import clean_data
from .base import AsyncBase
from .task import AsyncTask
from ..enums import QueryResultType, QueryGeometryType, QueryParamType

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from ..api import GeoboxClient
    from ..query import Query


class AsyncQuery(AsyncBase):

    BASE_ENDPOINT: str = 'queries/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str = None, 
        data: Dict = {}):
        """
        Constructs all the necessary attributes for the Query object.

        Args:
            api (AsyncGeoboxClient): The API instance.
            uuid (str): The UUID of the query.
            data (dict, optional): The data of the query.
        """
        self.result = {}
        self._system_query = False
        super().__init__(api, uuid=uuid, data=data)


    def _check_access(self) -> None:
        """
        Check if the query is a system query.

        Returns:
            None

        Raises:
            PermissionError: If the query is a read-only system query.
        """
        if self._system_query:
            raise PermissionError("Cannot modify system queries - they are read-only")


    @property
    def sql(self) -> str:
        """
        Get the SQL of the query.
        
        Returns:
            str: The SQL of the query.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     query.sql
            'SELECT * FROM some_layer'
        """
        return self.data['sql']
    

    @sql.setter
    def sql(self, value: str) -> None:
        """
        Set the SQL of the query.

        Args:
            value (str): The SQL of the query.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     query.sql = 'SELECT * FROM some_layer'
            >>>     await query.save()
        """
        self.data['sql'] = value


    @property
    def params(self) -> List[Dict]:
        """
        Get the parameters of the query.

        Returns:
            List[Dict]: The parameters of the query.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     query.params
            [{'name': 'layer', 'value': '12345678-1234-5678-1234-567812345678', 'type': 'Layer'}]
        """
        if not isinstance(self.data.get('params'), list):
            self.data['params'] = []

        return self.data['params']


    @params.setter
    def params(self, value: Dict) -> None:
        """
        Set the parameters of the query.

        Args:
            value (Dict): The parameters of the query.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     query.params = [{'name': 'layer', 'value': '12345678-1234-5678-1234-567812345678', 'type': 'Layer'}]
            >>>     await query.save()
        """
        if not isinstance(self.data.get('params'), list):
            self.data['params'] = []
        
        self.data['params'] = value


    @classmethod
    async def get_queries(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncQuery'], int]:
        """
        [async] Get Queries

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

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
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     queries = await AsyncQuery.get_queries(client)
            or  
            >>>     queries = await client.get_queries()
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'search_field': kwargs.get('search_field'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)
        }
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncQuery(api, item['uuid'], item))


    @classmethod
    async def create_query(cls, api: 'AsyncGeoboxClient', name: str, display_name: str = None, description:str = None, sql: str = None, params: List = None) -> 'AsyncQuery':
        """
        [async] Creates a new query.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): The name of the query.
            display_name (str, optional): The display name of the query.
            description (str, optional): The description of the query.
            sql (str, optional): The SQL statement for the query.
            params (list, optional): The parameters for the SQL statement.

        Returns:
            AsyncQuery: The created query instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.create_query(client, name='query_name', display_name='Query Name', sql='SELECT * FROM some_layer')
            or  
            >>>     query = await client.create_query(name='query_name', display_name='Query Name', sql='SELECT * FROM some_layer')
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "sql": sql,
            "params": params
        }
        return await super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: AsyncQuery(api, item['uuid'], item))


    @classmethod
    async def get_query(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncQuery':
        """
        [async] Retrieves a query by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the query.
            user_id (int, optional): specific user ID. privileges required.

        Returns:
            AsyncQuery: The retrieved query instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     query = await client.get_query(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: AsyncQuery(api, item['uuid'], item))


    @classmethod
    async def get_query_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncQuery', None]:
        """
        [async] Get a query by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the query to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncQuery | None: returns the query if a query matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query_by_name(client, name='test')
            or  
            >>>     query = await client.get_query_by_name(name='test')
        """
        queries = await cls.get_queries(api, q=f"name = '{name}'", user_id=user_id)
        if queries and queries[0].name == name:
            return queries[0]
        else:
            return None


    @classmethod
    async def get_system_queries(cls, api: 'AsyncGeoboxClient', **kwargs) -> List['AsyncQuery']:
        """
        [async] Returns the system queries as a list of Query objects.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

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
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     queries = await AsyncQuery.get_system_queries(client)
            or  
            >>>     queries = await client.get_system_queries()
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'search_fields': kwargs.get('search_fields'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 100),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)            
        }
        endpoint = urljoin(cls.BASE_ENDPOINT, 'systemQueries/')
        def factory_func(api, item):
            query = AsyncQuery(api, item['uuid'], item)
            query._system_query = True
            return query
            
        return await super()._get_list(api, endpoint, params, factory_func=factory_func)

    
    def add_param(self, name: str, value: str, type: 'QueryParamType', default_value: str = None, Domain: Dict = None) -> None:
        """
        Add a parameter to the query parameters.
        
        Args:
            name (str): The name of the parameter.
            value (str): The value of the parameter.
            type (str): The type of the parameter (default: 'Layer').
            default_value (str, optional): The default value for the parameter.
            Domain (Dict, optional): Domain information for the parameter.
            
        Returns:
            None
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     query = await client.get_query(uuid="12345678-1234-5678-1234-567812345678")
            >>>     query.add_param(name='param_name', value='param_value', type=QueryParamType.LAYER)
            >>>     await query.save()
        """
        self.params.append({
            'name': name,
            'value': value,
            'type': type.value,
            'default_value': default_value,
            'Domain': Domain
        })


    def remove_param(self, name: str) -> None:
        """
        Remove a parameter from the query parameters by name.
        
        Args:
            name (str): The name of the parameter to remove.
            
        Returns:
            None
            
        Raises:
            ValueError: If the parameter is not found in query parameters.
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     query = await client.get_query(uuid="12345678-1234-5678-1234-567812345678")
            >>>     query.remove_param(name='param_name')
            >>>     await quary.save()
        """
        for i, param in enumerate(self.params):
            if param.get('name') == name:
                self.params.pop(i)
                return
        
        raise ValueError(f"Parameter with name '{name}' not found in query parameters")


    async def execute(self, 
                f: str = "json",
                result_type: QueryResultType = QueryResultType.both, 
                return_count: bool = None,
                out_srid: int = None, 
                quant_factor: int = 1000000, 
                bbox_srid: int = None, 
                skip: int = None, 
                limit: int = None,
                skip_geometry: bool = False) -> Union[Dict, int]:
        """
        [async] Executes a query with the given SQL statement and parameters.

        Args:
            f (str): the output format of the executed query. options are: json, topojson. default is json.
            result_type (QueryResultType, optional): The type of result to return (default is "both").
            return_count (bool, optional): Whether to return the count of results.
            out_srid (int, optional): The output spatial reference ID.
            quant_factor (int, optional): The quantization factor (default is 1000000).
            bbox_srid (int, optional): The bounding box spatial reference ID.
            skip (int, optional): The number of results to skip.
            limit (int, optional): The maximum number of results to return.
            skip_geometry (bool): Whether to skip the geometry part of the features or not. default is False.

        Returns:
            Dict | int: The result of the query execution or the count number of the result

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     query = await client.get_query(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await query.execute(f='json')
        """
        if not self.sql:
            raise ValueError('"sql" parameter is required for this action!') 
        if not self.params:
            raise ValueError('"params" parameter is required for this action!')

        data = clean_data({
            "f": f if f in ['json', 'topojson'] else None,
            "sql": self.sql,
            "params": self.params,
            "result_type": result_type.value,
            "return_count": return_count,
            "out_srid": out_srid,
            "quant_factor": quant_factor,
            "bbox_srid": bbox_srid,
            "skip": skip,
            "limit": limit,
            "skip_geometry": skip_geometry
        })

        endpoint = urljoin(self.BASE_ENDPOINT, 'exec/')
        self.result = await self.api.post(endpoint, data)
        return self.result


    async def update(self, **kwargs) -> Dict:
        """
        [async] Updates the query with new data.

        Keyword Args:
            name (str): The new name of the query.
            display_name (str): The new display name of the query.
            sql (str): The new SQL statement for the query.
            params (list): The new parameters for the SQL statement.

        Returns:
            Dict: The updated query data.
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     query = await client.get_query(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await query.update(name='new_name')
        """
        self._check_access()
            
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),
            "sql": kwargs.get('sql'),
            "params": kwargs.get('params')
        }
        await super()._update(self.endpoint, data)


    async def save(self) -> None:
        """
        [async] Save the query. Creates a new query if query uuid is None, updates existing query otherwise.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await query.save()
        """
        self.params = [item for item in self.params if item.get('value')]

        try:
            if self.__getattr__('uuid'):
                await self.update(name=self.data['name'], display_name=self.data['display_name'], sql=self.sql, params=self.params)
        except AttributeError:
            response = await self.api.post(self.BASE_ENDPOINT, self.data)
            self.endpoint = urljoin(self.BASE_ENDPOINT, f'{response["uuid"]}/')        
            self.data.update(response)


    async def delete(self) -> str:
        """
        [async] Deletes a query.

        Returns:
            str: The response from the API.
            
        Raises:
            PermissionError: If the query is a read-only system query

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await query.delete()
        """
        self._check_access()
        await super()._delete(self.endpoint)


    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the query with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to share the query with.

        Returns:
            None
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search="John")
            >>>     await query.share(users=users)
        """
        self._check_access()
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the query with specified users.

        Args:
            users (List[AsyncUser]): The list of user objects to unshare the query with.

        Returns:
            None
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search="John")
            >>>     await query.unshare(users=users)
        """
        self._check_access()
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the query is shared with.

        Args:
            search (str, optional): the search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[AsyncUser]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search="John")
            >>>     await query.get_shared_users(search='John', skip=0, limit=10)
        """
        self._check_access()
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    @property
    def thumbnail(self) -> str:
        """
        Retrieves the thumbnail URL for the query.            

        Returns:
            str: The thumbnail URL.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     query.thumbnail
        """
        return super()._thumbnail()


    async def save_as_layer(self, layer_name: str, layer_type: 'QueryGeometryType' = None) -> 'AsyncTask':
        """
        [async] Saves the query as a new layer.

        Args:
            layer_name (str): The name of the new layer.
            layer_type (QueryGeometryType, optional): The type of the new layer.

        Returns:
            Task: The response task object.
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> async with AsyncGeoboxClient() as client:
            >>>     query = await AsyncQuery.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await query.save_as_layer(layer_name='test')
        """
        params = [{
            "name": item.get('name'),
            "type": item.get('type'),
            "value": item.get('default_value') if not item.get('value') else item.get('value')
        } for item in self.params]

        data = clean_data({
            "sql": self.sql,
            "params": params,
            "layer_name": layer_name,
            "layer_type": layer_type.value if layer_type else None
        })

        endpoint = urljoin(self.BASE_ENDPOINT, 'saveAsLayer/')
        response = await self.api.post(endpoint, data)
        task = await AsyncTask.get_task(self.api, response.get('task_id'))
        return task


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Query':
        """
        Switch to sync version of the query instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Query: the sync instance of the query.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.query import AsyncQuery
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     query = await AsyncQuery.get_query(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_query = query.to_sync(client)
        """
        from ..query import Query

        return Query(api=sync_client, uuid=self.uuid, data=self.data)