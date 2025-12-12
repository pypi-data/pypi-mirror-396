import os
import timeit
from pathlib import Path
import subprocess

import gmsh

from fiqus.utils.Utils import FilesAndFolders as uff
from fiqus.utils.Utils import GmshUtils
from fiqus.data.RegionsModelFiQuS import RegionsModel
from fiqus.pro_assemblers.ProAssembler import ASS_PRO as ass_pro


class RunGetdpCCT:
    def __init__(self, fdm, GetDP_path: dict = None, verbose=True):
        """
        Class to preparing brep files by adding terminals.
        :param fdm: FiQuS data model
        :param verbose: If True more information is printed in python console.
        """
        self.fdm = fdm
        self.cctdm = fdm.magnet
        self.GetDP_path = GetDP_path
        self.model_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name
        self.mesh_folder = Path(self.model_folder).parent
        self.verbose = verbose
        self.cctrm = uff.read_data_from_yaml(os.path.join(self.model_folder, f'{self.magnet_name}.regions'), RegionsModel)
        self.ap = ass_pro(os.path.join(self.model_folder, self.magnet_name))
        self.gu = GmshUtils(self.model_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)
        self.pos_names = []
        self.call_method = 'subprocess'
        # for variable, volume, file_ext in zip(self.cctdm.solve.variables, self.cctdm.solve.volumes, self.cctdm.solve.file_exts):
        #     self.pos_names.append(f'{variable}_{volume}.{file_ext}')

    def assemble_pro(self):
        if self.verbose:
            print('Assembling Pro File Started')
            start_time = timeit.default_timer()
        if self.verbose:
            print('Assembling pro file')
        self.ap.assemble_combined_pro(template=self.cctdm.solve.pro_template, rm=self.cctrm, dm=self.cctdm, mf=f"{os.path.join(self.mesh_folder, self.magnet_name)}.msh")
        if self.verbose:
            print(f'Assembling Pro File Took {timeit.default_timer() - start_time:.2f} s')

    def solve_and_postprocess(self, gui=False):
        command = "-solve -v2 -pos"
        model_file = 'Center_line.csv'
        self._run(command=command, model_file=model_file, gui=gui)

    def postprocess(self, gui=False):
        command = "-v2 -pos"
        model_file = 'Test.dat'
        self._run(command=command, model_file=model_file, gui=gui)

    def _run(self, command, model_file, gui=False):
        if self.verbose:
            print('Solving Started !!!')
            start_time = timeit.default_timer()
        mpi_prefix = []
        res = 'MagDynAVComplex'
        post_op = 'Get_LocalFields'

        if self.call_method == 'onelab':
            gmsh.onelab.run(f"{self.magnet_name}", f"{self.GetDP_path} {os.path.join(self.model_folder, self.magnet_name)}.pro {command} -msh {os.path.join(self.mesh_folder, self.magnet_name)}.msh")
        elif self.call_method == 'subprocess':
            command = ["-solve", res, "-v2", "-pos", post_op, "-verbose", str(self.fdm.run.verbosity_GetDP), '-sub_pc_type lu', '-pc_type lu', '-pc_factor_mat_solver_type mumps']
            subprocess.call(mpi_prefix + [f"{self.GetDP_path}", f"{os.path.join(self.model_folder, self.magnet_name)}.pro"] + command + [f"-msh {os.path.join(self.mesh_folder, self.magnet_name)}.msh"])

        self.model_file = os.path.join(self.model_folder, model_file)
        if self.verbose:
            print(''
                  f'Solving Took {timeit.default_timer() - start_time:.2f} s !!!'
                  '')
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()
