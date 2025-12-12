import os, json, gmsh, logging

from fiqus.utils.Utils import GmshUtils
from typing import Tuple

logger = logging.getLogger('FiQuS')

class Rectangle:
    """ A class to represent a rectangular surface in gmsh. """
    def __init__( self, x_center, y_center, z_center, width, height, name) -> None:
        self.name = name

        self.x_center = x_center
        self.y_center = y_center
        self.z_center = z_center
        self.width = width
        self.height = height

        self.tag = gmsh.model.occ.addRectangle(x_center-width/2, y_center-height/2, z_center, width, height)
        self.dimTag: Tuple = (2, self.tag)            


class Circle:
    """ A class to represent a circle surface in gmsh. """
    def __init__(self, x_center, y_center, z_center, radius, name) -> None:
        self.name = name

        self.x_center = x_center
        self.y_center = y_center
        self.z_center = z_center
        self.radius = radius

        self.tag = gmsh.model.occ.addDisk(self.x_center, self.y_center, self.z_center, radius, radius)
        self.dimTag: Tuple = (2, self.tag)


class HomogenizedConductor:
    """
    A class representing the geometry of a 2D cross section containing multiple cables and excitation coils in an isolating medium.

    :ivar cables: list of surfaces representing the cable cross sections.
    :vartype cables: list[list[Surface]]
    :ivar excitation_coils: list of surfaces representing the excitation coils cross sections.
    :vartype excitation_coils: list[list[Surface]]
    :ivar Air: Surrounding surface representing the air region.
    :vartype Air: Surface
    """
    def __init__(self, fdm) -> None:
        """
        Initializes the HomogenizedConductor object.
        """
        self.fdm = fdm

        self.cables = self.generate_cables()
        self.excitation_coils = self.generate_excitation_coils()
        self.air = self.generate_air()

    def generate_cables(self):
        """ 
        This function generates a list of rectangular surfaces according to the specifications of the cables within the yaml.

        :return: List of rectangle surfaces
        """
        cables = []
        for idx, cable in enumerate(self.fdm.magnet.geometry.cables_definition):
            cables.append(Rectangle(cable.center_position[0],cable.center_position[1],cable.center_position[2], 
                                        cable.width, cable.height, name='Cable'+str(idx+1)))
        return cables

    def generate_excitation_coils(self):
        """ 
        This function generates a list of rectangular surfaces according to the specifications of the excitation coils within the yaml.

        :return: List of rectangle surfaces
        """
        excitation_coils = []
        for idx, excitation_coil in enumerate(self.fdm.magnet.geometry.excitation_coils):
            excitation_coils.append(Rectangle(excitation_coil.center_position[0],excitation_coil.center_position[1],excitation_coil.center_position[2], 
                                        excitation_coil.width, excitation_coil.height, name='Coil'+str(idx+1)))
        return excitation_coils

    def generate_air(self):
        """
        This function generates the surrounding air surface by fragmenting a base surface with the previously defined cable surfaces.

        :raises ValueError: 'circle' is the only defined air surface form
        :return: fragmented air surface
        """
        if self.fdm.magnet.geometry.air_form == 'circle':
            air_pos = self.fdm.magnet.geometry.air.center_position
            air = Circle(air_pos[0],air_pos[1],air_pos[2],
                                self.fdm.magnet.geometry.air.radius, name='Air')
        else:
            raise ValueError('Undefined air_form.')
        # fragment air with cables and excitation coils
        gmsh.model.occ.synchronize()
        outDimTags, outDimTagsMap = gmsh.model.occ.fragment([(2, air.tag)], [cable.dimTag for cable in self.cables] + [excitation_coil.dimTag for excitation_coil in self.excitation_coils])
        return air
    
    def get_vi_dictionary(self):
        """ 
        This function dumps the dimTags of all surfaces into one dictionary, which can be used to generate the volume information file.

        :return: dictionary with volume information
        """
        vi_dictionary = {}
        # add all cables
        for cable in self.cables:
            vi_dictionary.update({str(cable.name):list(cable.dimTag)})
        # add all excitation coils
        for excitation_coil in self.excitation_coils:
            vi_dictionary.update({str(excitation_coil.name):list(excitation_coil.dimTag)})
        # add air
        vi_dictionary.update({str(self.air.name):list(self.air.dimTag)})
        return vi_dictionary


class Geometry:
    def __init__(self, fdm, inputs_folder_path, verbose=True) -> None:
        """ 
        Initializes the Geometry class.
        
        :param fdm: The fiqus data model.
        :type fdm: object
        :param inputs_folder_path: The full path to the folder with input files, i.e., conductor and STEP files.
        :type inputs_folder_path: str
        :param verbose: If True, more information is printed in the Python console. Defaults to True.
        :type verbose: bool, optional
        """
        self.fdm = fdm
        self.inputs_folder = inputs_folder_path
        self.geom_folder = os.path.join(os.getcwd())
        self.geom_file = os.path.join(self.geom_folder, f'{fdm.general.magnet_name}.brep')
        self.vi_file = os.path.join(self.geom_folder, f'{fdm.general.magnet_name}.vi')
        self.verbose = verbose
        # start GMSH
        self.gu = GmshUtils(self.geom_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)
        # To see the surfaces in a better way in GUI:
        gmsh.option.setNumber("Geometry.SurfaceType", 2)

    def generate_geometry(self):
        """
        Generates the geometry of conductors within a surrounding air region as specified in the yaml.

        :param gui: If True, launches an interactive GUI after generating the geometry. Default is False.
        :type gui: bool, optional
        :return: None
        """
        logger.info("Generating geometry")
        
        # 1) Either load the geometry from a yaml file or create the model from scratch
        self.geometry = HomogenizedConductor(fdm=self.fdm)
        
        gmsh.model.occ.synchronize()
        logger.info("Writing geometry")
        gmsh.write(self.geom_file) # Write the geometry to a .brep file

    def load_geometry(self):
        """ Loads geometry from .brep file. """
        logger.info("Loading geometry")

        gmsh.clear()
        gmsh.model.occ.importShapes(self.geom_file, format="brep")
        gmsh.model.occ.synchronize()

    def generate_vi_file(self, gui=False):
        """
        Generates volume information file. Volume information file stores dimTags of all
        the stored volumes. Since this model is 2D, those volumes are equivalent to simple surfaces.
        """

        dimTagsDict = self.geometry.get_vi_dictionary()
        with open(self.vi_file, 'w') as f:
            json.dump(dimTagsDict, f)

        if gui:
            #self.generate_physical_groups()
            self.gu.launch_interactive_GUI()
        else:
            if gmsh.isInitialized():
                gmsh.clear()
                gmsh.finalize()
