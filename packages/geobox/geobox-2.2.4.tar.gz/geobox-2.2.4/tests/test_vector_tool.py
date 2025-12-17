import pytest

from geobox.enums import GroupByAggFunction, NetworkTraceDirection, SpatialAggFunction, SpatialPredicate
from geobox.exception import NotFoundError
from geobox.task import Task
from geobox.vector_tool import VectorTool
from geobox.query import Query

def test_init(api):
    vector_tool = VectorTool(api)
    assert type(vector_tool) == VectorTool
    assert vector_tool.api == api


def test_repr(api):
    vector_tool = VectorTool(api)
    assert repr(vector_tool) == 'VectorTool()'


def test_wrong_query_name(api):
    vector_tool = VectorTool(api)
    api.get_system_queries.return_value = []
    with pytest.raises(NotFoundError):
        vector_tool.area(
            vector_uuid='1234'
        )


def test_area_execute(api):
    vector_tool = VectorTool(api)
    # execute
    output = {'result': 'test'}
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': '$area',
            'sql': 'test',
            "params": [
                {
                "name": "layer",
                "type": "Layer",
                "default_value": None,
                "domain": None
                },
            ]
        })]
    api.post.return_value = output
    result = vector_tool.area(
        vector_uuid='1234'
    )

    assert result == output


def test_area_save_as_layer(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': '$area',
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.area(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_as_geojson(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$as_geojson",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.as_geojson(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_as_wkt(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$as_wkt",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.as_wkt(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_buffer(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$buffer",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.buffer(
        vector_uuid='1234',
        distance=20,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_centroid(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$centroid",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.centroid(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_clip(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$clip",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.clip(
        vector_uuid='1234',
        clip_vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_concave_hull(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$concave_hull",
            'sql': 'test'
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.concave_hull(
        vector_uuid='1234',
        tolerance=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_convex_hull(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$convex_hull",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.convex_hull(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_feature_count_execute(api):
    vector_tool = VectorTool(api)
    # execute
    output = {'result': 'test'}
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': '$count',
            'sql': 'test',
            "params": [
                {
                "name": "layer",
                "type": "Layer",
                "default_value": None,
                "domain": None
                },
            ]
        })]
    api.post.return_value = output
    result = vector_tool.feature_count(
        vector_uuid='1234'
    )

    assert result == output


def test_count_point_in_polygons(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$count_point_in_polygons",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.count_point_in_polygons(
        polygon_vector_uuid='1234',
        point_vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_delaunay_triangulation(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$delaunay_triangulation",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.delaunay_triangulation(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_disjoint(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$disjoint",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.disjoint(
        vector_uuid='1234',
        filter_vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_dissolve(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$dissolve",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.dissolve(
        vector_uuid='1234',
        dissolve_field_name='field1',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_distance_to_nearest(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$distance_to_nearest",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.distance_to_nearest(
        vector_uuid='1234',
        nearest_vector_uuid='1234',
        search_radius=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_distinct(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$distinct",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.distinct(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_dump(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$dump",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.dump(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_erase(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$erase",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.erase(
        vector_uuid='1234',
        erase_vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_feature_bbox(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$feature_bbox",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.feature_bbox(
        vector_uuid='1234',
        srid=1234,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_feature_extent(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$feature_extent",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.feature_extent(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_find_and_replace(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$find_replace",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.find_and_replace(
        vector_uuid='1234',
        find="find",
        replace="replace",
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_from_geojson(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$from_geojson",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.from_geojson(
        vector_uuid='1234',
        json_field_name='field',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_from_wkt(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$from_wkt",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.from_wkt(
        vector_uuid='1234',
        wkt_column_name='field',
        srid=1234,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_generate_points(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$generate_points",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.generate_points(
        vector_uuid='1234',
        number_of_points=10,
        seed=1234,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_group_by(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$group_by",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.group_by(
        vector_uuid='1234',
        group_column_name='field1',
        agg_column_name='field2',
        agg_function=GroupByAggFunction.COUNT,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_hexagon_grid(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$hexagon_grid",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.hexagon_grid(
        vector_uuid='1234',
        cell_size=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_intersection(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$intersection",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.intersection(
        vector_uuid='1234',
        intersect_vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_join(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$join",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.join(
        vector1_uuid='1234',
        vector2_uuid='1234',
        vector1_join_column='field',
        vector2_join_column='field',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_lat_lon_to_point(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$lat_lon_to_point",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.lat_lon_to_point(
        latitude=10,
        longitude=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_layer_bbox(api):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$layer_bbox",
            'sql': 'test',
              "params": [
                {
                "name": "layer",
                "type": "Layer",
                "default_value": None,
                "domain": None
                },
                {
                "name": "srid",
                "type": "Integer",
                "default_value": 4326,
                "domain": {
                    "min": 1,
                    "max": 65536,
                    "items": None
                }
                }
            ],
        })]
    api.post.return_value = {'data': 'data'}
    result = vector_tool.layer_bbox(
        vector_uuid='1234',
        srid=1234
    )

    assert type(result) == dict


def test_layer_extent(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$layer_extent",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.layer_extent(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_length(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$length",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.length(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_linear_referencing(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$linear_referencing",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.linear_referencing(
        vector_uuid='1234',
        feature_id=1,
        dist=10,
        tolerance=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_line_to_polygon(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$line_to_polygon",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.line_to_polygon(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_make_envelop(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$make_envelop",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.make_envelop(
        xmin=1,
        ymin=2,
        xmax=3,
        ymax=4,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_merge(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$merge",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.merge(
        vector1_uuid='1234',
        vector2_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_network_trace(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$network_trace",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.network_trace(
        vector_uuid='1234',
        from_id=1,
        direction=NetworkTraceDirection.UP,
        tolerance=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_number_of_geoms(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$number_of_geoms",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.number_of_geoms(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_number_of_points(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$number_of_points",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.number_of_points(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_point_stats_in_polygon(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$point_stats_in_polygon",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.point_stats_in_polygon(
        polygon_vector_uuid='1234', 
        point_vector_uuid='1234', 
        stats_column='field', 
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_remove_holes(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$remove_holes",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.remove_holes(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_reverse_line(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$reverse_line",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.reverse_line(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_simplify(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$simplify",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.simplify(
        vector_uuid='1234',
        tolerance=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_snap_to_grid(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$snap_to_grid",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.snap_to_grid(
        vector_uuid='1234',
        grid_size=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_spatial_aggregation(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$spatial_aggregation",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.spatial_aggregation(
        vector_uuid='1234',
        agg_function=SpatialAggFunction.COLLECT,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_spatial_filter(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$spatial_filter",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.spatial_filter(
        vector_uuid='1234',
        spatial_predicate=SpatialPredicate.CONTAIN,
        filter_vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_spatial_group_by(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$spatial_group_by",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.spatial_group_by(
        vector_uuid='1234',
        group_column_name='field',
        agg_function=SpatialAggFunction.COLLECT,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_square_grid(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$square_grid",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.square_grid(
        vector_uuid='1234',
        cell_size=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_voronoi_polygons(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$voronoi_polygons",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.voronoi_polygons(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_within_distance(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$within_distance",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.within_distance(
        vector_uuid='1234',
        filter_vector_uuid='1234',
        dist=10,
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']


def test_xy_coordinate(api, mock_success_task_data):
    vector_tool = VectorTool(api)
    # execute
    api.get_system_queries.return_value = [Query(api=api, uuid='1234', 
        data={
            'name': "$xy_coordinate",
            'sql': 'test',
        })]
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    result = vector_tool.xy_coordinate(
        vector_uuid='1234',
        output_layer_name='test'
    )

    assert type(result) == Task
    assert result.uuid == mock_success_task_data['uuid']