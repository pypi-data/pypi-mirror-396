from typing import Optional, Dict, List, Union, TYPE_CHECKING

from .base import AsyncBase

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .user import AsyncUser
    from ..api import GeoboxClient
    from ..log import Log


class AsyncLog(AsyncBase):

    BASE_ENDPOINT = 'logs/'

    def __init__(self,
                api: 'AsyncGeoboxClient',
                log_id: int,
                data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Log object.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            log_id (int): The id of the log.
            data (Dict, optional): The data of the log.
        """
        super().__init__(api, data=data)
        self.log_id = log_id
        self.endpoint = f"{self.BASE_ENDPOINT}{self.log_id}"


    def __repr__(self) -> str:
        """
        Return a string representation of the Log object.

        Returns:
            str: A string representation of the Log object.
        """
        return f"AsyncLog(id={self.log_id}, activity_type={self.activity_type})"


    @classmethod
    async def get_logs(cls, api: 'AsyncGeoboxClient', **kwargs) -> List['AsyncLog']:
        """
        [async] Get a list of Logs

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

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
            >>> from geopox.aio.log import AsyncLog
            >>> async with AsyncGeoboxClient() as client:
            >>>     logs = await AsyncLog.get_logs(client)
            or  
            >>>     logs = await client.get_logs() 
        """ 
        params = {
            'search': kwargs.get('search'),
            'order_by': kwargs.get('order_by'),
            'skip': kwargs.get('skip'),
            'limit': kwargs.get('limit'),
            'user_id': kwargs.get('user_id'),
            'from_date': kwargs.get('from_date').strftime("%Y-%m-%dT%H:%M:%S.%f") if kwargs.get('from_date') else None,
            'to_date': kwargs.get('to_date').strftime("%Y-%m-%dT%H:%M:%S.%f") if kwargs.get('to_date') else None,
            'user_identity': kwargs.get('user_identity'),
            'activity_type': kwargs.get('activity_type')
        }
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncLog(api, item['id'], item))


    async def delete(self) -> None:
        """
        [async] Delete a log (privileges required)

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geopox.aio.log import AsyncLog
            >>> async with AsyncGeoboxClient() as client:
            >>>     log = await AsyncLog.get_logs(client)[0]
            >>>     await log.delete()
        """
        await super()._delete(self.endpoint)
        self.log_id = None


    @property
    async def user(self) -> Union['AsyncUser', None]:
        """
        [async] Get the owner user for the log

        Returns:
            User | None: if the log has owner user 

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geopox.aio.log import AsyncLog
            >>> async with AsyncGeoboxClient() as client:
            >>>     log = await AsyncLog.get_logs(client)[0]
            >>>     await log.user
        """
        return await self.api.get_user(self.owner_id)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Log':
        """
        Switch to sync version of the log instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Log: the sync instance of the log.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geopox.aio.log import AsyncLog
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     logs = await AsyncLog.get_logs(async_client)
            >>>     log = logs[0]
            >>>     sync_log = log.to_sync(client)
        """
        from ..log import Log

        return Log(api=sync_client, log_id=self.log_id, data=self.data)