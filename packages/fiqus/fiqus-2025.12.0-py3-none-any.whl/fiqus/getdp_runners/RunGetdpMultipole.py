import os
import pathlib
import subprocess
import logging
import timeit
import re

import gmsh
from fiqus.pro_assemblers.ProAssembler import ASS_PRO as aP
from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import FilesAndFolders as Util
from fiqus.data import DataFiQuS as dF
from fiqus.data import RegionsModelFiQuS as rM
from fiqus.data import DataMultipole as dM

logger = logging.getLogger(__name__)


class AssignNaming:
    def __init__(self, data: dF.FDM() = None):
        """
        Class to assign naming convention
        :param data: FiQuS data model
        """
        self.data: dF.FDM() = data

        self.naming_conv = {'omega': 'Omega', 'boundary': 'Bd_', 'powered': '_p', 'induced': '_i', 'air': '_a',
                            'air_far_field': '_aff', 'iron': '_bh', 'conducting': '_c', 'insulator': '_ins', 'terms': 'Terms'}
        self.data.magnet.postproc.electromagnetics.volumes = \
            [self.naming_conv['omega'] + (self.naming_conv[var] if var != 'omega' else '') for var in self.data.magnet.postproc.electromagnetics.volumes]
        self.data.magnet.postproc.thermal.volumes = \
            [self.naming_conv['omega'] + (self.naming_conv[var] if var != 'omega' else '') for var in self.data.magnet.postproc.thermal.volumes]


class RunGetdpMultipole:
    def __init__(self, data: AssignNaming = None, solution_folder: str = None, GetDP_path: str = None, verbose: bool = False):
        """
        Class to solve pro file
        :param data: FiQuS data model
        :param GetDP_path: settings data model
        :param verbose: If True more information is printed in python console.
        """
        logger.info(
            f"Initializing Multipole runner for {os.path.basename(solution_folder)}."
        )
        self.data: dF.FDM() = data.data
        self.naming_conv: dict = data.naming_conv
        self.solution_folder = solution_folder
        self.GetDP_path = GetDP_path
        self.verbose: bool = verbose
        self.call_method = 'subprocess'  # or onelab

        self.rm_EM = rM.RegionsModel()
        self.rm_TH = rM.RegionsModel()
        self.rc = dM.MultipoleRegionCoordinate()\
            if self.data.magnet.mesh.thermal.isothermal_conductors and self.data.magnet.solve.thermal.solve_type else None

        self.gu = GmshUtils(self.solution_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=self.data.run.verbosity_Gmsh)
        self.occ = gmsh.model.occ
        self.mesh = gmsh.model.mesh

        self.brep_iron_curves = {1: set(), 2: set(), 3: set(), 4: set()}
        self.mesh_files = os.path.join(os.path.dirname(self.solution_folder), self.data.general.magnet_name)
        self.model_file = os.path.join(self.solution_folder, 'Center_line.csv')

        self.mf = {'EM': f"{self.mesh_files}_EM.msh", 'TH': f"{self.mesh_files}_TH.msh"}

    def loadRegionFiles(self):
        if self.data.magnet.solve.electromagnetics.solve_type:
            self.rm_EM = Util.read_data_from_yaml(f"{self.mesh_files}_EM.reg", rM.RegionsModel)
        if self.data.magnet.solve.thermal.solve_type:
            self.rm_TH = Util.read_data_from_yaml(f"{self.mesh_files}_TH.reg", rM.RegionsModel)

    def loadRegionCoordinateFile(self):
        self.rc = Util.read_data_from_yaml(f"{self.mesh_files}_TH.reco", dM.MultipoleRegionCoordinate)

    def assemblePro(self):
        logger.info(f"Assembling pro file...")
        start_time = timeit.default_timer()
        ap = aP(file_base_path=os.path.join(self.solution_folder, self.data.general.magnet_name), naming_conv=self.naming_conv)
        BH_curves_path = os.path.join(pathlib.Path(os.path.dirname(__file__)).parent, 'pro_material_functions', 'ironBHcurves.pro')
        ap.assemble_combined_pro(template='Multipole_template.pro', rm_EM=self.rm_EM, rm_TH=self.rm_TH, rc=self.rc, dm=self.data, mf=self.mf, BH_curves_path=BH_curves_path)
        logger.info(
            f"Assembling pro file took"
            f" {timeit.default_timer() - start_time:.2f} s."
        )

    def solve_and_postprocess(self):
        commands = None
        if self.call_method == 'onelab':
            commands = f"-solve -v2 -pos -verbose {self.data.run.verbosity_GetDP}"
        elif self.call_method == 'subprocess':
            commands = []
            commands.append(["-solve", 'resolution', "-v2", "-pos", "Dummy", "-verbose", str(self.data.run.verbosity_GetDP)])

        self._run(commands=commands)

    def postprocess(self):
        if self.call_method == 'onelab':
            command = "-v2 -pos -verbose {self.data.run.verbosity_GetDP}"
        elif self.call_method == 'subprocess':
            command = [["-v2", "-pos", "-verbose", str(self.data.run.verbosity_GetDP)]]
        self._run(commands=command)

    def _run(self, commands):
        logger.info("Solving...")
        start_time = timeit.default_timer()
        if self.call_method == 'onelab':
            for command in commands:
                gmsh.onelab.run(f"{self.data.general.magnet_name}",
                                f"{self.GetDP_path} {os.path.join(self.solution_folder, self.data.general.magnet_name)}.pro {command}")
            gmsh.onelab.setChanged("GetDP", 0)
        elif self.call_method == 'subprocess':
            # subprocess.call([f"{self.GetDP_path}", f"{os.path.join(self.solution_folder, self.data.general.magnet_name)}.pro"] + command + ["-msh", f"{self.mesh_files}.msh"])

            # view_tag = gmsh.view.getTags()  # this should be b
            # # # v = "View[" + str(gmsh.view.getIndex('b')) + "]"
            # gmsh.view.write(view_tag, f"{os.path.join(self.solution_folder, self.data.general.magnet_name)}-view.msh")

            if self.data.magnet.solve.noOfMPITasks:
                mpi_prefix = ["mpiexec", "-np", str(self.data.magnet.solve.noOfMPITasks)]
            else:
                mpi_prefix = []
            
            for command in commands:
                getdpProcess = subprocess.Popen(
                    mpi_prefix + [f"{self.GetDP_path}", f"{os.path.join(self.solution_folder, self.data.general.magnet_name)}.pro"] +
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                with getdpProcess.stdout:
                    for line in iter(getdpProcess.stdout.readline, b""):
                        line = line.decode("utf-8").rstrip()
                        line = line.split("\r")[-1]
                        if "Info" in line:
                            parsedLine = re.sub(r"Info\s*:\s*", "", line)
                            logger.info(parsedLine)
                        elif "Warning" in line:
                            parsedLine = re.sub(r"Warning\s*:\s*", "", line)
                            if "Unknown" not in parsedLine:
                                logger.warning(parsedLine)
                        elif "Error" in line:
                            parsedLine = re.sub(r"Error\s*:\s*", "", line)
                            logger.error(parsedLine)
                            raise Exception(parsedLine)
                        elif "Critical" in line:
                            parsedLine = re.sub(r"Critical\s*:\s*", "", line)
                            logger.critical(parsedLine)
                        # catch the maximum temperature line
                        elif "Maximum temperature" in line:
                            parsedLine = re.sub(r"Print\s*:\s*", "", line)
                            logger.info(parsedLine)
                        # this activates the debugging message mode
                        elif self.data.run.verbosity_GetDP > 99:
                            logger.info(line)

                getdpProcess.wait()

        logger.info(
            f"Solving took {timeit.default_timer() - start_time:.2f} s."
        )

    def ending_step(self, gui: bool = False):
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()
