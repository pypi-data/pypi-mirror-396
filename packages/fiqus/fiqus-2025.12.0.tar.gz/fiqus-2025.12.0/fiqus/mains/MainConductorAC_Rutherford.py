import math
import os

from fiqus.geom_generators.GeometryConductorAC_Rutherford import Geometry
from fiqus.mesh_generators.MeshConductorAC_Rutherford import CableMesh
from fiqus.getdp_runners.RunGetdpConductorAC_Rutherford import Solve
from fiqus.post_processors.PostProcessAC_Rutherford import PostProcess
from fiqus.plotters.PlotPythonConductorAC import PlotPythonConductorAC

from fiqus.mains.MainConductorAC_Strand import MainConductorAC_Strand

class MainConductorAC_Rutherford(MainConductorAC_Strand):

    def generate_geometry(self, gui=False):
        """
        Generates the cable geometry.
        """
        os.chdir(self.geom_folder)
        g = Geometry(fdm=self.fdm, inputs_folder_path=self.inputs_folder_path, verbose=self.verbose)
        g.generate_cable_geometry(gui)



    def mesh(self, gui: bool = False):
        """ 
        Generates the mesh for the cable geometry.
        """
        os.chdir(self.mesh_folder)

        m = CableMesh(fdm=self.fdm, verbose=self.verbose)
        m.generate_mesh(self.geom_folder)
        m.generate_cuts()
        m.generate_regions_file()
        m.save_mesh(gui)

        return {"test": 0}
    
    def solve_and_postprocess_getdp(self, gui: bool = False):
        """
        Assembles the .pro-file from the template, then runs the simulation and the post-processing steps using GetDP.
        """
        os.chdir(self.solution_folder)

        # Checks if the strand type in the conductor data model is 'Homogenized', other types are not allowed (e.g., round) to avoid confusion as inputs in them won't be used
        if self.fdm.conductors[self.fdm.magnet.solve.conductor_name].strand.type != 'Homogenized':
            raise Exception(f"The strand type must be 'Homogenized' in the conductors section of the input .yaml file, any other type is not allowed.")

        s = Solve(self.fdm, self.GetDP_path, self.geom_folder, self.mesh_folder, self.verbose)
        s.read_excitation(inputs_folder_path=self.inputs_folder_path)
        # s.get_solution_parameters_from_yaml(inputs_folder_path=self.inputs_folder_path)
        s.assemble_pro()
        s.run_getdp(solve = True, postOperation = True, gui = gui)
        s.cleanup()
    
    def post_process_getdp(self, gui: bool = False):
        """ 
        Runs the post-processing steps trough GetDP.
        """
        os.chdir(self.solution_folder)

        s = Solve(self.fdm, self.GetDP_path, self.geom_folder, self.mesh_folder, self.verbose)
        s.read_excitation(inputs_folder_path=self.inputs_folder_path)
        # s.get_solution_parameters_from_yaml(inputs_folder_path=self.inputs_folder_path)
        s.assemble_pro()
        s.run_getdp(solve = False, postOperation = True, gui = gui)

    def post_process_python(self, gui: bool = False):
        """ 
        Runs the post-processing steps in the python PostProccess class.
        """
        os.chdir(self.solution_folder)

        p = PostProcess(self.solution_folder)
        p.show()

        return {'test': 0}