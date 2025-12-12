import os
import sys
import time
if len(sys.argv) == 3:
    sys.path.insert(0, os.path.join(os.getcwd(), 'steam-fiqus-dev'))
from fiqus.geom_generators.GeometryCCT import Generate_BREPs
from fiqus.geom_generators.GeometryCCT import Prepare_BREPs
from fiqus.pre_processors.PreProcessCCT import Pre_Process
from fiqus.mesh_generators.MeshCCT import Mesh
from fiqus.getdp_runners.RunGetdpCCT import RunGetdpCCT
from fiqus.post_processors.PostProcessCCT import Post_Process
from fiqus.plotters.PlotPythonCCT import PlotPythonCCT

class MainCCT:
    def __init__(self, fdm, verbose=True):
        """
        Main class for working with simulations for CCT type magnets
        :param fdm: FiQuS data model
        :param verbose: if True, more info is printed in the console
        """
        # os.chdir(model_folder)
        self.verbose = verbose
        self.fdm = fdm
        self.settings = None
        self.geom_folder = None
        self.mesh_folder = None
        self.solution_folder = None
        self.model_file = None
        self.model_folder = None

    def generate_geometry(self, gui=False):
        os.chdir(self.geom_folder)
        gb = Generate_BREPs(fdm=self.fdm, verbose=self.verbose)
        gb.generate_windings_or_fqpls('windings')
        gb.save_volume_info()
        gb.generate_windings_or_fqpls('fqpls')
        gb.generate_formers()
        gb.generate_air()
        gb.generate_regions_file()

        pb = Prepare_BREPs(fdm=self.fdm, verbose=self.verbose)
        pb.straighten_terminal(gui=False)
        pb.extend_terms(operation='extend', gui=False)  # use operation='add' for externally generated brep files for windings
        pb.save_fqpl_vi()
        pb.fragment(gui=gui)
        self.model_file = pb.model_file
        self.model_folder = pb.model_folder

    def load_geometry(self, gui=False):
        os.chdir(self.geom_folder)
        pb = Prepare_BREPs(fdm=self.fdm, verbose=self.verbose)
        pb.load_geometry(gui=gui)
        self.model_file = pb.model_file
        self.model_folder = pb.model_folder

    def pre_process(self, gui=False):
        os.chdir(self.geom_folder)
        pp = Pre_Process(fdm=self.fdm)
        pp.calculate_normals(gui=gui)

    def mesh(self, gui=False):
        os.chdir(self.geom_folder)
        pb = Prepare_BREPs(fdm=self.fdm, verbose=self.verbose)
        pb.load_geometry(gui=False)
        os.chdir(self.mesh_folder)
        m = Mesh(fdm=self.fdm)
        m.generate_physical_groups()
        m.generate_mesh(gui=False)
        m.generate_cuts(gui=False)
        m.save_mesh(gui=gui)
        self.model_file = m.model_file
        self.model_folder = m.model_folder
        return {'gamma': 0}  # to be modified with mesh_parameters (see multipole)

    def load_mesh(self, gui=False):
        os.chdir(self.mesh_folder)
        m = Mesh(fdm=self.fdm)
        m.load_mesh(gui=gui)

    def solve_and_postprocess_getdp(self, gui=False):
        os.chdir(self.solution_folder)
        gb = Generate_BREPs(fdm=self.fdm, verbose=self.verbose)
        gb.generate_regions_file()
        rg = RunGetdpCCT(fdm=self.fdm, GetDP_path=self.GetDP_path)
        rg.assemble_pro()
        start_time = time.time()
        rg.solve_and_postprocess(gui=gui)
        self.model_file = rg.model_file
        self.model_folder = rg.model_folder
        return time.time() - start_time

    def post_process_getdp(self, gui=False):
        os.chdir(self.solution_folder)
        gb = Generate_BREPs(fdm=self.fdm, verbose=self.verbose)
        gb.generate_regions_file()
        rg = RunGetdpCCT(fdm=self.fdm, GetDP_path=self.GetDP_path)
        rg.assemble_pro()
        rg.postprocess(gui=gui)
        self.model_file = rg.model_file
        self.model_folder = rg.model_folder

    def post_process_python(self, gui=False):
        os.chdir(self.solution_folder)
        pp = Post_Process(self.fdm)
        pp.postprocess_fields(gui=gui)
        #pp.postprocess_thermal_connections()
        pp.postporcess_inductance()
        self.model_file = pp.model_file
        self.model_folder = pp.model_folder
        return {'overall_error': 0}  # to be modified with postprocess_parameters (see multipole)

    def plot_python(self):
        os.chdir(self.solution_folder)
        p = PlotPythonCCT(self.fdm)
        p.plot_elements_file()
