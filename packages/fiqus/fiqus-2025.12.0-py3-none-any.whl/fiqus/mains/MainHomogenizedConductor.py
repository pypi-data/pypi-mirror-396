import os, cProfile

from fiqus.geom_generators.GeometryHomogenizedConductor import Geometry
from fiqus.mesh_generators.MeshHomogenizedConductor import Mesh
from fiqus.getdp_runners.RunGetdpHomogenizedConductor import Solve
from fiqus.post_processors.PostProcessHomogenizedConductor import PostProcess

class MainHomogenizedConductor:
    def __init__(self, fdm, inputs_folder_path='', outputs_folder_path='', verbose=True):
        """
        Main class for working with simulations for the homogenized conductor model.
        :param fdm: FiQuS data model
        :param inputs_folder_path: full path to folder with input files
        :param verbose: if True, more info is printed in the console
        """
        self.verbose = verbose
        self.fdm = fdm
        self.inputs_folder_path = inputs_folder_path
        self.outputs_folder_path = outputs_folder_path
        self.GetDP_path = None
        self.geom_folder = None
        self.mesh_folder = None
        self.solution_folder = None
        self.model_file = None
        self.model_folder = None
        

    def generate_geometry(self, gui=False):
        """ 
        Generates the conductor geometry. 
        """
        os.chdir(self.geom_folder)
        g = Geometry(fdm=self.fdm, inputs_folder_path=self.inputs_folder_path, verbose=self.verbose)
        g.generate_geometry()
        g.generate_vi_file(gui)


    def load_geometry(self, gui: bool = False):
        """
        Loads the previously generated geometry from the .brep file.
        """
        os.chdir(self.geom_folder)
        g = Geometry(fdm=self.fdm, inputs_folder_path=self.inputs_folder_path, verbose=self.verbose)
        g.load_geometry()
        # self.model_file = g.model_file

    def pre_process(self, gui=False):
        pass

    def mesh(self, gui: bool = False):
        """ 
        Generates the mesh for the geometry.
        """
        os.chdir(self.mesh_folder)

        m = Mesh(fdm=self.fdm, verbose=self.verbose)
        m.generate_mesh()
        m.generate_cuts()
        m.generate_regions_file()
        m.save_mesh(gui)

        return {"test": 0}

    def load_mesh(self, gui=False):
        """
        Loads the previously generated mesh from the MSH file.
        """
        os.chdir(self.mesh_folder)
        m = Mesh(fdm=self.fdm, verbose=self.verbose)
        m.load_mesh(gui)

        # self.model_file = m.mesh_file

    def solve_and_postprocess_getdp(self, gui: bool = False):
        """
        Assembles the .pro-file from the template, then runs the simulation and the post-processing steps using GetDP.
        """
        os.chdir(self.solution_folder)

        s = Solve(self.fdm, self.GetDP_path, self.geom_folder, self.mesh_folder, self.verbose)
        s.read_excitation(inputs_folder_path=self.inputs_folder_path)
        s.read_ro_parameters(inputs_folder_path=self.inputs_folder_path)    
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
        s.read_ro_parameters(inputs_folder_path=self.inputs_folder_path) 
        s.assemble_pro()
        s.run_getdp(solve = False, postOperation = True, gui = gui)

    def post_process_python(self, gui: bool = False):
        """
        Runs the post-processing steps in the python PostProcess class.
        """

        postProc = PostProcess(self.fdm, self.solution_folder)
        postProc.show()

        return {'test': 0}

    def batch_post_process_python(self, gui: bool = False):
        pass


