import gmsh
import statistics

class ParserMSH:
    def __init__(self, mesh_file_path):
        """
        Read msh file and returns mesh format and physical names as class attributes.
        :param mesh_file_path: Full path to .msh file, including file name and extension.
        """
        self.mesh_file_path = mesh_file_path

        self._mesh_format_markers = {'s': '$MeshFormat', 'e': '$EndMeshFormat'}
        self._physical_name_markers = {'s': 'PhysicalNames', 'e': '$EndPhysicalNames'}

        with open(mesh_file_path) as f:
            self._contents = f.read()

    def __get_content(self, markers_dict):
        """
        Gets text string between two markers specified in markers_dict
        """
        return self._contents[self._contents.find(markers_dict['s']) + len(markers_dict['s']):self._contents.find(markers_dict['e'])]

    def get_average_mesh_quality(self):
        """
        Gets the lowest mesh quality from the mesh file
        """
        gmsh.initialize()
        gmsh.open(self.mesh_file_path)

        # SICN not implemented in 1D!
        allElementsDim2 = gmsh.model.mesh.getElements(dim=2)[1]
        allElementsDim3 = gmsh.model.mesh.getElements(dim=3)[1]
        allElements = list(allElementsDim2[0]) + (list(allElementsDim3[0]) if allElementsDim3 else [])
        lowestQuality = statistics.fmean(gmsh.model.mesh.getElementQualities(allElements))

        gmsh.finalize()

        return lowestQuality

    @property
    def mesh_format(self):
        """
        Parse mesh_generators field and assign it to the class attribute
        """
        return self.__get_content(self._mesh_format_markers)

    @property
    def physical_names(self):
        """
        Parse physical_names field and assign it to the class attribute
        """
        return self.__get_content(self._physical_name_markers)
