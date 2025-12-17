from typing import List, Optional, Dict, List, Union, TYPE_CHECKING

from .vectorlayer import AsyncVectorLayer, LayerType, FileOutputFormat
from .feature import AsyncFeature

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .field import AsyncField
    from .user import AsyncUser
    from .task import AsyncTask
    from .file import AsyncFile
    from .attachment import AsyncAttachment
    from ..enums import InputGeomType
    from ..api import GeoboxClient
    from ..view import VectorLayerView


class AsyncVectorLayerView(AsyncVectorLayer):

    BASE_ENDPOINT = 'vectorLayerViews/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        uuid: str,
        layer_type: 'LayerType', 
        data: Optional[Dict] = {}) -> None:
        """
        Initialize an async VectorLayerView instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the vector layer view.
            layer_type (LayerType): The type of the vector layer view.
            data (Dict, optional): The data of the vector layer view.
        """
        super().__init__(api, uuid, layer_type, data)


    def __repr__(self) -> str:
        """
        Return a string representation of the AsyncVectorLayerView instance.

        Returns:
            str: A string representation of the AsyncVectorLayerView instance.
        """
        return f"AsyncVectorLayerView(uuid={self.uuid}, name={self.name}, layer_type={self.layer_type})"
    

    @property
    def vector_layer(self) -> 'AsyncVectorLayer':
        """
        Get the vector layer.

        Returns:
            VectorLayer: The vector layer.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid='e21e085a-8d30-407d-a740-ca9be9122c42')
            >>>     view.vector_layer
        """
        return AsyncVectorLayer(self.api, self.data['vector_layer']['uuid'], LayerType(self.data['vector_layer']['layer_type']), self.data['vector_layer'])


    @classmethod
    async def get_views(cls, api: 'AsyncGeoboxClient', **kwargs) -> Union[List['AsyncVectorLayerView'], int]:
        """
        [async] Get vector layer views.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.

        Keyword Args:
            layer_id(int): The id of the source vector layer.
            include_settings(bool): Whether to include the settings of the layer. default is False.
            q(str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search(str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields(str): Comma separated list of fields for searching.
            order_by(str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count(bool): Whether to return the count of the layer views. default is False.
            skip(int): The number of layer views to skip. minimum is 0.
            limit(int): The maximum number of layer views to return. minimum is 1. default is 10.
            user_id(int): Specific user. privileges required.
            shared(bool): Whether to return shared views. default is False.

        Returns:
            list[AsyncVectorLayerView] | int: A list of AsyncVectorLayerView instances or the layer views count if return_count is True.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     views = await AsyncVectorLayerView.get_views(client,
            ...                                              layer_id=1,
            ...                                              include_settings=True,
            ...                                              search="test",
            ...                                              search_fields="name",
            ...                                              order_by="name A",
            ...                                              return_count=False,
            ...                                              skip=0,
            ...                                              limit=10,
            ...                                              shared=True)
            or
            >>>     views = await client.get_views(layer_id=1,
            ...                                     include_settings=True,
            ...                                     search="test",
            ...                                     search_fields="name",
            ...                                     order_by="name A",
            ...                                     return_count=False,
            ...                                     skip=0,
            ...                                     limit=10,
            ...                                     shared=True)
        """
        params = {
            'f': 'json',
            'include_settings': kwargs.get('include_settings', False),
            'temporary': kwargs.get('temporary', False),
            'q': kwargs.get('q', None),
            'search': kwargs.get('search', None),
            'search_fields': kwargs.get('search_fields', None),
            'order_by': kwargs.get('order_by', None),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id', None),
            'shared': kwargs.get('shared', False)
        }
        return await super()._get_list(api=api, 
            endpoint=cls.BASE_ENDPOINT,
            params=params, 
            factory_func=lambda api, item: AsyncVectorLayerView(api, item['uuid'], LayerType(item['layer_type']), item))


    @classmethod
    async def get_views_by_ids(cls, api: 'AsyncGeoboxClient', ids: List[int], user_id: int = None, include_settings: bool = False) -> List['AsyncVectorLayerView']:
        """
        [async] Get vector layer views by their IDs.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            ids (List[int]): list of comma separated layer ids to be returned. e.g. 1, 2, 3
            user_id (int, optional): specific user. privileges required.
            include_settings (bool, optional): Whether to include the settings of the vector layer views. default is False.

        Returns:
            List[AsyncVectorLayerView]: A list of AsyncVectorLayerView instances.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     views = await AsyncVectorLayerView.get_views_by_ids(client, ids=[1,2,3])
            or
            >>>     views = await client.get_views_by_ids(ids=[1,2,3])
        """
        params = {
            'ids': ids,
            'user_id': user_id,
            'include_settings': include_settings
        }
        return await super()._get_list_by_ids(api=api, 
            endpoint=f'{cls.BASE_ENDPOINT}get-layers/', 
            params=params, 
            factory_func=lambda api, item: AsyncVectorLayerView(api, item['uuid'], LayerType(item['layer_type']), item))


    @classmethod
    async def get_view(cls, api: 'AsyncGeoboxClient', uuid: str, user_id: int = None) -> 'AsyncVectorLayerView':
        """
        [async] Get a specific vector layer view by its UUID.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The UUID of the vector layer view.
            user_id (int, optional): Specific user. privileges required.

        Returns:    
            AsyncVectorLayerView: A AsyncVectorLayerView instance.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>>     view = await client.get_view(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return await super()._get_detail(api=api,
            endpoint=cls.BASE_ENDPOINT,
            uuid=uuid, 
            params=params, 
            factory_func=lambda api, item: AsyncVectorLayerView(api, item['uuid'], LayerType(item['layer_type']), item))


    @classmethod
    async def get_view_by_name(cls, api: 'AsyncGeoboxClient', name: str, user_id: int = None) -> Union['AsyncVectorLayerView', None]:
        """
        [async] Get a view by name

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            name (str): the name of the view to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            AsyncVectorLayerView | None: returns the view if a view matches the given name, else None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view_by_name(client, name='test')
            or
            >>>     view = await client.get_view_by_name(name='test')
        """
        views = await cls.get_views(api, q=f"name = '{name}'", user_id=user_id)
        if views and views[0].name == name:
            return views[0]
        else:
            return None


    async def update(self, **kwargs) -> Dict:
        """
        [async] Update the vector layer view.

        Keyword Args:
            name (str): The name of the vector layer view.
            display_name (str): The display name of the vector layer view.
            description (str): The description of the vector layer view.

        Returns:
            Dict: The updated vector layer view.

        Raises:
            ValidationError: If the update data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.update(name="new_name")
            >>>     await view.update(display_name="new_display_name")
            >>>     await view.update(description="new_description")
        """
        return await super().update(name=kwargs.get('name'), display_name=kwargs.get('display_name'), description=kwargs.get('description'))
    

    async def delete(self) -> None:
        """
        [async] Delete the vector layer view.
        
        Returns:
            None
            
        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = async AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     async view.delete()
        """        
        return await super()._delete(self.endpoint)


    async def share(self, users: List['AsyncUser']) -> None:
        """
        [async] Shares the view with specified users.

        Args:
            users (List[AsyncUser]): The list of user IDs to share the view with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await view.share(users=users)
        """
        await super()._share(self.endpoint, users)
    

    async def unshare(self, users: List['AsyncUser']) -> None:
        """
        [async] Unshares the view with specified users.

        Args:
            users (List[AsyncUser]): The list of user IDs to unshare the view with.

        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     users = await client.search_users(search='John')
            >>>     await view.unshare(users=users)
        """
        await super()._unshare(self.endpoint, users)


    async def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['AsyncUser']:
        """
        [async] Retrieves the list of users the view is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[AsyncUser]: The list of shared users.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return await super()._get_shared_users(self.endpoint, params)


    async def get_fields(self) -> List['AsyncField']:
        """
        [async] Get all fields in the vector layer view.
        
        Returns:
            List[AsyncField]: A list of Field instances representing the vector layer view's fields.
            
        Raises:
            ApiRequestError: If the API request fails.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     fields = await view.get_fields()
        """
        return await super().get_fields()
    

    async def get_field(self, field_id: int) -> 'AsyncField':
        """
        [async] Get a specific field by its ID or name.
        
        Args:
            field_id (int): The ID of the field to retrieve.

        Returns:
            AsyncField: The requested field instance.
            
        Raises:
            NotFoundError: If the field with the specified ID is not found.
            ApiRequestError: If the API request fails.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await view.get_field(id=1)
        """
        return await super().get_field(field_id)


    async def get_field_by_name(self, name: str) -> 'AsyncField':
        """
        [async] Get a specific field by its name.
        
        Args:
            name (str, optional): The name of the field to retrieve.

        Returns:
            AsyncField: The requested field instance.
            
        Raises:
            NotFoundError: If the field with the specified name is not found. 

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await view.get_field_by_name(name='test')
        """      
        return await super().get_field_by_name(name)
    

    async def calculate_field(self, 
        target_field: str, 
        expression: str, 
        q: str = None, 
        bbox: List[float] = None, 
        bbox_srid: int = None, 
        feature_ids: List = None, 
        run_async: bool = True, 
        user_id: int = None) -> Union['AsyncTask', Dict]:
        """
        [async] Calculate values for a field based on an expression.
        
        Args:
            target_field (str): The field to calculate values for.
            expression (str): The expression to use for calculation.
            q (Optional[str]): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            bbox (Optional[List[float]]): Bounding box to filter features.
            bbox_srid (Optional[int]): Spatial reference ID for the bounding box.
            feature_ids (Optional[List[int]]): List of specific feature IDs to include.
            run_async (Optional[bool]): Whether to run the calculation asynchronously.
            user_id (Optional[int]): ID of the user running the calculation.
            
        Returns:
            AsyncTask | Dict: The task instance of the calculation operation or the api response if the run_async=False.
            
        Raises:
            ValidationError: If the calculation parameters are invalid.
            ApiRequestError: If the API request fails.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await view.calculate_field(target_field="target_field", 
            ...         expression="expression", 
            ...         q="name like 'my_layer'", 
            ...         bbox=[10, 20, 30, 40], 
            ...         bbox_srid=3857, 
            ...         feature_ids=[1, 2, 3], 
            ...         run_async=True)
        """
        return await super().calculate_field(target_field, expression, q, bbox, bbox_srid, feature_ids, run_async, user_id)
    

    async def get_features(self, geojson: bool = False, **kwargs) -> Union[List['AsyncFeature'], Dict, int]:
        """
        [async] Get features from the layer with optional filtering and pagination.
        
        Args:
            geojson (bool, optional): If True, returns the raw API response (GeoJSON dict). 
                            If False, returns a list of Feature objects. default: False.

        Keyword Args:
            quant_factor (int): Quantization factor. This parameter is only used by topojson encoder and is ignored for other formats. Higher quantizaion value means higher geometry precision. default is 1000000.
            skip (int): Number of features to skip. default is 0.
            limit (int): Maximum number of features to return. default is 100.
            user_id (int): Specific user. privileges required.
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            skip_geometry (bool): Whether to exclude geometry data. default is False.
            return_count (bool): Whether to return total count. default is False.
            feature_ids (List[int]): comma separated list of feature ids which should be filtered.
            select_fields (str): comma separated field names which should be included to the result. default is "[ALL]".
            skip_fields (str): comma separated field names which should be excluded from the result.
            out_srid (int): srid (epsg code) of result features. e.g. 4326. default is 3857
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, length D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            q (str): query filter based on OGC CQL standard. e.g. Name LIKE '%GIS%' AND INTERSECTS(geometry, 'SRID=3857;POLYGON((4901948 2885079, 7049893 2885079, 7049893 4833901, 4901948 4833901, 4901948 2885079))').
            bbox (str): Bounding box to filter features by. e.g. [50.275, 35.1195, 51.4459, 36.0416].
            bbox_srid (int): srid (epsg code) of bbox. e.g. 4326. default is 3857.
                
        Returns:
            List[Feature] | Dict | int: A list of Feature instances or the geojson api response if geojson=True or the features count if return_count is True.
            

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     layer = await AsyncVectorLayerView(api=client, name="my_layer", layer_type=LayerType.Point)
            >>>     features = await layer.get_features(quant_factor=1000000, 
            ...         skip=0, 
            ...         limit=100, 
            ...         skip_geometry=False, 
            ...         return_count=False, 
            ...         select_fields="fclass, osm_id", 
            ...         out_srid=4326, 
            ...         bbox_srid=4326)
        """ 
        return await super().get_features(geojson=geojson, **kwargs)
    

    async def get_feature(self, feature_id: int, out_srid: int = AsyncFeature.BASE_SRID) -> 'AsyncFeature':
        """
        [async] Get a specific feature by its ID.
        
        Args:
            feature_id (int): The ID of the feature to retrieve.
            out_srid (int, optional): Output spatial reference ID

        Returns:
            AsyncFeature: The requested feature instance.
            
        Raises:
            NotFoundError: If the feature with the specified ID is not found.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await view.get_feature(id=1)
        """
        return await super().get_feature(feature_id, out_srid)
    

    async def create_feature(self, geojson: Dict) -> 'AsyncFeature':
        """
        [async] Create a new feature in the layer.
        
        Args:
            geojson (dict): The feature data including properties and geometry.
            
        Returns:
            AsyncFeature: The newly created feature instance.
            
        Raises:
            ValidationError: If the feature data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     feature = await view.create_feature(geojson=geojson)
        """
        return await super().create_feature(geojson)


    async def delete_features(self, 
        q: str = None, 
        bbox: List[float] = None, 
        bbox_srid: int = None, 
        feature_ids: List[int] = None, 
        run_async: bool = True, 
        user_id: int = None) -> Union['AsyncTask', Dict]:
        """
        [async] Delete features from the layer based on specified criteria.
        
        Args:
            q (Optional[str]): Query to filter features to delete.
            bbox (Optional[List[float]]): Bounding box to filter features.
            bbox_srid (Optional[int]): Spatial reference ID for the bounding box.
            feature_ids (Optional[List[int]]): List of specific feature IDs to delete.
            run_async (Optional[bool]): Whether to run the deletion asynchronously.
            user_id (Optional[int]): ID of the user performing the deletion.
            
        Returns:
            AsyncTask | Dict: The task instance of the deletion operation or the api response if run_async=False.
            
        Raises:
            ValidationError: If the deletion parameters are invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.delete_features(q="name like 'my_layer'", 
            ...         bbox=[10, 20, 30, 40],
            ...         bbox_srid=3857, 
            ...         feature_ids=[1, 2, 3], 
            ...         run_async=True)
        """
        return await super().delete_features(q, bbox, bbox_srid, feature_ids, run_async, user_id)


    async def import_features(self,
        file: 'AsyncFile', 
        input_geom_type: 'InputGeomType' = None, 
        input_layer_name: str = None, 
        input_dataset: str = None, 
        user_id: int = None, 
        input_srid: int = None, 
        file_encoding: str = "utf-8", 
        replace_domain_codes_by_values: bool = False, 
        report_errors: bool = True) -> 'AsyncTask':
        """
        [async] Import features from a file into the layer.
        
        Args:
            file (File): file object to import.
            input_geom_type (InputGeomType, optional): Type of geometry in the input file.
            input_layer_name (str, optional): Name of the layer in the input file.
            input_dataset (str, optional): Name of the dataset in the input file.
            user_id (int, optional): Specific user.privileges requied.
            input_srid (int, optional): Spatial reference ID of the input data.
            file_encoding (str, optional): Character encoding of the input file.
            replace_domain_codes_by_values (bool, optional): Whether to replace domain codes with values.
            report_errors (bool, optional): Whether to report import errors.
            
        Returns:
            Task: The task instance of the import operation.
            
        Raises:
            ValidationError: If the import parameters are invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     file = await client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await view.import_features(file=file, 
            ...         input_geom_type=InputGeomType.POINT,
            ...         input_layer="my_layer",
            ...         input_dataset="my_dataset",
            ...         input_srid=3857,
            ...         file_encoding="utf-8",
            ...         replace_domain_codes_by_values=False, 
            ...         report_errors=True)
        """
        return await super().import_features(file, 
            input_geom_type, 
            input_layer_name, 
            input_dataset, 
            user_id, 
            input_srid, 
            file_encoding, 
            replace_domain_codes_by_values, 
            report_errors)


    async def export_features(self, 
        out_filename: str, 
        out_format: 'FileOutputFormat', 
        replace_domain_codes_by_values: bool = False, 
        run_async: bool = True, 
        bbox: List[float] = None, 
        out_srid: int = None, 
        zipped: bool = True, 
        feature_ids: List[int] = None, 
        bbox_srid: int = None, 
        q: str = None, 
        fields: List[str] = None) -> Union['AsyncTask', Dict]:
        """
        [async] Export features from the layer to a file.
        
        Args:
            out_filename (str): Name of the output file.
            out_format (FileOutputFormat): Format of the output file (e.g., 'Shapefile', 'GPKG', 'GeoJSON', 'CSV', 'KML', 'DXF').
            replace_domain_codes_by_values (bool, optional): Whether to replace domain codes with values.
            run_async (bool, optional): Whether to run the export asynchronously.
            bbox (List[float], optional): Bounding box to filter features.
            out_srid (int, optional): Spatial reference ID for the output.
            zipped (bool, optional): Whether to compress the output file.
            feature_ids (List[int], optional): List of specific feature IDs to export.
            bbox_srid (int, optional): Spatial reference ID for the bounding box.
            q (str, optional): Query to filter features.
            fields (List[str], optional): List of fields to include in the export.
            
        Returns:
            AsyncTask | Dict: The task instance of the export operation or the api response if run_async=False.
            
        Raises:
            ValidationError: If the export parameters are invalid.
            ApiRequestError: If the API request fails.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await view.export_features(out_filename="output.shp", 
            ...         out_format="shp",
            ...         replace_domain_codes_by_values=False, 
            ...         run_async=True, 
            ...         bbox=[10, 20, 30, 40], 
            ...         out_srid=3857, 
            ...         zipped=True, 
            ...         feature_ids=[1, 2, 3])
        """
        return await super().export_features(out_filename, 
            out_format, 
            replace_domain_codes_by_values, 
            run_async, 
            bbox, 
            out_srid, 
            zipped, 
            feature_ids, 
            bbox_srid, 
            q, 
            fields)

    
    def get_tile_pbf_url(self, x: int = '{x}', y: int = '{y}', z: int = '{z}') -> str:
        """
        Get a vector tile pbf url for the view.
        
        Args:
            x (int): X coordinate of the tile.
            y (int): Y coordinate of the tile.
            z (int): Zoom level of the tile.

        Returns:
            str: the vector tile url.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     tile = view.get_tile(x=10, y=20, z=1)
        """
        return super().get_tile_pbf_url(x, y, z)
    

    async def get_tile_json(self) -> Dict:
        """
        [async] Get the vector tile JSON configuration for the layer.
        
        Returns:
            Dict: The vector tile JSON configuration.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     tile_json = await view.get_tile_json()
        """
        return await super().get_tile_json()


    @property
    async def settings(self) -> Dict:
        """
        [async] Get the layer's settings.
        
        Returns:
            Dict: The layer settings.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     setting = await view.settings
        """
        return await super().settings


    async def update_settings(self, settings: Dict) -> Dict:
        """
        [async] Update the settings

        settings (Dict): settings dictionary

        Returns:
            Dict: updated settings

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> async with AsyncGeoboxClient() as client:
            >>>     view1 = await client.get_view(uuid="12345678-1234-5678-1234-567812345678")
            >>>     view2 = await client.get_view(uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view1.update_settings(view2.settings)
        """
        return await super().update_settings(settings) 


    async def set_settings(self, **kwargs) -> Dict:
        """
        [async] Set the settings of the Vector Layer.
        
        Keyword Args:
            title_field (str): The field to use as the title.
            domain_display_type (str): The type of domain display.
            allow_export (bool): Whether to allow export.
            editable (bool): Whether to allow editing.
            edit_geometry (bool): Whether to allow editing the geometry.
            editable_attributes (str): The attributes to allow editing.
            allow_insert (bool): Whether to allow inserting.
            allow_delete (bool): Whether to allow deleting.
            min_zoom (int): The minimum zoom level.
            max_zoom (int): The maximum zoom level.
            max_features (int): The maximum number of features.
            filter_features (bool): Whether to filter features.
            fields (List[str]): The fields to include in the layer.
            use_cache (bool): Whether to use caching.
            cache_until_zoom (int): The zoom level to cache until.
            
        Returns:
            Dict: The updated settings.
            
        Raises:
            ValidationError: If the settings data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.set_setting(title_field="name",
            ...         domain_display_type="Value",
            ...         allow_export=True,
            ...         editable=True,
            ...         edit_geometry=True,
            ...         editable_attributes="[ALL]",
            ...         allow_insert=True,
            ...         allow_delete=True,
            ...         min_zoom=0,
            ...         max_zoom=24,
            ...         max_features=65536,
            ...         filter_features=True,
            ...         fields=["id"],
            ...         use_cache=True,
            ...         cache_until_zoom=17)
        """
        return await super().set_settings(**kwargs)
    

    async def seed_cache(self, from_zoom: int = None, to_zoom: int = None, ignore_cache: bool = False, workers: int = 1, user_id: int = None) -> List['AsyncTask']:
        """
        [async] Seed the cache for the view.
        
        Args:
            from_zoom (int, optional): The zoom level to start caching from.
            to_zoom (int, optional): The zoom level to stop caching at.
            ignore_cache (bool, optional): Whether to ignore the cache. default is False.
            workers (int, optional): The number of workers to use. default is 1.
            user_id (int, optional): specified user. privileges required.

        Returns:
            List[Task]: The task instance of the cache seeding operation.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await view.cache_seed(from_zoom=0, to_zoom=10, ignore_cache=False, workers=1)
        """
        return await super().seed_cache(from_zoom, to_zoom, ignore_cache, workers, user_id)


    async def clear_cache(self) -> None:
        """
        [async] Clear the view's cache.
        
        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.clear_cache()
        """
        return await super().clear_cache()


    @property
    async def cache_size(self) -> int:
        """
        [async] Get the size of the view's cache.
        
        Returns:
            int: The size of the view's cache.
            
        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.cache_size
        """
        return await super().cache_size


    async def update_stats(self) -> None:
        """
        [async] Update the view's statistics.
        
        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.update_stats()
        """
        return await super().update_stats()


    async def prune_edited_areas(self) -> None:
        """
        [async] Prune edited areas. This method eliminates edited areas when there are too many of them. Cache builder uses this edited areas for partial cache generating.
        
        Returns:
            None

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.prune_edited_areas()
        """
        return await super().prune_edited_areas()


    async def get_attachments(self, **kwargs) -> List['AsyncAttachment']:
        """
        [async] Get the resouces attachments

        Keyword Args:
            element_id (str): the id of the element with attachment.
            search (str): search term for keyword-based searching among all textual fields.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            return_count (bool): Whether to return total count. default is False.

        Returns:
            List[AsyncAttachment] | int: A list of attachments instances or the total number of attachments.

        Raises:
            TypeError: if the resource type is not supported

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     await view.get_attachments()
        """
        from .attachment import AsyncAttachment

        return await AsyncAttachment.get_attachments(self.api, resource=self, **kwargs)
    
    
    async def create_attachment(self, 
        name: str, 
        loc_x: int,
        loc_y: int,
        file: 'AsyncFile',
        feature: 'AsyncFeature' = None,
        display_name: str = None, 
        description: str = None) -> 'Attachment':
        """
        [async] Create a new Attachment.

        Args:
            name (str): The name of the scene.
            loc_x (int): x parameter of the attachment location.
            loc_y (int): y parameter of the attachment location.
            file (AsyncFile): the file object.
            feature (AsyncFeature, optional): the feature object.
            display_name (str, optional): The display name of the scene.
            description (str, optional): The description of the scene.

        Returns:
            Attachment: The newly created Attachment instance.

        Raises:
            ValidationError: If the Attachment data is invalid.

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> async with AsyncGeoboxClient() as client:
            >>>     view = await AsyncVectorLayerView.get_view(client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     files = await client.get_files()
            >>>     file = file[0]
            >>>     await view.create_attachment(name='test', loc_x=10, loc_y=10, file=file)
        """
        from .attachment import AsyncAttachment

        return await AsyncAttachment.create_attachment(self.api,
            name=name,
            loc_x=loc_x,
            loc_y=loc_y,
            resource=self,
            file=file,
            feature=feature,
            display_name=display_name,
            description=description)
    

    def to_sync(self, sync_client: 'GeoboxClient') -> 'VectorLayerView':
        """
        Switch to sync version of the view instance to have access to the sync methods

        Args:
            sync_client (GeoboxClient): The sync version of the GeoboxClient instance for making requests.

        Returns:
            VectorLayerView: the sync instance of the view.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.view import AsyncVectorLayerView
            >>> client = GeoboxClient()
            >>> async with AsyncGeoboxClient() as async_client:
            >>>     view = await AsyncVectorLayerView.get_view(async_client, uuid="12345678-1234-5678-1234-567812345678")
            >>>     sync_view = view.to_sync(client)
        """
        from ..view import VectorLayerView

        return VectorLayerView(api=sync_client, uuid=self.uuid, layer_type=self.layer_type, data=self.data)