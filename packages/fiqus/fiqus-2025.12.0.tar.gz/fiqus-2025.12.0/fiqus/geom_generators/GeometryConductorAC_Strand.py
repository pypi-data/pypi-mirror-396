import os
import pickle

import numpy as np
import gmsh

import fiqus.data.DataFiQuSConductor as geom
from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import FilesAndFolders as UFF
from abc import ABC, abstractmethod
from typing import (Dict, List)
from scipy.integrate import quad


### HELPER FUNCTIONS ###

def cylindrical_to_cartesian(rad, angle, height):
    """
    Convert cylindrical coordinates to Cartesian coordinates.

    :return: A list of Cartesian coordinates [x, y, z].
    :rtype: list
    """
    return [rad * np.cos(angle), rad * np.sin(angle), height]


def cartesian_to_cylindrical(x, y, z):
    """
    Convert Cartesian coordinates to cylindrical coordinates.

    :return: A list of cylindrical coordinates [rad, angle, z].
    :rtype: list
    """
    rad = np.sqrt(x ** 2 + y ** 2)
    angle = np.arctan2(y, x)
    return [rad, angle, z]


def rotate_vector(vector, angle):
    """
    Rotate a 3D vector in the xy-plane by a given angle.

    :param vector: The 3D vector to rotate. It should be a list or numpy array of three numbers.
    :type vector: list or numpy.ndarray
    :param angle: The angle by which to rotate the vector, in radians.
    :type angle: float

    :return: The rotated vector.
    :rtype: numpy.ndarray
    """
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
    return np.matmul(rotation_matrix, vector)


### END HELPER FUNCTIONS ###


### GEOMETRY ###
class Point:
    """
    A class to represent a point in 3D space.

    :cvar points_registry: A list of all points created. This is a class-level attribute.
    :vartype points_registry: list
    :cvar point_snap_tolerance: The tolerance for snapping points to existing points. This is a class-level attribute.
    :vartype point_snap_tolerance: float

    :ivar pos: A numpy array representing the position of the point in 3D space. This is an instance-level attribute.
    :vartype pos: numpy.ndarray
    :ivar tag: A gmsh tag for the point, default is None. This is an instance-level attribute.
    :vartype tag: int, optional
    """
    points_registry = []  # Global registry of points
    point_snap_tolerance = 1e-10  # Tolerance for snapping points to existing points

    def __init__(self, pos: List[float]):
        """
        Constructs the attributes for the point object.

        :param pos: A list of three floats representing the position of the point in 3D space.
        :type pos: List[float]
        """
        self.pos = np.array(pos)
        self.tag = None

    @classmethod
    def create_or_get(cls, pos: any):
        """
        Creates a new point if no point with the given position exists, otherwise returns the existing one to assure unique points.

        :param pos: The position of the point.
        :type pos: list

        :return: A point object.
        :rtype: Point
        """
        new_point = cls(pos)
        if new_point in cls.points_registry:
            return cls.points_registry[cls.points_registry.index(new_point)]

        cls.points_registry.append(new_point)
        return new_point

    def create_gmsh_instance(self, meshSize: float = 0, tag: int = -1):
        if self.tag == None:
            self.tag = gmsh.model.occ.addPoint(self.pos[0], self.pos[1], self.pos[2], meshSize, tag)
        else:
            pass

    def __repr__(self) -> str:
        return f"Point({self.pos})"

    def __eq__(self, o: object) -> bool:
        # Two points sharing the same position (within a margin of point_snap_tolerance) should be considered the same point.
        if isinstance(o, Point):
            return np.linalg.norm(np.array(self.pos) - np.array(o.pos)) < self.point_snap_tolerance
        return False

    def __hash__(self) -> int:
        return hash(tuple(self.pos))


### CURVE ELEMENTS ###

class Curve(ABC):
    """
    Abstract base class for curves in 3D space.

    :cvar curves_registry: A list of all curves created. This is a class-level attribute.
    :vartype curves_registry: list

    :ivar P1: The start point of the curve. This is an instance-level attribute.
    :vartype P1: Point
    :ivar P2: The end point of the curve. This is an instance-level attribute.
    :vartype P2: Point
    :ivar points: A list of points used by the curve. This is an instance-level attribute.
    :vartype points: list
    :ivar tag: A tag for the curve. This is an instance-level attribute.
    :vartype tag: int
    """
    curves_registry = []

    def __init__(self) -> None:
        """
        Constructs the attributes for the curve object.
        """
        self.P1: Point = None
        self.P2: Point = None
        self.points = []
        self.tag = None

        # Curve.curves_registry.append(self)

    def set_points(self, *points: Point):
        """
        Sets the points used by the curve.

        :param points: The points to set.
        :type points: Point
        """
        self.points = list(points)

    @abstractmethod
    def get_length(self):
        pass

    @abstractmethod
    def create_gmsh_instance(self):
        pass

    @classmethod
    @abstractmethod
    def create_or_get(cls, *points):
        pass

    @classmethod
    def get_curve_from_tag(cls, tag):
        """
        Returns the curve with the given tag.

        :param tag: The tag of the curve.
        :type tag: int

        :return: The curve with the given tag, or None if no such curve exists.
        :rtype: Curve or None
        """
        for curve in cls.curves_registry:
            if curve.tag == tag:
                return curve
        return None

    @classmethod
    def get_closed_loops(cls, curves):
        """
        Returns a list of lists of curves, where each list of curves defines a closed loop.
        The function assumes that no two closed loops share a curve and that chains of curves do not split into multiple chains.

        :param curves: A list of curves.
        :type curves: list

        :return: A list of lists of curves, where each list of curves defines a closed loop.
        :rtype: list
        """
        closed_loops = []

        def get_curve_link(current_curve, curves, curve_link):
            # Recursive function to find a link of connected curves.
            # Curves is a list of curves to search through, not containing the current curve.
            # Curve_link is a list of curves that are connected to the current curve.
            # Curves are removed from 'curves' as they are added to the curve_link.
            # The function returns when no more curves are connected to the current link.
            for curve in curves:
                for point in [current_curve.P1, current_curve.P2]:
                    if point in [curve.P1, curve.P2]:
                        curve_link.append(curve)
                        curves.remove(curve)
                        return get_curve_link(curve, curves, curve_link)
            return curves, curve_link  # Return the remaining curves and the curve link

        while len(curves) > 0:
            curve0 = curves[0]
            curves.remove(curve0)
            curves, curve_link = get_curve_link(curve0, curves, [curve0])

            first_curve_points = set([curve_link[0].P1, curve_link[0].P2])
            last_curve_points = set([curve_link[-1].P1, curve_link[-1].P2])

            # TODO: Have to add the case where there is only a single curve in the link. This should not be considered a closed loop.
            if len(curve_link) > 2 and len(first_curve_points & last_curve_points) == 1:  # Check if the last curve in the link is connected to the first curve in the link. If so, the link is a closed loop.
                closed_loops.append(curve_link)
            # If the link only contains two curves, the curves must be connected at both ends to form a closed loop.
            elif len(curve_link) == 2 and len(first_curve_points & last_curve_points) == 2:
                closed_loops.append(curve_link)

        return closed_loops


class CircleArc(Curve):
    """
    A class to represent a circular arc, subclass of Curve.

    :ivar P1: The first point of the arc. This is an instance-level attribute.
    :vartype P1: Point
    :ivar P2: The second point of the arc. This is an instance-level attribute.
    :vartype P2: Point
    :ivar C: The center of the arc. This is an instance-level attribute.
    :vartype C: Point
    """

    def __init__(self, P1: any, C: any, P2: any) -> None:
        """
        Constructs the attributes for the arc object.

        :param P1: The start point of the arc.
        :type P1: list or Point
        :param P2: The end point of the arc.
        :type P2: list or Point
        :param C: The center of the arc.
        :type C: list or Point
        """
        super().__init__()
        self.P1 = P1 if isinstance(P1, Point) else Point.create_or_get(P1)
        self.P2 = P2 if isinstance(P2, Point) else Point.create_or_get(P2)
        self.C = C if isinstance(C, Point) else Point.create_or_get(C)

        self.set_points(self.P1, self.C, self.P2)

        Curve.curves_registry.append(self)

    def create_gmsh_instance(self, tag: int = -1):
        if self.tag == None:  # If the curve has not been created yet
            self.P1.create_gmsh_instance()
            self.P2.create_gmsh_instance()
            self.C.create_gmsh_instance()
            self.tag = gmsh.model.occ.addCircleArc(self.P1.tag, self.C.tag, self.P2.tag, tag)

    def get_length(self):
        radius = np.linalg.norm(self.P1.pos - self.C.pos)
        angle = np.arccos(np.dot(self.P1.pos - self.C.pos, self.P2.pos - self.C.pos) / (radius ** 2))
        return radius * angle

    @classmethod
    def create_or_get(cls, P1: any, C: any, P2: any):
        return cls(P1, C, P2)

    def __repr__(self) -> str:
        return f"CircleArc({self.P1.pos}, {self.P2.pos})"


class Line(Curve):
    """
    A class to represent a line, subclass of Curve.

    :ivar P1: the start point of the line
    :type P1: list or Point
    :ivar P2: the end point of the line
    :type P2: list or Point

    """

    def __init__(self, P1: any, P2: any) -> None:
        """
        Constructs the attributes for the line object.
        P1 and P2 can be either 'Point' objects or lists of three floats representing the position of the point.

        :param P1: the start point of the line
        :type P1: list or Point
        :param P2: the end point of the line
        :type P2: list or Point
        """
        super().__init__()
        self.P1 = P1 if isinstance(P1, Point) else Point.create_or_get(P1)
        self.P2 = P2 if isinstance(P2, Point) else Point.create_or_get(P2)

        self.set_points(self.P1, self.P2)

    def get_length(self):
        return np.linalg.norm(self.P1.pos - self.P2.pos)

    def get_furthest_point(self):
        """returns the line point which is further away from the origin"""
        if np.linalg.norm(self.P1.pos) > np.linalg.norm(self.P2.pos):
            return self.P1
        elif np.linalg.norm(self.P1.pos) < np.linalg.norm(self.P2.pos):
            return self.P2
        else:
            ValueError("cant determine furthest point. Dictance is equal")

    def __repr__(self) -> str:
        return f"Line from {tuple(self.P1.pos)} to {tuple(self.P2.pos)}"

    @classmethod
    def create_or_get(cls, P1: any, P2: any):
        """
        Creates a new line if it doesn't exist, or returns the existing one.

        :param P1: the first point of the line
        :type P1: Point
        :param P2: the second point of the line
        :type P2: Point

        :return: a line object
        :rtype: Line
        """

        new_line = cls(P1, P2)
        if new_line in cls.curves_registry:
            return cls.curves_registry[cls.curves_registry.index(new_line)]

        cls.curves_registry.append(new_line)
        return new_line

    @classmethod
    def is_colinear(cls, line1, line2):
        """
            Checks if two lines are colinear.
        """
        l1 = line1.P2.pos - line1.P1.pos
        l2 = line2.P2.pos - line2.P1.pos
        # Check if the lines are parallel
        if np.linalg.norm(np.cross(l1, l2)) < 1e-10:
            # Check if the lines are colinear
            if np.linalg.norm(np.cross(l1, line2.P1.pos - line1.P1.pos)) < 1e-10:
                return True
        return False

    @classmethod
    def remove_from_registry(cls, lines):
        """
        Removes a list of lines from the registry.

        :param lines: A list of lines to remove.
        :type lines: list
        """
        for line in lines:
            if line in cls.curves_registry:
                cls.curves_registry.remove(line)

    def create_gmsh_instance(self, tag: int = -1):
        if self.tag == None:
            self.P1.create_gmsh_instance()
            self.P2.create_gmsh_instance()
            self.tag = gmsh.model.occ.addLine(self.P1.tag, self.P2.tag, tag)

    def __eq__(self, o: object) -> bool:
        # Two Line-entities specified by the same two points should be considered equal lines.
        # Check if the other object is a line
        if isinstance(o, Line):
            # Check if the lines have the same points
            return (self.P1 == o.P1 and self.P2 == o.P2) or (self.P1 == o.P2 and self.P2 == o.P1)
        return False

    def __hash__(self) -> int:
        return hash(frozenset([self.P1, self.P2]))  # Frozenset is hashable and order-independent


class EllipseArc(Curve):
    """
    A class to represent an elliptical arc, subclass of Curve.

    :ivar P1: The start point of the arc. This is an instance-level attribute.
    :vartype P1: Point
    :ivar P2: The end point of the arc. This is an instance-level attribute.
    :vartype P2: Point
    :ivar C: The center point of the arc. This is an instance-level attribute.
    :vartype C: Point
    :ivar M: The major axis point of the arc (point anywhere on the major axis). This is an instance-level attribute.
    :vartype M: Point
    """

    def __init__(self, P_start: any, P_center: any, P_major: any, P_end: any) -> None:
        """
        Initializes an elliptical arc object.

        :param P_start: The start point of the arc. If not a Point instance, attempts to retrieve or create one.
        :type P_start: any
        :param P_end: The end point of the arc. If not a Point instance, attempts to retrieve or create one.
        :type P_end: any
        :param P_center: The center point of the arc. If not a Point instance, attempts to retrieve or create one.
        :type P_center: any
        :param P_major: The major axis point of the arc (point anywhere on the major axis). If not a Point instance, attempts to retrieve or create one.
        :type P_major: any

        :rtype: None
        """
        super().__init__()
        self.P1 = P_start if isinstance(P_start, Point) else Point.create_or_get(P_start)  # Start point
        self.P2 = P_end if isinstance(P_end, Point) else Point.create_or_get(P_end)  # End point
        self.C = P_center if isinstance(P_center, Point) else Point.create_or_get(P_center)  # Center point
        self.M = P_major if isinstance(P_major, Point) else Point.create_or_get(P_major)  # Major axis point (point anywhere on the major axis)

        self.set_points(self.P1, self.C, self.M, self.P2)

        Curve.curves_registry.append(self)
        # self.tag = None

    def get_length(self):
        # Approximate the length of the elliptical arc
        # 1) Center the ellipse on the origin and rotate it so that the major axis is on the x-axis
        # a) center the ellipse
        P1 = self.P1.pos - self.C.pos
        P2 = self.P2.pos - self.C.pos
        M = self.M.pos - self.C.pos
        # b) rotate the ellipse
        angle = np.arctan2(M[1], M[0])
        P1 = rotate_vector(P1, -angle)
        P2 = rotate_vector(P2, -angle)
        # c) calculate the semi-major and semi-minor axes
        x1, y1 = P1[0], P1[1]
        x2, y2 = P2[0], P2[1]

        b = np.sqrt((x2 ** 2 * y1 ** 2 - x1 ** 2 * y2 ** 2) / (x2 ** 2 - x1 ** 2))  # semi-minor axis
        a = np.sqrt((x2 ** 2 * y1 ** 2 - x1 ** 2 * y2 ** 2) / (y1 ** 2 - y2 ** 2))  # semi-major axis

        # 2) Calculate the length of the elliptical arc
        theta1 = np.arctan2(y1, x1)  # angle of the start point
        theta2 = np.arctan2(y2, x2)  # angle of the end point
        if theta2 < theta1:
            theta1, theta2 = theta2, theta1
        t = lambda theta: np.arctan((a / b) * np.tan(theta))  # Change of parameter from angle to t
        arc_length = quad(lambda theta: np.sqrt(a ** 2 * np.sin(t(theta)) ** 2 + b ** 2 * np.cos(t(theta)) ** 2), theta1, theta2)[0]  # Calculate the arc length

        return arc_length

    def create_gmsh_instance(self, tag: int = -1):
        if self.tag == None:
            self.P1.create_gmsh_instance()
            self.P2.create_gmsh_instance()
            self.C.create_gmsh_instance()
            self.M.create_gmsh_instance()
            self.tag = gmsh.model.occ.addEllipseArc(self.P1.tag, self.C.tag, self.M.tag, self.P2.tag, tag)

    def __repr__(self) -> str:
        return f"EllipseArc({self.P1.pos}, {self.P2.pos})"

    @classmethod
    def create_or_get(cls, P_start: any, P_center: any, P_major: any, P_end: any):
        return cls(P_start, P_center, P_major, P_end)


### SURFACE ELEMENTS ###

class Surface:
    """
    A class to represent a surface in 3D space.

    :cvar surfaces_registry: A class-level attribute that keeps track of all created surfaces.
    :vartype surfaces_registry: list
    :cvar curve_loop_registry: A class-level attribute that keeps track of all curve loops. Each curve loop is stored as a dict with the keys 'curves' and 'tag'. This list is necessary when creating surfaces with holes. The curve-loops of the holes may already have been created when creating the surface of the hole, in which case we get the tag of the existing curve-loop instead of creating a new one.
    :vartype curve_loop_registry: list

    :ivar boundary_curves: A list of Curve objects that define the closed outer boundary of the surface. This is an instance-level attribute.
    :vartype boundary_curves: list
    :ivar inner_boundary_curves: A list of lists of Curve objects. Each list of curves defines the closed boundary of a hole in the surface. This is an instance-level attribute.
    :vartype inner_boundary_curves: list
    :ivar curve_loop_tag: A unique identifier for the curve loop of the outer boundary, initially set to None. This is an instance-level attribute.
    :vartype curve_loop_tag: int
    :ivar inner_curve_loop_tags: A list of unique identifiers for the inner curve loops. Each tag corresponds to the curve-loop of a hole in the surface. This is an instance-level attribute.
    :vartype inner_curve_loop_tags: list
    :ivar surface_tag: A unique identifier for the surface, initially set to None. This is an instance-level attribute.
    :vartype surface_tag: int
    :ivar physical_boundary_tag: A unique identifier for the physical group of the boundary curves, initially set to None. This is an instance-level attribute.
    :vartype physical_boundary_tag: int
    :ivar physical_boundary_name: A name for the physical group of the boundary curves, initially set to None. This is an instance-level attribute.
    :vartype physical_boundary_name: str
    :ivar physical_inner_boundary_tags: A list of unique identifiers for the physical groups of the inner boundary curves. This is an instance-level attribute.
    :vartype physical_inner_boundary_tags: list
    :ivar physical_inner_boundary_names: A list of names for the physical groups of the inner boundary curves. This is an instance-level attribute.
    :vartype physical_inner_boundary_names: list
    :ivar physical_surface_tag: A unique identifier for the physical group of the surface, initially set to None. This is an instance-level attribute.
    :vartype physical_surface_tag: int
    :ivar physical_surface_name: A name for the physical group of the surface, initially set to None. This is an instance-level attribute.
    :vartype physical_surface_name: str
    :ivar material: The material-ID of the surface. Used to specify material properties in the .regions file, initially set to None. This is an instance-level attribute.
    :vartype material: any
    """

    surfaces_registry = []
    curve_loop_registry = []

    def __init__(self, boundary_curves: List[Curve] = [], inner_boundary_curves: List[List[Curve]] = []):
        """
        Constructs the attributes for the surface object.

        :param boundary_curves: A list of Curve objects that define the outer boundary of the surface. The curves must form a closed loop.
        :type boundary_curves: list[Curve]
        :param inner_boundary_curves: A list of lists of Curve objects. Each list of curves defines the boundary of a hole in the surface.
        :type inner_boundary_curves: list[list[Curve]]
        """
        self.boundary_curves = boundary_curves
        self.inner_boundary_curves = inner_boundary_curves

        self.curve_loop_tag = None
        self.inner_curve_loop_tags: List[int] = []
        self.surface_tag = None

        self.physical_boundary_tag = None
        self.physical_boundary_name = None
        self.physical_inner_boundary_tags = []
        self.physical_inner_boundary_names = []

        self.physical_surface_tag = None
        self.physical_surface_name = None

        self.material = None

        Surface.surfaces_registry.append(self)

    def create_gmsh_instance(self):
        if self.surface_tag == None:
            for curve in self.boundary_curves + sum(self.inner_boundary_curves, []):
                curve.create_gmsh_instance()

            self.curve_loop_tag = self.create_or_get_curve_loop(self.boundary_curves)
            self.inner_curve_loop_tags = [self.create_or_get_curve_loop(curves) for curves in self.inner_boundary_curves]
            self.surface_tag = gmsh.model.occ.add_plane_surface([self.curve_loop_tag] + self.inner_curve_loop_tags)

    def add_physical_boundary(self, name: str = ''):
        self.physical_boundary_tag = gmsh.model.add_physical_group(1, [curve.tag for curve in self.boundary_curves], name=name)
        self.physical_boundary_name = name

    def add_physical_surface(self, name: str = ''):
        self.physical_surface_tag = gmsh.model.add_physical_group(2, [self.surface_tag], name=name)
        self.physical_surface_name = name

    def get_circumference(self):
        return sum([curve.get_length() for curve in self.boundary_curves])

    @classmethod
    def update_tags(cls, surfaces):
        """
        Updates the tags of model entities of dimension lower than 2.

        When saving the geometry as a .brep file, these tags may be (seemingly arbitrarily) changed. This method ensures that the tags are consistent and correctly assigned.

        Steps:
        1) Find the tags of all outer boundary curves of every surface.
        2) Divide the boundary curves into groups. Each group of curves are either on the boundary of a single surface or on the intersection of the same multiple surfaces.
        3) Update the tags of the curves in the curve groups. The tags are assigned not to their corresponding curve but to any curve in the group.
        4) Update the tags of the points. Points which are in multiple curve-groups are assigned to a new group. Point tags are assigned based on the groups they are in.

        :param surfaces: A list of Surface objects to update the tags for.
        :type surfaces: list[Surface]
        """

        gmsh.model.occ.synchronize()
        # 1) Find the tags of all outer boundary curves of every surface
        # 1.1) Find the inner surfaces of each surface with holes
        surfaces_inner_surface_indices = []  # List of lists of indices of surfaces. Each list of indices corresponds to the surfaces that are inside the surface with the same index.
        for surface in surfaces:
            inner_surface_indices = []
            if surface.inner_boundary_curves:  # If the surface has holes
                for inner_boundary in surface.inner_boundary_curves:
                    for surface in surfaces:  # Loop through all surfaces to find the surfaces that are inside the outer surface.
                        if set(inner_boundary) & set(surface.boundary_curves):  # If the two sets of curves have any common curves, the inner surface is inside the outer surface.
                            inner_surface_indices.append(surfaces.index(surface))  # Add the index of the inner surface to the list of inner surfaces.
            surfaces_inner_surface_indices.append(inner_surface_indices)

        # 1.2) Find the tags of the outer boundary curves of each surface by finding the boundary of the surface (inner and outer) and removing the boundary curves of the inner surfaces.
        surfaces_outer_boundary_tags = [set([abs(tag) for dim, tag in gmsh.model.get_boundary([(2, surface.surface_tag)])]) for surface in surfaces]
        for surface_i in range(len(surfaces)):
            if surfaces[surface_i].inner_boundary_curves:
                surface_inner_surfaces_boundary_tags = set.union(*[surfaces_outer_boundary_tags[i] for i in surfaces_inner_surface_indices[surface_i]])  # The boundary tags of the inner surfaces
                surfaces_outer_boundary_tags[surface_i] = surfaces_outer_boundary_tags[surface_i] - surface_inner_surfaces_boundary_tags

                # 2) Divide the boundary curves into groups. Each group of curves are either on the boundary of a single surface or on the intersection of multiple surfaces, but not both.
        # We also find the tags of the curves in each group.
        surface_outer_boundary_curves = [set(surface.boundary_curves) for surface in surfaces]

        curve_groups = []  # List of sets of curves. Each set of curves is a group, defined as curves which lie only on the boundary of a single surface or on the intersection of multiple surfaces.
        curve_group_tags = []  # List of sets of tags. Each set of tags corresponds to the set of curves in curve_groups.
        for i, si_curves in enumerate(surface_outer_boundary_curves):
            for j, sj_curves in enumerate(surface_outer_boundary_curves[i + 1:]):
                j += i + 1
                common_curves = si_curves & sj_curves
                if common_curves:
                    curve_groups.append(common_curves)  # Add the common curves to the list of curve groups
                    si_curves -= common_curves  # Remove the common curves from the surface boundary curves
                    sj_curves -= common_curves  # Remove the common curves from the surface boundary curves

                    curve_group_tags.append(surfaces_outer_boundary_tags[i] & surfaces_outer_boundary_tags[j])  # Add the tags of the common curves to the list of curve group tags
                    surfaces_outer_boundary_tags[i] -= curve_group_tags[-1]  # Remove the tags of the common curves from the surface boundary tags
                    surfaces_outer_boundary_tags[j] -= curve_group_tags[-1]  # Remove the tags of the common curves from the surface boundary tags

            curve_groups.append(si_curves)  # Add the remaining curves to the list of curve groups
            curve_group_tags.append(surfaces_outer_boundary_tags[i])  # Add the tags of the remaining curves to the list of curve group tags

        # 3) Update the tags of the curves in the curve groups
        # The tags are assigned not to their corresponding curve but to any curve in the group.
        for group, group_tags in zip(curve_groups, curve_group_tags):
            for curve, tag in zip(group, group_tags):
                curve.tag = tag

        # 4) We have now updated the tags of all curves. Next we update the tags of the points.

        # 4.1) Get all points in each group of curves and the tags of the points in each group of curves
        curve_groups_points = [set([point for curve in group for point in [curve.P1, curve.P2]]) for group in curve_groups]
        curve_groups_point_tags = [set(sum([list(gmsh.model.get_adjacencies(1, tag)[1]) for tag in group_tags], [])) for group_tags in curve_group_tags]

        # 4.2) Points which are in multiple curve-groups are assigned to a new group.
        # These points will be removed from the groups they are in and assigned to the new group, based on the groups they are in.
        # Iterate trough all points and check which groups they are in. Points in same groups will be assigned to a new group.
        all_points = set.union(*curve_groups_points)
        point_new_groups = {}  # Dictionary with keys as tuples of indices of the groups the point is in, and values as lists of points in the same groups.
        for point in all_points:
            groups_point_is_in = [i for i, group in enumerate(curve_groups_points) if point in group]
            # If the point is in multiple groups, remove the point from all groups
            if len(groups_point_is_in) > 1:
                for i in groups_point_is_in:
                    curve_groups_points[i].remove(point)  # Remove the point from all groups, as it will be assigned to a new group.
                # Sort the groups the point is in, make it a tuple and use it as a key in a dictionary. The value is a list of all points in the same groups.
                point_new_groups[tuple(sorted(groups_point_is_in))] = point_new_groups.get(tuple(sorted(groups_point_is_in)), []) + [point]

        # 4.3) Update the tags of the points in the new groups
        # Get the tags of all points in each group of points as the boundary of the group of curves
        for group_indices, points in point_new_groups.items():
            # The tags of the points in the new group is the intersection of the tags of the points in the groups the point is in.
            point_tags = set.intersection(*[curve_groups_point_tags[i] for i in group_indices])

            # Update the tags of the points in the group
            for point, point_tag in zip(points, point_tags):
                point.tag = point_tag

            # Remove the tags of the points in the new group from the tags of the points in the groups the point was in before it was assigned to the new group.
            for i in group_indices:
                curve_groups_point_tags[i] -= point_tags

        # 4.4) Update the tags of points in the remaining groups 'curve_groups_points'
        for group, group_tags in zip(curve_groups_points, curve_groups_point_tags):
            for point, tag in zip(group, group_tags):
                point.tag = tag

    @classmethod
    def remove_from_registry(cls, surfaces):
        for surface in surfaces:
            cls.surfaces_registry.remove(surface)

    @classmethod
    def create_or_get_curve_loop(cls, curves):
        """
        Creates a curve loop if it does not already exist, otherwise returns the existing curve loop.

        A curve loop is a sequence of curves that form a closed loop. This method checks if a curve loop with the given curves already exists in the curve_loop_registry.
        If it does, the method returns the tag of the existing curve loop.
        If it doesn't, the method creates a new curve loop, adds it to the curve_loop_registry, and returns its tag.

        :param curves: A list of Curve objects that define the curve loop.
        :type curves: list[Curve]

        :return: The tag of the curve loop.
        :rtype: int
        """
        for curve_loop in cls.curve_loop_registry:
            if curve_loop['curves'] == set(curves):
                return curve_loop['tag']

        tag = gmsh.model.occ.addCurveLoop([curve.tag for curve in curves])
        cls.curve_loop_registry.append({'tag': tag, 'curves': set(curves)})
        return tag

    @classmethod
    def replace_overlapping_edges(cls):
        """
        Replaces overlapping boundary-curves of type 'Line' across all surfaces.

        If multiple surface boundaries contain lines which are overlapping, the overlapping lines are replaced by the fraction
        of the line which is unique to the surface as well as the fraction of the line which is shared with the other surface.

        Steps:
        1) Sort all existing lines into groups of lines which are colinear.
        2) For each group of colinear lines, make a list of all the unique points used, sorted by their location on the colinear line.
        3) For each line of each surface, replace the line by fragments of the line, defined by the points in the list from step 2.
        """
        # 1) Sort all existing lines into groups of lines which are colinear
        lines = [line for line in Curve.curves_registry if type(line) == Line]
        if len(lines) == 0:  # If there are no lines, skip the rest of the function
            return
        colinear_groups = [[lines[0]]]
        for line in lines[1:]:
            for group in colinear_groups:
                if Line.is_colinear(line, group[0]):
                    group.append(line)
                    break
            else:
                colinear_groups.append([line])

        # 2) For each group of colinear lines, make a list of all the unique points used, sorted by their location on the colinear line
        colinear_groups_points = []
        for group in colinear_groups:
            points = []
            for line in group:
                points.append(line.P1)
                points.append(line.P2)
            points = list(set(points))  # Remove duplicates
            angle = np.arctan2((line.P2.pos - line.P1.pos)[1], (line.P2.pos - line.P1.pos)[0])  # Angle of the lines with respect to the x-axis
            positions = [p.pos - points[0].pos for p in points]  # Move the points so that the colinear line passes through the origin
            positions = [rotate_vector(p, -angle)[0] for p in positions]  # Rotate the points so that the lines are parallel to the x-axis, making it a 1D problem.
            points = np.array(points)[np.argsort(positions)].tolist()  # Sort the points by their position along the colinear line
            colinear_groups_points.append(points)

            # 3) For each line for each surface, replace the line by fragments of the line, defined by the points in the list from step 2
        for area in cls.surfaces_registry:  # For each rectangle
            for l, line in enumerate(area.boundary_curves):  # For each line
                for i, group in enumerate(colinear_groups):  # Find the group of colinear lines that the line belongs to
                    if line in group:
                        if len(group) == 1:  # If the line is not colinear with any other line, skip it
                            break
                        # Find the points that define the line fragments
                        points = colinear_groups_points[i]
                        line_point1_index = points.index(line.P1)
                        line_point2_index = points.index(line.P2)
                        if line_point1_index > line_point2_index:
                            # If the points orientation differs from the line orientation, reverse the list of points
                            # The points are sorted by their position along the colinear line, which is not necessarily the same as the orientation of the line.
                            # The orientation of the fragments must match the orientation of the line.
                            points.reverse()
                            line_point1_index = points.index(line.P1)
                            line_point2_index = points.index(line.P2)
                        line_fragment_points = points[line_point1_index:line_point2_index + 1]  # The points that define the line fragments

                        # Create the line fragments
                        line_fragments = [Line.create_or_get(line_fragment_points[i], line_fragment_points[i + 1]) for i in range(len(line_fragment_points) - 1)]

                        if len(line_fragments) > 1:  # If the line is split into multiple fragments, remove the old line and insert the new fragments into the boundary curves of the surface.
                            Line.remove_from_registry([line])  # Remove the old line from the lines-registry.
                            for fragment in line_fragments:
                                area.boundary_curves.insert(area.boundary_curves.index(line), fragment)  # Insert the new line fragments into the boundary curves of the surface.
                            area.boundary_curves.remove(line)  # Remove the original line from the boundary curves of the surface.

    @classmethod
    def set_correct_boundary_orientation(self, surfaces):
        """
        When creating surfaces with holes, the boundaries must have a specific orientation to ensure that the surfaces are correctly defined.
        This method sets the correct orientation of the boundaries of the surfaces.
        The orientation of the boundary is determined by the orientation of the curve-loop, which is determined by the orientation of the first curve in the loop.
        We therefore must ensure that the first curve of the curve-loop is oriented correctly.
        """
        # It seems to work to just set all the boundaries to have the same orientation. Very simple and does not require any complex logic.
        for surface in surfaces:
            outer_boundary_points = sum([[curve.P1, curve.P2] for curve in surface.boundary_curves], [])
            mean_point = np.mean([point.pos for point in outer_boundary_points], axis=0)  # Mean point of the boundary (Center of mass)
            mean_to_P1 = surface.boundary_curves[0].P1.pos - mean_point  # Vector from the mean point to the first point of the boundary curve
            mean_to_P2 = surface.boundary_curves[0].P2.pos - mean_point  # Vector from the mean point to the second point of the boundary curve

            # Using the two vectors we can check the orientation of the first curve in the loop, based on the sign of the determinant of the matrix formed by the two vectors.
            if np.linalg.det(np.column_stack((mean_to_P1[:-1], mean_to_P2[:-1]))) < 0:
                # If the determinant is negative we reverse the orientation so that it is positive (counter-clockwise orientation)
                surface.boundary_curves[0].P1, surface.boundary_curves[0].P2 = surface.boundary_curves[0].P2, surface.boundary_curves[0].P1


class Disk(Surface):
    """
    A class to represent a disk. Inherits from the Surface class.

    :ivar rad: The radius of the disk. This is an instance-level attribute.
    :vartype rad: float
    :ivar partitions: The number of partitions to divide the boundary of the disk into when generating boundary curves. This is an instance-level attribute.
    :vartype partitions: int
    :ivar center_point: The center point of the disk. Can be a position ([x, y, z]) or a 'Point' object. This is an instance-level attribute.
    :vartype center_point: Point
    :ivar physicalEdgePointTag: A unique identifier for the physical group of the edge point. Used in pro-template for fixing phi=0 in the outer matrix boundary as well as on the filament boundaries. This is an instance-level attribute.
    :vartype physicalEdgePointTag: int
    """

    def __init__(self, center_point: any, rad: float, partitions: int = 4):
        """
        Constructs the attributes for the disk object.

        :param center_point: The center point of the disk. Can be a position ([x, y, z]) or a 'Point' object.
        :type center_point: any
        :param rad: The radius of the disk.
        :type rad: float
        :param partitions: The number of partitions to divide the boundary of the disk into when generating boundary curves, defaults to 4
        :type partitions: int, optional
        """
        super().__init__()
        self.rad = rad
        self.partitions = partitions

        self.center_point = center_point if isinstance(center_point, Point) else Point.create_or_get(center_point)
        self.boundary_curves = self.generate_boundary_curves()
        self.inner_boundary_curves = []

        self.physicalEdgePointTag = None  # Used in pro-template for fixing phi=0 in the outer matrix boundary as well as on the filament boundaries.

    def generate_boundary_curves(self):
        """
        Generates the boundary curves for the disk.

        This method divides the boundary of the disk into 'partitions' number of segments and creates a CircleArc for each segment.

        :return: A list of CircleArc objects that define the boundary of the disk.
        :rtype: list
        """
        edgePoints = [np.array(self.center_point.pos) + np.array(cylindrical_to_cartesian(self.rad, 2 * np.pi * n / self.partitions + np.pi + cartesian_to_cylindrical(self.center_point.pos[0], self.center_point.pos[1], self.center_point.pos[2])[1], 0)) for n in range(self.partitions)]
        boundary_curves = [CircleArc(edgePoints[n], self.center_point, edgePoints[(n + 1) % self.partitions]) for n in range(self.partitions)]
        return boundary_curves


class Rectangle(Surface):
    """
    A class to represent a Rectangle surface. Inherits from the Surface class.

    :ivar width: The width of the rectangle. This is an instance-level attribute.
    :vartype width: float
    :ivar height: The height of the rectangle. This is an instance-level attribute.
    :vartype height: float
    :ivar center_point: The center point of the Rectangle. Can be a position ([x, y, z]) or a 'Point' object. This is an instance-level attribute.
    :vartype center_point: Point
    """

    def __init__(self, center_point: any, width: float, height: float):
        """
        Constructs the attributes for the Rectangle object.
        """
        super().__init__()
        self.width = width
        self.height = height

        self.center_point = center_point if isinstance(center_point, Point) else Point.create_or_get(center_point)
        self.boundary_curves = self.generate_boundary_lines()
        self.inner_boundary_curves = []

    def generate_boundary_lines(self):
        """
        Generates the boundary lines for the Rectangle.

        :return: A list of Line objects that define the closed loop boundary of the Rectangle.
        :rtype: list
        """

        edgePoints = np.array(self.center_point.pos) + (np.array([self.width / 2.0, -self.height / 2.0, 0]), np.array([self.width / 2.0, self.height / 2.0, 0]), np.array([-self.width / 2.0, self.height / 2.0, 0]), np.array([-self.width / 2.0, -self.height / 2.0, 0]))
        boundary_curves = [Line(edgePoints[n], edgePoints[(n + 1) % 4]) for n in range(4)]
        return boundary_curves


class Square(Surface):
    """
    A class to represent a Square surface. Inherits from the Surface class.

    :ivar rad: The radius of the biggest circle fitting inside the square(can be interpreted as the smallest boundary distance to center). This is an instance-level attribute.
    :vartype rad: float
    :ivar partitions: The number of partitions to divide the boundary of the square into when generating the boundary curves. This is an instance-level attribute.
    :vartype partitions: int
    :ivar center_point: The center point of the Square. Can be a position ([x, y, z]) or a 'Point' object. This is an instance-level attribute.
    :vartype center_point: Point
    """

    def __init__(self, center_point: any, rad: float, partitions: int = 4):
        """
        Constructs the attributes for the Square object.

        :param center_point: The center point of the Square. Can be a position ([x, y, z]) or a 'Point' object.
        :type center_point: any
        :param rad: The radius of a circle fitting inside the Square.
        :type rad: float
        :param partitions: The number of partitions to divide the boundary of the Square into when generating the boundary curves, defaults to 4
        :type partitions: int, optional
        """
        super().__init__()
        self.rad = rad
        self.partitions = partitions

        self.center_point = center_point if isinstance(center_point, Point) else Point.create_or_get(center_point)
        self.boundary_curves = self.generate_boundary_lines()
        self.inner_boundary_curves = []

    def generate_boundary_lines(self):
        """
        Generates the boundary lines for the Square.

        This method divides the boundary of the square into 'partitions' number of Lines.

        :return: A list of Line objects that define the closed loop boundary of the Square.
        :rtype: list
        """
        if self.partitions != 4:
            raise ValueError(
                f"FiQuS does not support a square air boundary with partition count: {self.partitions}!"
            )

        edgePoints = np.array(self.center_point.pos) + (np.array([self.rad, -self.rad, 0]), np.array([self.rad, self.rad, 0]), np.array([-self.rad, self.rad, 0]), np.array([-self.rad, -self.rad, 0]))
        boundary_curves = [Line(edgePoints[n], edgePoints[(n + 1) % (self.partitions)]) for n in range(self.partitions)]
        return boundary_curves


class Semicircle(Surface):
    """
    A class to represent a Semicircle surface (aligned on the right side of y-axis). Inherits from the Surface class.

    :ivar offset_x: The offset of the semicircle diameter center in the negative x direction. This is an instance-level attribute.
    :vartype offset_x: float
    :ivar rad: The radius of the biggest circle fitting inside the square(can be interpreted as the smallest boundary distance to center). This is an instance-level attribute.
    :vartype rad: float
    :ivar partitions: The number of partitions to divide the boundary of the square into when generating the boundary curves. This is an instance-level attribute.
    :vartype partitions: int
    :ivar center_point: The center point of the Square. Can be a position ([x, y, z]) or a 'Point' object. This is an instance-level attribute.
    :vartype center_point: Point
    """
    # this is used in the meshing process to force the gmsh cohomology cut on the diameter of the semicircle domain
    physical_cohomology_subdomain = None

    def __init__(self, center_point: any, offset_x: float, rad: float, partitions: int = 4):
        """
        Constructs the attributes for the Square object.

        :param center_point: The center point of the Square. Can be a position ([x, y, z]) or a 'Point' object.
        :type center_point: any
        :param offset_x: The offset of the semicircle diameter center in the negative x direction. This is an instance-level attribute.
        :type offset_x: float
        :param rad: The radius of the Semicircle.
        :type rad: float
        :param partitions: The number of partitions to divide the boundary of the Semicircle into when generating the boundary curves, defaults to 4.
        :type partitions: int, optional
        """
        super().__init__()
        self.offset_x = offset_x
        self.rad = rad
        self.partitions = partitions

        self.center_point = center_point if isinstance(center_point, Point) else Point.create_or_get(center_point)
        self.boundary_curves = self.generate_boundary_lines()
        self.inner_boundary_curves = []

    def generate_boundary_lines(self):
        """
        Generates the boundary lines for the Square.

        This method divides the boundary of the semicircle into 'partitions' number of Lines.

        :return: A list of Line objects that define the closed loop boundary of the Semicircle.
        :rtype: list
        """
        if self.partitions != 4:
            raise ValueError(
                f"FiQuS does not support a semicircle air boundary with partition count: {self.partitions}!"
            )
        if self.offset_x > self.rad:
            raise ValueError(
                f"FiQuS does not support a semicircle with center offset bigger than radius!"
            )

        edgePoints = np.array(self.center_point.pos) + (np.array([-self.offset_x, -self.rad, 0]), np.array([self.rad - self.offset_x, 0, 0]), np.array([-self.offset_x, self.rad, 0]), np.array([-self.offset_x, 0, 0]))
        boundary_curves = []
        for n in range(self.partitions):
            if n < (self.partitions / 2):
                boundary_curves.append(CircleArc(edgePoints[n], [-self.offset_x, 0, 0], edgePoints[n + 1]))
            else:
                boundary_curves.append(Line(edgePoints[n], edgePoints[(n + 1) % (self.partitions)]))
        return boundary_curves

    def add_physical_boundary(self, name: str = ''):
        """
        This method extends the ususal procedure defined in 'Surface'.
        It generates an additional cohomology subdomain physical group and stores its tag as additional attribute """
        self.physical_boundary_tag = gmsh.model.add_physical_group(1, [curve.tag for curve in self.boundary_curves], name=name)
        self.physical_boundary_name = name
        # additional procedure - add the arc of semicircle boundary as cohomology subdomain
        _, lines = gmsh.model.get_adjacencies(2, self.surface_tag)
        self.physical_cohomology_subdomain = gmsh.model.add_physical_group(1, lines[0:int(len(self.boundary_curves) / 2)], name=name + ' subdomain')


class SquareSection(Surface):
    """
    A class to represent a square surface intersected with the quarter of a circle (used as surface in the 'periodic_square' model geometry). Inherits from the Surface class.

    :ivar rad: The max radius of a circle fitting inside the initial Square, which is then intersected by intersection_curve. This is an instance-level attribute.
    :vartype rad: float
    :ivar intersection_curve: The Curve intersecting the square(defined by exact 2 point on the square boundary). This is an instance-level attribute.
    :vartype intersection_curve: Curve object
    :ivar partitions: The number of partitions to divide the resulting boundary of the SquareSection into when generating boundary curves. This is an instance-level attribute.
    :vartype partitions: int
    :ivar center_point: The center point based on which the square section is extruded outwards. Can be a position ([x, y, z]) or a 'Point' object. This is an instance-level attribute.
    :vartype center_point: Point
    """

    def __init__(self, center_point: any, rad: float, intersection_curve: Curve, partitions: int = 5):
        """
        Constructs the attributes for the SquareSection object.

        :param center_point: The center point of extrusion for the SquareSection. Can be a position ([x, y, z]) or a 'Point' object.
        :type center_point: any
        :param rad: The max radius of a circle fitting inside the Square before intersection.
        :type rad: float
        :param partitions: The number of partitions to divide the boundary of the SquareSection into when generating boundary curves, should allways be 5
        :type partitions: int, optional
        """
        super().__init__()
        self.rad = rad
        self.intersection_curve = intersection_curve
        self.partitions = partitions

        self.center_point = center_point if isinstance(center_point, Point) else Point.create_or_get(center_point)
        self.outer_boundary_curves: List[Curve] = []
        self.cut_curves: List[Curve] = []
        self.boundary_curves = self.generate_boundary_lines()

    def generate_boundary_lines(self):
        """
        Generates the boundary lines for the SquareSection.

        This method divides the boundary of the square into 'partitions' number of segments and creates a line for each segment.

        :return: A list of line objects that define the boundary of the IntersectedSquare.
        :rtype: list
        """
        if self.partitions != 5:
            raise ValueError(
                f"FiQuS does not support a SquareSections with partition count: {self.partitions}!"
            )
        if not self.center_point.pos[0] == self.center_point.pos[1] == self.center_point.pos[2] == 0:
            print(self.center_point.pos)
            raise ValueError(
                f"FiQuS does not support a SquareSections with center extrusion point: {self.center_point}!"
            )

        # extrude intersection curves to the outside
        line1 = Line.create_or_get(self.intersection_curve.P2, Point.create_or_get(self.intersection_curve.P2.pos / np.linalg.norm(self.intersection_curve.P1.pos) * self.rad))
        line4 = Line.create_or_get(self.intersection_curve.P1, Point.create_or_get(self.intersection_curve.P1.pos / np.linalg.norm(self.intersection_curve.P1.pos) * self.rad))
        self.cut_curves = [line1, line4]
        # close IntersectedSquare of with outer boundary lines
        line2 = Line.create_or_get(line1.get_furthest_point(), Point.create_or_get(line1.get_furthest_point().pos + line4.get_furthest_point().pos))
        line3 = Line.create_or_get(line4.get_furthest_point(), line2.get_furthest_point())
        self.outer_boundary_curves = [line2, line3]

        boundary_curves = [self.intersection_curve, line1, line2, line3, line4]
        return boundary_curves


class Composite():
    """
    A helper class to handle a composite surface made up by multiple smaller surfaces.

    :ivar sections: A List of connected Surfaces which create a Composite regime.
    :vartype sections: List of Surfaces
    """

    def __init__(self, sections: List[Surface]):
        """
        Constructs the attributes for the Composite object.

        :type center_point: any
        :param sections: A List of Surface Sections which make up the Composite.
        :type sections: List of Surfaces

        """
        super().__init__()

        self.sections = sections

        self.physical_surface_tag = None
        self.physical_surface_name = None
        self.physical_boundary_tag = None
        self.physical_boundary_name = None
        self.strand_bnd_physicalEdgePointTag = None

        self.physical_inner_boundary_tags = []
        self.physical_inner_boundary_names = []

        self.physical_cuts = []
        self.inner_boundary_curves = []
        self.boundary_curves = self.generate_boundary_lines()

    def generate_boundary_lines(self):
        """
        Generates the boundary lines for the composite surface, made up by the section surfaces given on initialization.

        :return: A list of line objects that define the (outer) boundary of the composition.
        :rtype: list
        """
        boundary_curves = []
        for section in self.sections:
            boundary_curves.extend(section.outer_boundary_curves)
        return boundary_curves

    def add_physical_surface(self, name: str = ''):
        """
        Generates a physical surface group containing all the section surfaces.
        """
        self.physical_surface_tag = gmsh.model.add_physical_group(2, [section.surface_tag for section in self.sections], name=name)
        self.physical_surface_name = name

    @abstractmethod
    def add_physical_cuts(self, name):
        pass

    @abstractmethod
    def add_physical_boundaries(self, name):
        pass


class CompositeSquare(Composite):
    """
    A class to represent the Composite Square structure of the air surface in the 'periodic_square' model. Inherits general functionality from 'Composite'.
    """
    # special boundary tags
    physical_left_boundary_tag = None
    physical_right_boundary_tag = None
    physical_top_boundary_tag = None
    physical_bottom_boundary_tag = None

    def add_physical_cuts(self, name: str = ''):
        """
        Generates the two physical groups for the CompositeSquare air domain in the 'periodic_square' model.
        Cuts are used in getDP to imprint a source field in OmegaCC.
        """
        # generate physical cuts
        self.physical_cuts = []
        vertical_cuts_tags = [-self.sections[2].cut_curves[0].tag, self.sections[1].cut_curves[1].tag]
        self.physical_cuts.append(gmsh.model.add_physical_group(1, vertical_cuts_tags, name=name + " vertical"))
        vertical_boundary_tags = [self.sections[3].intersection_curve.tag, self.sections[0].intersection_curve.tag]
        self.physical_cuts.append(gmsh.model.add_physical_group(1, vertical_boundary_tags, name=name + " vertical boundary"))

        horizontal_cuts_tags = [-self.sections[0].cut_curves[1].tag, self.sections[1].cut_curves[0].tag]
        self.physical_cuts.append(gmsh.model.add_physical_group(1, horizontal_cuts_tags, name=name + " horizontal"))
        horizontal_boundary_tags = [self.sections[0].intersection_curve.tag, self.sections[1].intersection_curve.tag]
        self.physical_cuts.append(gmsh.model.add_physical_group(1, horizontal_boundary_tags, name=name + " horizontal boundary"))

    def add_physical_boundaries(self, name: str = ''):
        """
        Generates direction specific physical boundary groups for the the composite square and stores the group tags as additional attributes.
        """
        # add complete boundary closed loop
        self.physical_boundary_tag = gmsh.model.add_physical_group(1, [curve.tag for curve in self.boundary_curves], name=name)
        self.physical_boundary_name = name
        # here we actually have to get the line tags based on the sub surfaces because dim1 object-tags are not preserved in gmsh :(
        _, lines_sec0 = gmsh.model.get_adjacencies(2, self.sections[0].surface_tag)
        _, lines_sec1 = gmsh.model.get_adjacencies(2, self.sections[1].surface_tag)
        _, lines_sec2 = gmsh.model.get_adjacencies(2, self.sections[2].surface_tag)
        _, lines_sec3 = gmsh.model.get_adjacencies(2, self.sections[3].surface_tag)

        self.physical_left_boundary_tag = gmsh.model.add_physical_group(1, [lines_sec3[3], lines_sec0[2]], name=name + " left")
        self.physical_bottom_boundary_tag = gmsh.model.add_physical_group(1, [lines_sec0[3], lines_sec1[2]], name=name + " bottom")
        self.physical_right_boundary_tag = gmsh.model.add_physical_group(1, [lines_sec1[3], lines_sec2[2]], name=name + " right")
        self.physical_top_boundary_tag = gmsh.model.add_physical_group(1, [lines_sec2[3], lines_sec3[2]], name=name + " top")

        # set gauge point on boundary
        self.strand_bnd_physicalEdgePointTag = gmsh.model.addPhysicalGroup(0, [self.sections[2].outer_boundary_curves[0].points[1].tag])


class Hexagon(Surface):
    """
    A class to represent a hexagon. Inherits from the Surface class.

    :ivar rad: The radius of the hexagon.
    :vartype rad: float
    :ivar center_point: The center point of the hexagon. Can be a position ([x, y, z]) or a 'Point' object.
    :vartype center_point: Point
    :ivar rotation: The rotation of the hexagon in radians.
    :vartype rotation: float
    """

    def __init__(self, center_point: any, rad: float, rotation: float = 0):
        """
        Constructs the attributes for the hexagon object.

        :param center_point: The center point of the hexagon. Can be a position ([x, y, z]) or a 'Point' object.
        :type center_point: any
        :param rad: The radius of the hexagon.
        :type rad: float
        :param rotation: The rotation of the hexagon in radians.
        :type rotation: float
        """
        super().__init__()
        self.rad = rad
        self.center_point = center_point if isinstance(center_point, Point) else Point.create_or_get(center_point)
        self.rotation = rotation
        self.boundary_curves = self.generate_boundary_curves()
        self.inner_boundary_curves = []

    def generate_boundary_curves(self):
        """
        Generates the boundary curves for the hexagon.

        This method creates the boundary of the hexagon by rotating a vector from the center-point to the first edge-point.

        :return: A list of Line objects that define the boundary of the hexagon.
        :rtype: list
        """
        edgePoints = [np.array(self.center_point.pos) + rotate_vector(np.array([self.rad, 0, 0]), 2 * np.pi * n / 6 + self.rotation) for n in range(6)]
        boundary_curves = [Line.create_or_get(edgePoints[n], edgePoints[(n + 1) % 6]) for n in range(6)]
        return boundary_curves


### END GEOMETRY ###


class TwistedStrand:
    """
    A class to represent a 2D cross section of a twisted strand.

    :ivar filaments: Each list of surfaces represent six filaments in the same layer.
    :vartype filaments: list[list[Surface]]
    :ivar Matrix: List of surfaces corresponding to the matrix partitions.
    :vartype Matrix: list[Surface]
    :ivar Air: A surface representing the air region.
    :vartype Air: Surface
    """

    def __init__(self) -> None:
        """
        Initializes the TwistedStrand object.
        """
        self.filaments: List[List[Surface]] = []
        self.filament_holes: List[List[Surface]] = []  # If the filaments have holes (only for certain geometries obtained via YAML files)
        self.matrix: List[Surface] = []  # Inner, middle, outer
        self.air: List[Surface] = []  # one or more air surfaces
        self.air_composition: Composite = None  # Composite structure of multiple air (if more than one air surface is defined)
        self.domain_cut: int = None

    def create_filament_center_points(self, N_points: int, filament_radius: float, outer_boundary_radius: float, inner_boundary_radius: float, circular_filament_distribution=True):
        """
        Creates the center-points of N_points filaments. The points are distributed in layers---the first layer containing 6 points, the second 12, the third 18, etc---and groups of
        6 points satisfying rotational symmetry when rotated by pi/3. The first layer is composed of one group, the second of two groups, etc.

        :param N_points: The number of points to create.
        :type N_points: int
        :param filament_radius: The radius of the filament.
        :type filament_radius: float
        :param outer_boundary_radius: The radius of the outer boundary.
        :type outer_boundary_radius: float
        :param inner_boundary_radius: The radius of the inner boundary.
        :type inner_boundary_radius: float
        :param circular_filament_distribution: If True, points are distributed in a circular pattern. If False, points are distributed in a hexagonal pattern. Defaults to True.
        :type circular_filament_distribution: bool, optional

        :return: A list of lists of lists of points representing the filament center-points for each filament in each group. Each point is a list of three coordinates [x, y, z] and each list of points represents a group of 6 points satisfying rotational symmetry.
        :rtype: list[list[list[float]]]
        """
        # The hexagonal grid can be created by transforming the cartesian coordinate grid to a hexagonal grid.
        # Point centers are created as unit vectors in the hexagonal grid, and then transformed to cartesian coordinates.
        # This function takes as input a vector in the hexagonal grid and returns its distance from the origin in the cartesian coordinate system.
        point_relative_magnitude = lambda v: np.sqrt(v[0] ** 2 + 2 * v[0] * v[1] * np.cos(np.pi / 3) + v[1] ** 2)

        def create_first_hexant_points(N_points_per_hexant, outer_inner_boundary_ratio, possible_next_points=np.array([[1, 0]]), points=np.empty((0, 2))):
            """
            Recursive algorithm used to create the first hexant of an hexagonal point grid. These points can subsequently be rotated by n*pi/3 (for n in [1,5]) radians to create the next points.
            The function returns the points in the first sextant of the matrix, sorted by distance from the origin.

            The points are created in an iterative manner, starting from the points closest to the origin and moving outwards.
            Selecting the next point is done either by selecting the point with the smallest distance from the origin (giving a circular distribution), or by prioritizing points in the
            same layer as the previous point, choosing the point closest to the 30 degree angle (giving an hexagonal distribution). If no points are available in the same layer, the next layer is considered.
            Choosing points by distance from the origin results in a more circular distribution of points, while choosing points by angle results in a hexagonal distribution of points.
            """

            if circular_filament_distribution:
                # The next point is the one with the smallest distance from the origin
                next_point = min(possible_next_points, key=point_relative_magnitude)

            else:
                # 1) Filter possible next points to include only points in the lowest not full layer.
                next_points_in_same_layer = possible_next_points[possible_next_points.sum(axis=1) == possible_next_points.sum(axis=1).min()]
                # 2) Choose the next point as the one with an angle closest to 30 degrees.
                next_point = min(next_points_in_same_layer, key=lambda v: np.abs(v[1] - v[0]))

            possible_next_points = np.delete(possible_next_points, np.where(np.all(possible_next_points == next_point, axis=1)), axis=0)  # Remove the selected point from possible_next_points
            points = np.append(points, np.array([next_point]), axis=0)  # Add the selected point to points
            points = sorted(points, key=lambda p: point_relative_magnitude(p))  # Sort the points by their distance from the origin

            new_possible_next_points = np.array([next_point + np.array([1, 0]), next_point + np.array([0, 1])])  # The possible next points from the current point
            possible_next_points = np.unique(np.concatenate((new_possible_next_points, possible_next_points)), axis=0)  # Add the new possible next points to the list of possible next points

            if len(points) == N_points_per_hexant:
                # Check if the outer-inner boundary ratio is satisfied.
                # The outermost points are always placed at the outer boundary, if the outer-inner boundary ratio is not satisfied, the innermost points must be within the inner boundary.
                # The innermost point is then removed and replaced by a point in the outermost layer.
                if point_relative_magnitude(points[-1]) / point_relative_magnitude(points[0]) <= outer_inner_boundary_ratio:
                    return points
                else:
                    # N_points_per_hexant += 1 # Removed: it increases the number of filaments.
                    points = np.delete(points, 0, axis=0)
                    return create_first_hexant_points(N_points_per_hexant, outer_inner_boundary_ratio, possible_next_points, points)

            else:
                return create_first_hexant_points(N_points_per_hexant, outer_inner_boundary_ratio, possible_next_points, points)

        outer_boundary_radius -= filament_radius * 1.1
        if inner_boundary_radius != 0:
            inner_boundary_radius += filament_radius * 1.1

        outer_inner_boundary_ratio = outer_boundary_radius / inner_boundary_radius if inner_boundary_radius != 0 else 1e10
        if N_points % 6 == 1 and inner_boundary_radius == 0:
            N_points -= 1
            points = [[[0, 0, 0]]]
        else:
            points = []

        if N_points != 0:
            groups_of_rotational_symmetry_first_points = create_first_hexant_points(N_points // 6, outer_inner_boundary_ratio)  # The first hexant of points, sorted by distance from the origin

            R = outer_boundary_radius / point_relative_magnitude(groups_of_rotational_symmetry_first_points[-1])  # Scaling factor to place points at the correct distance from the origin
            cart_to_hex_transformation = np.array([[R, R * np.cos(np.pi / 3)], [0, R * np.sin(np.pi / 3)]])  # Transformation matrix from cartesian to hexagonal coordinates

            # Rotate the points to create the other hexants of points
            for point in groups_of_rotational_symmetry_first_points:
                transformed_point = np.matmul(cart_to_hex_transformation, point)  # Transform the point from the cartesian coordinate system to the hexagonal coordinate system
                point_group = []
                rotation_angle = 0
                for hexagon_side in range(0, 6):
                    rotation_matrix = np.array([[np.cos(rotation_angle), -np.sin(rotation_angle)], [np.sin(rotation_angle), np.cos(rotation_angle)]])

                    rotated_point = np.matmul(rotation_matrix, transformed_point)
                    point_group.append(list(rotated_point) + [0])

                    rotation_angle += np.pi / 3
                points.append(point_group)
        return points

    def create_geometry(self, filament_radius: float, hexagonal_filaments: bool, N_filaments: int, matrix_inner_radius: float, matrix_middle_radius: float, matrix_outer_radius: float, circular_filament_distribution: bool = False, hole_radius: float = 0.0, hexagonal_holes: bool = False):
        """
        Creates the full geometry of the strand cross-section.

        This method generates the geometry by creating a grid of points that represent the center points of the filaments.
        It then creates the filaments at these points. The filaments can be either hexagonal or circular, depending on the `hexagonal_filaments` parameter.
        Finally, it creates the matrix that contains the filaments. The matrix is divided into an inner, middle, and outer area. The middle section contains the filaments, and the inner and outer areas are 'empty'.

        :param filament_radius: The radius of the filaments.
        :type filament_radius: float
        :param hexagonal_filaments: If True, the filaments are hexagonal. If False, the filaments are circular.
        :type hexagonal_filaments: bool
        :param N_filaments: The number of filaments to create.
        :type N_filaments: int
        :param matrix_inner_radius: The radius of the inner area of the matrix.
        :type matrix_inner_radius: float
        :param matrix_middle_radius: The radius of the middle area of the matrix. This is where the filaments are located.
        :type matrix_middle_radius: float
        :param matrix_outer_radius: The radius of the outer area of the matrix.
        :type matrix_outer_radius: float
        :param circular_filament_distribution: If True, the filaments are distributed in a circular pattern. If False, the filaments are distributed in a hexagonal pattern. Defaults to False.
        :type circular_filament_distribution: bool, optional
        :param hole_radius: The radius of the filaments holes.
        :type hole_radius: float, optional
        """
        # 1) Create the point-grid representing the center points of the filaments
        # 1.1) Get the point positions
        filament_centers = self.create_filament_center_points(N_filaments, filament_radius, matrix_middle_radius, matrix_inner_radius, circular_filament_distribution)
        # 1.2) Create the center points
        center_points = []
        for layer in filament_centers:
            layer_points = []
            for pos in layer:
                P = Point.create_or_get(pos)
                layer_points.append(P)
            center_points.append(layer_points)

        # 2) Create the filaments
        filaments = []
        holes = []
        for layer_n in range(len(center_points)):
            layer_filaments = []
            layer_holes = []
            for point_i in range(len(center_points[layer_n])):
                if hexagonal_filaments:
                    filament = Hexagon(center_points[layer_n][point_i], filament_radius, np.pi / 6)
                else:
                    filament = Disk(center_points[layer_n][point_i], filament_radius)
                if hole_radius:
                    if hexagonal_holes:
                        hole = Hexagon(center_points[layer_n][point_i], hole_radius, np.pi / 6)
                    else:
                        hole = Disk(center_points[layer_n][point_i], hole_radius)
                    layer_holes.append(hole)
                    filament.inner_boundary_curves = [hole.boundary_curves]
                layer_filaments.append(filament)
            filaments.append(layer_filaments)
            if hole_radius:
                holes.append(layer_holes)
        self.filaments = filaments
        if hole_radius:
            self.filament_holes = holes
        # 3) Create the matrix
        # The matrix will be divided into an inner-, middle- and outer area. The middle section contains the filaments and the inner and outer areas are 'empty'.
        # No inner section will be made if the matrix inner_radius is 0.
        if matrix_inner_radius != 0:
            inner_section = Disk([0, 0, 0], matrix_inner_radius)
            middle_section = Disk([0, 0, 0], matrix_middle_radius)  # Middle section
            middle_section.inner_boundary_curves.append(inner_section.boundary_curves)
            for layer in self.filaments:
                for filament in layer:
                    middle_section.inner_boundary_curves.append(filament.boundary_curves)
        else:
            middle_section = Disk([0, 0, 0], matrix_middle_radius)  # Middle section
            for layer in self.filaments:
                for filament in layer:
                    middle_section.inner_boundary_curves.append(filament.boundary_curves)

        outer_section = Disk([0, 0, 0], matrix_outer_radius)
        outer_section.inner_boundary_curves.append(middle_section.boundary_curves)

        self.matrix = [middle_section, outer_section] if matrix_inner_radius == 0 else [inner_section, middle_section, outer_section]

    def add_air(self, rad: str, coil_rad: str, type: str):
        # The air region is defined as the region from the matrix outer boundary to the radius 'rad'. The air radius must be greater than the matrix radius.
        def determine_strand_boundary_single_air_domain(matrix):
            """
            This function finds the combined outer boundary of the strand geometry, which is the inner boundary of the air region.
            The outer boundary of the strand geometry is is not necessarily the outer boundary of the matrix, as the outer matrix partition
            may not fully contain the full strand (as with a WIRE-IN-CHANNEL geometry).
            """
            strand_outer_boundary = set(matrix[0].boundary_curves)  # Start with the boundary of the inner matrix partition
            for i, matrix_partition in enumerate(matrix[:-1]):  # Loop over the matrix partitions
                next_matrix_partition = matrix[i + 1]

                inner_partition_boundary = set(matrix_partition.boundary_curves)
                next_partition_boundary = set(next_matrix_partition.boundary_curves)

                if inner_partition_boundary & next_partition_boundary:  # If the inner and outer partition boundaries share some curves
                    strand_outer_boundary = strand_outer_boundary ^ next_partition_boundary  # Get the combined boundary of the inner and outer partition boundaries
                else:
                    strand_outer_boundary = next_partition_boundary  # If the inner and outer partition boundaries do not share any curves, the outer boundary is simply the boundary of the outer partition.

            strand_outer_boundary = Curve.get_closed_loops(list(strand_outer_boundary))[0]  # Simply used to sort the curves in the outer boundary into a correct order which can be used to create a closed loop.
            return strand_outer_boundary

        if type == 'strand_only':  # circle w. natural boundary
            self.air.append(Disk([0, 0, 0], rad))
            air_inner_boundaries = determine_strand_boundary_single_air_domain(self.matrix)
            self.air[0].inner_boundary_curves.extend([air_inner_boundaries])
        elif type == 'coil':  # offset semicircle w. natural boundary
            self.air.append(Semicircle([0, 0, 0], coil_rad, rad))
            air_inner_boundaries = determine_strand_boundary_single_air_domain(self.matrix)
            self.air[0].inner_boundary_curves.extend([air_inner_boundaries])
        elif type == 'periodic_square':
            outer_matrix_curves = self.matrix[-1].boundary_curves  # use matrix boundaries to initialize segmented air sections
            self.air = [SquareSection([0, 0, 0], rad, outer_matrix_curves[0]),
                        SquareSection([0, 0, 0], rad, outer_matrix_curves[1]),
                        SquareSection([0, 0, 0], rad, outer_matrix_curves[2]),
                        SquareSection([0, 0, 0], rad, outer_matrix_curves[3])]
            self.air_composition = CompositeSquare(self.air)
            self.air_composition.inner_boundary_curves.extend([self.matrix[-1].boundary_curves])
        else:
            raise ValueError(
                f"FiQuS does not support type: {type} with coil radius: {coil_rad}!"
            )

    def update_tags(self):
        """
        When the geometry is loaded from a .brep file, the tags of entities with dimensions lower than the highest dimension are not preserved and may change unpredictably.
        This function updates the tags of the points, curves and surfaces in the geometry to ensure that they are consistent with the current gmsh model.
        """
        surfaces = sum(self.filaments, []) + sum(self.filament_holes, []) + self.matrix + self.air

        Surface.update_tags(surfaces)

    def create_gmsh_instance(self):
        """
            Creates the gmsh instances of the geometry.
        """
        surfaces = sum(self.filaments, []) + sum(self.filament_holes, []) + self.matrix + self.air

        Surface.set_correct_boundary_orientation(surfaces)

        for surface in surfaces:
            surface.create_gmsh_instance()

    def add_physical_groups(self):
        """
            Creates all physical groups.
        """
        # Filaments: Add physical boundary and surface
        for layer_n in range(len(self.filaments)):
            for filament_i in range(len(self.filaments[layer_n])):
                self.filaments[layer_n][filament_i].add_physical_boundary(f"Boundary: Filament {filament_i} in layer {layer_n}")
                self.filaments[layer_n][filament_i].add_physical_surface(f"Surface: Filament {filament_i} in layer {layer_n}")

                self.filaments[layer_n][filament_i].physicalEdgePointTag = gmsh.model.addPhysicalGroup(0, [self.filaments[layer_n][filament_i].boundary_curves[0].points[0].tag])

        # Add physical surface for the filament holes
        for layer_n in range(len(self.filament_holes)):
            for filament_i in range(len(self.filament_holes[layer_n])):
                self.filament_holes[layer_n][filament_i].add_physical_boundary(f"Boundary: Filament hole {filament_i} in layer {layer_n}")
                self.filament_holes[layer_n][filament_i].add_physical_surface(f"Surface: Filament hole {filament_i} in layer {layer_n}")

                self.filament_holes[layer_n][filament_i].physicalEdgePointTag = gmsh.model.addPhysicalGroup(0, [self.filament_holes[layer_n][filament_i].boundary_curves[0].points[0].tag])

        # Matrix: Add physical boundary and surface for each partition
        for i, matrix_partition in enumerate(self.matrix):
            matrix_partition.add_physical_boundary(f"Boundary: Matrix partition {i}")
            matrix_partition.add_physical_surface(f"Surface: Matrix partition {i}")

        # Air: Add physical boundary and surfaces
        for i, air_partition in enumerate(self.air):
            air_partition.add_physical_boundary(f"Boundary: Air partition {i}")
            air_partition.add_physical_surface(f"Surface: Air partition {i}")

        if self.air_composition:
            # Cut: Add physical cuts, boundaries and the composite surface
            self.air_composition.add_physical_boundaries(f"Boundary: Air")
            self.air_composition.add_physical_surface(f"Surface: Air")

            self.air_composition.add_physical_cuts(f"Cut: Air")

            self.air_composition.physical_inner_boundary_tags.append(gmsh.model.addPhysicalGroup(1, [curve.tag for curve in self.air_composition.inner_boundary_curves[0]], name=f"InnerBoundary: Air"))
            self.air_composition.physical_inner_boundary_names.append(f"InnerBoundary: Air")
            self.air_composition.strand_bnd_physicalEdgePointTag = gmsh.model.addPhysicalGroup(0, [self.air_composition.inner_boundary_curves[0][0].points[0].tag])
        else:
            # Add inner boundary
            self.air[0].physical_inner_boundary_tags.append(gmsh.model.addPhysicalGroup(1, [curve.tag for curve in self.air[0].inner_boundary_curves[0]], name=f"InnerBoundary: Air"))
            self.air[0].physical_inner_boundary_names.append(f"InnerBoundary: Air")
            self.air[0].strand_bnd_physicalEdgePointTag = gmsh.model.addPhysicalGroup(0, [self.air[0].inner_boundary_curves[0][0].points[0].tag])

        # TEST add a physical group CUT through whole domain
        # tag = Line.create_or_get(self.air[0].center_point, self.air[0].boundary_curves[0].P1)
        # self.domain_cut = gmsh.model.add_physical_group(1, [tag], name = "Domain cut")

    def save(self, save_file):
        # This function saves the geometry class to a pickle file.
        # The geometry class is used again during meshing.
        with open(save_file, "wb") as geom_save_file:
            pickle.dump(self, geom_save_file)
            print(f"Geometry saved to file {save_file}")

    def write_geom_to_yaml(self, file_path):
        # This function writes the geometry to a yaml file.
        # The yaml file contains the coordinates of the points, the type of the curves and the indices of the points that make up the curves and the indices of the curves that make up the areas.
        # Note: Only the strands are written to the yaml file. The air region is not included.
        Conductor = geom.Conductor()  # Create a data model for the conductor data

        # Add Materials to the 'Solution' section of the data model
        # 1) Find all unique materials used in the geometry
        # materials = set([surface.material for surface in Surface.surfaces_registry if surface.material is not None])
        # # Sort the materials into two groups by their type. All materials with the same type are grouped together.
        # material_groups = {material_type: [material for material in materials if material.type == material_type] for material_type in set([material.type for material in materials])}
        # # 2) Add all unique materials to the data model, represented by a string with the material type and index in the material group
        # for material_type, material_group in material_groups.items():
        #     for i, material in enumerate(material_group):
        #         material_name = f"{material_type}_{i}"
        #         Conductor.Solution.Materials[material_name] = material

        surfaces = list(set(sum(self.filaments, []) + self.matrix))  # Combine all the filaments and the matrix to get all the surfaces which should be written. The air region is not included.
        curves = list(set(sum([surface.boundary_curves for surface in surfaces], [])))  # Extract all the boundary curves from the surfaces
        points = list(set(sum([curve.points for curve in curves], [])))  # Extract all the points from the curves

        # Populate the points dictionary with coordinates of each point
        # for p, point in enumerate(points):
        #     Conductor.Geometry.Points[p] = geom.Point(Coordinates=point.pos.tolist()) #{"Coordinates": point.pos.tolist()}
        for p, point in enumerate(Point.points_registry):
            if point in points:
                Conductor.Geometry.Points[p] = geom.Point(Coordinates=point.pos.tolist())

        # Populate the curves dictionary with type of each curve and indices of its points
        # for c, curve in enumerate(curves):
        #     curve_points = [Point.points_registry.index(point) for point in curve.points]
        #     Conductor.Geometry.Curves[c] = geom.Curve(
        #         Type=curve.__class__.__name__,
        #         Points=curve_points
        #     )
        for c, curve in enumerate(Curve.curves_registry):
            if curve in curves:
                curve_points = [Point.points_registry.index(point) for point in curve.points]
                Conductor.Geometry.Curves[c] = geom.Curve(
                    Type=curve.__class__.__name__,
                    Points=curve_points
                )

        # Populate the surfaces dictionary with material, boundary curves and inner boundary curves of each surface
        for a, surface in enumerate(Surface.surfaces_registry):
            if surface in surfaces:
                surface_boundary_curves = [Curve.curves_registry.index(curve) for curve in surface.boundary_curves]
                surface_inner_boundary_curves = [[Curve.curves_registry.index(curve) for curve in inner_boundary] for inner_boundary in surface.inner_boundary_curves]

                if surface in self.matrix:  # Add dummy values for writing the matrix surfaces to the data model
                    surface.layer = None
                    surface.layer_index = None

                elif surface in sum(self.filaments, []):  # Add dummy values for writing the filament surfaces to the data model
                    for l, layer in enumerate(self.filaments):
                        if surface in layer:
                            surface.layer = l
                            surface.layer_index = layer.index(surface)
                            break

                # Name the material based on its type and index in the material groups
                # if surface.material is None:
                #     material_name = None
                # else:
                #     material_type = surface.material.Type
                #     material_index = material_groups[material_type].index(surface.material)
                #     material_name = f"{material_type}_{material_index}"
                material_name = surface.material

                Conductor.Geometry.Areas[a] = geom.Area(
                    Material=material_name,
                    Boundary=surface_boundary_curves,
                    InnerBoundaries=surface_inner_boundary_curves,
                    Layer=surface.layer,
                    LayerIndex=surface.layer_index
                )

        # Write the data model to a yaml file
        UFF.write_data_to_yaml(file_path, Conductor.model_dump())

    @classmethod
    def read_geom_from_yaml(cls, file_path):
        """
            This function loads a geometry from a yaml file and returns a TwistedStrand object.
            The yaml file contains all points, curves and surfaces which define the geometry.
            - Points are defined by their position vector and can be referenced by an integer ID.
                : Position [x, y, z]
            - Curves are defined by their type (e.g. Line, CircleArc, etc.) and the ID of the points that make up the curves. Curves are referenced by an integer ID as well.
                : Type ('Line', 'CircleArc', etc.)
                : Points ([1,2,3]), list of point-ID defining the curve.
            - Surfaces are defined by material, outer boundary, inner boundaries and layer and layer-index if the surface is a strand.
                : Material ('Cu', 'NbTi', 'Nb3Sn', etc.)
                : Outer boundary ([2,3,4,5...]), list of curve-ID defining the outer boundary closed loop.
                : Inner boundaries ([[1,2,3], [4,5,6], ... ]), list of list of curve-IDs defining closed loops.
                : Layer (0, 1, 2, ...), the layer of a filament. None if the surface is part of the matrix.
                : LayerIndex (0, 1, 2, ...), the index of the filament in the layer. None if the surface is part of the matrix.

            :param file_path: The full path to the yaml file.
            :type file_path: str
            :param gmsh_curve_convention: If True, the curves are created using the gmsh convention for defining curves. Determines the order of the points in the curves. Defaults to False. This is a temporary solution. In the future, the order of the points in the curves will be updated to fit the gmsh convention.

        """
        Conductor = UFF.read_data_from_yaml(file_path, geom.Conductor)

        # 1) Create the points
        for point in Conductor.Geometry.Points.values():
            Point.create_or_get(point.Coordinates)

        # 2) Create the curves
        for curve in Conductor.Geometry.Curves.values():
            curve_type = curve.Type
            points = [Point.points_registry[p] for p in curve.Points]

            c = globals()[curve_type].create_or_get(*points)  # Create the curve of the specified type

            # TODO: To be added.
            # c.contact = curve.Contact
            # c.thickness = curve.Thickness
            # c.material = curve.Material

        # 3) Create the surfaces
        # TODO: area.boundary_material and boundary_thickness are not yet used.
        strand = cls()
        layers = max([area.Layer for area in Conductor.Geometry.Areas.values() if area.Layer is not None]) + 1  # The number of layers in the strand
        strand.filaments = [[None for i in range(6)] for j in range(layers)]  # Initialize the filaments list
        strand.filament_holes = [[None for i in range(6)] for j in range(layers)]  # Initialize the filament holes list

        for area_index, area_dm in Conductor.Geometry.Areas.items():
            boundary_curves = [Curve.curves_registry[c] for c in area_dm.Boundary]
            inner_boundary_curves = [[Curve.curves_registry[c] for c in inner_boundary] for inner_boundary in area_dm.InnerBoundaries]
            surface = Surface(boundary_curves, inner_boundary_curves)
            if area_dm.Material:  # If the material is provided
                surface.material = area_dm.Material

            if area_dm.Layer is None:
                # It is either a matrix partition or it is a hole in a filament.
                # We check if it is a hole in a filament by checking if the area outer boundary is in the inner boundary of a filament.
                is_hole = False
                for other_area in Conductor.Geometry.Areas.values():  # Loop over all areas to check if the area is a hole in a filament
                    if other_area.Layer is not None:  # If the other area is a filament
                        if area_dm.Boundary in other_area.InnerBoundaries:  # If the area is a hole in the other filament
                            # boundary_curves[0].P1, boundary_curves[0].P2 = boundary_curves[0].P2, boundary_curves[0].P1 # Reverse the order of the boundary curve points to get the correct orientation
                            layer = other_area.Layer
                            layer_index = other_area.LayerIndex
                            strand.filament_holes[layer][layer_index] = surface
                            is_hole = True
                            break

                if not is_hole:  # If it is not a hole, it is a matrix partition
                    strand.matrix.append(surface)

            else:
                strand.filaments[area_dm.Layer][area_dm.LayerIndex] = surface

        # Remove None values from the filaments list
        strand.filaments = [[filament for filament in layer if filament is not None] for layer in strand.filaments]
        strand.filament_holes = [[hole for hole in layer if hole is not None] for layer in strand.filament_holes]

        # Sort the matrix partitions from inner to outer based on the outermost point of the boundary curves of the partitions
        strand.matrix = sorted(strand.matrix, key=lambda surface: max([max([np.linalg.norm(point.pos) for point in curve.points]) for curve in surface.boundary_curves]))

        return strand


class Geometry:
    """
    Class to generate the ConductorAC Strand geometry.

    This class is responsible for generating the geometry of the twisted strand.
    It can either load a geometry from a YAML file or create the model from scratch.
    The geometry is saved to a .brep file and the geometry class is saved as a pickle file. If specified, the geometry representation can also be saved to a YAML file.

    :ivar fdm: The fiqus inputs data model.
    :vartype fdm: object
    :ivar cacdm: The magnet section of the fiqus inputs data model.
    :vartype cacdm: object
    :ivar inputs_folder: The full path to the folder with input files, i.e., conductor and STEP files.
    :vartype inputs_folder: str
    :ivar geom_folder: The full path to the current working directory.
    :vartype geom_folder: str
    :ivar magnet_name: The name of the magnet.
    :vartype magnet_name: str
    :ivar geom_file: The full path to the .brep file where the geometry will be saved.
    :vartype geom_file: str
    :ivar verbose: If True, more information is printed in the Python console.
    :vartype verbose: bool
    :ivar gu: An instance of the GmshUtils class.
    :vartype gu: object
    """

    def __init__(self, fdm, inputs_folder_path, verbose=True):
        """
        Initializes the Geometry class.

        :param fdm: The fiqus data model.
        :type fdm: object
        :param inputs_folder_path: The full path to the folder with input files, i.e., conductor and STEP files.
        :type inputs_folder_path: str
        :param verbose: If True, more information is printed in the Python console. Defaults to True.
        :type verbose: bool, optional
        """
        self.fdm = fdm
        self.cacdm = fdm.magnet
        self.inputs_folder = inputs_folder_path
        self.geom_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name
        self.geom_file = os.path.join(self.geom_folder, f'{self.magnet_name}.brep')
        self.verbose = verbose
        self.gu = GmshUtils(self.geom_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

        # To see the surfaces in a better way in GUI:
        gmsh.option.setNumber("Geometry.SurfaceType", 2)

    def generate_strand_geometry(self, gui=False):
        """
        Generates the geometry of a strand based on the settings specified in the input data model.
        The geometry can either be loaded from a YAML file or created from scratch. After creation, the geometry
        can be saved to a YAML file. The method also creates gmsh instances, adds physical groups to the geometry,
        writes the geometry to a .brep file, and saves the geometry-class to a pickle file. If `gui` is True, it
        launches an interactive GUI.

        :param gui: If True, launches an interactive GUI after generating the geometry. Default is False.
        :type gui: bool, optional

        :return: None
        """
        print("Generating geometry")
        # 0) Clear the registries. Used when generating reference files for tests.
        if Point.points_registry:  # If the points registry is not empty, clear it.
            Point.points_registry.clear()
        if Curve.curves_registry:  # If the curves registry is not empty, clear it.
            Curve.curves_registry.clear()
        if Surface.surfaces_registry:  # If the surfaces registry is not empty, clear it.
            Surface.surfaces_registry.clear()
        if Surface.curve_loop_registry:  # If the curve loop registry is not empty, clear it.
            Surface.curve_loop_registry.clear()

        # 1) Either load the geometry from a yaml file or create the model from scratch
        if self.cacdm.geometry.io_settings.load.load_from_yaml:
            CAC = TwistedStrand.read_geom_from_yaml(os.path.join(self.inputs_folder, self.cacdm.geometry.io_settings.load.filename))
        else:
            CAC = TwistedStrand()
            strand = self.fdm.conductors[self.cacdm.solve.conductor_name].strand
            if strand.filament_hole_diameter:
                filament_hole_radius = strand.filament_hole_diameter / 2
                if strand.filament_hole_diameter >= strand.filament_diameter:
                    raise ValueError(
                        f"Invalid strand geometry: filament_hole_diameter ({strand.filament_hole_diameter}) "
                        f"must be smaller than filament_diameter ({strand.filament_diameter})."
                    )
            else:
                filament_hole_radius = 0.0
            CAC.create_geometry(
                strand.filament_diameter / 2,
                self.cacdm.geometry.hexagonal_filaments,
                strand.number_of_filaments,
                strand.diameter_core / 2,
                strand.diameter_filamentary / 2,
                strand.diameter / 2,
                self.cacdm.geometry.filament_circular_distribution,
                filament_hole_radius,
                self.cacdm.geometry.hexagonal_holes
            )

        CAC.add_air(self.cacdm.geometry.air_radius, self.cacdm.geometry.coil_radius, self.cacdm.geometry.type)
        CAC.create_gmsh_instance()
        # 2) Save the geometry to a yaml file if specified
        if self.cacdm.geometry.io_settings.save.save_to_yaml:
            filename = self.cacdm.geometry.io_settings.save.filename
            CAC.write_geom_to_yaml(os.path.join(self.geom_folder, filename))

        if self.cacdm.geometry.rotate_angle:
            dimTags = gmsh.model.occ.getEntities(dim=-1)
            gmsh.model.occ.rotate(dimTags, 0.0, 0.0, 0.0, 0, 0, 1, self.cacdm.geometry.rotate_angle * np.pi / 180)

        gmsh.model.occ.synchronize()

        # Add physical groups to the geometry
        CAC.add_physical_groups()

        print("Writing geometry")
        gmsh.write(self.geom_file)  # Write the geometry to a .brep file
        CAC.save(os.path.join(self.geom_folder, f'{self.magnet_name}.pkl'))  # Save the geometry-class to a pickle file

        if gui:
            self.gu.launch_interactive_GUI()
        else:
            if gmsh.isInitialized():
                gmsh.clear()
                gmsh.finalize()

    def load_conductor_geometry(self, gui=False):
        """
        Loads geometry from .brep file.
        """

        print("Loading geometry")

        gmsh.clear()
        gmsh.model.occ.importShapes(self.geom_file, format="brep")
        gmsh.model.occ.synchronize()

        if gui:
            self.gu.launch_interactive_GUI()






