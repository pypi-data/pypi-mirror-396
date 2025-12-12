import timeit
import logging
import os
import subprocess
import re
import pandas as pd
import pickle
import numpy as np
import gmsh

from fiqus.utils.Utils import GmshUtils, FilesAndFolders
from fiqus.data.RegionsModelFiQuS import RegionsModel
import fiqus.data.DataFiQuSConductor as geom
from fiqus.geom_generators.GeometryConductorAC_Strand import TwistedStrand

from fiqus.pro_assemblers.ProAssembler import ASS_PRO

logger = logging.getLogger('FiQuS')


class Solve:
    def __init__(self, fdm, GetDP_path, geometry_folder, mesh_folder, verbose=True):
        self.fdm = fdm
        self.cacdm = fdm.magnet
        self.GetDP_path = GetDP_path
        self.solution_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name
        self.geometry_folder = geometry_folder
        self.mesh_folder = mesh_folder
        self.mesh_file = os.path.join(self.mesh_folder, f"{self.magnet_name}.msh")
        self.pro_file = os.path.join(self.solution_folder, f"{self.magnet_name}.pro")
        self.regions_file = os.path.join(mesh_folder, f"{self.magnet_name}.regions")

        self.verbose = verbose
        self.gu = GmshUtils(self.solution_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

        self.ass_pro = ASS_PRO(os.path.join(self.solution_folder, self.magnet_name))
        self.regions_model = FilesAndFolders.read_data_from_yaml(self.regions_file, RegionsModel)
        self.material_properties_model = None

        self.ed = {}  # excitation dictionary

        gmsh.option.setNumber("General.Terminal", verbose)

    def read_excitation(self, inputs_folder_path):
        """
        Function for reading a CSV file for the 'from_file' excitation case.

        :param inputs_folder_path: The full path to the folder with input files.
        :type inputs_folder_path: str
        """
        if self.cacdm.solve.source_parameters.source_type == 'piecewise' and self.cacdm.solve.source_parameters.piecewise.source_csv_file:
            input_file = os.path.join(inputs_folder_path, self.cacdm.solve.source_parameters.piecewise.source_csv_file)
            print(f'Using excitation from file: {input_file}')
            df = pd.read_csv(input_file, delimiter=',', engine='python')
            excitation_time = df['time'].to_numpy(dtype='float').tolist()
            self.ed['time'] = excitation_time
            excitation_value = df['value'].to_numpy(dtype='float').tolist()
            self.ed['value'] = excitation_value

    def get_solution_parameters_from_yaml(self, inputs_folder_path):
        """
        Function for reading material properties from the geometry YAML file.

        This reads the 'solution' section of the YAML file and stores it in the solution folder.
        This could also be a place to change the material properties in the future.

        :param inputs_folder_path: The full path to the folder with input files.
        :type inputs_folder_path: str
        """
        # load the geometry class from the .pkl file
        geom_save_file = os.path.join(self.mesh_folder, f'{self.magnet_name}.pkl')
        with open(geom_save_file, "rb") as geom_save_file:
            geometry_class: TwistedStrand = pickle.load(geom_save_file)

        if self.cacdm.geometry.io_settings.load.load_from_yaml:
            # If the geometry is loaded from a YAML file, we need to read the solution parameters (material properties and surfaces to exclude from IP-problem) from the YAML file.
            input_yaml_file = os.path.join(inputs_folder_path, self.cacdm.geometry.io_settings.load.filename)
            Conductor_dm = FilesAndFolders.read_data_from_yaml(input_yaml_file, geom.Conductor)
            solution_parameters = Conductor_dm.Solution

            # The geometry YAML file lists surfaces to exclude from the TI problem by their IDs. Here we convert these IDs to Gmsh physical surface tags.
            # This is done by comparing the outer boundary points of the surfaces to exclude with the outer boundary points of the matrix partitions.
            surfaces_excluded_from_TI_tags = []

            for surface_ID in solution_parameters.Surfaces_excluded_from_TI:  # 1) Find the outer boundary points of the surfaces to exclude
                outer_boundary_points_a = []
                outer_boundary_curves_a = Conductor_dm.Geometry.Areas[surface_ID].Boundary
                for curve_ID in outer_boundary_curves_a:
                    curve = Conductor_dm.Geometry.Curves[curve_ID]
                    for point_ID in curve.Points:
                        point = Conductor_dm.Geometry.Points[point_ID]
                        outer_boundary_points_a.append(tuple(point.Coordinates))

                for matrix_partition in geometry_class.matrix:  # 2) Find the outer boundary points of the matrix partitions
                    outer_boundary_points_b = []
                    outer_boundary_curves_b = matrix_partition.boundary_curves
                    if len(outer_boundary_curves_b) == len(outer_boundary_curves_a):  # If the number of boundary curves is different, the surfaces are not the same
                        for curve in outer_boundary_curves_b:
                            for point in curve.points:
                                outer_boundary_points_b.append(tuple(point.pos))

                        if np.allclose(sorted(outer_boundary_points_a), sorted(outer_boundary_points_b)):  # If the outer boundary points are the same, the surfaces are the same
                            surfaces_excluded_from_TI_tags.append(matrix_partition.physical_surface_tag)  # 3) Add the physical surface tag to the list of surfaces to exclude
                            break

            solution_parameters.Surfaces_excluded_from_TI = surfaces_excluded_from_TI_tags  # Replace the surface IDs with the physical surface tags

        else:
            # If the geometry is not loaded from a YAML file, we initialize the solution parameters with an empty model, in which we may store the resistances of the diffusion barriers.
            solution_parameters = geom.SolutionParameters()

        if self.cacdm.solve.diffusion_barriers.enable:
            # If the diffusion barriers are enabled, we either read the resistances of the barriers from the geometry YAML file or calculate them based on the material properties specified in the input YAML file.
            if self.cacdm.geometry.io_settings.load.load_from_yaml and self.cacdm.solve.diffusion_barriers.load_data_from_yaml:
                # If the diffusion barriers are enabled and the geometry YAML file provides information about the barriers, we can read the resistances from the YAML file.

                # If the file provides information about the diffusion barriers we determine the resistance associated with the barrier from: Material, Circumferences, Thicknesses and periodicity length, ell.
                # The code below loops trough all surfaces provided in the geometry file and determines which filaments each surface corresponds to.
                # The resistances of the barriers are then calculated and stored in the solution parameters data structure which is accessed by the .pro template.
                # The resistances are sorted by the physical surface tag of the surface to ensure that the order is consistent with the order of the surfaces in the .regions file.

                # 1) Loop through all the areas in the geometry file
                filament_barrier_resistances = []
                filament_barrier_areas = []
                for area_ID, area in Conductor_dm.Geometry.Areas.items():
                    # 2) If the area contains a BoundaryThickness, we continue
                    # print(f'Area ID: {area_ID}, area: {area}')
                    if area.BoundaryThickness:
                        # 3) We find the physical surface tag of the area by comparing the outer boundary points of the area with the outer boundary points of all surfaces
                        # surfaces = set(geometry_class.matrix + sum(geometry_class.filaments, [])) # All surfaces in the geometry
                        surfaces = set(sum(geometry_class.filaments, []))  # All surfaces in the geometry (only filaments are currently considered for diffusion barriers)
                        outer_boundary_points_a = []
                        outer_boundary_curves_a = area.Boundary
                        for curve_ID in outer_boundary_curves_a:
                            curve = Conductor_dm.Geometry.Curves[curve_ID]
                            for point_ID in curve.Points:
                                point = Conductor_dm.Geometry.Points[point_ID]
                                outer_boundary_points_a.append(tuple(point.Coordinates))

                        for surface in surfaces:
                            outer_boundary_points_b = []
                            outer_boundary_curves_b = surface.boundary_curves
                            if len(outer_boundary_curves_b) == len(outer_boundary_curves_a):
                                for curve in outer_boundary_curves_b:
                                    for point in curve.points:
                                        outer_boundary_points_b.append(tuple(point.pos))

                                if np.allclose(sorted(outer_boundary_points_a), sorted(outer_boundary_points_b)):
                                    # 4) If the outer boundary points are the same we have found the surface corresponding to the area
                                    # We calculate the resistance of the barrier and add it to the list of filament resistances
                                    if self.cacdm.solve.formulation_parameters.two_ell_periodicity:
                                        correctionFactor = 0.827
                                        ell = 2 * correctionFactor * self.fdm.conductors[self.cacdm.solve.conductor_name].strand.fil_twist_pitch / 6
                                    else:
                                        correctionFactor = 0.9549
                                        ell = correctionFactor * self.fdm.conductors[self.cacdm.solve.conductor_name].strand.fil_twist_pitch / 6
                                    # If the .yaml contains information about the material of the diffusion barrier, use the given material property for this material...
                                    if area.BoundaryMaterial:
                                        material = Conductor_dm.Solution.Materials[area.BoundaryMaterial]
                                        if material.Resistivity:
                                            resistivity = float(material.Resistivity)
                                        else:
                                            resistivity = self.cacdm.solve.diffusion_barriers.resistivity
                                    # ... otherwise, use the single (unique) value given in the model .yaml
                                    else:
                                        resistivity = self.cacdm.solve.diffusion_barriers.resistivity
                                    circumference = surface.get_circumference()
                                    thickness = area.BoundaryThickness

                                    resistance = float(resistivity * thickness / (ell * circumference))  # R = rho * L / A. A is chosen as the area of the surface of the filament over the periodicity length
                                    filament_barrier_resistances.append((surface.physical_surface_tag, resistance))  # Add the resistance to the list of filament resistances (along with the physical surface tag)
                                    filament_barrier_areas.append(float(thickness * circumference))

                                    surfaces = surfaces - {surface}  # Remove the surface from the set of surfaces to speed up the search
                                    break

                filament_barrier_resistances.sort(key=lambda x: x[0])  # Sort the resistances by the physical surface tags to ensure that the order is consistent with the order of the surfaces in the .regions file

                solution_parameters.DiffusionBarriers.FilamentResistances = [resistance for _, resistance in filament_barrier_resistances]
                solution_parameters.DiffusionBarriers.DiffusionBarrierAreas = filament_barrier_areas

            else:
                # If the diffusion barriers are enabled but should not be read from any geometry YAML file, we need to calculate the resistances of the barriers according to the material properties specified in the YAML file.
                # In this case we will also write a MaterialProperties.yaml file to the solution folder, but only with the resistances of the barriers.
                # Note that we do this for each filament individually, as the resistances of the barriers may differ between filaments if their circumferences are different.
                # The steps are the following:
                # 1) First we get the circumference of each filament.
                # 2) Then we calculate the resistance of the barrier for each filament, using the resistivity of the material, the thickness of the barrier, and the periodicity length, ell.
                # 3) We then write the resistances to the MaterialProperties.yaml file.

                if self.cacdm.solve.formulation_parameters.two_ell_periodicity:
                    correctionFactor = 0.827
                    ell = 2 * correctionFactor * self.fdm.conductors[self.cacdm.solve.conductor_name].strand.fil_twist_pitch / 6
                else:
                    correctionFactor = 0.9549
                    ell = correctionFactor * self.fdm.conductors[self.cacdm.solve.conductor_name].strand.fil_twist_pitch / 6
                barrier_resistivity = self.cacdm.solve.diffusion_barriers.resistivity
                barrier_thickness = self.cacdm.solve.diffusion_barriers.thickness

                filament_barrier_resistances = []  # List to store the resistances of the barriers
                filament_barrier_areas = []  # List to store the surface areas of the barriers
                for filament in sum(geometry_class.filaments, []):  # Loop through all filaments
                    circumference = filament.get_circumference()  # The circumference of the filament
                    resistance = float(barrier_resistivity * barrier_thickness / (ell * circumference))  # R = rho * L / A. A is determined as the area of the surface of the filament over the periodicity length
                    filament_barrier_resistances.append(resistance)  # Add the resistance to the list of resistances
                    filament_barrier_areas.append(float(barrier_thickness * circumference))  # Add the surface area to the list of resistances

                solution_parameters.DiffusionBarriers.FilamentResistances = filament_barrier_resistances  # Add the resistances to the solution parameters
                solution_parameters.DiffusionBarriers.DiffusionBarrierAreas = filament_barrier_areas  # Add the surface areas to the solution parameters

        if self.cacdm.solve.global_diffusion_barrier.enable:
            # 1) Retrieve the tag of the correct matrix partition, it should be the only one with filaments inside.
            # Here, we just take the partition with more than one internal boundary: it should be the correct one.
            for matrix_partition in geometry_class.matrix:
                # print(matrix_partition.inner_curve_loop_tags)
                if len(matrix_partition.inner_curve_loop_tags) > 1:
                    tag = matrix_partition.physical_boundary_tag
                    surface_tag = matrix_partition.physical_surface_tag
                    # print(tag)
                    break
            solution_parameters.GlobalDiffusionBarrier.RegionTag = tag
            solution_parameters.GlobalDiffusionBarrier.InternalRegionTag = surface_tag
            # 2) Compute the contact resistivity based on either the information in the .yaml input for geometry, or the data in the .yaml input for the main model
            if self.cacdm.geometry.io_settings.load.load_from_yaml and self.cacdm.solve.global_diffusion_barrier.load_data_from_yaml:
                # Find the corresponding surface from the .yaml input for geometry (the one with many inner surfaces)
                for area_ID, area in Conductor_dm.Geometry.Areas.items():
                    if len(area.InnerBoundaries) > 1:  # Same as above, we take the surface area which has more than one internal boundary, whose boundary should be the global diffusion barrier
                        thickness = area.BoundaryThickness
                        material = Conductor_dm.Solution.Materials[area.BoundaryMaterial]
                        if material.Resistivity:
                            resistivity = float(material.Resistivity)
                        else:
                            resistivity = self.cacdm.solve.global_diffusion_barrier.resistivity
                solution_parameters.GlobalDiffusionBarrier.ContactResistivity = resistivity * thickness
            else:
                solution_parameters.GlobalDiffusionBarrier.ContactResistivity = self.cacdm.solve.global_diffusion_barrier.resistivity * self.cacdm.solve.global_diffusion_barrier.thickness

        if self.cacdm.geometry.io_settings.load.load_from_yaml or self.cacdm.solve.diffusion_barriers.enable or self.cacdm.solve.global_diffusion_barrier.enable:
            # If the geometry is loaded from a YAML file or the diffusion barriers are enabled, we need to write these solution parameters to a data-structure in the solution folder, which can be read by the template.
            FilesAndFolders.write_data_to_yaml(os.path.join(self.solution_folder, "MaterialProperties.yaml"), solution_parameters.model_dump())
            self.material_properties_model = solution_parameters

        if self.cacdm.geometry.type == 'periodic_square' and not (self.cacdm.solve.source_parameters.sine.current_amplitude == 0.0):
            raise ValueError(
                f"FiQuS does not support periodic_square geometry type with non zero current amplitude!"
            )

    def assemble_pro(self):
        print("Assembling .pro file")
        self.ass_pro.assemble_combined_pro(template=self.cacdm.solve.pro_template, rm=self.regions_model, dm=self.fdm, ed=self.ed, mp=self.material_properties_model)

    def run_getdp(self, solve=True, postOperation=True, gui=False):

        command = ["-v2", "-verbose", str(self.fdm.run.verbosity_GetDP), "-mat_mumps_icntl_14", "100"]
        if solve:
            command += ["-solve", "MagDyn"]
        if self.cacdm.solve.formulation_parameters.formulation == "CATI" and self.cacdm.solve.formulation_parameters.dynamic_correction:
            command += ["-pos", "MagDyn", "MagDyn_dynCorr"]
        else:
            command += ["-pos", "MagDyn"]

        if self.cacdm.solve.general_parameters.noOfMPITasks:
            mpi_prefix = ["mpiexec", "-np", str(self.cacdm.solve.general_parameters.noOfMPITasks)]
        else:
            mpi_prefix = []

        startTime = timeit.default_timer()

        getdpProcess = subprocess.Popen(mpi_prefix + [self.GetDP_path, self.pro_file, "-msh", self.mesh_file] + command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        with getdpProcess.stdout:
            for line in iter(getdpProcess.stdout.readline, b""):
                line = line.decode("utf-8").rstrip()
                line = line.split("\r")[-1]
                if not "Test" in line:
                    if line.startswith("Info"):
                        parsedLine = re.sub(r"Info\s+:\s+", "", line)
                        logger.info(parsedLine)
                    elif line.startswith("Warning"):
                        parsedLine = re.sub(r"Warning\s+:\s+", "", line)
                        logger.warning(parsedLine)
                    elif line.startswith("Error"):
                        parsedLine = re.sub(r"Error\s+:\s+", "", line)
                        logger.error(parsedLine)
                        logger.error("Solving CAC failed.")
                        # raise Exception(parsedLine)
                    elif re.match("##", line):
                        logger.critical(line)
                    else:
                        logger.info(line)

        simulation_time = timeit.default_timer() - startTime
        # Save simulation time:
        if solve:
            logger.info(f"Solving CAC_1 has finished in {round(simulation_time, 3)} seconds.")
            with open(os.path.join(self.solution_folder, 'text_output', 'simulation_time.txt'), 'w') as file:
                file.write(str(simulation_time))

        if gui and ((postOperation and not solve) or (solve and postOperation and self.cacdm.postproc.pos_files.quantities is not [])):
            # gmsh.option.setNumber("Geometry.Volumes", 1)
            # gmsh.option.setNumber("Geometry.Surfaces", 1)
            # gmsh.option.setNumber("Geometry.Curves", 1)
            # gmsh.option.setNumber("Geometry.Points", 0)
            posFiles = [
                fileName
                for fileName in os.listdir(self.solution_folder)
                if fileName.endswith(".pos")
            ]
            for posFile in posFiles:
                gmsh.open(os.path.join(self.solution_folder, posFile))
            self.gu.launch_interactive_GUI()
        else:
            if gmsh.isInitialized():
                gmsh.clear()
                gmsh.finalize()

    def cleanup(self):
        """
            This function is used to remove .msh, .pre and .res files from the solution folder, as they may be large and not needed.
        """
        magnet_name = self.fdm.general.magnet_name
        cleanup = self.cacdm.postproc.cleanup

        if cleanup.remove_res_file:
            res_file_path = os.path.join(self.solution_folder, f"{magnet_name}.res")
            if os.path.exists(res_file_path):
                os.remove(res_file_path)
                logger.info(f"Removed {magnet_name}.res")

        if cleanup.remove_pre_file:
            pre_file_path = os.path.join(self.solution_folder, f"{magnet_name}.pre")
            if os.path.exists(pre_file_path):
                os.remove(pre_file_path)
                logger.info(f"Removed {magnet_name}.pre")

        if cleanup.remove_msh_file:
            msh_file_path = os.path.join(self.mesh_folder, f"{magnet_name}.msh")
            if os.path.exists(msh_file_path):
                os.remove(msh_file_path)
                logger.info(f"Removed {magnet_name}.msh")