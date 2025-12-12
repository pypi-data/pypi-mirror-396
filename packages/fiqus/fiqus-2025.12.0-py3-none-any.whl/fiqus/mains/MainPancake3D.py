import os
import sys
import math
import time as Time
import shutil
from copy import deepcopy
from enum import Enum

from fiqus.data.DataFiQuSPancake3D import (
    Pancake3DGeometry,
    Pancake3DMesh,
    Pancake3DSolve,
    Pancake3DPostprocess,
    Pancake3DSolveSaveQuantity,
)

from fiqus.geom_generators.GeometryPancake3DUtils import spiralCurve

if len(sys.argv) == 3:
    sys.path.insert(0, os.path.join(os.getcwd(), "steam-fiqus-dev"))

class direction(Enum):
    """
    A class to specify direction easily.
    """

    ccw = 0
    cw = 1
class Base:
    """
    Base class for geometry, mesh, and solution classes. It is created to avoid code
    duplication and to make the code more readable. Moreover, it guarantees that
    all the classes have the same fundamental methods and attributes.
    """

    def __init__(
        self,
        fdm,
        geom_folder=None,
        mesh_folder=None,
        solution_folder=None,
    ) -> None:
        """
        Define the fundamental attributes of the class.

        :param fdm: fiqus data model
        :param geom_folder: folder where the geometry related files are stored
        :type geom_folder: str
        :param mesh_folder: folder where the mesh related files are stored
        :type mesh_folder: str
        :param solution_folder: folder where the solution related files are stored
        :type solution_folder: str
        """

        self.magnet_name = fdm.general.magnet_name
        self.geom_folder = geom_folder
        self.mesh_folder = mesh_folder
        self.solution_folder = solution_folder

        self.dm = fdm  # Data model
        self.geo: Pancake3DGeometry = fdm.magnet.geometry  # Geometry data
        self.mesh: Pancake3DMesh = fdm.magnet.mesh  # Mesh data
        self.solve: Pancake3DSolve = fdm.magnet.solve  # Solve data
        self.pp: Pancake3DPostprocess = fdm.magnet.postproc  # Postprocess data

        self.geo_gui = False
        self.mesh_gui = False
        self.solve_gui = False
        self.python_postprocess_gui = False

        if fdm.run.launch_gui:
            if fdm.run.type == "start_from_yaml":
                self.python_postprocess_gui = True
            elif fdm.run.type == "geometry_only":
                self.geo_gui = True
            elif fdm.run.type == "mesh_only":
                self.mesh_gui = True
            elif fdm.run.type == "geometry_and_mesh":
                self.mesh_gui = True
            elif fdm.run.type == "solve_only":
                self.solve_gui = True
            elif fdm.run.type == "post_process_getdp_only":
                self.solve_gui = True
            elif fdm.run.type == "solve_with_post_process_python":
                self.python_postprocess_gui = True
            elif fdm.run.type == "post_process_python_only":
                self.python_postprocess_gui = True

        # Geometry related files:
        if self.geom_folder is not None:
            self.brep_file = os.path.join(self.geom_folder, f"{self.magnet_name}.brep")
            self.vi_file = os.path.join(self.geom_folder, f"{self.magnet_name}.vi")
            self.geometry_data_file = os.path.join(self.geom_folder, "geometry.yaml")

        # Mesh related files:
        if self.mesh_folder is not None:
            self.mesh_file = os.path.join(self.mesh_folder, f"{self.magnet_name}.msh")
            self.regions_file = os.path.join(
                self.mesh_folder, f"{self.magnet_name}.regions"
            )
            self.mesh_data_file = os.path.join(self.mesh_folder, "mesh.yaml")
        # Solution related files:
        if self.solution_folder is not None:
            self.pro_file = os.path.join(
                self.solution_folder, f"{self.magnet_name}.pro"
            )


from fiqus.geom_generators.GeometryPancake3D import Geometry
from fiqus.mesh_generators.MeshPancake3D import Mesh
from fiqus.getdp_runners.RunGetdpPancake3D import Solve
from fiqus.post_processors.PostProcessPancake3D import Postprocess
from fiqus.data.DataFiQuS import FDM


class MainPancake3D:
    """
    The main class for working with simulations for high-temperature superconductor
    pancake coil magnets.

    Geometry can be created and saved as a BREP file. Parameters like the number of
    turns, tape dimensions, contact layer thicknesses, and other dimensions can be
    specified. Contact layers can be modeled as two-dimensional shells or three-dimensional
    volumes. Moreover, multiple pancakes can be stacked on top of each other.

    Using the BREP file created, a mesh can be generated and saved as an MSH file.
    Winding mesh can be structured, and parameters like, azimuthal number of elements
    per turn, axial number of elements, and radial number of elements per turn can be
    specified for each pancake coil. The appropriate regions will be assigned to the
    relevant volumes accordingly so that finite element simulations can be done.

    Using the mesh files, GetDP can be used to analyze Pancake3D coils.

    :param fdm: FiQuS data model
    """

    def __init__(self, fdm, verbose):
        self.fdm: FDM = fdm
        self.GetDP_path = None

        self.geom_folder = None
        self.mesh_folder = None
        self.solution_folder = None

    def generate_geometry(self, gui=False):
        """
        Generates the geometry of the magnet and save it as a BREP file. Moreover, a
        text file with the extension VI (volume information file) is generated, which
        stores the names of the volume tags in JSON format.
        """
        geometry = Geometry(
            self.fdm,
            self.geom_folder,
            self.mesh_folder,
            self.solution_folder,
        )
        if self.fdm.magnet.geometry.conductorWrite:
            self.fdm.magnet.geometry.gapBetweenPancakes = 0.00024
            innerRadius = self.fdm.magnet.geometry.winding.innerRadius
            gap = self.fdm.magnet.geometry.winding.thickness
            # gap = 0.01
            turns = self.fdm.magnet.geometry.numberOfPancakes
            # turns = 4
            z = - self.fdm.magnet.geometry.winding.height/2
            initialTheta = 0.0
            # transitionNotchAngle = self.fdm.magnet.geometry.wi.t ##TODO pull from internal recalculated
            # transitionNotchAngle = 0.7853981633974483/2
            d = direction(0)
            sc = spiralCurve(innerRadius,
                            gap,
                            turns,
                            z,
                            initialTheta,
                            transitionNotchAngle,
                            self.fdm.magnet.geometry,
                            direction=d, # TODO code this to understand cw direction
                            cutPlaneNormal=None)
        else:
            geometry.generate_geometry()
            geometry.generate_vi_file()

            self.model_file = geometry.brep_file

    def load_geometry(self, gui=False):
        """
        Loads the previously generated geometry from the BREP file.
        """
        geometry = Geometry(
            self.fdm,
            self.geom_folder,
            self.mesh_folder,
            self.solution_folder,
        )

        geometry.load_geometry()
        self.model_file = geometry.brep_file

    def pre_process(self, gui=False):
        pass

    def mesh(self, gui=False):
        """
        Generates the mesh of the magnet, creates the physical regions, and saves it as
        an MSH file. Moreover, a text file with the extension REGIONS is generated,
        which stores the names and tags of the physical regions in YAML format.
        """
        mesh = Mesh(
            self.fdm,
            self.geom_folder,
            self.mesh_folder,
            self.solution_folder,
        )

        mesh.generate_mesh()
        mesh.generate_regions()
        mesh.generate_mesh_file()

        self.model_file = mesh.mesh_file

        return {"gamma": 0}  # to be modified with mesh_parameters (see multipole)

    def load_mesh(self, gui=False):
        """
        Loads the previously generated mesh from the MSH file.
        """
        mesh = Mesh(
            self.fdm,
            self.geom_folder,
            self.mesh_folder,
            self.solution_folder,
        )
        mesh.load_mesh()

        self.model_file = mesh.mesh_file

    def solve_and_postprocess_getdp(self, gui=False):
        """
        Simulates the Pancake3D magnet with GetDP using the created mesh file and post
        processes the results.
        """
        # calculate inductance and time constant:
        if self.fdm.magnet.solve.quantitiesToBeSaved is not None:
            save_list = list(
                map(
                    lambda quantity_object: quantity_object.quantity,
                    self.fdm.magnet.solve.quantitiesToBeSaved,
                )
            )
            new_solve_object_for_inductance_and_time_constant = {
                "type": "electromagnetic",
                "time": {
                    "timeSteppingType": "adaptive",
                    "extrapolationOrder": 1,
                    "adaptiveSteppingSettings": {
                        "initialStep": 1,
                        "minimumStep": 0.00001,
                        "maximumStep": 20,
                        "integrationMethod": "Euler",
                        "tolerances": [
                            {
                                "quantity": "magnitudeOfMagneticField",
                                "position": {
                                    "x": 0,
                                    "y": 0,
                                    "z": 0,
                                },
                                "relative": 0.05,  # 5%
                                "absolute": 0.00002,  # 0.00002 T
                                "normType": "LinfNorm",
                            }
                        ],
                    },
                },
                "nonlinearSolver": self.fdm.magnet.solve.nonlinearSolver,
                "air": {
                    "permeability": 1.2566e-06,
                },
                "initialConditions": {
                    "temperature": 4,
                },
            }
            inductance = None
            inductance_solution_folder = os.path.join(
                self.solution_folder,
                "inductance",
            )
            inductance_file = os.path.join(
                inductance_solution_folder, "Inductance-TimeTableFormat.csv"
            )
            if "inductance" in save_list:
                # to calculate inductance and time constant, we should run the simulation
                # with specigic power supply and material settings.
                copy_fdm = deepcopy(self.fdm)

                new_solve_object_for_inductance_and_time_constant["time"]["start"] = 0
                new_solve_object_for_inductance_and_time_constant["time"]["end"] = 100
                new_solve_object_for_inductance_and_time_constant["winding"] = {
                    "resistivity": 1e-20,
                    "thermalConductivity": 1,
                    "specificHeatCapacity": 1,
                }

                new_solve_object_for_inductance_and_time_constant["contactLayer"] = {
                    "resistivity": 1e-2,
                    "thermalConductivity": 1,
                    "specificHeatCapacity": 1,
                    "numberOfThinShellElements": 1,
                }
                new_solve_object_for_inductance_and_time_constant["terminals"] = {
                    "resistivity": 1e-10,
                    "thermalConductivity": 1,
                    "specificHeatCapacity": 1,
                    "terminalContactLayer": {
                        "resistivity": 1e-10,
                        "thermalConductivity": 1,
                        "specificHeatCapacity": 1,
                    },
                    "transitionNotch": {
                        "resistivity": 1e-10,
                        "thermalConductivity": 1,
                        "specificHeatCapacity": 1,
                    },
                }
                solve_object = Pancake3DSolve(
                    **new_solve_object_for_inductance_and_time_constant
                )
                solve_object.quantitiesToBeSaved = [Pancake3DSolveSaveQuantity(quantity="inductance")]
                copy_fdm.magnet.solve = solve_object

                new_power_supply_object_for_inductance = {
                    "t_control_LUT": [0, 0.1, 100],
                    "I_control_LUT": [0, 1, 1],
                }
                new_power_supply_object_for_inductance = PowerSupply(
                    **new_power_supply_object_for_inductance
                )
                copy_fdm.power_supply = new_power_supply_object_for_inductance

                # generate the folder if it does not exist:
                if not os.path.exists(inductance_solution_folder):
                    os.makedirs(inductance_solution_folder)
                else:
                    shutil.rmtree(inductance_solution_folder)
                    os.makedirs(inductance_solution_folder)

                solve = Solve(
                    copy_fdm,
                    self.GetDP_path,
                    self.geom_folder,
                    self.mesh_folder,
                    inductance_solution_folder,
                )
                solve.assemble_pro()

                start_time = Time.time()
                solve.run_getdp(solve=True, postOperation=True)

                with open(inductance_file, "r") as f:
                    # read the last line and second column:
                    inductance = float(f.readlines()[-1].split()[1].replace(",", ""))

                with open(inductance_file, "w") as f:
                    f.write(str(inductance))

            if "timeConstant" in save_list:
                # to calculate inductance and time constant, we should run the simulation
                # with specigic power supply and material settings.
                copy_fdm = deepcopy(self.fdm)

                if inductance is None:
                    raise ValueError(
                        "Time constant can not be calculated without inductance. Please"
                        " add 'inductance' to the 'quantitiesToBeSaved' list in the"
                        " 'solve' section of the YAML file."
                    )

                # equivalent radial resistance of the winding:
                # https://doi.org/10.1109/TASC.2021.3063653
                R_eq = 0
                for i in range(1, int(copy_fdm.magnet.geometry.winding.numberOfTurns)):
                    r_i = (
                        copy_fdm.magnet.geometry.winding.innerRadius
                        + i * copy_fdm.magnet.geometry.winding.thickness
                        + (i - 1) * copy_fdm.magnet.geometry.contactLayer.thickness
                        + copy_fdm.magnet.geometry.contactLayer.thickness / 2
                    )
                    w_d = copy_fdm.magnet.geometry.winding.height
                    R_ct = (
                        copy_fdm.magnet.solve.contactLayer.resistivity
                        * copy_fdm.magnet.geometry.contactLayer.thickness
                    )
                    R_eq = R_eq + R_ct / (2 * math.pi * r_i * w_d)

                estimated_time_constant = inductance / R_eq * 3

                new_solve_object_for_inductance_and_time_constant["time"]["start"] = 0
                new_solve_object_for_inductance_and_time_constant["time"][
                    "adaptiveSteppingSettings"
                ]["initialStep"] = (estimated_time_constant / 18)
                new_solve_object_for_inductance_and_time_constant["time"][
                    "adaptiveSteppingSettings"
                ]["minimumStep"] = (estimated_time_constant / 512)
                new_solve_object_for_inductance_and_time_constant["time"][
                    "adaptiveSteppingSettings"
                ]["maximumStep"] = (estimated_time_constant / 18)
                new_solve_object_for_inductance_and_time_constant["time"]["start"] = 0
                new_solve_object_for_inductance_and_time_constant["time"]["end"] = (
                    0.1 + estimated_time_constant * 8 + 0.001
                )
                new_solve_object_for_inductance_and_time_constant["winding"] = (
                    copy_fdm.magnet.solve.winding.model_dump()
                )
                new_solve_object_for_inductance_and_time_constant["contactLayer"] = (
                    copy_fdm.magnet.solve.contactLayer.model_dump()
                )
                new_solve_object_for_inductance_and_time_constant["terminals"] = (
                    copy_fdm.magnet.solve.terminals.model_dump()
                )
                solve_object = Pancake3DSolve(
                    **new_solve_object_for_inductance_and_time_constant
                )
                solve_object.quantitiesToBeSaved = [
                    Pancake3DSolveSaveQuantity(quantity="timeConstant")
                ]

                solve_object.contactLayer.resistivity = copy_fdm.magnet.solve.contactLayer.resistivity
                copy_fdm.magnet.solve = solve_object

                new_power_supply_object_for_time_constant = {
                    "t_control_LUT": [
                        0,
                        0.1,
                        0.1 + estimated_time_constant * 6,
                        0.1 + estimated_time_constant * 6 + 0.001,
                        0.1 + estimated_time_constant * 8 + 0.001,
                    ],
                    "I_control_LUT": [0, 1, 1, 0, 0],
                }
                new_power_supply_object_for_time_constant = PowerSupply(
                    **new_power_supply_object_for_time_constant
                )
                copy_fdm.power_supply = new_power_supply_object_for_time_constant

                time_constant_solution_folder = os.path.join(
                    self.solution_folder,
                    "time_constant",
                )
                # generate the folder if it does not exist:
                if not os.path.exists(time_constant_solution_folder):
                    os.makedirs(time_constant_solution_folder)
                solve = Solve(
                    copy_fdm,
                    self.GetDP_path,
                    self.geom_folder,
                    self.mesh_folder,
                    time_constant_solution_folder,
                )
                solve.assemble_pro()

                solve.run_getdp(solve=True, postOperation=True)

                # then compute the time constant and write it to a file:
                # read axialComponentOfTheMagneticFieldForTimeConstant-TimeTableFormat.txt

                time_constant_file = os.path.join(
                    time_constant_solution_folder,
                    "axialComponentOfTheMagneticFieldForTimeConstant-TimeTableFormat.csv",
                )
                times = []
                Bzs = []
                isNegative = False
                with open(time_constant_file, "r") as f:
                    for line in f.readlines():
                        time = float(line.split()[1])
                        Bz = float(line.split()[-1])
                        times.append(time)
                        if Bz < 0:
                            isNegative = True
                            Bzs.append(-Bz)
                        else:
                            if isNegative:
                                raise ValueError(
                                    "The magnetic field should not change sign."
                                )
                            Bzs.append(Bz)

                # find the maximum value of Bz:
                max_Bz = max(Bzs)

                # during decay, find the time when Bz is 1/e of the maximum value (36.8%):
                # Do linear interpolation if required:
                percents_of_max_Bz = []
                for Bz_i in Bzs:
                    percents_of_max_Bz.append(Bz_i / max_Bz)

                peak_index = percents_of_max_Bz.index(max(percents_of_max_Bz))
                for percent in percents_of_max_Bz[peak_index:]:
                    if percent < 0.368:
                        index = percents_of_max_Bz.index(percent)
                        break

                # find the time when percents_of_max_Bz
                x1 = times[index - 1]
                x2 = times[index]
                y1 = percents_of_max_Bz[index - 1]
                y2 = percents_of_max_Bz[index]

                time_constant = (
                    x1 + (0.368 - y1) * (x2 - x1) / (y2 - y1) - times[peak_index]
                )

                # write the time constant to a file:
                time_constant_file = os.path.join(
                    time_constant_solution_folder, "time_constant.csv"
                )
                with open(time_constant_file, "w") as f:
                    f.write(str(time_constant))

        # main solver:
        if "inductance" in save_list:
            for save_object in self.fdm.magnet.solve.quantitiesToBeSaved:
                if save_object.quantity == "inductance":
                    self.fdm.magnet.solve.quantitiesToBeSaved.remove(save_object)

        if "timeConstant" in save_list:
            for save_object in self.fdm.magnet.solve.quantitiesToBeSaved:
                if save_object.quantity == "timeConstant":
                    self.fdm.magnet.solve.quantitiesToBeSaved.remove(save_object)

        solve = Solve(
            self.fdm,
            self.GetDP_path,
            self.geom_folder,
            self.mesh_folder,
            self.solution_folder,
        )
        solve.assemble_pro()

        start_time = Time.time()
        solve.run_getdp(solve=True, postOperation=True)

        return Time.time() - start_time

    def post_process_getdp(self, gui=False):
        solve = Solve(
            self.fdm,
            self.GetDP_path,
            self.geom_folder,
            self.mesh_folder,
            self.solution_folder,
        )
        solve.assemble_pro()

        start_time = Time.time()
        solve.run_getdp(solve=False, postOperation=True)

        return Time.time() - start_time

    def post_process_python(self, gui=False):
        """
        To be written.
        """
        postprocess = Postprocess(
            self.fdm,
            self.geom_folder,
            self.mesh_folder,
            self.solution_folder,
        )

        if self.fdm.magnet.postproc is not None:
            if self.fdm.magnet.postproc.timeSeriesPlots is not None:
                postprocess.plotTimeSeriesPlots()
            if self.fdm.magnet.postproc.magneticFieldOnCutPlane is not None:
                postprocess.plotMagneticFieldOnCutPlane()

        return {"overall_error": 0}

    def plot_python(self):
        pass
