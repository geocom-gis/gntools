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

from xml.etree.cElementTree import tostring

import pytest

from gntools.common.geometry import GeometrySerializationError
from gntools.common.geometry import serialize


def test_points():
    assert tostring(serialize('{"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}}')) == \
           '<geometry><Point esrienum="1" x="-118.15" y="33.8" /></geometry>'

    assert tostring(serialize('{"x": -118.15, "y": 33.80, "z": 10.0, "spatialReference": {"wkid": 4326}}')) == \
           '<geometry><Point esrienum="1" x="-118.15" y="33.8" /></geometry>'

    with pytest.raises(GeometrySerializationError):
        serialize('{"x": null, "spatialReference": {"wkid": 4326}}')
        serialize('{"x": "NaN", "y": 22.2, "spatialReference": {"wkid": 4326}}')


def test_multipoints():
    with pytest.raises(NotImplementedError):
        assert serialize('{"points": [[-97.06138, 32.837], [-97.06133, 32.836], [-97.06124, 32.834], '
                         '[-97.06127, 32.832]], "spatialReference": {"wkid": 4326}}')


def test_polylines():
    assert tostring(serialize(
            '{"paths": [[[-97.06138, 32.837], [-97.06133, 32.836], [-97.06124, 32.834], [-97.06127, 32.832]], '
            '[[-97.06326, 32.759], [-97.06298, 32.755]]], "spatialReference": {"wkid": 4326}}')) == \
           '<geometry><Polyline esrienum="3"><Path esrienum="6"><Line esrienum="13"><Point esrienum="1" ' \
           'x="-97.06138" y="32.837" /><Point esrienum="1" x="-97.06133" y="32.836" /></Line><Line esrienum="13">' \
           '<Point esrienum="1" x="-97.06133" y="32.836" /><Point esrienum="1" x="-97.06124" y="32.834" /></Line>' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06124" y="32.834" /><Point esrienum="1" x="-97.06127" ' \
           'y="32.832" /></Line></Path><Path esrienum="6"><Line esrienum="13"><Point esrienum="1" x="-97.06326" ' \
           'y="32.759" /><Point esrienum="1" x="-97.06298" y="32.755" /></Line></Path></Polyline></geometry>'

    assert tostring(serialize('{"curvePaths":[[[6,3],[5,3], {"b":[[3,2],[6,1],[2,4]]}, [1,2], '
                              '{"a":[[0,2],[0,3],0,0,2.094395102393195,1.83,0.33333333]}]]}')) == \
           '<geometry><Polyline esrienum="3"><Line esrienum="13"><Point esrienum="1" x="6" y="3" />' \
           '<Point esrienum="1" x="5" y="3" /></Line><BezierCurve esrienum="15"><Point esrienum="1" x="5" y="3" />' \
           '<Point esrienum="1" x="6" y="1" /><Point esrienum="1" x="3" y="2" /><Point esrienum="1" x="2" y="4" />' \
           '</BezierCurve><Line esrienum="13"><Point esrienum="1" x="3" y="2" /><Point esrienum="1" x="1" y="2" />' \
           '</Line><EllipticArc RotationAngle="2.09439510239" ellipseStd="false" esrienum="16" isCCW="true" ' \
           'minorMajorRatio="0.33333333"><Point esrienum="1" x="0" y="3" /><Point esrienum="1" x="1" y="2" />' \
           '<Point esrienum="1" x="0" y="2" /></EllipticArc></Polyline></geometry>'

    with pytest.raises(GeometrySerializationError):
        serialize('{"paths": []}')


def test_polygons():
    assert tostring(serialize('{"rings": [[[-97.06138, 32.837], [-97.06133, 32.836], [-97.06124, 32.834], '
                              '[-97.06127, 32.832], [-97.06138, 32.837]], [[-97.06326, 32.759], [-97.06298, 32.755], '
                              '[-97.06153, 32.749], [-97.06326, 32.759]]], "spatialReference": {"wkid": 4326}}')) == \
           '<geometry><Polygon esrienum="4"><Ring esrienum="11" isexterior="false"><Line esrienum="13">' \
           '<Point esrienum="1" x="-97.06138" y="32.837" /><Point esrienum="1" x="-97.06133" y="32.836" /></Line>' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06133" y="32.836" />' \
           '<Point esrienum="1" x="-97.06124" y="32.834" /></Line><Line esrienum="13">' \
           '<Point esrienum="1" x="-97.06124" y="32.834" /><Point esrienum="1" x="-97.06127" y="32.832" /></Line>' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06127" y="32.832" />' \
           '<Point esrienum="1" x="-97.06138" y="32.837" /></Line></Ring><Ring esrienum="11" isexterior="true">' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06326" y="32.759" />' \
           '<Point esrienum="1" x="-97.06298" y="32.755" /></Line><Line esrienum="13">' \
           '<Point esrienum="1" x="-97.06298" y="32.755" /><Point esrienum="1" x="-97.06153" y="32.749" /></Line>' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06153" y="32.749" />' \
           '<Point esrienum="1" x="-97.06326" y="32.759" /></Line></Ring></Polygon></geometry>'

    assert tostring(serialize('{"hasZ": true, "hasM": true, "rings": [[[-97.06138, 32.837, 35.1, 4], '
                              '[-97.06133, 32.836, 35.2, 4.1], [-97.06124, 32.834, 35.3, 4.2], '
                              '[-97.06127, 32.832, 35.2, 44.3], [-97.06138, 32.837, 35.1, 4]], '
                              '[[-97.06326, 32.759, 35.4], [-97.06298, 32.755, 35.5], [-97.06153, 32.749, 35.6], '
                              '[-97.06326, 32.759, 35.4]]], "spatialReference": {"wkid": 4326}}')) == \
           '<geometry><Polygon esrienum="4"><Ring esrienum="11" isexterior="false"><Line esrienum="13">' \
           '<Point esrienum="1" x="-97.06138" y="32.837" /><Point esrienum="1" x="-97.06133" y="32.836" /></Line>' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06133" y="32.836" />' \
           '<Point esrienum="1" x="-97.06124" y="32.834" /></Line><Line esrienum="13">' \
           '<Point esrienum="1" x="-97.06124" y="32.834" /><Point esrienum="1" x="-97.06127" y="32.832" /></Line>' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06127" y="32.832" />' \
           '<Point esrienum="1" x="-97.06138" y="32.837" /></Line></Ring><Ring esrienum="11" isexterior="true">' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06326" y="32.759" />' \
           '<Point esrienum="1" x="-97.06298" y="32.755" /></Line><Line esrienum="13">' \
           '<Point esrienum="1" x="-97.06298" y="32.755" /><Point esrienum="1" x="-97.06153" y="32.749" /></Line>' \
           '<Line esrienum="13"><Point esrienum="1" x="-97.06153" y="32.749" />' \
           '<Point esrienum="1" x="-97.06326" y="32.759" /></Line></Ring></Polygon></geometry>'

    assert tostring(serialize('{"hasM":true, "curveRings":[[[11,11,1],[10,10,2],[10,11,3],[11,11,4], '
                              '{"b":[[15,15,2],[10,17],[18,20]]}, [11,11,4]], [[15,15,1], {"c":[[20,16,3],[20,14]]}, '
                              '[15,15,3]]], "rings":[[[11,11,1],[10,10,2],[10,11,3],[11,11,4]], '
                              '[[15,15,1],[11,11,2],[12,15.5],[15.4,17.3],[15,15,3]], '
                              '[[20,16,1],[20,14],[17.6,12.5],[15,15,2],[20,16,3]]]}')) == \
           '<geometry><Polygon esrienum="4"><Ring esrienum="11" isexterior="false"><Line esrienum="13">' \
           '<Point esrienum="1" x="11" y="11" /><Point esrienum="1" x="10" y="10" /></Line><Line esrienum="13">' \
           '<Point esrienum="1" x="10" y="10" /><Point esrienum="1" x="10" y="11" /></Line><Line esrienum="13">' \
           '<Point esrienum="1" x="10" y="11" /><Point esrienum="1" x="11" y="11" /></Line>' \
           '<BezierCurve esrienum="15"><Point esrienum="1" x="11" y="11" /><Point esrienum="1" x="10" y="17" />' \
           '<Point esrienum="1" x="15" y="15" /><Point esrienum="1" x="18" y="20" /></BezierCurve>' \
           '<Line esrienum="13"><Point esrienum="1" x="15" y="15" /><Point esrienum="1" x="11" y="11" /></Line>' \
           '</Ring><Ring esrienum="11" isexterior="true"><CircularArc esrienum="14" isCCW="false" isMinor="true">' \
           '<Point esrienum="1" x="20" y="14" /><Point esrienum="1" x="15" y="15" />' \
           '<Point esrienum="1" x="20" y="16" /></CircularArc><Line esrienum="13">' \
           '<Point esrienum="1" x="20" y="16" /><Point esrienum="1" x="15" y="15" /></Line></Ring></Polygon></geometry>'

    assert tostring(serialize('{"curveRings":[[[2614965.7939804718,1208439.9020207711],[2614970.1199936271,'
                              '1208431.4469750039],[2614969.0720170774,1208431.2809807248],[2614968.89000405,'
                              '1208431.6609754674],[2614967.2670044936,1208431.5140034519],[2614967.4980248809,'
                              '1208431.0309881307],[2614962.1900123954,1208430.1890026741],[2614949.8259915747,'
                              '1208423.1749934964],[2614940.3700243309,1208418.3110006861],[2614933.179007981,'
                              '1208414.8260218762],[2614912.734980341,1208405.8510175534],[2614878.7399926856,'
                              '1208391.97202361],[2614855.4780169241,1208382.8419878371],[2614841.1610103324,'
                              '1208376.8490236886],[2614827.1269849427,1208369.6399862431],[2614812.4890026823,'
                              '1208359.6499939822],[2614808.5690147355,1208353.6119771041],[2614806.7569939494,'
                              '1208345.8680135868],[2614811.2150116041,1208330.9409930371],[2614816.998981148,'
                              '1208309.5689792819],[2614821.8980149664,1208291.5379758365],[2614824.0840234645,'
                              '1208286.8690112866],[2614824.9770186245,1208284.9619793035],[2614832.8999916539,'
                              '1208270.2399987318],{"c":[[2614837.9070018493,1208259.7830098979],[2614835.544898151,'
                              '1208265.0792100625]]},{"c":[[2614842.1960217059,1208247.2610041685],'
                              '[2614840.2461284823,1208253.5886668742]]},[2614855.1869762912,1208194.2960140668],'
                              '{"c":[[2614856.807022389,1208192.0089873411],[2614855.8532347376,'
                              '1208193.0506631166]]},[2614856.4349869601,1208191.8829898722],[2614859.0509987324,'
                              '1208181.1559850089],{"c":[[2614859.2919807769,1208178.954007823],[2614859.0950308456,'
                              '1208180.0466288342]]},[2614862.4949795604,1208167.0340066813],[2614867.3060103804,'
                              '1208147.3100217693],[2614866.4860006422,1208146.178998027],[2614865.1670068949,'
                              '1208149.6219776832],[2614861.8119801804,1208160.4739788361],[2614852.8439840563,'
                              '1208193.0560127757],[2614840.0430018157,1208246.1640202589],{"c":[[2614835.8059928305,'
                              '1208258.4630149789],[2614838.0898387567,1208252.370477814]]},'
                              '{"c":[[2614829.9959928207,1208270.7419862561],[2614833.0730370851,'
                              '1208264.6839062278]]},[2614822.8710037507,1208283.7829994299],[2614819.210018944,'
                              '1208292.0269981883],[2614814.4650154002,1208308.805986274],[2614809.4019896463,'
                              '1208328.1450206377],[2614808.3630236462,1208331.5210218988],{"c":[[2614806.0309942439,'
                              '1208332.6059917472],[2614807.3200571681,1208332.3279861303]]},'
                              '{"c":[[2614803.2720151395,1208330.9769851603],[2614804.4127594247,'
                              '1208332.195841148]]},[2614802.9519905858,1208329.6109864004],[2614800.0809803605,'
                              '1208317.343979124],[2614797.2870103046,1208309.2679769881],[2614794.4730168134,'
                              '1208305.3929917105],[2614794.1300153658,1208304.3629861958],{"c":[[2614792.0949835666,'
                              '1208298.2479792051],[2614792.9348704047,1208301.3645964167]]},'
                              '{"c":[[2614791.8819842748,1208287.9949791171],[2614791.5119922017,'
                              '1208293.1313779613]]},{"c":[[2614794.277988553,1208270.4799796082],[2614793.246940067,'
                              '1208279.2603181682]]},{"c":[[2614795.3849841766,1208248.002021458],'
                              '[2614795.1039652177,1208259.2544195855]]},{"c":[[2614796.2879910544,'
                              '1208237.5039845742],[2614795.7409202158,1208242.7447826203]]},'
                              '{"c":[[2614797.9720120281,1208226.9869754948],[2614797.0330064222,'
                              '1208232.2299488303]]},[2614804.5170222931,1208205.3500016294],[2614801.8769823983,'
                              '1208204.6449764706],[2614793.8610005118,1208226.1690181606],[2614791.9920130521,'
                              '1208252.1509773843],{"c":[[2614791.8399851173,1208270.1630086191],[2614792.190996856,'
                              '1208261.1593140804]]},{"c":[[2614789.5050022602,1208287.9609893374],'
                              '[2614790.9429304413,1208279.0974785751]]},{"c":[[2614788.967022609,'
                              '1208299.6549759544],[2614788.8920048508,1208293.7921566418]]},[2614785.7930077501,'
                              '1208297.2080120333],[2614721.6270080134,1208262.0540178753],[2614710.1060238816,'
                              '1208255.15098859],[2614707.7629815899,1208257.8739755638],[2614720.2059948631,'
                              '1208265.3380114548],[2614783.8449777812,1208300.2539770193],[2614789.1220039986,'
                              '1208304.6549779437],[2614793.7609834522,1208310.6190082319],[2614796.755988799,'
                              '1208318.3819940127],[2614804.9599907435,1208355.4430201463],[2614810.712022908,'
                              '1208363.1519927122],[2614825.1930214353,1208372.5650096871],[2614829.1940041743,'
                              '1208374.6140078269],{"c":[[2614830.6719839983,1208377.3940115385],[2614830.0819045277,'
                              '1208375.9248419367]]},{"c":[[2614830.7410147935,1208381.1450016908],'
                              '[2614830.9470001622,1208379.2650805942]]},[2614825.5519915745,1208397.3920171596],'
                              '[2614828.7820219919,1208398.4610183127],[2614834.210976027,1208382.0709854551],'
                              '{"c":[[2614836.5460089445,1208380.224023778],[2614835.2411555042,'
                              '1208380.9738754742]]},{"c":[[2614839.8460212722,1208380.0689923279],'
                              '[2614838.1831659512,1208379.8729998237]]},[2614854.3389838003,1208386.0129991807],'
                              '[2614877.5990072787,1208394.8449861221],[2614911.4830150418,1208408.6939949654],'
                              '[2614931.9219867662,1208417.7119996212],[2614939.0370141789,1208421.0789903365],'
                              '[2614948.1919791289,1208425.7839970626],[2614960.4169872515,1208433.2340165488],'
                              '[2614964.2209894471,1208437.9509872831],[2614964.5000160187,1208437.4419915564],'
                              '[2614965.5039910674,1208438.767993506],[2614965.2570019923,1208439.2359912507],'
                              '[2614965.7939804718,1208439.9020207711]]],"spatialReference":{"wkid":2056,'
                              '"latestWkid":2056}}')) == \
           '<geometry><Polygon esrienum="4"><Ring esrienum="11" isexterior="false"><Line esrienum="13"><Point ' \
           'esrienum="1" x="2614965.79398" y="1208439.90202" /><Point esrienum="1" x="2614970.11999" ' \
           'y="1208431.44698" /></Line><Line esrienum="13"><Point esrienum="1" x="2614970.11999" y="1208431.44698" ' \
           '/><Point esrienum="1" x="2614969.07202" y="1208431.28098" /></Line><Line esrienum="13"><Point ' \
           'esrienum="1" x="2614969.07202" y="1208431.28098" /><Point esrienum="1" x="2614968.89" y="1208431.66098" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614968.89" y="1208431.66098" /><Point esrienum="1" ' \
           'x="2614967.267" y="1208431.514" /></Line><Line esrienum="13"><Point esrienum="1" x="2614967.267" ' \
           'y="1208431.514" /><Point esrienum="1" x="2614967.49802" y="1208431.03099" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614967.49802" y="1208431.03099" /><Point esrienum="1" ' \
           'x="2614962.19001" y="1208430.189" /></Line><Line esrienum="13"><Point esrienum="1" x="2614962.19001" ' \
           'y="1208430.189" /><Point esrienum="1" x="2614949.82599" y="1208423.17499" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614949.82599" y="1208423.17499" /><Point esrienum="1" ' \
           'x="2614940.37002" y="1208418.311" /></Line><Line esrienum="13"><Point esrienum="1" x="2614940.37002" ' \
           'y="1208418.311" /><Point esrienum="1" x="2614933.17901" y="1208414.82602" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614933.17901" y="1208414.82602" /><Point esrienum="1" ' \
           'x="2614912.73498" y="1208405.85102" /></Line><Line esrienum="13"><Point esrienum="1" x="2614912.73498" ' \
           'y="1208405.85102" /><Point esrienum="1" x="2614878.73999" y="1208391.97202" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614878.73999" y="1208391.97202" /><Point esrienum="1" ' \
           'x="2614855.47802" y="1208382.84199" /></Line><Line esrienum="13"><Point esrienum="1" x="2614855.47802" ' \
           'y="1208382.84199" /><Point esrienum="1" x="2614841.16101" y="1208376.84902" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614841.16101" y="1208376.84902" /><Point esrienum="1" ' \
           'x="2614827.12698" y="1208369.63999" /></Line><Line esrienum="13"><Point esrienum="1" x="2614827.12698" ' \
           'y="1208369.63999" /><Point esrienum="1" x="2614812.489" y="1208359.64999" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614812.489" y="1208359.64999" /><Point esrienum="1" ' \
           'x="2614808.56901" y="1208353.61198" /></Line><Line esrienum="13"><Point esrienum="1" x="2614808.56901" ' \
           'y="1208353.61198" /><Point esrienum="1" x="2614806.75699" y="1208345.86801" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614806.75699" y="1208345.86801" /><Point esrienum="1" ' \
           'x="2614811.21501" y="1208330.94099" /></Line><Line esrienum="13"><Point esrienum="1" x="2614811.21501" ' \
           'y="1208330.94099" /><Point esrienum="1" x="2614816.99898" y="1208309.56898" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614816.99898" y="1208309.56898" /><Point esrienum="1" ' \
           'x="2614821.89801" y="1208291.53798" /></Line><Line esrienum="13"><Point esrienum="1" x="2614821.89801" ' \
           'y="1208291.53798" /><Point esrienum="1" x="2614824.08402" y="1208286.86901" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614824.08402" y="1208286.86901" /><Point esrienum="1" ' \
           'x="2614824.97702" y="1208284.96198" /></Line><Line esrienum="13"><Point esrienum="1" x="2614824.97702" ' \
           'y="1208284.96198" /><Point esrienum="1" x="2614832.89999" y="1208270.24" /></Line><CircularArc ' \
           'esrienum="14" isCCW="true" isMinor="true"><Point esrienum="1" x="2614835.5449" y="1208265.07921" />' \
           '<Point esrienum="1" x="2614832.89999" y="1208270.24" /><Point esrienum="1" x="2614837.907" ' \
           'y="1208259.78301" /></CircularArc>' \
           '<CircularArc esrienum="14" isCCW="true" isMinor="true"><Point esrienum="1" ' \
           'x="2614840.24613" y="1208253.58867" /><Point esrienum="1" x="2614837.907" y="1208259.78301" /><Point ' \
           'esrienum="1" x="2614842.19602" y="1208247.261" /></CircularArc><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614842.19602" y="1208247.261" /><Point esrienum="1" x="2614855.18698" y="1208194.29601" ' \
           '/></Line><CircularArc esrienum="14" isCCW="false" isMinor="true"><Point esrienum="1" x="2614855.85323" ' \
           'y="1208193.05066" /><Point esrienum="1" x="2614855.18698" y="1208194.29601" /><Point esrienum="1" ' \
           'x="2614856.80702" y="1208192.00899" /></CircularArc><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614856.80702" y="1208192.00899" /><Point esrienum="1" x="2614856.43499" y="1208191.88299" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614856.43499" y="1208191.88299" /><Point ' \
           'esrienum="1" x="2614859.051" y="1208181.15599" /></Line><CircularArc esrienum="14" isCCW="false" ' \
           'isMinor="true"><Point esrienum="1" x="2614859.09503" y="1208180.04663" /><Point esrienum="1" ' \
           'x="2614859.051" y="1208181.15599" /><Point esrienum="1" x="2614859.29198" y="1208178.95401" ' \
           '/></CircularArc><Line esrienum="13"><Point esrienum="1" x="2614859.29198" y="1208178.95401" /><Point ' \
           'esrienum="1" x="2614862.49498" y="1208167.03401" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614862.49498" y="1208167.03401" /><Point esrienum="1" x="2614867.30601" y="1208147.31002" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614867.30601" y="1208147.31002" /><Point ' \
           'esrienum="1" x="2614866.486" y="1208146.179" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614866.486" y="1208146.179" /><Point esrienum="1" x="2614865.16701" y="1208149.62198" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614865.16701" y="1208149.62198" /><Point esrienum="1" ' \
           'x="2614861.81198" y="1208160.47398" /></Line><Line esrienum="13"><Point esrienum="1" x="2614861.81198" ' \
           'y="1208160.47398" /><Point esrienum="1" x="2614852.84398" y="1208193.05601" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614852.84398" y="1208193.05601" /><Point esrienum="1" ' \
           'x="2614840.043" y="1208246.16402" /></Line>' \
           '<CircularArc esrienum="14" isCCW="false" isMinor="true"><Point ' \
           'esrienum="1" x="2614838.08984" y="1208252.37048" /><Point esrienum="1" x="2614840.043" y="1208246.16402" ' \
           '/><Point esrienum="1" x="2614835.80599" y="1208258.46301" /></CircularArc><CircularArc esrienum="14" ' \
           'isCCW="false" isMinor="true"><Point esrienum="1" x="2614833.07304" y="1208264.68391" /><Point ' \
           'esrienum="1" x="2614835.80599" y="1208258.46301" /><Point esrienum="1" x="2614829.99599" ' \
           'y="1208270.74199" /></CircularArc><Line esrienum="13"><Point esrienum="1" x="2614829.99599" ' \
           'y="1208270.74199" /><Point esrienum="1" x="2614822.871" y="1208283.783" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614822.871" y="1208283.783" />' \
           '<Point esrienum="1" x="2614819.21002" ' \
           'y="1208292.027" /></Line><Line esrienum="13"><Point esrienum="1" x="2614819.21002" y="1208292.027" ' \
           '/><Point esrienum="1" x="2614814.46502" y="1208308.80599" /></Line><Line esrienum="13"><Point ' \
           'esrienum="1" x="2614814.46502" y="1208308.80599" /><Point esrienum="1" x="2614809.40199" ' \
           'y="1208328.14502" /></Line><Line esrienum="13"><Point esrienum="1" x="2614809.40199" y="1208328.14502" ' \
           '/><Point esrienum="1" x="2614808.36302" y="1208331.52102" /></Line><CircularArc esrienum="14" ' \
           'isCCW="false" isMinor="true"><Point esrienum="1" x="2614807.32006" y="1208332.32799" /><Point ' \
           'esrienum="1" x="2614808.36302" y="1208331.52102" /><Point esrienum="1" x="2614806.03099" ' \
           'y="1208332.60599" /></CircularArc><CircularArc esrienum="14" isCCW="false" isMinor="true"><Point ' \
           'esrienum="1" x="2614804.41276" y="1208332.19584" /><Point esrienum="1" x="2614806.03099" ' \
           'y="1208332.60599" /><Point esrienum="1" x="2614803.27202" y="1208330.97699" /></CircularArc><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614803.27202" y="1208330.97699" /><Point esrienum="1" ' \
           'x="2614802.95199" y="1208329.61099" /></Line><Line esrienum="13"><Point esrienum="1" x="2614802.95199" ' \
           'y="1208329.61099" /><Point esrienum="1" x="2614800.08098" y="1208317.34398" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614800.08098" y="1208317.34398" /><Point esrienum="1" ' \
           'x="2614797.28701" y="1208309.26798" /></Line><Line esrienum="13"><Point esrienum="1" x="2614797.28701" ' \
           'y="1208309.26798" /><Point esrienum="1" x="2614794.47302" y="1208305.39299" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614794.47302" y="1208305.39299" /><Point esrienum="1" ' \
           'x="2614794.13002" y="1208304.36299" /></Line><CircularArc esrienum="14" isCCW="false" ' \
           'isMinor="true"><Point esrienum="1" x="2614792.93487" y="1208301.3646" /><Point esrienum="1" ' \
           'x="2614794.13002" y="1208304.36299" /><Point esrienum="1" x="2614792.09498" y="1208298.24798" ' \
           '/></CircularArc><CircularArc esrienum="14" isCCW="false" isMinor="true"><Point esrienum="1" ' \
           'x="2614791.51199" y="1208293.13138" /><Point esrienum="1" x="2614792.09498" y="1208298.24798" /><Point ' \
           'esrienum="1" x="2614791.88198" y="1208287.99498" /></CircularArc><CircularArc esrienum="14" isCCW="true" ' \
           'isMinor="true"><Point esrienum="1" x="2614793.24694" y="1208279.26032" /><Point esrienum="1" ' \
           'x="2614791.88198" y="1208287.99498" /><Point esrienum="1" x="2614794.27799" y="1208270.47998" ' \
           '/></CircularArc><CircularArc esrienum="14" isCCW="true" isMinor="true"><Point esrienum="1" ' \
           'x="2614795.10397" y="1208259.25442" /><Point esrienum="1" x="2614794.27799" y="1208270.47998" /><Point ' \
           'esrienum="1" x="2614795.38498" y="1208248.00202" /></CircularArc>' \
           '<CircularArc esrienum="14" isCCW="false" ' \
           'isMinor="true"><Point esrienum="1" x="2614795.74092" y="1208242.74478" /><Point esrienum="1" ' \
           'x="2614795.38498" y="1208248.00202" /><Point esrienum="1" x="2614796.28799" y="1208237.50398" ' \
           '/></CircularArc><CircularArc esrienum="14" isCCW="false" isMinor="true"><Point esrienum="1" ' \
           'x="2614797.03301" y="1208232.22995" /><Point esrienum="1" x="2614796.28799" y="1208237.50398" /><Point ' \
           'esrienum="1" x="2614797.97201" y="1208226.98698" /></CircularArc><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614797.97201" y="1208226.98698" /><Point esrienum="1" x="2614804.51702" y="1208205.35" /></Line>' \
           '<Line esrienum="13"><Point esrienum="1" x="2614804.51702" y="1208205.35" /><Point esrienum="1" ' \
           'x="2614801.87698" y="1208204.64498" /></Line><Line esrienum="13"><Point esrienum="1" x="2614801.87698" ' \
           'y="1208204.64498" /><Point esrienum="1" x="2614793.861" y="1208226.16902" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614793.861" y="1208226.16902" /><Point esrienum="1" ' \
           'x="2614791.99201" y="1208252.15098" /></Line><CircularArc esrienum="14" isCCW="false" ' \
           'isMinor="true"><Point esrienum="1" x="2614792.191" y="1208261.15931" /><Point esrienum="1" ' \
           'x="2614791.99201" y="1208252.15098" /><Point esrienum="1" x="2614791.83999" y="1208270.16301" ' \
           '/></CircularArc><CircularArc esrienum="14" isCCW="false" isMinor="true"><Point esrienum="1" ' \
           'x="2614790.94293" y="1208279.09748" /><Point esrienum="1" x="2614791.83999" y="1208270.16301" /><Point ' \
           'esrienum="1" x="2614789.505" y="1208287.96099" /></CircularArc><CircularArc esrienum="14" isCCW="true" ' \
           'isMinor="true"><Point esrienum="1" x="2614788.892" y="1208293.79216" /><Point esrienum="1" ' \
           'x="2614789.505" y="1208287.96099" /><Point esrienum="1" x="2614788.96702" y="1208299.65498" ' \
           '/></CircularArc><Line esrienum="13"><Point esrienum="1" x="2614788.96702" y="1208299.65498" /><Point ' \
           'esrienum="1" x="2614785.79301" y="1208297.20801" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614785.79301" y="1208297.20801" /><Point esrienum="1" x="2614721.62701" y="1208262.05402" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614721.62701" y="1208262.05402" /><Point ' \
           'esrienum="1" x="2614710.10602" y="1208255.15099" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614710.10602" y="1208255.15099" /><Point esrienum="1" x="2614707.76298" y="1208257.87398" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614707.76298" y="1208257.87398" /><Point ' \
           'esrienum="1" x="2614720.20599" y="1208265.33801" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614720.20599" y="1208265.33801" /><Point esrienum="1" x="2614783.84498" y="1208300.25398" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614783.84498" y="1208300.25398" /><Point ' \
           'esrienum="1" x="2614789.122" y="1208304.65498" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614789.122" y="1208304.65498" /><Point esrienum="1" x="2614793.76098" y="1208310.61901" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614793.76098" y="1208310.61901" /><Point ' \
           'esrienum="1" x="2614796.75599" y="1208318.38199" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614796.75599" y="1208318.38199" /><Point esrienum="1" x="2614804.95999" y="1208355.44302" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614804.95999" y="1208355.44302" /><Point ' \
           'esrienum="1" x="2614810.71202" y="1208363.15199" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614810.71202" y="1208363.15199" /><Point esrienum="1" x="2614825.19302" y="1208372.56501" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614825.19302" y="1208372.56501" /><Point ' \
           'esrienum="1" x="2614829.194" y="1208374.61401" /></Line><CircularArc esrienum="14" isCCW="false" ' \
           'isMinor="true"><Point esrienum="1" x="2614830.0819" y="1208375.92484" /><Point esrienum="1" ' \
           'x="2614829.194" y="1208374.61401" /><Point esrienum="1" x="2614830.67198" y="1208377.39401" ' \
           '/></CircularArc><CircularArc esrienum="14" isCCW="false" isMinor="true"><Point esrienum="1" ' \
           'x="2614830.947" y="1208379.26508" /><Point esrienum="1" x="2614830.67198" y="1208377.39401" /><Point ' \
           'esrienum="1" x="2614830.74101" y="1208381.145" /></CircularArc><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614830.74101" y="1208381.145" /><Point esrienum="1" x="2614825.55199" y="1208397.39202" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614825.55199" y="1208397.39202" /><Point ' \
           'esrienum="1" x="2614828.78202" y="1208398.46102" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614828.78202" y="1208398.46102" /><Point esrienum="1" x="2614834.21098" y="1208382.07099" ' \
           '/></Line><CircularArc esrienum="14" isCCW="false" isMinor="true"><Point esrienum="1" x="2614835.24116" ' \
           'y="1208380.97388" /><Point esrienum="1" x="2614834.21098" y="1208382.07099" /><Point esrienum="1" ' \
           'x="2614836.54601" y="1208380.22402" /></CircularArc><CircularArc esrienum="14" isCCW="false" ' \
           'isMinor="true"><Point esrienum="1" x="2614838.18317" y="1208379.873" /><Point esrienum="1" ' \
           'x="2614836.54601" y="1208380.22402" /><Point esrienum="1" x="2614839.84602" y="1208380.06899" ' \
           '/></CircularArc><Line esrienum="13"><Point esrienum="1" x="2614839.84602" y="1208380.06899" /><Point ' \
           'esrienum="1" x="2614854.33898" y="1208386.013" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614854.33898" y="1208386.013" /><Point esrienum="1" x="2614877.59901" y="1208394.84499" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614877.59901" y="1208394.84499" /><Point ' \
           'esrienum="1" x="2614911.48302" y="1208408.69399" /></Line><Line esrienum="13"><Point esrienum="1" ' \
           'x="2614911.48302" y="1208408.69399" /><Point esrienum="1" x="2614931.92199" y="1208417.712" ' \
           '/></Line><Line esrienum="13"><Point esrienum="1" x="2614931.92199" y="1208417.712" /><Point esrienum="1" ' \
           'x="2614939.03701" y="1208421.07899" /></Line><Line esrienum="13"><Point esrienum="1" x="2614939.03701" ' \
           'y="1208421.07899" /><Point esrienum="1" x="2614948.19198" y="1208425.784" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614948.19198" y="1208425.784" /><Point esrienum="1" ' \
           'x="2614960.41699" y="1208433.23402" /></Line><Line esrienum="13"><Point esrienum="1" x="2614960.41699" ' \
           'y="1208433.23402" /><Point esrienum="1" x="2614964.22099" y="1208437.95099" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614964.22099" y="1208437.95099" /><Point esrienum="1" ' \
           'x="2614964.50002" y="1208437.44199" /></Line><Line esrienum="13"><Point esrienum="1" x="2614964.50002" ' \
           'y="1208437.44199" /><Point esrienum="1" x="2614965.50399" y="1208438.76799" /></Line><Line ' \
           'esrienum="13"><Point esrienum="1" x="2614965.50399" y="1208438.76799" /><Point esrienum="1" ' \
           'x="2614965.257" y="1208439.23599" /></Line><Line esrienum="13"><Point esrienum="1" x="2614965.257" ' \
           'y="1208439.23599" /><Point esrienum="1" x="2614965.79398" y="1208439.90202" ' \
           '/></Line></Ring></Polygon></geometry>'

    with pytest.raises(GeometrySerializationError):
        serialize('{"rings": []}')
