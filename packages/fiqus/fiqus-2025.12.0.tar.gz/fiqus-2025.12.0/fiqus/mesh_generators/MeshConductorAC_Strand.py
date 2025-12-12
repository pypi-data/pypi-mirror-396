import os
import pickle

import gmsh
import numpy as np

from fiqus.data import RegionsModelFiQuS
from fiqus.utils.Utils import GmshUtils, FilesAndFolders
from fiqus.data.RegionsModelFiQuS import RegionsModel

from fiqus.geom_generators.GeometryConductorAC_Strand import TwistedStrand, Line

occ = gmsh.model.occ


class Mesh:
    def __init__(self, fdm, verbose=True):
        """
        A base-class used to manage the mesh for the CAC Strand and Rutherford models.

        :ivar fdm: The fiqus data model for input parameters.
        :vartype fdm: dict
        :ivar cacdm: The magnet section from the fdm.
        :vartype cacdm: object
        :ivar mesh_folder: The path to the folder where the mesh files are stored.
        :vartype mesh_folder: str
        :ivar magnet_name: The name of the magnet model.
        :vartype magnet_name: str
        :ivar mesh_file: The path to the .msh file for the mesh.
        :vartype mesh_file: str
        :ivar regions_file: The path to the .regions file for the mesh.
        :vartype regions_file: str
        :ivar verbose: If True, the class will print additional information during execution.
        :vartype verbose: bool
        :ivar gu: An instance of the GmshUtils class for managing the gmsh utility.
        :vartype gu: GmshUtils
        """
        self.fdm = fdm
        self.cacdm = fdm.magnet
        self.mesh_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name
        self.mesh_file = os.path.join(self.mesh_folder, f"{self.magnet_name}.msh")
        self.regions_file = os.path.join(self.mesh_folder, f"{self.magnet_name}.regions")
        self.verbose = verbose
        self.gu = GmshUtils(self.mesh_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

        gmsh.option.setNumber("General.Terminal", verbose)

    def save_mesh(self, gui: bool = False):
        """
            Saves the mesh to a .msh file. If gui is True, the mesh is also loaded in the gmsh GUI.
        """
        gmsh.write(self.mesh_file)
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            if gmsh.isInitialized():
                gmsh.clear()
                gmsh.finalize()

    def load_mesh(self, gui: bool = False):
        """
            Loads a previously generated mesh.
        """
        gmsh.clear()
        gmsh.open(self.mesh_file)

        if gui:
            self.gu.launch_interactive_GUI()


class StrandMesh(Mesh):
    """
    A subclass of Mesh that handles mesh generation for the twisted strand cross-section geometries.

    :ivar geometry_class: An instance of the TwistedStrand class that stores all the information about the model structure. Initially set to None and should be loaded or assigned before mesh generation methods are called.
    :vartype geometry_class: TwistedStrand

    :param fdm: The fiqus data model, providing all the necessary data and parameters for mesh generation.
    :type fdm: object
    :param verbose: A boolean flag that indicates whether additional information should be printed to the console during operation. Defaults to True.
    :type verbose: bool, optional
    """

    def __init__(self, fdm, verbose=True):
        super().__init__(fdm, verbose)
        self.geometry_class: TwistedStrand = None  # Class from geometry generation step, used to store all information about the model structure.

    def filament_field(self):
        """
        Generates the filament mesh size field.

        The standard mesh size field is linearly interpolated between the mesh size at the filament boundary and the center.
        Amplitude dependent meshing is applied if the field is expected to only penetrate a few elements in the filaments, adjusting the mesh size near the filament edges to capture the field penetration region accurately.

        :return: The filament mesh size field tag.
        :rtype: int
        """
        # Define some constants
        # Choose the largest distance from the center of mass of the filaments to the filament boundary as the filament radius.
        # This approximation is done to account for the fact that the filaments may not be circular, but can have any shape.
        filament_rad = 0
        for layer in self.geometry_class.filaments:
            for filament in layer:
                center_of_mass = gmsh.model.occ.get_center_of_mass(2, filament.surface_tag)
                for curve in filament.boundary_curves:
                    r = max([np.linalg.norm(np.array(center_of_mass) - curve.P1.pos), np.linalg.norm(np.array(center_of_mass) - curve.P2.pos)])
                    if r > filament_rad:
                        filament_rad = r
        meshSize_at_filament_boundary = filament_rad * self.cacdm.mesh.filaments.boundary_mesh_size_ratio
        meshSize_at_filament_center = filament_rad * self.cacdm.mesh.filaments.center_mesh_size_ratio
        filament_edges = sum([filament.boundary_curves for layer in self.geometry_class.filaments for filament in layer], [])

        amplitude_dependent_meshing, field_penetration_distance = self.evaluate_amplitude_dependent_meshing().values()
        desired_elements_in_field_penetration_region = self.cacdm.mesh.filaments.desired_elements_in_field_penetration_region

        frequency_dependent_meshing, skin_depth = self.evaluate_frequency_dependent_meshing().values()
        if frequency_dependent_meshing:
            filaments_in_skindepth = [filament for layer in self.geometry_class.filaments for filament in layer if np.linalg.norm(filament.center_point.pos) > self.geometry_class.matrix[-1].rad - 2 * skin_depth]
        else:
            filaments_in_skindepth = [filament for layer in self.geometry_class.filaments for filament in layer]

        if amplitude_dependent_meshing:
            # The field only penetrates a few elements. We should thus decrease the mesh size close to the filament edges.
            # min_mesh_size will be overwritten, while meshSize_at_filament_center will remain.

            circular_filament_fields = []
            nodesPerFilament = 2 * np.pi * filament_rad / ((field_penetration_distance) / desired_elements_in_field_penetration_region)  # We place nodes for meshing at the filament boundary for more efficient meshing (transfinite meshing)

            for filament in filaments_in_skindepth:
                circular_field = gmsh.model.mesh.field.add("Ball")
                gmsh.model.mesh.field.setNumber(circular_field, "Radius", (filament_rad - field_penetration_distance) * 0.85)
                gmsh.model.mesh.field.setNumber(circular_field, "XCenter", filament.center_point.pos[0])
                gmsh.model.mesh.field.setNumber(circular_field, "YCenter", filament.center_point.pos[1])
                gmsh.model.mesh.field.setNumber(circular_field, "Thickness", (filament_rad - field_penetration_distance) * 0.15)
                gmsh.model.mesh.field.setNumber(circular_field, "VIn", meshSize_at_filament_center)
                gmsh.model.mesh.field.setNumber(circular_field, "VOut", (field_penetration_distance) / desired_elements_in_field_penetration_region)
                circular_filament_fields.append(circular_field)

                for circle_arc_tag in [CA.tag for CA in filament.boundary_curves]:
                    gmsh.model.mesh.setTransfiniteCurve(circle_arc_tag, int(nodesPerFilament / len(filament.boundary_curves)), "Progression", 1)

            filament_fields = gmsh.model.mesh.field.add("Max")
            gmsh.model.mesh.field.setNumbers(filament_fields, "FieldsList", circular_filament_fields)

            self.cacdm.mesh.filaments.boundary_mesh_size_ratio = ((field_penetration_distance) / desired_elements_in_field_penetration_region) / filament_rad


        else:
            # Generalized to arbitrary filament shapes (not only circular)
            f_dist_boundary = gmsh.model.mesh.field.add("Distance")
            gmsh.model.mesh.field.setNumbers(f_dist_boundary, "CurvesList", [edge.tag for edge in filament_edges])

            mass_centers = []
            for layer in self.geometry_class.filaments:
                for filament in layer:
                    x, y, z = gmsh.model.occ.get_center_of_mass(2, filament.surface_tag)
                    mass_center_tag = gmsh.model.occ.addPoint(x, y, z)
                    mass_centers.append(mass_center_tag)
            gmsh.model.occ.synchronize()

            f_dist_center = gmsh.model.mesh.field.add("Distance")
            gmsh.model.mesh.field.setNumbers(f_dist_center, "PointsList", mass_centers)

            # Linearly interpolate between the mesh size at the filament center and the mesh size at the filament boundary.
            filament_fields = gmsh.model.mesh.field.add("MathEval")
            gmsh.model.mesh.field.setString(
                filament_fields,
                "F",
                f"( {meshSize_at_filament_boundary} * F{f_dist_center} + {meshSize_at_filament_center} * F{f_dist_boundary} ) / ( F{f_dist_center} + F{f_dist_boundary} )"
            )

        # Restrict the filament fields to the filaments
        filament_mesh_field = gmsh.model.mesh.field.add("Restrict")
        gmsh.model.mesh.field.setNumber(filament_mesh_field, "InField", filament_fields)

        if frequency_dependent_meshing:
            gmsh.model.mesh.field.setNumbers(filament_mesh_field, "SurfacesList", [filament.surface_tag for filament in filaments_in_skindepth])
        else:
            gmsh.model.mesh.field.setNumbers(filament_mesh_field, "SurfacesList", [filament.surface_tag for layer in self.geometry_class.filaments for filament in layer] + [hole.surface_tag for layer in self.geometry_class.filament_holes for hole in layer])

        return filament_mesh_field

    def matrix_threshold_to_filament_field(self, filaments):
        """
        Adjusts the matrix mesh size based on the distance from the filaments to improve mesh quality.

        This method creates a mesh size field that gradually refines the mesh in the matrix as it approaches the filaments.
        Filaments typically have a finer mesh than the matrix, and a large gradient in mesh size at their boundary can degrade the mesh quality.
        The method interpolates the mesh size from a minimum value at the filament boundary to a maximum value at a specified distance from the filaments, based on configuration parameters in the FDM.

        :param filaments: A list of filament surface objects for which the boundary mesh size adjustments are to be made.
        :type filaments: list[list[object]]

        :return: The tag of the created mesh size field, which is restricted to the matrix domain.
        :rtype: int
        """
        matrix = self.geometry_class.matrix
        matrix_mesh_options = self.cacdm.mesh.matrix

        filament_edges = sum([[CA.tag for CA in filament.boundary_curves] for filament in filaments], [])  # List of tags of all filament boundaries
        # Distance to filament boundaries field:
        distance_to_filament_field = gmsh.model.mesh.field.add("Distance")
        gmsh.model.mesh.field.setNumbers(distance_to_filament_field, "CurvesList", filament_edges)

        # Choose the largest distance from the center of mass of the filaments to the filament boundary as the filament radius.
        # This approximation is done to account for the fact that the filaments may not be circular, but can have any shape.
        filament_rad = 0
        for layer in self.geometry_class.filaments:
            for filament in layer:
                center_of_mass = gmsh.model.occ.get_center_of_mass(2, filament.surface_tag)
                for curve in filament.boundary_curves:
                    r = max([np.linalg.norm(np.array(center_of_mass) - curve.P1.pos), np.linalg.norm(np.array(center_of_mass) - curve.P2.pos)])
                    if r > filament_rad:
                        filament_rad = r

        filament_boundary_meshSize = filament_rad * self.cacdm.mesh.filaments.boundary_mesh_size_ratio

        # Linarily interpolate the mesh size from the filament boundaries to a specified distance from filaments.
        threshold_to_filament_field = gmsh.model.mesh.field.add("Threshold")
        gmsh.model.mesh.field.setNumber(threshold_to_filament_field, "InField", distance_to_filament_field)
        gmsh.model.mesh.field.setNumber(threshold_to_filament_field, "SizeMin", filament_boundary_meshSize)
        gmsh.model.mesh.field.setNumber(threshold_to_filament_field, "SizeMax", filament_rad * matrix_mesh_options.mesh_size_matrix_ratio_inner)
        gmsh.model.mesh.field.setNumber(threshold_to_filament_field, "DistMin", 0)
        gmsh.model.mesh.field.setNumber(threshold_to_filament_field, "DistMax", filament_rad * matrix_mesh_options.interpolation_distance_from_filaments_ratio)
        gmsh.model.mesh.field.setNumber(threshold_to_filament_field, "StopAtDistMax", 1)
        # gmsh.model.mesh.field.setNumber(threshold_to_filament_field, "Sigmoid", 0)

        meshSize_by_filament_field = gmsh.model.mesh.field.add("Restrict")  # Restrict the mesh to the matrix
        gmsh.model.mesh.field.setNumber(meshSize_by_filament_field, "InField", threshold_to_filament_field)
        gmsh.model.mesh.field.setNumbers(meshSize_by_filament_field, "SurfacesList", [partition.surface_tag for partition in matrix])
        # matrix_mesh_size_fields.append(meshSize_by_filament_field)
        return meshSize_by_filament_field

    def evaluate_amplitude_dependent_meshing(self):
        """
        Evaluates the necessity for amplitude-dependent meshing based on the applied magnetic field's amplitude.

        This method assesses whether the amplitude of the applied magnetic field is low enough that it only partially penetrates the filaments.
        In such cases, a finer mesh is required in the field penetration region to accurately capture field variations, while a coarser mesh can be used in the filament center where the field does not penetrate.
        It calculates the field penetration distance and determines whether an adjustment in the mesh is necessary to ensure accurate simulation results.

        :return: A dictionary containing:
            - "amplitude_dependent_meshing" (bool): Indicates whether amplitude-dependent meshing is needed based on the magnetic field's penetration.
            - "field_penetration_distance" (float): The estimated distance the magnetic field penetrates into the filaments, used to adjust the mesh size accordingly.
        :rtype: Dict[str, Union[bool, float]]
        """
        if self.cacdm.mesh.filaments.amplitude_dependent_scaling and self.cacdm.solve.source_parameters.sine.current_amplitude == 0 and not self.cacdm.geometry.io_settings.load.load_from_yaml:
            filament_radius = self.geometry_class.filaments[0][0].rad
            min_meshSize = filament_radius * self.cacdm.mesh.filaments.boundary_mesh_size_ratio
            meshSize_at_filament_center = filament_radius * self.cacdm.mesh.filaments.center_mesh_size_ratio

            applied_field_amplitude = self.cacdm.solve.source_parameters.sine.field_amplitude
            applied_field_amplitude = max(applied_field_amplitude, 0.01)  # Limit the amplitude to 0.01 T to avoid excessively fine mesh (Could be removed?).
            jc = 3e9  # self.cacdm.solve.material_properties.superconducting.jc.constant
            mu0 = np.pi * 4e-7

            field_penetration_distance = applied_field_amplitude / (mu0 * jc) * self.cacdm.mesh.filaments.field_penetration_depth_scaling_factor  # Estimate the field penetration distance

            # The mesh size in the filaments can be written as mesh_size(x) = a*x+b, with x being the distance from the filament boundary and a,b defined as:
            a = (meshSize_at_filament_center - min_meshSize) / filament_radius
            b = min_meshSize
            # The number of elements in the range x:[x0, x1] is approximated by the function:
            number_of_elements_in_range = lambda a, b, x0, x1: np.log(a * x1 + b) / a - np.log(a * x0 + b) / a if a != 0 else (x1 - x0) / b

            number_of_elements_penetrated_by_field = number_of_elements_in_range(a, b, 0, field_penetration_distance)
            desired_elements_in_field_penetration_region = self.cacdm.mesh.filaments.desired_elements_in_field_penetration_region

            if (number_of_elements_penetrated_by_field < desired_elements_in_field_penetration_region) and field_penetration_distance < filament_radius:
                print(
                    f"The magnetic field is expected to penetrate over approximately {round(number_of_elements_penetrated_by_field, 3)} elements in the filaments. To ensure that the field penetrates over at least {desired_elements_in_field_penetration_region} elements, the mesh in the filaments has been adjusted.")
                return dict(amplitude_dependent_meshing=True, field_penetration_distance=field_penetration_distance)

        return dict(amplitude_dependent_meshing=False, field_penetration_distance=1e10)

    def evaluate_frequency_dependent_meshing(self):
        """
        Evaluates the need for frequency-dependent meshing based on the skin depth due to the applied magnetic field's frequency.

        This method determines if the frequency of the applied magnetic field is high enough to confine the currents to a thin layer near the surface of the strand.
        A fine mesh is required in this region to capture current variations accurately, while a coarser mesh can suffice in the strand center.
        The method calculates the skin depth using the field frequency and the matrix resistivity, then approximates the number of elements within this depth.
        If the calculated number is less than desired, it indicates that frequency-dependent meshing adjustments are needed.

        :return: A dictionary containing:
            - "frequency_dependent_meshing" (bool): Indicates whether frequency-dependent meshing adjustments are necessary.
            - "skin_depth" (float): The calculated skin depth, which informs how the mesh should be adjusted to accurately model current variations.
        :rtype: Dict[str, Union[bool, float]]
        """
        if self.cacdm.mesh.matrix.rate_dependent_scaling_matrix and not self.cacdm.geometry.io_settings.load.load_from_yaml:
            matrix_mesh_options = self.cacdm.mesh.matrix

            filament_radius = self.geometry_class.filaments[0][0].rad

            mesh_size_matrix_inner = filament_radius * matrix_mesh_options.mesh_size_matrix_ratio_inner
            mesh_size_matrix_middle = filament_radius * matrix_mesh_options.mesh_size_matrix_ratio_middle
            mesh_size_matrix_outer = filament_radius * matrix_mesh_options.mesh_size_matrix_ratio_outer

            matrix = self.geometry_class.matrix

            rho_matrix = 1.81e-10  # self.cacdm.solve.material_properties.matrix.resistivity.constant
            mu0 = np.pi * 4e-7
            skin_depth = np.sqrt(rho_matrix / (np.pi * mu0 * self.cacdm.solve.source_parameters.sine.frequency)) * self.cacdm.mesh.matrix.skindepth_scaling_factor
            # Function which approximates number of elements in a range given a linearly interpolated mesh size.
            number_of_elements_in_range = lambda a, b, x0, x1: np.log(a * x1 + b) / a - np.log(a * x0 + b) / a if a != 0 else (x1 - x0) / b

            # If the skindepth is smaller than the outer matrix, we only evaluate the outer matrix field to approximate number of elements in skindepth.
            if skin_depth <= matrix[-1].rad - matrix[-2].rad:
                a = (mesh_size_matrix_outer - mesh_size_matrix_middle) / (matrix[-1].rad - matrix[-2].rad)
                b = mesh_size_matrix_middle
                elements_in_skindepth = number_of_elements_in_range(a, b, matrix[-1].rad - matrix[-2].rad - skin_depth, matrix[-1].rad - matrix[-2].rad)

            elif skin_depth > matrix[-1].rad - matrix[-2].rad and skin_depth < matrix[-1].rad:
                # If the skindepth is larger than the outer matrix, we evaluate the inner and outer matrix field to approximate number of elements in skindepth.
                a1 = (mesh_size_matrix_middle - mesh_size_matrix_inner) / (matrix[-2].rad)
                b1 = mesh_size_matrix_middle
                a2 = (mesh_size_matrix_outer - mesh_size_matrix_middle) / (matrix[-1].rad - matrix[-2].rad)
                b2 = mesh_size_matrix_middle
                elements_in_skindepth = number_of_elements_in_range(a1, b1, matrix[-1].rad - skin_depth, matrix[-2].rad) + number_of_elements_in_range(a2, b2, 0, matrix[-1].rad - matrix[-2].rad)

            else:  # If the skindepth is greater than the matrix radius we do not want to act, and set the number of elements in skindepth to a high number.
                elements_in_skindepth = 1e10

            desired_elements_in_skindepth = self.cacdm.mesh.matrix.desired_elements_in_skindepth

            if elements_in_skindepth < desired_elements_in_skindepth:
                print(f"The skindepth of the matrix is expected to contain only {round(elements_in_skindepth, 3)} elements. The mesh in the matrix has been adjusted to ensure at least {desired_elements_in_skindepth} elements in the skindepth.")
                return dict(frequency_dependent_meshing=True, skin_depth=skin_depth)

        return dict(frequency_dependent_meshing=False, skin_depth=1e10)

    def matrix_field(self):
        """
        Creates a mesh size field for the matrix as a combination of three fields:
        - A distance-based interpolation between the matrix center and partition boundaries. The mesh size is linearly interpolated from the center to the boundary of the second matrix partition, and then to the outer matrix boundary.
        - Adjustments near the filaments to ensure a smooth transition from the filament mesh to the matrix mesh.
        - Frequency-dependent adjustments to capture skin depth effects.

        :return: The tag of the composite mesh size field created for the matrix.
        :rtype: int
        """
        matrix_mesh_options = self.cacdm.mesh.matrix
        # Choose the largest distance from the center of mass of the filaments to the filament boundary as the filament radius.
        # This approximation is done to account for the fact that the filaments may not be circular, but can have any shape.
        filament_rad = 0
        for layer in self.geometry_class.filaments:
            for filament in layer:
                center_of_mass = gmsh.model.occ.get_center_of_mass(2, filament.surface_tag)
                for curve in filament.boundary_curves:
                    r = max([np.linalg.norm(np.array(center_of_mass) - curve.P1.pos), np.linalg.norm(np.array(center_of_mass) - curve.P2.pos)])
                    if r > filament_rad:
                        filament_rad = r

        mesh_size_matrix_inner = filament_rad * matrix_mesh_options.mesh_size_matrix_ratio_inner
        mesh_size_matrix_middle = filament_rad * matrix_mesh_options.mesh_size_matrix_ratio_middle
        mesh_size_matrix_outer = filament_rad * matrix_mesh_options.mesh_size_matrix_ratio_outer

        filament_edge_points = []
        for layer in self.geometry_class.filaments:
            for filament in layer:
                for curve in filament.boundary_curves:
                    filament_edge_points.append(curve.P1)
                    filament_edge_points.append(curve.P2)
        filament_outer_point = max(filament_edge_points, key=lambda p: np.linalg.norm(p.pos))
        # Distance from the outermost filament edge to the center of the matrix
        # This is done instead of referencing the middle matrix radius, to be able to mesh arbitrary geometries.
        filament_outer_point_dist = np.linalg.norm(filament_outer_point.pos)

        matrix = self.geometry_class.matrix
        matrix_outer_point_dist = max([np.linalg.norm(p.pos) for curve in matrix[-1].boundary_curves for p in [curve.P1, curve.P2]])  # Distance from the outermost matrix edge to the center of the matrix

        matrix_mesh_size_fields = []

        # 'Distance from matrix center'- field:
        dist_from_center_field = gmsh.model.mesh.field.add("MathEval")
        gmsh.model.mesh.field.setString(dist_from_center_field, "F", "sqrt(x^2 + y^2)")

        # Mesh size-field in the middle partition of the matrix. The mesh size is large at the center and decreases linearily towards the edge of the middle matrix.
        interpField_innerToMiddle = gmsh.model.mesh.field.add("Threshold")
        gmsh.model.mesh.field.setNumber(interpField_innerToMiddle, "InField", dist_from_center_field)
        gmsh.model.mesh.field.setNumber(interpField_innerToMiddle, "SizeMin", mesh_size_matrix_inner)
        gmsh.model.mesh.field.setNumber(interpField_innerToMiddle, "SizeMax", mesh_size_matrix_middle)
        gmsh.model.mesh.field.setNumber(interpField_innerToMiddle, "DistMin", 0)
        gmsh.model.mesh.field.setNumber(interpField_innerToMiddle, "DistMax", filament_outer_point_dist)

        # Restrict the middle field to the inner and middle matrix (only middle matrix in the case where we have a center filament and thus no inner matrix).
        middle_matrix_field = gmsh.model.mesh.field.add("Restrict")
        gmsh.model.mesh.field.setNumber(middle_matrix_field, "InField", interpField_innerToMiddle)
        gmsh.model.mesh.field.setNumbers(middle_matrix_field, "SurfacesList", [partition.surface_tag for partition in matrix[:-1]])
        matrix_mesh_size_fields.append(middle_matrix_field)

        # Mesh size-field in the outer partition of the matrix. The mesh size is small at the edge of the middle matrix and increases towards the outer edge.
        interpField_middleToOuter = gmsh.model.mesh.field.add("Threshold")
        gmsh.model.mesh.field.setNumber(interpField_middleToOuter, "InField", dist_from_center_field)
        gmsh.model.mesh.field.setNumber(interpField_middleToOuter, "SizeMin", mesh_size_matrix_middle)
        gmsh.model.mesh.field.setNumber(interpField_middleToOuter, "SizeMax", mesh_size_matrix_outer)
        gmsh.model.mesh.field.setNumber(interpField_middleToOuter, "DistMin", filament_outer_point_dist)
        gmsh.model.mesh.field.setNumber(interpField_middleToOuter, "DistMax", matrix_outer_point_dist)

        # Restric the outer field to the outer matrix partition:
        outer_matrix_field = gmsh.model.mesh.field.add("Restrict")
        gmsh.model.mesh.field.setNumber(outer_matrix_field, "InField", interpField_middleToOuter)
        gmsh.model.mesh.field.setNumbers(outer_matrix_field, "SurfacesList", [matrix[-1].surface_tag])
        matrix_mesh_size_fields.append(outer_matrix_field)

        # The last field adjusts the matrix mesh size with respect to the distance from the filaments. The reason is that the filaments typically has a finer mesh than the matrix and
        # the large mesh size gradient at the boundary between the matrix and the filaments can lead to a bad quality mesh. We thus want to gradually refine the mesh in the matrix close to the filaments.
        # This is done by interpolating the mesh size based on the distance to the filament boundaries.
        meshSize_by_filament_field = self.matrix_threshold_to_filament_field([filament for layer in self.geometry_class.filaments for filament in layer])
        matrix_mesh_size_fields.append(meshSize_by_filament_field)

        frequency_dependent_meshing, skin_depth = self.evaluate_frequency_dependent_meshing().values()

        if frequency_dependent_meshing:
            # If the skindepth only consists of a few elements, we add an additional mesh size field in the matrix. This field is large outside of the skindepth, but
            # in the skindepth it is defined as the constant field which gives the skindepth the 'desired number of elements'. In between the two regions we interpolate between the two values.
            # print(f"The skindepth of the matrix is expected to contain only {round(elements_in_skindepth, 3)} elements. The mesh in the matrix has been adjusted to ensure at least {desired_elements_in_skindepth} elements in the skindepth.")

            circular_field = gmsh.model.mesh.field.add("Ball")
            gmsh.model.mesh.field.setNumber(circular_field, "Radius", (matrix[-1].rad - skin_depth) * 0.85)
            # gmsh.model.mesh.field.setNumber(circular_field, "Thickness", (matrix[-1].rad-skin_depth)*0.15)
            gmsh.model.mesh.field.setNumber(circular_field, "VIn", mesh_size_matrix_inner)
            gmsh.model.mesh.field.setNumber(circular_field, "VOut", (skin_depth) / self.cacdm.mesh.matrix.desired_elements_in_skindepth)

            # -- Restrict the mesh size field to the matrix and the filaments not in the skindepth region -- #
            filaments_not_in_skindepth = [filament for layer in self.geometry_class.filaments for filament in layer if np.linalg.norm(filament.center_point.pos) < self.geometry_class.matrix[-1].rad - 2 * skin_depth]

            circular_field_restricted = gmsh.model.mesh.field.add("Restrict")
            gmsh.model.mesh.field.setNumber(circular_field_restricted, "InField", circular_field)
            gmsh.model.mesh.field.setNumbers(circular_field_restricted, "SurfacesList", [partition.surface_tag for partition in matrix] + [filament.surface_tag for filament in filaments_not_in_skindepth])
            # -- -- #

            self.cacdm.mesh.matrix.mesh_size_matrix_ratio_outer = skin_depth / self.cacdm.mesh.matrix.desired_elements_in_skindepth * 1 / filament_rad

            filaments_in_skindepth = [filament for layer in self.geometry_class.filaments for filament in layer if np.linalg.norm(filament.center_point.pos) > self.geometry_class.matrix[-1].rad - 2 * skin_depth]
            meshSize_by_filament_field = self.matrix_threshold_to_filament_field(filaments_in_skindepth)  # Redefine the interpolation field to apply only to the filaments in the skindepth region.

            matrix_meshSize_field = gmsh.model.mesh.field.add("Min")
            gmsh.model.mesh.field.setNumbers(matrix_meshSize_field, "FieldsList", [circular_field_restricted, meshSize_by_filament_field])
            return matrix_meshSize_field

        # Combine all the matrix mesh size fields by selecting the minimum value of all fields.
        matrix_meshSize_field = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(matrix_meshSize_field, "FieldsList", matrix_mesh_size_fields)

        return matrix_meshSize_field

    def air_field(self):
        """
        Generates a mesh size field for the air domain surrounding the model.
        The field linearly interpolates between the mesh size at the outer boundary of the matrix and the air boundary.

        :return: The tag of the created mesh size field for the air domain.
        :rtype: int
        """
        # Choose the largest distance from the center of mass of the filaments to the filament boundary as the filament radius.
        # This approximation is done to account for the fact that the filaments may not be circular, but can have any shape.
        filament_rad = 0
        for layer in self.geometry_class.filaments:
            for filament in layer:
                center_of_mass = gmsh.model.occ.get_center_of_mass(2, filament.surface_tag)
                for curve in filament.boundary_curves:
                    r = max([np.linalg.norm(np.array(center_of_mass) - curve.P1.pos), np.linalg.norm(np.array(center_of_mass) - curve.P2.pos)])
                    if r > filament_rad:
                        filament_rad = r

        mesh_size_outer_matrix = filament_rad * self.cacdm.mesh.matrix.mesh_size_matrix_ratio_outer
        mesh_size_air_boundary = filament_rad * self.cacdm.mesh.air.max_mesh_size_ratio

        if self.geometry_class.air_composition:
            air_outer_boundary_curves = self.geometry_class.air_composition.boundary_curves
            air_inner_boundary_curves = sum(self.geometry_class.air_composition.inner_boundary_curves, [])
        else:
            air_outer_boundary_curves = self.geometry_class.air[0].boundary_curves
            air_inner_boundary_curves = sum(self.geometry_class.air[0].inner_boundary_curves, [])

        dist_from_outer_air_boundary_field = gmsh.model.mesh.field.add("Distance")
        gmsh.model.mesh.field.setNumbers(dist_from_outer_air_boundary_field, "CurvesList", [curve.tag for curve in air_outer_boundary_curves])

        dist_from_matrix_boundary = gmsh.model.mesh.field.add("Distance")
        gmsh.model.mesh.field.setNumbers(dist_from_matrix_boundary, "CurvesList", [curve.tag for curve in air_inner_boundary_curves])

        air_field = gmsh.model.mesh.field.add("MathEval")
        gmsh.model.mesh.field.setString(
            air_field,
            "F",
            f"( {mesh_size_air_boundary} * F{dist_from_matrix_boundary} + {mesh_size_outer_matrix} * F{dist_from_outer_air_boundary_field} ) / ( F{dist_from_matrix_boundary} + F{dist_from_outer_air_boundary_field} )"
        )
        return air_field

    def load_geometry_class(self, geom_folder):
        """
        Loads the TwistedStrand geometry class from a .pkl file saved within the specified geometry folder.
        The geometry class contains all the information about the strand geometry, facilitating mesh generation.

        :param geom_folder: The path to the folder where the geometry class .pkl file is saved.
        :type geom_folder: str

        :return: An instance of the TwistedStrand geometry class.
        :rtype: object
        """
        geom_save_file = os.path.join(geom_folder, f'{self.magnet_name}.pkl')

        with open(geom_save_file, "rb") as geom_save_file:  # Unnecessary to return geom instead of setting self.geometry_class
            geom = pickle.load(geom_save_file)
        return geom

    def generate_mesh(self, geom_folder):
        """
        Generates the mesh for the entire model geometry based on combined mesh size fields.

        The method generates mesh size fields for the filament, matrix, and air domains separately and combines these fields to define a unified mesh size field for the full geometry.
        The combined field is applied as the background mesh size field.

        :param geom_folder: The path to the folder containing the saved geometry class (.pkl file). This folder is used to load the geometry details required for mesh generation.
        :type geom_folder: str
        """

        # So far: Adds physical groups and generates an automatic mesh. To be further developed.
        self.geometry_class: TwistedStrand = self.load_geometry_class(geom_folder)
        self.geometry_class.update_tags()
        self.geometry_class.add_physical_groups()

        total_filament_boundary_distance_field = self.filament_field()
        matrixField = self.matrix_field()
        airField = self.air_field()

        total_meshSize_field = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(total_meshSize_field, "FieldsList", [total_filament_boundary_distance_field, matrixField, airField])

        gmsh.model.mesh.field.setAsBackgroundMesh(total_meshSize_field)

        gmsh.option.setNumber("Mesh.MeshSizeFactor", self.cacdm.mesh.scaling_global)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)

        # enforce center nodes
        if self.fdm.magnet.mesh.matrix.force_center_symmetry:
            dist = self.geometry_class.filaments[0][0].center_point.pos[0] * 5e-2  # 5% of inner filament distance seems sufficient
            center = self.geometry_class.matrix[0].center_point.pos
            d_tag = gmsh.model.occ.add_point(center[0], center[1] - dist, center[2])
            u_tag = gmsh.model.occ.add_point(center[0], center[1] + dist, center[2])
            l_tag = gmsh.model.occ.add_point(center[0] - dist, center[1], center[2])
            r_tag = gmsh.model.occ.add_point(center[0] + dist, center[1], center[2])
            outDimTags, _ = gmsh.model.occ.fragment([(2, self.geometry_class.matrix[0].surface_tag)], [(0, gmsh.model.occ.add_point(center[0], center[1], center[2])), (0, d_tag), (0, u_tag), (0, l_tag), (0, r_tag)])  #
            gmsh.model.occ.synchronize()
            # update the physical surface
            gmsh.model.removePhysicalGroups([(2, self.geometry_class.matrix[0].physical_surface_tag)])
            self.geometry_class.matrix[0].physical_surface_tag = gmsh.model.add_physical_group(2, [outDimTags[0][1]], tag=self.geometry_class.matrix[0].physical_surface_tag, name='Surface: Matrix partition 0')

        gmsh.model.mesh.generate(2)

    def generate_cuts(self):
        """
            Computes the cuts for imposing global quantities.
        """
        # Computes cuts, as needed for imposing global quantities
        if self.verbose:
            print('(Co)homology computation')

        # a) Cut for the total current intensity (through OmegaCC)
        if self.fdm.magnet.geometry.type == 'periodic_square':
            # only enforce periodic mesh - cut already defined in composite geometry
            self.set_periodic_mesh()
        else:
            # cohomology cut for single air domain
            air_region = self.geometry_class.air[0]
            gmsh.model.mesh.addHomologyRequest("Homology", domainTags=[air_region.physical_inner_boundary_tags[0]], dims=[1])
            if self.fdm.magnet.geometry.type == 'strand_only':
                gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[air_region.physical_surface_tag], dims=[1])
            elif self.fdm.magnet.geometry.type == 'coil':
                # add semicircle arc as sudomain to force homology cut onto semicircle diameter
                gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[air_region.physical_surface_tag], subdomainTags=[air_region.physical_cohomology_subdomain], dims=[1])

            cuts = gmsh.model.mesh.computeHomology()
            gmsh.model.mesh.clearHomologyRequests()
            gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains", str(cuts[1][1]))
            gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains2", str(cuts[0][1]))
            gmsh.plugin.run("HomologyPostProcessing")
            air_region.strand_bnd_cut_tag = cuts[1][1] + 1  # The cut tag for the strand boundary

        # b) Cuts for the individual filaments
        for layer in self.geometry_class.filaments:
            for filament in layer:
                filBnd = filament.physical_boundary_tag
                gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[filBnd], dims=[1])
        cuts = gmsh.model.mesh.computeHomology()

        filaments = sum(self.geometry_class.filaments, [])
        for i in range(len(cuts)):
            filaments[i].cut_tag = cuts[i][1]

    def set_periodic_mesh(self):
        """
        Enforces symmetric air mesh by mirroring the node positions from bottom to top and left to right.
        """
        air = self.geometry_class.air
        # link left and right
        dx, dy, dz = air[0].cut_curves[1].P2.pos - air[2].cut_curves[0].P2.pos
        gmsh.model.mesh.set_periodic(1, [self.geometry_class.air_composition.physical_left_boundary_tag], [self.geometry_class.air_composition.physical_right_boundary_tag], [1, 0, 0, dx, 0, 1, 0, dy, 0, 0, 1, dz, 0, 0, 0, 1])
        # link bottom and top
        dx, dy, dz = air[0].cut_curves[0].P2.pos - air[3].cut_curves[1].P2.pos
        gmsh.model.mesh.set_periodic(1, [self.geometry_class.air_composition.physical_bottom_boundary_tag], [self.geometry_class.air_composition.physical_top_boundary_tag], [1, 0, 0, dx, 0, 1, 0, dy, 0, 0, 1, dz, 0, 0, 0, 1])

    def generate_regions_file(self):
        """
        Generates a .regions file for the GetDP solver, containing all necessary information about the model.
        The regions model contains data about physical surfaces, boundaries, points and cuts and is stored in the mesh folder.
        """
        regions_model = RegionsModel()

        """ -- Initialize data -- """
        regions_model.powered["Filaments"] = RegionsModelFiQuS.Powered()
        regions_model.powered["Filaments"].vol.numbers = []  # Filament physical surfaces tags
        regions_model.powered["Filaments"].vol.names = []  # Filament physical surfaces names
        regions_model.powered["Filaments"].surf.numbers = []  # Filament physical boundaries tags
        regions_model.powered["Filaments"].surf.names = []  # Filament physical boundaries names
        regions_model.powered["Filaments"].cochain.numbers = []  # Filament boundary cut tags
        regions_model.powered["Filaments"].curve.names = []  # Stores physical points at filament boundary (to fix phi=0)
        regions_model.powered["Filaments"].curve.numbers = []  # Stores physical points at filament boundary (to fix phi=0)

        regions_model.powered["Filaments"].surf_in.numbers = []  # Filament holes physical tags
        regions_model.powered["Filaments"].surf_in.names = []  # Filament holes physical names

        regions_model.insulator.curve.numbers = []  # Filament holes curves physical tags
        regions_model.insulator.curve.names = []  # Filament holes curves physical names

        regions_model.induced["Matrix"] = RegionsModelFiQuS.Induced()
        regions_model.induced["Matrix"].vol.numbers = []  # Matrix partition physical surfaces tags
        regions_model.induced["Matrix"].vol.names = []  # Matrix partition physical surfaces names
        regions_model.induced["Matrix"].surf_in.numbers = []  # Matrix partition physical boundaries tags
        regions_model.induced["Matrix"].surf_in.names = []  # Matrix partition physical boundaries names
        regions_model.induced["Matrix"].surf_out.numbers = []  # Strand physical outer boundary tag
        regions_model.induced["Matrix"].surf_out.names = []  # Strand physical outer boundary name
        regions_model.induced["Matrix"].cochain.numbers = []  # Strand outer boundary cut tag
        regions_model.induced["Matrix"].cochain.names = []  # Strand outer boundary cut name
        """ -- -- """

        for layer_i, layer in enumerate(self.geometry_class.filaments):
            for filament_j, filament in enumerate(layer):
                regions_model.powered["Filaments"].vol.numbers.append(filament.physical_surface_tag)  # Surfaces in powered.vol
                if self.cacdm.geometry.io_settings.load.load_from_yaml:
                    regions_model.powered["Filaments"].vol.names.append(filament.material)
                else:
                    regions_model.powered["Filaments"].vol.names.append(filament.physical_surface_name)

                regions_model.powered["Filaments"].surf.numbers.append(filament.physical_boundary_tag)  # Boundaries in powered.surf
                regions_model.powered["Filaments"].surf.names.append(filament.physical_boundary_name)

                regions_model.powered["Filaments"].cochain.numbers.append(filament.cut_tag)

                # Add physical point at filament boundary to fix phi=0
                regions_model.powered["Filaments"].curve.names.append(f"EdgePoint: filament_{layer_i + 1}_{filament_j + 1}")
                regions_model.powered["Filaments"].curve.numbers.append(filament.physicalEdgePointTag)

        for layer in self.geometry_class.filament_holes:
            for hole in layer:
                regions_model.powered["Filaments"].surf_in.numbers.append(hole.physical_surface_tag)
                regions_model.insulator.curve.numbers.append(hole.physical_boundary_tag)
                if self.cacdm.geometry.io_settings.load.load_from_yaml:
                    regions_model.powered["Filaments"].surf_in.names.append(hole.material)
                    regions_model.insulator.curve.names.append(hole.material)
                else:
                    regions_model.powered["Filaments"].surf_in.names.append(hole.physical_surface_name)
                    regions_model.insulator.curve.names.append(hole.physical_boundary_name)
                # Add physical point at hole boundary (inner filament boundary) to fix phi=0
                regions_model.powered["Filaments"].curve.numbers.append(hole.physicalEdgePointTag)

        for matrixPartition in self.geometry_class.matrix:
            regions_model.induced["Matrix"].vol.numbers.append(matrixPartition.physical_surface_tag)
            if self.cacdm.geometry.io_settings.load.load_from_yaml:
                regions_model.induced["Matrix"].vol.names.append(matrixPartition.material)
            else:
                regions_model.induced["Matrix"].vol.names.append(matrixPartition.physical_surface_name)

            regions_model.induced["Matrix"].surf_in.numbers.append(matrixPartition.physical_boundary_tag)
            regions_model.induced["Matrix"].surf_in.names.append(matrixPartition.physical_boundary_name)

        # Add manual cut regions depending on the selected geometry type
        if self.fdm.magnet.geometry.type == 'periodic_square':
            regions_model.air.cochain.numbers = self.geometry_class.air_composition.physical_cuts
            regions_model.air.cochain.names = ["Air vertical cut tag", "vertical cut strand boundary", "Air horizontal cut tag", "horizontal cut strand boundary"]
            air_region = self.geometry_class.air_composition

            regions_model.induced["Domain"] = RegionsModelFiQuS.Induced()
            regions_model.induced["Domain"].surf_out.numbers = [air_region.physical_top_boundary_tag, air_region.physical_bottom_boundary_tag, air_region.physical_left_boundary_tag, air_region.physical_right_boundary_tag]
            regions_model.induced["Domain"].surf_out.names = ["Domain boundary top", "Domain boundary bottom", "Domain boundary left", "Domain boundary right"]
        elif self.fdm.magnet.geometry.type == 'strand_only' or self.fdm.magnet.geometry.type == 'coil':
            regions_model.induced["Matrix"].cochain.numbers.append(self.geometry_class.air[0].strand_bnd_cut_tag)
            regions_model.induced["Matrix"].cochain.names.append("Strand boundary cut tag")
            air_region = self.geometry_class.air[0]

        regions_model.induced["Matrix"].surf_out.numbers.append(air_region.physical_inner_boundary_tags[0])
        regions_model.induced["Matrix"].surf_out.names.append(air_region.physical_inner_boundary_names[0])

        regions_model.air.vol.number = air_region.physical_surface_tag
        regions_model.air.vol.name = air_region.physical_surface_name

        regions_model.air.surf.number = air_region.physical_boundary_tag
        regions_model.air.surf.name = air_region.physical_boundary_name

        # Add physical gauge point in air to fix phi=0
        regions_model.air.point.names = ["Point at air boundary"]
        regions_model.air.point.numbers = [air_region.strand_bnd_physicalEdgePointTag]

        # HTCondor hack - store pickle file in geometry and mesh folder
        self.geometry_class.save(os.path.join(self.mesh_folder, f'{self.magnet_name}.pkl'))  # Save the geometry-class to a pickle file
        FilesAndFolders.write_data_to_yaml(self.regions_file, regions_model.model_dump())