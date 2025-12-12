import os, cProfile

from fiqus.geom_generators.GeometryConductorAC_Strand import Geometry
from fiqus.mesh_generators.MeshConductorAC_Strand import Mesh, StrandMesh
from fiqus.getdp_runners.RunGetdpConductorAC_Strand import Solve
from fiqus.post_processors.PostProcessConductorAC import PostProcess, BatchPostProcess


class MainConductorAC_Strand:
    def __init__(self, fdm, inputs_folder_path='', outputs_folder_path='', verbose=True):
        """
        Main class for working with simulations for the Conductor AC model.
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
        Generates the strand geometry.
        """
        os.chdir(self.geom_folder)
        g = Geometry(fdm=self.fdm, inputs_folder_path=self.inputs_folder_path, verbose=self.verbose)
        g.generate_strand_geometry(gui)

    def load_geometry(self, gui: bool = False):
        """
        Loads the previously generated geometry from the .brep file.
        """
        os.chdir(self.geom_folder)
        g = Geometry(fdm=self.fdm, inputs_folder_path=self.inputs_folder_path, verbose=self.verbose)
        g.load_conductor_geometry(gui)
        # self.model_file = g.model_file

    def pre_process(self, gui=False):
        pass

    def mesh(self, gui: bool = False):
        """
        Generates the mesh for the strand geometry.
        """
        os.chdir(self.mesh_folder)

        m = StrandMesh(fdm=self.fdm, verbose=self.verbose)
        m.generate_mesh(self.geom_folder)
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
        s.get_solution_parameters_from_yaml(inputs_folder_path=self.inputs_folder_path)
        s.assemble_pro()
        s.run_getdp(solve=True, postOperation=True, gui=gui)
        s.cleanup()

    # def pre_process(self):
    #     os.chdir(self.solution_folder)

    #     s = Solve(self.fdm, self.GetDP_path, self.mesh_folder, self.verbose)

    def post_process_getdp(self, gui: bool = False):
        """
        Runs the post-processing steps trough GetDP.
        """
        os.chdir(self.solution_folder)

        s = Solve(self.fdm, self.GetDP_path, self.geom_folder, self.mesh_folder, self.verbose)
        s.read_excitation(inputs_folder_path=self.inputs_folder_path)
        s.get_solution_parameters_from_yaml(inputs_folder_path=self.inputs_folder_path)
        s.assemble_pro()
        s.run_getdp(solve=False, postOperation=True, gui=gui)

    #
    def post_process_python(self, gui: bool = False):
        # os.chdir(self.solution_folder)
        postProc = PostProcess(self.fdm, self.outputs_folder_path)

        if self.fdm.magnet.postproc.plot_instantaneous_power:
            postProc.instantaneous_loss()

        if self.fdm.magnet.postproc.plot_flux.show:
            postProc.internal_flux()

        postProc.plotter.show()

        return {'test': 0}

    def batch_post_process_python(self, gui: bool = False):
        """
        Runs batch post-processing steps using Python.
        Used for gathering, analysing, comparing and plotting data from multiple simulations.
        """
        BatchPostProc = BatchPostProcess(self.fdm, lossMap_gridData_folder=None, inputs_folder_path=self.inputs_folder_path, outputs_folder_path=self.outputs_folder_path)

        if self.fdm.magnet.postproc.batch_postproc.loss_map.produce_loss_map:
            # plotter.save_lossMap_gridData()
            # plotter.save_magnetization()
            BatchPostProc.plotter.create_lossMap()

        if self.fdm.magnet.postproc.batch_postproc.loss_map.cross_section.plot_cross_section:
            BatchPostProc.plotter.plot_lossMap_crossSection()

        if self.fdm.magnet.postproc.batch_postproc.loss_map.cross_section_sweep.animate_cross_section_sweep:
            BatchPostProc.plotter.animate_lossMap_crossSection()

        if self.fdm.magnet.postproc.batch_postproc.plot2d.produce_plot2d:
            BatchPostProc.plotter.plot2d()

        if self.fdm.magnet.postproc.batch_postproc.rohf_on_grid.fit_rohf or self.fdm.magnet.postproc.batch_postproc.rohf_on_grid.produce_error_map:
            BatchPostProc.rohf_on_grid()


