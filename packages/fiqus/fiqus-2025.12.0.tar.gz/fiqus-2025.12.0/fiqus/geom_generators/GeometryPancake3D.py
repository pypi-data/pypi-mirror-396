import math
import logging
from enum import Enum
from inspect import currentframe, getframeinfo
from typing import List, Tuple, Dict
import operator

import os
import json
import timeit
import numpy as np
import gmsh

from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import FilesAndFolders
from fiqus.mains.MainPancake3D import Base
from fiqus.data.DataFiQuSPancake3D import Pancake3DGeometry

logger = logging.getLogger(__name__)

# coordinateList = []

def findSurfacesWithNormalsOnXYPlane(dimTags):
    result = []
    for dimTag in dimTags:
        surfaceNormal = gmsh.model.getNormal(dimTag[1], [0.5, 0.5])
        if abs(surfaceNormal[2]) < 1e-6:
            result.append(dimTag)

    return result


def findOuterOnes(dimTags, findInnerOnes=False):
    """
    Finds the outermost surface/curve/point in a list of dimTags. The outermost means
    the furthest from the origin.
    """
    dim = dimTags[0][0]
    if dim == 2:
        distances = []
        for dimTag in dimTags:
            _, curves = gmsh.model.occ.getCurveLoops(dimTag[1])
            for curve in curves:
                curve = list(curve)
                pointTags = gmsh.model.getBoundary(
                    [(1, curveTag) for curveTag in curve],
                    oriented=False,
                    combined=False,
                )
                # Get the positions of the points:
                points = []
                for dimTag in pointTags:
                    boundingbox1 = gmsh.model.occ.getBoundingBox(0, dimTag[1])[:3]
                    boundingbox2 = gmsh.model.occ.getBoundingBox(0, dimTag[1])[3:]
                    boundingbox = list(map(operator.add, boundingbox1, boundingbox2))
                    points.append(list(map(operator.truediv, boundingbox, (2, 2, 2))))

                distances.append(
                    max([point[0] ** 2 + point[1] ** 2 for point in points])
                )
    elif dim == 1:
        distances = []
        for dimTag in dimTags:
            pointTags = gmsh.model.getBoundary(
                [dimTag],
                oriented=False,
                combined=False,
            )
            # Get the positions of the points:
            points = []
            for dimTag in pointTags:
                boundingbox1 = gmsh.model.occ.getBoundingBox(0, dimTag[1])[:3]
                boundingbox2 = gmsh.model.occ.getBoundingBox(0, dimTag[1])[3:]
                boundingbox = list(map(operator.add, boundingbox1, boundingbox2))
                points.append(list(map(operator.truediv, boundingbox, (2, 2, 2))))

            distances.append(max([point[0] ** 2 + point[1] ** 2 for point in points]))

    if findInnerOnes:
        goalDistance = min(distances)
    else:
        goalDistance = max(distances)

    result = []
    for distance, dimTag in zip(distances, dimTags):
        # Return all the dimTags with the hoal distance:
        if math.isclose(distance, goalDistance, abs_tol=1e-6):
            result.append(dimTag)

    return result


class dimTags:
    """
    This is a class for (dim, tag) tuple lists. DimTags are heavily used in GMSH, and
    dimTags class makes it easier to store and manipulate them.

    Every dimTags instance with the save option True will be stored in the
    dimTagsStorage class. dimTags instances with the save option False will not be
    stored. dimTagsStorage class stores all the dimTags with the corresponding names so
    that later the dimTagsStorage class can be used to create the volume information
    file. The volume information file is required in the meshing stage to create the
    appropriate regions.

    If parentName is specified, during the volume information file generation, another
    key that is equal to parentName is created, and all the dimTags are also added
    there. For example, air consists of many parts such as gap, outer tube, inner
    cylinder parts, and their dimTags object all have the parentName of self.geo.air.name
    (user input of the air name) so that in the volume information file, they are all
    combined under the air name as well.

    :param name: name of the dimTags object (default: None)
    :type name: str, optional
    :param parentName: name of the parent dimTags object (default: None)
    :type parentName: str, optional
    :param save: True if the instance to be stored in dimTagsStorage class, False
        otherwise (default: False)
    :type save: bool, optional
    """

    point = 0
    curve = 1
    surface = 2
    volume = 3

    def storageUpdateRequired(func):
        """
        A decorator for dimTags class. It will update the dimTagsStorage class if the
        save option is True and the decorated function is called. Use this decorator
        for every function that changes the dimTags instance so that the storage gets
        updated.

        :param func: function to be decorated
        :type func: function
        :return: decorated function
        :rtype: function
        """

        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)

            if self.save:
                # Update the dimTagsStorage:
                dimTagsStorage.updateDimTags(self)

        return wrapper

    def __init__(
        self,
        name: str = None,
        parentName: str = None,
        save: bool = False,
    ):
        self.name = name

        dimTagsObjects = dimTagsStorage.getDimTagsObject(name)
        if dimTagsObjects != []:
            dimTagsObject = dimTagsObjects[0]
            self.physicalTag = dimTagsObject.physicalTag
            # To store points, curves, surfaces, and volumes separately:
            self.dimTags = dimTagsObject.dimTags
            self.dimTagsForPG = dimTagsObject.dimTagsForPG
            self.allDimTags = dimTagsObject.allDimTags
            self.parentName = dimTagsObject.parentName
            self.save = dimTagsObject.save
        else:
            self.physicalTag = None
            # To store points, curves, surfaces, and volumes separately:
            self.dimTags = [[] for _ in range(4)]
            self.dimTagsForPG = [[] for _ in range(4)]  # dim tags for physical groups
            self.allDimTags = []
            self.parentName = parentName
            self.save = save
            if self.save:
                dimTagsStorage.updateDimTags(self)

    @storageUpdateRequired
    def add(
        self,
        dimTagsList: List[Tuple[int, int]],
        dimTagsListForPG: List[Tuple[int, int]] = None,
    ):
        """
        Adds a list of (dim, tag) tuples to the dimTags object.

        dimTagsListForPG is also accepted as an argument because sometimes, the stored
        dimTags and the current dimTags in the geometry generation can be different. For
        example, if volume 61 is deleted, the other volume tags (62, 63, ...) won't
        shift back. However, after saving the geometry as a BREP file and rereading it,
        the volume tags will be shifted back. In this case, the stored dimTags should be
        shifted as well. But to create the correct physical region in the
        geometry-creating process (which won't be saved in the BREP file, just used for
        debugging purposes), another optional dimTagsListForPG argument is accepted.

        :param dimTagsList: list of (dim, tag) tuples
        :type dimTagsList: list[tuple[int, int]]
        :param dimTagsListForPG: list of (dim, tag) tuples for physical groups
            (default: None). If dimTagsListForPG is None, dimTagsList will be used for
            physical groups as well.
        :type dimTagsListForPG: list[tuple[int, int]], optional

        """
        if not isinstance(dimTagsList, list):
            dimTagsList = [dimTagsList]

        if not all(isinstance(element, tuple) for element in dimTagsList):
            raise TypeError("Dim tags must be a list of tuples!")

        # Sometimes, negative entities can be added for topology.
        for i, v in enumerate(dimTagsList):
            if v[1] < 0:
                dimTagsList[i] = (v[0], -v[1])

        # Add dim tags if they are not already added:
        for v in dimTagsList:
            if v not in self.allDimTags:
                self.dimTags[v[0]].append(v)
                if dimTagsListForPG is None:
                    self.dimTagsForPG[v[0]].append(v)
                self.allDimTags.append(v)

        if dimTagsListForPG is not None:
            if not isinstance(dimTagsListForPG, list):
                dimTagsListForPG = [dimTagsListForPG]

            if not all(isinstance(element, tuple) for element in dimTagsListForPG):
                raise TypeError("Dim tags must be a list of tuples!")

            for i, v in enumerate(dimTagsListForPG):
                if v[1] < 0:
                    dimTagsListForPG[i] = (v[0], -v[1])
            for v in dimTagsListForPG:
                if v not in self.dimTagsForPG:
                    self.dimTagsForPG[v[0]].append(v)

    def addWithTags(self, dim: int, tags: List[int], tagsForPG: List[int] = None):
        """
        Adds a list of tags with a specific dimension to the dimTags object. The
        explanation of the tagsForPG argument is given in the add() method.

        :param dim: dimension of the tags
        :type dim: int
        :param tags: list of tags
        :type tags: list[tuple[int, int]]
        :param tagsForPG: list of tags for physical groups (default: None)
        :type tagsForPG: list[tuple[int, int]], optional

        """
        if not isinstance(tags, list):
            tags = [tags]

        if not isinstance(dim, int):
            raise TypeError("Dimension must be an integer!")

        if not all(isinstance(element, int) for element in tags):
            raise TypeError("Tags must be a list of integers!")

        dims = [dim] * len(tags)
        dimTagsList = list(zip(dims, tags))

        if tagsForPG is not None:
            if not isinstance(tagsForPG, list):
                tagsForPG = [tagsForPG]

            if not all(isinstance(element, int) for element in tagsForPG):
                raise TypeError("Tags must be a list of integers!")

            dimTagsListForPG = list(zip(dims, tagsForPG))
            self.add(dimTagsList, dimTagsListForPG)
        else:
            self.add(dimTagsList)

    def getDimTags(self, dim: int = None) -> List[Tuple[int, int]]:
        """
        Returns the stored list of (dim, tag) tuples with a specific dimension. If dim
        is not specified, returns all the (dim, tag) tuples.

        :param dim: dimension of the tags to be returned (default: None)
        :type dim: int, optional
        :return: list of (dim, tag) tuples
        :rtype: list[tuple[int, int]]
        """
        if dim is None:
            return self.dimTags[0] + self.dimTags[1] + self.dimTags[2] + self.dimTags[3]
        else:
            return self.dimTags[dim]

    def getDimTagsForPG(self, dim: int = None) -> List[Tuple[int, int]]:
        """
        Returns the stored list of (dim, tag) tuples for physical groups with a specific
        dimension. If dim is not specified, returns all the (dim, tag) tuples for
        physical groups.

        :param dim: dimension of the tags to be returned (default: None)
        :type dim: int, optional
        :return: list of (dim, tag) tuples for physical groups
        :rtype: list[tuple[int, int]]
        """
        if dim is None:
            return (
                self.dimTagsForPG[0]
                + self.dimTagsForPG[1]
                + self.dimTagsForPG[2]
                + self.dimTagsForPG[3]
            )
        else:
            return self.dimTagsForPG[dim]

    def getTags(self, dim: int, forPhysicalGroup=False) -> List[int]:
        """
        Returns the stored list of tags with a specific dimension.

        :param dim: dimension of the tags to be returned
        :type dim: int
        :return: list of tags
        :rtype: list[int]
        """
        if forPhysicalGroup:
            return [v[1] for v in self.dimTagsForPG[dim]]
        else:
            return [v[1] for v in self.dimTags[dim]]

    def getExtrusionTop(self, dim=3):
        """
        Returns the top surfaces, lines, or points of an extrusion operation if the
        dimTags object contains the tags of an extrusion operation.
        gmsh.model.occ.extrusion() function returns all the entities that are created
        by the extrusion as a dim tags list. The first element is always the top
        surface, the second is the volume. However, when more than one surface is
        extruded, extracting the top surfaces is not trivial. This function returns
        the top surfaces of an extrusion operation. It does that by finding the entities
        right before the volume entities. If dim is 2, the function will return the top
        curves of an extrusion operation. If dim is 1, the function will return the top
        points of an extrusion.

        :param dim: dimension of the entity that is being created (default: 3)
        :type dim: int, optional
        :return: list of (dim, tag) tuples of the top entities of an extrusion operation
        :rtype: list[tuple[int, int]]
        """

        topSurfaces = []
        for index, dimTag in enumerate(self.allDimTags):
            if dimTag[0] == dim:
                topSurfaces.append(self.allDimTags[index - 1])

        return topSurfaces

    def getExtrusionSide(self, dim=3):
        """
        Returns the side surfaces, lines, or points of an extrusion operation if the
        dimTags object contains the tags of an extrusion operation.
        gmsh.model.occ.extrusion() function returns all the entities that are created
        by the extrusion as a dim tags list. The first element is always the top
        surface, the second is the volume. The other elements are the side surfaces.
        However, when more than one surface is extruded, extracting the side surfaces
        is not trivial. This function returns the side surfaces of an extrusion
        operation. It does that by finding returning all the entities except the top
        surface and the volume. If dim is 2, the function will return the side curves of
        an extrusion operation.

        :param dim: dimension of the entity that is being created (default: 3)
        :type dim: int, optional
        :return: list of (dim, tag) tuples of the side entities of an extrusion operation
        :rtype: list[tuple[int, int]]
        """
        sideSurfaces = []
        sideSurfaceStartIndex = None
        for index, dimTag in enumerate(self.allDimTags):
            if dimTag[0] == dim:
                if sideSurfaceStartIndex is not None:
                    sideSurfaces.append(
                        self.allDimTags[sideSurfaceStartIndex : index - 1]
                    )
                    sideSurfaceStartIndex = index + 1
                else:
                    sideSurfaceStartIndex = index + 1

        sideSurfaces.append(self.allDimTags[sideSurfaceStartIndex:])

        return sideSurfaces

    def __add__(self, other):
        """
        Adds two dimTags objects and returns a new dimTags object with the same save and
        name attirbues of the first dimTags object.

        It might cause bugs because of the recursive behavior of the
        @storageUpdateRequired decorator. Use with caution. Currently only used by
        dimTagsStorage.updateDimTags method.

        :param other: dimTags object to be added
        :type other: dimTags
        :return: dimTags object with the sum of the two dimTags objects
        :rtype: dimTags
        """
        result = dimTags()
        result.name = self.name
        result.parentName = self.parentName
        result.physicalTag = self.physicalTag
        result.dimTags = self.dimTags
        result.dimTagsForPG = self.dimTagsForPG
        result.allDimTags = self.allDimTags

        result.add(other.allDimTags)
        result.save = self.save
        return result

    def __repr__(self):
        """
        Returns the string representation of the dimTags object. If the dimTags object
        is saved, it will return "SAVED: name". If the dimTags object is not saved, it
        will return "NOT SAVED: name".

        dimTags objects are used as dictionary keys throughout the code. This
        representation makes debugging easier.

        :return: string representation of the dimTags object
        :rtype: str
        """
        if self.save:
            return "SAVED: " + self.name
        else:
            return "NOT SAVED: " + self.name


class dimTagsStorage:
    """
    This is a global class to store the dimTags of important entities in the model.
    Every dimTags instance with self.save = True will be stored in this class. Later,
    the storage will be used to generate the volume information (*.vi) file. *.vi file
    will be used for generating the physical regions in the meshing part.

    Users should not use this class directly. Instead, they should use the dimTags
    class. If they assign save = True to the dimTags instance, it will be stored in this
    class.

    This class is a singleton class. It means that there will be only one instance of
    this class in the whole module. This is done to be able to use the same storage
    throughout this module. See the singleton design pattern for more information.
    """

    __instance = None
    __dimTagsDict = {}  # Dictionary with the names of the dimTags objects as keys and
    # dimTags objects as values

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def updateDimTags(cls, dimTagsObject: dimTags):
        """
        Either adds or updates the dimTags object in the storage.

        :param dimTags: dimTags object to be added or updated.
        :type dimTags: dimTags

        """
        if dimTagsObject.name in cls.__dimTagsDict:
            newDimTags = dimTagsObject + cls.__dimTagsDict[dimTagsObject.name]
            cls.__dimTagsDict[dimTagsObject.name] = newDimTags
        else:
            cls.__dimTagsDict[dimTagsObject.name] = dimTagsObject

    # @classmethod
    # def updateDimTagsFromDict(cls, name: str, dimTagsList: List[Tuple[int, int]]):
    #     """
    #     Updates or adds dimTags from a list of (dim, tag) tuples.
    #
    #     :param name: Name of the dimTags entry to update or add.
    #     :type name: str
    #     :param dimTagsList: List of (dim, tag) tuples to be associated with the name.
    #     :type dimTagsList: List[Tuple[int, int]]
    #     """
    #     # Check if the entry exists; if so, update it, otherwise add a new entry
    #     if name in cls.__dimTagsDict:
    #         existingDimTags = cls.__dimTagsDict[
    #             name].dimTags  # Assuming dimTags object has a dimTags attribute storing the list of tuples
    #         updatedDimTags = existingDimTags + dimTagsList
    #         cls.__dimTagsDict[name].dimTags = updatedDimTags  # Update the list of tuples
    #     else:
    #         # Create a new dimTags object (this step depends on how your dimTags class is structured)
    #         newDimTagsObject = dimTags(name=name, dimTags=dimTagsList)  # Assuming such a constructor exists
    #         cls.__dimTagsDict[name] = newDimTagsObject

    @classmethod
    def getDimTagsObject(cls, names: List[str]):
        """
        Returns the dimTags object with the given names.

        :param names: names of the dimTags objects.
        :type names: list[str]
        :return: dimTags objects with the given name.
        :rtype: list[dimTags]
        """
        if not isinstance(names, list):
            names = [names]

        dimTagsObjects = []
        for name in names:
            if name in cls.__dimTagsDict:
                dimTagsObjects.append(cls.__dimTagsDict[name])

        return dimTagsObjects

    @classmethod
    def getDimTags(cls, names: List[str], dim: int = None) -> List[Tuple[int, int]]:
        """
        Returns the stored list of (dim, tag) tuples with dimension a specific dimenions
        and names. If dim is not specified, all the stored (dim, tag) tuples under the
        given names will be returned.

        :param names: names of the dimTags object that will be returned
        :type names: list[str]
        :param dim: dimension of the (dim, tag) tuples to be returned (default: None).
            If dim is None, all the stored (dim, tag) tuples under the name names will
            be returned.
        :type dim: int, optional
        :return: list of (dim, tag) tuples
        """
        if not isinstance(names, list):
            names = [names]

        dimTagsResult = []
        for name in names:
            dimTagsResult.extend(cls.__dimTagsDict[name].getDimTags(dim))

        return dimTagsResult

    @classmethod
    def getTags(cls, names: List[str], dim: int) -> List[int]:
        """
        Returns the stored list of tags with dimension a specific dimension and names.

        :param names: names of the dimTags objects
        :type names: list[str]
        :param dim: dimension of the tags to be returned
        :type dim: int
        :return: list of tags
        :rtype: list[int]
        """
        dimTags = cls.getDimTags(names, dim)
        tags = [dimTag[1] for dimTag in dimTags]

        return tags

    @classmethod
    def getDimTagsDict(
        cls, forPhysicalGroups=False
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Returns a dictionary with the names of the dimTags objects as keys and the
        stored list of (dim, tag) tuples as values. This method is used to generate the
        .vi file. If forPhysicalGroups is True, the dimTags for physical groups will be
        returned instead of the dimTags.

        :param forPhysicalGroups: True if the dimTags for physical groups should be
            returned, False otherwise (default: False)
        :type forPhysicalGroups: bool, optional
        :return: dictionary with the names of the dimTags objects as keys and the
            stored list of (dim, tag) tuples as values
        :rtype: dict[str, list[tuple[int, int]]]
        """
        dictionary = {}
        for name, dimTagsObject in cls.__dimTagsDict.items():
            if dimTagsObject.parentName is not None:
                if dimTagsObject.parentName in dictionary:
                    if forPhysicalGroups:
                        dictionary[dimTagsObject.parentName].extend(
                            dimTagsObject.getDimTagsForPG()
                        )
                    else:
                        dictionary[dimTagsObject.parentName].extend(
                            dimTagsObject.getDimTags()
                        )
                else:
                    if forPhysicalGroups:
                        dictionary[dimTagsObject.parentName] = (
                            dimTagsObject.getDimTagsForPG()
                        )
                    else:
                        dictionary[dimTagsObject.parentName] = (
                            dimTagsObject.getDimTags()
                        )
            if forPhysicalGroups:
                dictionary[name] = dimTagsObject.getDimTagsForPG()
            else:
                dictionary[name] = dimTagsObject.getDimTags()

        return dictionary

    @classmethod
    def getAllStoredDimTags(cls) -> List[Tuple[int, int]]:
        """
        Returns a list of all the stored (dim, tag) tuples, regardless of the name of
        the dimTags object (i.e. all the dimTags objects are merged into one list).

        :return: list of all the stored (dim, tag) tuples.
        :rtype: list[tuple[int, int]]
        """
        AllStoredDimTags = []
        for name, dimTagsObject in cls.__dimTagsDict.items():
            AllStoredDimTags.extend(dimTagsObject.getDimTags())

        return AllStoredDimTags

    @classmethod
    def clear(cls):
        """
        Clears the dimTagsStorage class.


        """
        cls.__instance = None
        cls.__dimTagsDict = (
            {}
        )  # Dictionary with the names of the dimTags objects as keys and
        # dimTags objects as values


class coordinate(Enum):
    """
    A class to specify coordinate types easily.
    """

    rectangular = 0
    cylindrical = 1
    spherical = 2


class direction(Enum):
    """
    A class to specify direction easily.
    """

    ccw = 0
    cw = 1


class point:
    """
    This is a class for creating points in GMSH. It supports rectangular and cylindrical
    coordinates. Moreover, vector operations are supported.

    :param r0: x, r, or r (default: 0.0)
    :type r0: float, optional
    :param r1: y, theta, or theta (default: 0.0)
    :type r1: float, optional
    :param r2: z, z, or phi (default: 0.0)
    :type r2: float, optional
    :param type: coordinate type (default: coordinate.rectangular)
    :type type: coordinate, optional
    """

    def __init__(self, r0=0.0, r1=0.0, r2=0.0, type=coordinate.rectangular) -> None:

        self.type = type  # Store 'type' as an instance attribute

        if type is coordinate.rectangular:
            self.x = r0
            self.y = r1
            self.z = r2

            self.r = math.sqrt(self.x**2 + self.y**2)
            self.theta = math.atan2(self.y, self.x)
        elif type is coordinate.cylindrical:
            self.r = r0
            self.theta = r1
            self.x = self.r * math.cos(self.theta)
            self.y = self.r * math.sin(self.theta)
            self.z = r2
        elif type is coordinate.spherical:
            raise ValueError("Spherical coordinates are not supported yet!")
        else:
            raise ValueError("Improper coordinate type value!")

        self.tag = gmsh.model.occ.addPoint(self.x, self.y, self.z)

    def __repr__(self):
        """
        Returns the string representation of the point.

        :return: string representation of the point
        :rtype: str
        """
        return "point(%r, %r, %r, %r)" % (self.x, self.y, self.z, self.type)

    def __abs__(self):
        """
        Returns the magnitude of the point vector.

        :return: the magnitude of the point vector
        :rtype: float
        """
        return math.hypot(self.x, self.y, self.z)

    def __add__(self, other):
        """
        Returns the summation of two point vectors.

        :param other: point vector to be added
        :type other: point
        :return: the summation of two point vectors
        :rtype: point
        """
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return point(x, y, z, coordinate.rectangular)

    def __mul__(self, scalar):
        """
        Returns the product of a point vector and a scalar.

        :param scalar: a scalar value
        :type scalar: float
        :return: point
        :rtype: point
        """
        return point(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
            coordinate.rectangular,
        )


class spiralCurve():
    """
    A class to create a spiral curves parallel to XY plane in GMSH. The curve is defined
    by a spline and it is divided into sub-curves. Sub-curves are used because it makes
    the geometry creation process easier.

    :param innerRadius: inner radius
    :type innerRadius: float
    :param gap: gap after each turn
    :type gap: float
    :param turns: number of turns
    :type turns: float
    :param z: z coordinate
    :type z: float
    :param initialTheta: initial theta angle in radians
    :type initialTheta: float
    :param direction: direction of the spiral (default: direction.ccw)
    :type direction: direction, optional
    :param cutPlaneNormal: normal vector of the plane that will cut the spiral curve
        (default: None)
    :type cutPlaneNormal: tuple[float, float, float], optional
    """

    # If the number of points used per turn is n, then the number of sections per turn
    # is n-1. They set the resolution of the spiral curve. It sets the limit of the
    # precision of the float number of turns that can be used to create the spiral
    # curve. The value below might be modified in Geometry.__init__ method.
    sectionsPerTurn = 16

    # There will be curvesPerTurn curve entities per turn. It will be effectively the
    # number of volumes per turn in the end. The value below might be modified in
    # Geometry.__init__ method.
    curvesPerTurn = 2

    def __init__(
        self,
        innerRadius,
        gap,
        turns,
        z,
        initialTheta,
        transitionNotchAngle,
        direction=direction.ccw,
        cutPlaneNormal=Tuple[float, float, float],
    ) -> None:
        spt = self.sectionsPerTurn  # just to make the code shorter
        self.turnRes = 1 / spt  # turn resolution
        cpt = self.curvesPerTurn  # just to make the code shorter
        self.turns = turns

        # =============================================================================
        # GENERATING POINTS STARTS ====================================================
        # =============================================================================

        # Calculate the coordinates of the points that define the spiral curve:
        if direction is direction.ccw:
            # If the spiral is counter-clockwise, the initial theta angle decreases,
            # and r increases as the theta angle decreases.
            multiplier = 1
        elif direction is direction.cw:
            # If the spiral is clockwise, the initial theta angle increases, and r
            # increases as the theta angle increases.
            multiplier = -1

        NofPointsPerTurn = int(spt + 1)
        thetaArrays = []
        for turn in range(1, int(self.turns) + 1):
            thetaArrays.append(
                np.linspace(
                    initialTheta + (turn - 1) * 2 * math.pi * multiplier,
                    initialTheta + (turn) * 2 * math.pi * multiplier,
                    NofPointsPerTurn,
                )
            )

        thetaArrays.append(
            np.linspace(
                initialTheta + (turn) * 2 * math.pi * multiplier,
                initialTheta + (self.turns) * 2 * math.pi * multiplier,
                round(spt * (self.turns - turn) + 1),
            )
        )

        if cutPlaneNormal is not None:
            # If the cutPlaneNormal is specified, the spiral curve will be cut by a
            # plane that is normal to the cutPlaneNormal vector and passes through the
            # origin.

            alpha = math.atan2(cutPlaneNormal[1], cutPlaneNormal[0]) - math.pi / 2
            alpha2 = alpha + math.pi

            listOfBreakPoints = []
            for turn in range(1, int(self.turns) + 2):
                breakPoint1 = alpha + (turn - 1) * 2 * math.pi * multiplier
                breakPoint2 = alpha2 + (turn - 1) * 2 * math.pi * multiplier
                if (
                    breakPoint1 > initialTheta
                    and breakPoint1 < initialTheta + 2 * math.pi * self.turns
                ):
                    listOfBreakPoints.append(breakPoint1)
                if (
                    breakPoint2 > initialTheta
                    and breakPoint2 < initialTheta + 2 * math.pi * self.turns
                ):
                    listOfBreakPoints.append(breakPoint2)

            thetaArrays.append(np.array(listOfBreakPoints))

        theta = np.concatenate(thetaArrays)
        theta = np.round(theta, 10)
        theta = np.unique(theta)
        theta = np.sort(theta)
        theta = theta[::multiplier]

        r = innerRadius + (theta - initialTheta) / (2 * math.pi) * (gap) * multiplier
        z = np.ones(theta.shape) * z

        # Create the points and store their tags:
        points = []  # point objects
        pointTags = []  # point tags
        breakPointObjectsDueToCutPlane = []  # only used if cutPlaneNormal is not None
        breakPointTagsDueToCutPlane = []  # only used if cutPlaneNormal is not None
        pointObjectsWithoutBreakPoints = []  # only used if cutPlaneNormal is not None
        pointTagsWithoutBreakPoints = []  # only used if cutPlaneNormal is not None
        breakPointObjectsDueToTransition = []
        breakPointTagsDueToTransition = []
        coordinateList = []

        for j in range(len(theta)):
            pointObject = point(r[j], theta[j], z[j], coordinate.cylindrical)
            [x_c, y_c, z_c] = [r[j], theta[j], z[j]]
            #print([x_c, y_c, z_c])
            coordinateList.append([x_c, y_c, z_c])
            points.append(pointObject)
            pointTags.append(pointObject.tag)
            if cutPlaneNormal is not None:
                if theta[j] in listOfBreakPoints:
                    breakPointObjectsDueToCutPlane.append(pointObject)
                    breakPointTagsDueToCutPlane.append(pointObject.tag)
                else:
                    pointObjectsWithoutBreakPoints.append(pointObject)
                    pointTagsWithoutBreakPoints.append(pointObject.tag)

            # identify if the point is a break point due to the layer transition:
            angle1 = initialTheta + (2 * math.pi - transitionNotchAngle) * multiplier
            angle2 = (
                initialTheta
                + ((self.turns % 1) * 2 * math.pi + transitionNotchAngle) * multiplier
            )
            if math.isclose(
                math.fmod(theta[j], 2 * math.pi), angle1, abs_tol=1e-6
            ) or math.isclose(math.fmod(theta[j], 2 * math.pi), angle2, abs_tol=1e-6):
                breakPointObjectsDueToTransition.append(pointObject)
                breakPointTagsDueToTransition.append(pointObject.tag)

        # Plotter
        # x_coords = [coord[0] for coord in coordinateList]
        # y_coords = [coord[1] for coord in coordinateList]
        # z_coords = [coord[2] for coord in coordinateList]

        # print(f'number of divisions {self.Pancake3DMeshWinding.ane}')
        # print(self.wi.ane)
        # Creating the 3D plot
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')

        # Plotting the coordinates
        # ax.scatter(x_coords, y_coords, z_coords, c='r', marker='o')
        #
        # # Setting labels
        # ax.set_xlabel('X Label')
        # ax.set_ylabel('Y Label')
        # ax.set_zlabel('Z Label')
        #
        # plt.show()

        # Logic to break the points up into relevant geom coordinates
        # Brick points structure (for X-Y plane only for now):
        # [[[x1, y1, z1], [x2, y2, z2], [x3, y3, z3], [x4, y4, z4]], ...]
        # Theoretically, very easy to extend to 8 points knowing the height of the

        # Defining the coordinate lists to which the points are to be added

        # winding one covers the list of points in the domain of theta [k, pi*k], where k is an integer number
        winding_1 = []
        # winding one covers the list of points in the domain of theta [pi*k, 2pi*k], where k is an integer number
        winding_2 = []
        # winding one covers the list of points in the domain of theta [k, pi*k], where k is an integer number
        winding_3 = []
        # winding one covers the list of points in the domain of theta [pi*k, 2pi*k], where k is an integer number
        winding_4 = []
        #print(theta[10])
        # heightPancake = self.geo.winding.height
        # print(heightPancake)
        for i in range(len(theta)-1): # range is reduced as no brick can be created starting at the last point
            # Assuming theta is a numpy array and you're looking for the index of a value close to pi
            value_to_find = theta[i]+np.pi
            tolerance = 1e-10  # Define a small tolerance
            # Find indices where the condition is true
            indices = np.where(np.abs(theta - value_to_find) < tolerance)[0]
            if len(indices) > 0:
                windingUpIndex = indices[0]  # Take the first index if there are multiple matches
                try:
                    x_1 = r[i] * np.cos(theta[i])
                    y_1 = r[i] * np.sin(theta[i])
                    z_g = z[i]
                    x_2 = r[i+1] * np.cos(theta[i+1])
                    y_2 = r[i+1] * np.sin(theta[i+1])
                    x_3 = r[windingUpIndex] * np.cos(theta[windingUpIndex])
                    y_3 = r[windingUpIndex] * np.sin(theta[windingUpIndex])
                    x_4 = r[windingUpIndex+1] * np.cos(theta[windingUpIndex+1])
                    y_4 = r[windingUpIndex+1] * np.sin(theta[windingUpIndex+1])
                    addPoints = [[x_1, y_1, z_g], [x_2, y_2, z_g], [x_3, y_3, z_g], [x_4, y_4, z_g]]
                    k = theta[i]//(2*np.pi)
                    if (theta[i] <= np.pi*(k+1)):
                        # print('winding 1 or 3')
                        if (k%2 == 0):
                            # print('winding 1')
                            winding_1.append(addPoints)
                        else:
                            # print('winding 3')
                            winding_3.append(addPoints)

                    if (theta[i] >= np.pi*(k+1)):
                        # print('winding 2 or 4')
                        if (k%2 == 0):
                            # print('winding 2')
                            winding_2.append(addPoints)
                        else:
                            # print('winding 4')
                            winding_4.append(addPoints)
                except IndexError:
                    print('All of the winding conductor points have been found')

        # print(winding_1)
        # print(winding_2)
        # print(winding_3)
        # print(winding_4)

        # Plotter
        # x_coords = [coord[0] for coord in winding_1]
        # y_coords = [coord[1] for coord in winding_1]
        # z_coords = [coord[2] for coord in winding_1]
        #
        # # Creating the 3D plot
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        #
        # # Plotting the coordinates
        # ax.scatter(x_coords, y_coords, z_coords, c='r', marker='o')
        #
        # # Setting labels
        # ax.set_xlabel('X Label')
        # ax.set_ylabel('Y Label')
        # ax.set_zlabel('Z Label')
        #
        # plt.show()

        # if True:
        #     indexPoint = 1
        #     rangeUpdated = 0
        #     dict_cond = {0: {'SHAPE': 'BR8', 'XCENTRE': '0.0', 'YCENTRE': '0.0', 'ZCENTRE': '0.0', 'PHI1': '0.0', 'THETA1': '0.0', 'PSI1': '0.0', 'XCEN2': '0.0', 'YCEN2': '0.0', 'ZCEN2': '0.0', 'THETA2': '0.0', 'PHI2': '0.0', 'PSI2': '0.0', 'XP1': '-0.879570', 'YP1': '-0.002940', 'ZP1': '-1.131209', 'XP2': '-0.879570', 'YP2': '0.002940', 'ZP2': '-1.131209', 'XP3': '-0.881381', 'YP3': '0.002940', 'ZP3': '-1.114205', 'XP4': '-0.881381', 'YP4': '-0.002940', 'ZP4': '-1.114205', 'XP5': '-0.861227', 'YP5': '-0.002972', 'ZP5': '-1.129183', 'XP6': '-0.861208', 'YP6': '0.002908', 'ZP6': '-1.129182', 'XP7': '-0.863294', 'YP7': '0.002912', 'ZP7': '-1.112210', 'XP8': '-0.863313', 'YP8': '-0.002968', 'ZP8': '-1.112211', 'CURD': '201264967.975494', 'SYMMETRY': '1', 'DRIVELABEL': 'drive 0', 'IRXY': '0', 'IRYZ': '0', 'IRZX': '0', 'TOLERANCE': '1e-6'}, 1: {'SHAPE': 'BR8', 'XCENTRE': '0.0', 'YCENTRE': '0.0', 'ZCENTRE': '0.0', 'PHI1': '0.0', 'THETA1': '0.0', 'PSI1': '0.0', 'XCEN2': '0.0', 'YCEN2': '0.0', 'ZCEN2': '0.0', 'THETA2': '0.0', 'PHI2': '0.0', 'PSI2': '0.0', 'XP1': '-0.861227', 'YP1': '-0.002972', 'ZP1': '-1.129183', 'XP2': '-0.861208', 'YP2': '0.002908', 'ZP2': '-1.129182', 'XP3': '-0.863294', 'YP3': '0.002912', 'ZP3': '-1.112210', 'XP4': '-0.863313', 'YP4': '-0.002968', 'ZP4': '-1.112211', 'XP5': '-0.842917', 'YP5': '-0.003066', 'ZP5': '-1.126858', 'XP6': '-0.842880', 'YP6': '0.002814', 'ZP6': '-1.126858', 'XP7': '-0.845242', 'YP7': '0.002830', 'ZP7': '-1.109922', 'XP8': '-0.845278', 'YP8': '-0.003050', 'ZP8': '-1.109922', 'CURD': '201264967.975494', 'SYMMETRY': '1', 'DRIVELABEL': 'drive 0', 'IRXY': '0', 'IRYZ': '0', 'IRZX': '0', 'TOLERANCE': '1e-6'}, 2: {'SHAPE': 'BR8', 'XCENTRE': '0.0', 'YCENTRE': '0.0', 'ZCENTRE': '0.0', 'PHI1': '0.0', 'THETA1': '0.0', 'PSI1': '0.0', 'XCEN2': '0.0', 'YCEN2': '0.0', 'ZCEN2': '0.0', 'THETA2': '0.0', 'PHI2': '0.0', 'PSI2': '0.0', 'XP1': '-0.842917', 'YP1': '-0.003066', 'ZP1': '-1.126858', 'XP2': '-0.842880', 'YP2': '0.002814', 'ZP2': '-1.126858', 'XP3': '-0.845242', 'YP3': '0.002830', 'ZP3': '-1.109922', 'XP4': '-0.845278', 'YP4': '-0.003050', 'ZP4': '-1.109922', 'XP5': '-0.824646', 'YP5': '-0.003216', 'ZP5': '-1.124235', 'XP6': '-0.824593', 'YP6': '0.002664', 'ZP6': '-1.124239', 'XP7': '-0.827229', 'YP7': '0.002698', 'ZP7': '-1.107343', 'XP8': '-0.827282', 'YP8': '-0.003181', 'ZP8': '-1.107339', 'CURD': '201264967.975494', 'SYMMETRY': '1', 'DRIVELABEL': 'drive 0', 'IRXY': '0', 'IRYZ': '0', 'IRZX': '0', 'TOLERANCE': '1e-6'}}
        #     # print(dict_cond)
        #     for brick in dict_cond:
        #         for pointIndex in range (rangeUpdated, rangeUpdated+7):
        #             dict_cond[brick][f'XP{indexPoint}'] = str(coordinateList[pointIndex][0])
        #             dict_cond[brick][f'YP{indexPoint}'] = str(coordinateList[pointIndex][1])
        #             dict_cond[brick][f'ZP{indexPoint}'] = str(coordinateList[pointIndex][2])
        #             indexPoint+=1
        #         indexPoint = 1
        #         rangeUpdated = rangeUpdated + 8

            # writing COND.json file
            # Define the path for the JSON file, one directory up from the current script
            # json_file_path = os.path.join(os.path.dirname(os.getcwd()), "BR8.json")

            # Function to print the contents of a JSON file
            # def print_json_contents(path):
            #     try:
            #         with open(path, 'r') as file:
            #             data = json.load(file)
            #             print(json.dumps(data, indent=4))
            #     except FileNotFoundError:
            #         print("File not found.")
            #     except json.JSONDecodeError:
            #         print("File is empty or contains non-JSON conforming data.")
            #
            # # Print current contents
            # print("Current contents of BR8.json:")
            # print_json_contents(json_file_path)

            # Overwrite the JSON file
            # with open(json_file_path, 'w') as file:
            #     json.dump(dict_cond, file, indent=4)
            #
            # print("\nContents of BR8.json after overwriting:")
            # print_json_contents(json_file_path)
            # writing the .cond file

            # p = tuh.Paths('tests/parsers', '')
            # FilesAndFolders.prep_folder(p.model_folder)

            # Specify the target directory relative to the current working directory
            target_dir = os.path.join(os.getcwd(), 'tests', '_outputs', 'parsers')

            # Ensure the target directory exists
            os.makedirs(target_dir, exist_ok=True)

            # Define the output file path
            # out_file = os.path.join(target_dir, 'BR8.cond')
            # list_of_shapes = ['BR8']
            # for shape in list_of_shapes:
            #         pc = ParserCOND()
            #         input_dict = dict_cond
            #         pc.write_cond(input_dict, out_file)
            # print('path')
            # print(out_file)
            # print('hello world')
        # =============================================================================
        # GENERATING POINTS ENDS ======================================================
        # =============================================================================

        # =============================================================================
        # GENERATING SPLINES STARTS ===================================================
        # =============================================================================

        # Create the spline with the points:
        spline = gmsh.model.occ.addSpline(pointTags)

        # Split the spline into sub-curves:
        sectionsPerCurve = int(spt / cpt)

        # Create a list of point tags that will split the spline:
        # Basically, they are the points to divide the spirals into sectionsPerCurve
        # turns. However, some other points are also included to support the float
        # number of turns. It is best to visually look at the divisions with
        # gmsh.fltk.run() to understand why the split points are chosen the way they are
        # selected.

        if cutPlaneNormal is None:
            pointObjectsWithoutBreakPoints = points
            pointTagsWithoutBreakPoints = pointTags

        splitPointTags = list(
            set(pointTagsWithoutBreakPoints[:-1:sectionsPerCurve])
            | set(pointTagsWithoutBreakPoints[-spt - 1 :: -spt])
            | set(breakPointTagsDueToCutPlane)
            | set(breakPointTagsDueToTransition)
        )
        splitPointTags = sorted(splitPointTags)
        # Remove the first element of the list (starting point):
        _, *splitPointTags = splitPointTags

        # Also create a list of corresponding point objects:
        splitPoints = list(
            set(pointObjectsWithoutBreakPoints[:-1:sectionsPerCurve])
            | set(pointObjectsWithoutBreakPoints[-spt - 1 :: -spt])
            | set(breakPointObjectsDueToCutPlane)
            | set(breakPointObjectsDueToTransition)
        )
        splitPoints = sorted(splitPoints, key=lambda x: x.tag)
        # Remove the first element of the list (starting point):
        _, *splitPoints = splitPoints

        # Split the spline:
        dims = [0] * len(splitPointTags)
        _, splines = gmsh.model.occ.fragment(
            [(1, spline)],
            list(zip(dims, splitPointTags)),
            removeObject=True,
            removeTool=True,
        )
        splines = splines[0]
        self.splineTags = [j for _, j in splines]

        # Note the turn number of each spline. This will be used in getSplineTag and
        # getSplineTags methods.
        self.splineTurns = []
        for i in range(len(self.splineTags)):
            if i == 0:
                startPoint = points[0]
                endPoint = splitPoints[0]
            elif i == len(self.splineTags) - 1:
                startPoint = splitPoints[-1]
                endPoint = points[-1]
            else:
                startPoint = splitPoints[i - 1]
                endPoint = splitPoints[i]

            startTurn = (startPoint.theta - initialTheta) / (2 * math.pi)
            startTurn = round(startTurn / self.turnRes) * self.turnRes
            endTurn = (endPoint.theta - initialTheta) / (2 * math.pi)
            endTurn = round(endTurn / self.turnRes) * self.turnRes

            if direction is direction.ccw:
                self.splineTurns.append((startTurn, endTurn))
            else:
                self.splineTurns.append((-startTurn, -endTurn))

        # Check if splineTurn tuples starts with the small turn number:
        for i in range(len(self.splineTurns)):
            self.splineTurns[i] = sorted(self.splineTurns[i])

        # =============================================================================
        # GENERATING SPLINES ENDS =====================================================
        # =============================================================================

        # Find start and end points of the spiral curve:
        gmsh.model.occ.synchronize()  # synchronize the model to make getBoundary work
        self.startPointTag = gmsh.model.getBoundary([(1, self.getSplineTag(0))])[1][1]
        self.endPointTag = gmsh.model.getBoundary(
            [(1, self.getSplineTag(self.turns, endPoint=True))]
        )[1][1]

    def getSplineTag(self, turn, endPoint=False):
        """
        Returns the spline tag at a specific turn. It returns the spline tag of the
        section that is on the turn except its end point.

        :param turn: turn number (it can be a float)
        :type turn: float
        :param endPoint: if True, return the spline tag of the section that is on the
            turn including its end point but not its start point (default: False)
        :type endPoint: bool, optional
        :return: spline tag
        """
        if endPoint:
            for i, r in enumerate(self.splineTurns):
                if r[0] + (self.turnRes / 2) < turn <= r[1] + (self.turnRes / 2):
                    return self.splineTags[i]
        else:
            for i, r in enumerate(self.splineTurns):
                if r[0] - (self.turnRes / 2) <= turn < r[1] - (self.turnRes / 2):
                    return self.splineTags[i]

    def getPointTag(self, turn, endPoint=False):
        """
        Returns the point object at a specific turn.

        :param turn: turn number (it can be a float)
        :type turn: float
        :return: point object
        :rtype: point
        """
        if turn < 0 or turn > self.turns:
            raise ValueError("Turn number is out of range!")

        if turn == 0:
            return self.startPointTag
        elif turn == self.turns:
            return self.endPointTag
        else:
            curveTag = self.getSplineTag(turn, endPoint=endPoint)
            if endPoint:
                points = gmsh.model.getBoundary([(1, curveTag)])
                return points[1][1]
            else:
                points = gmsh.model.getBoundary([(1, curveTag)])
                return points[0][1]

    def getSplineTags(self, turnStart=None, turnEnd=None):
        """
        Get the spline tags from a specific turn to another specific turn. If turnStart
        and turnEnd are not specified, it returns all the spline tags.

        :param turnStart: start turn number (it can be a float) (default: None)
        :type turnStart: float, optional
        :param turnEnd: end turn number (it can be a float) (default: None)
        :type turnEnd: float, optional
        :return: spline tags
        :rtype: list[int]
        """
        if turnStart is None and turnEnd is None:
            return self.splineTags
        elif turnStart is None or turnEnd is None:
            raise ValueError(
                "turnStart and turnEnd must be both specified or both not specified."
                " You specified only one of them."
            )
        else:
            start = self.splineTags.index(self.getSplineTag(turnStart, False))
            end = self.splineTags.index(self.getSplineTag(turnEnd, True)) + 1
            return self.splineTags[start:end]


class spiralSurface:
    """
    This is a class to create a spiral surface parallel to the XY plane in GMSH. If
    thinShellApproximation is set to False, it creates two spiral surfaces parallel to
    the XY plane, and their inner and outer curve loops in GMSH. One of the surfaces is
    the main surface specified, which is the winding surface, and the other is the
    contact layer surface (the gap between the winding surface). If thinShellApproximation
    is set to True, it creates only one spiral surface that touches each other
    (conformal).

    Note that surfaces are subdivided depending on the spiral curve divisions because
    this is required for the thin-shell approximation. Otherwise, when
    thinShellApproximation is set to True, it would be a disc rather than a spiral since
    it touches each other. However, this can be avoided by dividing the surfaces into
    small parts and making them conformal. Dividing the surfaces is not necessary when
    thinShellApproximation is set to false, but in order to use the same logic with TSA,
    it is divided anyway.

    :param innerRadius: inner radius
    :type innerRadius: float
    :param thickness: thickness
    :type thickness: float
    :param contactLayerThickness: contact layer thickness
    :type contactLayerThickness: float
    :param turns: number of turns
    :type turns: float
    :param z: z coordinate
    :type z: float
    :param initialTheta: initial theta angle in radians
    :type initialTheta: float
    :param spiralDirection: direction of the spiral (default: direction.ccw)
    :type spiralDirection: direction, optional
    :param thinShellApproximation: if True, the thin shell approximation is used
        (default: False)
    :type thinShellApproximation: bool, optional
    :param cutPlaneNormal: normal vector of the plane that will cut the spiral surface
        (default: None)
    :type cutPlaneNormal: tuple[float, float, float], optional
    """

    def __init__(
        self,
        innerRadius,
        thickness,
        contactLayerThickness,
        turns,
        z,
        initialTheta,
        transitionNotchAngle,
        spiralDirection=direction.ccw,
        thinShellApproximation=False,
        cutPlaneNormal=None,
    ) -> None:
        r_i = innerRadius
        t = thickness
        theta_i = initialTheta
        self.theta_i = theta_i

        self.surfaceTags = []
        self.contactLayerSurfaceTags = []

        self.direction = spiralDirection
        self.tsa = thinShellApproximation
        self.transitionNotchAngle = transitionNotchAngle
        # =============================================================================
        # GENERATING SPIRAL CURVES STARTS =============================================
        # =============================================================================
        if thinShellApproximation:
            # Create only one spiral curve because the thin shell approximation is used:
            # Winding thickness is increased slightly to ensure that the outer radius
            # would be the same without the thin shell approximation.
            turns = (
                turns + 1
            )  # for TSA, spiral has (n+1) turns but spiral surface has n
            spiral = spiralCurve(
                r_i,
                t + contactLayerThickness * (turns - 1) / (turns),
                turns,
                z,
                theta_i,
                transitionNotchAngle,
                spiralDirection,
                cutPlaneNormal=cutPlaneNormal,
            )

            # These are created to be able to use the same code with TSA and without TSA:
            innerSpiral = spiral
            outerSpiral = spiral
        else:
            # Create two spiral curves because the thin shell approximation is not used:
            innerSpiral = spiralCurve(
                r_i - contactLayerThickness,
                t + contactLayerThickness,
                turns + 1,
                z,
                theta_i,
                transitionNotchAngle,
                spiralDirection,
                cutPlaneNormal=cutPlaneNormal,
            )
            outerSpiral = spiralCurve(
                r_i,
                t + contactLayerThickness,
                turns + 1,
                z,
                theta_i,
                transitionNotchAngle,
                spiralDirection,
                cutPlaneNormal=cutPlaneNormal,
            )

        self.innerSpiral = innerSpiral
        self.outerSpiral = outerSpiral
        self.turns = turns
        # =============================================================================
        # GENERATING SPIRAL CURVES ENDS ===============================================
        # =============================================================================

        # =============================================================================
        # GENERATING SURFACES STARTS ==================================================
        # =============================================================================
        endLines = []
        endInsLines = []

        # This is used to check if all the contact layers are finished:
        allContactLayersAreFinished = False

        # Itterate over the spline tags:
        for i in range(len(innerSpiral.splineTags)):
            if thinShellApproximation:
                # The current spline will be the inner spline:
                innerSplineTag = spiral.splineTags[i]

                # Find the spline tag of the outer spline by finding the spline tag of
                # the spline that is exactly on the next turn:

                # Note the turn number of the current spline's start point:
                startTurn = spiral.splineTurns[i][0]

                if startTurn + 1 + 1e-4 > turns:
                    # If the current spline is on the outer surface, break the loop,
                    # because the whole surface is finished:
                    break

                # Find the outer spline tag:
                isItBroken = True
                for j, turnTuple in enumerate(spiral.splineTurns):
                    # Equality can not be checked with == because of the floating point
                    # errors:
                    if abs(turnTuple[0] - 1 - startTurn) < 1e-4:
                        outerSplineTag = spiral.splineTags[j]
                        isItBroken = False
                        break

                if isItBroken:
                    raise RuntimeError(
                        "Something went wrong while creating the spiral surface. Outer"
                        f" spline tag of {innerSplineTag} could not be found for TSA."
                    )

            else:
                # Store the tags of the current splines:
                innerSplineTag = innerSpiral.splineTags[i]
                outerSplineTag = outerSpiral.splineTags[i]

                # The current outer spline will be the inner spline of the
                # contact layer:
                innerInsSplineTag = outerSpiral.splineTags[i]

                # Find the spline tag of the contact layer's outer spline by finding the
                # spline tag of the spline that is exactly on the next turn:

                # Note the turn number of the current spline's start point:
                startTurn = outerSpiral.splineTurns[i][0]

                if startTurn + 1 + 1e-4 > turns + 1:
                    # If the current spline is on the outer surface, note that all the
                    # contact layers are finished:
                    allContactLayersAreFinished = True

                # Find the contact layer's outer spline tag:
                for j, turnTuple in enumerate(innerSpiral.splineTurns):
                    if math.isclose(turnTuple[0], 1 + startTurn, abs_tol=1e-6):
                        outerInsSplineTag = innerSpiral.splineTags[j]
                        break

            # Create the lines to connect the two splines so that a surface can be
            # created:

            # Create start line:
            if i == 0:
                # If it is the first spline, start line should be created.

                # Create points:
                isStartPoint = gmsh.model.getBoundary([(1, innerSplineTag)])[1][1]
                if thinShellApproximation:
                    osStartPoint = gmsh.model.getBoundary([(1, outerSplineTag)])[0][1]
                else:
                    osStartPoint = gmsh.model.getBoundary([(1, outerSplineTag)])[1][1]

                # Create the line:
                startLine = gmsh.model.occ.addLine(osStartPoint, isStartPoint)
                firstStartLine = startLine

                # Create lines for the contact layer if the thin shell approximation is not
                # used:
                if not thinShellApproximation and not allContactLayersAreFinished:
                    isInsStartPoint = gmsh.model.getBoundary([(1, innerInsSplineTag)])[
                        1
                    ][1]
                    osInsStartPoint = gmsh.model.getBoundary([(1, outerInsSplineTag)])[
                        0
                    ][1]

                    # Create the line:
                    startInsLine = gmsh.model.occ.addLine(
                        osInsStartPoint, isInsStartPoint
                    )
                    firstInsStartLine = startInsLine

            else:
                # If it is not the first spline, the start line is the end line of the
                # previous surface. This guarantees that the surfaces are connected
                # (conformality).
                startLine = endLines[i - 1]

                # Do the same for the contact layer if the thin shell approximation is not
                # used:
                if not thinShellApproximation and not allContactLayersAreFinished:
                    startInsLine = endInsLines[i - 1]

            # Create end line:

            # Create points:
            # The ifs are used because getBoundary is not consistent somehow.
            if i == 0:
                isEndPoint = gmsh.model.getBoundary([(1, innerSplineTag)])[0][1]
            else:
                isEndPoint = gmsh.model.getBoundary([(1, innerSplineTag)])[1][1]

            if (not i == 0) or thinShellApproximation:
                osEndPoint = gmsh.model.getBoundary([(1, outerSplineTag)])[1][1]
            else:
                osEndPoint = gmsh.model.getBoundary([(1, outerSplineTag)])[0][1]

            # Create the line:
            endLine = gmsh.model.occ.addLine(isEndPoint, osEndPoint)
            endLines.append(endLine)

            # Create lines for the contact layer if the thin shell approximation is not
            # used:
            if not thinShellApproximation and not allContactLayersAreFinished:
                if i == 0:
                    isInsEndPoint = gmsh.model.getBoundary([(1, innerInsSplineTag)])[0][
                        1
                    ]
                else:
                    isInsEndPoint = gmsh.model.getBoundary([(1, innerInsSplineTag)])[1][
                        1
                    ]

                osInsEndPoint = gmsh.model.getBoundary([(1, outerInsSplineTag)])[1][1]

                # Create the line:
                endInsLine = gmsh.model.occ.addLine(isInsEndPoint, osInsEndPoint)
                endInsLines.append(endInsLine)

            # Create the surface:
            curveLoop = gmsh.model.occ.addCurveLoop(
                [startLine, innerSplineTag, endLine, outerSplineTag]
            )
            self.surfaceTags.append(gmsh.model.occ.addPlaneSurface([curveLoop]))

            # Create the surface for the contact layer if the thin shell approximation is
            # not used:
            if not thinShellApproximation and not allContactLayersAreFinished:
                curveLoop = gmsh.model.occ.addCurveLoop(
                    [startInsLine, innerInsSplineTag, endInsLine, outerInsSplineTag]
                )
                self.contactLayerSurfaceTags.append(
                    gmsh.model.occ.addPlaneSurface([curveLoop])
                )

        # =============================================================================
        # GENERATING SURFACES ENDS ====================================================
        # =============================================================================

        # =============================================================================
        # GENERATING CURVE LOOPS STARTS ===============================================
        # =============================================================================

        # Create the inner and outer curve loops (for both TSA == True and TSA == False):

        # VERY IMPORTANT NOTES ABOUT THE DIRECTION OF THE CURVE LOOPS
        # 1- GMSH doesn't like duplicates. Or the user doesn't like duplicates if they
        #     want conformality. Actually, it's a positive thing about debugging because
        #     you can always use `Geometry.remove_all_duplicates()` to see if there are
        #     any duplicates. If there are, the problem is found. Solve it.
        # 2- The problem arises when one uses surface loops or curve loops. Because even
        #     if you think there are no duplicates, GMSH/OCC might create some during
        #     addCurveLoops and addSurfaceLoops operations. Even though
        #     `geometry.remove_all_duplicates()` tells that there are duplicates, the
        #     user doesn't suspect about addCurveLoop and addSurfaceLoop at first,
        #     because it doesn't make sense.
        # 3- How you put the curves in the curve loops is very important! The same curve
        #     loop with the same lines might cause problems if the user puts them in a
        #     different order. For example, to create a plane surface with two curve
        #     loops, the direction of the curve loops should be the same. That's why the
        #     code has both innerCurveLoopTag and innerOppositeCurveLoopTag (the same
        #     thing for the outer curve loop).

        # create the transition layer (notch):
        # Inner curve loop:
        notchStartPoint = innerSpiral.getPointTag(
            1 - transitionNotchAngle / (2 * math.pi)
        )
        notchLeftPoint = innerSpiral.getPointTag(0)
        notchLeftLine = gmsh.model.occ.addLine(notchStartPoint, notchLeftPoint)
        notchRightLine = innerSpiral.getSplineTag(
            1 - transitionNotchAngle / (2 * math.pi)
        )

        if thinShellApproximation:
            innerStartCurves = [firstStartLine]
        else:
            innerStartCurves = [firstInsStartLine, firstStartLine]

        if thinShellApproximation:

            notchCurveLoop = gmsh.model.occ.addCurveLoop(
                [notchLeftLine, notchRightLine] + innerStartCurves
            )
            self.innerNotchSurfaceTags = [
                gmsh.model.occ.addPlaneSurface([notchCurveLoop])
            ]
        else:
            notchMiddlePoint = outerSpiral.getPointTag(0)
            notchMiddleLine = gmsh.model.occ.addLine(notchStartPoint, notchMiddlePoint)

            notchCurveLoop1 = gmsh.model.occ.addCurveLoop(
                [notchLeftLine, notchMiddleLine, firstStartLine]
            )
            notchCurveLoop2 = gmsh.model.occ.addCurveLoop(
                [notchMiddleLine, notchRightLine, firstInsStartLine]
            )
            self.innerNotchSurfaceTags = [
                gmsh.model.occ.addPlaneSurface([notchCurveLoop1]),
                gmsh.model.occ.addPlaneSurface([notchCurveLoop2]),
            ]

        lines = innerSpiral.getSplineTags(
            0, 1 - transitionNotchAngle / (2 * math.pi)
        )  # The first turn of the spline
        innerCurves = lines + [notchLeftLine]
        self.innerNotchLeftLine = notchLeftLine

        self.innerStartCurves = innerStartCurves

        self.innerCurveLoopTag = gmsh.model.occ.addCurveLoop(innerCurves)
        self.innerOppositeCurveLoopTag = gmsh.model.occ.addCurveLoop(innerCurves[::-1])

        # Outer curve loop:
        # The last turn of the spline:
        if thinShellApproximation:
            notchStartPoint = innerSpiral.getPointTag(
                self.turns + transitionNotchAngle / (2 * math.pi) - 1
            )
            notchLeftPoint = innerSpiral.getPointTag(self.turns)
            notchLeftLine = gmsh.model.occ.addLine(notchStartPoint, notchLeftPoint)
            notchRightLine = innerSpiral.getSplineTag(
                self.turns - 1 + transitionNotchAngle / (2 * math.pi), endPoint=True
            )
        else:
            notchStartPoint = outerSpiral.getPointTag(
                self.turns + transitionNotchAngle / (2 * math.pi)
            )
            notchMiddlePoint = innerSpiral.getPointTag(self.turns + 1)
            notchLeftPoint = outerSpiral.getPointTag(self.turns + 1)
            notchLeftLine = gmsh.model.occ.addLine(notchStartPoint, notchLeftPoint)
            notchMiddleLine = gmsh.model.occ.addLine(notchStartPoint, notchMiddlePoint)
            notchRightLine = outerSpiral.getSplineTag(
                self.turns + transitionNotchAngle / (2 * math.pi), self.turns
            )
        if thinShellApproximation:
            lines = outerSpiral.getSplineTags(turns - 1, turns)
        else:
            lines = outerSpiral.getSplineTags(turns, turns + 1)

        if thinShellApproximation:
            outerEndCurves = [endLines[-1]]
        else:
            outerEndCurves = [endInsLines[-1], endLines[-1]]

        if thinShellApproximation:
            notchCurveLoop1 = gmsh.model.occ.addCurveLoop(
                [notchLeftLine, notchRightLine, endLines[-1]]
            )
            self.outerNotchSurfaceTags = [
                gmsh.model.occ.addPlaneSurface([notchCurveLoop1]),
            ]
        else:
            notchCurveLoop1 = gmsh.model.occ.addCurveLoop(
                [notchLeftLine, notchMiddleLine, endLines[-1]]
            )
            notchCurveLoop2 = gmsh.model.occ.addCurveLoop(
                [notchMiddleLine, notchRightLine, endInsLines[-1]]
            )
            self.outerNotchSurfaceTags = [
                gmsh.model.occ.addPlaneSurface([notchCurveLoop1]),
                gmsh.model.occ.addPlaneSurface([notchCurveLoop2]),
            ]

        if thinShellApproximation:
            lines = innerSpiral.getSplineTags(
                self.turns - 1 + transitionNotchAngle / (2 * math.pi), self.turns
            )  # The first turn of the spline
        else:
            lines = outerSpiral.getSplineTags(
                self.turns + transitionNotchAngle / (2 * math.pi), self.turns + 1
            )
        outerCurves = lines + [notchLeftLine]
        self.outerNotchLeftLine = notchLeftLine

        self.outerEndCurves = outerEndCurves

        self.outerCurveLoopTag = gmsh.model.occ.addCurveLoop(outerCurves)
        self.outerOppositeCurveLoopTag = gmsh.model.occ.addCurveLoop(outerCurves[::-1])
        # =============================================================================
        # GENERATING CURVE LOOPS ENDS =================================================
        # =============================================================================

        if not thinShellApproximation:
            surfaceTags = self.surfaceTags
            self.surfaceTags = self.contactLayerSurfaceTags
            self.contactLayerSurfaceTags = surfaceTags

    def getInnerRightPointTag(self):
        """
        Returns the point tag of the inner left point.

        :return: point tag
        :rtype: int
        """
        return self.innerSpiral.getPointTag(0)

    def getInnerUpperPointTag(self):
        """
        Returns the point tag of the inner right point.

        :return: point tag
        :rtype: int
        """
        if self.direction is direction.ccw:
            return self.innerSpiral.getPointTag(0.25)
        else:
            return self.innerSpiral.getPointTag(0.75)

    def getInnerLeftPointTag(self):
        """
        Returns the point tag of the inner upper point.

        :return: point tag
        :rtype: int
        """
        return self.innerSpiral.getPointTag(0.5)

    def getInnerLowerPointTag(self):
        """
        Returns the point tag of the inner lower point.

        :return: point tag
        :rtype: int
        """
        if self.direction is direction.ccw:
            return self.innerSpiral.getPointTag(0.75)
        else:
            return self.innerSpiral.getPointTag(0.25)

    def getOuterRightPointTag(self):
        """
        Returns the point tag of the outer left point.

        :return: point tag
        :rtype: int
        """
        if self.tsa:
            turns = self.turns
        else:
            turns = self.turns + 1
        return self.outerSpiral.getPointTag(turns, endPoint=False)

    def getOuterLowerPointTag(self):
        """
        Returns the point tag of the outer right point.

        :return: point tag
        :rtype: int
        """
        if self.tsa:
            turns = self.turns
        else:
            turns = self.turns + 1
        if self.direction is direction.ccw:
            return self.outerSpiral.getPointTag(turns - 0.25, endPoint=False)
        else:
            return self.outerSpiral.getPointTag(turns - 0.75, endPoint=False)

    def getOuterLeftPointTag(self):
        """
        Returns the point tag of the outer upper point.

        :return: point tag
        :rtype: int
        """
        if self.tsa:
            turns = self.turns
        else:
            turns = self.turns + 1
        return self.outerSpiral.getPointTag(turns - 0.5, endPoint=False)

    def getOuterUpperPointTag(self):
        """
        Returns the point tag of the outer lower point.

        :return: point tag
        :rtype: int
        """
        if self.tsa:
            turns = self.turns
        else:
            turns = self.turns + 1
        if self.direction is direction.ccw:
            return self.outerSpiral.getPointTag(turns - 0.75, endPoint=False)
        else:
            return self.outerSpiral.getPointTag(turns - 0.25, endPoint=False)

    def getInnerUpperRightCurves(self):
        """
        Returns the curve tags of the upper right curves.

        :return: curve tags
        :rtype: list[int]
        """
        if self.direction is direction.ccw:
            curves = self.innerSpiral.getSplineTags(0, 0.25)
        else:
            lines = self.innerSpiral.getSplineTags(
                0.75, 1 - self.transitionNotchAngle / (2 * math.pi)
            )  # The first turn of the spline
            lines = lines + [self.innerNotchLeftLine]

            return lines

        return curves

    def getInnerUpperLeftCurves(self):
        """
        Returns the curve tags of the upper left curves.

        :return: curve tags
        :rtype: list[int]
        """
        if self.direction is direction.ccw:
            curves = self.innerSpiral.getSplineTags(0.25, 0.5)
        else:
            curves = self.innerSpiral.getSplineTags(0.5, 0.75)

        return curves

    def getInnerLowerLeftCurves(self):
        """
        Returns the curve tags of the lower left curves.

        :return: curve tags
        :rtype: list[int]
        """
        if self.direction is direction.ccw:
            curves = self.innerSpiral.getSplineTags(0.5, 0.75)
        else:
            curves = self.innerSpiral.getSplineTags(0.25, 0.5)

        return curves

    def getInnerLowerRightCurves(self):
        """
        Returns the curve tags of the lower right curves.

        :return: curve tags
        :rtype: list[int]
        """
        if self.direction is direction.ccw:
            lines = self.innerSpiral.getSplineTags(
                0.75, 1 - self.transitionNotchAngle / (2 * math.pi)
            )  # The first turn of the spline
            lines = lines + [self.innerNotchLeftLine]

            return lines
        else:
            curves = self.innerSpiral.getSplineTags(0, 0.25)

        return curves

    def getOuterUpperRightCurves(self):
        """
        Returns the curve tags of the upper right curves.

        :return: curve tags
        :rtype: list[int]
        """
        if self.tsa:
            turns = self.turns
        else:
            turns = self.turns + 1

        if self.direction is direction.ccw:
            if self.tsa:
                lines = self.innerSpiral.getSplineTags(
                    self.turns - 1 + self.transitionNotchAngle / (2 * math.pi),
                    self.turns - 0.75,
                )  # The first turn of the spline
            else:
                lines = self.outerSpiral.getSplineTags(
                    self.turns + self.transitionNotchAngle / (2 * math.pi),
                    self.turns + 1 - 0.75,
                )
            lines = lines + [self.outerNotchLeftLine]

            return lines
        else:
            curves = self.outerSpiral.getSplineTags(turns - 0.25, turns)

        return curves

    def getOuterUpperLeftCurves(self):
        """
        Returns the curve tags of the lower right curves.

        :return: curve tags
        :rtype: list[int]
        """
        if self.tsa:
            turns = self.turns
        else:
            turns = self.turns + 1
        if self.direction is direction.ccw:
            curves = self.outerSpiral.getSplineTags(turns - 0.75, turns - 0.5)
        else:
            curves = self.outerSpiral.getSplineTags(turns - 0.5, turns - 0.25)

        return curves

    def getOuterLowerLeftCurves(self):
        """
        Returns the curve tags of the lower left curves.

        :return: curve tags
        :rtype: list[int]
        """
        if self.tsa:
            turns = self.turns
        else:
            turns = self.turns + 1
        if self.direction is direction.ccw:
            curves = self.outerSpiral.getSplineTags(turns - 0.5, turns - 0.25)
        else:
            curves = self.outerSpiral.getSplineTags(turns - 0.75, turns - 0.5)

        return curves

    def getOuterLowerRightCurves(self):
        """
        Returns the curve tags of the upper left curves.

        :return: curve tags
        :rtype: list[int]
        """
        if self.tsa:
            turns = self.turns
        else:
            turns = self.turns + 1
        if self.direction is direction.ccw:
            curves = self.outerSpiral.getSplineTags(turns - 0.25, turns)
        else:
            if self.tsa:
                lines = self.innerSpiral.getSplineTags(
                    self.turns - 1 + self.transitionNotchAngle / (2 * math.pi),
                    self.turns - 0.75,
                )  # The first turn of the spline
            else:
                lines = self.outerSpiral.getSplineTags(
                    self.turns + self.transitionNotchAngle / (2 * math.pi),
                    self.turns + 1 - 0.75,
                )
            lines = lines + [self.outerNotchLeftLine]

            return lines

        return curves

    def getInnerStartCurves(self):
        """
        Returns the curve tags of the start curves.

        :return: curve tags
        :rtype: list[int]
        """
        return self.innerStartCurves

    def getOuterEndCurves(self):
        """
        Returns the curve tags of the end curves.

        :return: curve tags
        :rtype: list[int]
        """
        return self.outerEndCurves


class circleWithFourCurves:
    def __init__(
        self,
        x,
        y,
        z,
        radius,
        upperRightTag=None,
        upperLeftTag=None,
        lowerLeftTag=None,
        lowerRightTag=None,
        leftPointTag=None,
        rightPointTag=None,
        upperPointTag=None,
        lowerPointTag=None,
    ):
        self.x = x
        self.y = y
        self.z = z
        self.r = radius
        if upperRightTag is None:
            dummyCircle = gmsh.model.occ.addCircle(self.x, self.y, self.z, self.r)
            self.leftPointTag = gmsh.model.occ.addPoint(self.x - self.r, self.y, self.z)
            self.rightPointTag = gmsh.model.occ.addPoint(
                self.x + self.r, self.y, self.z
            )
            self.upperPointTag = gmsh.model.occ.addPoint(
                self.x, self.y + self.r, self.z
            )
            self.lowerPointTag = gmsh.model.occ.addPoint(
                self.x, self.y - self.r, self.z
            )

            fragmentResults = gmsh.model.occ.fragment(
                [(1, dummyCircle)],
                [
                    (0, self.leftPointTag),
                    (0, self.rightPointTag),
                    (0, self.upperPointTag),
                    (0, self.lowerPointTag),
                ],
            )[0]
            linesDimTags = [dimTag for dimTag in fragmentResults if dimTag[0] == 1]

            self.upperRightTag = linesDimTags[0][1]
            self.upperLeftTag = linesDimTags[1][1]
            self.lowerLeftTag = linesDimTags[2][1]
            self.lowerRightTag = linesDimTags[3][1]
        else:
            self.upperRightTag = upperRightTag
            self.upperLeftTag = upperLeftTag
            self.lowerLeftTag = lowerLeftTag
            self.lowerRightTag = lowerRightTag

            self.leftPointTag = leftPointTag
            self.rightPointTag = rightPointTag
            self.upperPointTag = upperPointTag
            self.lowerPointTag = lowerPointTag


class outerAirSurface:
    def __init__(
        self,
        outerRadius,
        innerRadius,
        type="cylinder",
        divideIntoFourParts=False,
        divideTerminalPartIntoFourParts=False,
    ):
        self.surfaceTags = []

        self.divideIntoFourParts = divideIntoFourParts
        self.divideTerminalPartIntoFourParts = divideTerminalPartIntoFourParts

        # for cylinder:
        self.shellTags = []

        # for cuboid:
        self.shellTagsPart1 = []
        self.shellTagsPart2 = []
        self.shellTagsPart3 = []
        self.shellTagsPart4 = []

        self.type = type
        self.outerRadius = outerRadius
        self.innerRadius = innerRadius

    def createFromScratch(self, z, shellTransformation=False, shellRadius=None):
        self.z = z

        if self.divideIntoFourParts:
            self.innerCircle = circleWithFourCurves(0, 0, z, self.innerRadius)
        else:
            if self.divideTerminalPartIntoFourParts:
                self.innerCircle = circleWithFourCurves(0, 0, z, self.innerRadius)
                innerCL = gmsh.model.occ.addCurveLoop(
                    [
                        self.innerCircle.upperRightTag,
                        self.innerCircle.upperLeftTag,
                        self.innerCircle.lowerLeftTag,
                        self.innerCircle.lowerRightTag,
                    ]
                )
            else:
                innerCL = gmsh.model.occ.addCircle(0, 0, z, self.innerRadius)
                innerCL = gmsh.model.occ.addCurveLoop([innerCL])

        if self.type == "cylinder" and self.divideIntoFourParts:
            outerCircle = circleWithFourCurves(0, 0, z, self.outerRadius)

            leftLineTag = gmsh.model.occ.addLine(
                outerCircle.leftPointTag, self.innerCircle.leftPointTag
            )
            rightLineTag = gmsh.model.occ.addLine(
                outerCircle.rightPointTag, self.innerCircle.rightPointTag
            )
            upperLineTag = gmsh.model.occ.addLine(
                outerCircle.upperPointTag, self.innerCircle.upperPointTag
            )
            lowerLineTag = gmsh.model.occ.addLine(
                outerCircle.lowerPointTag, self.innerCircle.lowerPointTag
            )

            # Create surfaces:
            upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    outerCircle.upperRightTag,
                    rightLineTag,
                    self.innerCircle.upperRightTag,
                    -upperLineTag,
                ]
            )
            self.upperRightTag = gmsh.model.occ.addPlaneSurface([upperRightCurveLoop])
            self.surfaceTags.append(self.upperRightTag)

            upperLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    outerCircle.upperLeftTag,
                    leftLineTag,
                    self.innerCircle.upperLeftTag,
                    -upperLineTag,
                ]
            )
            self.upperLeftTag = gmsh.model.occ.addPlaneSurface([upperLeftCurveLoop])
            self.surfaceTags.append(self.upperLeftTag)

            lowerLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    outerCircle.lowerLeftTag,
                    leftLineTag,
                    self.innerCircle.lowerLeftTag,
                    -lowerLineTag,
                ]
            )
            self.lowerLeftTag = gmsh.model.occ.addPlaneSurface([lowerLeftCurveLoop])
            self.surfaceTags.append(self.lowerLeftTag)

            lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    outerCircle.lowerRightTag,
                    rightLineTag,
                    self.innerCircle.lowerRightTag,
                    -lowerLineTag,
                ]
            )
            self.lowerRightTag = gmsh.model.occ.addPlaneSurface([lowerRightCurveLoop])
            self.surfaceTags.append(self.lowerRightTag)

            if shellTransformation:
                shellOuterCircle = circleWithFourCurves(0, 0, z, shellRadius)
                shellLeftLineTag = gmsh.model.occ.addLine(
                    shellOuterCircle.leftPointTag, outerCircle.leftPointTag
                )
                shellRightLineTag = gmsh.model.occ.addLine(
                    shellOuterCircle.rightPointTag, outerCircle.rightPointTag
                )
                shellUpperLineTag = gmsh.model.occ.addLine(
                    shellOuterCircle.upperPointTag, outerCircle.upperPointTag
                )
                shellLowerLineTag = gmsh.model.occ.addLine(
                    shellOuterCircle.lowerPointTag, outerCircle.lowerPointTag
                )

                # Create surfaces:
                upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                    [
                        shellOuterCircle.upperRightTag,
                        shellRightLineTag,
                        outerCircle.upperRightTag,
                        -shellUpperLineTag,
                    ]
                )
                self.upperRightTag = gmsh.model.occ.addPlaneSurface(
                    [upperRightCurveLoop]
                )
                self.shellTags.append(self.upperRightTag)

                upperLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                    [
                        shellOuterCircle.upperLeftTag,
                        shellLeftLineTag,
                        outerCircle.upperLeftTag,
                        -shellUpperLineTag,
                    ]
                )
                self.upperLeftTag = gmsh.model.occ.addPlaneSurface([upperLeftCurveLoop])
                self.shellTags.append(self.upperLeftTag)

                lowerLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                    [
                        shellOuterCircle.lowerLeftTag,
                        shellLeftLineTag,
                        outerCircle.lowerLeftTag,
                        -shellLowerLineTag,
                    ]
                )
                self.lowerLeftTag = gmsh.model.occ.addPlaneSurface([lowerLeftCurveLoop])
                self.shellTags.append(self.lowerLeftTag)

                lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                    [
                        shellOuterCircle.lowerRightTag,
                        shellRightLineTag,
                        outerCircle.lowerRightTag,
                        -shellLowerLineTag,
                    ]
                )
                self.lowerRightTag = gmsh.model.occ.addPlaneSurface(
                    [lowerRightCurveLoop]
                )
                self.shellTags.append(self.lowerRightTag)

        elif self.type == "cylinder" and not self.divideIntoFourParts:
            outerCL = gmsh.model.occ.addCircle(0, 0, z, self.outerRadius)
            outerCL = gmsh.model.occ.addCurveLoop([outerCL])

            if shellTransformation:
                shellOuterCL = gmsh.model.occ.addCircle(0, 0, z, shellRadius)
                shellOuterCL = gmsh.model.occ.addCurveLoop([shellOuterCL])

                shellSurfaceTag = gmsh.model.occ.addPlaneSurface(
                    [shellOuterCL, outerCL]
                )
                self.shellTags.append(shellSurfaceTag)

            surfaceTag = gmsh.model.occ.addPlaneSurface([outerCL, innerCL])
            self.surfaceTags.append(surfaceTag)

        elif self.type == "cuboid":
            # LL: lower left
            # LR: lower right
            # UR: upper right
            # UL: upper left
            airLLpointTag = point(-self.outerRadius, -self.outerRadius, z).tag
            airLRpointTag = point(self.outerRadius, -self.outerRadius, z).tag
            airURpointTag = point(self.outerRadius, self.outerRadius, z).tag
            airULpointTag = point(-self.outerRadius, self.outerRadius, z).tag

            # LH: lower horizontal
            # UH: upper horizontal
            # LV: left vertical
            # RV: right vertical
            airLHlineTag = gmsh.model.occ.addLine(airLLpointTag, airLRpointTag)
            airRVLineTag = gmsh.model.occ.addLine(airLRpointTag, airURpointTag)
            airUHLineTag = gmsh.model.occ.addLine(airURpointTag, airULpointTag)
            airLVLineTag = gmsh.model.occ.addLine(airULpointTag, airLLpointTag)

            outerCL = gmsh.model.occ.addCurveLoop(
                [airLHlineTag, airRVLineTag, airUHLineTag, airLVLineTag]
            )

            if self.divideIntoFourParts:
                innerCL = gmsh.model.occ.addCurveLoop(
                    [
                        self.innerCircle.upperRightTag,
                        self.innerCircle.lowerRightTag,
                        self.innerCircle.lowerLeftTag,
                        self.innerCircle.upperLeftTag,
                    ]
                )

            surfaceTag = gmsh.model.occ.addPlaneSurface([outerCL, innerCL])
            self.surfaceTags.append(surfaceTag)

            if shellTransformation:
                # LL: lower left
                # LR: lower right
                # UR: upper right
                # UL: upper left
                shellLLpointTag = point(
                    -shellRadius,
                    -shellRadius,
                    z,
                ).tag
                shellLRpointTag = point(
                    shellRadius,
                    -shellRadius,
                    z,
                ).tag
                shellURpointTag = point(
                    shellRadius,
                    shellRadius,
                    z,
                ).tag
                shellULpointTag = point(
                    -shellRadius,
                    shellRadius,
                    z,
                ).tag

                # LH: lower horizontal
                # UH: upper horizontal
                # LV: left vertical
                # RV: right vertical
                shellLHlineTag = gmsh.model.occ.addLine(
                    shellLLpointTag, shellLRpointTag
                )
                shellRVLineTag = gmsh.model.occ.addLine(
                    shellLRpointTag, shellURpointTag
                )
                shellUHLineTag = gmsh.model.occ.addLine(
                    shellURpointTag, shellULpointTag
                )
                shellLVLineTag = gmsh.model.occ.addLine(
                    shellULpointTag, shellLLpointTag
                )

                shellLowerLeftLineTag = gmsh.model.occ.addLine(
                    shellLLpointTag, airLLpointTag
                )
                shellLowerRightLineTag = gmsh.model.occ.addLine(
                    shellLRpointTag, airLRpointTag
                )
                shellUpperLeftLineTag = gmsh.model.occ.addLine(
                    shellULpointTag, airULpointTag
                )
                shellUpperRightLineTag = gmsh.model.occ.addLine(
                    shellURpointTag, airURpointTag
                )

                # Shell lower surface:
                shellLowerPSTag = gmsh.model.occ.addCurveLoop(
                    [
                        shellLowerLeftLineTag,
                        airLHlineTag,
                        shellLowerRightLineTag,
                        shellLHlineTag,
                    ]
                )
                shellLowerPSTag = gmsh.model.occ.addPlaneSurface([shellLowerPSTag])
                self.shellTagsPart1.append(shellLowerPSTag)

                # Shell right surface:
                shellRightPSTag = gmsh.model.occ.addCurveLoop(
                    [
                        shellLowerRightLineTag,
                        airRVLineTag,
                        shellUpperRightLineTag,
                        shellRVLineTag,
                    ]
                )
                shellRightPSTag = gmsh.model.occ.addPlaneSurface([shellRightPSTag])
                self.shellTagsPart2.append(shellRightPSTag)

                # Shell upper surface:
                shellUpperPSTag = gmsh.model.occ.addCurveLoop(
                    [
                        shellUpperLeftLineTag,
                        airUHLineTag,
                        shellUpperRightLineTag,
                        shellUHLineTag,
                    ]
                )
                shellUpperPSTag = gmsh.model.occ.addPlaneSurface([shellUpperPSTag])
                self.shellTagsPart3.append(shellUpperPSTag)

                # Shell left surface:
                shellLeftPSTag = gmsh.model.occ.addCurveLoop(
                    [
                        shellLowerLeftLineTag,
                        airLVLineTag,
                        shellUpperLeftLineTag,
                        shellLVLineTag,
                    ]
                )
                shellLeftPSTag = gmsh.model.occ.addPlaneSurface([shellLeftPSTag])
                self.shellTagsPart4.append(shellLeftPSTag)

    def setPrecreatedSurfaceTags(
        self,
        surfaceTags,
        cylinderShellTags=None,
        cuboidShellTags1=None,
        cuboidShellTags2=None,
        cuboidShellTags3=None,
        cuboidShellTags4=None,
    ):
        if not isinstance(surfaceTags, list):
            raise TypeError("surfaceTags must be a list.")

        self.z = gmsh.model.occ.getCenterOfMass(2, surfaceTags[0])[2]
        self.surfaceTags.extend(surfaceTags)

        if self.divideIntoFourParts or self.divideTerminalPartIntoFourParts:
            # Create innerCircle object from the tags:
            curves = gmsh.model.getBoundary(
                [(2, tag) for tag in surfaceTags], oriented=False
            )
            innerCurveDimTags = findOuterOnes(curves, findInnerOnes=True)
            innerCurveTags = [dimTag[1] for dimTag in innerCurveDimTags]
            innerCurveTags.sort()
            upperRightCurve = innerCurveTags[0]
            upperLeftCurve = innerCurveTags[1]
            lowerLeftCurve = innerCurveTags[2]
            lowerRightCurve = innerCurveTags[3]

            points = gmsh.model.getBoundary([(1, upperLeftCurve)], oriented=False)
            pointTags = [dimTag[1] for dimTag in points]
            pointTags.sort()
            upperPointTag = pointTags[0]
            leftPointTag = pointTags[1]

            points = gmsh.model.getBoundary([(1, lowerRightCurve)], oriented=False)
            pointTags = [dimTag[1] for dimTag in points]
            pointTags.sort()
            rightPointTag = pointTags[0]
            lowerPointTag = pointTags[1]

            self.innerCircle = circleWithFourCurves(
                0,
                0,
                self.z,
                self.outerRadius,
                upperRightTag=upperRightCurve,
                upperLeftTag=upperLeftCurve,
                lowerLeftTag=lowerLeftCurve,
                lowerRightTag=lowerRightCurve,
                leftPointTag=leftPointTag,
                rightPointTag=rightPointTag,
                upperPointTag=upperPointTag,
                lowerPointTag=lowerPointTag,
            )

        if cylinderShellTags is not None:
            self.shellTags.extend(cylinderShellTags)

        if cuboidShellTags1 is not None:
            self.shellTagsPart1.extend(cuboidShellTags1)
            self.shellTagsPart2.extend(cuboidShellTags2)
            self.shellTagsPart3.extend(cuboidShellTags3)
            self.shellTagsPart4.extend(cuboidShellTags4)

    def getInnerCL(self):
        # checked!
        # _, curves = gmsh.model.occ.getCurveLoops(self.surfaceTags[0])
        # curves = list(curves)
        # curves = list(curves[1])

        # innerCL = gmsh.model.occ.addCurveLoop(curves)

        gmsh.model.occ.synchronize()  # don't delete this line
        curves = gmsh.model.getBoundary(
            [(2, tag) for tag in self.surfaceTags], oriented=False
        )
        innerCurveDimTags = findOuterOnes(curves, findInnerOnes=True)
        innerCurveTags = [dimTag[1] for dimTag in innerCurveDimTags]

        innerCL = gmsh.model.occ.addCurveLoop(innerCurveTags)
        return innerCL


class outerTerminalSurface:
    def __init__(
        self,
        outerRadius,
        tubeThickness,
        divideIntoFourParts=False,
    ):
        self.tubeSurfaceTags = []
        self.nontubeSurfaceTags = []

        self.divideIntoFourParts = divideIntoFourParts

        self.outerRadius = outerRadius
        self.tubeThickness = tubeThickness

    def createNontubePartWithMiddleCircleAndWinding(
        self, middleCircle: circleWithFourCurves, winding: spiralSurface
    ):
        leftLineTag = gmsh.model.occ.addLine(
            middleCircle.leftPointTag, winding.getOuterLeftPointTag()
        )
        rightLineTag = gmsh.model.occ.addLine(
            middleCircle.rightPointTag, winding.getOuterRightPointTag()
        )
        upperLineTag = gmsh.model.occ.addLine(
            middleCircle.upperPointTag, winding.getOuterUpperPointTag()
        )
        lowerLineTag = gmsh.model.occ.addLine(
            middleCircle.lowerPointTag, winding.getOuterLowerPointTag()
        )

        # Create surfaces for the nontube part:
        if winding.direction is direction.ccw:
            upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                winding.getOuterUpperRightCurves()
                # + winding.getOuterEndCurves()
                + [rightLineTag, middleCircle.upperRightTag, upperLineTag]
            )
        else:
            upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                winding.getOuterUpperRightCurves()
                + [rightLineTag, middleCircle.upperRightTag, upperLineTag]
            )
        self.upperRightTag = gmsh.model.occ.addPlaneSurface([upperRightCurveLoop])
        self.nontubeSurfaceTags.append(self.upperRightTag)

        upperLeftCurveLoop = gmsh.model.occ.addCurveLoop(
            winding.getOuterUpperLeftCurves()
            + [leftLineTag, middleCircle.upperLeftTag, upperLineTag]
        )
        self.upperLeftTag = gmsh.model.occ.addPlaneSurface([upperLeftCurveLoop])
        self.nontubeSurfaceTags.append(self.upperLeftTag)

        lowerLeftCurveLoop = gmsh.model.occ.addCurveLoop(
            winding.getOuterLowerLeftCurves()
            + [leftLineTag, middleCircle.lowerLeftTag, lowerLineTag]
        )
        self.lowerLeftTag = gmsh.model.occ.addPlaneSurface([lowerLeftCurveLoop])
        self.nontubeSurfaceTags.append(self.lowerLeftTag)

        if winding.direction is direction.ccw:
            lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                winding.getOuterLowerRightCurves()
                + [rightLineTag, middleCircle.lowerRightTag, lowerLineTag]
            )
        else:
            lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                winding.getOuterLowerRightCurves()
                # + winding.getOuterEndCurves()
                + [rightLineTag, middleCircle.lowerRightTag, lowerLineTag]
            )
        self.lowerRightTag = gmsh.model.occ.addPlaneSurface([lowerRightCurveLoop])
        self.nontubeSurfaceTags.append(self.lowerRightTag)

    def createWithOuterAirAndWinding(
        self, outerAir: outerAirSurface, winding: spiralSurface, pancakeIndex
    ):
        # Tube part:
        z = outerAir.z

        if self.divideIntoFourParts:
            outerCircle = outerAir.innerCircle
            middleCircle = circleWithFourCurves(
                0, 0, z, self.outerRadius - self.tubeThickness
            )

            leftLineTag = gmsh.model.occ.addLine(
                outerCircle.leftPointTag, middleCircle.leftPointTag
            )
            rightLineTag = gmsh.model.occ.addLine(
                outerCircle.rightPointTag, middleCircle.rightPointTag
            )
            upperLineTag = gmsh.model.occ.addLine(
                outerCircle.upperPointTag, middleCircle.upperPointTag
            )
            lowerLineTag = gmsh.model.occ.addLine(
                outerCircle.lowerPointTag, middleCircle.lowerPointTag
            )

            # Create surfaces for the tube part:
            upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    outerCircle.upperRightTag,
                    rightLineTag,
                    middleCircle.upperRightTag,
                    -upperLineTag,
                ]
            )
            self.upperRightTag = gmsh.model.occ.addPlaneSurface([upperRightCurveLoop])
            self.tubeSurfaceTags.append(self.upperRightTag)

            upperLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    outerCircle.upperLeftTag,
                    leftLineTag,
                    middleCircle.upperLeftTag,
                    -upperLineTag,
                ]
            )
            self.upperLeftTag = gmsh.model.occ.addPlaneSurface([upperLeftCurveLoop])
            self.tubeSurfaceTags.append(self.upperLeftTag)

            lowerLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    outerCircle.lowerLeftTag,
                    leftLineTag,
                    middleCircle.lowerLeftTag,
                    -lowerLineTag,
                ]
            )
            self.lowerLeftTag = gmsh.model.occ.addPlaneSurface([lowerLeftCurveLoop])
            self.tubeSurfaceTags.append(self.lowerLeftTag)

            lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    outerCircle.lowerRightTag,
                    rightLineTag,
                    middleCircle.lowerRightTag,
                    -lowerLineTag,
                ]
            )
            self.lowerRightTag = gmsh.model.occ.addPlaneSurface([lowerRightCurveLoop])
            self.tubeSurfaceTags.append(self.lowerRightTag)

        else:
            outerCL = outerAir.getInnerCL()

            middleCL = gmsh.model.occ.addCircle(
                0, 0, z, self.outerRadius - self.tubeThickness
            )
            middleCL = gmsh.model.occ.addCurveLoop([middleCL])

            tubeSurface = gmsh.model.occ.addPlaneSurface([outerCL, middleCL])
            self.tubeSurfaceTags.append(tubeSurface)

        # Nontube part:
        if self.divideIntoFourParts:
            self.createNontubePartWithMiddleCircleAndWinding(middleCircle, winding)

        else:
            # Inner and outer curve loops. Sometimes the opposite curve loops are used
            # because the other one comes from the self.contactTerminalSurface. To create
            # a valid surface, the topology of the curve loops should be consistent. See the
            # note in the spiralSurface class.
            if pancakeIndex % 2 == 0:
                innerCL = winding.outerCurveLoopTag
            elif pancakeIndex % 2 == 1:
                innerCL = winding.outerOppositeCurveLoopTag

            # potential bug (curve order might be wrong)
            if self.divideIntoFourParts:
                middleCL = gmsh.model.occ.addCurveLoop(
                    [
                        middleCircle.upperRightTag,
                        middleCircle.upperLeftTag,
                        middleCircle.lowerLeftTag,
                        middleCircle.lowerRightTag,
                    ]
                )

            nontubeSurface = gmsh.model.occ.addPlaneSurface([middleCL, innerCL])
            self.nontubeSurfaceTags.append(nontubeSurface)

    def createWithWindingAndTubeTags(
        self, winding: spiralSurface, tubeTags, pancakeIndex
    ):
        if not isinstance(tubeTags, list):
            raise TypeError("tubeTags must be a list.")

        self.tubeSurfaceTags.extend(tubeTags)

        middleCurves = gmsh.model.getBoundary(
            [(2, tag) for tag in tubeTags], oriented=False
        )
        middleCurveDimTags = findOuterOnes(middleCurves, findInnerOnes=True)
        middleCurveTags = [dimTag[1] for dimTag in middleCurveDimTags]

        if self.divideIntoFourParts:
            # Create middleCircle object from the tags:
            middleCurveTags.sort()
            upperRightCurve = middleCurveTags[0]
            upperLeftCurve = middleCurveTags[1]
            lowerLeftCurve = middleCurveTags[2]
            lowerRightCurve = middleCurveTags[3]

            points = gmsh.model.getBoundary([(1, upperLeftCurve)], oriented=False)
            pointTags = [dimTag[1] for dimTag in points]
            pointTags.sort()
            upperPointTag = pointTags[0]
            leftPointTag = pointTags[1]

            points = gmsh.model.getBoundary([(1, lowerRightCurve)], oriented=False)
            pointTags = [dimTag[1] for dimTag in points]
            pointTags.sort()
            rightPointTag = pointTags[0]
            lowerPointTag = pointTags[1]

            z = gmsh.model.occ.getCenterOfMass(1, upperRightCurve)[2]
            middleCircle = circleWithFourCurves(
                0,
                0,
                z,
                self.outerRadius - self.tubeThickness,
                upperRightTag=upperRightCurve,
                upperLeftTag=upperLeftCurve,
                lowerLeftTag=lowerLeftCurve,
                lowerRightTag=lowerRightCurve,
                leftPointTag=leftPointTag,
                rightPointTag=rightPointTag,
                upperPointTag=upperPointTag,
                lowerPointTag=lowerPointTag,
            )

            self.createNontubePartWithMiddleCircleAndWinding(middleCircle, winding)
        else:
            middleCL = gmsh.model.occ.addCurveLoop(middleCurveTags)

            if pancakeIndex % 2 == 0:
                innerCL = winding.outerCurveLoopTag
            elif pancakeIndex % 2 == 1:
                innerCL = winding.outerOppositeCurveLoopTag

            nontubeSurface = gmsh.model.occ.addPlaneSurface([middleCL, innerCL])
            self.nontubeSurfaceTags.append(nontubeSurface)


class innerAirSurface:
    def __init__(
        self, radius, divideIntoFourParts=False, divideTerminalPartIntoFourParts=False
    ):
        self.surfaceTags = []

        self.divideIntoFourParts = divideIntoFourParts
        self.divideTerminalPartIntoFourParts = divideTerminalPartIntoFourParts

        self.radius = radius

    def createFromScratch(self, z):
        self.z = z
        if self.divideIntoFourParts:
            self.outerCircle = circleWithFourCurves(0, 0, z, self.radius)

            originTag = point(0, 0, z).tag

            leftLineTag = gmsh.model.occ.addLine(
                self.outerCircle.leftPointTag, originTag
            )
            rightLineTag = gmsh.model.occ.addLine(
                self.outerCircle.rightPointTag, originTag
            )
            upperLineTag = gmsh.model.occ.addLine(
                self.outerCircle.upperPointTag, originTag
            )
            lowerLineTag = gmsh.model.occ.addLine(
                self.outerCircle.lowerPointTag, originTag
            )

            upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                [self.outerCircle.upperRightTag, rightLineTag, -upperLineTag]
            )
            upperRightTag = gmsh.model.occ.addPlaneSurface([upperRightCurveLoop])
            self.surfaceTags.append(upperRightTag)

            upperLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                [self.outerCircle.upperLeftTag, leftLineTag, -upperLineTag]
            )
            upperLeftTag = gmsh.model.occ.addPlaneSurface([upperLeftCurveLoop])
            self.surfaceTags.append(upperLeftTag)

            lowerLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                [self.outerCircle.lowerLeftTag, leftLineTag, -lowerLineTag]
            )
            lowerLeftTag = gmsh.model.occ.addPlaneSurface([lowerLeftCurveLoop])
            self.surfaceTags.append(lowerLeftTag)

            lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                [self.outerCircle.lowerRightTag, rightLineTag, -lowerLineTag]
            )
            lowerRightTag = gmsh.model.occ.addPlaneSurface([lowerRightCurveLoop])
            self.surfaceTags.append(lowerRightTag)

        else:
            if self.divideTerminalPartIntoFourParts:
                self.outerCircle = circleWithFourCurves(0, 0, z, self.radius)
                outerCL = gmsh.model.occ.addCurveLoop(
                    [
                        self.outerCircle.upperRightTag,
                        self.outerCircle.upperLeftTag,
                        self.outerCircle.lowerLeftTag,
                        self.outerCircle.lowerRightTag,
                    ]
                )
            else:
                outerCL = gmsh.model.occ.addCircle(0, 0, z, self.radius)
                outerCL = gmsh.model.occ.addCurveLoop([outerCL])

            surfaceTag = gmsh.model.occ.addPlaneSurface([outerCL])
            self.surfaceTags.append(surfaceTag)

    def setPrecreatedSurfaceTags(self, surfaceTags):
        if not isinstance(surfaceTags, list):
            raise TypeError("surfaceTags must be a list.")

        self.z = gmsh.model.occ.getCenterOfMass(2, surfaceTags[0])[2]  # potential bug
        self.surfaceTags = []
        self.surfaceTags.extend(surfaceTags)

        if self.divideIntoFourParts or self.divideTerminalPartIntoFourParts:
            # Create outerCirle object from the tags:
            curves = gmsh.model.getBoundary(
                [(2, tag) for tag in surfaceTags], oriented=False
            )
            outerCurveDimTags = findOuterOnes(curves)
            outerCurveTags = [dimTag[1] for dimTag in outerCurveDimTags]
            outerCurveTags.sort()
            upperRightCurve = outerCurveTags[0]
            upperLeftCurve = outerCurveTags[1]
            lowerLeftCurve = outerCurveTags[2]
            lowerRightCurve = outerCurveTags[3]

            points = gmsh.model.getBoundary([(1, upperLeftCurve)], oriented=False)
            pointTags = [dimTag[1] for dimTag in points]
            pointTags.sort()
            upperPointTag = pointTags[0]
            leftPointTag = pointTags[1]

            points = gmsh.model.getBoundary([(1, lowerRightCurve)], oriented=False)
            pointTags = [dimTag[1] for dimTag in points]
            pointTags.sort()
            rightPointTag = pointTags[0]
            lowerPointTag = pointTags[1]

            self.outerCircle = circleWithFourCurves(
                0,
                0,
                self.z,
                self.radius,
                upperRightTag=upperRightCurve,
                upperLeftTag=upperLeftCurve,
                lowerLeftTag=lowerLeftCurve,
                lowerRightTag=lowerRightCurve,
                leftPointTag=leftPointTag,
                rightPointTag=rightPointTag,
                upperPointTag=upperPointTag,
                lowerPointTag=lowerPointTag,
            )

    def getOuterCL(self):
        # checked!
        # _, curves = gmsh.model.occ.getCurveLoops(self.surfaceTags[0])
        # curves = list(curves)
        # curves = [int(curves[0])]

        # outerCL = gmsh.model.occ.addCurveLoop([curves[0]])

        # return outerCL

        curves = gmsh.model.getBoundary(
            [(2, tag) for tag in self.surfaceTags], oriented=False
        )
        outerCurveDimTags = findOuterOnes(curves)
        outerCurveTags = [dimTag[1] for dimTag in outerCurveDimTags]

        outerCL = gmsh.model.occ.addCurveLoop(outerCurveTags)
        return outerCL


class innerTerminalSurface:
    def __init__(self, innerRadius, tubeThickness, divideIntoFourParts=False):
        self.tubeSurfaceTags = []
        self.nontubeSurfaceTags = []

        self.divideIntoFourParts = divideIntoFourParts

        self.innerRadius = innerRadius
        self.tubeThickness = tubeThickness

    def createNontubePartWithMiddleCircleAndWinding(
        self, middleCircle: circleWithFourCurves, winding: spiralSurface
    ):
        leftLineTag = gmsh.model.occ.addLine(
            winding.getInnerLeftPointTag(), middleCircle.leftPointTag
        )
        rightLineTag = gmsh.model.occ.addLine(
            winding.getInnerRightPointTag(), middleCircle.rightPointTag
        )
        upperLineTag = gmsh.model.occ.addLine(
            winding.getInnerUpperPointTag(), middleCircle.upperPointTag
        )
        lowerLineTag = gmsh.model.occ.addLine(
            winding.getInnerLowerPointTag(), middleCircle.lowerPointTag
        )

        # Create surfaces for the nontube part:
        if winding.direction is direction.ccw:
            upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                winding.getInnerUpperRightCurves()
                + [
                    upperLineTag,
                    middleCircle.upperRightTag,
                    rightLineTag,
                ]
            )
        else:
            upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                winding.getInnerUpperRightCurves()
                + [
                    upperLineTag,
                    middleCircle.upperRightTag,
                    rightLineTag,
                ]
                # + winding.getInnerStartCurves()
            )
        self.upperRightTag = gmsh.model.occ.addPlaneSurface([upperRightCurveLoop])
        self.nontubeSurfaceTags.append(self.upperRightTag)

        upperLeftCurveLoop = gmsh.model.occ.addCurveLoop(
            winding.getInnerUpperLeftCurves()
            + [
                upperLineTag,
                middleCircle.upperLeftTag,
                leftLineTag,
            ]
        )
        self.upperLeftTag = gmsh.model.occ.addPlaneSurface([upperLeftCurveLoop])
        self.nontubeSurfaceTags.append(self.upperLeftTag)

        lowerLeftCurveLoop = gmsh.model.occ.addCurveLoop(
            winding.getInnerLowerLeftCurves()
            + [
                lowerLineTag,
                middleCircle.lowerLeftTag,
                leftLineTag,
            ]
        )
        self.lowerLeftTag = gmsh.model.occ.addPlaneSurface([lowerLeftCurveLoop])
        self.nontubeSurfaceTags.append(self.lowerLeftTag)

        if winding.direction is direction.ccw:
            lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                winding.getInnerLowerRightCurves()
                + [
                    lowerLineTag,
                    middleCircle.lowerRightTag,
                    rightLineTag,
                ]
                # + winding.getInnerStartCurves()
            )
        else:
            lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                winding.getInnerLowerRightCurves()
                + [
                    lowerLineTag,
                    middleCircle.lowerRightTag,
                    rightLineTag,
                ]
            )
        self.lowerRightTag = gmsh.model.occ.addPlaneSurface([lowerRightCurveLoop])
        self.nontubeSurfaceTags.append(self.lowerRightTag)

    def createWithInnerAirAndWinding(
        self, innerAir: innerAirSurface, winding: spiralSurface, pancakeIndex
    ):
        z = innerAir.z

        # Tube part:
        if self.divideIntoFourParts:
            innerCircle = innerAir.outerCircle
            middleCircle = circleWithFourCurves(
                0, 0, z, self.innerRadius + self.tubeThickness
            )

            leftLineTag = gmsh.model.occ.addLine(
                middleCircle.leftPointTag, innerCircle.leftPointTag
            )
            rightLineTag = gmsh.model.occ.addLine(
                middleCircle.rightPointTag, innerCircle.rightPointTag
            )
            upperLineTag = gmsh.model.occ.addLine(
                middleCircle.upperPointTag, innerCircle.upperPointTag
            )
            lowerLineTag = gmsh.model.occ.addLine(
                middleCircle.lowerPointTag, innerCircle.lowerPointTag
            )

            # Create surfaces for the tube part:
            upperRightCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    middleCircle.upperRightTag,
                    rightLineTag,
                    innerCircle.upperRightTag,
                    -upperLineTag,
                ]
            )
            self.upperRightTag = gmsh.model.occ.addPlaneSurface([upperRightCurveLoop])
            self.tubeSurfaceTags.append(self.upperRightTag)

            upperLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    middleCircle.upperLeftTag,
                    leftLineTag,
                    innerCircle.upperLeftTag,
                    -upperLineTag,
                ]
            )
            self.upperLeftTag = gmsh.model.occ.addPlaneSurface([upperLeftCurveLoop])
            self.tubeSurfaceTags.append(self.upperLeftTag)

            lowerLeftCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    middleCircle.lowerLeftTag,
                    leftLineTag,
                    innerCircle.lowerLeftTag,
                    -lowerLineTag,
                ]
            )
            self.lowerLeftTag = gmsh.model.occ.addPlaneSurface([lowerLeftCurveLoop])
            self.tubeSurfaceTags.append(self.lowerLeftTag)

            lowerRightCurveLoop = gmsh.model.occ.addCurveLoop(
                [
                    middleCircle.lowerRightTag,
                    rightLineTag,
                    innerCircle.lowerRightTag,
                    -lowerLineTag,
                ]
            )
            self.lowerRightTag = gmsh.model.occ.addPlaneSurface([lowerRightCurveLoop])
            self.tubeSurfaceTags.append(self.lowerRightTag)

        else:
            innerCL = innerAir.getOuterCL()

            middleCL = gmsh.model.occ.addCircle(
                0, 0, z, self.innerRadius + self.tubeThickness
            )
            middleCL = gmsh.model.occ.addCurveLoop([middleCL])

            tubeSurface = gmsh.model.occ.addPlaneSurface([middleCL, innerCL])
            self.tubeSurfaceTags.append(tubeSurface)

        # Nontube part:
        if self.divideIntoFourParts:
            self.createNontubePartWithMiddleCircleAndWinding(middleCircle, winding)

        else:
            # Inner and outer curve loops. Sometimes the opposite curve loops are used
            # because the other one comes from the self.contactTerminalSurface. To create
            # a valid surface, the topology of the curve loops should be consistent. See the
            # note in the spiralSurface class.
            if pancakeIndex == 0:
                outerCL = winding.innerCurveLoopTag

            elif pancakeIndex % 2 == 0:
                outerCL = winding.innerOppositeCurveLoopTag

            elif pancakeIndex % 2 == 1:
                outerCL = winding.innerCurveLoopTag

            # potential bug (curve order might be wrong)
            if self.divideIntoFourParts:
                middleCL = gmsh.model.occ.addCurveLoop(
                    [
                        middleCircle.upperRightTag,
                        middleCircle.upperLeftTag,
                        middleCircle.lowerLeftTag,
                        middleCircle.lowerRightTag,
                    ]
                )

            nontubeSurface = gmsh.model.occ.addPlaneSurface([outerCL, middleCL])
            self.nontubeSurfaceTags.append(nontubeSurface)

    def createWithWindingAndTubeTags(
        self, winding: spiralSurface, tubeTags, pancakeIndex
    ):
        if not isinstance(tubeTags, list):
            raise TypeError("tubeTags must be a list.")

        self.tubeSurfaceTags.extend(tubeTags)

        middleCurves = gmsh.model.getBoundary(
            [(2, tag) for tag in tubeTags], oriented=False
        )
        middleCurveDimTags = findOuterOnes(middleCurves)
        middleCurveTags = [dimTag[1] for dimTag in middleCurveDimTags]

        if self.divideIntoFourParts:
            # Create middleCircle object from the tags:
            middleCurveTags.sort()
            upperRightCurve = middleCurveTags[0]
            upperLeftCurve = middleCurveTags[1]
            lowerLeftCurve = middleCurveTags[2]
            lowerRightCurve = middleCurveTags[3]

            points = gmsh.model.getBoundary([(1, upperLeftCurve)], oriented=False)
            pointTags = [dimTag[1] for dimTag in points]
            pointTags.sort()
            upperPointTag = pointTags[0]
            leftPointTag = pointTags[1]

            points = gmsh.model.getBoundary([(1, lowerRightCurve)], oriented=False)
            pointTags = [dimTag[1] for dimTag in points]
            pointTags.sort()
            rightPointTag = pointTags[0]
            lowerPointTag = pointTags[1]

            z = gmsh.model.occ.getCenterOfMass(1, upperRightCurve)[2]
            middleCircle = circleWithFourCurves(
                0,
                0,
                z,
                self.innerRadius + self.tubeThickness,
                upperRightTag=upperRightCurve,
                upperLeftTag=upperLeftCurve,
                lowerLeftTag=lowerLeftCurve,
                lowerRightTag=lowerRightCurve,
                leftPointTag=leftPointTag,
                rightPointTag=rightPointTag,
                upperPointTag=upperPointTag,
                lowerPointTag=lowerPointTag,
            )

            self.createNontubePartWithMiddleCircleAndWinding(middleCircle, winding)
        else:
            middleCL = gmsh.model.occ.addCurveLoop(middleCurveTags)

            if pancakeIndex == 0:
                outerCL = winding.innerCurveLoopTag

            elif pancakeIndex % 2 == 0:
                outerCL = winding.innerOppositeCurveLoopTag

            elif pancakeIndex % 2 == 1:
                outerCL = winding.innerCurveLoopTag

            nontubeSurface = gmsh.model.occ.addPlaneSurface([outerCL, middleCL])
            self.nontubeSurfaceTags.append(nontubeSurface)


class pancakeCoilsWithAir:
    """
    A class to create Pancake3D coil. With this class, any number of pancake coils stack
    can be created in GMSH. Moreover, the class also creates some parts of the air
    volume as well. It creates the inner cylinder air volume and the outer tube air
    volume. However, the air between the pancake coils is not created. It is created in
    the gapAir class.

    self.fundamentalSurfaces are the surfaces at the bottom of each pancake coil. They
    are created one by one with self.generateFundamentalSurfaces() method. The first
    created self.fundamentalSurfaces are the first pancake coil's bottom surfaces. Those
    surfaces include the outer air shell surface, outer air tube surface, outer
    terminal's outer tube part, outer terminal's touching part, winding surfaces,
    contact layer surfaces, inner terminal's touching part, inner terminal's inner tube
    part, and inner air disc. Terminals are divided into two because they can only be
    connected with the perfect tubes since each pancake coil is rotated in a different
    direction.

    For the first pancake coil, self.fundamentalSurfaces are extruded downwards to
    connect the terminal to the end of the geometry at the bottom.

    Then self.fundamentalSurfaces are extruded upwards to create the first pancake coil
    with self.extrudeWindingPart method. The method returns the extrusion's top
    surfaces, which are saved in the topSurfaces variable.

    Then those topSurfaces variable is given to another method, self.extrudeGapPart, and
    they are further extruded upwards up to the bottom of the next pancake coil.
    However, only the air tube, air cylinder, and connection terminal (the perfect inner
    terminal tube or outer terminal tube) are extruded. Otherwise, conformality would be
    impossible. The gaps are filled with air in gapAir class with fragment operation
    later. Then the top surfaces are returned by the method and saved in
    self.contactSurfaces variable.

    Then using the self.contactSurfaces, self.generateFundamentalSurfaces method creates
    the new fundamental surfaces. All the surfaces from the self.contactSurfaces are
    used in the new self.fundamentalSurfaces variable to avoid surface duplication.

    The logic goes until the last topSurfaces are extruded upwards to connect the last
    terminal to the top of the geometry.

    Every pancake coil's rotation direction is different each time. Otherwise, their
    magnetic fields would neutralize each other.

    The first and second pancake coils are connected with the inner terminal. Then the
    second and the third pancake coils are connected with the outer terminal. And so on.

    :param geometryData: geometry information
    """

    def __init__(self, geometryData, meshData) -> None:
        logger.info("Generating pancake coils has been started.")
        start_time = timeit.default_timer()

        # Data:
        self.geo = geometryData
        self.mesh = meshData

        # ==============================================================================
        # CREATING VOLUME STORAGES STARTS ==============================================
        # ==============================================================================
        # Air shell (they will be empty if shellTransformation == False):
        # For cylinder type:
        self.airShellVolume = dimTags(name=self.geo.air.shellVolumeName, save=True)

        # For cuboid type:
        self.airShellVolumePart1 = dimTags(
            name=self.geo.air.shellVolumeName + "-Part1", save=True
        )
        self.airShellVolumePart2 = dimTags(
            name=self.geo.air.shellVolumeName + "-Part2", save=True
        )
        self.airShellVolumePart3 = dimTags(
            name=self.geo.air.shellVolumeName + "-Part3", save=True
        )
        self.airShellVolumePart4 = dimTags(
            name=self.geo.air.shellVolumeName + "-Part4", save=True
        )

        # Outer air tube volume (actually it is not a tube if the air type is cuboid):
        self.outerAirTubeVolume = dimTags(
            name=self.geo.air.name + "-OuterTube", save=True, parentName=self.geo.air.name
        )

        # Outer terminal's outer tube part:
        self.outerTerminalTubeVolume = dimTags(
            name=self.geo.terminals.outer.name + "-Tube", save=True, parentName=self.geo.terminals.outer.name
        )

        # Outer terminal's volume that touches the winding:
        self.outerTerminalTouchingVolume = dimTags(
            name=self.geo.terminals.outer.name + "-Touching",
            save=True,
            parentName=self.geo.terminals.outer.name,
        )

        # Inner terminal's volume that touches the winding:
        self.innerTerminalTouchingVolume = dimTags(
            name=self.geo.terminals.inner.name + "-Touching",
            save=True,
            parentName=self.geo.terminals.inner.name,
        )

        # Inner terminal's inner tube part:
        self.innerTerminalTubeVolume = dimTags(
            name=self.geo.terminals.inner.name + "-Tube", save=True, parentName=self.geo.terminals.inner.name
        )

        # Transition layers:
        self.innerTransitionNotchVolume = dimTags(
            name="innerTransitionNotch",
            save=True,
        )
        self.outerTransitionNotchVolume = dimTags(
            name="outerTransitionNotch",
            save=True,
        )

        # Inner air cylinder volume:
        self.centerAirCylinderVolume = dimTags(
            name=self.geo.air.name + "-InnerCylinder",
            save=True,
            parentName=self.geo.air.name,
        )

        # Top and bottom parts of the air volume:
        self.topAirPancakeWindingExtursionVolume = dimTags(
            name=self.geo.air.name + "-TopPancakeWindingExtursion",
            save=True,
            parentName=self.geo.air.name,
        )
        self.topAirPancakeContactLayerExtursionVolume = dimTags(
            name=self.geo.air.name + "-TopPancakeContactLayerExtursion",
            save=True,
            parentName=self.geo.air.name,
        )
        self.topAirTerminalsExtrusionVolume = dimTags(
            name=self.geo.air.name + "-TopTerminalsExtrusion",
            save=True,
            parentName=self.geo.air.name,
        )
        self.topAirTubeTerminalsExtrusionVolume = dimTags(
            name=self.geo.air.name + "-TopTubeTerminalsExtrusion",
            save=True,
            parentName=self.geo.air.name,
        )

        self.bottomAirPancakeWindingExtursionVolume = dimTags(
            name=self.geo.air.name + "-BottomPancakeWindingExtursion",
            save=True,
            parentName=self.geo.air.name,
        )
        self.bottomAirPancakeContactLayerExtursionVolume = dimTags(
            name=self.geo.air.name + "-BottomPancakeContactLayerExtursion",
            save=True,
            parentName=self.geo.air.name,
        )
        self.bottomAirTerminalsExtrusionVolume = dimTags(
            name=self.geo.air.name + "-BottomTerminalsExtrusion",
            save=True,
            parentName=self.geo.air.name,
        )
        self.bottomAirTubeTerminalsExtrusionVolume = dimTags(
            name=self.geo.air.name + "-BottomTubeTerminalsExtrusion",
            save=True,
            parentName=self.geo.air.name,
        )

        # Gap air:
        self.gapAirVolume = dimTags(
            name=self.geo.air.name + "-Gap", save=True, parentName=self.geo.air.name
        )

        # Create additional/optional volume storages (they might be used in the meshing
        # process):
        self.firstTerminalVolume = dimTags(name=self.geo.terminals.firstName, save=True)
        self.lastTerminalVolume = dimTags(name=self.geo.terminals.lastName, save=True)

        # ==============================================================================
        # CREATING VOLUME STORAGES ENDS ================================================
        # ==============================================================================

        # self.fundamentalSurfaces is a dictionary of surface dimTags tuples. The keys
        # are the dimTags objects of the corresponding volumes. The values are the
        # dimTags tuples of the surfaces that are used to extrude the volumes. It is
        # created in self.generateFundamentalSurfaces method.
        self.fundamentalSurfaces = {}

        # self.pancakeIndex stores the index of the current pancake coil.
        self.pancakeIndex = 0

        # self.contactSurfaces is a dictionary of surface dimTags tuples. The keys are
        # the dimTags objects of the corresponding volumes. The values are the dimTags
        # tuples of the surfaces that are obtained from the previous extrusion and used
        # for the next extrusion. The same surface is used for the next extrusion to
        # avoid surface duplication. It is created in self.extrudeGapPart and
        # self.extrudeWindingPart methods.
        self.contactSurfaces = {}

        # They will be lists of dimTags objects:
        self.individualWinding = []
        self.individualContactLayer = []

        self.gapAirSurfacesDimTags = []

        for i in range(self.geo.numberOfPancakes):
            # Itterate over the number of pancake coils:
            self.individualWinding.append(
                dimTags(
                    name=self.geo.winding.name + str(self.pancakeIndex + 1),
                    save=True,
                    parentName=self.geo.winding.name,
                )
            )
            self.individualContactLayer.append(
                dimTags(
                    name=self.geo.contactLayer.name + str(self.pancakeIndex + 1),
                    save=True,
                    parentName=self.geo.contactLayer.name,
                )
            )

            # Generate the fundamental surfaces:
            self.fundamentalSurfaces = self.generateFundamentalSurfaces()

            # Create gap air or collect the gap air surfaces:
            if i != 0:
                bottomSurfacesDimTags = []
                for key, value in topSurfaces.items():
                    if (
                        key is self.individualWinding[self.pancakeIndex - 1]
                        or key is self.individualContactLayer[self.pancakeIndex - 1]
                        or key is self.outerTerminalTouchingVolume
                        or key is self.innerTerminalTouchingVolume
                        or key is self.innerTransitionNotchVolume
                        or key is self.outerTransitionNotchVolume
                    ):
                        bottomSurfacesDimTags.extend(value)

                topSurfacesDimTags = []
                for key, value in self.fundamentalSurfaces.items():
                    if (
                        key is self.individualWinding[self.pancakeIndex]
                        or key is self.individualContactLayer[self.pancakeIndex]
                        or key is self.outerTerminalTouchingVolume
                        or key is self.innerTerminalTouchingVolume
                        or key is self.innerTransitionNotchVolume
                        or key is self.outerTransitionNotchVolume
                    ):
                        topSurfacesDimTags.extend(value)

                sideSurfacesDimTags = []
                if i % 2 == 1:
                    # Touches it tube and air tube
                    bottomSurfacesDimTags.extend(
                        topSurfaces[self.outerTerminalTubeVolume]
                    )
                    topSurfacesDimTags.extend(
                        self.fundamentalSurfaces[self.outerTerminalTubeVolume]
                    )

                    if self.mesh.terminals.structured:
                        lastItTubeVolDimTags = self.innerTerminalTubeVolume.getDimTags(
                            3
                        )[-4:]
                    else:
                        lastItTubeVolDimTags = self.innerTerminalTubeVolume.getDimTags(
                            3
                        )[-1:]

                    lastItTubeSurfsDimTags = gmsh.model.getBoundary(
                        lastItTubeVolDimTags, oriented=False
                    )
                    lastItTubeSideSurfsDimTags = findSurfacesWithNormalsOnXYPlane(
                        lastItTubeSurfsDimTags
                    )
                    sideSurfacesDimTags.extend(
                        findOuterOnes(lastItTubeSideSurfsDimTags)
                    )

                    if self.mesh.air.structured:
                        lastAirTubeVolDimTags = self.outerAirTubeVolume.getDimTags(3)[
                            -4:
                        ]
                    else:
                        lastAirTubeVolDimTags = self.outerAirTubeVolume.getDimTags(3)[
                            -1:
                        ]
                    lastAirTubeSurfsDimTags = gmsh.model.getBoundary(
                        lastAirTubeVolDimTags, oriented=False
                    )
                    lastAirTubeSurfsDimTags = findSurfacesWithNormalsOnXYPlane(
                        lastAirTubeSurfsDimTags
                    )
                    sideSurfacesDimTags.extend(
                        findOuterOnes(lastAirTubeSurfsDimTags, findInnerOnes=True)
                    )

                else:
                    # Touches ot tube and air cylinder
                    bottomSurfacesDimTags.extend(
                        topSurfaces[self.innerTerminalTubeVolume]
                    )
                    topSurfacesDimTags.extend(
                        self.fundamentalSurfaces[self.innerTerminalTubeVolume]
                    )
                    if self.mesh.terminals.structured:
                        lastOtTubeVolDimTags = self.outerTerminalTubeVolume.getDimTags(
                            3
                        )[-4:]
                    else:
                        lastOtTubeVolDimTags = self.outerTerminalTubeVolume.getDimTags(
                            3
                        )[-1:]

                    lastOtTubeSurfsDimTags = gmsh.model.getBoundary(
                        lastOtTubeVolDimTags, oriented=False
                    )
                    lastOtTubeSurfsDimTags = findSurfacesWithNormalsOnXYPlane(
                        lastOtTubeSurfsDimTags
                    )
                    sideSurfacesDimTags.extend(
                        findOuterOnes(lastOtTubeSurfsDimTags, findInnerOnes=True)
                    )

                    if self.mesh.air.structured:
                        lastAirCylinderVolDimTags = (
                            self.centerAirCylinderVolume.getDimTags(3)[-4:]
                        )
                    else:
                        lastAirCylinderVolDimTags = (
                            self.centerAirCylinderVolume.getDimTags(3)[-1:]
                        )

                    lastAirCylinderSurfsDimTags = gmsh.model.getBoundary(
                        lastAirCylinderVolDimTags, oriented=False
                    )
                    lastAirCylinderSurfsDimTags = findSurfacesWithNormalsOnXYPlane(
                        lastAirCylinderSurfsDimTags
                    )
                    sideSurfacesDimTags.extend(
                        findOuterOnes(lastAirCylinderSurfsDimTags)
                    )

                allGapAirSurfacesDimTags = (
                    bottomSurfacesDimTags + topSurfacesDimTags + sideSurfacesDimTags
                )

                # Technically, since all the boundary surfaces of the gap air volumes
                # are found here, we should be able to create the gap air volumes with
                # addSurfaceLoop and addVolume functions. However, when those are used,
                # Geometry.remove_all_duplicates() will indicate some
                # duplicates/ill-shaped geometry entities. The indication is
                # gmsh.model.occ.remove_all_duplicates() will change the geometry
                # (delete some volumes and create new ones), and I have always thought
                # that means there are big errors in the geometry and that geometry
                # should not be used.

                # Alternatively, using these surface tags, the gap air can be created
                # with fragment operations as well. Geometry.remove_all_duplicates()
                # will tell everything is fine when the fragment operation is used.

                # However, I checked manually as well, the way I am using the
                # addSurfaceLoop and addVolume should definitely work (because the end
                # result is the same with fragments), and I think it is a gmsh/occ
                # related problem. In the end, I realized creating the gap air with
                # addSurfaceLoop and addVolume won't even affect the mesh, and
                # everything seems conformal and nice. Since the fragment operation
                # is also very slow, I decided to use addSurfaceLoop and addVolume them.
                # However, I keep it as an option so that if the user feels something
                # funny about the geometry, the gap air can be created with fragment
                # operations as well.

                if not self.geo.air.generateGapAirWithFragment:
                    allGapAirSurfacesTags = [
                        dimTag[1] for dimTag in allGapAirSurfacesDimTags
                    ]
                    surfaceLoop = gmsh.model.occ.addSurfaceLoop(allGapAirSurfacesTags)
                    volume = gmsh.model.occ.addVolume([surfaceLoop])
                    self.gapAirVolume.add([(3, volume)])

                else:
                    # Save the surface tags for a fast fragment operation:
                    self.gapAirSurfacesDimTags.append(allGapAirSurfacesDimTags)

            # self.extrudeSurfaces uses self.fundamentalSurfaces for extrusion and adds
            # the new volumes to the dimTags objects and returns the dictionary of the
            # new top surfaces. The new top surfaces then will be used in extrudeGapPart
            # method.
            topSurfaces = self.extrudeWindingPart()

            if i == 0:
                # If it is the first pancake coil, fundemental surfaces are extruded
                # downwards to create the bottom air volume and terminal volume.
                _ = self.extrudeGapPart(
                    self.fundamentalSurfaces,
                    -self.geo.air.axialMargin,
                    terminalDimTagsObject=self.outerTerminalTubeVolume,
                    firstTerminal=True,
                )

            if not i == self.geo.numberOfPancakes - 1:
                # If it is not the last pancake coil, extrude the terminal surface to
                # create the next contactTerminalSurface and store the new volume in the
                # corresponding dimTags object.
                self.contactSurfaces = self.extrudeGapPart(topSurfaces)

            else:
                # If it is the last pancake coil, extrude the terminal surface all the
                # way up to the top and store the new volume in the corresponding
                # dimTags object.
                _ = self.extrudeGapPart(
                    topSurfaces,
                    self.geo.air.axialMargin,
                    lastTerminal=True,
                )
            self.pancakeIndex = self.pancakeIndex + 1

        # Create the gap air volume:
        if self.geo.air.generateGapAirWithFragment and self.geo.numberOfPancakes > 1:
            self.generateGapAirWithFragment(self.gapAirSurfacesDimTags)

        logger.info(
            "Generating pancake coils has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )

    def generateFundamentalSurfaces(self):
        """
        Generates the inner air, outer air, winding, contact layer, and terminal surfaces
        of the current pancake coil and returns them. It finds the z coordinate of the
        surfaces and the direction of the pancake coil, depending on the pancake index.

        :return: list of dimTags that contains fundamental surfaces
        :rtype: list[tuple[int, int]]
        """
        fundamentalSurfaces = {}

        # Select the direction of the spiral:
        if self.pancakeIndex % 2 == 0:
            spiralDirection = direction.ccw
        else:
            spiralDirection = direction.cw

        # Calculate the z coordinate of the surfaces:
        z = (
            -self.geo.air.h / 2
            + self.geo.air.axialMargin
            + self.pancakeIndex * (self.geo.winding.height + self.geo.gapBetweenPancakes)
        )

        # Create the winding and contact layer surface:
        surface = spiralSurface(
            self.geo.winding.innerRadius,
            self.geo.winding.thickness,
            self.geo.contactLayer.thickness,
            self.geo.winding.numberOfTurns,
            z,
            self.geo.winding.theta_i,
            self.geo.terminals.transitionNotchAngle,
            spiralDirection,
            thinShellApproximation=self.geo.contactLayer.thinShellApproximation,
        )
        #print("this is the surface")
        #print(surface)
        # Save the surface tags (if TSA, contactLayerSurfaceTags will be empty):
        fundamentalSurfaces[self.individualWinding[self.pancakeIndex]] = [
            (2, tag) for tag in surface.surfaceTags
        ]
        fundamentalSurfaces[self.individualContactLayer[self.pancakeIndex]] = [
            (2, tag) for tag in surface.contactLayerSurfaceTags
        ]

        if self.geo.air.type == "cylinder":
            outerAirSurf = outerAirSurface(
                self.geo.air.radius,
                self.geo.terminals.outer.r,
                type="cylinder",
                divideIntoFourParts=self.mesh.air.structured,
                divideTerminalPartIntoFourParts=self.mesh.terminals.structured,
            )
        elif self.geo.air.type == "cuboid":
            outerAirSurf = outerAirSurface(
                self.geo.air.sideLength / 2,
                self.geo.terminals.outer.r,
                type="cuboid",
                divideIntoFourParts=self.mesh.air.structured,
                divideTerminalPartIntoFourParts=self.mesh.terminals.structured,
            )

        outerTerminalSurf = outerTerminalSurface(
            self.geo.terminals.outer.r,
            self.geo.terminals.outer.thickness,
            divideIntoFourParts=self.mesh.terminals.structured,
        )
        innerTerminalSurf = innerTerminalSurface(
            self.geo.terminals.inner.r,
            self.geo.terminals.inner.thickness,
            divideIntoFourParts=self.mesh.terminals.structured,
        )
        innerAirSurf = innerAirSurface(
            self.geo.terminals.inner.r,
            divideIntoFourParts=self.mesh.air.structured,
            divideTerminalPartIntoFourParts=self.mesh.terminals.structured,
        )

        if self.contactSurfaces:
            # If self.contactSurfaces is not empty, it means that it is not the
            # first pancake coil. In that case, contactSurfaces should be used to
            # avoid surface duplication.

            # Create outer air:
            outerAirPSDimTags = self.contactSurfaces[self.outerAirTubeVolume]
            outerAirPSTags = [dimTag[1] for dimTag in outerAirPSDimTags]
            if self.geo.air.shellTransformation:
                if self.geo.air.type == "cuboid":
                    cuboidShellDimTags1 = self.contactSurfaces[self.airShellVolumePart1]
                    cuboidShellTags1 = [dimTag[1] for dimTag in cuboidShellDimTags1]
                    cuboidShellDimTags2 = self.contactSurfaces[self.airShellVolumePart2]
                    cuboidShellTags2 = [dimTag[1] for dimTag in cuboidShellDimTags2]
                    cuboidShellDimTags3 = self.contactSurfaces[self.airShellVolumePart3]
                    cuboidShellTags3 = [dimTag[1] for dimTag in cuboidShellDimTags3]
                    cuboidShellDimTags4 = self.contactSurfaces[self.airShellVolumePart4]
                    cuboidShellTags4 = [dimTag[1] for dimTag in cuboidShellDimTags4]
                    outerAirSurf.setPrecreatedSurfaceTags(
                        outerAirPSTags,
                        cuboidShellTags1=cuboidShellTags1,
                        cuboidShellTags2=cuboidShellTags2,
                        cuboidShellTags3=cuboidShellTags3,
                        cuboidShellTags4=cuboidShellTags4,
                    )
                elif self.geo.air.type == "cylinder":
                    cylinderShellDimTags = self.contactSurfaces[self.airShellVolume]
                    cylinderShellTags = [dimTag[1] for dimTag in cylinderShellDimTags]
                    outerAirSurf.setPrecreatedSurfaceTags(
                        outerAirPSTags,
                        cylinderShellTags=cylinderShellTags,
                    )
            else:
                outerAirSurf.setPrecreatedSurfaceTags(outerAirPSTags)

            # Create inner air:
            innerAirPSDimTags = self.contactSurfaces[self.centerAirCylinderVolume]
            innerAirPSTags = [dimTag[1] for dimTag in innerAirPSDimTags]
            innerAirSurf.setPrecreatedSurfaceTags(innerAirPSTags)

            if self.pancakeIndex % 2 == 0:
                # In this case, we should create all the surfaces for the inner terminal
                # but not for outer terminal. Because it is a pancake coil with an even
                # index (self.pancakeIndex%2==0) which means that it is connected to the
                # previous pancake coil with outer terminal and the outer terminal
                # surface is ready (extruded before).

                # Create outer terminal:
                outerTerminalTubePSDimTags = self.contactSurfaces[
                    self.outerTerminalTubeVolume
                ]
                outerTerminalTubePSTags = [
                    dimTag[1] for dimTag in outerTerminalTubePSDimTags
                ]
                outerTerminalSurf.createWithWindingAndTubeTags(
                    surface, outerTerminalTubePSTags, self.pancakeIndex
                )

                # Create inner terminal:
                innerTerminalSurf.createWithInnerAirAndWinding(
                    innerAirSurf, surface, self.pancakeIndex
                )

            else:
                # In this case, we should create all the surfaces for the outer terminal
                # but not for inner terminal. Because it is a pancake coil with an odd
                # index (self.pancakeIndex%2==1) which means that it is connected to the
                # previous pancake coil with inner terminal and the inner terminal
                # surface is ready (extruded before).

                # Create outer terminal:
                outerTerminalSurf.createWithOuterAirAndWinding(
                    outerAirSurf, surface, self.pancakeIndex
                )

                # Create inner terminal:
                innerTerminalTubePSDimTags = self.contactSurfaces[
                    self.innerTerminalTubeVolume
                ]
                innerTerminalTubePSTags = [
                    dimTag[1] for dimTag in innerTerminalTubePSDimTags
                ]
                innerTerminalSurf.createWithWindingAndTubeTags(
                    surface, innerTerminalTubePSTags, self.pancakeIndex
                )

        else:
            # If self.contactSurfaces is empty, it means that it is the first pancake
            # coil. In that case, the surfaces should be created from scratch.

            if self.geo.air.shellTransformation:
                if self.geo.air.type == "cuboid":
                    outerAirSurf.createFromScratch(
                        z,
                        shellTransformation=True,
                        shellRadius=self.geo.air.shellSideLength / 2,
                    )
                else:
                    outerAirSurf.createFromScratch(
                        z,
                        shellTransformation=True,
                        shellRadius=self.geo.air.shellOuterRadius,
                    )
            else:
                outerAirSurf.createFromScratch(z)

            innerAirSurf.createFromScratch(z)
            outerTerminalSurf.createWithOuterAirAndWinding(
                outerAirSurf, surface, self.pancakeIndex
            )
            innerTerminalSurf.createWithInnerAirAndWinding(
                innerAirSurf, surface, self.pancakeIndex
            )

        # Save the surface tags:
        fundamentalSurfaces[self.outerAirTubeVolume] = [
           (2, tag) for tag in outerAirSurf.surfaceTags
        ]

        fundamentalSurfaces[self.centerAirCylinderVolume] = [
           (2, tag) for tag in innerAirSurf.surfaceTags
        ]

        fundamentalSurfaces[self.outerTerminalTubeVolume] = [
           (2, tag) for tag in outerTerminalSurf.tubeSurfaceTags
        ]
        fundamentalSurfaces[self.outerTerminalTouchingVolume] = [
           (2, tag) for tag in outerTerminalSurf.nontubeSurfaceTags
        ]

        fundamentalSurfaces[self.innerTerminalTubeVolume] = [
           (2, tag) for tag in innerTerminalSurf.tubeSurfaceTags
        ]
        fundamentalSurfaces[self.innerTerminalTouchingVolume] = [
           (2, tag) for tag in innerTerminalSurf.nontubeSurfaceTags
        ]
        fundamentalSurfaces[self.innerTransitionNotchVolume] = [
           (2, tag) for tag in surface.innerNotchSurfaceTags
        ]
        fundamentalSurfaces[self.outerTransitionNotchVolume] = [
           (2, tag) for tag in surface.outerNotchSurfaceTags
        ]

        if self.geo.air.shellTransformation:
            if self.geo.air.type == "cuboid":
                fundamentalSurfaces[self.airShellVolumePart1] = [
                    (2, tag) for tag in outerAirSurf.shellTagsPart1
                ]
                fundamentalSurfaces[self.airShellVolumePart2] = [
                    (2, tag) for tag in outerAirSurf.shellTagsPart2
                ]
                fundamentalSurfaces[self.airShellVolumePart3] = [
                    (2, tag) for tag in outerAirSurf.shellTagsPart3
                ]
                fundamentalSurfaces[self.airShellVolumePart4] = [
                    (2, tag) for tag in outerAirSurf.shellTagsPart4
                ]
            elif self.geo.air.type == "cylinder":
                fundamentalSurfaces[self.airShellVolume] = [
                    (2, tag) for tag in outerAirSurf.shellTags
                ]
        # windingSurfaces = {}
        # # Save only the winding surface tags:
        # windingSurfaces[self.individualWinding[self.pancakeIndex]] = [
        #     (2, tag) for tag in surface.surfaceTags
        # ]
        # fundamentalSurfaces = windingSurfaces
        # print(fundamentalSurfaces)

        return fundamentalSurfaces

    def extrudeGapPart(
        self,
        surfacesDict,
        tZ: float = None,
        terminalDimTagsObject: dimTags = None,
        firstTerminal=False,
        lastTerminal=False,
    ):
        """
        Extrudes the given surfaces dimTags dictionary to a given height (tZ) and adds
        the created volumes to the corresponding dictionary keys (dimTags objects). It
        returns the extrusion's top surfaces as a dictionary again, where the keys are
        the corresponding dimTagsObjects and the values are the dimTags of the surfaces.

        If tZ is not given, then it is set to the gap height (self.geo.gapBetweenPancakes). This is the
        default value used for connecting the pancake coils. Only for the creation of
        the first and the last pancake coils different tZ values are used.

        If terminalDimTagsObject is not given, then the created volume is added
        automatically to the innerTerminalVolume or outerTerminalVolume dimTags object,
        depending on the value of self.pancakeIndex. However, giving
        terminalDimTagsObject is necessary for creating the first and the last terminal.
        Otherwise, finding out the correct terminal dimTagsObject would be very
        challenging.

        :param surfaces: the surface dimTag dictionary to be extruded. The keys are the
                    dimTags objects and the values are the dimTags of the surfaces. The
                    keys are used to easily add the corresponding volumes to the correct
                    dimTags objects
        :type surfaces: dict[dimTags, list[tuple[int, int]]]
        :param tZ: the height of the extrusion
        :type tZ: float, optional
        :param terminalDimTagsObject: the dimTags object of the terminal to be extruded
        :type terminalDimTagsObject: dimTags, optional
        :return: top surfaces of the extrusion as a dictionary where the keys are the
                    dimTags objects and the values are the dimTags of the surfaces
        :rtype: dict[dimTags, list[tuple[int, int]]]
        """
        bottomPart = False
        topPart = False
        if tZ is None:
            tZ = self.geo.gapBetweenPancakes
        elif tZ < 0:
            bottomPart = True
        elif tZ > 0:
            topPart = True

        if terminalDimTagsObject is None:
            # terminalDimTagsObject needs to be given for the first terminal that is
            # extruded downwards.
            if self.pancakeIndex % 2 == 0:
                terminalDimTagsObject = self.innerTerminalTubeVolume
            else:
                terminalDimTagsObject = self.outerTerminalTubeVolume

        # if terminalDimTagsObject is self.innerTerminalVolume:
        #     otherTerminal = self.outerTerminalVolume
        # else:
        #     otherTerminal = self.innerTerminalVolume

        # Create the list of surfaces to be extruded:
        listOfDimTags = []
        listOfDimTagsObjects = []
        listOfDimTagsForTopSurfaces = []
        if topPart:
            # Then in this case, most of the surfaces should be added to the air volumes
            # instead of the terminal, winding, and contact layer volumes.
            for key, dimTagsList in surfacesDict.items():
                if key is self.individualWinding[self.pancakeIndex]:
                    dimTagsObjects = [self.topAirPancakeWindingExtursionVolume] * len(
                        dimTagsList
                    )
                elif key is self.individualContactLayer[self.pancakeIndex]:
                    dimTagsObjects = [
                        self.topAirPancakeContactLayerExtursionVolume
                    ] * len(dimTagsList)
                elif (
                    key is terminalDimTagsObject
                    or key is self.airShellVolume
                    or key is self.airShellVolumePart1
                    or key is self.airShellVolumePart2
                    or key is self.airShellVolumePart3
                    or key is self.airShellVolumePart4
                    or key is self.outerAirTubeVolume
                    or key is self.centerAirCylinderVolume
                ):
                    dimTagsObjects = [key] * len(dimTagsList)
                else:
                    # key is self.outerTerminalTouchingVolume
                    # or key is self.innerTerminalTouchingVolume
                    # or key is (other terminal's tube volume)
                    dimTagsObjects = [self.topAirTerminalsExtrusionVolume] * len(
                        dimTagsList
                    )
                    if (
                        key is self.innerTerminalTubeVolume
                        or key is self.outerTerminalTubeVolume
                    ):
                        dimTagsObjects = [
                            self.topAirTubeTerminalsExtrusionVolume
                        ] * len(dimTagsList)

                listOfDimTagsForTopSurfaces = listOfDimTagsForTopSurfaces + [key] * len(
                    dimTagsList
                )
                listOfDimTags = listOfDimTags + dimTagsList
                listOfDimTagsObjects = listOfDimTagsObjects + dimTagsObjects
        elif bottomPart:
            # Then in this case, most of the surfaces should be added to the air volumes
            # instead of the terminal, winding, and contact layer volumes.
            for key, dimTagsList in surfacesDict.items():
                if key is self.individualWinding[self.pancakeIndex]:
                    dimTagsObjects = [
                        self.bottomAirPancakeWindingExtursionVolume
                    ] * len(dimTagsList)
                elif key is self.individualContactLayer[self.pancakeIndex]:
                    dimTagsObjects = [
                        self.bottomAirPancakeContactLayerExtursionVolume
                    ] * len(dimTagsList)
                elif (
                    key is terminalDimTagsObject
                    or key is self.airShellVolume
                    or key is self.airShellVolumePart1
                    or key is self.airShellVolumePart2
                    or key is self.airShellVolumePart3
                    or key is self.airShellVolumePart4
                    or key is self.outerAirTubeVolume
                    or key is self.centerAirCylinderVolume
                ):
                    dimTagsObjects = [key] * len(dimTagsList)
                else:
                    # key is self.outerTerminalTouchingVolume
                    # or key is self.innerTerminalTouchingVolume
                    # or key is (other terminal's tube volume)
                    dimTagsObjects = [self.bottomAirTerminalsExtrusionVolume] * len(
                        dimTagsList
                    )
                    if (
                        key is self.innerTerminalTubeVolume
                        or key is self.outerTerminalTubeVolume
                    ):
                        dimTagsObjects = [
                            self.bottomAirTubeTerminalsExtrusionVolume
                        ] * len(dimTagsList)

                listOfDimTagsForTopSurfaces = listOfDimTagsForTopSurfaces + [key] * len(
                    dimTagsList
                )
                listOfDimTags = listOfDimTags + dimTagsList
                listOfDimTagsObjects = listOfDimTagsObjects + dimTagsObjects
        else:
            for key, dimTagsList in surfacesDict.items():
                if (
                    key is self.outerAirTubeVolume
                    or key is self.centerAirCylinderVolume
                    or key is self.airShellVolume
                    or key is self.airShellVolumePart1
                    or key is self.airShellVolumePart2
                    or key is self.airShellVolumePart3
                    or key is self.airShellVolumePart4
                    or key is terminalDimTagsObject
                ):
                    dimTagsObjects = [key] * len(dimTagsList)

                    listOfDimTags = listOfDimTags + dimTagsList
                    listOfDimTagsObjects = listOfDimTagsObjects + dimTagsObjects

            listOfDimTagsForTopSurfaces = listOfDimTagsObjects

        extrusionResult = dimTags()
        extrusionResult.add(gmsh.model.occ.extrude(listOfDimTags, 0, 0, tZ))

        # Add the created volumes to the corresponding dimTags objects:
        volumeDimTags = extrusionResult.getDimTags(3)
        for i, volumeDimTag in enumerate(volumeDimTags):
            listOfDimTagsObjects[i].add(volumeDimTag)

        if firstTerminal:
            self.firstTerminalVolume.add(terminalDimTagsObject.getDimTags(3))
        elif lastTerminal:
            self.lastTerminalVolume.add(terminalDimTagsObject.getDimTags(3))

        topSurfacesDimTags = extrusionResult.getExtrusionTop()
        topSurfacesDict = {}
        for i, topSurfaceDimTag in enumerate(topSurfacesDimTags):
            if listOfDimTagsObjects[i] in topSurfacesDict:
                topSurfacesDict[listOfDimTagsForTopSurfaces[i]].append(topSurfaceDimTag)
            else:
                topSurfacesDict[listOfDimTagsForTopSurfaces[i]] = [topSurfaceDimTag]

        return topSurfacesDict

    def extrudeWindingPart(self):
        """
        Extrudes all the fundamental surfaces of the pancake coil by self.geo.winding.height and
        returns the next connection terminal's top surface dimTag, and other air dimTags
        in a dictionary so that they can be further extruded.

        :return: dictionary of top surfaces where the keys are the dimTags objects and
                    the values are the dimTags of the surfaces
        :rtype: dict[dimTags, list[tuple[int, int]]]
        """
        # Create the list of surfaces to be extruded:
        listOfDimTags = []
        listOfDimTagsObjects = []
        for key, dimTagsList in self.fundamentalSurfaces.items():
            dimTagsObjects = [key] * len(dimTagsList)

            listOfDimTags = listOfDimTags + dimTagsList
            listOfDimTagsObjects = listOfDimTagsObjects + dimTagsObjects

        # Extrude the fundamental surfaces:
        extrusionResult = dimTags()
        extrusionResult.add(gmsh.model.occ.extrude(listOfDimTags, 0, 0, self.geo.winding.height))

        # Add the created volumes to the corresponding dimTags objects:
        volumes = extrusionResult.getDimTags(3)
        for i, volumeDimTag in enumerate(volumes):
            listOfDimTagsObjects[i].add(volumeDimTag)

        if self.pancakeIndex == 0:
            # Note the first pancake (sometimes useful for creating regions in the
            # meshing part):
            for i, volumeDimTag in enumerate(volumes):
                if listOfDimTagsObjects[i].parentName == self.geo.terminals.outer.name:
                    self.firstTerminalVolume.add(volumeDimTag)

        # Not elif! Because the first pancake coil is also the last pancake coil if
        # there is only one pancake coil.
        if self.pancakeIndex == self.geo.numberOfPancakes - 1:
            # Note the last pancake (sometimes useful for creating regions in the
            # meshing part):
            for i, volumeDimTag in enumerate(volumes):
                if (
                    self.pancakeIndex % 2 == 1
                    and listOfDimTagsObjects[i].parentName == self.geo.terminals.outer.name
                ):
                    self.lastTerminalVolume.add(volumeDimTag)
                elif (
                    self.pancakeIndex % 2 == 0
                    and listOfDimTagsObjects[i].parentName == self.geo.terminals.inner.name
                ):
                    self.lastTerminalVolume.add(volumeDimTag)

        # Return the top surfaces:
        # Add the created top surfaces to a new dictionary:
        topSurfacesDimTags = extrusionResult.getExtrusionTop()
        topSurfaces = {}
        for i, topSurfaceDimTag in enumerate(topSurfacesDimTags):
            if listOfDimTagsObjects[i] in topSurfaces:
                topSurfaces[listOfDimTagsObjects[i]].append(topSurfaceDimTag)
            else:
                topSurfaces[listOfDimTagsObjects[i]] = [topSurfaceDimTag]

        return topSurfaces

    def generateGapAirWithFragment(
        self, gapAirSurfacesDimTags: List[List[Tuple[int, int]]]
    ):
        """
        A class to fill the gap between the multiple pancake coils with air. First, it
        creates a dummy cylinder with the same radius as the outer terminal's outer
        radius. Then using gapAirSurfacesDimTags, gmsh.model.occ.fragment() operation is
        applied to the dummy cylinder volume in a for loop to create the gap air
        volumes. After each fragment operation, one of the volumes created is removed
        because it is the solid volume which is the combination of windings,
        contact layers, and terminals. In the end, dummy cylinder is removed as well.


        WARNING:
        Currently, this method doesn't work.

        :param geometry: geometry information
        :param pancakeCoils: pancakeCoilsWithAir object
        :type pancakeCoils: pancakeCoilsWithAir
        """
        logger.info("Generating gap air has been started.")
        start_time = timeit.default_timer()

        # Create the dummy air volume:
        dummyAir = gmsh.model.occ.addCylinder(
            0,
            0,
            -self.geo.air.h / 2,
            0,
            0,
            self.geo.air.h,
            self.geo.terminals.outer.r,
        )

        toBeDeletedDimTags = []
        gapAirVolumesCurrentDimTags = []
        for i in range(len(gapAirSurfacesDimTags)):
            # Get the outer surfaces of the pancake coils for cutting the pancake coils
            # from the dummy air. The outer surfaces are used instead of pancake volumes
            # to reduce the amount of work for gmsh. It makes it significantly faster.
            # if len(gapAirSurfacesDimTags[i]) !=12:
            fragmentResults = gmsh.model.occ.fragment(
                [(3, dummyAir)],
                gapAirSurfacesDimTags[i],
                removeObject=False,
                removeTool=False,
            )
            fragmentVolumeResultsDimTags = fragmentResults[1][0]
            toBeDeletedDimTags.append(fragmentVolumeResultsDimTags[0])
            gapAirVolumesCurrentDimTags.append(fragmentVolumeResultsDimTags[1])

        toBeDeletedDimTags.append((3, dummyAir))
        # Fragmnet operation both creates the air volume and solid pancake coils volume
        # because the surfaces are used for cutting. Therefore, the solid pancake coils
        # volume should be removed from the fragment results:
        gmsh.model.occ.remove(toBeDeletedDimTags)

        # Add results to the air volume storage. After the geometry is saves as a .brep
        # file, and loaded back, the gaps between the tags are avoided by moving the
        # the other tags. Therefore, this is how the tags are stored:
        toBeDeletedTags = [dimTag[1] for dimTag in toBeDeletedDimTags]
        volumeTagsStart = min(toBeDeletedTags)
        numberOfGapAirVolumes = len(gapAirVolumesCurrentDimTags)
        gapAirVolumesToBeSaved = [
            (3, volumeTagsStart + i) for i in range(numberOfGapAirVolumes)
        ]

        # For debugging purposes, physical groups are being created in the geometry
        # generation process as well. Normally, it us done during meshing because BREP
        # files cannot store physical groups. Since the tags above (airVolumes) will be
        # valid after only saving the geometry as a BREP file and loading it back, the
        # current tags are given to the airVolume.add() method as well. This is done to
        # be able to create the correct physical group.
        self.gapAirVolume.add(
            dimTagsList=gapAirVolumesToBeSaved,
            dimTagsListForPG=gapAirVolumesCurrentDimTags,
        )

        logger.info(
            "Generating gap air has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )


class Geometry(Base):
    """
    Main geometry class for Pancake3D.

    :param fdm: FiQuS data model
    :param geom_folder: folder where the geometry files are saved
    :type geom_folder: str
    :param mesh_folder: folder where the mesh files are saved
    :type mesh_folder: str
    :param solution_folder: folder where the solution files are saved
    :type solution_folder: str
    """

    def __init__(
        self,
        fdm,
        geom_folder,
        mesh_folder,
        solution_folder,
    ) -> None:
        super().__init__(fdm, geom_folder, mesh_folder, solution_folder)

        # Clear if there is any existing dimTags storage:
        dimTagsStorage.clear()

        # Start GMSH:
        self.gu = GmshUtils(self.geom_folder)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

        # To speed up the GUI:
        gmsh.option.setNumber("Geometry.NumSubEdges", 10)

        # To see the surfaces in a better way in GUI:
        gmsh.option.setNumber("Geometry.SurfaceType", 1)

        # To avoid any unwanted modifications to the geometry, the automatic fixing of
        # the geometry is disabled:
        gmsh.option.setNumber("Geometry.OCCAutoFix", 0)

        # Set the tolerance:
        if self.geo.dimensionTolerance < gmsh.option.getNumber("Geometry.Tolerance"):
            gmsh.option.setNumber("Geometry.Tolerance", self.geo.dimensionTolerance)

        gmsh.option.setNumber("Geometry.ToleranceBoolean", self.geo.dimensionTolerance)

        spiralCurve.sectionsPerTurn = self.geo.winding.spt
        spiralCurve.curvesPerTurn = self.geo.winding.numberOfVolumesPerTurn

    def generate_geometry(self):
        """
        Generates geometry and saves it as a .brep file.


        """
        logger.info(
            f"Generating Pancake3D geometry ({self.brep_file}) has been started."
        )
        start_time = timeit.default_timer()

        self.pancakeCoil = pancakeCoilsWithAir(self.geo, self.mesh)

        gmsh.model.occ.synchronize()
        gmsh.write(self.brep_file)

        logger.info(
            f"Generating Pancake3D geometry ({self.brep_file}) has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )

    def load_geometry(self):
        """
        Loads geometry from .brep file.
        """
        logger.info("Loading Pancake3D geometry has been started.")
        start_time = timeit.default_timer()

        previousGeo = FilesAndFolders.read_data_from_yaml(
            self.geometry_data_file, Pancake3DGeometry
        )

        if previousGeo.model_dump() != self.geo.model_dump():
            raise ValueError(
                "Geometry data has been changed. Please regenerate the geometry or load"
                " the previous geometry data."
            )

        gmsh.clear()
        gmsh.model.occ.importShapes(self.brep_file, format="brep")
        gmsh.model.occ.synchronize()

        logger.info(
            "Loading Pancake3D geometry has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )

    def generate_vi_file(self):
        """
        Generates volume information file. Volume information file stores dimTags of all
        the stored volumes in the geometry. Without this file, regions couldn't be
        created, meaning that finite element simulation cannot be done.

        The file extension is custom because users are not supposed to edit or open this
        file, and it makes it intuitively clear that it is a volume information file.
        """
        logger.info(
            f"Generating volume information file ({self.vi_file}) has been started."
        )
        start_time = timeit.default_timer()

        dimTagsDict = dimTagsStorage.getDimTagsDict()
        json.dump(
            dimTagsDict,
            open(self.vi_file, "w"),
        )

        logger.info(
            "Generating volume information file has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )

        if self.geo_gui:
            self.generate_physical_groups()
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()

    @staticmethod
    def generate_physical_groups():
        """
        Generates physical groups. Physical groups are not saved in the BREP file but
        it can be useful for debugging purposes.


        """
        gmsh.model.occ.synchronize()

        dimTagsDict = dimTagsStorage.getDimTagsDict(forPhysicalGroups=True)

        for key, value in dimTagsDict.items():
            tags = [dimTag[1] for dimTag in value]
            gmsh.model.addPhysicalGroup(
                3,
                tags,
                name=key,
            )

    @staticmethod
    def remove_all_duplicates():
        """
        Removes all the duplicates and then prints the entities that are created or
        removed during the operation. It prints the line number where the function is
        called as well. This function is helpful for debugging. Finding duplicates means
        there is a problem in geometry creation logic, and the meshes will not be
        conformal. It shouldn't be used in the final version of the code since removing
        duplicates is computationally expensive, and there shouldn't be duplicates at
        all.

        WARNING:
        This function currently does not work properly. It is not recommended to use
        right now. It finds duplicates even if there are no duplicates (topology
        problems).
        """

        logger.info(f"Removing all the duplicates has been started.")
        start_time = timeit.default_timer()

        gmsh.model.occ.synchronize()
        oldEntities = []
        oldEntities.extend(gmsh.model.getEntities(3))
        oldEntities.extend(gmsh.model.getEntities(2))
        oldEntities.extend(gmsh.model.getEntities(1))
        oldEntities.extend(gmsh.model.getEntities(0))
        oldEntities = set(oldEntities)

        gmsh.model.occ.removeAllDuplicates()

        gmsh.model.occ.synchronize()
        newEntities = []
        newEntities.extend(gmsh.model.getEntities(3))
        newEntities.extend(gmsh.model.getEntities(2))
        newEntities.extend(gmsh.model.getEntities(1))
        newEntities.extend(gmsh.model.getEntities(0))
        newEntities = set(newEntities)
        NewlyCreated = newEntities - oldEntities
        Removed = oldEntities - newEntities

        frameinfo = getframeinfo(currentframe().f_back)

        if len(NewlyCreated) > 0 or len(Removed) > 0:
            logger.warning(f"Duplicates found! Line: {frameinfo.lineno}")
            logger.warning(f"{len(NewlyCreated)}NewlyCreated = {list(NewlyCreated)}")
            logger.warning(f"{len(Removed)}Removed = {list(Removed)}")
        else:
            logger.info(f"No duplicates found! Line: {frameinfo.lineno}")

        logger.info(
            "Removing all the duplicates has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )
