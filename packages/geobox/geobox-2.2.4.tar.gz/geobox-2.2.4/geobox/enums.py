from enum import Enum

# File Enums
class InputGeomType(Enum):
    POINT = 'POINT'
    LINE = 'LINE'
    POLYGON = 'POLYGON'
    MULTIPOINT = 'MULTIPOINT'
    MULTILINE = 'MULTILINE'
    MULTIPOLYGON = 'MULTIPOLYGON'
    POINT_Z = 'POINTZ'
    LINE_Z = 'LINEZ'
    POLYGON_Z = 'POLYGONZ'
    MULTIPOINT_Z = 'MULTIPOINTZ'
    MULTILINE_Z = 'MULTILINEZ'
    MULTIPOLYGON_Z = 'MULTIPOLYGONZ'
    
class PublishFileType(Enum):
    VECTOR = 'vector'
    RASTER = 'raster'
    MODEL3D = 'model3d'
    Tiles3D = 'tiles3d'

class FileType(Enum):
    Compressed = 'Compressed'
    Complex = 'Complex'
    Image = 'Image'
    Video = 'Video'
    Document = 'Document'
    GPKG = 'GPKG'
    DXF = 'DXF'
    GPX = 'GPX'
    CSV = 'CSV'
    Shapefile = 'Shapefile'
    KML = 'KML'
    GLB = 'GLB'
    FileGDB = 'FileGDB'
    GeoTIFF = 'GeoTIFF'
    GeoJSON = 'GeoJSON'
    ThreedTiles = 'ThreedTiles'

class FileFormat(Enum):
    # Spatial Data Formats
    Shapefile = '.shp'
    FileGDB = '.gdb'
    CSV = '.csv'
    KML = '.kml'
    DXF = '.dxf'
    GPX = '.gpx'
    GPKG = '.gpkg'
    GeoJSON = '.geojson'
    # GeoTIFF = '.tiff'

    # Image Formats
    JPG = '.jpg'
    JPEG = '.jpeg'
    SVG = '.svg'
    PNG = '.png'
    BMP = '.bmp'
    TIF = '.tif'
    GIF = '.gif'

    # Video Formats
    MP4 = '.mp4'
    AVI = '.avi'
    OGG = '.ogg'
    WEBM = '.webm'
    MPEG = '.mpeg'
    WMV = '.wmv'

    # Document Formats
    TXT = '.txt'
    DOC = '.doc'
    DOCX = '.docx'
    XLS = '.xls'
    XLSX = '.xlsx'
    PPT = '.ppt'
    PPTX = '.pptx'
    PDF = '.pdf'

    # Compressed Formats
    ZIP = '.zip'
    SEVEN_Z = '.7z'  # 7z
    RAR = '.rar'
    ISO = '.iso'
    GZ = '.gz'
    BZ2 = '.bz2'
    TAR = '.tar'
    CAB = '.cab'
    IMG = '.img'


# Field Enums
class FieldType(Enum):
    """
    A class representing the data type of a field.
    """
    Integer = "Integer"
    """
    An integer field.
    """
    Float = "Float"
    """
    A float field.
    """
    String = "String"
    """
    A string field.
    """
    Long = "Long"
    """
    A Long field.
    """
    DATE = "Date"
    """
    A Date field.
    """
    TIME = "Time"
    """
    A Time Field.
    """
    DATETIME = "DateTime"
    """
    A DateTime Field.
    """


# Layer Enums
class LayerType(Enum):
    """
    Enumeration of supported vector layer geometry types.
    
    This enum defines the different types of geometric shapes that can be stored in a vector layer.
    Each type represents a specific geometric structure supported by the Geobox API.
    """
    Point = "Point"
    """A single point in 2D space"""
    
    MultiPoint = "MultiPoint"
    """A collection of points"""
    
    Polygon = "Polygon"
    """A closed shape defined by a sequence of points"""

    Polyline = "Polyline"
    """A polyline geometry"""


# Layer Enums
class FeatureType(Enum):
    """
    Enumeration of supported feature geometry types.
    
    This enum defines the different types of geometric shapes that can be stored in a feature.
    Each type represents a specific geometric structure supported by the Geobox API.
    """
    Point = "Point"
    """A single point in 2D space"""

    MultiPoint = "MultiPoint"
    """A collection of points"""
    
    LineString = "LineString"
    """A sequence of points forming a line"""

    MultiLineString = "MultiLineString"
    """A collection of lines"""
    
    Polygon = "Polygon"
    """A closed shape defined by a sequence of points"""
    
    MultiPolygon = "MultiPolygon"
    """A collection of polygons"""


# Task Enums
class TaskStatus(Enum):
    """
    Enumeration of possible task statuses.
    """
    PENDING = "PENDING"
    """
    The task is pending.
    """
    PROGRESS = "PROGRESS"
    """
    The task is in progress.
    """
    SUCCESS = "SUCCESS"
    """
    The task is successful.
    """
    FAILURE = "FAILURE"
    """
    The task is failed.
    """
    ABORTED = "ABORTED"
    """
    The task is aborted.
    """

class QueryGeometryType(Enum):
    """
    Enumeration of possible query geometry types.
    """
    POINT = "Point"
    """
    A point geometry.
    """
    MULTIPOINT = "Multipoint"
    """
    A multipoint geometry.
    """
    POLYLINE = "Polyline"
    """
    A polyline geometry.
    """
    POLYGON = "Polygon"
    """
    A polygon geometry.
    """

class QueryParamType(Enum):
    """
    Enumeration of possible query parameter types.
    """
    LAYER = "Layer"
    """
    A layer parameter.
    """
    ATTRIBUTE = "Attribute"
    """
    A Attribute parameter.
    """
    FLOAT = "Float"
    """
    A Float parameter.
    """
    INTEGER = "Integer"
    """
    A Integer parameter.
    """
    TEXT = "Text"
    """
    A Text parameter.
    """
    BOOLEAN = "Boolean"
    """
    A Boolean parameter.
    """


class UserRole(Enum):
    SYSTEM_ADMIN = "System Admin"

    ACCOUNT_ADMIN = "Account Admin"

    PUBLISHER = "Publisher"

    EDITOR = "Editor"

    VIEWER = "Viewer"


class UserStatus(Enum):
    NEW = "New"

    PENDING = "Pending"

    ACTIVE = "Active"

    DISABLED = "Disabled"


class MaxLogPolicy(Enum):
    OverwriteFirstLog = "OverwriteFirstLog"

    IgnoreLogging = "IgnoreLogging"


class InvalidDataPolicy(Enum):
    ReportToAdmin = "ReportToAdmin"

    LogOnly = "LogOnly"


class LoginFailurePolicy(Enum):
    BlockIPTemporarily = "BlockIPTemporarily"

    DisableAccount = "DisableAccount"


class MaxConcurrentSessionPolicy(Enum):
    CloseLastSession = "CloseLastSession"

    CloseMostInactiveSession = "CloseMostInactiveSession"

    PreventNewSession = "PreventNewSession"


class RoutingGeometryType(Enum):
    geojson = "geojson"

    polyline = "polyline"

    polyline6= "polyline6"


class RoutingOverviewLevel(Enum):
    Full = 'full'

    Simplified = 'simplified'


class QueryResultType(Enum):
    metadata = "metadata"

    data = "data"

    both = "both"


class FileOutputFormat(Enum):
    Shapefile = "Shapefile"

    GPKG = "GPKG"

    GeoJSON = "GeoJSON"

    CSV = "CSV"

    KML = "KML"

    DXF = "DXF"


class UsageScale(Enum):
    Hour = 'hour'

    Day = 'day'

    Month = 'month'


class UsageParam(Enum):
    Traffict = 'traffic'

    Calls = 'calls'


class AnalysisDataType(Enum):
    uint8 = 'uint8'
    uint16 = 'uint16'
    int16 = 'int16'
    uint32 = 'uint32'
    int32 = 'int32'
    float32 = 'float32'
    float64 = 'float64'


class PolygonizeConnectivity(Enum):
    connected_8 = 8
    connected_4 = 4


class AnalysisResampleMethod(Enum):
    near = 'near'
    bilinear = 'bilinear'
    cubic = 'cubic'
    cubicspline = 'cubicspline'
    lanczos = 'lanczos'
    average = 'average'
    mode = 'mode'
    max = 'max'
    min = 'min'
    med = 'med'
    q1 = 'q1'
    q3 = 'q3'
    rms = 'rms'
    sum = 'sum'


class SlopeUnit(Enum):
    degree = 'degree'
    percent = 'percent'


class AnalysisAlgorithm(Enum):
    Horn = 'Horn'
    ZevenbergenThorne = 'ZevenbergenThorne'


class RangeBound(Enum):
    left = 'left'
    right = 'right'
    both = 'both'
    neither = 'neither'


class DistanceUnit(Enum):
    GEO = 'GEO'
    PIXEL = 'PIXEL'


class GroupByAggFunction(Enum):
    COUNT = 'count'
    SUM = 'sum'
    MIN = 'min'
    MAX = 'max'
    AVG = 'avg'


class NetworkTraceDirection(Enum):
    UP = "up"
    DOWN = "down"


class SpatialAggFunction(Enum):
    COLLECT = 'collect'
    UNION = 'union'
    EXTENT = 'extent'
    MAKELINE = 'makeline'


class SpatialPredicate(Enum):
    INTERSECT = 'Intersect'
    CONTAIN = 'Contain'
    CROSS = 'Cross'
    EQUAL = 'Equal'
    OVERLAP = 'Overlap'
    TOUCH = 'Touch'
    WITHIN = 'Within'