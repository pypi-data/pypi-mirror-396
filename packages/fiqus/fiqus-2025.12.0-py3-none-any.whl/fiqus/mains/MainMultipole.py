import os
import gmsh
import time

from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import FilesAndFolders as Util
from fiqus.data import DataFiQuS as dF
from fiqus.data.DataRoxieParser import FiQuSGeometry
from fiqus.geom_generators.GeometryMultipole import Geometry
from fiqus.mesh_generators.MeshMultipole import Mesh
from fiqus.getdp_runners.RunGetdpMultipole import RunGetdpMultipole
from fiqus.getdp_runners.RunGetdpMultipole import AssignNaming
from fiqus.post_processors.PostProcessMultipole import PostProcess
from fiqus.plotters.PlotPythonMultipole import PlotPythonMultipole


class MainMultipole:
    def __init__(self, fdm: dF.FDM = None, rgd_path: str = None, verbose: bool = None):
        """
        Main class for working with simulations for multipole type magnets
        :param fdm: FiQuS data model
        :param rgd_path: ROXIE geometry data path
        :param verbose: if True, more info is printed in the console
        """
        self.fdm = fdm
        self.rgd = rgd_path
        self.verbose = verbose

        self.GetDP_path = None
        self.geom_folder = None
        self.mesh_folder = None
        self.solution_folder = None

    def force_symmetry(self):
        fdm = self.fdm.__deepcopy__()
        fdm.magnet.geometry.electromagnetics.symmetry = 'x'
        return fdm
    def generate_geometry(self, gui: bool = False):
        geom = Util.read_data_from_yaml(self.rgd, FiQuSGeometry)
        fdm = self.force_symmetry() if 'solenoid' in geom.Roxie_Data.coil.coils[1].type else self.fdm  # todo: this should be handled by pydantic
        if self.fdm.magnet.geometry.plot_preview:
            plotter = PlotPythonMultipole(geom, self.fdm)
            plotter.plot_coil_wedges()
        gg = Geometry(data=fdm, geom=geom, geom_folder=self.geom_folder, verbose=self.verbose)
        gg.saveHalfTurnCornerPositions()
        geometry_settings = {'EM': fdm.magnet.geometry.electromagnetics, 'TH': self.fdm.magnet.geometry.thermal}
        geometry_type_list = []
        if fdm.magnet.geometry.electromagnetics.create: geometry_type_list.append('EM')
        if fdm.magnet.geometry.thermal.create: geometry_type_list.append('TH')
        for geometry_type in geometry_type_list:
            gg.saveStrandPositions(geometry_type)
            if geometry_settings[geometry_type].with_iron_yoke:
                gg.constructIronGeometry(geometry_settings[geometry_type].symmetry if geometry_type == 'EM' else 'none')
            gg.constructCoilGeometry(geometry_type)
            if geometry_settings[geometry_type].with_wedges:
                gg.constructWedgeGeometry(geometry_settings[geometry_type].use_TSA if geometry_type == 'TH' else False)
            gmsh.model.occ.synchronize()
            if geometry_type == 'TH':
                if geometry_settings[geometry_type].use_TSA:
                    gg.constructThinShells(geometry_settings[geometry_type].with_wedges)
                else:
                    gg.constructInsulationGeometry()
            gg.buildDomains(geometry_type, geometry_settings[geometry_type].symmetry if geometry_type == 'EM' else 'none')
            if geometry_type == 'EM':
                gg.fragment()
            gg.saveBoundaryRepresentationFile(geometry_type)
            gg.loadBoundaryRepresentationFile(geometry_type)
            gg.updateTags(geometry_type, geometry_settings[geometry_type].symmetry if geometry_type == 'EM' else 'none')
            gg.saveAuxiliaryFile(geometry_type)
            gg.clear()
        gg.ending_step(gui)

    def load_geometry(self, gui: bool = False):
        pass
        # gu = GmshUtils(self.geom_folder, self.verbose)
        # gu.initialize(verbosity_Gmsh=self.fdm.run.verbosity_Gmsh)
        # model_file = os.path.join(self.geom_folder, self.fdm.general.magnet_name)
        # gmsh.option.setString(name='Geometry.OCCTargetUnit', value='M')  # set units to meters
        # gmsh.open(model_file + '_EM.brep')
        # gmsh.open(model_file + '_TH.brep')
        # if gui: gu.launch_interactive_GUI()

    def pre_process(self, gui: bool = False):
        pass

    def load_geometry_for_mesh(self, run_type):
        gu = GmshUtils(self.geom_folder, self.verbose)
        gu.initialize(verbosity_Gmsh=self.fdm.run.verbosity_Gmsh)
        model_file = os.path.join(self.geom_folder, self.fdm.general.magnet_name)
        gmsh.option.setString(name='Geometry.OCCTargetUnit', value='M')  # set units to meters
        gmsh.open(model_file + f'_{run_type}.brep')

    def mesh(self, gui: bool = False):
        mm = Mesh(data=self.fdm, mesh_folder=self.mesh_folder, verbose=self.verbose)
        geom = Util.read_data_from_yaml(self.rgd, FiQuSGeometry)
        fdm = self.force_symmetry() if 'solenoid' in geom.Roxie_Data.coil.coils[1].type else self.fdm
        geometry_settings = {'EM': fdm.magnet.geometry.electromagnetics, 'TH': self.fdm.magnet.geometry.thermal}
        mesh_settings = {'EM': fdm.magnet.mesh.electromagnetics, 'TH': fdm.magnet.mesh.thermal}
        mesh_type_list = []
        if fdm.magnet.mesh.electromagnetics.create: mesh_type_list.append('EM')
        if fdm.magnet.mesh.thermal.create: mesh_type_list.append('TH')
        for physics_solved in mesh_type_list:
            self.load_geometry_for_mesh(physics_solved)
            if physics_solved == 'TH' and self.fdm.magnet.geometry.thermal.use_TSA:
                mm.loadStrandPositions(physics_solved)
            mm.loadAuxiliaryFile(physics_solved)
            if geometry_settings[physics_solved].with_iron_yoke:
                mm.getIronCurvesTags()
            mm.defineMesh(geometry_settings[physics_solved], mesh_settings[physics_solved], physics_solved)
            mm.createPhysicalGroups(geometry_settings[physics_solved])
            mm.updateAuxiliaryFile(physics_solved)
            if geometry_settings[physics_solved].model_dump().get('use_TSA', False):
                mm.rearrangeThinShellsData()
            mm.assignRegionsTags(geometry_settings[physics_solved], mesh_settings[physics_solved])
            mm.saveRegionFile(physics_solved)
            mm.setMeshOptions(physics_solved)
            mm.generateMesh()
            mm.checkMeshQuality()
            mm.saveMeshFile(physics_solved)
            if geometry_settings[physics_solved].model_dump().get('use_TSA', False):
                mm.saveClosestNeighboursList()
                if self.fdm.magnet.mesh.thermal.isothermal_conductors: mm.selectMeshNodes(elements='conductors')
                if self.fdm.magnet.geometry.thermal.with_wedges and self.fdm.magnet.mesh.thermal.isothermal_wedges: mm.selectMeshNodes(elements='wedges')
                mm.saveRegionCoordinateFile(physics_solved)
            mm.clear()
        mm.ending_step(gui)
        return mm.mesh_parameters

    def load_mesh(self, gui: bool = False):
        gu = GmshUtils(self.geom_folder, self.verbose)
        gu.initialize(verbosity_Gmsh=self.fdm.run.verbosity_Gmsh)
        gmsh.open(f"{os.path.join(self.mesh_folder, self.fdm.general.magnet_name)}.msh")
        if gui: gu.launch_interactive_GUI()

    def solve_and_postprocess_getdp(self, gui: bool = False):
        an = AssignNaming(data=self.fdm)
        rg = RunGetdpMultipole(data=an, solution_folder=self.solution_folder, GetDP_path=self.GetDP_path, verbose=self.verbose)
        rg.loadRegionFiles()
        if self.fdm.magnet.solve.thermal.solve_type and self.fdm.magnet.geometry.thermal.use_TSA:
            rg.loadRegionCoordinateFile()
        rg.assemblePro()
        start_time = time.time()
        rg.solve_and_postprocess()
        rg.ending_step(gui)
        return time.time() - start_time

    def post_process_getdp(self, gui: bool = False):
        an = AssignNaming(data=self.fdm)
        rg = RunGetdpMultipole(data=an, solution_folder=self.solution_folder, GetDP_path=self.GetDP_path, verbose=self.verbose)
        rg.loadRegionFiles()
        if self.fdm.magnet.solve.thermal.solve_type and self.fdm.magnet.geometry.thermal.use_TSA:
            rg.loadRegionCoordinateFile()
        rg.assemblePro()
        rg.postprocess()
        rg.ending_step(gui)

    def post_process_python(self, gui: bool = False):
        if self.fdm.run.type == 'post_process_python_only':
            an = AssignNaming(data=self.fdm)
            data = an.data
        else: data = self.fdm

        run_types = []
        if self.fdm.magnet.solve.electromagnetics.solve_type: run_types.append('EM')
        if self.fdm.magnet.solve.thermal.solve_type: run_types.append('TH')
        pp_settings = {'EM': self.fdm.magnet.postproc.electromagnetics, 'TH': self.fdm.magnet.postproc.thermal}
        pp = PostProcess(data=data, solution_folder=self.solution_folder, verbose=self.verbose)
        for run_type in run_types:
            pp.prepare_settings(pp_settings[run_type])
            pp.loadStrandPositions(run_type)
            pp.loadAuxiliaryFile(run_type)
            if pp_settings[run_type].plot_all != 'False': pp.loadHalfTurnCornerPositions()
            if pp_settings[run_type].model_dump().get('take_average_conductor_temperature', False): pp.loadRegionFile()
            pp.postProcess(pp_settings[run_type])
            if run_type == 'EM' and self.fdm.magnet.geometry.electromagnetics.symmetry != 'none': pp.completeMap2d()
            pp.clear()
        pp.ending_step(gui)
        return pp.postprocess_parameters

    def plot_python(self):
        os.chdir(self.solution_folder)
        p = PlotPythonMultipole(self.fdm, self.fdm)
        p.plot_coil_wedges()
