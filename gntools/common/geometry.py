# coding: utf-8
#
# Copyright 2019 Geocom Informatik AG / VertiGIS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
GEONIS-specific module to handle or parse Esri geometries.
"""

import json as _json
import math as _math
from xml.etree import cElementTree as _Xml

import gpf.common.iterutils as _iter
import gpf.common.validate as _vld

_JSON_NAN = 'NaN'
_JSON_PATHS = 'paths'
_JSON_CURVEPATHS = 'curvePaths'
_JSON_RINGS = 'rings'
_JSON_CURVERINGS = 'curveRings'
_JSON_X = 'x'
_JSON_Y = 'y'

_XML_X = _JSON_X
_XML_Y = _JSON_Y
_XML_TRUE = 'true'
_XML_FALSE = 'false'

_CURVE_CARC = 'c'
_CURVE_EARC = 'a'
_CURVE_BEZIER = 'b'

_TAG_GEOMETRY = 'geometry'
_TAG_POINT = 'Point'
_TAG_POLYLINE = 'Polyline'
_TAG_POLYGON = 'Polygon'
_TAG_PATH = 'Path'
_TAG_RING = 'Ring'
_TAG_LINE = 'Line'
_TAG_CARC = 'CircularArc'
_TAG_BEZIER = 'BezierCurve'
_TAG_EARC = 'EllipticArc'

_ATTR_ENUM = 'esrienum'
_ATTR_CCW = 'isCCW'
_ATTR_ANGLE = 'RotationAngle'
_ATTR_MINOR = 'isMinor'
_ATTR_RATIO = 'minorMajorRatio'
_ATTR_ESTD = 'ellipseStd'
_ATTR_EXT = 'isexterior'

# Supported Esri geometry types
# Reference: https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#esriGeometryType.htm
_ESRI_ENUM_POINT = 1
_ESRI_ENUM_POLYLINE = 3
_ESRI_ENUM_POLYGON = 4
_ESRI_ENUM_PATH = 6
_ESRI_ENUM_RING = 11
_ESRI_ENUM_LINE = 13
_ESRI_ENUM_CARC = 14
_ESRI_ENUM_BEZIER = 15
_ESRI_ENUM_EARC = 16

# Use fairly accurate tolerance, so we don't screw up the arcs (midpoints)
XY_TOLERANCE = 1e-09


class GeometrySerializationError(ValueError):
    pass


def _get_slopes(p1, p2, p3):
    """ Calculates the slopes between `p1` and `p2`, and `p2` and `p3`. Returns a tuple (slope_a, slope_b). """

    dx_a = p2[0] - p1[0]
    dy_a = float(p2[1] - p1[1])
    dx_b = p3[0] - p2[0]
    dy_b = float(p3[1] - p2[1])

    if _math.fabs(dx_a) <= XY_TOLERANCE and _math.fabs(dy_b) <= XY_TOLERANCE:
        return None, None

    return dy_a / dx_a, dy_b / dx_b


def _get_distance(p1, p2):
    """ Calculates the simple Euclidean distance between `p1` and `p2`. """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return _math.sqrt(dx * dx + dy * dy)


def _is_perpendicular(p1, p2, p3):
    """ Looks if the 3 input points are perpendicular and/or parallel to on another. """

    dx_a = p2[0] - p1[0]
    dy_a = p2[1] - p1[1]
    dx_b = p3[0] - p2[0]
    dy_b = p3[1] - p2[1]

    if _math.fabs(dx_a) <= XY_TOLERANCE and _math.fabs(dy_b) <= XY_TOLERANCE:
        # Points are perpendicular and parallel to x-y axis
        return False

    if _math.fabs(dy_a) <= XY_TOLERANCE or _math.fabs(dy_b) <= XY_TOLERANCE:
        # A line of two points is perpendicular to x-axis 1 or 2
        return True

    if _math.fabs(dx_a) <= XY_TOLERANCE or _math.fabs(dx_b) <= XY_TOLERANCE:
        # A line of two points is perpendicular to y-axis 1 or 2
        return True

    return False


def _reorder(p1, p2, p3):
    """ Returns a tuple of the input points, possibly reordered such that no points are perpendicular. """

    if not _is_perpendicular(p1, p2, p3):
        return p1, p2, p3
    elif not _is_perpendicular(p1, p3, p2):
        return p1, p3, p2
    elif not _is_perpendicular(p2, p1, p3):
        return p2, p1, p3
    elif not _is_perpendicular(p2, p3, p1):
        return p2, p3, p1
    elif not _is_perpendicular(p3, p2, p1):
        return p3, p2, p1
    elif not _is_perpendicular(p3, p1, p2):
        return p3, p1, p2
    else:
        raise GeometrySerializationError('All arc points are perpendicular')


def get_angle(center_point, from_arcpoint, to_arcpoint):
    """
    Calculates and returns the angle of a center-point arc in degrees.

    :param center_point:    Arc center point (``(x, y)``).
    :param from_arcpoint:   The start point of the arc (``(x, y, ...)``).
    :param to_arcpoint:     The last point of the arc (``(x, y, ...)``).
    :type center_point:     tuple, list
    :type from_arcpoint:    tuple, list
    :type to_arcpoint:      tuple, list
    :return:                An angle in degrees.
    :rtype:                 float
    """
    radius = _get_distance(from_arcpoint, center_point)
    chord = _get_distance(from_arcpoint, to_arcpoint)
    return _math.degrees(2 * _math.asin(chord / (2.0 * radius)))


def get_arc_center(start_point, mid_point, end_point):
    """
    Calculates and returns the center point as a tuple of (x, y) for the defined 3-point arc points.

    :param start_point: First point (``(x, y, ...)``).
    :param mid_point:   Middle or other point on the arc (``(x, y, ...)``).
    :param end_point:   Last point (``(x, y, ...)``).
    :type start_point:  tuple, list
    :type mid_point:    tuple, list
    :type end_point:    tuple, list
    :return:            A tuple of X, Y ``float`` values.
    :rtype:             tuple
    """
    p1, p2, p3 = _reorder(start_point, mid_point, end_point)

    x1, y1 = p1[:2]
    x2, y2 = p2[:2]
    x3, y3 = p3[:2]

    slope_a, slope_b = _get_slopes(p1, p2, p3)
    if slope_a is None and slope_b is None:
        return 0.5 * (x2 + x3), 0.5 * (y1 + y2)

    if _math.fabs(slope_a - slope_b) <= XY_TOLERANCE:
        raise GeometrySerializationError('All arc points are colinear')

    x = (slope_a * slope_b * (y1 - y3) + slope_b * (x1 + x2) - slope_a * (x2 + x3)) / 2.0 * (slope_b - slope_a)
    y = -1.0 * (x - (x1 + x2) / 2.0) / slope_a + (y1 + y2) / 2.0
    return x, y


def is_minor(start_point, mid_point, end_point):
    """
    Returns ``True`` when the defined 3-point arc is minor (less than 180 degrees).

    :param start_point: First point (``(x, y, ...)``).
    :param mid_point:   Middle or other point on the arc (``(x, y, ...)``).
    :param end_point:   Last point (``(x, y, ...)``).
    :type start_point:  tuple, list
    :type mid_point:    tuple, list
    :type end_point:    tuple, list
    :rtype:             bool
    """
    center = get_arc_center(start_point, mid_point, end_point)
    return get_angle(center, start_point, end_point) < 180


def is_clockwise(ring):
    """
    Returns ``True`` when the given list or tuple of polygon ring coordinates turns clockwise.

    This is achieved by calculating an area approximation for the ring using the Shoelace formula.
    When the area is positive, the ring turns clockwise. When negative, the ring turns counterclockwise.

    :param ring:    An EsriJSON ring.
    :type ring:     tuple, list
    :rtype:         bool
    """
    if not all(isinstance(v, (list, tuple)) for v in ring):
        # If the ring contains arcs, we'll simplify it to a list of coordinates.
        # Note that this will no longer produce an accurate area.
        ring = _simplify_ring(ring)

    return ((sum(pair[0][0] * pair[1][1] for pair in zip(ring[:-1], ring[1:])) +
             sum(-(pair[1][0] * pair[0][1]) for pair in zip(ring[:-1], ring[1:]))) / 2.0) > 0


def _fix_start(start_object):
    """
    If `start_object` is not a point iterable but a curve object, `start_object` is set to the curves' end point.

    :param start_object:    A start point iterable or curve object.
    :return:                A 'true' start point.
    """
    if isinstance(start_object, dict):
        # The start point needs to be derived from the end point of the curve object
        return _read_curve(start_object)[1][0]
    return start_object


def _read_curve(curve_object):
    """
    Extracts a tuple of (curve type, curve properties) from the single `curve_object` key-value pair.

    :param curve_object:    The curve object dictionary (key-value pair).
    :rtype:                 tuple
    """
    return _iter.first(curve_object.iteritems())


def _simplify_ring(ring):
    """
    Returns a "simplified" version of a polygon ring (list of coordinates).
    If the polygon contains arcs, only their start and end points (and control points) will be taken.
    Note that this might produce invalid geometries.
    This function should therefore only be used by the :func:`is_clockwise` function.

    :param ring:    A list or tuple of polygon ring coordinates.
    :rtype:         list
    """
    coords = []
    for point in ring:
        if isinstance(point, dict):
            # We are dealing with an arc/curve
            curve_type, curve_points = _read_curve(point)
            if curve_type == _CURVE_CARC:
                # For circular arcs, add the midpoint, followed by the end point
                coords.extend(reversed(curve_points))
            elif curve_type == _CURVE_EARC:
                # For elliptical arcs, simply add the end point for now: todo
                coords.append(curve_points[0])
            elif curve_type == _CURVE_BEZIER:
                # For bezier curves, add the control points, followed by the end point
                coords.extend(curve_points[:1])
                coords.append(curve_points[0])
        else:
            coords.append(point)
    return coords


def _serialize_point(x, y):
    """
    Serializes the EsriJSON point to XML.

    :param x:   Coordinate X value.
    :param y:   Coordinate Y value.
    :return:    An XML 'Point' element.
    """
    if x in (None, _JSON_NAN) or y in (None, _JSON_NAN):
        raise GeometrySerializationError('Points should have valid numeric X and Y values')
    return _Xml.Element(_TAG_POINT, {_ATTR_ENUM: str(_ESRI_ENUM_POINT), _XML_X: str(x), _XML_Y: str(y)})


def _serialize_line(p1, p2):
    """
    Serializes the EsriJSON line to XML.

    :param p1:  First point [x, y, ...] or last curve object.
    :param p2:  Second point [x, y, ...].
    :return:    An XML 'Line' element.
    """
    p1 = _fix_start(p1)
    line_xml = _Xml.Element(_TAG_LINE, {_ATTR_ENUM: str(_ESRI_ENUM_LINE)})
    line_xml.append(_serialize_point(*p1[:2]))
    line_xml.append(_serialize_point(*p2[:2]))
    return line_xml


def _serialize_carc(start_point, end_point, interior_point):
    """
    Serializes the EsriJSON circular arc to XML.

    :param start_point:     Start point [x, y, ...]
    :param end_point:       End point [x, y, ...]
    :param interior_point:  Interior a.k.a. midpoint [x, y, ...]
    :return:                An XML 'CircularArc' element.
    """
    curve_xml = _Xml.Element(_TAG_CARC, {
        _ATTR_ENUM: str(_ESRI_ENUM_CARC),
        _ATTR_CCW: _XML_FALSE if is_clockwise([start_point, interior_point, end_point, start_point]) else _XML_TRUE,
        _ATTR_MINOR: _XML_TRUE if is_minor(start_point, interior_point, end_point) else _XML_FALSE
    })
    curve_xml.append(_serialize_point(*interior_point[:2]))
    curve_xml.append(_serialize_point(*start_point[:2]))
    curve_xml.append(_serialize_point(*end_point[:2]))
    return curve_xml


def _serialize_earc(start_point, *args):
    """
    Serializes the EsriJSON elliptic arc to XML.

    :param start_point:     Start point [x, y, ...]
    :param args:            Values `end_point`, `center_point`, `minor`, `cw`, `rotation`, `axis` and `ratio`.
    :return:                An XML 'EllipticArc' element.
    """
    end_point, center_point, _, cw, rotation, _, ratio = args
    curve_xml = _Xml.Element(_TAG_EARC, {
        _ATTR_ENUM: str(_ESRI_ENUM_EARC),
        _ATTR_ESTD: _XML_FALSE,
        _ATTR_CCW: _XML_FALSE if cw else _XML_TRUE,
        _ATTR_ANGLE: str(rotation),
        _ATTR_RATIO: str(ratio)
    })
    curve_xml.append(_serialize_point(*center_point[:2]))
    curve_xml.append(_serialize_point(*start_point[:2]))
    curve_xml.append(_serialize_point(*end_point[:2]))
    return curve_xml


def _serialize_bezier(start_point, end_point, control_p1, control_p2):
    """
    Serializes the EsriJSON bezier curve object to XML.
    More info: https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#IBezierCurve_QueryCoord.htm

    :param start_point:     Start point [x, y, ...]
    :param end_point:       End point [x, y, ...]
    :param control_p1:      Control point 1 [x, y]
    :param control_p2:      Control point 2 [x, y]
    :return:                An XML 'BezierCurve' element.
    """
    curve_xml = _Xml.Element(_TAG_BEZIER, {_ATTR_ENUM: str(_ESRI_ENUM_BEZIER)})
    curve_xml.append(_serialize_point(*start_point[:2]))
    curve_xml.append(_serialize_point(*control_p1[:2]))
    curve_xml.append(_serialize_point(*end_point[:2]))
    curve_xml.append(_serialize_point(*control_p2[:2]))
    return curve_xml


def _serialize_curve(start_object, curve_object):
    """
    Serializes the EsriJSON curve object definition to XML.

    :param start_object:    The start point (x, y) for the curve or the previous curve object.
    :param curve_object:    An EsriJSON curve object value (dict).
    :return:                An XML 'CircularArc', 'EllipticArc' or 'BezierCurve' element.
    """
    start_point = _fix_start(start_object)
    curve_type, curve_points = _read_curve(curve_object)
    if curve_type == _CURVE_CARC:
        return _serialize_carc(start_point, *curve_points)
    elif curve_type == _CURVE_EARC:
        return _serialize_earc(start_point, *curve_points)
    elif curve_type == _CURVE_BEZIER:
        return _serialize_bezier(start_point, *curve_points)
    raise GeometrySerializationError('{!r} is an unsupported curve object type')


def _serialize_ring(ring):
    """
    Serializes the EsriJSON ring definition to XML.

    :param ring:    A single EsriJSON 'curveRings' or 'rings' object value.
    :return:        An XML 'Ring' element.
    """
    # Calculate "isexterior" property: Esri defines this as "ring orientation is clockwise, area > 0".
    is_ext = is_clockwise(ring)
    ring_xml = _Xml.Element(_TAG_RING,
                            {_ATTR_ENUM: str(_ESRI_ENUM_RING), _ATTR_EXT: _XML_TRUE if is_ext else _XML_FALSE})
    _serialize_path(ring, ring_xml)
    return ring_xml


def _serialize_path(path, parent_node):
    """
    Serializes an EsriJSON `path` to XML and adds the elements to `parent_node`.

    :param path:    A single EsriJSON 'curvePaths/Rings' or 'paths/rings' object value.
    """
    for p1, p2 in zip(path, path[1:]):
        if isinstance(p2, list):
            parent_node.append(_serialize_line(p1, p2))
        elif isinstance(p2, dict):
            parent_node.append(_serialize_curve(p1, p2))


def _serialize_polyline(polyline):
    """
    Serializes the EsriJSON polyline definition to XML.

    Note that multipart polylines will consist of multiple Path elements.
    :param polyline:    An EsriJSON 'curvePaths' or 'paths' object value.
    :return:            An XML 'Polyline' element.
    """
    _vld.pass_if(polyline, GeometrySerializationError, 'Polyline does not have any geometry parts')

    polyline_xml = _Xml.Element(_TAG_POLYLINE, {_ATTR_ENUM: str(_ESRI_ENUM_POLYLINE)})
    is_multi = len(polyline) > 1  # Does the GEONIS Protocol really never write Paths for single part polylines?
    for path in polyline:
        _serialize_path(path,
                        _Xml.SubElement(polyline_xml, _TAG_PATH, {_ATTR_ENUM: str(_ESRI_ENUM_PATH)})
                        if is_multi else polyline_xml)
    return polyline_xml


def _serialize_polygon(polygons):
    """
    Serializes the EsriJSON polygon definition to XML.

    :param polygons:    An EsriJSON 'curveRings' or 'rings' object value.
    :return:            An XML 'Polygon' element.
    """
    _vld.pass_if(polygons, GeometrySerializationError, 'Polygon does not have any geometry parts')

    polygon_xml = _Xml.Element(_TAG_POLYGON, {_ATTR_ENUM: str(_ESRI_ENUM_POLYGON)})
    for path in polygons:
        polygon_xml.append(_serialize_ring(path))
    return polygon_xml


def _serialize_geometry(esri_json):
    """
    Serializes the EsriJSON dictionary to a GEONIS Protocol XML geometry.
    For more info on Esri JSON: https://developers.arcgis.com/documentation/common-data-types/geometry-objects.htm

    :param esri_json:   An EsriJSON dictionary.
    :return:            An XML 'Geometry' element.
    """

    _vld.pass_if(isinstance(esri_json, dict), TypeError, 'EsriJSON object should be a dictionary')

    xml_geom = _Xml.Element(_TAG_GEOMETRY)

    if not esri_json:
        # EsriJSON is empty (this should not happen actually)
        return xml_geom
    elif _JSON_X in esri_json or _JSON_Y in esri_json:
        # Point geometry
        xml_geom.append(_serialize_point(esri_json.get(_JSON_X), esri_json.get(_JSON_Y)))
    elif _JSON_CURVEPATHS in esri_json or _JSON_PATHS in esri_json:
        # Polyline (with lines and/or arcs/curves)
        xml_geom.append(_serialize_polyline(esri_json.get(_JSON_CURVEPATHS) or esri_json.get(_JSON_PATHS)))
    elif _JSON_CURVERINGS in esri_json or _JSON_RINGS in esri_json:
        # Polygon (based on lines and/or arcs/curves)
        xml_geom.append(_serialize_polygon(esri_json.get(_JSON_CURVERINGS) or esri_json.get(_JSON_RINGS)))
    else:
        raise NotImplementedError('Geometries other than point, polyline or polygon are not supported')

    return xml_geom


def serialize(geometry):
    """
    Serializes Esri Geometry, an Esri Point, EsriJSON or a coordinate iterable into GEONIS Protocol XML geometry.
    Regardless of the dimensions of the input geometry, the output geometry will always be 2D.

    :param geometry:    An Esri Geometry or Point instance, an Esri JSON string or a coordinate iterable.
    :type geometry:     Geometry, str, unicode, tuple, list
    :return:            An XML 'Geometry' element.
    :rtype:             Element

    .. seealso::        :class:`gntools.protocol.Logger`, :class:`gntools.protocol.Feature`
    """

    json_shape = None

    try:
        if hasattr(geometry, 'JSON'):
            # Extract EsriJSON string from arcpy Geometry instance
            geometry = geometry.JSON
        elif hasattr(geometry, 'X') and hasattr(geometry, 'Y'):
            # Convert arcpy Point instance to EsriJSON dict
            json_shape = {_JSON_X: geometry.X, _JSON_Y: geometry.Y}
        elif _vld.is_iterable(geometry) and len(geometry) > 1:
            # Geometry consists of at least 2 coordinates (assume x and y): convert to EsriJSON dict
            json_shape = {_JSON_X: geometry[0], _JSON_Y: geometry[1]}

        if isinstance(geometry, basestring):
            # Geometry is an EsriJSON string: load as dict
            json_shape = _json.loads(geometry)

    except Exception as e:
        raise GeometrySerializationError('serialize() requires an EsriJSON string, '
                                         'Geometry or Point instance, or a coordinate tuple: {}'.format(e))

    return _serialize_geometry(json_shape)
