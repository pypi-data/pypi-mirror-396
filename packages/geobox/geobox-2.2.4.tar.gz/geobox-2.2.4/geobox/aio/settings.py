from typing import List, Dict, Optional, TYPE_CHECKING
from urllib.parse import urljoin, urlencode

from .base import AsyncBase
from ..utils import clean_data
from ..enums import MaxLogPolicy, InvalidDataPolicy, LoginFailurePolicy, MaxConcurrentSessionPolicy

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from ..api import GeoboxClient
    from ..settings import SystemSettings


class AsyncSystemSettings(AsyncBase):

    BASE_ENDPOINT = 'settings/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        data: Optional[Dict] = {}):
        """
        Initialize a System Settings instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            data (Dict, optional): The data of the Setting.
        """
        super().__init__(api, data=data)


    @property
    def max_log_policy(self) -> 'MaxLogPolicy':
        """
        Get max log policy

        Returns:
            MaxLogPolicy: max log policy
        """
        return MaxLogPolicy(self.data.get('max_log_policy'))
    

    @property
    def invalid_data_policy(self) -> 'InvalidDataPolicy':
        """
        Get invalid data policy

        Returns:
            InvalidDataPolicy: invalid data policy
        """
        return InvalidDataPolicy(self.data.get('invalid_data_policy'))
    

    @property
    def login_failure_policy(self) -> 'LoginFailurePolicy':
        """
        Get login failure policy

        Returns:
            LoginFailurePolicy: login failure policy
        """
        return LoginFailurePolicy(self.data.get('login_failure_policy'))
    

    @property
    def max_concurrent_session_policy(self) -> 'MaxConcurrentSessionPolicy':
        """
        Get max concurrent sessions

        Returns:
            MaxConcurrentSessionPolicy: max concurrent sessions
        """
        return MaxConcurrentSessionPolicy(self.data.get('max_concurrent_session_policy'))


    def __repr__(self) -> str:
        """
        Return a string representation of the system setting instance.

        Returns:
            str: A string representation of the system setting instance.
        """
        return "AsyncSystemSettings()"


    @classmethod
    async def get_system_settings(cls, api: 'AsyncGeoboxClient') -> 'AsyncSystemSettings':
        """
        [async] Get System Settings object (Permission Required).

        Args: 
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

        Returns:
            AsyncSystemSetting: the system settings object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.setting import AsyncSystemSettings
            >>> async with AsyncGeoboxClient() as client:
            >>>     setting = await AsyncSystemSettings.get_system_settings(client)
            or  
            >>>     setting = await client.get_system_settings()
        """
        params = clean_data({
            'f': 'json'
        })
        query_string = urlencode(params)
        endpoint = urljoin(cls.BASE_ENDPOINT, f"?{query_string}")
        response = await api.get(endpoint)
        return AsyncSystemSettings(api, response)


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the system settings.

        Keyword Args:
            brand_name (str)
            brand_website (str)
            max_log (int)
            max_log_policy (MaxLogPolicy)
            users_can_view_their_own_logs (bool)
            max_upload_file_size (int)
            invalid_data_policy (InvalidDataPolicy)
            max_login_attempts (int)
            login_failure_policy (LoginFailurePolicy)
            login_attempts_duration (int)
            min_password_length (int)
            max_concurrent_session (int)
            max_concurrent_session_policy (MaxConcurrentSessionPolicy)
            session_timeout (int)
            allowed_ip_addresses (Dict)
            blocked_ip_addresses (Dict)

        Returns:
            Dict: The updated system settings data.

        Raises:
            ValidationError: If the system settings data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.setting import AsyncSystemSettings
            >>> async with AsyncGeoboxClient() as client:
            >>>     settings = await AsyncSystemSetting.get_system_settings(client)
            or  
            >>>     settings = await client.get_system_settings()
            >>>     await settings.update(max_log=100000)
        """
        data = {
            "brand_name": kwargs.get('brand_name'),
            "brand_website": kwargs.get('brand_website'),
            "max_log": kwargs.get('max_log'),
            "max_log_policy": kwargs.get('max_log_policy').value if kwargs.get('max_log_policy') else None,
            "max_upload_file_size": kwargs.get('max_upload_file_size'),
            "invalid_data_policy": kwargs.get('invalid_data_policy').value if kwargs.get('invalid_data_policy') else None,
            "max_login_attempts": kwargs.get('max_login_attempts'),
            "login_failure_policy": kwargs.get('login_failure_policy').value if kwargs.get('login_failure_policy') else None,
            "login_attempts_duration": kwargs.get('login_attempts_duration'),
            "min_password_length": kwargs.get('min_password_length'),
            "max_concurrent_session": kwargs.get('max_concurrent_session'),
            "max_concurrent_session_policy": kwargs.get('max_concurrent_session_policy').value if kwargs.get('max_concurrent_session_policy') else None,
            "session_timeout": kwargs.get('session_timeout'),
            "allowed_ip_addresses": kwargs.get('allowed_ip_addresses'),
            "blocked_ip_addresses": kwargs.get('blocked_ip_addresses'),
            
        }
        return await super()._update(self.BASE_ENDPOINT, data)


    def to_sync(self, sync_client: 'GeoboxClient') -> 'SystemSettings':
        """
        Switch to sync version of the system settings instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            SystemSettings: the sync instance of the system settings.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.setting import AsyncSystemSettings
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     settings = await AsyncSystemSetting.get_system_settings(async_client)
            or  
            >>>     settings = await async_client.get_system_settings()
            >>>     sync_settings = settings.to_sync(client)
        """
        from ..task import Task as SyncTask

        return SyncTask(api=sync_client, uuid=self.uuid, data=self.data)