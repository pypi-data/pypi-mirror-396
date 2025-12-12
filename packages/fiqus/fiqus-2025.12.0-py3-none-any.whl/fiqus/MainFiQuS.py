import argparse
import csv
import os
import pathlib
import sys
import time
import getpass
import platform
import subprocess
import json

import pandas as pd

FiQuS_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FiQuS_path)

from fiqus.utils.Utils import FilesAndFolders as Util
from fiqus.utils.Utils import CheckForExceptions as Check
from fiqus.utils.Utils import create_json_schema
from fiqus.utils.Utils import get_data_settings
from fiqus.utils.Utils import initialize_logger
from fiqus.data.DataFiQuS import FDM, SolveDumpDataModel
from fiqus.data.DataSettings import DataSettings
from fiqus.mains.MainCCT import MainCCT
from fiqus.mains.MainMultipole import MainMultipole
from fiqus.mains.MainPancake3D import MainPancake3D
from fiqus.mains.MainConductorAC_Strand import MainConductorAC_Strand
from fiqus.mains.MainHomogenizedConductor import MainHomogenizedConductor
from fiqus.mains.MainConductorAC_Rutherford import MainConductorAC_Rutherford

class MainFiQuS:
    """
    This is the top level class of FiQuS.
    """

    def __init__(
            self,
            input_file_path: str = None,
            model_folder: str = None,
            GetDP_path=None,
            fdm=None,
            fds=None,
            htcondor_jobid=None
    ):
        """
        Main class for working with FiQuS simulations
        :param input_file_path: full path to input file yaml
        :type input_file_path: str
        :param model_folder: full path to the base output folder, called model folder
        :type model_folder: str
        :param GetDP_path: full path to GetDP executable
        :type GetDP_path: str
        :param fdm: FiQuS Data Model - object of fiqus DataFiQus
        :type fdm: object
        :param fds: FiQuS Data Settings - object of DataSettings
        :type fds: object
        """
        self.time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S")

        self.start_folder = os.getcwd()
        self.wrk_folder = model_folder
        self.file_name = None

        # Load yaml input file
        if not fdm:
            self.fdm: FDM = Util.read_data_from_yaml(input_file_path, FDM)
            copyInputFile = (
                "copy"
                f" {input_file_path} {os.path.join(self.wrk_folder, 'logs', f'INPUT_FILE_{self.time_stamp}.FiQuS.yaml')}"
            )
            subprocess.run(copyInputFile, shell=True, stdout=subprocess.DEVNULL)
        else:
            self.fdm: FDM = fdm
        verbose = self.fdm.run.verbosity_FiQuS
        self.logger = initialize_logger(
            verbose=verbose, time_stamp=self.time_stamp, work_folder=self.wrk_folder
        )
        if verbose:
            Util.print_welcome_graphics()
        # Intialize logger

        # Create JSON schema
        create_json_schema(self.fdm)

        # Check for input errors
        Check.check_inputs(run=self.fdm.run)

        # Initialize Main object
        if self.fdm.magnet.type == "CCT_straight":
            self.main_magnet = MainCCT(fdm=self.fdm, verbose=verbose)
        elif self.fdm.magnet.type == "Pancake3D":
            self.main_magnet = MainPancake3D(fdm=self.fdm, verbose=verbose)
        elif self.fdm.magnet.type == "CACStrand":
            self.main_magnet = MainConductorAC_Strand(fdm=self.fdm, inputs_folder_path=pathlib.Path(input_file_path).parent, outputs_folder_path=model_folder, verbose=verbose)
        elif self.fdm.magnet.type == "HomogenizedConductor":
            self.main_magnet = MainHomogenizedConductor(fdm=self.fdm, inputs_folder_path=pathlib.Path(input_file_path).parent, outputs_folder_path=model_folder, verbose=verbose)
        elif self.fdm.magnet.type == "CACRutherford":
            self.main_magnet = MainConductorAC_Rutherford(fdm=self.fdm, inputs_folder_path=pathlib.Path(input_file_path).parent, verbose=verbose)
        elif self.fdm.magnet.type == "multipole":
            self.file_name = os.path.basename(input_file_path)[:-5]
            if not self.fdm.magnet.geometry.geom_file_path:
                self.fdm.magnet.geometry.geom_file_path = f"{input_file_path[:-5]}.geom"
            self.main_magnet = MainMultipole(
                fdm=self.fdm,
                rgd_path=self.fdm.magnet.geometry.geom_file_path,
                verbose=verbose,
            )

        else:
            raise ValueError(
                f"FiQuS does not support magnet type: {self.fdm.magnet.type}!"
            )

        # Load user paths for executables and additional files
        self.logger.info(f'{getpass.getuser()} is running on {platform.platform()}')
        if not fds:
            fds = get_data_settings(GetDP_path=GetDP_path)
        else:
            fds = get_data_settings(GetDP_path=GetDP_path, settings=fds)
        self.main_magnet.GetDP_path = fds.GetDP_path
        self.logger.info(f"{self.main_magnet.GetDP_path} is going to be used for FE solving.")
        
        # self.logger.info(gmsh.onelab.run(self.fdm.general.magnet_name, f"{self.main_magnet.settings['GetDP_path']} -info"))
        
        # update htcondor csv
        if htcondor_jobid:
            base_path_model_files = fds.base_path_model_files
            htcondor_csv_file = os.path.join(base_path_model_files, "htcondor_run_log.csv")

            self.change_htcondor_run_log(htcondor_csv_file, htcondor_jobid, "Running")

        # Save Model/Geometry/Mesh/Solution folder paths
        self.save_folders()

        # Build magnet
        self.summary = dict.fromkeys(
            [
                "SJ",
                "SICN",
                "SIGE",
                "Gamma",
                "nodes",
                "solution_time",
                "overall_error",
                "minimum_diff",
                "maximum_diff",
            ]
        )

        try:
            self.build_magnet()
        except Exception as e:
            # update htcondor csv
            if htcondor_jobid:
                self.change_htcondor_run_log(htcondor_csv_file, htcondor_jobid, "Failed")
            
            self.logger.error(f"Error: {e}")
            raise e
        else:
            # update htcondor csv
            if htcondor_jobid:
                self.change_htcondor_run_log(htcondor_csv_file, htcondor_jobid, "Finished")

    def save_folders(self):
        """
        Method to make or delete folders of FiQuS
        :return: Nothing, only does file and folder operation
        :rtype: None
        """
        def _check_and_generate_path(folder_type: str = None):
            if folder_type == "Geometry":
                folder = self.wrk_folder
            elif folder_type == "Mesh":
                folder = self.main_magnet.geom_folder
            elif folder_type == "Solution":
                folder = self.main_magnet.mesh_folder
            else:
                raise Exception("Incompatible type.")

            if getattr(self.fdm.run, folder_type.lower()) is None:
                # folder_key is not given, so it is computed
                folder_key = Util.compute_folder_key(
                    folder_type=folder_type,
                    folder=folder,
                    overwrite=self.fdm.run.overwrite,
                )
            else:
                # folder_key is given
                folder_key = getattr(self.fdm.run, folder_type.lower())

            required_folder = folder_type in required_folders
            if self.fdm.run.overwrite and folder_type == (
                    required_folders[0] if required_folders else None
            ):
                Check.check_overwrite_conditions(
                    folder_type=folder_type, folder=folder, folder_key=folder_key
                )
            return Util.get_folder_path(
                folder_type=folder_type,
                folder=folder,
                folder_key=folder_key,
                overwrite=self.fdm.run.overwrite,
                required_folder=required_folder,
            )

        if self.fdm.run.type == "start_from_yaml":
            required_folders = ["Geometry", "Mesh", "Solution"]
        elif self.fdm.run.type == "geometry_and_mesh":
            required_folders = ["Geometry", "Mesh"]
        elif self.fdm.run.type == "mesh_and_solve_with_post_process_python":
            required_folders = ["Mesh", "Solution"]
        elif self.fdm.run.type in ["solve_with_post_process_python", "solve_only"]:
            required_folders = ["Solution"]
        elif self.fdm.run.type == "geometry_only":
            required_folders = (
                []
                if self.fdm.run.geometry and not self.fdm.run.overwrite
                else ["Geometry"]
            )
        elif self.fdm.run.type == "mesh_only":
            required_folders = (
                [] if self.fdm.run.mesh and not self.fdm.run.overwrite else ["Mesh"]
            )
        else:  # post_process_getdp_only or post_process_python_only or plot_python
            required_folders = []



        self.main_magnet.geom_folder = _check_and_generate_path(folder_type="Geometry")
        if not self.fdm.run.type in ["geometry_only"]:
            self.main_magnet.mesh_folder = _check_and_generate_path(folder_type="Mesh")
        if not (
                self.fdm.run.type == "geometry_only"
                or self.fdm.run.type == "mesh_only"
        ):
            self.main_magnet.solution_folder = _check_and_generate_path(
                folder_type="Solution"
            )

        if self.fdm.run.type in [
            "start_from_yaml",
            "geometry_and_mesh",
            "geometry_only",
        ]:
            Util.write_data_model_to_yaml(
                os.path.join(self.main_magnet.geom_folder, "geometry.yaml"),
                self.fdm.magnet.geometry,
                by_alias=True,
                with_comments=True,
            )
        if self.fdm.run.type in [
            "start_from_yaml",
            "geometry_and_mesh",
            "mesh_and_solve_with_post_process_python",
            "mesh_only",
        ]:
            Util.write_data_model_to_yaml(
                os.path.join(self.main_magnet.mesh_folder, "mesh.yaml"),
                self.fdm.magnet.mesh,
                by_alias=True,
                with_comments=True,
            )
        if self.fdm.run.type in [
            "start_from_yaml",
            "mesh_and_solve_with_post_process_python",
            "solve_with_post_process_python",
            "solve_only",
            "post_process",
            "plot_python",
            "postprocess_veusz"
        ]:
            solve_dump_data = SolveDumpDataModel(
                solve=self.fdm.magnet.solve,
                circuit=self.fdm.circuit,
                power_supply=self.fdm.power_supply,
                quench_protection=self.fdm.quench_protection,
                quench_detection=self.fdm.quench_detection,
                conductors=self.fdm.conductors
            )
            Util.write_data_model_to_yaml(
                os.path.join(self.main_magnet.solution_folder, "solve.yaml"),
                solve_dump_data,
                by_alias=True,
                with_comments=True,
            )
        if self.fdm.run.type in [
            "start_from_yaml",
            "mesh_and_solve_with_post_process_python",
            "solve_with_post_process_python",
            "post_process_python_only",
            "post_process_getdp_only",
            "post_process",
            "postprocess_veusz",
            "plot_python"
        ]:
            Util.write_data_model_to_yaml(
                os.path.join(self.main_magnet.solution_folder, "postproc.yaml"),
                self.fdm.magnet.postproc,
                by_alias=True,
                with_comments=True,
            )

        try:
            run_type = self.fdm.run.type
            comments = self.fdm.run.comments
            if self.main_magnet.geom_folder is not None:
                geo_folder = os.path.relpath(self.main_magnet.geom_folder)
                geo_folder = os.path.relpath(
                    geo_folder, os.path.join("tests", "_outputs")
                )
            else:
                geo_folder = "-"

            if self.main_magnet.mesh_folder is not None:
                mesh_folder = os.path.relpath(self.main_magnet.mesh_folder)
                mesh_folder = os.path.relpath(
                    mesh_folder, os.path.join("tests", "_outputs")
                )
            else:
                mesh_folder = "-"

            if self.main_magnet.solution_folder is not None:
                solution_folder = os.path.relpath(self.main_magnet.solution_folder)
                solution_folder = os.path.relpath(
                    solution_folder, os.path.join("tests", "_outputs")
                )
            else:
                solution_folder = "-"

            run_log_row = [
                self.time_stamp,
                run_type,
                comments,
                geo_folder,
                mesh_folder,
                solution_folder,
            ]
            self.add_to_run_log(
                os.path.join(self.wrk_folder, "run_log.csv"), run_log_row
            )
        except:
            self.logger.warning("Run log could not be completed.")


    def build_magnet(self):
        """
        Main method to build magnets, i.e. to run various fiqus run types and magnet types
        :return: none
        :rtype: none
        """
        if self.fdm.run.type == "start_from_yaml":
            self.main_magnet.generate_geometry()
            self.main_magnet.pre_process()
            self.main_magnet.load_geometry()
            for key, value in self.main_magnet.mesh().items():
                self.summary[key] = value
            self.summary["solution_time"] = self.main_magnet.solve_and_postprocess_getdp()
            for key, value in self.main_magnet.post_process_python(gui=self.main_magnet.fdm.run.launch_gui).items():
                self.summary[key] = value
        elif self.fdm.run.type == "pre_process_only":
            self.main_magnet.pre_process()
            for key, value in self.main_magnet.post_process_python(gui=self.main_magnet.fdm.run.launch_gui).items():
                self.summary[key] = value  # todo: DISABLE FOR ONE GROUP ONLY
        elif self.fdm.run.type == "geometry_only":
            self.main_magnet.generate_geometry(
               gui=(self.main_magnet.fdm.run.launch_gui if self.fdm.magnet.type != "CCT_straight" else False)
            )
            if self.fdm.magnet.type in ["CCT_straight", "CWS"]:
                self.main_magnet.pre_process(gui=self.main_magnet.fdm.run.launch_gui)
        elif self.fdm.run.type == "geometry_and_mesh":
            self.main_magnet.generate_geometry()
            self.main_magnet.pre_process()
            self.main_magnet.load_geometry()
            for key, value in self.main_magnet.mesh(gui=self.main_magnet.fdm.run.launch_gui).items():
                self.summary[key] = value
        elif self.fdm.run.type == "mesh_and_solve_with_post_process_python":
            self.main_magnet.load_geometry()
            for key, value in self.main_magnet.mesh().items():
               self.summary[key] = value
            self.summary["solution_time"] = self.main_magnet.solve_and_postprocess_getdp()
            for key, value in self.main_magnet.post_process_python(gui=self.main_magnet.fdm.run.launch_gui).items():
               self.summary[key] = value
        elif self.fdm.run.type == "mesh_only":
            self.main_magnet.load_geometry()
            for key, value in self.main_magnet.mesh(gui=self.main_magnet.fdm.run.launch_gui).items():
                self.summary[key] = value
        elif self.fdm.run.type == "solve_with_post_process_python":
            self.summary["solution_time"] = (
                self.main_magnet.solve_and_postprocess_getdp(gui=self.main_magnet.fdm.run.launch_gui)
            )
            for key, value in self.main_magnet.post_process_python(gui=self.main_magnet.fdm.run.launch_gui).items():
                self.summary[key] = value
        elif self.fdm.run.type == "solve_only":
            self.summary["solution_time"] = (
                self.main_magnet.solve_and_postprocess_getdp(gui=self.main_magnet.fdm.run.launch_gui)
            )
        elif self.fdm.run.type == "postprocess_veusz":
            self.main_magnet.post_process_veusz(gui=self.main_magnet.fdm.run.launch_gui)
        elif self.fdm.run.type == "post_process_getdp_only":
            self.main_magnet.post_process_getdp(gui=self.main_magnet.fdm.run.launch_gui)
        elif self.fdm.run.type == "post_process_python_only":
            for key, value in self.main_magnet.post_process_python(gui=self.main_magnet.fdm.run.launch_gui).items():
                self.summary[key] = value
        elif self.fdm.run.type == "post_process":
            self.main_magnet.post_process_getdp(gui=self.main_magnet.fdm.run.launch_gui)
            for key, value in self.main_magnet.post_process_python(gui=self.main_magnet.fdm.run.launch_gui).items():
                self.summary[key] = value
        elif self.fdm.run.type == "plot_python":
            self.main_magnet.plot_python()

        elif self.fdm.run.type == "batch_post_process_python":
            self.main_magnet.batch_post_process_python()
        os.chdir(self.start_folder)

        if self.file_name:
            file_path = os.path.join(self.wrk_folder, f"{self.file_name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.summary, f, indent=2)

    @staticmethod
    def add_to_run_log(path_to_csv, run_log_row):
        # If file does not exist, write the header
        if not os.path.isfile(path_to_csv):
            header = [
                "Time Stamp",
                "Run Type",
                "Comments",
                "Geometry Directory",
                "Mesh Directory",
                "Solution Directory",
            ]
            with open(path_to_csv, "a", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)

        # Open the CSV file in append mode
        with open(path_to_csv, "a+", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(run_log_row)

    def change_htcondor_run_log(self, htcondor_csv_file, htcondor_jobid, new_status="None"):
        try: 
            df = pd.read_csv(htcondor_csv_file)
            df.loc[df['Job ID'] == htcondor_jobid, 'Status'] = str(new_status)
            self.logger.info(f"Changed status of JobID {htcondor_jobid} to {new_status} in {htcondor_csv_file}.")
            df.to_csv(htcondor_csv_file, index=False)
        except:
            self.logger.warning(f"Could not change status of JobID {htcondor_jobid} to {new_status} in {htcondor_csv_file}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="FiQuS",
        description="Finite Elements Quench Simulator",
        epilog="steam-team@cern.ch",
    )
    parser.add_argument(
        dest="full_path_input",
        type=str,
        help="Full path to FiQuS input yaml file",
    )
    parser.add_argument(
        "--output", '-o', dest="output_path", type=str, help="Full path to FiQuS output folder"
    )
    parser.add_argument(
        "--getdp", '-g', dest="GetDP_path", type=str, help="Full path to GetDP executable"
    )

    parser.add_argument("--htcondor_jobid", '-j', type=int, default=0,
                        help="HTCondor job ID (optional)", required=False)

    parser.add_argument("--fiqus_data_model", '-m', type=str, 
                        help="Full path to FiQuS Data Model file (optional)", required=False)

    parser.add_argument("--fiqus_data_settings", '-s', type=str, 
                        help="Full path to FiQuS Data Settings file (optional)", required=False)

    args, unknown = parser.parse_known_args()

    # remove these options from sys.argv, otherwise they are passed onto Gmsh
    # in Gmsh.initialize()
    options_to_remove = ["-o", "-g", "-j", "-m", "-s"]
    # Loop through and remove each option and its value
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] in options_to_remove:
            sys.argv.pop(i)  # Remove the option
            if i < len(sys.argv):
                sys.argv.pop(i)  # Remove the associated value
        else:
            i += 1

    if args.fiqus_data_model != None and args.fiqus_data_settings != None:
        # read fdm and fds from a file (HTCondor case)
        input_fdm = Util.read_data_from_yaml(args.fiqus_data_model, FDM)
        input_fds = Util.read_data_from_yaml(args.fiqus_data_settings, DataSettings)

        MainFiQuS(
            input_file_path=args.full_path_input,
            model_folder=args.output_path,
            fdm=input_fdm,
            fds=input_fds,
            htcondor_jobid=args.htcondor_jobid
        )
    else:
        # fdm and fds from input (STEAM SDK case)
        MainFiQuS(
            input_file_path=args.full_path_input,
            model_folder=args.output_path,
            GetDP_path=args.GetDP_path,
        )
    print("FiQuS run completed")
