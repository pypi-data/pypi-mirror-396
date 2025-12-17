import time
import asyncio
from urllib.parse import urljoin
from typing import Optional, Dict, List, Optional, Union, TYPE_CHECKING
import logging

from .base import AsyncBase
from ..enums import TaskStatus

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .vectorlayer import AsyncVectorLayer
    from .raster import AsyncRaster
    from .model3d import AsyncModel
    from .file import AsyncFile
    from .tile3d import AsyncTile3d
    from ..api import GeoboxClient
    from ..task import Task

logger = logging.getLogger(__name__)


class AsyncTask(AsyncBase):

    BASE_ENDPOINT: str = 'tasks/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str, 
        data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Task object.

        Args:
            api (AsyncGeoboxClient): The API instance.
            uuid (str): The UUID of the task.
            data (Dict, optional): The task data.
        """
        super().__init__(api, uuid=uuid, data=data)
        self._data = data if isinstance(data, dict) else {}


    async def refresh_data(self) -> None:
        """
        [async] Updates the task data.
        """
        task = await self.get_task(self.api, self.uuid)
        self._data = task.data


    @property
    async def output_asset(self) -> Union['AsyncVectorLayer', 'AsyncRaster', 'AsyncModel', 'AsyncFile', 'AsyncTile3d', None]:
        """
        [async] output asset property

        Returns:
            AsyncVectorLayer | AsyncRaster | AsyncModel | AsyncFile | AsyncTile3d | None: if task type is publish, it returns the published layer

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await task.output_asset
        """
        if self.data.get('result', {}).get('layer_uuid'):
            return await self.api.get_vector(uuid=self.data['result']['layer_uuid'])

        elif self.data.get('result', {}).get('raster_uuid'):
            return await self.api.get_raster(uuid=self.data['result']['raster_uuid'])

        elif self.data.get('result', {}).get('model_uuid'):
            return await self.api.get_model(uuid=self.data['result']['model_uuid'])

        elif self.data.get('result', {}).get('file_uuid'):
            return await self.api.get_file(uuid=self.data['result']['file_uuid'])
        
        elif self.data.get('result', {}).get('3dtiles_uuid'):
            return await self.api.get_3dtile(uuid=self.data['result']['3dtiles_uuid'])

        else:
            return None


    @property
    def data(self) -> Dict:
        """
        Returns the task data.

        Returns:
            Dict: the task data as a dictionary
            
        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task.data
        """
        return self._data
    

    @data.setter
    def data(self, value: Dict) -> None:
        """
        Sets the task data.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task.data = {'name': 'test'}
        """
        self._data = value if isinstance(value, dict) else {}
    

    @property
    async def status(self) -> 'TaskStatus':
        """
        [async] Returns the status of the task. (auto refresh)

        Returns:
            TaskStatus: the status of the task(SUCCESS, FAILURE, ABORTED, PENDING, PROGRESS)
        
        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await task.status
        """
        await self.refresh_data()
        return TaskStatus(self._data.get('state'))


    @property
    def errors(self) -> Union[Dict, None]:
        """
        Get the task errors.

        Returns:
            Dict | None: if there are any errors

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task.errors    
        """
        result = self.data.get('result', {})
        if result.get('errors') or result.get('detail', {}).get('msg'):
            return result
        else: 
            return None


    @property
    async def progress(self) -> Union[int, None]:
        """
        [async] Returns the progress of the task.

        Returns:
            int | None: the progress of the task in percentage or None if the task is not running

        Example:
              >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await task.progress
        """
        endpoint = urljoin(self.endpoint, 'status/')
        response = await self.api.get(endpoint)
        
        current = response.get('current')
        total = response.get('total')
        if not total or not current:
            return None
        
        return int((current / total) * 100)

    
    async def _wait(self, timeout: Union[int, None] = None, interval: int = 1, progress_bar: bool = True) -> 'TaskStatus':
        start_time = time.time()
        last_progress = 0
        pbar = self._create_progress_bar() if progress_bar else None
        
        try:
            while True:
                self._check_timeout(start_time, timeout)
                status = await self.status
                
                if self._is_final_state(status):
                    await self._update_progress_bar(pbar, last_progress, status)
                    return status
                
                if pbar:
                    last_progress = await self._update_progress_bar(pbar, last_progress)
                
                await asyncio.sleep(interval)

        finally:
            if pbar:
                pbar.close()


    async def wait(self, timeout: Union[int, None] = None, interval: int = 1, progress_bar: bool = True, retry: int = 3) -> 'TaskStatus':
        """
        [async] Wait for the task to finish.
        
        Args:
            timeout (int, optional): Maximum time to wait in seconds.
            interval (int, optional): Time between status checks in seconds.
            progress_bar (bool, optional): Whether to show a progress bar. default: True
            retry (int, optional): Number of times to retry if waiting for the task fails. default is 3
            
        Returns:
            TaskStatus: the status of the task(SUCCESS, FAILURE, ABORTED, PENDING, PROGRESS)
            
        Raises:
            TimeoutError: If the task doesn't complete within timeout seconds.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await task.wait() # return the status of the task
        """
        last_exception = None

        for attempt in range(1, retry + 1):
            try:
                return await self._wait(timeout, interval, progress_bar)
            except Exception as e:
                last_exception = e
                logger.warning(f"[Retry {attempt}/{retry}] Task wait failed: {e}")
                time.sleep(interval)
        raise last_exception


    def _create_progress_bar(self) -> 'tqdm':
        """Creates a progress bar for the task."""
        try:
            from tqdm.auto import tqdm
        except ImportError:
            from .api import logger
            logger.warning("[tqdm] extra is required to show the progress bar. install with: pip insatll geobox[tqdm]")
            return None

        return tqdm(total=100, colour='green', desc=f"Task: {self.name}", unit="%", leave=True)


    def _check_timeout(self, start_time: float, timeout: Union[int, None]) -> None:
        """Checks if the task has exceeded the timeout period."""
        if timeout and time.time() - start_time > float(timeout):
            raise TimeoutError(f"Task {self.name} timed out after {timeout} seconds")


    def _is_final_state(self, status: 'TaskStatus') -> bool:
        """Checks if the task has reached a final state."""
        return status in [TaskStatus.FAILURE, TaskStatus.SUCCESS, TaskStatus.ABORTED]


    async def _update_progress_bar(self, pbar: Union['tqdm', None], last_progress: int, status: 'TaskStatus' = None) -> int:
        """
        [async] Updates the progress bar with current progress and returns the new last_progress.
        
        Args:
            pbar (tqdm | None): The progress bar to update
            last_progress (int): The last progress value
            status (TaskStatus, optional): The task status. If provided and SUCCESS, updates to 100%
            
        Returns:
            int: The new last_progress value
        """
        if not pbar:
            return last_progress
        
        if status == TaskStatus.SUCCESS:
            pbar.update(100 - last_progress)
            return 100
        
        current_progress = await self.progress
        if current_progress is not None:
            progress_diff = current_progress - last_progress
            if progress_diff > 0:
                pbar.update(progress_diff)
                return current_progress
        return last_progress


    async def abort(self) -> None:
        """
        [async] Aborts the task.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await task.abort()
        """
        endpoint = urljoin(self.endpoint, 'abort/')
        await self.api.post(endpoint)


    @classmethod
    async def get_tasks(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['Task'], int]:
        """
        [async] Get a list of tasks

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            
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
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     tasks = await AsyncTask.get_tasks(client)
            or  
            >>>     tasks = await client.get_tasks()
        """
        params = {
            'f': 'json',
            'state': kwargs.get('state').value if kwargs.get('state') else None,
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'search_fields': kwargs.get('search_fields'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip'),
            'limit': kwargs.get('limit'),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)
        }
        return await super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: AsyncTask(api, item['uuid'], item))
        


    @classmethod
    async def get_task(cls, api: 'AsyncGeoboxClient', uuid: str) -> 'AsyncTask':
        """
        [async] Gets a task.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the task.

        Returns:
            AsyncTask: The task object.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await AsyncTask.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     task = await client.get_task(uuid="12345678-1234-5678-1234-567812345678")
        """
        return await super()._get_detail(api, cls.BASE_ENDPOINT, uuid, factory_func=lambda api, item: AsyncTask(api, item['uuid'], item))


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Task':
        """
        Switch to sync version of the task instance to have access to the sync methods

        Args:
            sync_client (SyncGeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Task: the sync instance of the task.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.task import AsyncTask
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     task = await AsyncTask.get_task(async_client, uuid="12345678-1234-5678-1234-567812345678")
            or  
            >>>     task = await async_client.get_task(uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_task = task.to_sync(client)
        """
        from ..task import Task

        return Task(api=sync_client, uuid=self.uuid, data=self.data)