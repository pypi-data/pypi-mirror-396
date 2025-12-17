from typing import Dict, Optional, TYPE_CHECKING, Union

from geobox.field import Field

from .vectorlayer import AsyncVectorLayer
from .view import AsyncVectorLayerView
from .base import AsyncBase
from .raster import AsyncRaster
from ..enums import (AnalysisDataType, PolygonizeConnectivity, AnalysisResampleMethod, 
                    SlopeUnit, AnalysisAlgorithm, RangeBound, DistanceUnit)
from ..utils import clean_data

if TYPE_CHECKING:
    from . import AsyncGeoboxClient
    from .task import AsyncTask

class AsyncRasterAnalysis(AsyncBase):

    BASE_ENDPOINT = 'analysis/'

    def __init__(self, 
        api: 'AsyncGeoboxClient', 
        data: Optional[Dict] = {}):
        """
        [async] Initialize a workflow instance.

        Args:
            api (AsyncGeoboxClient): The AsyncGeoboxClient instance for making requests.
            uuid (str): The unique identifier for the workflow.
            data (Dict): The response data of the workflow.
        """
        super().__init__(api, data=data)


    def __repr__(self) -> str:
        return f"AsyncRasterAnalysis()"


    async def rasterize(self, 
        layer: Union[AsyncVectorLayer, AsyncVectorLayerView],
        output_raster_name: str,
        pixel_size: int = 10,
        nodata: Optional[int] = -9999,
        data_type: Optional[AnalysisDataType] = AnalysisDataType.int16,
        burn_value: Optional[int] = 1,
        burn_attribute: Optional[str] = None,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Rasterize a vector layer

        This method converts a vector layer (or view) to a raster dataset using the specified parameters. 
        You can control the output raster's name, pixel size, data type, nodata value, and the value to burn (either a constant or from an attribute field). 
        Only users with Publisher role or higher can perform this operation.

        Args:
            layer (AsyncVectorLayer | AsyncVectorLayerView): VectorLayer or VectorLayerView instance
            output_raster_name (str): Name for the output raster dataset
            pixel_size (int, optional): Pixel size for the output raster (must be > 0). default: 10
            nodata (int, optional): NoData value to use in the output raster. default: -9999
            data_type (AnalysisDataType, optional): Data type for the output raster (e.g., int16, float32). default: AnalysisDataType.int16
            burn_value (int, optional): Value to burn into the raster for all features (if burn_attribute is not set). default: 1
            burn_attribute (str, optional): Name of the attribute field to use for burning values into the raster
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     vector = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.rasterize(layer=vector, output_raster_name='test')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.rasterize(layer=vector, output_raster_name='test')
        """
        if not isinstance(layer, AsyncVectorLayer) and not isinstance(layer, AsyncVectorLayerView):
            raise ValueError("'layer' input only accepts vector layer and view objects!")

        endpoint = f'{self.BASE_ENDPOINT}rasterize/'

        data = clean_data({
            'layer_uuid': layer.uuid,
            'output_raster_name': output_raster_name,
            'is_view': False if isinstance(layer, AsyncVectorLayer) else True,
            'pixel_size': pixel_size,
            'nodata': nodata,
            'data_type': data_type.value,
            'burn_value': burn_value,
            'burn_attribute': burn_attribute,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def polygonize(self,
        raster: 'AsyncRaster',
        output_layer_name: str,
        band_index: int = 1,
        value_field: Optional[str] = None,
        mask_nodata: bool = False,
        connectivity: PolygonizeConnectivity = PolygonizeConnectivity.connected_4,
        keep_values: Optional[str] = None,
        layer_name: Optional[str] = None,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Convert a raster to vector polygons

        vectorizes a raster (polygonize) to a vector dataset (*.gpkg). Only users with Publisher role or higher can perform this operation

        Args:
            raster (Raster): Raster instance
            output_layer_name  (str): Name for the output vector layer.
            band_index (int, optional): Raster band to polygonize. default: 1
            value_field (str, optional): Name of attribute field storing the pixel value. default: None
            mask_nodata (bool, optional): If True, NoData pixels are excluded using the band mask. default: False
            connectivity (PolygonizeConnectivity, optional): 4 or 8 connectivity for region grouping. default: PolygonizeConnectivity.connected_4 
            keep_values (str, optional): JSON array of values to keep (e.g., '[1,2,3]'). default: None
            layer_name (str, optional): Output layer name. default: None
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.polygonize(raster=raster, output_layer_name='test')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.polygonize(raster=raster, output_layer_name='test')
        """
        endpoint = f'{self.BASE_ENDPOINT}polygonize/'

        data = clean_data({
            'raster_uuid': raster.uuid,
            'output_layer_name': output_layer_name,
            'band_index': band_index,
            'value_field': value_field,
            'mask_nodata': mask_nodata,
            'connectivity': connectivity.value,
            'keep_values': keep_values,
            'layer_name': layer_name,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def clip(self, 
        raster: 'AsyncRaster',
        layer: Union[AsyncVectorLayer, AsyncVectorLayerView],
        output_raster_name: str,
        where: Optional[str] = None,
        dst_nodata: int = -9999,
        crop: bool = True,
        resample: AnalysisResampleMethod = AnalysisResampleMethod.near,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Clip a raster using a vector layer as a mask

        clips a raster dataset using a vector layer as the clipping boundary. Only users with Publisher role or higher can perform this operation

        Args:
            raster (Raster): Raster instance
            layer (AsyncVectorLayer | AsyncVectorLayerView): VectorLayer or VectorLayerView instance
            output_raster_name (str): Name for the output raster dataset
            where (str, optional): Optional attribute filter, e.g. 'VEG=forest'.
            dst_nodata (int, optional): Output NoData value. default: -9999
            crop (bool, optional): True=shrink extent to polygon(s); False=keep full extent but mask outside. default: True
            resample (CropResample, optional): Resampling method: 'near', 'bilinear', 'cubic', 'lanczos', etc. default: CropResample.near
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     vector = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.clip(raster=raster, layer=vector, output_raster_name='test')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.clip(raster=raster, layer=vector, output_raster_name='test')
        """
        if not isinstance(layer, AsyncVectorLayer) and not isinstance(layer, AsyncVectorLayerView):
            raise ValueError("'layer' input only accepts vector layer and view objects!")

        endpoint = f'{self.BASE_ENDPOINT}clip/'

        data = clean_data({
            'raster_uuid': raster.uuid,
            'layer_uuid': layer.uuid,
            'output_raster_name': output_raster_name,
            'is_view': False if isinstance(layer, AsyncVectorLayer) else True,
            'where': where,
            'dst_nodata': dst_nodata,
            'crop': crop,
            'resample': resample.value,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def calculator(self,
        variables: str,
        expr: str,
        output_raster_name: str,
        match_raster_uuid: Optional[str] = None,
        resample: AnalysisResampleMethod = AnalysisResampleMethod.bilinear,
        out_dtype: AnalysisDataType = AnalysisDataType.float32,
        dst_nodata: int = -9999,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Perform raster calculator operations on multiple raster datasets.

        it allows you to perform mathematical operations on one or more raster datasets using NumPy expressions. 
        Variables in the expression correspond to raster datasets specified in the variables dictionary.

        Examples:
            NDVI calculation: variables='{"NIR": "raster_uuid_1", "RED": "raster_uuid_2"}', expr="(NIR-RED)/(NIR+RED)"
            Slope threshold: variables='{"SLOPE": "raster_uuid_1"}', expr="np.where(SLOPE>30,1,0)"
            Multi-band operations: variables='{"IMG": ["raster_uuid_1", 2]}', expr="IMG*2"

        Args:
            variables (str): JSON string mapping variable names to raster specifications. Format: '{"NIR": "raster_uuid_1", "RED": "raster_uuid_2"}' or '{"IMG": ["raster_uuid_1", 2]}' for multi-band operations.
            expr (str): Mathematical expression using NumPy syntax. Use variable names from the variables dict, e.g., '(NIR-RED)/(NIR+RED)' or 'where(SLOPE>30,1,0)' or 'where((dist_to_highway < 1000) & (slope < 10), 1, 0)' .Supported functions: np, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, exp, log, log10, sqrt, abs, floor, ceil, round, minimum, maximum, clip, where, isnan, isfinite, pi, e.
            output_raster_name (str): Name for the output raster dataset.
            match_raster_uuid (str, optional): Optional raster UUID to match the output grid and projection. If not provided, the first variable becomes the reference grid.
            resample (CropResample, optional): Resampling method: 'near', 'bilinear', 'cubic', 'lanczos', etc. default: CropResample.near
            out_dtype (AnalysisDataType, optional): Data type for the output raster (e.g., int16, float32). default: AnalysisDataType.float32
            dst_nodata (int, optional): NoData value for the output raster. default = -9999
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.calculator(variables={"NIR": "raster_uuid_1", "RED": "raster_uuid_2"},
            ...         expr='where(SLOPE>30,1,0)',
            ...         output_raster_name='test')
            or
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = raster_analysis.calculator(variables={"NIR": "raster_uuid_1", "RED": "raster_uuid_2"},
            ...         expr='where(SLOPE>30,1,0)',
            ...         output_raster_name='test')
        """
        endpoint = f'{self.BASE_ENDPOINT}calculator/'

        data = clean_data({
            'variables': variables,
            'expr': expr,
            'output_raster_name': output_raster_name,
            'match_raster_uuid': match_raster_uuid,
            'resample': resample.value,
            'out_dtype': out_dtype.value,
            'dst_nodata': dst_nodata,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def slope(self,
        raster: 'AsyncRaster',
        output_raster_name: str,
        slope_units: SlopeUnit = SlopeUnit.degree,
        algorithm: AnalysisAlgorithm = AnalysisAlgorithm.Horn,
        scale: int = 1,
        compute_edges: bool = True,
        nodata_out: int = -9999,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Calculate slope from a DEM raster.

        This endpoint creates a slope raster from a Digital Elevation Model (DEM). Only users with Publisher role or higher can perform this operation.

        Args:
            raster (Raster): DEM Raster instance
            output_raster_name (str): Name for the output raster dataset.
            slope_units (SlopeUnit, optional): Slope units: 'degree' or 'percent'. default: SlopeUnit.degree
            algorithm (AnalysisAlgorithm, optional): Algorithm: 'Horn' or 'ZevenbergenThorne'. default: AnalysisAlgorithm.Horn
            scale (int, optional): Ratio of vertical units to horizontal units. default: 1
            compute_edges (bool, optional): Whether to compute edges. default: True
            nodata (int, optional): NoData value for the output raster. default = -9999
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.slope(raster=raster, output_raster_name='test')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.slope(raster=raster, output_raster_name='test')
        """
        endpoint = f'{self.BASE_ENDPOINT}slope/' 

        data = clean_data({
            'raster_uuid': raster.uuid,
            'output_raster_name': output_raster_name,
            'slope_units': slope_units.value,
            'algorithm': algorithm.value,
            'scale': scale,
            'compute_edges': compute_edges,
            'nodata_out': nodata_out,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def aspect(self,
        raster: 'AsyncRaster',
        output_raster_name: str,
        algorithm: AnalysisAlgorithm = AnalysisAlgorithm.Horn,
        trigonometric: bool = False,
        zero_for_flat: bool = True,
        compute_edges: bool = True,
        nodata_out: int = -9999,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Calculate aspect from a DEM raster.

        it creates an aspect raster (degrees 0–360) from a Digital Elevation Model (DEM).
        Only users with Publisher role or higher can perform this operation.

        Args:
            raster (Raster): DEM Raster instance
            output_raster_name (str): Name for the output raster dataset.
            algorithm (AnalysisAlgorithm, optional): Algorithm: 'Horn' or 'ZevenbergenThorne'. default: AnalysisAlgorithm.Horn
            trigonometric (bool, optional): False: azimuth (0°=N, 90°=E, clockwise); True: 0°=E, counter-clockwise. default: False
            zero_for_flat (bool, optional): Set flats (slope==0) to 0 instead of NoData. default: True
            compute_edges (bool, optional): Whether to compute edges. default: True
            nodata (int, optional): NoData value for the output raster. default = -9999
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.aspect(raster=raster, output_raster_name='test')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.aspect(raster=raster, output_raster_name='test')
        """

        endpoint = f'{self.BASE_ENDPOINT}aspect/' 

        data = clean_data({
            'raster_uuid': raster.uuid,
            'output_raster_name': output_raster_name,
            'algorithm': algorithm.value,
            'trigonometric': trigonometric,
            'zero_for_flat': zero_for_flat,
            'compute_edges': compute_edges,
            'nodata_out': nodata_out,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def reclassify(self,
        raster: 'AsyncRaster',
        output_raster_name: str,
        rules: str,
        default_value: Optional[int] = None,
        nodata_in: int = -9999,
        nodata_out: int = -9999,
        out_dtype: AnalysisDataType = AnalysisDataType.int16,
        inclusive: RangeBound = RangeBound.left,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Reclassify a raster using value mapping or class breaks.

        This endpoint reclassifies raster values according to specified rules. 
        Only users with Publisher role or higher can perform this operation.

        Args:
            raster (Raster): Raster instance
            output_raster_name (str): Name for the output reclassified raster dataset.
            rules (str): JSON string containing reclassification rules. 
                            For mode='exact', it should be a dict {old_value: new_value}. 
                            For mode='range', it should be a list of (low, high, new_value). 
                            Example for mode='exact': '{"1": 10, "2": 20, "3": 30}'. 
                            Example for mode='range': '[[0, 10, 1], [10, 20, 2], [20, 30, 3]]'.
                            the method would detect the mode type based on the rules input.
            default_value (str, optional): Value to assign when a pixel matches no rule.
            nodata_in (int, optional): NoData of input. If None, tries to get from the input raster.
            nodata_out (int, optional): NoData value to set on output band.
            out_dtype (AnalysisDataType, optional): Output data type. default: AnalysisDataType.int16
            inclusive (RangeBound, optional): Range bound semantics for mode='range': 'left', 'right', 'both', 'neither'. default: RangeBound.left
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.reclassify(raster=raster, output_raster_name='test', rules='{"1": 10, "2": 20, "3": 30}')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = raster_analysis.reclassify(raster=raster, output_raster_name='test', rules='{"1": 10, "2": 20, "3": 30}')
        """
        endpoint = f'{self.BASE_ENDPOINT}reclassify/'

        data = clean_data({
            'raster_uuid': raster.uuid,
            'output_raster_name': output_raster_name,
            'rules': rules,
            'mode': 'exact' if isinstance(rules, dict) else 'range' if isinstance(rules, list) else None,
            'default_value': default_value,
            'nodata_in': nodata_in,
            'nodata_out': nodata_out,
            'out_dtype': out_dtype.value,
            'inclusive': inclusive.value,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def resample(self,
        raster: 'AsyncRaster',
        output_raster_name: str,
        out_res: Optional[str] = None,
        scale_factor: Optional[str] = None,
        match_raster_uuid: Optional[str] = None,
        resample_method: AnalysisResampleMethod = AnalysisResampleMethod.near,
        dst_nodata: int = -9999,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Resample a raster to a different resolution.

        it resamples a raster using GDAL Warp. 
        Exactly one of out_res, scale_factor, or match_raster_uuid must be provided. 
        Only users with Publisher role or higher can perform this operation.

        Args:
            raster (Raster): Raster instance
            output_raster_name (str): Name for the output reclassified raster dataset.
            out_res (str, optional): Output resolution as 'x_res,y_res' (e.g., '10,10').
            scale_factor (int, optional): Scale factor (e.g., 2.0 for 2x finer resolution).
            match_raster_uuid (str, optional): UUID of reference raster to match resolution/extent.
            resample_method (AnalysisResampleMethod, optional): Resampling method: 'near', 'bilinear', 'cubic', 'lanczos', etc.
            dst_nodata (int, optional): Output NoData value.
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.resample(raster=raster, output_raster_name='test', out_res='10,10')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.resample(raster=raster, output_raster_name='test', out_res='10,10')
        """
        if sum(x is not None for x in [out_res, scale_factor, match_raster_uuid]) != 1:
            raise ValueError('Exactly one of out_res, scale_factor, or match_raster_uuid must be provided!')

        endpoint = f'{self.BASE_ENDPOINT}resample/'

        data = clean_data({
            'raster_uuid': raster.uuid,
            'output_raster_name': output_raster_name,
            'out_res': out_res,
            'scale_factor': scale_factor,
            'match_raster_uuid': match_raster_uuid,
            'resample_method': resample_method.value,
            'dst_nodata': dst_nodata,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def idw_interpolation(self,
        layer: Union[AsyncVectorLayer, AsyncVectorLayerView],
        output_raster_name: str,
        z_field: Field,
        match_raster_uuid: Optional[str] = None,
        pixel_size: int = 10,
        extent: Optional[str] = None,
        power: float = 2.0,
        smoothing: float = 0.0,
        max_points: int = 16,
        radius: int = 1000,
        nodata: int = -9999,
        out_dtype: AnalysisDataType = AnalysisDataType.float32,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Create an IDW (Inverse Distance Weighting) interpolation raster from point data.

        it creates a raster using IDW interpolation from point data in a vector layer. 
        Only users with Publisher role or higher can perform this operation.

        Args:
            layer (AsyncVectorLayer | AsyncVectorLayerview): layer containing point data 
            output_raster_name (str): Name for the output IDW raster dataset.
            z_field (Field): the field containing the values to interpolate.
            match_raster_uuid (str, optional): UUID of reference raster to match resolution/extent.
            pixel_size (int, optional): Pixel size for the output raster. default: 10
            extent (str, optional): Extent as 'minX,minY,maxX,maxY'.
            power (float, optional): Power parameter for IDW. default: 2.0
            smoothing (float, optional): Smoothing parameter for IDW. default: 0.0
            max_points (int, optional): Maximum number of neighbors to use. default: 16
            radius (int, optional): Search radius in map units. default: 1000
            nodata (int, optional): NoData value for the output raster. default: -9999
            out_dtype (AnalysisDataType, optional): Output data type.
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     vector = await client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>>     field = await vector.get_field_by_name('field_name')
            >>>     task = await client.raster_analysis.idw_interpolation(layer=vector, output_raster_name='test', z_field=field)
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.idw_interpolation(layer=vector, output_raster_name='test', z_field=field)
        """
        endpoint = f'{self.BASE_ENDPOINT}idw/'

        data = clean_data({
            'layer_uuid': layer.uuid,
            'output_raster_name': output_raster_name,
            'z_field': z_field.name,
            'is_view': False if isinstance(layer, AsyncVectorLayer) else True,
            'match_raster_uuid': match_raster_uuid,
            'pixel_size': pixel_size,
            'extent': extent,
            'power': power,
            'smoothing': smoothing,
            'max_points': max_points,
            'radius': radius,
            'nodata': nodata,
            'out_dtype': out_dtype.value,
            'user_id': user_id
        })
        
        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def constant(self,
        output_raster_name: str,
        extent: str,
        value : int,
        pixel_size: int = 10,
        dtype: AnalysisDataType = AnalysisDataType.float32,
        nodata: int = -9999,
        align_to: Optional[str] = None,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Create a raster filled with a constant value.

        This endpoint creates a north-up GeoTIFF filled with a constant value. 
        Only users with Publisher role or higher can perform this operation.

        Args:
            output_raster_name (str): Name for the output constant raster dataset.
            extent (str): Extent as 'minX,minY,maxX,maxY' (e.g., '0,0,100,100').
            value (int): Constant value to fill the raster with.
            pixel_size (int, optional): Pixel size for the output raster (must be > 0). default: 10
            dtype (AnalysisDataType, optoinal): Output data type. default: AnalysisDataType.float32
            nodata (int, optional): NoData value for the raster. default: -9999
            align_to (str, optional): Grid origin to snap to as 'x0,y0' (e.g., '0,0').
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     task = await client.raster_analysis.constant(output_raster_name='test', extent='0,0,100,100', value=10)
            or
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.constant(output_raster_name='test', extent='0,0,100,100', value=10)
        """
        endpoint = f'{self.BASE_ENDPOINT}constant/'

        data = clean_data({
            'output_raster_name': output_raster_name,
            'extent': extent,
            'value': value,
            'pixel_size': pixel_size,
            'dtype': dtype.value,
            'nodata': nodata,
            'align_to': align_to,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def fill_nodata(self,
        raster: 'AsyncRaster',
        output_raster_name: str,
        band: Union[int, str] = 1,
        nodata: Optional[int] = None,
        max_search_dist: Optional[int] = None,
        smoothing_iterations: Optional[int] = None,
        mask_raster_uuid: Optional[str] = None,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Fill NoData regions in a raster using GDAL's FillNodata algorithm.

        it fills gaps (NoData regions) in a raster by interpolating values from surrounding valid pixels. 
        This is commonly used for data cleaning and gap filling in remote sensing and elevation data. 
        Only users with Publisher role or higher can perform this operation.

        Args:
            raster (Raster): the input raster to fill NoData regions in
            output_raster_name (str): Name for the output filled raster dataset.
            band (int | str): 1-based band index to process or 'all' to process all bands. default: 1
            nodata (int, optional): NoData value to use. If None, uses the band's existing NoData.
            max_search_dist (int, optoinal): Maximum distance in pixels to search for valid data.
            smoothing_iterations (int, optional): Number of smoothing iterations to apply.
            mask_raster_uuid (str, optional): Optional UUID of a mask raster (0=masked, >0=valid).
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.fill_nodata(raster=raster, output_raster_name='test')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analyis.fill_nodata(raster=raster, output_raster_name='test')
        """
        endpoint = f'{self.BASE_ENDPOINT}fill/'

        data = clean_data({
            'raster_uuid': raster.uuid,
            'output_raster_name': output_raster_name,
            'band': band,
            'nodata': nodata,
            'max_search_dist': max_search_dist,
            'smoothing_iterations': smoothing_iterations,
            'mask_raster_uuid': mask_raster_uuid,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])


    async def proximity(self,
        raster: 'AsyncRaster',
        output_raster_name: str,
        dist_units: DistanceUnit = DistanceUnit.GEO,
        burn_value: int = 1,
        nodata: int = -9999,
        user_id: Optional[int] = None) -> 'AsyncTask':
        """
        [async] Create a proximity (distance) raster from a raster layer.

        it creates a raster showing the distance from each pixel to the nearest pixel in the input raster layer. 
        Only users with Publisher role or higher can perform this operation.

        Args:
            raster (Raster): the raster layer to create proximity raster from.
            output_raster_name (str): Name for the output proximity raster dataset.
            dist_units (DistanceUnit, optional): Distance units: 'GEO' for georeferenced units, 'PIXEL' for pixels. default: DistanceUnit.GEO
            burn_value (int, optional): Value treated as targets (distance 0). default: 1
            nodata (int, optional): NoData value to use in the output raster. default: -9999
            user_id (int, optional): specific user. priviledges required!

        Returns:
            AsyncTask: task instance of the process

        Example:
            >>> from geobox.aio import AsyncGeoboxClient
            >>> from geobox.aio.raster_analysis import AsyncRasterAnalysis
            >>> async with AsyncGeoboxClient() as client:
            >>>     raster = await client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
            >>>     task = await client.raster_analysis.proximity(raster=raster, output_raster_name='test')
            or  
            >>>     raster_analysis = AsyncRasterAnalysis(client)
            >>>     task = await raster_analysis.proximity(raster=raster, output_raster_name='test')
        """
        endpoint = f'{self.BASE_ENDPOINT}proximity/'

        data = clean_data({
            'raster_uuid': raster.uuid,
            'output_raster_name': output_raster_name,
            'dist_units': dist_units.value,
            'burn_value': burn_value,
            'nodata': nodata,
            'user_id': user_id
        })

        response = await self.api.post(endpoint=endpoint, payload=data, is_json=False)
        return await self.api.get_task(response['task_id'])