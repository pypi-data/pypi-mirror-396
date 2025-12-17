from urllib.parse import urlencode
from typing import Dict, List, Union, TYPE_CHECKING
from datetime import datetime

from .base import AsyncBase
from .user import AsyncUser
from .apikey import AsyncApiKey
from ..utils import clean_data
from ..enums import UsageScale, UsageParam

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from ..api import GeoboxClient
    from ..usage import Usage


class AsyncUsage(AsyncBase):

    BASE_ENDPOINT = 'usage/'

    def __init__(self,
        api: 'AsyncGeoboxClient',
        user: 'AsyncUser'):
        """
        Constructs the necessary attributes for the Usage object.

        Args:
            api (AsyncGeoboxClient): The API instance.
            user (User): the user usage object.
        """
        self.api = api
        self.user = user


    def __repr__(self) -> str:
        """
        Return a string representation of the Usage object.

        Returns:
            str: A string representation of the Usage object.
        """
        return f"AsyncUsage(user={self.user})"


    @classmethod
    async def get_api_usage(cls, 
        api: 'AsyncGeoboxClient', 
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
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
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
            >>> from geobox.aio.usage import AsyncUsage
            >>> async with AsyncGeoboxClient() as client:
            >>>     user = await client.get_user() # gets current user
            >>>     usage = await AsyncUsage.get_api_usage(client, 
            ...                                         resource=user, 
            ...                                         scale=UsageScale.Day, 
            ...                                         param=UsageParam.Calls, 
            ...                                         days_before_now=5)
            or  
            >>>     usage = await client.get_api_usage(resource=user, 
            ...                                         scale=UsageScale.Day, 
            ...                                         param=UsageParam.Calls, 
            ...                                         days_before_now=5)
        """
        if not(from_date and to_date) and not days_before_now:
            raise ValueError("one of days_before_now or from_date/to_date parameters must have value")

        params = {}
        if isinstance(resource, AsyncUser):
            params['eid'] = resource.user_id
        elif isinstance(resource, AsyncApiKey):
            params['eid'] = resource.key
        else:
            raise ValueError("resource must be a 'AsyncUser' or 'AsyncApikey' object")

        params = clean_data({
            **params,
            'scale': scale.value if scale else None,
            'param': param.value if param else None,
            'from_date': from_date.strftime("%Y-%m-%dT%H:%M:%S.%f") if from_date else None,
            'to_date': to_date.strftime("%Y-%m-%dT%H:%M:%S.%f") if to_date else None,
            'days_before_now': days_before_now,
            'limit': limit
        })
        query_strings = urlencode(params)
        endpoint = f"{cls.BASE_ENDPOINT}api?{query_strings}"

        return await api.get(endpoint)


    @classmethod
    async def get_process_usage(cls, 
        api: 'AsyncGeoboxClient',
        user_id: int = None, 
        from_date: datetime = None, 
        to_date: datetime = None, 
        days_before_now: int = None) -> float:
        """
        [async] Get process usage of a user in seconds

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
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
            >>> from geobox.aio.usage import AsyncUsage
            >>> async with AsyncGeoboxClient() as client:
            >>>     process_usage = await AsyncUsage.get_process_usage(client, days_before_now=5)
            or  
            >>>     process_usage = await client.get_process_usage(days_before_now=5)
        """
        if not(from_date and to_date) and not days_before_now:
            raise ValueError("one of days_before_now or from_date/to_date parameters must have value")

        params = clean_data({
            'user_id': user_id if user_id else None,
            'from_date': from_date.strftime("%Y-%m-%dT%H:%M:%S.%f") if from_date else None,
            'to_date': to_date.strftime("%Y-%m-%dT%H:%M:%S.%f") if to_date else None,
            'days_before_now': days_before_now
        })
        query_strings = urlencode(params)
        endpoint = f"{cls.BASE_ENDPOINT}process?{query_strings}"
        return await api.get(endpoint)


    @classmethod
    async def get_usage_summary(cls, api: 'AsyncGeoboxClient', user_id: int = None) -> Dict:
        """
        [async] Get the usage summary of a user

        Args:
            api (AsyncGeoboxClient): The API instance.
            user_id (int, optional): the id of the user. leave blank to get the current user report.

        Returns:
            Dict: the usage summary of the users

        Returns:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.usage import AsyncUsage
            >>> async with AsyncGeoboxClient() as client:
            >>>     usage_summary = await AsyncUsage.get_usage_summary(client)
            or  
            >>>     usage_summary = await client.get_usage_summary()
        """
        params = clean_data({
            'user_id': user_id if user_id else None
        })
        query_strings = urlencode(params)
        endpoint = f"{cls.BASE_ENDPOINT}summary?{query_strings}"
        return await api.get(endpoint)


    @classmethod
    async def update_usage(cls, api: 'AsyncGeoboxClient', user_id: int = None) -> Dict:
        """
        [async] Update usage of a user

        Args:
            api (AsyncGeoboxClient): The API instance.
            user_id (int, optional): the id of the user. leave blank to get the current user report.
            
        Returns:
            Dict: the updated data

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.usage import AsyncUsage
            >>> async with AsyncGeoboxClient() as client:
            >>>     await AsyncUsage.update_usage(client)
            or  
            >>>     await client.update_usage()
        """
        data = clean_data({
            'user_id': user_id if user_id else None
        })
        endpoint = f"{cls.BASE_ENDPOINT}update"
        return await api.post(endpoint, payload=data)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Usage':
        """
        Switch to sync version of the usage instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Usage: the sync instance of the usage.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.usage import AsyncUsage
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     user = await async_client.get_user()
            >>>     usage = await AsyncUsage.get_api_usage(async_client, 
            ...                                         resource=user, 
            ...                                         scale=UsageScale.Day, 
            ...                                         param=UsageParam.Calls, 
            ...                                         days_before_now=5)
            >>>     sync_usage = await usage.to_sync(client)
        """
        from ..usage import Usage

        user = self.user.to_sync(sync_client)
        return Usage(api=sync_client, user=user)