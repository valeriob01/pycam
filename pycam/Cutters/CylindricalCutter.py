"""
Copyright 2008-2010 Lode Leroy
Copyright 2010-2018 Lars Kruse <devel@sumpfralle.de>

This file is part of PyCAM.

PyCAM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyCAM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCAM.  If not, see <http://www.gnu.org/licenses/>.
"""

from pycam.Geometry import INFINITE
from pycam.Cutters.BaseCutter import BaseCutter
from pycam.Geometry.intersection import intersect_circle_plane, intersect_circle_point, \
        intersect_circle_line
from pycam.Geometry.PointUtils import padd, psub


class CylindricalCutter(BaseCutter):

    def __init__(self, radius, **kwargs):
        BaseCutter.__init__(self, radius, **kwargs)
        self.axis = (0, 0, 1, 'v')

    def __repr__(self):
        return "CylindricalCutter<%s,%s>" % (self.location, self.radius)

    def get_tool_x3d(self):
        yield '<Cylinder radius="{:f}" height="{:f}" />'.format(self.radius, self.height)

    def moveto(self, location, **kwargs):
        BaseCutter.moveto(self, location, **kwargs)
        self.center = (location[0], location[1], location[2] - self.get_required_distance())

    def intersect_circle_plane(self, direction, triangle, start=None):
        if start is None:
            start = self.location
        (ccp, cp, d) = intersect_circle_plane(padd(psub(start, self.location), self.center),
                                              self.distance_radius, direction, triangle)
        if ccp and cp:
            cl = padd(cp, psub(start, ccp))
            return (cl, ccp, cp, d)
        return (None, None, None, INFINITE)

    def intersect_circle_point(self, direction, point, start=None):
        if start is None:
            start = self.location
        (ccp, cp, l) = intersect_circle_point(padd(psub(start, self.location), self.center),
                                              self.axis, self.distance_radius,
                                              self.distance_radiussq, direction, point)
        if ccp:
            cl = padd(cp, psub(start, ccp))
            return (cl, ccp, cp, l)
        return (None, None, None, INFINITE)

    def intersect_circle_line(self, direction, edge, start=None):
        if start is None:
            start = self.location
        (ccp, cp, l) = intersect_circle_line(padd(psub(start, self.location), self.center),
                                             self.axis, self.distance_radius,
                                             self.distance_radiussq, direction, edge)
        if ccp:
            cl = padd(cp, psub(start, ccp))
            return (cl, ccp, cp, l)
        return (None, None, None, INFINITE)

    def intersect(self, direction, triangle, start=None):
        (cl_t, d_t, cp_t) = self.intersect_circle_triangle(direction, triangle, start=start)
        d = INFINITE
        cl = None
        cp = None
        if d_t < d:
            d = d_t
            cl = cl_t
            cp = cp_t
        if cl and (direction[0] == 0) and (direction[1] == 0):
            return (cl, d, cp)
        (cl_e1, d_e1, cp_e1) = self.intersect_circle_edge(direction, triangle.e1, start=start)
        (cl_e2, d_e2, cp_e2) = self.intersect_circle_edge(direction, triangle.e2, start=start)
        (cl_e3, d_e3, cp_e3) = self.intersect_circle_edge(direction, triangle.e3, start=start)
        if d_e1 < d:
            d = d_e1
            cl = cl_e1
            cp = cp_e1
        if d_e2 < d:
            d = d_e2
            cl = cl_e2
            cp = cp_e2
        if d_e3 < d:
            d = d_e3
            cl = cl_e3
            cp = cp_e3
        if cl and (direction[0] == 0) and (direction[1] == 0):
            return (cl, d, cp)
        (cl_p1, d_p1, cp_p1) = self.intersect_circle_vertex(direction, triangle.p1, start=start)
        (cl_p2, d_p2, cp_p2) = self.intersect_circle_vertex(direction, triangle.p2, start=start)
        (cl_p3, d_p3, cp_p3) = self.intersect_circle_vertex(direction, triangle.p3, start=start)
        if d_p1 < d:
            d = d_p1
            cl = cl_p1
            cp = cp_p1
        if d_p2 < d:
            d = d_p2
            cl = cl_p2
            cp = cp_p2
        if d_p3 < d:
            d = d_p3
            cl = cl_p3
            cp = cp_p3
        if cl and (direction[0] == 0) and (direction[1] == 0):
            return (cl, d, cp)
        if (direction[0] != 0) or (direction[1] != 0):
            cl_p1, d_p1, cp_p1 = self.intersect_cylinder_vertex(direction, triangle.p1,
                                                                start=start)
            cl_p2, d_p2, cp_p2 = self.intersect_cylinder_vertex(direction, triangle.p2,
                                                                start=start)
            cl_p3, d_p3, cp_p3 = self.intersect_cylinder_vertex(direction, triangle.p3,
                                                                start=start)
            if d_p1 < d:
                d = d_p1
                cl = cl_p1
                cp = cp_p1
            if d_p2 < d:
                d = d_p2
                cl = cl_p2
                cp = cp_p2
            if d_p3 < d:
                d = d_p3
                cl = cl_p3
                cp = cp_p3
            cl_e1, d_e1, cp_e1 = self.intersect_cylinder_edge(direction, triangle.e1, start=start)
            cl_e2, d_e2, cp_e2 = self.intersect_cylinder_edge(direction, triangle.e2, start=start)
            cl_e3, d_e3, cp_e3 = self.intersect_cylinder_edge(direction, triangle.e3, start=start)
            if d_e1 < d:
                d = d_e1
                cl = cl_e1
                cp = cp_e1
            if d_e2 < d:
                d = d_e2
                cl = cl_e2
                cp = cp_e2
            if d_e3 < d:
                d = d_e3
                cl = cl_e3
                cp = cp_e3
        return (cl, d, cp)
