from urllib.parse import urljoin
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from .base import AsyncBase
from ..enums import FeatureType

if TYPE_CHECKING:
    from .vectorlayer import VectorLayer
    from ..api import GeoboxClient
    from ..feature import Feature


class AsyncFeature(AsyncBase):

    BASE_SRID = 3857

    def __init__(self, 
        layer: 'VectorLayer', 
        srid: Optional[int] = 3857,
        data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Feature object.

        Args:
            layer (VectorLayer): The vector layer this feature belongs to
            srid (int, optional): The Spatial Reference System Identifier (default is 3857)
            data (Dict, optional): The feature data contains the feature geometry and properties
        """
        super().__init__(api=layer.api)
        self.layer = layer
        self._srid = srid
        self.data = data or {
            "type": "Feature",
            "geometry": {},
            "properties": {}
        }
        self.original_geometry = self.data.get('geometry')
        self.endpoint = urljoin(layer.endpoint, f'features/{self.data.get("id")}/') if self.data.get('id') else None


    def __dir__(self) -> List[str]:
        """
        Return a list of available attributes for the Feature object.
        
        This method extends the default dir() behavior to include:
        - All keys from the feature data dictionary
        - All keys from the geometry dictionary
        - All keys from the properties dictionary
        
        This allows for better IDE autocompletion and introspection of feature attributes.
        
        Returns:
            list: A list of attribute names available on this Feature object.
        """
        return super().__dir__() + list(self.data.keys()) + list(self.data.get('geometry').keys()) + list(self.data.get('properties').keys())


    def __repr__(self) -> str:
        """
        Return a string representation of the Feature object.

        Returns:
            str: A string representation of the Feature object.
        """
        feature_id = getattr(self, "id", "-1")
        return f"AsyncFeature(id={feature_id}, type={self.feature_type})"
    

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the resource.

        Args:
            name (str): The name of the attribute
        """
        if name in self.data:
            return self.data.get(name)
        # elif name in self.data['geometry']:
        #     return self.data['geometry'].get(name)
        elif name in self.data['properties']:
            return self.data['properties'].get(name)
        
        raise AttributeError(f"Feature has no attribute {name}")


    @property
    def srid(self) -> int:
        """
        Get the Spatial Reference System Identifier (SRID) of the feature.

        Returns:
            int: The SRID of the feature.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     feature.srid  # 3857
        """
        return self._srid
    

    @property
    def feature_type(self) -> 'FeatureType':
        """
        Get the type of the feature.

        Returns:
            FeatureType: The type of the feature.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     feature.feature_type
        """
        return FeatureType(self.data.get('geometry').get('type')) if self.data.get('geometry') else None
    

    @property
    def coordinates(self) -> List[float]:
        """
        Get the coordinates of the ferepoature.

        Returns:
            list: The coordinates of the feature.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     feature.coordinates
        """
        return self.data.get('geometry').get('coordinates') if self.data.get('geometry') else None
    

    @coordinates.setter
    def coordinates(self, value: List[float]) -> None:
        """
        Set the coordinates of the feature.

        Args:
            value (list): The coordinates to set.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     feature.coordinates = [10, 20]
        """
        self.data['geometry']['coordinates'] = value
    

    @property
    async def length(self) -> float:
        """
        [async] Returns the length of thefeature geometry (geometry package extra is required!)

        Returns:
            float: the length of thefeature geometry

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     await feature.length
        """
        try:
            return self.geom_length
        except AttributeError:
            endpoint = f'{self.endpoint}length'
            return await self.api.get(endpoint)


    @property
    async def area(self) -> float:
        """
        [async] Returns the area of thefeature geometry (geometry package extra is required!)

        Returns:
            float: the area of thefeature geometry

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     await feature.area
        """
        try:
            return self.geom_area
        except AttributeError:
            endpoint = f'{self.endpoint}area'
            return await self.api.get(endpoint)
    
    
    async def save(self) -> None:
        """
        [async] Save the feature. Creates a new feature if feature_id is None, updates existing feature otherwise.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     feature.properties['name'] = 'New Name'
            >>>     await feature.save()
        """
        data = self.data.copy()
        srid = self.srid

        try:
            if self.id:
                await self.update(self.data)

        except AttributeError:
            if self.srid != self.BASE_SRID:
                self = self.transform(self.BASE_SRID)
            endpoint = urljoin(self.layer.endpoint, 'features/')
            request_data = self.data.copy()
            response = await self.layer.api.post(endpoint, request_data)
            self.endpoint = urljoin(self.layer.endpoint, f'features/{response["id"]}/')        
            self.data.update(response)

        self.data['geometry'] = data['geometry']
        self._srid = srid


    async def delete(self) -> None:
        """
        [async] Delete the feature.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     await feature.delete()
        """
        await super()._delete(self.endpoint)


    async def update(self, geojson: Dict) -> Dict:
        """
        [async] Update the feature data property.

        Args:
            geojson (Dict): The GeoJSON data for the feature

        Returns:
            Dict: The response from the API.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     geojson = {
            ...         "geometry": {
            ...             "type": "Point",
            ...             "coordinates": [10, 20]
            ...         }
            ...     }   
            >>>     await feature.update(geojson)
        """
        self.data = geojson
        data = self.data.copy()
        srid = self.srid

        if self.srid != self.BASE_SRID:
            self = self.transform(self.BASE_SRID)

        await super()._update(self.endpoint, self.data, clean=False)
        self.data['geometry'] = data['geometry']
        self._srid = srid
        return self.data
    

    @classmethod
    async def create_feature(cls, layer: 'VectorLayer', geojson: Dict, srid: int = 3857) -> 'AsyncFeature':
        """
        [async] Create a new feature in the vector layer.

        Args:
            layer (VectorLayer): The vector layer to create the feature in
            geojson (Dict): The GeoJSON data for the feature
            srid (int, optional): the feature srid. default: 3857

        Returns:
            AsyncFeature: The created feature instance

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     geojson = {
            ...        "type": "Feature",
            ...        "geometry": {"type": "Point", "coordinates": [10, 20]},
            ...        "properties": {"name": "My Point"}
            ...     }
            >>>     feature = await Feature.create_feature(layer, geojson)
        """
        feature = AsyncFeature(layer, srid=srid, data=geojson)
        data = feature.data.copy()
        srid = feature.srid

        if feature.srid != feature.BASE_SRID:
            feature = feature.transform(feature.BASE_SRID)

        endpoint = urljoin(layer.endpoint, 'features/')
        
        feature = await cls._create(layer.api, endpoint, feature.data, factory_func=lambda api, item: AsyncFeature(layer, data=item))
        feature.data['geometry'] = data['geometry']
        feature._srid = srid
        return feature


    @classmethod
    async def get_feature(cls, layer: 'VectorLayer', feature_id: int, user_id: int = None) -> 'AsyncFeature':
        """
        [async] Get a feature by its ID.

        Args:
            layer (VectorLayer): The vector layer the feature belongs to
            feature_id (int): The ID of the feature
            user_id (int): specific user. privileges required.

        Returns:
            AsyncFeature: The retrieved feature instance

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.feature import AsyncFeature
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await AsyncFeature.get_feature(layer, feature_id=1)
        """
        param = {
            'f': 'json',
            'user_id': user_id
        }
        endpoint = urljoin(layer.endpoint, f'features/')
        return await cls._get_detail(layer.api, endpoint, uuid=feature_id, params=param, factory_func=lambda api, item: AsyncFeature(layer, data=item))


    @property
    def geometry(self) -> 'BaseGeometry':
        """
        Get the feature geometry as a Shapely geometry object.

        Returns:
            shapely.geometry.BaseGeometry: The Shapely geometry object representing the feature's geometry

        Raises:
            ValueError: If the geometry is not a dictionary
            ValueError: If the geometry type is not present in the feature data
            ValueError: If the geometry coordinates are not present in the feature data
            ImportError: If shapely is not installed

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     feature.geometry
        """
        try:
            from shapely.geometry import shape
        except ImportError:
            raise ImportError(
                "The 'geometry' extra is required for this function. "
                "Install it with: pip install geobox[geometry]"
            )
        
        if not self.data.get('geometry'):
            raise ValueError("Geometry is not present in the feature data")
        
        elif not isinstance(self.data['geometry'], dict):
            raise ValueError("Geometry is not a dictionary")
        
        elif not self.data['geometry'].get('type'):
            raise ValueError("Geometry type is not present in the feature data")
        
        elif not self.data['geometry'].get('coordinates'):
            raise ValueError("Geometry coordinates are not present in the feature data")
        
        else:
            return shape(self.data['geometry'])
    

    @geometry.setter
    def geometry(self, value: object) -> None:
        """
        Set the feature geometry.

        Args:
            value (object): The geometry to set.

        Raises:
            ValueError: If geometry type is not supported
            ValueError: If the geometry has a different type than the layer type
            ImportError: If shapely is not installed

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from shapely.affinity import translate
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1)
            >>>     geom = feature.geometry
            >>>     geom = translate(geom, 3.0, 0.5) # example change applied to the feature's geometry
            >>>     feature.geometry = geom
            >>>     await feature.save()
        """
        try:
            from shapely.geometry import mapping, Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
        except ImportError:
            raise ImportError(
                "The 'geometry' extra is required for this function. "
                "Install it with: pip install geobox[geometry]"
            )
        
        if not isinstance(value, (Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon)):
            raise ValueError("Geometry must be a Shapely geometry object")
        
        elif self.feature_type and value.geom_type != self.feature_type.value:
            raise ValueError("Geometry must have the same type as the layer type")
        
        else:
            self.data['geometry'] = mapping(value)

        
    def transform(self, out_srid: int) -> 'AsyncFeature':
        """
        Transform the feature geometry to a new SRID.

        Args:
            out_srid (int): The target SRID to transform the geometry to (e.g., 4326 for WGS84, 3857 for Web Mercator)

        Returns:
            AsyncFeature: A new Feature instance with transformed geometry.

        Raises:
            ValueError: If the feature has no geometry or if the transformation fails.
            ImportError: If pyproj is not installed.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1, srid=3857)
            >>>     # Transform from Web Mercator (3857) to WGS84 (4326)
            >>>     transformed = feature.transform(out_srid=4326)
            >>>     transformed.srid  # 4326
        """
        try:
            from pyproj import Transformer
            from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, mapping
        except ImportError:
            raise ImportError(
                "The 'geometry' extra is required for this function. "
                "Install it with: pip install geobox[geometry]"
            )

        if not self.data or not self.data.get('geometry'):
            raise ValueError("Feature geometry is required for transformation")

        # Get the current SRID from the feature or default to 3857 (Web Mercator)
        current_srid = self.srid or 3857

        # Create transformer
        transformer = Transformer.from_crs(current_srid, out_srid, always_xy=True)

        # Get the geometry
        geom = self.geometry

        # Transform coordinates based on geometry type
        if geom.geom_type == 'Point':
            x, y = geom.x, geom.y
            new_x, new_y = transformer.transform(x, y)
            new_geom = Point(new_x, new_y)
        elif geom.geom_type == 'LineString':
            coords = list(geom.coords)
            new_coords = [transformer.transform(x, y) for x, y in coords]
            new_geom = LineString(new_coords)
        elif geom.geom_type == 'Polygon':
            exterior = [transformer.transform(x, y) for x, y in geom.exterior.coords]
            interiors = [[transformer.transform(x, y) for x, y in interior.coords] for interior in geom.interiors]
            new_geom = Polygon(exterior, holes=interiors)
        elif geom.geom_type == 'MultiPoint':
            new_geoms = [Point(transformer.transform(point.x, point.y)) for point in geom.geoms]
            new_geom = MultiPoint(new_geoms)
        elif geom.geom_type == 'MultiLineString':
            new_geoms = [LineString([transformer.transform(x, y) for x, y in line.coords]) for line in geom.geoms]
            new_geom = MultiLineString(new_geoms)
        elif geom.geom_type == 'MultiPolygon':
            new_geoms = []
            for poly in geom.geoms:
                exterior = [transformer.transform(x, y) for x, y in poly.exterior.coords]
                interiors = [[transformer.transform(x, y) for x, y in interior.coords] for interior in poly.interiors]
                new_geoms.append(Polygon(exterior, holes=interiors))
            new_geom = MultiPolygon(new_geoms)

        # update the feature data
        self.data['geometry'] = mapping(new_geom)
        self._srid = out_srid

        return self


    def to_sync(self, sync_client: 'GeoboxClient') -> 'Feature':
        """
        [async] Switch to sync version of the feature instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            Feature: the sync instance of the feature.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     layer = await async_client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await layer.get_feature(id=1, srid=3857)
            >>>     sync_feature = feature.to_sync(client)
        """
        from ..feature import Feature

        sync_layer = self.layer.to_sync(sync_client=sync_client)
        return Feature(layer=sync_layer, srid=self.srid, data=self.data)