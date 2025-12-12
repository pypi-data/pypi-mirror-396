import timeit
import json
import logging
import math
from enum import Enum
import operator
import itertools
import re

import gmsh
import scipy.integrate
import numpy as np

from fiqus.data import RegionsModelFiQuS
from fiqus.utils.Utils import GmshUtils
from fiqus.data.RegionsModelFiQuS import RegionsModel
from fiqus.mains.MainPancake3D import Base
from fiqus.utils.Utils import FilesAndFolders
from fiqus.data.DataFiQuSPancake3D import Pancake3DGeometry, Pancake3DMesh


logger = logging.getLogger(__name__)


class regionType(str, Enum):
    """
    A class to specify region type easily in the regions class.
    """

    powered = "powered"
    insulator = "insulator"
    air = "air"
    air_far_field = "air_far_field"


class entityType(str, Enum):
    """
    A class to specify entity type easily in the regions class.
    """

    vol = "vol"
    vol_in = "vol_in"
    vol_out = "vol_out"
    surf = "surf"
    surf_th = "surf_th"
    surf_in = "surf_in"
    surf_out = "surf_out"
    surf_ext = "surf_ext"
    cochain = "cochain"
    curve = "curve"
    point = "point"


class regions:
    """
    A class to generate physical groups in GMSH and create the corresponding regions
    file. The regions file is the file where the region tags are stored in the FiQuS
    regions data model convention. The file is used to template the *.pro file (GetDP
    input file).
    """

    def __init__(self):
        # Main types of entities:
        # The keys are the FiQuS region categories, and the values are the corresponding
        # GMSH entity type.
        self.entityMainType = {
            "vol": "vol",
            "vol_in": "vol",
            "vol_out": "vol",
            "surf": "surf",
            "surf_th": "surf",
            "surf_in": "surf",
            "surf_out": "surf",
            "surf_ext": "surf",
            "cochain": "curve",
            "curve": "curve",
            "point": "point",
        }

        # Dimensions of entity types:
        self.entityDim = {"vol": 3, "surf": 2, "curve": 1, "point": 0}

        # Keys for regions file. The keys are appended to the name of the regions
        # accordingly.
        self.entityKey = {
            "vol": "",
            "vol_in": "",
            "vol_out": "",
            "surf": "_bd",
            "surf_th": "_bd",
            "surf_in": "_in",
            "surf_out": "_out",
            "surf_ext": "_ext",
            "cochain": "_cut",
            "curve": "_curve",
            "point": "_point",
        }

        # FiQuS convetion for region numbers:
        self.regionTags = {
            "vol": 1000000,  # volume region tag start
            "surf": 2000000,  # surface region tag start
            "curve": 3000000,  # curve region tag start
            "point": 4000000,  # point region tag start
        }

        # Initialize the regions model:
        self.rm = RegionsModelFiQuS.RegionsModel()

        # This is used because self.rm.powered["Pancake3D"] is not initialized in
        # RegionsModelFiQuS.RegionsModel. It should be fixed in the future.
        self.rm.powered["Pancake3D"] = RegionsModelFiQuS.Powered()

        # Initializing the required variables (air and powered.vol_in and
        # powered.vol_out are not initialized because they are not lists but numbers):
        self.rm.powered["Pancake3D"].vol.names = []
        self.rm.powered["Pancake3D"].vol.numbers = []
        self.rm.powered["Pancake3D"].surf.names = []
        self.rm.powered["Pancake3D"].surf.numbers = []
        self.rm.powered["Pancake3D"].surf_th.names = []
        self.rm.powered["Pancake3D"].surf_th.numbers = []
        self.rm.powered["Pancake3D"].surf_in.names = []
        self.rm.powered["Pancake3D"].surf_in.numbers = []
        self.rm.powered["Pancake3D"].surf_out.names = []
        self.rm.powered["Pancake3D"].surf_out.numbers = []
        self.rm.powered["Pancake3D"].curve.names = []
        self.rm.powered["Pancake3D"].curve.numbers = []

        self.rm.insulator.vol.names = []
        self.rm.insulator.vol.numbers = []
        self.rm.insulator.surf.names = []
        self.rm.insulator.surf.numbers = []
        self.rm.insulator.curve.names = []
        self.rm.insulator.curve.numbers = []

        self.rm.air_far_field.vol.names = []
        self.rm.air_far_field.vol.numbers = []

        self.rm.air.cochain.names = []
        self.rm.air.cochain.numbers = []
        self.rm.air.point.names = []
        self.rm.air.point.numbers = []

    def addEntities(
        self, name, entityTags, regionType: regionType, entityType: entityType
    ):
        """
        Add entities as a physical group in GMSH and add the corresponding region to the
        regions file data.

        :param name: Name of the region (entityKey will be appended).
        :type name: str
        :param entityTags: Tags of the entities to be added as a physical group.
        :type entityTags: list of integers (tags)
        :param regionType: Type of the region. regionType class should be used.
        :type regionType: regionType
        :param entityType: Type of the entity. entityType class should be used.
        :type entityType: entityType
        """
        if not isinstance(entityTags, list):
            entityTags = [entityTags]

        name = name + self.entityKey[entityType]
        mainType = self.entityMainType[entityType]
        dim = self.entityDim[mainType]
        regionTag = self.regionTags[mainType]

        if regionType is regionType.powered:
            if entityType is entityType.vol_in or entityType is entityType.vol_out:
                getattr(self.rm.powered["Pancake3D"], entityType).name = name
                getattr(self.rm.powered["Pancake3D"], entityType).number = regionTag

            else:
                getattr(self.rm.powered["Pancake3D"], entityType).names.append(name)
                getattr(self.rm.powered["Pancake3D"], entityType).numbers.append(
                    regionTag
                )
        elif regionType is regionType.insulator:
            getattr(self.rm.insulator, entityType).names.append(name)
            getattr(self.rm.insulator, entityType).numbers.append(regionTag)
        elif regionType is regionType.air:
            if entityType is entityType.cochain or entityType is entityType.point:
                getattr(self.rm.air, entityType).names.append(name)
                getattr(self.rm.air, entityType).numbers.append(regionTag)
            else:
                getattr(self.rm.air, entityType).name = name
                getattr(self.rm.air, entityType).number = regionTag
        elif regionType is regionType.air_far_field:
            getattr(self.rm.air_far_field, entityType).names.append(name)
            getattr(self.rm.air_far_field, entityType).numbers.append(regionTag)

        gmsh.model.addPhysicalGroup(dim=dim, tags=entityTags, tag=regionTag, name=name)
        self.regionTags[mainType] = self.regionTags[mainType] + 1

    def generateRegionsFile(self, filename):
        """
        Generate the regions file from the final data.

        :param filename: Name of the regions file (with extension).
        :type filename: str
        """
        FilesAndFolders.write_data_to_yaml(filename, self.rm.model_dump())


class curveType(Enum):
    """
    A class to specify curve type easily in the windingCurve class.
    """

    axial = 0
    horizontal = 1
    spiralArc = 2
    circle = 3


class curve:
    """
    Even though volume tags can be stored in a volume information file and can be used
    after reading the BREP (geometry) file, surface tags and line tags cannot be stored
    because their tags will be changed. However, we need to know which line is which to
    create a proper mesh. For example, we would like to know which lines are on the XY
    plane, which lines are straight, which lines are spirals, etc.

    This class is created for recognizing lines of winding, contact layer, and top/bottom
    air volumes (because they are extrusions of winding and contact layer). Line tags of
    the volumes can be easily accessed with gmsh.model.getBoundary() function. Then a
    line tag can be used to create an instance of this object. The class will analyze
    the line's start and end points and decide if it's a spiral, axial, or horizontal
    curve. Then, it calculates the length of the line. This information is required to
    create a structured mesh for winding, contact layer, and top/bottom air volumes.

    Every windingCurve object is a line that stores the line's type and length.

    :param tag: Tag of the line.
    :type tag: int
    :param geometryData: Geometry data object.
    """

    def __init__(self, tag, geometryData):
        self.geo = geometryData

        self.tag = tag

        pointDimTags = gmsh.model.getBoundary(
            [(1, self.tag)], oriented=False, combined=True
        )
        self.pointTags = [dimTag[1] for dimTag in pointDimTags]

        # Get the positions of the points:
        self.points = []
        for tag in self.pointTags:
            boundingbox1 = gmsh.model.occ.getBoundingBox(0, tag)[:3]
            boundingbox2 = gmsh.model.occ.getBoundingBox(0, tag)[3:]
            boundingbox = list(map(operator.add, boundingbox1, boundingbox2))
            self.points.append(list(map(operator.truediv, boundingbox, (2, 2, 2))))

        # Round the point positions to the nearest multiple of self.geo.dimensionTolerance to avoid
        # numerical errors:
        for i in range(len(self.points)):
            for coord in range(3):
                self.points[i][coord] = (
                    round(self.points[i][coord] / self.geo.dimensionTolerance) * self.geo.dimensionTolerance
                )

        if self.isCircle():
            self.type = curveType.circle
            # The length of the circle curves are not used.

        elif self.isAxial():
            self.type = curveType.axial

            self.length = abs(self.points[0][2] - self.points[1][2])

        elif self.isHorizontal():
            self.type = curveType.horizontal

            self.length = math.sqrt(
                (self.points[0][0] - self.points[1][0]) ** 2
                + (self.points[0][1] - self.points[1][1]) ** 2
            )

        else:
            # If the curve is not axial or horizontal, it is a spiral curve:
            self.type = curveType.spiralArc

            # First point:
            r1 = math.sqrt(self.points[0][0] ** 2 + self.points[0][1] ** 2)
            theta1 = math.atan2(self.points[0][1], self.points[0][0])

            # Second point:
            r2 = math.sqrt(self.points[1][0] ** 2 + self.points[1][1] ** 2)
            theta2 = math.atan2(self.points[1][1], self.points[1][0])

            # Calculate the length of the spiral curve with numerical integration:
            self.length = curve.calculateSpiralArcLength(r1, r2, theta1, theta2)

            # Calculate starting turn number (n1, float) and ending turn number (n2,
            # float): (note that they are float modulos of 1, and not the exact turn
            # numbers)
            self.n1 = (theta1 - self.geo.winding.theta_i) / 2 / math.pi
            self.n1 = round(self.n1 / self.geo.winding.turnTol) * self.geo.winding.turnTol

            self.n2 = (theta2 - self.geo.winding.theta_i) / 2 / math.pi
            self.n2 = round(self.n2 / self.geo.winding.turnTol) * self.geo.winding.turnTol

    def isAxial(self):
        """
        Checks if the curve is an axial curve. It does so by comparing the z-coordinates
        of its starting and end points.

        :return: True if the curve is axial, False otherwise.
        :rtype: bool
        """
        return not math.isclose(
            self.points[0][2], self.points[1][2], abs_tol=self.geo.dimensionTolerance
        )

    def isHorizontal(self):
        """
        Checks if the curve is a horizontal curve. It does so by comparing the center of
        mass of the line and the average of the points' x and y coordinates. Having an
        equal z-coordinate for both starting point and ending point is not enough since
        spiral curves are on the horizontal plane as well.

        :return: True if the curve is horizontal, False otherwise.
        :rtype: bool
        """
        cm = gmsh.model.occ.getCenterOfMass(1, self.tag)
        xcm = (self.points[0][0] + self.points[1][0]) / 2
        ycm = (self.points[0][1] + self.points[1][1]) / 2

        return math.isclose(cm[0], xcm, abs_tol=self.geo.dimensionTolerance) and math.isclose(
            cm[1], ycm, abs_tol=self.geo.dimensionTolerance
        )

    def isCircle(self):
        """
        Checks if the curve is a circle. Since combined is set to True in
        gmsh.model.getBoundary() function, the function won't return any points for
        circle curves.
        """
        if len(self.points) == 0:
            return True
        else:
            return False

    @staticmethod
    def calculateSpiralArcLength(r_1, r_2, theta_1, theta_2):
        r"""
        Numerically integrates the speed function of the spiral arc to calculate the
        length of the arc.

        In pancake coil design, spirals are cylindrical curves where the radius is
        linearly increasing with theta. The parametric equation of a spiral sitting on
        an XY plane can be given as follows:

        $$
        \\theta = t
        $$

        $$
        r = a t + b
        $$

        $$
        z = c
        $$

        where $a$, $b$, and $c$ are constants and $t$ is any real number on a given set.

        How to calculate arc length?

        The same spiral curve can be specified with a position vector in cylindrical
        coordinates:

        $$
        \\text{position vector} = \\vec{r} = r \\vec{u}_r
        $$

        where $\\vec{u}_r$ is a unit vector that points towards the point.

        Taking the derivative of the $\\vec{r}$ with respect to $t$ would give the
        $\\text{velocity vector}$ ($\\vec{v}$) (note that both $\\vec{u}_r$ and
        $\\vec{r}$ change with time, product rule needs to be used):

        $$
        \\text{velocity vector} = \\vec{\\dot{r}} = \\dot{r} \\vec{u}_r + (r \\dot{\\theta}) \\vec{u}_\\theta
        $$

        where $\\vec{\\dot{r}}$ and $\\dot{\\theta}$ are the derivatives of $r$ and
        $\\theta$ with respect to $t$, and $\\vec{u}_\\theta$ is a unit vector that is
        vertical to $\\vec{u}_r$ and points to the positive angle side.

        The magnitude of the $\\vec{\\dot{r}}$ would result in speed. Speed's
        integration with respect to time gives the arc length. The $\\theta$ and $r$ are
        already specified above with the parametric equations. The only part left is
        finding the $a$ and $b$ constants used in the parametric equations. Because TSA
        and non-TSA spirals are a little different, the easiest way would be to
        calculate them with a given two points on spirals, which are end and starts
        points. The rest of the code is self-explanatory.

        :param r_1: radial position of the starting point
        :type r_1: float
        :param r_2: radial position of the ending point
        :type r_2: float
        :param theta_1: angular position of the starting point
        :type theta_1: float
        :param theta_2: angular position of the ending point
        :type theta_2: float
        :return: length of the spiral arc
        :rtype: float
        """
        # The same angle can be subtracted from both theta_1 and theta_2 to simplify the
        # calculations:
        theta2 = theta_2 - theta_1
        theta1 = 0

        # Since r = a * theta + b, r_1 = b since theta_1 = 0:
        b = r_1

        # Since r = a * theta + b, r_2 = a * theta2 + b:
        a = (r_2 - b) / theta2

        def integrand(t):
            return math.sqrt(a**2 + (a * t + b) ** 2)

        return abs(scipy.integrate.quad(integrand, theta1, theta2)[0])


alreadyMeshedSurfaceTags = []


class Mesh(Base):
    """
    Main mesh class for Pancake3D.

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

        # Read volume information file:
        with open(self.vi_file, "r") as f:
            self.dimTags = json.load(f)

        for key, value in self.dimTags.items():
            self.dimTags[key] = [tuple(dimTag) for dimTag in value]

        # Start GMSH:
        self.gu = GmshUtils(self.mesh_folder)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

        self.contactLayerAndWindingRadialLines = []  # Store for strucured terminals

    def generate_mesh(self):
        """
        Sets the mesh settings and generates the mesh.


        """
        logger.info("Generating Pancake3D mesh has been started.")

        start_time = timeit.default_timer()

        # =============================================================================
        # MESHING WINDING AND CONTACT LAYER STARTS =======================================
        # =============================================================================
        allWindingAndCLSurfaceTags = []
        allWindingAndCLLineTags = []
        for i in range(self.geo.numberOfPancakes):
            # Get the volume tags:
            windingVolumeDimTags = self.dimTags[self.geo.winding.name + str(i + 1)]
            windingVolumeTags = [dimTag[1] for dimTag in windingVolumeDimTags]

            contactLayerVolumeDimTags = self.dimTags[self.geo.contactLayer.name + str(i + 1)]
            contactLayerVolumeTags = [dimTag[1] for dimTag in contactLayerVolumeDimTags]

            # Get the surface and line tags:
            windingSurfaceTags, windingLineTags = self.get_boundaries(
                windingVolumeDimTags, returnTags=True
            )
            allWindingAndCLSurfaceTags.extend(windingSurfaceTags)
            allWindingAndCLLineTags.extend(windingLineTags)
            contactLayerSurfaceTags, contactLayerLineTags = self.get_boundaries(
                contactLayerVolumeDimTags, returnTags=True
            )
            allWindingAndCLSurfaceTags.extend(contactLayerSurfaceTags)
            allWindingAndCLLineTags.extend(contactLayerLineTags)

            self.structure_mesh(
                windingVolumeTags,
                windingSurfaceTags,
                windingLineTags,
                contactLayerVolumeTags,
                contactLayerSurfaceTags,
                contactLayerLineTags,
                meshSettingIndex=i,
            )

        notchVolumesDimTags = (
            self.dimTags["innerTransitionNotch"] + self.dimTags["outerTransitionNotch"]
        )
        notchVolumeTags = [dimTag[1] for dimTag in notchVolumesDimTags]

        notchSurfaceTags, notchLineTags = self.get_boundaries(
            notchVolumesDimTags, returnTags=True
        )

        for lineTag in notchLineTags:
            if lineTag not in allWindingAndCLLineTags:
                gmsh.model.mesh.setTransfiniteCurve(lineTag, 1)

        recombine = self.mesh.winding.elementType[0] in ["hexahedron", "prism"]
        for surfaceTag in notchSurfaceTags:
            if surfaceTag not in allWindingAndCLSurfaceTags:
                gmsh.model.mesh.setTransfiniteSurface(surfaceTag)
                if recombine:
                    normal = gmsh.model.getNormal(surfaceTag, [0.5, 0.5])
                    if abs(normal[2]) > 1e-4:
                        pass
                    else:
                        gmsh.model.mesh.setRecombine(2, surfaceTag)
                    

        for volumeTag in notchVolumeTags:
            gmsh.model.mesh.setTransfiniteVolume(volumeTag)

        # =============================================================================
        # MESHING WINDING AND CONTACT LAYER ENDS =========================================
        # =============================================================================

        # =============================================================================
        # MESHING AIR STARTS ==========================================================
        # =============================================================================
        # Winding and contact layer extrusions of the air:
        # Get the volume tags:
        airTopWindingExtrusionVolumeDimTags = self.dimTags[
            self.geo.air.name + "-TopPancakeWindingExtursion"
        ]

        airTopContactLayerExtrusionVolumeDimTags = self.dimTags[
            self.geo.air.name + "-TopPancakeContactLayerExtursion"
        ]

        airTopTerminalsExtrusionVolumeDimTags = self.dimTags[
            self.geo.air.name + "-TopTerminalsExtrusion"
        ]

        airBottomWindingExtrusionVolumeDimTags = self.dimTags[
            self.geo.air.name + "-BottomPancakeWindingExtursion"
        ]

        airBottomContactLayerExtrusionVolumeDimTags = self.dimTags[
            self.geo.air.name + "-BottomPancakeContactLayerExtursion"
        ]

        airBottomTerminalsExtrusionVolumeDimTags = self.dimTags[
            self.geo.air.name + "-BottomTerminalsExtrusion"
        ]

        removedAirVolumeDimTags = []
        newAirVolumeDimTags = []
        if self.mesh.air.structured:
            # Then it means air type is cuboid!
            airTopWindingExtrusionVolumeTags = [
                dimTag[1] for dimTag in airTopWindingExtrusionVolumeDimTags
            ]
            airTopContactLayerExtrusionVolumeTags = [
                dimTag[1] for dimTag in airTopContactLayerExtrusionVolumeDimTags
            ]
            airBottomWindingExtrusionVolumeTags = [
                dimTag[1] for dimTag in airBottomWindingExtrusionVolumeDimTags
            ]
            airBottomContactLayerExtrusionVolumeTags = [
                dimTag[1] for dimTag in airBottomContactLayerExtrusionVolumeDimTags
            ]

            # Calcualte axial number of elements for air:
            axialElementsPerLengthForWinding = min(self.mesh.winding.axialNumberOfElements) / self.geo.winding.height
            axneForAir = round(
                axialElementsPerLengthForWinding * self.geo.air.axialMargin + 1e-6
            )

            # Get the surface and line tags:
            (
                airTopWindingExtrusionSurfaceTags,
                airTopWindingExtrusionLineTags,
            ) = self.get_boundaries(
                airTopWindingExtrusionVolumeDimTags, returnTags=True
            )
            (
                airTopContactLayerExtrusionSurfaceTags,
                airTopContactLayerExtrusionLineTags,
            ) = self.get_boundaries(
                airTopContactLayerExtrusionVolumeDimTags, returnTags=True
            )

            self.structure_mesh(
                airTopWindingExtrusionVolumeTags,
                airTopWindingExtrusionSurfaceTags,
                airTopWindingExtrusionLineTags,
                airTopContactLayerExtrusionVolumeTags,
                airTopContactLayerExtrusionSurfaceTags,
                airTopContactLayerExtrusionLineTags,
                meshSettingIndex=self.geo.numberOfPancakes - 1,  # The last pancake coil
                axialNumberOfElements=axneForAir,
                bumpCoefficient=1,
            )

            # Get the surface and line tags:
            (
                airBottomWindingExtrusionSurfaceTags,
                airBottomWindingExtrusionLineTags,
            ) = self.get_boundaries(
                airBottomWindingExtrusionVolumeDimTags, returnTags=True
            )
            (
                airBottomContactLayerExtrusionSurfaceTags,
                airBottomContactLayerExtrusionLineTags,
            ) = self.get_boundaries(
                airBottomContactLayerExtrusionVolumeDimTags, returnTags=True
            )

            self.structure_mesh(
                airBottomWindingExtrusionVolumeTags,
                airBottomWindingExtrusionSurfaceTags,
                airBottomWindingExtrusionLineTags,
                airBottomContactLayerExtrusionVolumeTags,
                airBottomContactLayerExtrusionSurfaceTags,
                airBottomContactLayerExtrusionLineTags,
                meshSettingIndex=0,  # The first pancake coil
                axialNumberOfElements=axneForAir,
                bumpCoefficient=1,
            )

            # Structure tubes of the air:
            airOuterTubeVolumeDimTags = self.dimTags[self.geo.air.name + "-OuterTube"]
            airOuterTubeVolumeTags = [dimTag[1] for dimTag in airOuterTubeVolumeDimTags]

            airTopTubeTerminalsVolumeDimTags = self.dimTags[
                self.geo.air.name + "-TopTubeTerminalsExtrusion"
            ]
            airTopTubeTerminalsVolumeTags = [
                dimTag[1] for dimTag in airTopTubeTerminalsVolumeDimTags
            ]

            airBottomTubeTerminalsVolumeDimTags = self.dimTags[
                self.geo.air.name + "-BottomTubeTerminalsExtrusion"
            ]
            airBottomTubeTerminalsVolumeTags = [
                dimTag[1] for dimTag in airBottomTubeTerminalsVolumeDimTags
            ]

            # Structure inner cylinder of the air:
            airInnerCylinderVolumeDimTags = self.dimTags[
                self.geo.air.name + "-InnerCylinder"
            ]
            airInnerCylinderVolumeTags = [
                dimTag[1] for dimTag in airInnerCylinderVolumeDimTags
            ]

            airTubesAndCylinders = airOuterTubeVolumeTags + airInnerCylinderVolumeTags

            if self.geo.air.shellTransformation:
                shellVolumes = self.dimTags[self.geo.air.shellVolumeName]
                shellVolumeTags = [dimTag[1] for dimTag in shellVolumes]
                airTubesAndCylinders.extend(shellVolumeTags)

            airRadialElementMultiplier = 1 / self.mesh.air.radialElementSize
            self.structure_tubes_and_cylinders(
                airTubesAndCylinders,
                radialElementMultiplier=airRadialElementMultiplier,
            )

            if self.mesh.terminals.structured:
                terminalsRadialElementMultiplier = 1 / self.mesh.terminals.radialElementSize

                self.structure_tubes_and_cylinders(
                    airTopTubeTerminalsVolumeTags + airBottomTubeTerminalsVolumeTags,
                    radialElementMultiplier=terminalsRadialElementMultiplier,
                )

                airTopTouchingTerminalsVolumeDimTags = list(
                    set(airTopTerminalsExtrusionVolumeDimTags)
                    - set(airTopTubeTerminalsVolumeDimTags)
                )
                airTopTouchingTerminalsVolumeTags = [
                    dimTag[1] for dimTag in airTopTouchingTerminalsVolumeDimTags
                ]

                airBottomTouchingTerminalsVolumeDimTags = list(
                    set(airBottomTerminalsExtrusionVolumeDimTags)
                    - set(airBottomTubeTerminalsVolumeDimTags)
                )
                airBottomTouchingTerminalsVolumeTags = [
                    dimTag[1] for dimTag in airBottomTouchingTerminalsVolumeDimTags
                ]

                self.structure_tubes_and_cylinders(
                    airTopTouchingTerminalsVolumeTags
                    + airBottomTouchingTerminalsVolumeTags,
                    terminalNonTubeParts=True,
                    radialElementMultiplier=terminalsRadialElementMultiplier,
                )

        else:
            # Fuse top volumes:
            airTopVolumeDimTags = (
                airTopWindingExtrusionVolumeDimTags
                + airTopContactLayerExtrusionVolumeDimTags
                + airTopTerminalsExtrusionVolumeDimTags
            )
            airTopVolumeDimTag = Mesh.fuse_volumes(
                airTopVolumeDimTags,
                fuseSurfaces=True,
                fusedSurfacesArePlane=True,
            )
            newAirVolumeDimTags.append(airTopVolumeDimTag)
            removedAirVolumeDimTags.extend(airTopVolumeDimTags)

            # Fuse bottom volumes:
            airBottomVolumeDimTags = (
                airBottomWindingExtrusionVolumeDimTags
                + airBottomContactLayerExtrusionVolumeDimTags
                + airBottomTerminalsExtrusionVolumeDimTags
            )
            airBottomVolumeDimTag = Mesh.fuse_volumes(
                airBottomVolumeDimTags,
                fuseSurfaces=True,
                fusedSurfacesArePlane=True,
            )
            newAirVolumeDimTags.append(airBottomVolumeDimTag)
            removedAirVolumeDimTags.extend(airBottomVolumeDimTags)

            # Fuse inner cylinder and outer tube part of air:
            airInnerCylinderVolumeDimTags = self.dimTags[
                self.geo.air.name + "-InnerCylinder"
            ]
            if self.geo.numberOfPancakes > 1:
                # Fuse the first two and the last two volumes separately (due to cuts):
                firstTwoVolumes = airInnerCylinderVolumeDimTags[0:2]
                lastTwoVolumes = airInnerCylinderVolumeDimTags[-2:]
                airInnerCylinderVolumeDimTags = airInnerCylinderVolumeDimTags[2:-2]
                airInnerCylinderVolumeDimTag = Mesh.fuse_volumes(
                    airInnerCylinderVolumeDimTags, fuseSurfaces=False
                )
                airInnerCylinderVolumeDimTagFirst = Mesh.fuse_volumes(
                    firstTwoVolumes,
                    fuseSurfaces=False,
                )
                airInnerCylinderVolumeDimTagLast = Mesh.fuse_volumes(
                    lastTwoVolumes,
                    fuseSurfaces=False,
                )
                newAirVolumeDimTags.append(airInnerCylinderVolumeDimTag)
                newAirVolumeDimTags.append(airInnerCylinderVolumeDimTagFirst)
                newAirVolumeDimTags.append(airInnerCylinderVolumeDimTagLast)
                removedAirVolumeDimTags.extend(
                    airInnerCylinderVolumeDimTags + firstTwoVolumes + lastTwoVolumes
                )
                self.dimTags[self.geo.air.name + "-InnerCylinder"] = [
                    airInnerCylinderVolumeDimTag,
                    airInnerCylinderVolumeDimTagFirst,
                    airInnerCylinderVolumeDimTagLast,
                ]
            else:
                pass
                # self.dimTags[self.geo.air.name + "-InnerCylinder"] = [
                #     self.dimTags[self.geo.air.name + "-InnerCylinder"][1],
                #     self.dimTags[self.geo.air.name + "-InnerCylinder"][0],
                #     self.dimTags[self.geo.air.name + "-InnerCylinder"][2],
                # ]

            airOuterTubeVolumeDimTags = self.dimTags[self.geo.air.name + "-OuterTube"]
            airOuterTubeVolumeDimTag = Mesh.fuse_volumes(
                airOuterTubeVolumeDimTags,
                fuseSurfaces=True,
                fusedSurfacesArePlane=False,
            )
            newAirOuterTubeVolumeDimTag = airOuterTubeVolumeDimTag
            removedAirVolumeDimTags.extend(airOuterTubeVolumeDimTags)
            self.dimTags[self.geo.air.name + "-OuterTube"] = [newAirOuterTubeVolumeDimTag]

            if self.geo.air.shellTransformation:
                # Fuse air shell volumes:
                if self.geo.air.type == "cylinder":
                    removedShellVolumeDimTags = []
                    shellVolumeDimTags = self.dimTags[self.geo.air.shellVolumeName]
                    shellVolumeDimTag = Mesh.fuse_volumes(
                        shellVolumeDimTags,
                        fuseSurfaces=True,
                        fusedSurfacesArePlane=False,
                    )
                    removedShellVolumeDimTags.extend(shellVolumeDimTags)
                    newShellVolumeDimTags = [shellVolumeDimTag]
                    for removedDimTag in removedShellVolumeDimTags:
                        self.dimTags[self.geo.air.shellVolumeName].remove(removedDimTag)
                elif self.geo.air.type == "cuboid":
                    # Unfortunately, surfaces cannot be combined for the cuboid type of air.
                    # However, it doesn't affect the mesh quality that much.
                    newShellVolumeDimTags = []

                    shellPart1VolumeDimTag = Mesh.fuse_volumes(
                        self.dimTags[self.geo.air.shellVolumeName + "-Part1"],
                        fuseSurfaces=False,
                    )
                    self.dimTags[self.geo.air.shellVolumeName + "-Part1"] = [
                        shellPart1VolumeDimTag
                    ]

                    shellPart2VolumeDimTag = Mesh.fuse_volumes(
                        self.dimTags[self.geo.air.shellVolumeName + "-Part2"],
                        fuseSurfaces=False,
                    )
                    self.dimTags[self.geo.air.shellVolumeName + "-Part2"] = [
                        shellPart2VolumeDimTag
                    ]

                    shellPart3VolumeDimTag = Mesh.fuse_volumes(
                        self.dimTags[self.geo.air.shellVolumeName + "-Part3"],
                        fuseSurfaces=False,
                    )
                    self.dimTags[self.geo.air.shellVolumeName + "-Part3"] = [
                        shellPart3VolumeDimTag
                    ]

                    shellPart4VolumeDimTag = Mesh.fuse_volumes(
                        self.dimTags[self.geo.air.shellVolumeName + "-Part4"],
                        fuseSurfaces=False,
                    )
                    self.dimTags[self.geo.air.shellVolumeName + "-Part4"] = [
                        shellPart4VolumeDimTag
                    ]

                # The problem is, shell volume and outer air tube volume has a common
                # surface and that surface should be combined as well for high quality mesh.
                # However, it can be only done for cylinder type of air for now.
                # Get the combined boundary surfaces:
                if self.geo.air.type == "cylinder":
                    (
                        newAirOuterTubeVolumeDimTag,
                        newShellVolumeDimTag,
                    ) = Mesh.fuse_common_surfaces_of_two_volumes(
                        [airOuterTubeVolumeDimTag],
                        newShellVolumeDimTags,
                        fuseOtherSurfaces=False,
                        surfacesArePlane=False,
                    )
                    self.dimTags[self.geo.air.name + "-OuterTube"] = [newAirOuterTubeVolumeDimTag]

                    airOuterTubeVolumeDimTag = newAirOuterTubeVolumeDimTag
                    self.dimTags[self.geo.air.shellVolumeName].append(
                        newShellVolumeDimTag
                    )

            newAirVolumeDimTags.append(newAirOuterTubeVolumeDimTag)

            # Update volume tags dictionary of air:
            self.dimTags[self.geo.air.name] = list(
                (
                    set(self.dimTags[self.geo.air.name]) - set(removedAirVolumeDimTags)
                ).union(set(newAirVolumeDimTags))
            )

        # ==============================================================================
        # MESHING AIR ENDS =============================================================
        # ==============================================================================

        # ==============================================================================
        # MESHING TERMINALS STARTS =====================================================
        # ==============================================================================
        if self.mesh.terminals.structured:
            # Structure tubes of the terminals:
            terminalOuterTubeVolumeDimTags = self.dimTags[self.geo.terminals.outer.name + "-Tube"]
            terminalOuterTubeVolumeTags = [
                dimTag[1] for dimTag in terminalOuterTubeVolumeDimTags
            ]
            terminalInnerTubeVolumeDimTags = self.dimTags[self.geo.terminals.inner.name + "-Tube"]
            terminalInnerTubeVolumeTags = [
                dimTag[1] for dimTag in terminalInnerTubeVolumeDimTags
            ]

            terminalsRadialElementMultiplier = 1 / self.mesh.terminals.radialElementSize
            self.structure_tubes_and_cylinders(
                terminalOuterTubeVolumeTags + terminalInnerTubeVolumeTags,
                radialElementMultiplier=terminalsRadialElementMultiplier,
            )

            # Structure nontube parts of the terminals:
            terminalOuterNonTubeVolumeDimTags = self.dimTags[
                self.geo.terminals.outer.name + "-Touching"
            ]
            terminalOuterNonTubeVolumeTags = [
                dimTag[1] for dimTag in terminalOuterNonTubeVolumeDimTags
            ]
            terminalInnerNonTubeVolumeDimTags = self.dimTags[
                self.geo.terminals.inner.name + "-Touching"
            ]
            terminalInnerNonTubeVolumeTags = [
                dimTag[1] for dimTag in terminalInnerNonTubeVolumeDimTags
            ]

            self.structure_tubes_and_cylinders(
                terminalInnerNonTubeVolumeTags + terminalOuterNonTubeVolumeTags,
                terminalNonTubeParts=True,
                radialElementMultiplier=terminalsRadialElementMultiplier,
            )
        # ==============================================================================
        # MESHING TERMINALS ENDS =======================================================
        # ==============================================================================

        # ==============================================================================
        # FIELD SETTINGS STARTS ========================================================
        # ==============================================================================

        # Mesh fields for the air:
        # Meshes will grow as they get further from the field surfaces:
        fieldSurfacesDimTags = gmsh.model.getBoundary(
            self.dimTags[self.geo.winding.name], oriented=False, combined=True
        )
        fieldSurfacesTags = [dimTag[1] for dimTag in fieldSurfacesDimTags]

        distanceField = gmsh.model.mesh.field.add("Distance")

        gmsh.model.mesh.field.setNumbers(
            distanceField,
            "SurfacesList",
            fieldSurfacesTags,
        )

        thresholdField = gmsh.model.mesh.field.add("Threshold")
        gmsh.model.mesh.field.setNumber(thresholdField, "InField", distanceField)
        gmsh.model.mesh.field.setNumber(thresholdField, "SizeMin", self.mesh.sizeMin)
        gmsh.model.mesh.field.setNumber(thresholdField, "SizeMax", self.mesh.sizeMax)
        gmsh.model.mesh.field.setNumber(
            thresholdField, "DistMin", self.mesh.startGrowingDistance
        )

        gmsh.model.mesh.field.setNumber(
            thresholdField, "DistMax", self.mesh.stopGrowingDistance
        )

        gmsh.model.mesh.field.setAsBackgroundMesh(thresholdField)

        # ==============================================================================
        # FIELD SETTINGS ENDS ==========================================================
        # ==============================================================================

        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)

        try:
            # Only print warnings and errors:
            # Don't print on terminal, because we will use logger:
            gmsh.option.setNumber("General.Terminal", 0)
            # Start logger:
            gmsh.logger.start()

            gmsh.option.setNumber("Mesh.Algorithm", 6)
            gmsh.option.setNumber("Mesh.Algorithm3D", 1)

            # Mesh:
            gmsh.model.mesh.generate()
            gmsh.model.mesh.optimize("Netgen")

            # Print the log:
            log = gmsh.logger.get()
            for line in log:
                if line.startswith("Info"):
                    logger.info(re.sub(r"Info:\s+", "", line))
                elif line.startswith("Warning"):
                    logger.warning(re.sub(r"Warning:\s+", "", line))

            gmsh.logger.stop()
        except:
            # Print the log:
            log = gmsh.logger.get()
            for line in log:
                if line.startswith("Info"):
                    logger.info(re.sub(r"Info:\s+", "", line))
                elif line.startswith("Warning"):
                    logger.warning(re.sub(r"Warning:\s+", "", line))
                elif line.startswith("Error"):
                    logger.error(re.sub(r"Error:\s+", "", line))

            gmsh.logger.stop()

            self.generate_regions()

            logger.error(
                "Meshing Pancake3D magnet has failed. Try to change"
                " minimumElementSize and maximumElementSize parameters."
            )
            raise

        # SICN not implemented in 1D!
        allElementsDim2 = list(gmsh.model.mesh.getElements(dim=2)[1][0])
        allElementsDim3 = list(gmsh.model.mesh.getElements(dim=3)[1][0])
        allElements = allElementsDim2 + allElementsDim3
        elementQualities = gmsh.model.mesh.getElementQualities(allElements)
        lowestQuality = min(elementQualities)
        averageQuality = sum(elementQualities) / len(elementQualities)
        NofLowQualityElements = len(
            [quality for quality in elementQualities if quality < 0.01]
        )
        NofIllElemets = len(
            [quality for quality in elementQualities if quality < 0.001]
        )

        logger.info(
            f"The lowest quality among the elements is {lowestQuality:.4f} (SICN). The"
            " number of elements with quality lower than 0.01 is"
            f" {NofLowQualityElements}."
        )

        if NofIllElemets > 0:
            logger.warning(
                f"There are {NofIllElemets} elements with quality lower than 0.001. Try"
                " to change minimumElementSize and maximumElementSize parameters."
            )

        # Create cuts:
        # This is required to make the air a simply connected domain. This is required
        # for the solution part. You can read more about Homology in GMSH documentation.
        airTags = [dimTag[1] for dimTag in self.dimTags[self.geo.air.name]]

        if self.geo.air.shellTransformation:
            shellTags = [
                dimTag[1] for dimTag in self.dimTags[self.geo.air.shellVolumeName]
            ]
            airTags.extend(shellTags)

        dummyAirRegion = gmsh.model.addPhysicalGroup(dim=3, tags=airTags)
        dummyAirRegionDimTag = (3, dummyAirRegion)

        innerCylinderTags = [self.dimTags[self.geo.air.name + "-InnerCylinder"][0][1]]
        gapTags = [dimTag[1] for dimTag in self.dimTags[self.geo.air.name + "-Gap"]]
        # Only remove every second gap:
        gapTags = gapTags[1::2]

        dummyAirRegionWithoutInnerCylinder = gmsh.model.addPhysicalGroup(
            dim=3, tags=list(set(airTags) - set(innerCylinderTags) - set(gapTags))
        )
        dummyAirRegionWithoutInnerCylinderDimTag = (
            3,
            dummyAirRegionWithoutInnerCylinder,
        )

        windingTags = [dimTag[1] for dimTag in self.dimTags[self.geo.winding.name]]
        dummyWindingRegion = gmsh.model.addPhysicalGroup(dim=3, tags=windingTags)
        dummyWindingRegionDimTag = (3, dummyWindingRegion)

        if self.geo.contactLayer.thinShellApproximation:
            # Find all the contact layer surfaces:
            allWindingDimTags = []
            for i in range(self.geo.numberOfPancakes):
                windingDimTags = self.dimTags[self.geo.winding.name + str(i + 1)]
                allWindingDimTags.extend(windingDimTags)

            windingBoundarySurfaces = gmsh.model.getBoundary(
                allWindingDimTags, combined=True, oriented=False
            )
            allWindingSurfaces = gmsh.model.getBoundary(
                allWindingDimTags, combined=False, oriented=False
            )

            contactLayerSurfacesDimTags = list(
                set(allWindingSurfaces) - set(windingBoundarySurfaces)
            )
            contactLayerTags = [dimTag[1] for dimTag in contactLayerSurfacesDimTags]

            # Get rid of non-contactLayer surfaces:
            realContactLayerTags = []
            for contactLayerTag in contactLayerTags:
                surfaceNormal = list(gmsh.model.getNormal(contactLayerTag, [0.5, 0.5]))
                centerOfMass = gmsh.model.occ.getCenterOfMass(2, contactLayerTag)

                if (
                    abs(
                        surfaceNormal[0] * centerOfMass[0]
                        + surfaceNormal[1] * centerOfMass[1]
                    )
                    > 1e-6
                ):
                    realContactLayerTags.append(contactLayerTag)

            # Get rid of surfaces that touch terminals:
            terminalSurfaces = gmsh.model.getBoundary(
                self.dimTags[self.geo.terminals.outer.name] + self.dimTags[self.geo.terminals.inner.name],
                combined=False,
                oriented=False,
            )
            terminalSurfaces = [dimTag[1] for dimTag in terminalSurfaces]
            finalContactLayerTags = [
                tag for tag in realContactLayerTags if tag not in terminalSurfaces
            ]

            dummyContactLayerRegion = gmsh.model.addPhysicalGroup(
                dim=2, tags=finalContactLayerTags
            )
            dummyContactLayerRegionDimTag = (2, dummyContactLayerRegion)

        else:
            contactLayerTags = [dimTag[1] for dimTag in self.dimTags[self.geo.contactLayer.name]]

            # get rid of volumes that touch terminals:
            terminalSurfaces = gmsh.model.getBoundary(
                self.dimTags[self.geo.terminals.outer.name] + self.dimTags[self.geo.terminals.inner.name],
                combined=False,
                oriented=False,
            )
            finalContactLayerTags = []
            for contactLayerTag in contactLayerTags:
                insulatorSurfaces = gmsh.model.getBoundary(
                    [(3, contactLayerTag)], combined=False, oriented=False
                )
                itTouchesTerminals = False
                for insulatorSurface in insulatorSurfaces:
                    if insulatorSurface in terminalSurfaces:
                        itTouchesTerminals = True
                        break

                if not itTouchesTerminals:
                    finalContactLayerTags.append(contactLayerTag)

            dummyContactLayerRegion = gmsh.model.addPhysicalGroup(
                dim=3, tags=finalContactLayerTags
            )
            dummyContactLayerRegionDimTag = (3, dummyContactLayerRegion)

        # First cohomology request (normal cut for NI coils):
        gmsh.model.mesh.addHomologyRequest(
            "Cohomology",
            domainTags=[dummyAirRegion],
            subdomainTags=[],
            dims=[1],
        )

        if self.mesh.computeCohomologyForInsulating:
            # Second cohomology request (insulated cut for insulated coils):
            if self.geo.numberOfPancakes > 1:
                gmsh.model.mesh.addHomologyRequest(
                    "Cohomology",
                    domainTags=[
                        dummyAirRegionWithoutInnerCylinder,
                        dummyContactLayerRegion,
                    ],
                    subdomainTags=[],
                    dims=[1],
                )
            else:
                gmsh.model.mesh.addHomologyRequest(
                    "Cohomology",
                    domainTags=[
                        dummyAirRegion,
                        dummyContactLayerRegion,
                    ],
                    subdomainTags=[],
                    dims=[1],
                )

            # Third cohomology request (for cuts between pancake coils):
            gmsh.model.mesh.addHomologyRequest(
                "Cohomology",
                domainTags=[
                    dummyAirRegion,
                    dummyContactLayerRegion,
                    dummyWindingRegion,
                ],
                subdomainTags=[],
                dims=[1],
            )

        # Start logger:
        gmsh.logger.start()

        cuts = gmsh.model.mesh.computeHomology()

        # Print the log:
        log = gmsh.logger.get()
        for line in log:
            if line.startswith("Info"):
                logger.info(re.sub(r"Info:\s+", "", line))
            elif line.startswith("Warning"):
                logger.warning(re.sub(r"Warning:\s+", "", line))
        gmsh.logger.stop()

        if self.geo.numberOfPancakes > 1:
            cutsDictionary = {
                "H^1{1}": self.geo.air.cutName,
                "H^1{1,4,3}": "CutsBetweenPancakes",
                "H^1{2,4}": "CutsForPerfectInsulation",
            }
        else:
            cutsDictionary = {
                "H^1{1}": self.geo.air.cutName,
                "H^1{1,4,3}": "CutsBetweenPancakes",
                "H^1{1,4}": "CutsForPerfectInsulation",
            }
        cutTags = [dimTag[1] for dimTag in cuts]
        cutEntities = []
        for tag in cutTags:
            name = gmsh.model.getPhysicalName(1, tag)
            cutEntities = list(gmsh.model.getEntitiesForPhysicalGroup(1, tag))
            cutEntitiesDimTags = [(1, cutEntity) for cutEntity in cutEntities]
            for key in cutsDictionary:
                if key in name:
                    if cutsDictionary[key] in self.dimTags:
                        self.dimTags[cutsDictionary[key]].extend(cutEntitiesDimTags)
                    else:
                        self.dimTags[cutsDictionary[key]] = cutEntitiesDimTags

        # Remove newly created physical groups because they will be created again in
        # generate_regions method.
        gmsh.model.removePhysicalGroups(
            [dummyContactLayerRegionDimTag]
            + [dummyAirRegionDimTag]
            + [dummyAirRegionWithoutInnerCylinderDimTag]
            + [dummyWindingRegionDimTag]
            + cuts
        )

        logger.info(
            "Generating Pancake3D mesh has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )

    def structure_mesh(
        self,
        windingVolumeTags,
        windingSurfaceTags,
        windingLineTags,
        contactLayerVolumeTags,
        contactLayerSurfaceTags,
        contactLayerLineTags,
        meshSettingIndex,
        axialNumberOfElements=None,
        bumpCoefficient=None,
    ):
        """
        Structures the winding and contact layer meshed depending on the user inputs. If
        the bottom and top part of the air is to be structured, the same method is used.

        :param windingVolumeTags: tags of the winding volumes
        :type windingVolumeTags: list[int]
        :param windingSurfaceTags: tags of the winding surfaces
        :type windingSurfaceTags: list[int]
        :param windingLineTags: tags of the winding lines
        :type windingLineTags: list[int]
        :param contactLayerVolumeTags: tags of the contact layer volumes
        :type contactLayerVolumeTags: list[int]
        :param contactLayerSurfaceTags: tags of the contact layer surfaces
        :type contactLayerSurfaceTags: list[int]
        :param contactLayerLineTags: tags of the contact layer lines
        :type contactLayerLineTags: list[int]
        :param meshSettingIndex: index of the mesh setting
        :type meshSettingIndex: int
        :param axialNumberOfElements: number of axial elements
        :type axialNumberOfElements: int, optional
        :param bumpCoefficient: bump coefficient for axial meshing
        :type bumpCoefficient: float, optional

        """
        # Transfinite settings:
        # Arc lenght of the innermost one turn of spiral:
        if self.geo.contactLayer.thinShellApproximation:
            oneTurnSpiralLength = curve.calculateSpiralArcLength(
                self.geo.winding.innerRadius,
                self.geo.winding.innerRadius
                + self.geo.winding.thickness
                + self.geo.contactLayer.thickness * (self.geo.numberOfPancakes - 1) / self.geo.numberOfPancakes,
                0,
                2 * math.pi,
            )
        else:
            oneTurnSpiralLength = curve.calculateSpiralArcLength(
                self.geo.winding.innerRadius,
                self.geo.winding.innerRadius + self.geo.winding.thickness,
                0,
                2 * math.pi,
            )

        # Arc length of one element:
        arcElementLength = oneTurnSpiralLength / self.mesh.winding.azimuthalNumberOfElementsPerTurn[meshSettingIndex]

        # Number of azimuthal elements per turn:
        arcNumElementsPerTurn = round(oneTurnSpiralLength / arcElementLength)

        # Make all the lines transfinite:
        for j, lineTags in enumerate([windingLineTags, contactLayerLineTags]):
            for lineTag in lineTags:
                lineObject = curve(lineTag, self.geo)

                if lineObject.type is curveType.horizontal:
                    # The curve is horizontal, so radialNumberOfElementsPerTurn entry is
                    # used.
                    if self.geo.contactLayer.thinShellApproximation:
                        numNodes = self.mesh.winding.radialNumberOfElementsPerTurn[meshSettingIndex] + 1

                    else:
                        if j == 0:
                            # This line is the winding's horizontal line:
                            numNodes = self.mesh.winding.radialNumberOfElementsPerTurn[meshSettingIndex] + 1

                        else:
                            # This line is the contact layer's horizontal line:
                            numNodes = self.mesh.contactLayer.radialNumberOfElementsPerTurn[meshSettingIndex] + 1

                    # Set transfinite curve:
                    self.contactLayerAndWindingRadialLines.append(lineTag)
                    gmsh.model.mesh.setTransfiniteCurve(lineTag, numNodes)

                elif lineObject.type is curveType.axial:
                    # The curve is axial, so axialNumberOfElements entry is used.
                    if axialNumberOfElements is None:
                        numNodes = self.mesh.winding.axialNumberOfElements[meshSettingIndex] + 1
                    else:
                        numNodes = axialNumberOfElements + 1

                    if bumpCoefficient is None:
                        bumpCoefficient = self.mesh.winding.axialDistributionCoefficient[meshSettingIndex]
                    gmsh.model.mesh.setTransfiniteCurve(
                        lineTag, numNodes, meshType="Bump", coef=bumpCoefficient
                    )

                else:
                    # The line is an arc, so the previously calculated arcNumElementsPerTurn
                    # is used. All the number of elements per turn must be the same
                    # independent of radial position. Otherwise, transfinite meshing cannot
                    # be performed. However, to support the float number of turns, number
                    # of nodes are being calculated depending on the start and end turns of
                    # the arc.d
                    lengthInTurns = abs(lineObject.n2 - lineObject.n1)
                    if lengthInTurns > 0.5:
                        # The arc can never be longer than half a turn.
                        lengthInTurns = 1 - lengthInTurns

                    lengthInTurns = (
                        round(lengthInTurns / self.geo.winding.turnTol) * self.geo.winding.turnTol
                    )

                    arcNumEl = round(arcNumElementsPerTurn * lengthInTurns)

                    arcNumNodes = int(arcNumEl + 1)

                    # Set transfinite curve:
                    gmsh.model.mesh.setTransfiniteCurve(lineTag, arcNumNodes)

        for j, surfTags in enumerate([windingSurfaceTags, contactLayerSurfaceTags]):
            for surfTag in surfTags:
                # Make all the surfaces transfinite:
                gmsh.model.mesh.setTransfiniteSurface(surfTag)

                if self.mesh.winding.elementType[meshSettingIndex] == "hexahedron":
                    # If the element type is hexahedron, recombine all the surfaces:
                    gmsh.model.mesh.setRecombine(2, surfTag)
                elif self.mesh.winding.elementType[meshSettingIndex] == "prism":
                    # If the element type is prism, recombine only the side surfaces:
                    surfaceNormal = list(gmsh.model.getNormal(surfTag, [0.5, 0.5]))
                    if abs(surfaceNormal[2]) < 1e-6:
                        gmsh.model.mesh.setRecombine(2, surfTag)

                # If the element type is tetrahedron, do not recombine any surface.

        for volTag in windingVolumeTags + contactLayerVolumeTags:
            # Make all the volumes transfinite:
            gmsh.model.mesh.setTransfiniteVolume(volTag)

    def structure_tubes_and_cylinders(
        self, volumeTags, terminalNonTubeParts=False, radialElementMultiplier=1
    ):
        # Number of azimuthal elements per quarter:
        arcNumElementsPerQuarter = int(self.mesh.winding.azimuthalNumberOfElementsPerTurn[0] / 4)
        radialNumberOfElementsPerLength = (
            self.mesh.winding.radialNumberOfElementsPerTurn[0] / self.geo.winding.thickness * radialElementMultiplier
        )

        surfacesDimTags = gmsh.model.getBoundary(
            [(3, tag) for tag in volumeTags], combined=False, oriented=False
        )
        surfacesTags = [dimTag[1] for dimTag in surfacesDimTags]
        surfacesTags = list(set(surfacesTags))

        curvesDimTags = gmsh.model.getBoundary(
            surfacesDimTags, combined=False, oriented=False
        )
        curvesTags = [dimTag[1] for dimTag in curvesDimTags]

        # Make all the lines transfinite:
        for curveTag in curvesTags:
            curveObject = curve(curveTag, self.geo)

            if curveObject.type is curveType.horizontal:
                # The curve is horizontal, so radialNumberOfElementsPerTurn entry is
                # used.

                # But, the curve might be a part of the transitionNotch.
                isTransitionNotch = False
                point2 = curveObject.points[1]
                point1 = curveObject.points[0]
                if (
                    abs(point2[0] - point1[0]) > 1e-5
                    and abs(point2[1] - point1[1]) > 1e-5
                ):
                    isTransitionNotch = True

                if isTransitionNotch:
                    gmsh.model.mesh.setTransfiniteCurve(curveTag, 2)
                else:
                    if terminalNonTubeParts:
                        if curveTag not in self.contactLayerAndWindingRadialLines:
                            numNodes = (
                                round(radialNumberOfElementsPerLength * self.geo.terminals.inner.thickness)
                                + 1
                            )
                            # Set transfinite curve:
                            gmsh.model.mesh.setTransfiniteCurve(curveTag, numNodes)
                    else:
                        numNodes = (
                            round(radialNumberOfElementsPerLength * curveObject.length)
                            + 1
                        )
                        # Set transfinite curve:
                        gmsh.model.mesh.setTransfiniteCurve(curveTag, numNodes)

            elif curveObject.type is curveType.axial:
                # The curve is axial, so axialNumberOfElements entry is used.
                if math.isclose(curveObject.length, self.geo.winding.height, rel_tol=1e-7):
                    numNodes = min(self.mesh.winding.axialNumberOfElements) + 1
                else:
                    axialElementsPerLength = min(self.mesh.winding.axialNumberOfElements) / self.geo.winding.height
                    numNodes = (
                        round(axialElementsPerLength * curveObject.length + 1e-6) + 1
                    )

                gmsh.model.mesh.setTransfiniteCurve(curveTag, numNodes)

            else:
                # The line is an arc
                lengthInTurns = abs(curveObject.n2 - curveObject.n1)
                if lengthInTurns > 0.5:
                    # The arc can never be longer than half a turn.
                    lengthInTurns = 1 - lengthInTurns

                lengthInTurns = (
                    round(lengthInTurns / self.geo.winding.turnTol) * self.geo.winding.turnTol
                )

                arcNumEl = round(arcNumElementsPerQuarter * 4 * lengthInTurns)

                arcNumNodes = int(arcNumEl + 1)

                # Set transfinite curve:

                gmsh.model.mesh.setTransfiniteCurve(curveTag, arcNumNodes)

        for surfaceTag in surfacesTags:
            # Make all the surfaces transfinite:

            if self.mesh.winding.elementType[0] == "hexahedron":
                # If the element type is hexahedron, recombine all the surfaces:
                gmsh.model.mesh.setRecombine(2, surfaceTag)
            elif self.mesh.winding.elementType[0] == "prism":
                # If the element type is prism, recombine only the side surfaces:
                surfaceNormal = list(gmsh.model.getNormal(surfaceTag, [0.5, 0.5]))
                if abs(surfaceNormal[2]) < 1e-5:
                    gmsh.model.mesh.setRecombine(2, surfaceTag)

            curves = gmsh.model.getBoundary(
                [(2, surfaceTag)], combined=False, oriented=False
            )
            numberOfCurves = len(curves)
            if terminalNonTubeParts:
                if numberOfCurves == 4:
                    numberOfHorizontalCurves = 0
                    for curveTag in curves:
                        curveObject = curve(curveTag[1], self.geo)
                        if curveObject.type is curveType.horizontal:
                            numberOfHorizontalCurves += 1

                    if numberOfHorizontalCurves == 3:
                        pass
                    else:
                        gmsh.model.mesh.setTransfiniteSurface(surfaceTag)

                elif numberOfCurves == 3:
                    pass
                else:
                    curves = gmsh.model.getBoundary(
                        [(2, surfaceTag)], combined=False, oriented=False
                    )
                    curveObjects = [curve(line[1], self.geo) for line in curves]

                    divisionCurves = []
                    for curveObject in curveObjects:
                        if curveObject.type is curveType.horizontal:
                            point1 = curveObject.points[0]
                            point2 = curveObject.points[1]
                            if not (
                                abs(point2[0] - point1[0]) > 1e-5
                                and abs(point2[1] - point1[1]) > 1e-5
                            ):
                                divisionCurves.append(curveObject)

                    cornerPoints = (
                        divisionCurves[0].pointTags + divisionCurves[1].pointTags
                    )

                    if surfaceTag not in alreadyMeshedSurfaceTags:
                        alreadyMeshedSurfaceTags.append(surfaceTag)
                        gmsh.model.mesh.setTransfiniteSurface(
                            surfaceTag, cornerTags=cornerPoints
                        )
            else:
                if numberOfCurves == 3:
                    # Then it is a pie, corner points should be adjusted:
                    originPointTag = None
                    curveObject1 = curve(curves[0][1], self.geo)
                    for point, tag in zip(curveObject1.points, curveObject1.pointTags):
                        if math.sqrt(point[0] ** 2 + point[1] ** 2) < 1e-6:
                            originPointTag = tag

                    if originPointTag is None:
                        curveObject2 = curve(curves[1][1], self.geo)
                        for point, tag in zip(
                            curveObject2.points, curveObject2.pointTags
                        ):
                            if math.sqrt(point[0] ** 2 + point[1] ** 2) < 1e-6:
                                originPointTag = tag

                    otherPointDimTags = gmsh.model.getBoundary(
                        [(2, surfaceTag)],
                        combined=False,
                        oriented=False,
                        recursive=True,
                    )
                    otherPointTags = [dimTag[1] for dimTag in otherPointDimTags]
                    otherPointTags.remove(originPointTag)
                    cornerTags = [originPointTag] + otherPointTags
                    gmsh.model.mesh.setTransfiniteSurface(
                        surfaceTag, cornerTags=cornerTags
                    )
                else:
                    gmsh.model.mesh.setTransfiniteSurface(surfaceTag)

        for volumeTag in volumeTags:
            if terminalNonTubeParts:
                surfaces = gmsh.model.getBoundary(
                    [(3, volumeTag)], combined=False, oriented=False
                )
                curves = gmsh.model.getBoundary(
                    surfaces, combined=False, oriented=False
                )
                curves = list(set(curves))

                if len(curves) == 12:
                    numberOfArcs = 0
                    for curveTag in curves:
                        curveObject = curve(curveTag[1], self.geo)
                        if curveObject.type is curveType.spiralArc:
                            numberOfArcs += 1
                    if numberOfArcs == 2:
                        pass
                    else:
                        gmsh.model.mesh.setTransfiniteVolume(volumeTag)
                # elif len(curves) == 15:
                #     divisionCurves = []
                #     for curveTag in curves:
                #         curveObject = curve(curveTag[1], self.geo)
                #         if curveObject.type is curveType.horizontal:
                #             point1 = curveObject.points[0]
                #             point2 = curveObject.points[1]
                #             if not (
                #                 abs(point2[0] - point1[0]) > 1e-5
                #                 and abs(point2[1] - point1[1]) > 1e-5
                #             ):
                #                 divisionCurves.append(curveObject)

                #     cornerPoints = (
                #         divisionCurves[0].pointTags
                #         + divisionCurves[1].pointTags
                #         + divisionCurves[2].pointTags
                #         + divisionCurves[3].pointTags
                #     )
                #     gmsh.model.mesh.setTransfiniteVolume(
                #         volumeTag, cornerTags=cornerPoints
                #     )
            else:
                # Make all the volumes transfinite:
                gmsh.model.mesh.setTransfiniteVolume(volumeTag)

    @staticmethod
    def get_boundaries(volumeDimTags, returnTags=False):
        """
        Returns all the surface and line dimTags or tags of a given list of volume
        dimTags.

        :param volumeDimTags: dimTags of the volumes
        :type volumeDimTags: list[tuple[int, int]]
        :param returnTags: if True, returns tags instead of dimTags
        :type returnTags: bool, optional
        :return: surface and line dimTags or tags
        :rtype: tuple[list[tuple[int, int]], list[tuple[int, int]]] or
            tuple[list[int], list[int]]
        """
        # Get the surface tags:
        surfaceDimTags = list(
            set(
                gmsh.model.getBoundary(
                    volumeDimTags,
                    combined=False,
                    oriented=False,
                    recursive=False,
                )
            )
        )

        # Get the line tags:
        lineDimTags = list(
            set(
                gmsh.model.getBoundary(
                    surfaceDimTags,
                    combined=False,
                    oriented=False,
                    recursive=False,
                )
            )
        )

        if returnTags:
            surfaceTags = [dimTag[1] for dimTag in surfaceDimTags]
            lineTags = [dimTag[1] for dimTag in lineDimTags]
            return surfaceTags, lineTags
        else:
            return surfaceDimTags, lineDimTags

    @staticmethod
    def fuse_volumes(volumeDimTags, fuseSurfaces=True, fusedSurfacesArePlane=False):
        """
        Fuses all the volumes in a given list of volume dimTags, removes old volumes,
        and returns the new volume dimTag. Also, if compundSurfacces is True, it fuses
        the surfaces that only belong to the volume. fusedSurfacesArePlane can be
        used to change the behavior of the fuse_surfaces method.

        :param volumeDimTags: dimTags of the volumes
        :type volumeDimTags: list[tuple[int, int]]
        :param fuseSurfaces: if True, fuses the surfaces that only belong to the
            volume
        :type fuseSurfaces: bool, optional
        :param fusedSurfacesArePlane: if True, fused surfaces are assumed to be
            plane, and fusion is performed accordingly
        :return: new volume's dimTag
        :rtype: tuple[int, int]
        """

        # Get the combined boundary surfaces:
        boundarySurfacesDimTags = gmsh.model.getBoundary(
            volumeDimTags,
            combined=True,
            oriented=False,
            recursive=False,
        )
        boundarSurfacesTags = [dimTag[1] for dimTag in boundarySurfacesDimTags]

        # Get all the boundary surfaces:
        allBoundarySurfacesDimTags = gmsh.model.getBoundary(
            volumeDimTags,
            combined=False,
            oriented=False,
            recursive=False,
        )

        # Find internal (common) surfaces:
        internalSurfacesDimTags = list(
            set(allBoundarySurfacesDimTags) - set(boundarySurfacesDimTags)
        )

        # Get the combined boundary lines:
        boundaryLinesDimTags = gmsh.model.getBoundary(
            allBoundarySurfacesDimTags,
            combined=True,
            oriented=False,
            recursive=False,
        )
        boundarLinesTags = [dimTag[1] for dimTag in boundaryLinesDimTags]

        # Get all the boundary lines:
        allBoundaryLinesDimTags = gmsh.model.getBoundary(
            allBoundarySurfacesDimTags,
            combined=False,
            oriented=False,
            recursive=False,
        )

        # Find internal (common) lines:
        internalLinesDimTags = list(
            set(allBoundaryLinesDimTags) - set(boundarLinesTags)
        )

        # Remove the old volumes:
        removedVolumeDimTags = volumeDimTags
        gmsh.model.occ.remove(removedVolumeDimTags, recursive=False)

        # Remove the internal surfaces:
        gmsh.model.occ.remove(internalSurfacesDimTags, recursive=False)

        # Remove the internal lines:
        gmsh.model.occ.remove(internalLinesDimTags, recursive=False)

        # Create a new single volume (even thought we don't use the new volume tag
        # directly, it is required for finding the surfaces that only belong to the
        # volume):
        surfaceLoop = gmsh.model.occ.addSurfaceLoop(boundarSurfacesTags, sewing=True)
        newVolumeTag = gmsh.model.occ.addVolume([surfaceLoop])
        newVolumeDimTag = (3, newVolumeTag)
        gmsh.model.occ.synchronize()

        if fuseSurfaces:
            newVolumeDimTag = Mesh.fuse_possible_surfaces_of_a_volume(
                (3, newVolumeTag), surfacesArePlane=fusedSurfacesArePlane
            )

        return newVolumeDimTag

    @staticmethod
    def fuse_common_surfaces_of_two_volumes(
        volume1DimTags, volume2DimTags, fuseOtherSurfaces=False, surfacesArePlane=False
    ):
        """
        Fuses common surfaces of two volumes. Volumes are given as a list of dimTags,
        but they are assumed to form a single volume, and this function fuses those
        multiple volumes into a single volume as well. If fuseOtherSurfaces is set to
        True, it tries to fuse surfaces that only belong to one volume too; however,
        that feature is not used in Pancake3D currently.

        :param volume1DimTags: dimTags of the first volume
        :type volume1DimTags: list[tuple[int, int]]
        :param volume2DimTags: dimTags of the second volume
        :type volume2DimTags: list[tuple[int, int]]
        :param fuseOtherSurfaces: if True, fuses the surfaces that only belong to one
            volume
        :type fuseOtherSurfaces: bool, optional
        :param surfacesArePlane: if True, fused surfaces are assumed to be plane, and
            fusion is performed accordingly
        :type surfacesArePlane: bool, optional
        :return: new volumes dimTags
        :rtype: tuple[tuple[int, int], tuple[int, int]]
        """
        vol1BoundarySurfacesDimTags = gmsh.model.getBoundary(
            volume1DimTags,
            combined=True,
            oriented=False,
            recursive=False,
        )

        vol2BoundarySurfacesDimTags = gmsh.model.getBoundary(
            volume2DimTags,
            combined=True,
            oriented=False,
            recursive=False,
        )

        # Remove the old volumes:
        gmsh.model.occ.remove(volume1DimTags + volume2DimTags, recursive=False)

        # Find common surfaces:
        commonSurfacesDimTags = list(
            set(vol2BoundarySurfacesDimTags).intersection(
                set(vol1BoundarySurfacesDimTags)
            )
        )

        # Fuse common surfaces:
        fusedCommonSurfaceDimTags = Mesh.fuse_surfaces(
            commonSurfacesDimTags, surfacesArePlane=surfacesArePlane
        )

        # Create the new volumes:
        for commonSurfaceDimTag in commonSurfacesDimTags:
            vol1BoundarySurfacesDimTags.remove(commonSurfaceDimTag)
            vol2BoundarySurfacesDimTags.remove(commonSurfaceDimTag)

        vol1BoundarySurfacesDimTags.extend(fusedCommonSurfaceDimTags)
        vol1BoundarySurfaceTags = [dimTag[1] for dimTag in vol1BoundarySurfacesDimTags]
        vol2BoundarySurfacesDimTags.extend(fusedCommonSurfaceDimTags)
        vol2BoundarySurfaceTags = [dimTag[1] for dimTag in vol2BoundarySurfacesDimTags]

        vol1SurfaceLoop = gmsh.model.occ.addSurfaceLoop(
            vol1BoundarySurfaceTags, sewing=True
        )
        vol1NewVolumeDimTag = (3, gmsh.model.occ.addVolume([vol1SurfaceLoop]))

        vol2SurfaceLoop = gmsh.model.occ.addSurfaceLoop(
            vol2BoundarySurfaceTags, sewing=True
        )
        vol2NewVolumeDimTag = (
            3,
            gmsh.model.occ.addVolume([vol2SurfaceLoop]),
        )

        gmsh.model.occ.synchronize()

        if fuseOtherSurfaces:
            vol1NewVolumeDimTag = Mesh.fuse_possible_surfaces_of_a_volume(
                vol1NewVolumeDimTag, surfacesArePlane=surfacesArePlane
            )
            vol2NewVolumeDimTag = Mesh.fuse_possible_surfaces_of_a_volume(
                vol2NewVolumeDimTag, surfacesArePlane=surfacesArePlane
            )

        return vol1NewVolumeDimTag, vol2NewVolumeDimTag

    @staticmethod
    def fuse_possible_surfaces_of_a_volume(volumeDimTag, surfacesArePlane=False):
        """
        Fuses surfaces that only belong to the volumeDimTag.

        :param volumeDimTag: dimTag of the volume
        :type volumeDimTag: tuple[int, int]
        :param surfacesArePlane: if True, fused surfaces are assumed to be plane, and
            fusion is performed accordingly
        :type surfacesArePlane: bool, optional
        :return: new volume dimTag
        :rtype: tuple[int, int]
        """
        boundarySurfacesDimTags = gmsh.model.getBoundary(
            [volumeDimTag],
            combined=True,
            oriented=False,
            recursive=False,
        )
        boundarSurfacesTags = [dimTag[1] for dimTag in boundarySurfacesDimTags]

        # Combine surfaces that only belong to the volume:
        toBeFusedSurfacesDimTags = []
        surfacesNormals = []
        for surfaceDimTag in boundarySurfacesDimTags:
            upward, _ = gmsh.model.getAdjacencies(surfaceDimTag[0], surfaceDimTag[1])

            if len(list(upward)) == 1:
                toBeFusedSurfacesDimTags.append(surfaceDimTag)
                # Get the normal of the surface:
                surfacesNormals.append(
                    list(gmsh.model.getNormal(surfaceDimTag[1], [0.5, 0.5]))
                )

        # Remove the old volume (it is not required anymore):
        gmsh.model.occ.remove([volumeDimTag], recursive=False)
        gmsh.model.occ.synchronize()

        # Categorize surfaces based on their normals so that they can be combined
        # correctly. Without these, perpendicular surfaces will cause problems.

        # Define a threshold to determine if two surface normals are similar or not
        threshold = 1e-6

        # Initialize an empty list to store the sets of surfaces
        setsOfSurfaces = []

        # Calculate the Euclidean distance between each pair of objects
        for i in range(len(toBeFusedSurfacesDimTags)):
            surfaceDimTag = toBeFusedSurfacesDimTags[i]
            surfaceTouchingVolumeTags, _ = list(
                gmsh.model.getAdjacencies(surfaceDimTag[0], surfaceDimTag[1])
            )
            surfaceNormal = surfacesNormals[i]
            assignedToASet = False

            for surfaceSet in setsOfSurfaces:
                representativeSurfaceDimTag = surfaceSet[0]
                representativeSurfaceTouchingVolumeTags, _ = list(
                    gmsh.model.getAdjacencies(
                        representativeSurfaceDimTag[0],
                        representativeSurfaceDimTag[1],
                    )
                )
                representativeNormal = list(
                    gmsh.model.getNormal(representativeSurfaceDimTag[1], [0.5, 0.5])
                )

                # Calculate the difference between surfaceNormal and
                # representativeNormal:
                difference = math.sqrt(
                    sum(
                        (x - y) ** 2
                        for x, y in zip(surfaceNormal, representativeNormal)
                    )
                )

                # Check if the distance is below the threshold
                if difference < threshold and set(surfaceTouchingVolumeTags) == set(
                    representativeSurfaceTouchingVolumeTags
                ):
                    # Add the object to an existing category
                    surfaceSet.append(surfaceDimTag)
                    assignedToASet = True
                    break

            if not assignedToASet:
                # Create a new category with the current object if none of the
                # existing sets match
                setsOfSurfaces.append([surfaceDimTag])

        for surfaceSet in setsOfSurfaces:
            if len(surfaceSet) > 1:
                oldSurfaceDimTags = surfaceSet
                newSurfaceDimTags = Mesh.fuse_surfaces(
                    oldSurfaceDimTags, surfacesArePlane=surfacesArePlane
                )
                newSurfaceTags = [dimTag[1] for dimTag in newSurfaceDimTags]

                oldSurfaceTags = [dimTag[1] for dimTag in oldSurfaceDimTags]
                boundarSurfacesTags = [
                    tag for tag in boundarSurfacesTags if tag not in oldSurfaceTags
                ]
                boundarSurfacesTags.extend(newSurfaceTags)

        # Create a new single volume:
        surfaceLoop = gmsh.model.occ.addSurfaceLoop(boundarSurfacesTags, sewing=True)
        newVolumeTag = gmsh.model.occ.addVolume([surfaceLoop])
        gmsh.model.occ.synchronize()

        return (3, newVolumeTag)

    @staticmethod
    def fuse_surfaces(surfaceDimTags, surfacesArePlane=False, categorizeSurfaces=False):
        """
        Fuses all the surfaces in a given list of surface dimTags, removes the old
        surfaces, and returns the new dimTags. If surfacesArePlane is True, the surfaces
        are assumed to be plane, and fusing will be done without gmsh.model.occ.fuse
        method, which is faster.

        :param surfaceDimTags: dimTags of the surfaces
        :type surfaceDimTags: list[tuple[int, int]]
        :param surfacesArePlane: if True, surfaces are assumed to be plane
        :type surfacesArePlane: bool, optional
        :return: newly created surface dimTags
        :rtype: list[tuple[int, int]]
        """
        oldSurfaceDimTags = surfaceDimTags

        if surfacesArePlane:
            # Get the combined boundary curves:
            boundaryCurvesDimTags = gmsh.model.getBoundary(
                oldSurfaceDimTags,
                combined=True,
                oriented=False,
                recursive=False,
            )

            # Get all the boundary curves:
            allCurvesDimTags = gmsh.model.getBoundary(
                oldSurfaceDimTags,
                combined=False,
                oriented=False,
                recursive=False,
            )

            # Find internal (common) curves:
            internalCurvesDimTags = list(
                set(allCurvesDimTags) - set(boundaryCurvesDimTags)
            )

            # Remove the old surfaces:
            gmsh.model.occ.remove(oldSurfaceDimTags, recursive=False)

            # Remove the internal curves:
            gmsh.model.occ.remove(internalCurvesDimTags, recursive=True)

            # Create a new single surface:
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
                            gmsh.model.occ.synchronize()
                            pointTags = gmsh.model.getBoundary(
                                [(1, curveTag) for curveTag in curve],
                                oriented=False,
                                combined=False,
                            )
                            # Get the positions of the points:
                            points = []
                            for dimTag in pointTags:
                                boundingbox1 = gmsh.model.occ.getBoundingBox(
                                    0, dimTag[1]
                                )[:3]
                                boundingbox2 = gmsh.model.occ.getBoundingBox(
                                    0, dimTag[1]
                                )[3:]
                                boundingbox = list(
                                    map(operator.add, boundingbox1, boundingbox2)
                                )
                                points.append(
                                    list(map(operator.truediv, boundingbox, (2, 2, 2)))
                                )

                            distances.append(
                                max([point[0] ** 2 + point[1] ** 2 for point in points])
                            )
                elif dim == 1:
                    distances = []
                    for dimTag in dimTags:
                        gmsh.model.occ.synchronize()
                        pointTags = gmsh.model.getBoundary(
                            [dimTag],
                            oriented=False,
                            combined=False,
                        )
                        # Get the positions of the points:
                        points = []
                        for dimTag in pointTags:
                            boundingbox1 = gmsh.model.occ.getBoundingBox(0, dimTag[1])[
                                :3
                            ]
                            boundingbox2 = gmsh.model.occ.getBoundingBox(0, dimTag[1])[
                                3:
                            ]
                            boundingbox = list(
                                map(operator.add, boundingbox1, boundingbox2)
                            )
                            points.append(
                                list(map(operator.truediv, boundingbox, (2, 2, 2)))
                            )

                        distances.append(
                            max([point[0] ** 2 + point[1] ** 2 for point in points])
                        )

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

            outerCurvesDimTags = findOuterOnes(boundaryCurvesDimTags)
            outerCurvesTags = [dimTag[1] for dimTag in outerCurvesDimTags]
            curveLoopOuter = gmsh.model.occ.addCurveLoop(outerCurvesTags)

            innerCurvesDimTags = findOuterOnes(
                boundaryCurvesDimTags, findInnerOnes=True
            )
            innerCurvesTags = [dimTag[1] for dimTag in innerCurvesDimTags]
            curveLoopInner = gmsh.model.occ.addCurveLoop(innerCurvesTags)

            newSurfaceTag = gmsh.model.occ.addPlaneSurface(
                [curveLoopOuter, curveLoopInner]
            )

            gmsh.model.occ.synchronize()

            return [(2, newSurfaceTag)]
        else:
            # Create a new single surface:
            # The order of tags seems to be important for the fuse method to work
            # and not crash with a segmentation fault.
            try:
                fuseResults = gmsh.model.occ.fuse(
                    [oldSurfaceDimTags[0]],
                    oldSurfaceDimTags[1:],
                    removeObject=False,
                    removeTool=False,
                )
                newSurfaceDimTags = fuseResults[0]
            except:
                return oldSurfaceDimTags

            # Get the combined boundary curves:
            gmsh.model.occ.synchronize()
            boundaryCurvesDimTags = gmsh.model.getBoundary(
                newSurfaceDimTags,
                combined=True,
                oriented=False,
                recursive=False,
            )

            # Get all the boundary curves:
            allCurvesDimTags = gmsh.model.getBoundary(
                oldSurfaceDimTags,
                combined=False,
                oriented=False,
                recursive=False,
            )

            # Find internal (common) curves:
            internalCurvesDimTags = list(
                set(allCurvesDimTags) - set(boundaryCurvesDimTags)
            )

            # Remove the old surfaces:
            gmsh.model.occ.remove(oldSurfaceDimTags, recursive=False)

            # Remove the internal curves:
            gmsh.model.occ.remove(internalCurvesDimTags, recursive=False)

            gmsh.model.occ.synchronize()

            return newSurfaceDimTags

    def generate_regions(self):
        """
        Generates physical groups and the regions file. Physical groups are generated in
        GMSH, and their tags and names are saved in the regions file. FiQuS use the
        regions file to create the corresponding .pro file.

        .vi file sends the information about geometry from geometry class to mesh class.
        .regions file sends the information about the physical groups formed out of
        elementary entities from the mesh class to the solution class.

        The file extension for the regions file is custom because users should not edit
        or even see this file.

        Regions are generated in the meshing part because BREP files cannot store
        regions.
        """
        logger.info("Generating physical groups and regions file has been started.")
        start_time = timeit.default_timer()

        # Create regions instance to both generate regions file and physical groups:
        self.regions = regions()

        # ==============================================================================
        # WINDING AND CONTACT LAYER REGIONS START =========================================
        # ==============================================================================
        if not self.geo.contactLayer.thinShellApproximation:
            windingTags = [dimTag[1] for dimTag in self.dimTags[self.geo.winding.name]]
            self.regions.addEntities(
                self.geo.winding.name, windingTags, regionType.powered, entityType.vol
            )

            insulatorTags = [dimTag[1] for dimTag in self.dimTags[self.geo.contactLayer.name]]

            terminalDimTags = (
                self.dimTags[self.geo.terminals.inner.name] + self.dimTags[self.geo.terminals.outer.name]
            )
            terminalAndNotchSurfaces = gmsh.model.getBoundary(
                terminalDimTags, combined=False, oriented=False
            )
            transitionNotchSurfaces = gmsh.model.getBoundary(
                self.dimTags["innerTransitionNotch"]
                + self.dimTags["outerTransitionNotch"],
                combined=False,
                oriented=False,
            )

            contactLayer = []
            contactLayerBetweenTerminalsAndWinding = []
            for insulatorTag in insulatorTags:
                insulatorSurfaces = gmsh.model.getBoundary(
                    [(3, insulatorTag)], combined=False, oriented=False
                )
                itTouchesTerminals = False
                for insulatorSurface in insulatorSurfaces:
                    if (
                        insulatorSurface
                        in terminalAndNotchSurfaces + transitionNotchSurfaces
                    ):
                        contactLayerBetweenTerminalsAndWinding.append(insulatorTag)
                        itTouchesTerminals = True
                        break

                if not itTouchesTerminals:
                    contactLayer.append(insulatorTag)

            self.regions.addEntities(
                self.geo.contactLayer.name, contactLayer, regionType.insulator, entityType.vol
            )

            self.regions.addEntities(
                "WindingAndTerminalContactLayer",
                contactLayerBetweenTerminalsAndWinding,
                regionType.insulator,
                entityType.vol,
            )
        else:
            # Calculate the number of stacks for each individual winding. Number of
            # stacks is the number of volumes per turn. It affects how the regions
            # are created because of the TSA's pro file formulation.

            # find the smallest prime number that divides NofVolumes:
            windingDimTags = self.dimTags[self.geo.winding.name + "1"]
            windingTags = [dimTag[1] for dimTag in windingDimTags]
            NofVolumes = self.geo.winding.numberOfVolumesPerTurn
            smallest_prime_divisor = 2
            while NofVolumes % smallest_prime_divisor != 0:
                smallest_prime_divisor += 1

            # the number of stacks is the region divison per turn:
            NofStacks = smallest_prime_divisor

            # the number of sets are the total number of regions for all windings and
            # contact layers:
            NofSets = 2 * NofStacks

            allInnerTerminalSurfaces = gmsh.model.getBoundary(
                self.dimTags[self.geo.terminals.inner.name] + self.dimTags["innerTransitionNotch"],
                combined=False,
                oriented=False,
            )
            allInnerTerminalContactLayerSurfaces = []
            for innerTerminalSurface in allInnerTerminalSurfaces:
                normal = gmsh.model.getNormal(innerTerminalSurface[1], [0.5, 0.5])
                if abs(normal[2]) < 1e-5:
                    curves = gmsh.model.getBoundary(
                        [innerTerminalSurface], combined=False, oriented=False
                    )
                    curveTags = [dimTag[1] for dimTag in curves]
                    for curveTag in curveTags:
                        curveObject = curve(curveTag, self.geo)
                        if curveObject.type is curveType.spiralArc:
                            allInnerTerminalContactLayerSurfaces.append(
                                innerTerminalSurface[1]
                            )

            finalWindingSets = []
            finalContactLayerSets = []
            for i in range(NofSets):
                finalWindingSets.append([])
                finalContactLayerSets.append([])

            for i in range(self.geo.numberOfPancakes):
                windingDimTags = self.dimTags[self.geo.winding.name + str(i + 1)]
                windingTags = [dimTag[1] for dimTag in windingDimTags]

                NofVolumes = len(windingDimTags)

                windings = []
                for windingTag in windingTags:
                    surfaces = gmsh.model.getBoundary(
                        [(3, windingTag)], combined=False, oriented=False
                    )
                    curves = gmsh.model.getBoundary(
                        surfaces, combined=False, oriented=False
                    )
                    curveTags = list(set([dimTag[1] for dimTag in curves]))
                    for curveTag in curveTags:
                        curveObject = curve(curveTag, self.geo)
                        if curveObject.type is curveType.spiralArc:
                            windingVolumeLengthInTurns = abs(
                                curveObject.n2 - curveObject.n1
                            )
                            if windingVolumeLengthInTurns > 0.5:
                                # The arc can never be longer than half a turn.
                                windingVolumeLengthInTurns = (
                                    1 - windingVolumeLengthInTurns
                                )

                    windings.append((windingTag, windingVolumeLengthInTurns))

                windingStacks = []
                while len(windings) > 0:
                    stack = []
                    stackLength = 0
                    for windingTag, windingVolumeLengthInTurns in windings:
                        if stackLength < 1 / NofStacks - 1e-6:
                            stack.append(windingTag)
                            stackLength += windingVolumeLengthInTurns
                        else:
                            break
                    # remove all the windings that are already added to the stack:
                    windings = [
                        (windingTag, windingVolumeLengthInTurns)
                        for windingTag, windingVolumeLengthInTurns in windings
                        if windingTag not in stack
                    ]

                    # find spiral surfaces of the stack:
                    stackDimTags = [(3, windingTag) for windingTag in stack]
                    stackSurfacesDimTags = gmsh.model.getBoundary(
                        stackDimTags, combined=True, oriented=False
                    )
                    stackCurvesDimTags = gmsh.model.getBoundary(
                        stackSurfacesDimTags, combined=False, oriented=False
                    )
                    # find the curve furthest from the origin:
                    curveObjects = []
                    for curveDimTag in stackCurvesDimTags:
                        curveObject = curve(curveDimTag[1], self.geo)
                        if curveObject.type is curveType.spiralArc:
                            curveObjectDistanceFromOrigin = math.sqrt(
                                curveObject.points[0][0] ** 2
                                + curveObject.points[0][1] ** 2
                            )
                            curveObjects.append(
                                (curveObject, curveObjectDistanceFromOrigin)
                            )

                    # sort the curves based on their distance from the origin (furthest first)
                    curveObjects.sort(key=lambda x: x[1], reverse=True)

                    curveTags = [curveObject[0].tag for curveObject in curveObjects]

                    # only keep half of the curveTags:
                    furthestCurveTags = curveTags[: len(curveTags) // 2]

                    stackSpiralSurfaces = []
                    for surfaceDimTag in stackSurfacesDimTags:
                        normal = gmsh.model.getNormal(surfaceDimTag[1], [0.5, 0.5])
                        if abs(normal[2]) < 1e-5:
                            curves = gmsh.model.getBoundary(
                                [surfaceDimTag], combined=False, oriented=False
                            )
                            curveTags = [dimTag[1] for dimTag in curves]
                            for curveTag in curveTags:
                                if curveTag in furthestCurveTags:
                                    stackSpiralSurfaces.append(surfaceDimTag[1])
                                    break

                    # add inner terminal surfaces too:
                    if len(windingStacks) >= NofStacks:
                        correspondingWindingStack = windingStacks[
                            len(windingStacks) - NofStacks
                        ]
                        correspondingWindings = correspondingWindingStack[0]
                        correspondingSurfaces = gmsh.model.getBoundary(
                            [(3, windingTag) for windingTag in correspondingWindings],
                            combined=True,
                            oriented=False,
                        )
                        correspondingSurfaceTags = [
                            dimTag[1] for dimTag in correspondingSurfaces
                        ]
                        for surface in allInnerTerminalContactLayerSurfaces:
                            if surface in correspondingSurfaceTags:
                                stackSpiralSurfaces.append(surface)

                    windingStacks.append((stack, stackSpiralSurfaces))

                windingSets = []
                contactLayerSets = []
                for j in range(NofSets):
                    windingTags = [
                        windingTags for windingTags, _ in windingStacks[j::NofSets]
                    ]
                    windingTags = list(itertools.chain.from_iterable(windingTags))

                    surfaceTags = [
                        surfaceTags for _, surfaceTags in windingStacks[j::NofSets]
                    ]
                    surfaceTags = list(itertools.chain.from_iterable(surfaceTags))

                    windingSets.append(windingTags)
                    contactLayerSets.append(surfaceTags)

                # windingSets is a list with a length of NofSets.
                # finalWindingSets is also a list with a length of NofSets.
                for j, (windingSet, contactLayerSet) in enumerate(
                    zip(windingSets, contactLayerSets)
                ):
                    finalWindingSets[j].extend(windingSet)
                    finalContactLayerSets[j].extend(contactLayerSet)

            # Seperate transition layer:
            terminalAndNotchSurfaces = gmsh.model.getBoundary(
                self.dimTags[self.geo.terminals.inner.name]
                + self.dimTags[self.geo.terminals.outer.name]
                + self.dimTags["innerTransitionNotch"]
                + self.dimTags["outerTransitionNotch"],
                combined=False,
                oriented=False,
            )
            terminalAndNotchSurfaceTags = set(
                [dimTag[1] for dimTag in terminalAndNotchSurfaces]
            )

            contactLayerSets = []
            terminalWindingContactLayerSets = []
            for j in range(NofSets):
                contactLayerSets.append([])
                terminalWindingContactLayerSets.append([])

            for j in range(NofSets):
                allContactLayersInTheSet = finalContactLayerSets[j]

                insulatorList = []
                windingTerminalInsulatorList = []
                for contactLayer in allContactLayersInTheSet:
                    if contactLayer in terminalAndNotchSurfaceTags:
                        windingTerminalInsulatorList.append(contactLayer)
                    else:
                        insulatorList.append(contactLayer)

                contactLayerSets[j].extend(set(insulatorList))
                terminalWindingContactLayerSets[j].extend(set(windingTerminalInsulatorList))

            allContactLayerSurfacesForAllPancakes = []
            for j in range(NofSets):
                # Add winding volumes:
                self.regions.addEntities(
                    self.geo.winding.name + "-" + str(j + 1),
                    finalWindingSets[j],
                    regionType.powered,
                    entityType.vol,
                )

                # Add insulator surfaces:
                self.regions.addEntities(
                    self.geo.contactLayer.name + "-" + str(j + 1),
                    contactLayerSets[j],
                    regionType.insulator,
                    entityType.surf,
                )
                allContactLayerSurfacesForAllPancakes.extend(contactLayerSets[j])

                # Add terminal and winding contact layer:
                allContactLayerSurfacesForAllPancakes.extend(
                    terminalWindingContactLayerSets[j]
                )

                # Add intersection of transition notch boundary and WindingAndTerminalContactLayer:
                transitionNotchSurfaces = gmsh.model.getBoundary(
                    self.dimTags["innerTransitionNotch"]
                    + self.dimTags["outerTransitionNotch"],
                    combined=False,
                    oriented=False,
                    recursive=False
                )

                terminalContactLayerMinusNotch = set(terminalWindingContactLayerSets[j]).difference([tag for (dim, tag) in transitionNotchSurfaces])
                
                self.regions.addEntities(
                    "WindingAndTerminalContactLayerWithoutNotch" + "-" + str(j + 1),
                    list(terminalContactLayerMinusNotch),
                    regionType.insulator,
                    entityType.surf,
                )

                notchAndTerminalContactLayerIntersection = set([tag for (dim, tag) in transitionNotchSurfaces]).intersection(terminalWindingContactLayerSets[j])

                self.regions.addEntities(
                    "WindingAndTerminalContactLayerOnlyNotch" + "-" + str(j + 1),
                    list(notchAndTerminalContactLayerIntersection),
                    regionType.insulator,
                    entityType.surf,
                )

            allContactLayerSurfacesForAllPancakes = list(
                set(allContactLayerSurfacesForAllPancakes)
            )
            # Get insulator's boundary line that touches the air (required for the
            # pro file formulation):
            allContactLayerSurfacesForAllPancakesDimTags = [
                (2, surfaceTag) for surfaceTag in allContactLayerSurfacesForAllPancakes
            ]
            insulatorBoundary = gmsh.model.getBoundary(
                allContactLayerSurfacesForAllPancakesDimTags,
                combined=True,
                oriented=False,
            )
            insulatorBoundaryTags = [dimTag[1] for dimTag in insulatorBoundary]

            # Add insulator boundary lines:
            # Vertical lines should be removed from the insulator boundary because
            # they touch the terminals, not the air:
            verticalInsulatorBoundaryTags = []
            insulatorBoundaryTagsCopy = insulatorBoundaryTags.copy()
            for lineTag in insulatorBoundaryTagsCopy:
                lineObject = curve(lineTag, self.geo)
                if lineObject.type is curveType.axial:
                    verticalInsulatorBoundaryTags.append(lineTag)
                    insulatorBoundaryTags.remove(lineTag)

            # Create regions:
            self.regions.addEntities(
                self.geo.contactLayerBoundaryName,
                insulatorBoundaryTags,
                regionType.insulator,
                entityType.curve,
            )
            self.regions.addEntities(
                self.geo.contactLayerBoundaryName + "-TouchingTerminal",
                verticalInsulatorBoundaryTags,
                regionType.insulator,
                entityType.curve,
            )

        innerTransitionNotchTags = [
            dimTag[1] for dimTag in self.dimTags["innerTransitionNotch"]
        ]
        outerTransitionNotchTags = [
            dimTag[1] for dimTag in self.dimTags["outerTransitionNotch"]
        ]
        self.regions.addEntities(
            "innerTransitionNotch",
            innerTransitionNotchTags,
            regionType.powered,
            entityType.vol,
        )
        self.regions.addEntities(
            "outerTransitionNotch",
            outerTransitionNotchTags,
            regionType.powered,
            entityType.vol,
        )
        # ==============================================================================
        # WINDING AND CONTACT LAYER REGIONS ENDS =======================================
        # ==============================================================================

        # ==============================================================================
        # TERMINAL REGIONS START =======================================================
        # ==============================================================================

        innerTerminalTags = [dimTag[1] for dimTag in self.dimTags[self.geo.terminals.inner.name]]
        self.regions.addEntities(
            self.geo.terminals.inner.name, innerTerminalTags, regionType.powered, entityType.vol_in
        )
        outerTerminalTags = [dimTag[1] for dimTag in self.dimTags[self.geo.terminals.outer.name]]
        self.regions.addEntities(
            self.geo.terminals.outer.name,
            outerTerminalTags,
            regionType.powered,
            entityType.vol_out,
        )

        # Top and bottom terminal surfaces:
        firstTerminalDimTags = self.dimTags[self.geo.terminals.firstName]
        lastTerminalDimTags = self.dimTags[self.geo.terminals.lastName]

        if self.mesh.terminals.structured:
            topSurfaceDimTags = []
            for i in [1, 2, 3, 4]:
                lastTerminalSurfaces = gmsh.model.getBoundary(
                    [lastTerminalDimTags[-i]], combined=False, oriented=False
                )
                topSurfaceDimTags.append(lastTerminalSurfaces[-1])
        else:
            lastTerminalSurfaces = gmsh.model.getBoundary(
                [lastTerminalDimTags[-1]], combined=False, oriented=False
            )
            topSurfaceDimTags = [lastTerminalSurfaces[-1]]
        topSurfaceTags = [dimTag[1] for dimTag in topSurfaceDimTags]

        if self.mesh.terminals.structured:
            bottomSurfaceDimTags = []
            for i in [1, 2, 3, 4]:
                firstTerminalSurfaces = gmsh.model.getBoundary(
                    [firstTerminalDimTags[-i]], combined=False, oriented=False
                )
                bottomSurfaceDimTags.append(firstTerminalSurfaces[-1])
        else:
            firstTerminalSurfaces = gmsh.model.getBoundary(
                [firstTerminalDimTags[-1]], combined=False, oriented=False
            )
            bottomSurfaceDimTags = [firstTerminalSurfaces[-1]]
        bottomSurfaceTags = [dimTag[1] for dimTag in bottomSurfaceDimTags]

        self.regions.addEntities(
            "TopSurface",
            topSurfaceTags,
            regionType.powered,
            entityType.surf_out,
        )
        self.regions.addEntities(
            "BottomSurface",
            bottomSurfaceTags,
            regionType.powered,
            entityType.surf_in,
        )

        # if self.geo.contactLayer.tsa:
        #     outerTerminalSurfaces = gmsh.model.getBoundary(
        #         self.dimTags[self.geo.terminals.o.name], combined=True, oriented=False
        #     )
        #     outerTerminalSurfaces = [dimTag[1] for dimTag in outerTerminalSurfaces]
        #     innerTerminalSurfaces = gmsh.model.getBoundary(
        #         self.dimTags[self.geo.terminals.i.name], combined=True, oriented=False
        #     )
        #     innerTerminalSurfaces = [dimTag[1] for dimTag in innerTerminalSurfaces]
        #     windingSurfaces = gmsh.model.getBoundary(
        #         self.dimTags[self.geo.winding.name] + self.dimTags[self.geo.contactLayer.name],
        #         combined=True,
        #         oriented=False,
        #     )
        #     windingSurfaces = [dimTag[1] for dimTag in windingSurfaces]

        #     windingAndOuterTerminalCommonSurfaces = list(
        #         set(windingSurfaces).intersection(set(outerTerminalSurfaces))
        #     )
        #     windingAndInnerTerminalCommonSurfaces = list(
        #         set(windingSurfaces).intersection(set(innerTerminalSurfaces))
        #     )

        #     self.regions.addEntities(
        #         "WindingAndTerminalContactLayer",
        #         windingAndOuterTerminalCommonSurfaces
        #         + windingAndInnerTerminalCommonSurfaces,
        #         regionType.insulator,
        #         entityType.surf,
        #     )

        # ==============================================================================
        # TERMINAL REGIONS ENDS ========================================================
        # ==============================================================================

        # ==============================================================================
        # AIR AND AIR SHELL REGIONS STARTS =============================================
        # ==============================================================================
        airTags = [dimTag[1] for dimTag in self.dimTags[self.geo.air.name]]
        self.regions.addEntities(
            self.geo.air.name, airTags, regionType.air, entityType.vol
        )

        # Create a region with two points on air to be used in the pro file formulation:
        # To those points, Phi=0 boundary condition will be applied to set the gauge.
        outerAirSurfaces = gmsh.model.getBoundary(
            self.dimTags[self.geo.air.name + "-OuterTube"], combined=True, oriented=False
        )
        outerAirSurface = outerAirSurfaces[-1]
        outerAirCurves = gmsh.model.getBoundary(
            [outerAirSurface], combined=True, oriented=False
        )
        outerAirCurve = outerAirCurves[-1]
        outerAirPoint = gmsh.model.getBoundary(
            [outerAirCurve], combined=False, oriented=False
        )
        outerAirPointTag = outerAirPoint[0][1]
        self.regions.addEntities(
            "OuterAirPoint",
            [outerAirPointTag],
            regionType.air,
            entityType.point,
        )

        innerAirSurfaces = gmsh.model.getBoundary(
            self.dimTags[self.geo.air.name + "-InnerCylinder"],
            combined=True,
            oriented=False,
        )
        innerAirSurface = innerAirSurfaces[0]
        innerAirCurves = gmsh.model.getBoundary(
            [innerAirSurface], combined=True, oriented=False
        )
        innerAirCurve = innerAirCurves[-1]
        innerAirPoint = gmsh.model.getBoundary(
            [innerAirCurve], combined=False, oriented=False
        )
        innerAirPointTag = innerAirPoint[0][1]
        self.regions.addEntities(
            "InnerAirPoint",
            [innerAirPointTag],
            regionType.air,
            entityType.point,
        )

        if self.geo.air.shellTransformation:
            if self.geo.air.type == "cylinder":
                airShellTags = [
                    dimTag[1] for dimTag in self.dimTags[self.geo.air.shellVolumeName]
                ]
                self.regions.addEntities(
                    self.geo.air.shellVolumeName,
                    airShellTags,
                    regionType.air_far_field,
                    entityType.vol,
                )
            elif self.geo.air.type == "cuboid":
                airShell1Tags = [
                    dimTag[1]
                    for dimTag in self.dimTags[self.geo.air.shellVolumeName + "-Part1"]
                    + self.dimTags[self.geo.air.shellVolumeName + "-Part3"]
                ]
                airShell2Tags = [
                    dimTag[1]
                    for dimTag in self.dimTags[self.geo.air.shellVolumeName + "-Part2"]
                    + self.dimTags[self.geo.air.shellVolumeName + "-Part4"]
                ]
                self.regions.addEntities(
                    self.geo.air.shellVolumeName + "-PartX",
                    airShell1Tags,
                    regionType.air_far_field,
                    entityType.vol,
                )
                self.regions.addEntities(
                    self.geo.air.shellVolumeName + "-PartY",
                    airShell2Tags,
                    regionType.air_far_field,
                    entityType.vol,
                )
        # ==============================================================================
        # AIR AND AIR SHELL REGIONS ENDS ===============================================
        # ==============================================================================

        # ==============================================================================
        # CUTS STARTS ==================================================================
        # ==============================================================================
        if self.geo.air.cutName in self.dimTags:
            cutTags = [dimTag[1] for dimTag in self.dimTags[self.geo.air.cutName]]
            self.regions.addEntities(
                self.geo.air.cutName, cutTags, regionType.air, entityType.cochain
            )

        if "CutsForPerfectInsulation" in self.dimTags:
            cutTags = [dimTag[1] for dimTag in self.dimTags["CutsForPerfectInsulation"]]
            self.regions.addEntities(
                "CutsForPerfectInsulation", cutTags, regionType.air, entityType.cochain
            )

        if "CutsBetweenPancakes" in self.dimTags:
            cutTags = [dimTag[1] for dimTag in self.dimTags["CutsBetweenPancakes"]]
            self.regions.addEntities(
                "CutsBetweenPancakes", cutTags, regionType.air, entityType.cochain
            )
        # ==============================================================================
        # CUTS ENDS ====================================================================
        # ==============================================================================

        # ==============================================================================
        # PANCAKE BOUNDARY SURFACE STARTS ==============================================
        # ==============================================================================
        # Pancake3D Boundary Surface:
        allPancakeVolumes = (
            self.dimTags[self.geo.winding.name]
            + self.dimTags[self.geo.terminals.inner.name]
            + self.dimTags[self.geo.terminals.outer.name]
            + self.dimTags[self.geo.contactLayer.name]
            + self.dimTags["innerTransitionNotch"]
            + self.dimTags["outerTransitionNotch"]
        )
        Pancake3DAllBoundary = gmsh.model.getBoundary(
            allPancakeVolumes, combined=True, oriented=False
        )
        Pancake3DBoundaryDimTags = list(
            set(Pancake3DAllBoundary)
            - set(topSurfaceDimTags)
            - set(bottomSurfaceDimTags)
        )
        pancake3DBoundaryTags = [dimTag[1] for dimTag in Pancake3DBoundaryDimTags]
        self.regions.addEntities(
            self.geo.pancakeBoundaryName,
            pancake3DBoundaryTags,
            regionType.powered,
            entityType.surf,
        )

        if self.geo.contactLayer.thinShellApproximation:
            # add non-winding boundary for convective cooling 
            windingBoundaryDimTags = gmsh.model.getBoundary(
                [(3, tag) for tag in itertools.chain(*finalWindingSets)],
                combined=True,
                oriented=False,
            )

            inner_terminal_and_transition_notch_all_boundaries = gmsh.model.getBoundary(
                self.dimTags[self.geo.terminals.inner.name] + self.dimTags["innerTransitionNotch"],
                combined=True,
                oriented=False
            )

            inner_terminal_and_transition_notch_boundary_dim_tags = set(Pancake3DBoundaryDimTags).intersection(inner_terminal_and_transition_notch_all_boundaries)
            inner_terminal_and_transition_notch_boundary_tags = [dimTag[1] for dimTag in inner_terminal_and_transition_notch_boundary_dim_tags]
            self.regions.addEntities(
                f"{self.geo.pancakeBoundaryName}-InnerTerminalAndTransitionNotch",
                inner_terminal_and_transition_notch_boundary_tags,
                regionType.powered,
                entityType.surf_th,
            )

            outer_terminal_and_transition_notch_all_boundaries = gmsh.model.getBoundary(
                self.dimTags[self.geo.terminals.outer.name] + self.dimTags["outerTransitionNotch"],
                combined=True,
                oriented=False
            )

            outer_terminal_and_transition_notch_boundary_dim_tags = set(Pancake3DBoundaryDimTags).intersection(outer_terminal_and_transition_notch_all_boundaries)
            outer_terminal_and_transition_notch_boundary_tags = [dimTag[1] for dimTag in outer_terminal_and_transition_notch_boundary_dim_tags]
            self.regions.addEntities(
                f"{self.geo.pancakeBoundaryName}-outerTerminalAndTransitionNotch",
                outer_terminal_and_transition_notch_boundary_tags,
                regionType.powered,
                entityType.surf_th,
            )

            # add pancake boundary for convective cooling following the winding numbering logic
            # computes the intersection between pancake boundary and the boundary of each winding group
            for j in range(NofSets):

                windingBoundaryDimTags = gmsh.model.getBoundary(
                    [(3, tag) for tag in finalWindingSets[j]],
                    combined=True,
                    oriented=False,
                )

                windingBoundaryDimTags = set(windingBoundaryDimTags).intersection(Pancake3DBoundaryDimTags)

                windingBoundaryTags = [dimTag[1] for dimTag in windingBoundaryDimTags]
                self.regions.addEntities(
                    f"{self.geo.pancakeBoundaryName}-Winding{j+1}",
                    windingBoundaryTags,
                    regionType.powered,
                    entityType.surf_th,
                )

        if not self.geo.contactLayer.thinShellApproximation:
            # Pancake3D Boundary Surface with only winding and terminals:
            allPancakeVolumes = (
                self.dimTags[self.geo.winding.name]
                + self.dimTags[self.geo.terminals.inner.name]
                + self.dimTags[self.geo.terminals.outer.name]
                + self.dimTags["innerTransitionNotch"]
                + self.dimTags["outerTransitionNotch"]
                + [(3, tag) for tag in contactLayerBetweenTerminalsAndWinding]
            )
            Pancake3DAllBoundary = gmsh.model.getBoundary(
                allPancakeVolumes, combined=True, oriented=False
            )
            Pancake3DBoundaryDimTags = list(
                set(Pancake3DAllBoundary)
                - set(topSurfaceDimTags)
                - set(bottomSurfaceDimTags)
            )
            pancake3DBoundaryTags = [dimTag[1] for dimTag in Pancake3DBoundaryDimTags]
            self.regions.addEntities(
                self.geo.pancakeBoundaryName + "-OnlyWindingAndTerminals",
                pancake3DBoundaryTags,
                regionType.powered,
                entityType.surf,
            )

        # ==============================================================================
        # PANCAKE BOUNDARY SURFACE ENDS ================================================
        # ==============================================================================

        # Generate regions file:
        self.regions.generateRegionsFile(self.regions_file)
        self.rm = FilesAndFolders.read_data_from_yaml(self.regions_file, RegionsModel)

        logger.info(
            "Generating physical groups and regions file has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )

    def generate_mesh_file(self):
        """
        Saves mesh file to disk.


        """
        logger.info(
            f"Generating Pancake3D mesh file ({self.mesh_file}) has been started."
        )
        start_time = timeit.default_timer()

        gmsh.write(self.mesh_file)

        logger.info(
            f"Generating Pancake3D mesh file ({self.mesh_file}) has been finished"
            f" in {timeit.default_timer() - start_time:.2f} s."
        )

        if self.mesh_gui:
            gmsh.option.setNumber("Geometry.Volumes", 0)
            gmsh.option.setNumber("Geometry.Surfaces", 0)
            gmsh.option.setNumber("Geometry.Curves", 0)
            gmsh.option.setNumber("Geometry.Points", 0)
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()

    def load_mesh(self):
        """
        Loads mesh from .msh file.


        """
        logger.info("Loading Pancake3D mesh has been started.")
        start_time = timeit.default_timer()

        previousGeo = FilesAndFolders.read_data_from_yaml(
            self.geometry_data_file, Pancake3DGeometry
        )
        previousMesh = FilesAndFolders.read_data_from_yaml(
            self.mesh_data_file, Pancake3DMesh
        )

        if previousGeo.model_dump() != self.geo.model_dump():
            raise ValueError(
                "Geometry data has been changed. Please regenerate the geometry or load"
                " the previous geometry data."
            )
        elif previousMesh.model_dump() != self.mesh.model_dump():
            raise ValueError(
                "Mesh data has been changed. Please regenerate the mesh or load the"
                " previous mesh data."
            )

        gmsh.clear()
        gmsh.open(self.mesh_file)

        logger.info(
            "Loading Pancake3D mesh has been finished in"
            f" {timeit.default_timer() - start_time:.2f} s."
        )
