import os, json, gmsh

from fiqus.data import RegionsModelFiQuS
from fiqus.utils.Utils import GmshUtils, FilesAndFolders
from fiqus.data.RegionsModelFiQuS import RegionsModel
    
class Mesh:
    def __init__(self, fdm, verbose=True):
        """
        A base-class used to manage the mesh for HomogenizedConductor model.

        :ivar fdm: The fiqus data model for input parameters.
        :vartype fdm: dict
        """
        self.fdm = fdm
        self.mesh_folder = os.path.join(os.getcwd())
        self.geom_folder = os.path.dirname(self.mesh_folder)
        self.mesh_file = os.path.join(self.mesh_folder, f"{self.fdm.general.magnet_name}.msh")
        self.regions_file = os.path.join(self.mesh_folder, f"{self.fdm.general.magnet_name}.regions")
        self.vi_file = os.path.join(self.geom_folder, f'{self.fdm.general.magnet_name}.vi')
        self.verbose = verbose

        # dictionaries for physical groups
        self.dimTags_physical_surfaces = {}
        self.dimTags_physical_boundaries = {}
        self.dimTags_physical_cuts = {}
        self.dimTags_physical_points ={}

        # Read volume information file:
        with open(self.vi_file, "r") as f:
            self.dimTags = json.load(f)

        for key, value in self.dimTags.items():
            self.dimTags[key] = tuple(value) # dimTags contains all surfaces

        self.gu = GmshUtils(self.mesh_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

        gmsh.option.setNumber("General.Terminal", verbose)

    def generate_mesh(self):
        """ This function generates a mesh based on the volume information (vi) file created in the geometry step and the yaml input. """

        self.generate_physical_groups()

        # scale by domain size
        domain_size = self.fdm.magnet.geometry.air.radius
        # Mesh size field for cables:
        strand_field = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumbers(strand_field, "SurfacesList", [value[1] for key, value in self.dimTags.items() if 'Cable' in key])
        gmsh.model.mesh.field.setNumber(strand_field, "VIn", self.fdm.magnet.mesh.cable_mesh_size_ratio * domain_size)
        # Mesh size field for excitation coils:
        coil_field = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumbers(coil_field, "SurfacesList", [value[1] for key, value in self.dimTags.items() if 'Coil' in key])
        gmsh.model.mesh.field.setNumber(coil_field, "VIn", self.fdm.magnet.mesh.cable_mesh_size_ratio * domain_size)
        # Mesh size field for air:
        air_field = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumbers(air_field, "SurfacesList", [self.dimTags['Air'][1]])
        gmsh.model.mesh.field.setNumber(air_field, "VIn", self.fdm.magnet.mesh.air_boundary_mesh_size_ratio * domain_size)

        total_meshSize_field = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(total_meshSize_field, "FieldsList", [strand_field, coil_field, air_field])
        gmsh.model.mesh.field.setAsBackgroundMesh(total_meshSize_field)

        gmsh.option.setNumber("Mesh.MeshSizeFactor", self.fdm.magnet.mesh.scaling_global)
        gmsh.model.mesh.generate(2)


    def generate_physical_groups(self):
        """ This function generates the physical groups within the mesh based on the volume information (vi) file and stores their tags in dictionaries.

        :raises ValueError: For unknown volume names in the vi-file
        """
        gmsh.model.occ.synchronize()

        for key, value in self.dimTags.items():
            # surface
            surf_tag = gmsh.model.addPhysicalGroup(dim=value[0], tags=[value[1]], name=key)
            self.dimTags_physical_surfaces.update({str(key):(2, surf_tag)})
            # (outer) boundary curves
            if 'Air' in key:
                boundary_curves = gmsh.model.get_boundary([tuple(val) for val in self.dimTags.values()], combined=True)
            elif 'Cable' in key:
                boundary_curves = gmsh.model.get_boundary([tuple(value)]) 
            elif 'Coil' in key:
                boundary_curves = gmsh.model.get_boundary([tuple(value)]) 
            else:
                raise ValueError('Unknown volume in declaration in VI file.')
            bnd_tag = gmsh.model.addPhysicalGroup(dim=1, tags=[dimTag[1] for dimTag in boundary_curves], name=key+'Boundary' )
            self.dimTags_physical_boundaries.update({str(key+'Boundary' ):(1, bnd_tag)})
            # arbitrary boundary point
            point_tag = gmsh.model.addPhysicalGroup(dim=0, tags=[gmsh.model.get_boundary(boundary_curves, combined=False)[0][1]], name=key+'BoundaryPoint' )
            self.dimTags_physical_points.update({str(key+'BoundaryPoint' ):(1, point_tag)})


    def generate_cuts(self):
        """ This function generates and orients the domain cuts for the cable and coil regions through the gmsh internal homology module."""

        dimTags_physical_cable_boundaries = {k: v for k, v in self.dimTags_physical_boundaries.items() if 'Cable' in k}
        dimTags_physical_excitation_coil_boundaries = {k: v for k, v in self.dimTags_physical_boundaries.items() if 'Coil' in k}

        tags_physical_cable_surfaces = [v[1] for k, v in self.dimTags_physical_surfaces.items() if 'Cable' in k]
        tags_physical_excitation_coil_surfaces = [v[1] for k, v in self.dimTags_physical_surfaces.items() if 'Coil' in k]
        
        # print(dimTags_physical_cable_boundaries)
        # print(dimTags_physical_excitation_coil_boundaries)
        # print(tags_physical_cable_surfaces)
        # print(tags_physical_excitation_coil_surfaces)

        # cohomology cuts for all cables
        for _, value in dimTags_physical_cable_boundaries.items():
            gmsh.model.mesh.addHomologyRequest("Homology", domainTags=[value[1]], dims=[1])
        for _, value in dimTags_physical_excitation_coil_boundaries.items():
            gmsh.model.mesh.addHomologyRequest("Homology", domainTags=[value[1]], dims=[1])

        gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[self.dimTags_physical_surfaces['Air'][1]]+tags_physical_excitation_coil_surfaces, dims=[1])
        for coil_surface in tags_physical_excitation_coil_surfaces:
            tags_physical_excitation_other_coil_surfaces = [other_coil for other_coil in tags_physical_excitation_coil_surfaces if other_coil != coil_surface]
            gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[self.dimTags_physical_surfaces['Air'][1]]+tags_physical_cable_surfaces+tags_physical_excitation_other_coil_surfaces, dims=[1])



        dimTags_homology = gmsh.model.mesh.computeHomology()
        # print(dimTags_homology)
        dimTags_bnds = dimTags_homology[:int(len(dimTags_homology)/2)] # first half are dimTags are the cut boundaries
        dimTags_cuts = dimTags_homology[int(len(dimTags_homology)/2):] # second half are the actual cut edges
        gmsh.model.mesh.clearHomologyRequests()
        
        # post process homology cuts
        bnd_tags = []
        cut_tags = []
        for i in range(len(dimTags_physical_cable_boundaries)):
            self.dimTags_physical_cuts.update({'Cable'+str(i+1)+'Cut':(1, dimTags_cuts[-1][1]+(i+1))}) # +1 tag shift for post processed cuts
            bnd_tags.append(dimTags_bnds[i][1])
            cut_tags.append(dimTags_cuts[i][1])
        for i in range(len(dimTags_physical_excitation_coil_boundaries)):
            self.dimTags_physical_cuts.update({'Coil'+str(i+1)+'Cut':(1, dimTags_cuts[-1][1]+(len(dimTags_physical_cable_boundaries)+i+1))}) # +1 tag shift for post processed cuts
            bnd_tags.append(dimTags_bnds[len(dimTags_physical_cable_boundaries)+i][1])
            cut_tags.append(dimTags_cuts[len(dimTags_physical_cable_boundaries)+i][1])
        gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains", ','.join(map(str,bnd_tags)))
        gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains2", ','.join(map(str,cut_tags)))
        gmsh.plugin.run("HomologyPostProcessing")


    def generate_regions_file(self):
        """
        Generates a .regions file for the GetDP solver, containing all necessary information about the model.
        The regions model contains data about physical surfaces, boundaries, points and cuts and is stored in the mesh folder.

        :raises ValueError: For unknown volumes in the vi-file
        """
        regions_model = RegionsModel()

        # The region Cables will include the homogenized surfaces
        regions_model.powered['Cables'] = RegionsModelFiQuS.Powered()
        regions_model.powered['Cables'].vol.names = []
        regions_model.powered['Cables'].vol.numbers = []
        regions_model.powered['Cables'].surf.names = []
        regions_model.powered['Cables'].surf.numbers = [] 
        regions_model.powered['Cables'].curve.names = []
        regions_model.powered['Cables'].curve.numbers = [] 
        regions_model.powered['Cables'].cochain.names = []
        regions_model.powered['Cables'].cochain.numbers = [] 
        # Excitation coil regions
        regions_model.powered['ExcitationCoils'] = RegionsModelFiQuS.Powered()
        regions_model.powered['ExcitationCoils'].vol.names = []
        regions_model.powered['ExcitationCoils'].vol.numbers = []
        regions_model.powered['ExcitationCoils'].surf.names = []
        regions_model.powered['ExcitationCoils'].surf.numbers = [] 
        regions_model.powered['ExcitationCoils'].curve.names = []
        regions_model.powered['ExcitationCoils'].curve.numbers = [] 
        regions_model.powered['ExcitationCoils'].cochain.names = []
        regions_model.powered['ExcitationCoils'].cochain.numbers = [] 
       
        gmsh.model.occ.synchronize()
        for name in self.dimTags.keys():
            cut_name = name+'Cut'
            boundary_name = name+'Boundary'
            point_name = boundary_name+'Point'
            if 'Air' in name:
                regions_model.air.vol.number = self.dimTags_physical_surfaces[name][1]
                regions_model.air.vol.name = "Air"
                regions_model.air.surf.number = self.dimTags_physical_boundaries[boundary_name][1]
                regions_model.air.surf.name = boundary_name
                regions_model.air.point.names = [point_name]
                regions_model.air.point.numbers = [self.dimTags_physical_points[point_name][1]]
            elif 'Cable' in name:
                regions_model.powered['Cables'].vol.names.append(name)
                regions_model.powered['Cables'].vol.numbers.append(self.dimTags_physical_surfaces[name][1])
                regions_model.powered['Cables'].surf.names.append(boundary_name)
                regions_model.powered['Cables'].surf.numbers.append(self.dimTags_physical_boundaries[boundary_name][1])
                regions_model.powered['Cables'].curve.names.append(point_name)
                regions_model.powered['Cables'].curve.numbers.append(self.dimTags_physical_points[point_name][1])
                regions_model.powered['Cables'].cochain.names.append(cut_name)
                regions_model.powered['Cables'].cochain.numbers.append(self.dimTags_physical_cuts[cut_name][1])
            elif 'Coil' in name:
                regions_model.powered['ExcitationCoils'].vol.names.append(name)
                regions_model.powered['ExcitationCoils'].vol.numbers.append(self.dimTags_physical_surfaces[name][1])
                regions_model.powered['ExcitationCoils'].surf.names.append(boundary_name)
                regions_model.powered['ExcitationCoils'].surf.numbers.append(self.dimTags_physical_boundaries[boundary_name][1])
                regions_model.powered['ExcitationCoils'].curve.names.append(point_name)
                regions_model.powered['ExcitationCoils'].curve.numbers.append(self.dimTags_physical_points[point_name][1])
                regions_model.powered['ExcitationCoils'].cochain.names.append(cut_name)
                regions_model.powered['ExcitationCoils'].cochain.numbers.append(self.dimTags_physical_cuts[cut_name][1])
            else:
                raise ValueError('Unknown physical region')

        FilesAndFolders.write_data_to_yaml(self.regions_file, regions_model.model_dump())

    def save_mesh(self, gui: bool = False):
        """ Saves the mesh to a .msh file. If gui is True, the mesh is also loaded in the gmsh GUI. """
        
        gmsh.write(self.mesh_file)
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            if gmsh.isInitialized():
                gmsh.clear()
                gmsh.finalize()

    def load_mesh(self, gui : bool = False):
        """ Loads a previously generated mesh. """
        
        gmsh.clear()
        gmsh.open(self.mesh_file)

        if gui:
            self.gu.launch_interactive_GUI()

