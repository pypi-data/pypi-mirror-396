import timeit
import json
import logging
import math
from enum import Enum
import operator
import itertools
import os
import pickle
import subprocess
import re
import pandas as pd

import gmsh
import numpy as np

from fiqus.data import RegionsModelFiQuS
from fiqus.utils.Utils import GmshUtils, FilesAndFolders
from fiqus.data.RegionsModelFiQuS import RegionsModel
# import fiqus.data.DataConductorACGeom as geom

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

        self.ed = {} # excitation dictionary

        gmsh.option.setNumber("General.Terminal", verbose)

    def read_excitation(self, inputs_folder_path):
        """
        Function for reading csv for the 'from_file' excitation case
        :type inputs_folder_path: str
        """
        # if self.cacdm.solve.source_parameters.source_type == 'from_file':
        #     input_file = os.path.join(inputs_folder_path, self.cacdm.solve.source_parameters.source_csv_file)
        #     logger.info(f'Getting applied field and transport current from file: {input_file}')
        #     df = pd.read_csv(input_file, delimiter=',', engine='python')
        #     excitation_time = df['time'].to_numpy(dtype='float').tolist()
        #     self.ed['time'] = excitation_time
        #     excitation_b = df['b'].to_numpy(dtype='float').tolist()
        #     self.ed['b'] = excitation_b
        #     excitation_I = df['I'].to_numpy(dtype='float').tolist()
        #     self.ed['I'] = excitation_I

        if self.cacdm.solve.source_parameters.excitation_coils.enable and self.cacdm.solve.source_parameters.excitation_coils.source_csv_file:
            input_file = os.path.join(inputs_folder_path, self.cacdm.solve.source_parameters.excitation_coils.source_csv_file)
            logger.info(f'Getting excitation coils currents from file: {input_file}')
            df = pd.read_csv(input_file, delimiter=',', engine='python')
            
            if( len(df.columns) != len(self.cacdm.geometry.excitation_coils.centers)+1):
                logger.warning('Number of excitation coils in geometry ('+ str(len(self.cacdm.geometry.excitation_coils.centers))+') and input source file ('+str(len(df.columns))+') not compatible')

            excitation_time = df['time'].to_numpy(dtype='float').tolist()
            self.ed['time'] = excitation_time
            for i in range(1, len(df.columns)):
                Istr = 'I'+str(i)
                excitation_value = df[Istr].to_numpy(dtype='float').tolist()
                self.ed[Istr] = excitation_value

    # def get_material_properties(self, inputs_folder_path):
    #     """
    #     Function for reading material properties from the geometry YAML file.
    #     This reads the 'solution' section of the YAML file and stores it in the solution folder.
    #     This could also be a place to change the material properties in the future.
    #     """
    #     if self.cacdm.geometry.io_settings.load.load_from_yaml:
    #         input_yaml_file = os.path.join(inputs_folder_path, self.cacdm.geometry.io_settings.load.filename)
    #         Conductor_dm = FilesAndFolders.read_data_from_yaml(input_yaml_file, geom.Conductor)
    #         solution_parameters = Conductor_dm.Solution
    #         FilesAndFolders.write_data_to_yaml(os.path.join(self.solution_folder, "MaterialProperties.yaml"), solution_parameters.dict())
    #         self.material_properties_model = solution_parameters

        


    def assemble_pro(self):
        logger.info("Assembling .pro file")
        self.ass_pro.assemble_combined_pro(template = self.cacdm.solve.pro_template, rm = self.regions_model, dm = self.fdm, ed=self.ed, mp=self.material_properties_model)

    def run_getdp(self, solve = True, postOperation = True, gui = False):

        # f = self.cacdm.solve.source_parameters.frequency
        # bmax = self.cacdm.solve.source_parameters.applied_field_amplitude
        # Imax_ratio = self.cacdm.solve.source_parameters.ratio_of_max_imposed_current_amplitude

        command = ["-v2", "-verbose", "3"]
        if solve: 
            # command += ["-solve", "js_to_hs_2"] if not self.cacdm.solve.frequency_domain_solver.enable else ["-solve", "MagDyn_freq"] # for debugging purposes
            command += ["-solve", "MagDyn"] if not self.cacdm.solve.frequency_domain_solver.enable else ["-solve", "MagDyn_freq"] 
        # Solve_only seems to always call postproc, here we only save .pos-files if specified in input file
        # if (postOperation and not solve) or (solve and postOperation and self.cacdm.postproc.generate_pos_files): 
        # if self.cacdm.solve.formulation_parameters.dynamic_correction:
        #     command += " -pos MagDyn MagDyn_dynCorr"
        # else:
        command += ["-pos", "MagDyn"]

        logger.info(f"Running GetDP with command: {command}")
        startTime = timeit.default_timer()
        # subprocess.run(f"{self.GetDP_path} {self.pro_file} {command} -msh {self.mesh_file}")

        if self.cacdm.solve.general_parameters.noOfMPITasks:
            mpi_prefix = ["mpiexec", "-np", str(self.cacdm.solve.general_parameters.noOfMPITasks)]
        else:
            mpi_prefix = []

        getdpProcess = subprocess.Popen(mpi_prefix + [self.GetDP_path] + [self.pro_file] + command + ["-msh"] + [self.mesh_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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
        
        simulation_time = timeit.default_timer()-startTime
        # Save simulation time:
        if solve:
            logger.info(f"Solving Rutherford has finished in {round(simulation_time, 3)} seconds.")
            with open(self.solution_folder+f'\\txt_files\\simulation_time.txt', 'w') as file:
                file.write(str(simulation_time))


        if gui and ((postOperation and not solve) or (solve and postOperation and self.cacdm.postproc.generate_pos_files)):
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
            This funtion is used to remove .pre and .res files from the solution folder, as they may be large and not needed.
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