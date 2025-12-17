from typing import Dict, TYPE_CHECKING
from urllib.parse import urlencode

from ..enums import RoutingGeometryType, RoutingOverviewLevel
from ..utils import clean_data

if TYPE_CHECKING:
    from . import AsyncGeoboxClient

class AsyncRouting:

    BASE_ENDPOINT = 'routing/'

    @classmethod
    async def route(cls, api: 'AsyncGeoboxClient', stops: str, **kwargs) -> Dict:
        """
        Find best driving routes between coordinates and return results.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            stops (str): Comma-separated list of stop coordinates in the format lon,lat;lon,lat.

        Keyword Args:
            alternatives (bool): Whether to return alternative routes. Default value : False.
            steps (bool): Whether to include step-by-step navigation instructions. Default value : False.
            geometries (RoutingGeometryType): Format of the returned geometry.
            overview (RoutingOverviewLevel): Level of detail in the returned geometry.
            annotations (bool): Whether to include additional metadata like speed, weight, etc.

        Returns:
            Dict: the routing output

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.route import AsyncRouting
            >>> async with AsyncGeoboxClient() as client:
            >>>     route = await AsyncRouting.route(client,
            ...                             stops="53,33;56,36",
            ...                             alternatives=True,
            ...                             steps=True,
            ...                             geometries=RoutingGeometryType.geojson,
            ...                             overview=RoutingOverviewLevel.full,
            ...                             annotations=True)
            or  
            >>>     route = await client.route(stops="53,33;56,36",
            ...                             alternatives=True,
            ...                             steps=True,
            ...                             geometries=RoutingGeometryType.geojson,
            ...                             overview=RoutingOverviewLevel.full,
            ...                             annotations=True)
        """
        params = clean_data({
            'stops': stops,
            'alternatives': kwargs.get('alternatives'),
            'steps': kwargs.get('steps'),
            'geometries': kwargs.get('geometries').value if kwargs.get('geometries') else None,
            'overview': kwargs.get('overview').value if kwargs.get('geometries') else None,
            'annotaions': kwargs.get('annotations')
        })
        query_string = urlencode(params)
        endpoint = f"{cls.BASE_ENDPOINT}route?{query_string}"
        return await api.get(endpoint)
    
