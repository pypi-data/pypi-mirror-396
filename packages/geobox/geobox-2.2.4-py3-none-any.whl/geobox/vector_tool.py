from typing import Dict, Optional, TYPE_CHECKING, Union

from geobox.exception import NotFoundError

from .feature import Feature
from .base import Base
from .enums import GroupByAggFunction, NetworkTraceDirection, SpatialAggFunction, SpatialPredicate

if TYPE_CHECKING:
    from . import GeoboxClient
    from .task import Task
    from .query import Query



class VectorTool(Base):

    BASE_ENDPOINT = 'queries/'

    def __init__(self, api: 'GeoboxClient'):
        """
        Initialize a VectorTool instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
        """
        super().__init__(api)


    def __repr__(self) -> str:
        return f"VectorTool()"


    def _add_params_to_query(self, query_name: str, inputs: dict) -> 'Query':
        """add user input params to the query"""
        queries = self.api.get_system_queries(q=f"name = '{query_name}'")
        try:
            query = next(query for query in queries if query.name == query_name)
        except StopIteration:
            raise NotFoundError("Vector Tool not found!")

        for param in query.params:
            if param['name'] in inputs.keys():
                query.params[query.params.index(param)]['value'] = inputs[param['name']]

        return query


    def _run_query(self, query: 'Query', output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """execute or save as layer"""
        if not output_layer_name:
            response = query.execute()
            return response

        else:
            task = query.save_as_layer(layer_name=output_layer_name)
            return task


    def area(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Computes and adds a new column for the area of each polygon in the layer, aiding in spatial measurements
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.area(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.area(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$area', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def as_geojson(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Converts geometries to GeoJSON format, adding a column with GeoJSON strings for each geometry in the layer
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.as_geojson(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.as_geojson(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$as_geojson', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def as_wkt(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Converts geometries into WKT (Well-Known Text) format, storing it as a new column in the layer
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.as_wkt(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.as_wkt(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$as_wkt', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def buffer(self,
        vector_uuid: str,
        distance: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Generates a buffer zone around each geometry in the layer, expanding each shape by a specified distance
        
        Args:
            vector_uuid (str): UUID of the vector layer
            distance (float): Buffer distance
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")

            >>> # execution
            >>> result = client.vector_tool.buffer(vector_uuid=vector.uuid, distance=1000)
            
            >>> # save as layer
            >>> task = client.vector_tool.buffer(vector_uuid=vector.uuid, distance=1000, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'distance': distance
        }
        query = self._add_params_to_query(query_name='$buffer', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def centroid(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Calculates the centroid point of each geometry, which represents the geometric center of each shape
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.centroid(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.centroid(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$centroid', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def clip(self,
        vector_uuid: str,
        clip_vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Clips geometries and retains only the parts of the geometries that fall within the specified boundaries
        
        Args:
            vector_uuid (str): UUID of the vector layer
            clip_vector_uuid (str): UUID of the clip vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> clip_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.clip(vector_uuid=vector.uuid, clip_vector_uuid=clip_vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.clip(vector_uuid=vector.uuid, clip_vector_uuid=clip_vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'clip': clip_vector_uuid
        }
        query = self._add_params_to_query(query_name='$clip', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def concave_hull(self,
        vector_uuid: str,
        tolerance: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Creates a concave hull (a polygon that closely wraps around all geometries) for the layer with a specified tolerance
        
        Args:
            vector_uuid (str): UUID of the vector layer
            tolerance (float): Tolerance parameter for concave hull
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.concave_hull(vector_uuid=vector.uuid, tolerance=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.concave_hull(vector_uuid=vector.uuid, tolerance=10, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'tolerance': tolerance
        }
        query = self._add_params_to_query(query_name='$concave_hull', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def convex_hull(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Calculates a convex hull for all geometries in a layer, creating a polygon that minimally contains all points or shapes
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.convex_hull(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.convex_hull(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$convex_hull', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def feature_count(self, vector_uuid: str) -> Dict:
        """
        Counts the total number of rows in the specified layer, which is useful for data volume estimation
        
        Args:
            vector_uuid (str): UUID of the vector layer

        Returns:
            Dict: the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.feature_count(vector_uuid=vector.uuid)
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$count', inputs=inputs)
        return self._run_query(query=query)


    def count_point_in_polygons(self,
        polygon_vector_uuid: str,
        point_vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Counts the number of points within each polygon, giving a density measure of points per polygon
        
        Args:
            polygon_vector_uuid (str): UUID of the polygon layer
            point_vector_uuid (str): UUID of the point layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> polygon_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> point_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.count_point_in_polygons(
            ...     polygon_vector_uuid=polygon_vector.uuid,
            ...     point_vector_uuid=point_vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.count_point_in_polygons(
            ...     polygon_vector_uuid=polygon_vector.uuid,
            ...     point_vector_uuid=point_vector.uuid, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'polygon_layer': polygon_vector_uuid,
            'point_layer': point_vector_uuid
        }
        query = self._add_params_to_query(query_name='$count_point_in_polygons', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def delaunay_triangulation(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Generates Delaunay triangles from points, creating a tessellated network of polygons from input points
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.delaunay_triangulation(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.delaunay_triangulation(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$delaunay_triangulation', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def disjoint(self,
        vector_uuid: str,
        filter_vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Filters geometries that do not intersect with another layer, creating a subset with only disjoint geometries
        
        Args:
            vector_uuid (str): UUID of the vector layer
            filter_vector_uuid (str): UUID of the filter layer
            output_layer_name (str): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> filter_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.disjoint(vector_uuid=vector.uuid, filter_vector_uuid=filter_vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.disjoint(vector_uuid=vector.uuid, filter_vector_uuid=filter_vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid, 
            'filter_layer': filter_vector_uuid
        }
        query = self._add_params_to_query(query_name='$disjoint', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def dissolve(self,
        vector_uuid: str,
        dissolve_field_name: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Combines geometries based on a specified attribute, grouping them into single shapes for each unique attribute value
        
        Args:
            vector_uuid (str): UUID of the vector layer
            dissolve_field_name (str): Field to dissolve by
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.dissolve(vector_uuid=vector.uuid, dissolve_field_name="field_name")
            
            >>> # save as layer
            >>> task = client.vector_tool.dissolve(vector_uuid=vector.uuid, dissolve_field_name="field_name", output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid, 
            'dissolve_field': dissolve_field_name
        }
        query = self._add_params_to_query(query_name='$dissolve', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def distance_to_nearest(self,
        vector_uuid: str,
        nearest_vector_uuid: str,
        search_radius: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Calculates the minimum distance between geometries in one layer and their nearest neighbors in another
        
        Args:
            vector_uuid (str): UUID of the vector layer
            nearest_vector_uuid (str): UUID of the nearest layer
            search_radius (float): Search radius for nearest features
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> nearest_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.distance_to_nearest(
            ...     vector_uuid=vector.uuid, 
            ...     nearest_vector_uuid=nearest_vector.uuid, 
            ...     search_radius=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.distance_to_nearest(
            ...     vector_uuid=vector.uuid, 
            ...     nearest_vector_uuid=nearest_vector.uuid, 
            ...     search_radius=10, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid, 
            'nearest_layer': nearest_vector_uuid,
            'search_radius': search_radius
        }
        query = self._add_params_to_query(query_name='$distance_to_nearest', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def distinct(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Selects only unique rows from the input layer, removing duplicate entries across columns
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.distinct(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.distinct(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$distinct', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def dump(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Splits multi-part geometries into single-part geometries, producing individual shapes from complex collections
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.dump(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.dump(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$dump', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def erase(self,
        vector_uuid: str,
        erase_vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Removes portions of geometries that intersect with a specified erase layer, leaving only the non-overlapping parts
        
        Args:
            vector_uuid (str): UUID of the vector layer
            erase_vector_uuid (str): UUID of the erase layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> erase_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.erase(vector_uuid=vector.uuid, erase_vector_uuid=erase_vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.erase(vector_uuid=vector.uuid, erase_vector_uuid=erase_vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'erase': erase_vector_uuid
        }
        query = self._add_params_to_query(query_name='$erase', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def feature_bbox(self,
        vector_uuid: str,
        srid: int,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Adds a bounding box column to each feature, showing the min/max x and y coordinates as a text representation
        
        Args:
            vector_uuid (str): UUID of the vector layer
            srid (int): SRID for the output bounding boxes
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.feature_bbox(vector_uuid=vector.uuid, srid=4326)
            
            >>> # save as layer
            >>> task = client.vector_tool.feature_bbox(vector_uuid=vector.uuid, srid=4326, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'srid': srid
        }
        query = self._add_params_to_query(query_name='$feature_bbox', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def feature_extent(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Produces bounding boxes for each feature in the layer, representing the spatial extent of each geometry as a polygon
        
        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.feature_extent(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.feature_extent(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$feature_extent', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def find_and_replace(self,
        vector_uuid: str,
        find: str,
        replace: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Finds and replaces specified text in a column, updating values based on input patterns
        
        Args:
            vector_uuid (str): UUID of the vector layer
            find (str): Text to find
            replace (str): Text to replace with
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.find_and_replace(vector_uuid=vector.uuid, find="find example", replace="replce example")
            
            >>> # save as layer
            >>> task = client.vector_tool.find_and_replace(vector_uuid=vector.uuid, find="find example", replace="replce example", output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'find': find,
            'replace': replace
        }
        query = self._add_params_to_query(query_name='$find_replace', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def from_geojson(self,
        vector_uuid: str,
        json_field_name: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Converts GeoJSON strings in a specified column to geometries, adding these as a new column in the layer
        
        Args:
            vector_uuid (str): UUID of the vector layer
            json_field_name (str): Name of the column containing GeoJSON strings
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
        
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.from_geojson(vector_uuid=vector.uuid, json_field_name="json_field")
            
            >>> # save as layer
            >>> task = client.vector_tool.from_geojson(vector_uuid=vector.uuid, json_field_name="json_field", output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'json_field': json_field_name
        }
        query = self._add_params_to_query(query_name='$from_geojson', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def from_wkt(self,
        vector_uuid: str,
        wkt_column_name: str,
        srid: int,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Converts WKT strings in a specified column to geometries, adding them as a new column in the layer
        
        Args:
            vector_uuid (str): UUID of the vector layer
            wkt_column_name (str): Name of the column containing WKT strings
            srid (int): SRID for the output geometries
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
        
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.from_wkt(vector_uuid=vector.uuid, wkt_column_name="wkt_field")
            
            >>> # save as layer
            >>> task = client.vector_tool.from_wkt(vector_uuid=vector.uuid, wkt_column_name="wkt_field", output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'wkt_column': wkt_column_name,
            'srid': srid
        }
        query = self._add_params_to_query(query_name='$from_wkt', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def generate_points(self,
        vector_uuid: str,
        number_of_points: int,
        seed: int,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Generates random points within each polygon, creating a specified number of points for each geometry
        
        Args:
            vector_uuid (str): UUID of the vector layer
            number_of_points (int): Number of points to generate per polygon
            seed (int): Random seed for reproducible results
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
        
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.generate_points(vector_uuid=vector.uuid, number_of_points=10, seed=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.generate_points(vector_uuid=vector.uuid, number_of_points=10, seed=10, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'number_of_points': number_of_points,
            'seed': seed
        }
        query = self._add_params_to_query(query_name='$generate_points', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def group_by(self,
        vector_uuid: str,
        group_column_name: str,
        agg_column_name: str,
        agg_function: 'GroupByAggFunction',
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Groups the layer by a specified column, applying aggregation functions like count, sum, min, max, and average
        
        Args:
            vector_uuid (str): UUID of the vector layer
            group_column_name (str): Column to group by
            agg_column_name (str): Column to aggregate
            agg_function (GroupByAggFunction): Aggregation function: count, sum, min, max, avg
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
            
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vector_tool import GroupByAggFunction
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.group_by(
            ...     vector_uuid=vector.uuid, 
            ...     group_column_name="field_1", 
            ...     agg_column_name="field_2", 
            ...     agg_function=GroupByAggFunction.SUM)
            
            >>> # save as layer
            >>> task = client.vector_tool.group_by(
            ...     vector_uuid=vector.uuid, 
            ...     group_column_name="field_1", 
            ...     agg_column_name="field_2", 
            ...     agg_function=GroupByAggFunction.SUM, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'group_column': group_column_name,
            'agg_column': agg_column_name,
            'agg_function': agg_function.value
        }
        query = self._add_params_to_query(query_name='$group_by', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def hexagon_grid(self,
        vector_uuid: str,
        cell_size: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Creates a grid of hexagons over the layer extent, counting the number of features intersecting each hexagon
        
        Args:
            vector_uuid (str): UUID of the vector layer
            cell_size (float): Size of hexagon cells
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
        
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.hexagon_grid(
            ...     vector_uuid=vector.uuid, 
            ...     cell_size=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.hexagon_grid(
            ...     vector_uuid=vector.uuid, 
            ...     cell_size=10, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'cell_size': cell_size
        }
        query = self._add_params_to_query(query_name='$hexagon_grid', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def intersection(self,
        vector_uuid: str,
        intersect_vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Calculates intersections between geometries in two layers, retaining only overlapping portions

        Args:
            vector_uuid (str): UUID of the vector layer
            intersect_vector_uuid (str): UUID of the intersect layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
        
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> intersect_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.hexagon_grid(
            ...     vector_uuid=vector.uuid, 
            ...     intersect_vector_uuid=intersect_vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.hexagon_grid(
            ...     vector_uuid=vector.uuid, 
            ...     intersect_vector_uuid=intersect_vector.uuid, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'intersect': intersect_vector_uuid
        }
        query = self._add_params_to_query(query_name='$intersection', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def join(self,
        vector1_uuid: str,
        vector2_uuid: str,
        vector1_join_column: str,
        vector2_join_column: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Joins two layers based on specified columns, combining attributes from both tables into one

        Args:
            vector1_uuid (str): UUID of the first vector layer
            vector2_uuid (str): UUID of the second vector layer
            vector1_join_column (str): Join column from first layer
            vector2_join_column (str): Join column from second layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
        
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector1 = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> vector2 = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.join(
            ...     vector1_uuid=vector1.uuid,
            ...     vector2_uuid=vector2.uuid, 
            ...     vector1_join_column="vector1_field_name", 
            ...     vector2_join_column="vector2_field_name")
            
            >>> # save as layer
            >>> task = client.vector_tool.join(
            ...     vector1_uuid=vector1.uuid,
            ...     vector2_uuid=vector2.uuid, 
            ...     vector1_join_column="vector1_field_name", 
            ...     vector2_join_column="vector2_field_name", 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer1': vector1_uuid,
            'layer2': vector2_uuid,
            'layer1_join_column': vector1_join_column,
            'layer2_join_column': vector2_join_column
        }
        query = self._add_params_to_query(query_name='$join', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def lat_lon_to_point(self,
        latitude: float,
        longitude: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Converts latitude and longitude values to a point geometry, storing it as a new feature

        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
        
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            
            >>> # execution
            >>> result = client.vector_tool.lat_lon_to_point(
            ...     latitude=10, 
            ...     longitude=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.lat_lon_to_point(
            ...     latitude=10, 
            ...     longitude=10, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'latitude': latitude,
            'longitude': longitude
        }
        query = self._add_params_to_query(query_name='$lat_lon_to_point', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def layer_bbox(self,
        vector_uuid: str,
        srid: int) -> Dict:
        """
        Computes the bounding box for all geometries in the layer, outputting it as a single text attribute

        Args:
            vector_uuid (str): UUID of the vector layer
            srid (int): SRID for the output bounding box

        Returns:
            Dict: the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.layer_bbox(vector_uuid=vector.uuid, srid=4326)
        """
        inputs = {
            'layer': vector_uuid,
            'srid': srid
        }
        query = self._add_params_to_query(query_name='$layer_bbox', inputs=inputs)
        return self._run_query(query=query)


    def layer_extent(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Calculates the spatial extent of the entire layer, producing a bounding box polygon around all geometries

        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.layer_extent(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.layer_extent(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$layer_extent', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def length(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Computes the length of line geometries in the layer, adding it as an attribute for each feature

        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.length(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.length(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$length', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def linear_referencing(self,
        vector_uuid: str,
        feature_id: int,
        dist: float,
        tolerance: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Returns points separated at a specified distance along a line, based on linear referencing techniques

        Args:
            vector_uuid (str): UUID of the vector layer
            feature_id (int): ID of the feature to reference
            dist (float): Distance along the line
            tolerance (float): Tolerance for point placement
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = vector.get_features()
            
            >>> # execution
            >>> result = client.vector_tool.linear_referencing(
            ...     vector_uuid=vector.uuid,
            ...     feature_id=feature.id,
            ...     dist=10,
            ...     tolerance=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.linear_referencing(
            ...     vector_uuid=vector.uuid,
            ...     feature_id=feature.id,
            ...     dist=10,
            ...     tolerance=10,
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'feature_id': feature_id,
            'dist': dist,
            'tolerance': tolerance
        }
        query = self._add_params_to_query(query_name='$linear_referencing', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def line_to_polygon(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Converts line geometries into polygons by closing the line segments to form closed shapes

        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.line_to_polygon(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.line_to_polygon(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$line_to_polygon', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def make_envelop(self,
        xmin: float,
        ymin: float,
        xmax: float,
        ymax: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Generates a rectangular bounding box based on provided minimum and maximum x and y coordinates

        Args:
            xmin (float): Minimum x coordinate
            ymin (float): Minimum y coordinate
            xmax (float): Maximum x coordinate
            ymax (float): Maximum y coordinate
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.make_envelop(xmin=10. ymin=10, xmax=10, ymax=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.make_envelop(xmin=10. ymin=10, xmax=10, ymax=10, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax,
        }
        query = self._add_params_to_query(query_name='$make_envelop', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def merge(self,
        vector1_uuid: str,
        vector2_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Combines two layers into one by uniting their attributes and geometries, forming a single cohesive layer

        Args:
            vector1_uuid (str): UUID of the first vector layer
            vector2_uuid (str): UUID of the second vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

            Returns:
                Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector1 = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> vector2 = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.merge(vector1_uuid=vector1.uuid, vector2_uuid=vector2.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.merge(vector1_uuid=vector1.uuid, vector2_uuid=vector2.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer1': vector1_uuid,
            'layer2': vector2_uuid
        }
        query = self._add_params_to_query(query_name='$merge', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def network_trace(self,
        vector_uuid: str,
        from_id: int,
        direction: NetworkTraceDirection,
        tolerance: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Performs a recursive spatial network trace, traversing connected lines based on specified direction and tolerance

        Args:
            vector_uuid (str): UUID of the vector layer
            from_id (int): Starting feature ID for the trace
            direction (NetworkTraceDirection): Direction of trace: UP(upstream) or DOWN(downstream)
            tolerance (float): Tolerance for network connectivity
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.network_trace(
            ...     vector_uuid=vector1.uuid, 
            ...     from_id=10,
            ...     direction=NetworkTraceDirection.UP,
            ...     tolerance=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.network_trace(
            ...     vector_uuid=vector1.uuid, 
            ...     from_id=10,
            ...     direction=NetworkTraceDirection.UP,
            ...     tolerance=10), 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'from_id': from_id,
            'direction': direction,
            'tolerance': tolerance
        }
        query = self._add_params_to_query(query_name='$network_trace', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def number_of_geoms(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Counts the number of geometry parts in each multi-part shape, adding this count as a new column

        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.number_of_geoms(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.number_of_geoms(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$number_of_geoms', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def number_of_points(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Counts the number of vertices in each geometry, providing an attribute with this point count

        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.number_of_points(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.number_of_points(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$number_of_points', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def point_stats_in_polygon(self,
        polygon_vector_uuid: str,
        point_vector_uuid: str,
        stats_column: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Aggregates statistical data for points within each polygon, calculating sum, average, minimum, and maximum

        Args:
            polygon_vector_uuid (str): UUID of the polygon layer
            point_vector_uuid (str): UUID of the point layer
            stats_column (str): Column to calculate statistics on
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> polygon_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> point_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.point_stats_in_polygon(
            ...     polygon_vector_uuid=polygon_vector.uuid,
            ...     point_vector_uuid=point_vector.uuid,
            ...     stats_column="field_name")
            
            >>> # save as layer
            >>> task = client.vector_tool.point_stats_in_polygon(
            ...     polygon_vector_uuid=polygon_vector.uuid,
            ...     point_vector_uuid=point_vector.uuid,
            ...     stats_column="field_name"),
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'polygon_layer': polygon_vector_uuid, 
            'point_layer': point_vector_uuid, 
            'stats_column': stats_column
        }
        query = self._add_params_to_query(query_name='$point_stats_in_polygon', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def remove_holes(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Removes interior holes from polygon geometries, leaving only the outer boundary of each shape

        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.remove_holes(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.remove_holes(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$remove_holes', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def reverse_line(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Reverses the direction of line geometries, swapping start and end points of each line

        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.reverse_line(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.reverse_line(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$reverse_line', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def simplify(self,
        vector_uuid: str,
        tolerance: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Simplifies geometries based on a tolerance value, reducing detail while preserving general shape

        Args:
            vector_uuid (str): UUID of the vector layer
            tolerance (float): Simplification tolerance
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.simplify(
            ...     vector_uuid=vector.uuid
            ...     tolerance=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.simplify(
            ...     vector_uuid=vector.uuid
            ...     tolerance=10,
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'tolerance': tolerance
        }
        query = self._add_params_to_query(query_name='$simplify', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def snap_to_grid(self,
        vector_uuid: str,
        grid_size: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Aligns geometries to a grid of a specified size, rounding coordinates to fall on the grid lines

        Args:
            vector_uuid (str): UUID of the vector layer
            grid_size (float): Size of the grid cells
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.snap_to_grid(
            ...     vector_uuid=vector.uuid
            ...     grid_size=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.snap_to_grid(
            ...     vector_uuid=vector.uuid
            ...     grid_size=10,
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'grid_size': grid_size
        }
        query = self._add_params_to_query(query_name='$snap_to_grid', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def spatial_aggregation(self,
        vector_uuid: str,
        agg_function: 'SpatialAggFunction',
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Aggregates geometries by performing spatial functions like union or extent on all geometries in the layer

        Args:
            vector_uuid (str): UUID of the vector layer
            agg_function (SpatialAggFunction): Aggregation function: collect, union, extent, makeline
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vector_tool import SpatialAggFunction
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.spatial_aggregation(
            ...     vector_uuid=vector.uuid
            ...     agg_function=SpatialAggFunction.COLLECT)
            
            >>> # save as layer
            >>> task = client.vector_tool.spatial_aggregation(
            ...     vector_uuid=vector.uuid
            ...     agg_function=SpatialAggFunction.COLLECT,
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'agg_function': agg_function
        }
        query = self._add_params_to_query(query_name='$spatial_aggregation', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def spatial_filter(self,
        vector_uuid: str,
        spatial_predicate: 'SpatialPredicate',
        filter_vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Filters features in a layer based on spatial relationships with a filter layer, such as intersects, contains, or within

        Args:
            vector_uuid (str): UUID of the vector layer
            spatial_predicate (SpatialPredicate): Spatial predicate: Intersect, Contain, Cross, Equal, Overlap, Touch, Within
            filter_vector_uuid (str): UUID of the filter layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vector_tool import SpatialAggFunction
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> filter_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.spatial_filter(
            ...     vector_uuid=vector.uuid
            ...     spatial_predicate=SpatialPredicate.INTERSECT,
            ...     filter_vector_uuid=filter_vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.spatial_filter(
            ...     vector_uuid=vector.uuid
            ...     spatial_predicate=SpatialPredicate.INTERSECT,
            ...     filter_vector_uuid=filter_vector.uuid,
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid, 
            'spatial_predicate': spatial_predicate, 
            'filter_layer': filter_vector_uuid
        }
        query = self._add_params_to_query(query_name='$spatial_filter', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def spatial_group_by(self,
        vector_uuid: str,
        group_column_name: str,
        agg_function: 'SpatialAggFunction',
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Groups geometries by a specified column and aggregates them using spatial functions like union, collect, or extent
        
        Args:
            vector_uuid (str): UUID of the vector layer
            group_column_name (str): Column to group by
            agg_function (SpatialAggFunction): Spatial aggregation function: collect, union, extent, makeline
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
            
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vector_tool import GroupByAggFunction
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.spatial_group_by(
            ...     vector_uuid=vector.uuid, 
            ...     group_column_name="field_1", 
            ...     agg_function=SpatialAggFunction.COLLECT)
            
            >>> # save as layer
            >>> task = client.vector_tool.spatial_group_by(
            ...     vector_uuid=vector.uuid, 
            ...     group_column_name="field_1", 
            ...     agg_function=SpatialAggFunction.COLLECT, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'group_column': group_column_name,
            'agg_function': agg_function.value
        }
        query = self._add_params_to_query(query_name='$spatial_group_by', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def square_grid(self,
        vector_uuid: str,
        cell_size: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Generates a square grid across the layer extent, counting how many geometries intersect each square cell

        Args:
            vector_uuid (str): UUID of the vector layer
            cell_size (float): Size of square grid cells
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.
        
        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.square_grid(
            ...     vector_uuid=vector.uuid, 
            ...     cell_size=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.square_grid(
            ...     vector_uuid=vector.uuid, 
            ...     cell_size=10, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'cell_size': cell_size
        }
        query = self._add_params_to_query(query_name='$square_grid', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def voronoi_polygons(self,
        vector_uuid: str,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Creates Voronoi polygons from input points, partitioning the space so each polygon surrounds a unique point

        Args:
            vector_uuid (str): UUID of the vector layer
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.voronoi_polygons(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.voronoi_polygons(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid
        }
        query = self._add_params_to_query(query_name='$voronoi_polygons', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def within_distance(self,
        vector_uuid: str,
        filter_vector_uuid: str,
        dist: float,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Filters geometries that are within a specified distance of a filter layer, useful for proximity analysis

        Args:
            vector_uuid (str): UUID of the vector layer
            filter_vector_uuid (str): UUID of the filter layer
            dist (float): Search distance
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> filter_vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.within_distance(
            ...     vector_uuid=vector.uuid,
            ...     filter_vector_uuid=filter_vector=filter_vector.uuid,
            ...     dist=10)
            
            >>> # save as layer
            >>> task = client.vector_tool.within_distance(
            ...     vector_uuid=vector.uuid,
            ...     filter_vector_uuid=filter_vector=filter_vector.uuid,
            ...     dist=10, 
            ...     output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'filter_layer': filter_vector_uuid,
            'dist': dist
        }
        query = self._add_params_to_query(query_name='$within_distance', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)


    def xy_coordinate(self,
        vector_uuid: str,
        srid: Optional[int] = Feature.BASE_SRID,
        output_layer_name: Optional[str] = None) -> Union['Task', Dict]:
        """
        Extracts the X and Y coordinates for each geometry in a layer, adding coord_x and coord_y columns

        Args:
            vector_uuid (str): UUID of the vector layer
            srid (int, optional): SRID for coordinate extraction. default: 3857
            output_layer_name (str, optional): Name for the output layer. name must be a valid identifier and without spacing.

        Returns:
            Union['Task', Dict]: If output_layer_name is specified, the function returns a task object; if not, it returns the vector tool execution result.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> vector = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            
            >>> # execution
            >>> result = client.vector_tool.xy_coordinate(vector_uuid=vector.uuid)
            
            >>> # save as layer
            >>> task = client.vector_tool.xy_coordinate(vector_uuid=vector.uuid, output_layer_name="output_layer")
            >>> task.wait()
            >>> output_layer = task.output_asset
        """
        inputs = {
            'layer': vector_uuid,
            'srid': srid
        }
        query = self._add_params_to_query(query_name='$xy_coordinate', inputs=inputs)
        return self._run_query(query=query, output_layer_name=output_layer_name)