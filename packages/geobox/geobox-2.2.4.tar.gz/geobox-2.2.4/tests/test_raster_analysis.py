import pytest
from unittest.mock import patch

from geobox.raster_analysis import RasterAnalysis
from geobox.enums import FieldType, LayerType
from geobox.field import Field
from geobox.raster import Raster
from geobox.task import Task
from geobox.vectorlayer import VectorLayer


def test_init(api):
    analysis = RasterAnalysis(api)
    assert type(analysis) == RasterAnalysis
    assert analysis.api == api


def test_repr(api):
    analysis = RasterAnalysis(api)
    assert repr(analysis) == 'RasterAnalysis()'


def test_rasterize(api, mock_success_task_data, mock_vector_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    vector = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.rasterize(
        layer=vector,
        output_raster_name='test'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/rasterize/', payload={'layer_uuid': vector.uuid, 'output_raster_name': 'test', 'is_view': False, 'pixel_size': 10, 'nodata': -9999, 'data_type': 'int16', 'burn_value': 1}, is_json=False)

    # error
    with pytest.raises(ValueError):
        raster_analysis.rasterize(
            layer='vector',
            output_raster_name='test'
        )


def test_polygonize(api, mock_success_task_data, mock_raster_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.polygonize(
        raster=raster,
        output_layer_name='test'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/polygonize/', payload={'raster_uuid': raster.uuid, 'output_layer_name': 'test', 'band_index': 1, 'mask_nodata': False, 'connectivity': 4}, is_json=False)


def test_clip(api, mock_success_task_data, mock_raster_data, mock_vector_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    vector = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.clip(
        layer=vector,
        raster=raster,
        output_raster_name='test'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/clip/', payload={'raster_uuid': raster.uuid, 'layer_uuid': '297fa7ca-877a-400c-8003-d65de9e791c2', 'output_raster_name': 'test', 'is_view': False, 'dst_nodata': -9999, 'crop': True, 'resample': 'near'}, is_json=False)

    # error
    with pytest.raises(ValueError):
        raster_analysis.clip(
            layer='vector',
            raster=raster,
            output_raster_name='test'
        ) 


def test_calculator(api, mock_success_task_data, mock_raster_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.calculator(
        variables={"RED": raster.uuid},
        expr='where(SLOPE>30,1,0)',
        output_raster_name='test'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/calculator/', payload={'variables': {'RED': raster.uuid}, 'expr': 'where(SLOPE>30,1,0)', 'output_raster_name': 'test', 'resample': 'bilinear', 'out_dtype': 'float32', 'dst_nodata': -9999}, is_json=False)


def test_slope(api, mock_success_task_data, mock_raster_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.slope(
        raster=raster,
        output_raster_name='test'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/slope/', payload={'raster_uuid': raster.uuid, 'output_raster_name': 'test', 'slope_units': 'degree', 'algorithm': 'Horn', 'scale': 1, 'compute_edges': True, 'nodata_out': -9999}, is_json=False)


def test_aspect(api, mock_success_task_data, mock_raster_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.aspect(
        raster=raster,
        output_raster_name='test'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/aspect/', payload={'raster_uuid': raster.uuid, 'output_raster_name': 'test', 'algorithm': 'Horn', 'trigonometric': False, 'zero_for_flat': True, 'compute_edges': True, 'nodata_out': -9999}, is_json=False)


def test_reclassify(api, mock_success_task_data, mock_raster_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.reclassify(
        raster=raster,
        output_raster_name='test',
        rules='{"1": 10, "2": 20, "3": 30}'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/reclassify/', payload={'raster_uuid': raster.uuid, 'output_raster_name': 'test', 'rules': '{"1": 10, "2": 20, "3": 30}', 'nodata_in': -9999, 'nodata_out': -9999, 'out_dtype': 'int16', 'inclusive': 'left'}, is_json=False)


def test_resample(api, mock_success_task_data, mock_raster_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.resample(
        raster=raster,
        output_raster_name='test',
        out_res='10,10'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/resample/', payload={'raster_uuid': raster.uuid, 'output_raster_name': 'test', 'out_res': '10,10', 'resample_method': 'near', 'dst_nodata': -9999}, is_json=False)

    # error
    with pytest.raises(ValueError):
        raster_analysis.resample(
            raster=raster,
            output_raster_name='test'
        )


def test_idw_interpolation(api, mock_success_task_data, mock_vector_data, mock_field_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    vector = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer=vector, data_type=FieldType.String, field_id=mock_field_data['id'], data=mock_field_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.idw_interpolation(
        layer=vector,
        output_raster_name='test',
        z_field=field
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/idw/', payload={'layer_uuid': vector.uuid, 'output_raster_name': 'test', 'z_field': 'test', 'is_view': False, 'pixel_size': 10, 
        'power': 2.0, 'smoothing': 0.0, 'max_points': 16, 'radius': 1000, 'nodata': -9999, 'out_dtype': 'float32'}, is_json=False)


def test_constant(api, mock_success_task_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }


    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.constant(
        output_raster_name='test',
        extent='0,0,100,100', 
        value=10
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/constant/', payload={'output_raster_name': 'test', 'extent': '0,0,100,100', 'value': 10, 'pixel_size': 10, 'dtype': 'float32', 'nodata': -9999}, is_json=False)


def test_fill_nodata(api, mock_success_task_data, mock_raster_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.fill_nodata(
        raster=raster,
        output_raster_name='test'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/fill/', payload={'raster_uuid': raster.uuid, 'output_raster_name': 'test', 'band': 1}, is_json=False)


def test_proximity(api, mock_success_task_data, mock_raster_data):
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get_task.return_value = task
    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }

    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    raster_analysis = RasterAnalysis(api)
    task = raster_analysis.proximity(
        raster=raster,
        output_raster_name='test'
    )

    assert type(task) == Task
    assert task.uuid == mock_success_task_data['uuid']
    api.post.assert_called_once_with(endpoint='analysis/proximity/', payload={'raster_uuid': 'aea9c935-b0e2-423d-b25d-6c41d5ac22c5', 'output_raster_name': 'test', 'dist_units': 'GEO', 'burn_value': 1, 'nodata': -9999}, is_json=False)