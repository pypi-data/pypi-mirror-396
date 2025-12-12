import os, re, subprocess, logging, timeit
import pandas as pd
import gmsh

from fiqus.data.DataFiQuSConductor import Conductor, SolutionParameters
from fiqus.data.RegionsModelFiQuS import RegionsModel
from fiqus.utils.Utils import GmshUtils, FilesAndFolders

from fiqus.pro_assemblers.ProAssembler import ASS_PRO

logger = logging.getLogger('FiQuS')

class Solve:
    def __init__(self, fdm, GetDP_path, geometry_folder, mesh_folder, verbose=True):
        self.fdm = fdm
        self.GetDP_path = GetDP_path

        self.solution_folder = os.path.join(os.getcwd())
        self.geometry_folder = geometry_folder
        self.mesh_folder = mesh_folder

        self.mesh_file = os.path.join(self.mesh_folder, f"{self.fdm.general.magnet_name}.msh")
        self.pro_file = os.path.join(self.solution_folder, f"{self.fdm.general.magnet_name}.pro")
        self.regions_file = os.path.join(mesh_folder, f"{self.fdm.general.magnet_name}.regions")
        
        self.verbose = verbose
        self.gu = GmshUtils(self.solution_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

        self.ass_pro = ASS_PRO(os.path.join(self.solution_folder, self.fdm.general.magnet_name))
        self.regions_model = FilesAndFolders.read_data_from_yaml(self.regions_file, RegionsModel)
        self.material_properties_model = None

        self.ed = {} # excitation dictionary
        self.rohm = {} # rohm parameter dictionary
        self.rohf = {} # rohf parameter dictionary

        gmsh.option.setNumber("General.Terminal", verbose)

    def read_ro_parameters(self, inputs_folder_path):
        """
        Function for reading the CSV files containing the reduced order parameters for ROHF and ROHM.
        The function expects CSV files with an descriptive first header row (i.e. 'alphas,kappas,taus') and following rows with comma seperated parameter values for each cell starting from cell 1. 

        :param inputs_folder_path: The full path to the folder with input files
        """
        class reduced_order_params:
            " This structure is used to access the parameter dictionaries inside the pro template with a convenient syntax 'mp.rohf' or 'mp.rohm'."
            def __init__(self, rohf_dict=None, rohm_dict=None):
                self.rohf = rohf_dict
                self.rohm = rohm_dict

        if self.fdm.magnet.solve.rohm.enable and self.fdm.magnet.solve.rohm.parameter_csv_file:
            parameter_file = os.path.join(inputs_folder_path, self.fdm.magnet.solve.rohm.parameter_csv_file)
            df = pd.read_csv(parameter_file, delimiter=',', engine='python')
            df.index += 1
            logger.info(f'Using ROHM parameters from file: {parameter_file}:')
            logger.info(df)
            self.rohm = df.to_dict(orient='dict')

        if self.fdm.magnet.solve.rohf.enable and self.fdm.magnet.solve.rohf.parameter_csv_file:
            parameter_file = os.path.join(inputs_folder_path, self.fdm.magnet.solve.rohf.parameter_csv_file)
            df = pd.read_csv(parameter_file, delimiter=',', engine='python')
            df.index += 1
            logger.info(f'Using ROHF parameters from file: {parameter_file}:')
            logger.info(df)
            self.rohf = df.to_dict(orient='dict')

        # For the moment the reduced order parameters are treated as material properties mp structure.
        self.material_properties_model = reduced_order_params(rohf_dict=self.rohf, rohm_dict=self.rohm)

    def read_excitation(self, inputs_folder_path):
        """
        Function for reading a CSV file for the 'from_file' excitation case.

        :param inputs_folder_path: The full path to the folder with input files.
        :type inputs_folder_path: str
        """
        if self.fdm.magnet.solve.source_parameters.source_type == 'piecewise' and self.fdm.magnet.solve.source_parameters.piecewise.source_csv_file:
            input_file = os.path.join(inputs_folder_path, self.fdm.magnet.solve.source_parameters.piecewise.source_csv_file)
            logger.info(f'Using excitation from file: {input_file}')
            df = pd.read_csv(input_file, delimiter=',', engine='python')
            excitation_time = df['time'].to_numpy(dtype='float').tolist()
            self.ed['time'] = excitation_time
            excitation_value = df['value'].to_numpy(dtype='float').tolist()
            self.ed['value'] = excitation_value
                
    def assemble_pro(self):
        logger.info("Assembling .pro file")
        self.ass_pro.assemble_combined_pro(template = self.fdm.magnet.solve.pro_template, rm = self.regions_model, dm = self.fdm, ed=self.ed, mp=self.material_properties_model)

    def run_getdp(self, solve = True, postOperation = True, gui = False):

        command = ["-v2", "-verbose", "3", "-mat_mumps_icntl_14","100"]
        if solve: 
            command += ["-solve", "MagDyn"]
        command += ["-pos", "MagDyn"]

        if self.fdm.magnet.solve.general_parameters.noOfMPITasks:
            mpi_prefix = ["mpiexec", "-np", str(self.fdm.magnet.solve.general_parameters.noOfMPITasks)]
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
                        logger.error("Solving HomogenizedConductor failed.")
                        # raise Exception(parsedLine)
                    elif re.match("##", line):
                        logger.critical(line)
                    else:
                        logger.info(line)
        
        simulation_time = timeit.default_timer()-startTime
        # Save simulation time:
        if solve:
            logger.info(f"Solving HomogenizedConductor has finished in {round(simulation_time, 3)} seconds.")
            with open(os.path.join(self.solution_folder, 'txt_files', 'simulation_time.txt'), 'w') as file:
                file.write(str(simulation_time))


        if gui and ((postOperation and not solve) or (solve and postOperation and self.fdm.magnet.postproc.generate_pos_files)):
            # gmsh.option.setNumber("Geometry.Volumes", 1)
            # gmsh.option.setNumber("Geometry.Surfaces", 1)
            # gmsh.option.setNumber("Geometry.Curves", 1)
            # gmsh.option.setNumber("Geometry.Points", 0)
            posFiles = [
                fileName
                for fileName in os.listdir(self.solution_folder)
                if fileName.endswith(".pos")
            ]
            for posFile in reversed(posFiles):
                gmsh.open(os.path.join(self.solution_folder, posFile))
            self.gu.launch_interactive_GUI()
        else:
            if gmsh.isInitialized():
                gmsh.clear()
                gmsh.finalize()

    def cleanup(self):
        """
            This funtion is used to remove .msh, .pre and .res files from the solution folder, as they may be large and not needed.
        """
        magnet_name = self.fdm.general.magnet_name
        cleanup = self.fdm.magnet.postproc.cleanup

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