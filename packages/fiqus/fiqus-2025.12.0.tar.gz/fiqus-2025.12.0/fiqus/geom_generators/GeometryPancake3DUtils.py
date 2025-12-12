import math
from enum import Enum
from typing import List, Tuple, Dict

import os
import numpy as np
import gmsh
import copy

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from fiqus.parsers.ParserCOND import ParserCOND

class direction(Enum):
    """
    A class to specify direction easily.
    """

    ccw = 0
    cw = 1

class coordinate(Enum):
    """
    A class to specify coordinate types easily.
    """

    rectangular = 0
    cylindrical = 1
    spherical = 2

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



class spiralCurve:
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
        geo,
        direction=direction.ccw, # TODO code this to understand cw direction
        cutPlaneNormal=Tuple[float, float, float]
    ) -> None:
        spt = self.sectionsPerTurn  # just to make the code shorter
        self.turnRes = 1 / spt  # turn resolution
        cpt = self.curvesPerTurn  # just to make the code shorter
        self.turns = turns
        self.geo = geo
        # =============================================================================
        # GENERATING POINTS STARTS ====================================================
        # =============================================================================
        print('The theta is')
        print(initialTheta)

        print('This is the status of the cutPlane')
        print(cutPlaneNormal)
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

        for i in range(len(theta)-1): # range is reduced as no brick can be created starting at the last point
            # print(i)
            # Assuming theta is a numpy array and you're looking for the index of a value close to pi
            value_to_find = theta[i]+2*np.pi
            tolerance = 1e-10  # Define a small tolerance
            # Find indices where the condition is true
            indices = np.where(np.abs(theta - value_to_find) < tolerance)[0]
            z = self.geo.wi.h/2
            z_p = z
            z_n = -z

            if len(indices) > 0:
                windingUpIndex = indices[0]  # Take the first index if there are multiple matches

                try:
                    x_1 = r[i] * np.cos(theta[i])
                    y_1 = r[i] * np.sin(theta[i])
                    x_2 = r[i + 1] * np.cos(theta[i + 1])
                    y_2 = r[i + 1] * np.sin(theta[i + 1])
                    x_3 = r[windingUpIndex] * np.cos(theta[windingUpIndex])
                    y_3 = r[windingUpIndex] * np.sin(theta[windingUpIndex])
                    x_4 = r[windingUpIndex + 1] * np.cos(theta[windingUpIndex + 1])
                    y_4 = r[windingUpIndex + 1] * np.sin(theta[windingUpIndex + 1])

                    addPoints = [[x_1, y_1, z_n], [x_2, y_2, z_n], [x_4, y_4, z_n], [x_3, y_3, z_n], [x_1, y_1, z_p], [x_2, y_2, z_p], [x_4, y_4, z_p], [x_3, y_3, z_p]]

                    k = int(theta[i] / (2 * np.pi))

                    angle_in_current_turn = round(theta[i] % (2 * np.pi), 6)
                    angle_second_brick_point = round(theta[i+1] % (2 * np.pi), 6)

                    if (((round(angle_in_current_turn, 6) <= round(np.pi, 6)) or (round(angle_in_current_turn, 6) == round(2*np.pi, 6))) and (round(angle_second_brick_point, 6) <= round(np.pi, 6))):
                        k = int(round(theta[i] / (2 * np.pi)))
                        if k % 2 == 0:
                            winding_1.append(addPoints)
                        else:
                            winding_3.append(addPoints)

                    if (round(angle_in_current_turn, 6) >= round(np.pi, 6) and (round(angle_second_brick_point, 6) >= round(np.pi, 6) or round(angle_second_brick_point, 6) == 0.0)):

                        if k % 2 == 0:
                            winding_2.append(addPoints)
                        else:
                            winding_4.append(addPoints)

                except IndexError:
                    print('All of the winding conductor points have been found')

        x_coords = []
        y_coords = []
        z_coords = []

        # Writing the conductor file
        windingPointList = [winding_1, winding_2, winding_3, winding_4]

        if self.geo.conductorWrite:
            dict_cond_sample = {0: {'SHAPE': 'BR8', 'XCENTRE': '0.0', 'YCENTRE': '0.0', 'ZCENTRE': '0.0', 'PHI1': '0.0', 'THETA1': '0.0', 'PSI1': '0.0', 'XCEN2': '0.0', 'YCEN2': '0.0', 'ZCEN2': '0.0', 'THETA2': '0.0', 'PHI2': '0.0', 'PSI2': '0.0', 'XP1': '-0.879570', 'YP1': '-0.002940', 'ZP1': '-1.131209', 'XP2': '-0.879570', 'YP2': '0.002940', 'ZP2': '-1.131209', 'XP3': '-0.881381', 'YP3': '0.002940', 'ZP3': '-1.114205', 'XP4': '-0.881381', 'YP4': '-0.002940', 'ZP4': '-1.114205', 'XP5': '-0.861227', 'YP5': '-0.002972', 'ZP5': '-1.129183', 'XP6': '-0.861208', 'YP6': '0.002908', 'ZP6': '-1.129182', 'XP7': '-0.863294', 'YP7': '0.002912', 'ZP7': '-1.112210', 'XP8': '-0.863313', 'YP8': '-0.002968', 'ZP8': '-1.112211', 'CURD': '201264967.975494', 'SYMMETRY': '1', 'DRIVELABEL': 'drive 0', 'IRXY': '0', 'IRYZ': '0', 'IRZX': '0', 'TOLERANCE': '1e-6'}}

            # Use a dictionary to manage dict_cond_1, dict_cond_2, etc.
            dict_conds = {}

            k = 1  # Start from 1 for dict_cond_1, dict_cond_2, ...
            for winding in windingPointList:
                n = 0
                dict_conds[k] = {}
                for brick in winding:
                    dict_conds[k][n] = copy.deepcopy(dict_cond_sample[0])
                    for pointIndex in range(8):
                        dict_conds[k][n][f'XP{pointIndex + 1}'] = str(brick[pointIndex][0])
                        dict_conds[k][n][f'YP{pointIndex + 1}'] = str(brick[pointIndex][1])
                        dict_conds[k][n][f'ZP{pointIndex + 1}'] = str(brick[pointIndex][2])
                    n += 1
                k += 1

            target_dir = os.path.join(os.getcwd(), 'tests', '_outputs', 'parsers')

            # Ensure the target directory exists
            os.makedirs(target_dir, exist_ok=True)
            for i in range (1, 5):
                # Define the output file path
                out_file = os.path.join(target_dir, f'winding_{i}.cond')
                input_dict = dict_conds[i]
                list_of_shapes = ['BR8']
                for shape in list_of_shapes:
                        pc = ParserCOND()
                        print(f'the input dictionary is {input_dict}')
                        pc.write_cond(input_dict, out_file)

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

