import re
import inspect
import pandas as pd


class ParserPOS:

    def __init__(self, pos_file_path):
        """
        Read pos file and returns its content as object attribute .data_dict that is a dictionary.
        :param pos_file_path: Full path to .pos file, including file name and extension.
        """
        self._mesh_format_markers = {'s': '$MeshFormat', 'e': '$EndMeshFormat'}
        self._nodes_markers = {'s': '$Nodes', 'e': '$EndNodes'}
        self._elements_markers = {'s': '$Elements', 'e': '$EndElements'}
        self._elements_node_data_markers = {'s': '$ElementNodeData', 'e': '$EndElementNodeData'}
        self._physical_name_markers = {'s': 'PhysicalNames', 'e': '$EndPhysicalNames'}

        with open(pos_file_path, "r", encoding="utf-8", errors="replace") as f:
            self._contents = f.read()
        # node properteis
        self._node_numbers = []
        self._node_coordinates = []
        # element properties
        self._element_numbers = []
        self._element_types = []
        self._element_number_of_tags = []
        self._element_physical_tags = []
        self._element_elementary_tags = []
        self._element_node_numbers = []
        # elements_node_data properties
        self._data_element_tags = []
        self._data_num_nodes_per_element = []
        self._values = []
        # parse the content (output is in this class attributes)
        self._parse()

    def __get_content(self, markers_dict):
        """
        Gets text string between two markers specified in markers_dict
        """
        return self._contents[self._contents.find(markers_dict['s']) + len(markers_dict['s']):self._contents.find(markers_dict['e'])]

    @staticmethod
    def __get_lines(data_str, empty_lines=[0, -1]):
        """
        Converts text string into a list of lines
        """
        data_str = re.sub('\n', "'", data_str)
        data_str = re.sub('"', '', data_str)
        str_list = re.split("'", data_str)
        for empty_line in empty_lines:
            if not str_list.pop(empty_line) == '':
                raise ValueError('Error in parsing lines')
        return str_list

    @staticmethod
    def __list_from_list_at_pos(dest_list, source_list, d_type, pos):
        """
        This one is a bit complex. It converts a supplied in source list and appends it destination list.
        It uses data type and position to append to the right type to the destination list from the right place in the source list.
        Position could be an integer, a list of integers or a tuple with a reference variables to figure out positions from them.
        """
        if isinstance(pos, int):
            dest_list.append(d_type(source_list[pos]))
        elif isinstance(pos, list):
            dest_list.append([d_type(source_list[p]) for p in pos])
        elif isinstance(pos, tuple):
            offset = pos[0]
            dimension = pos[1]
            ref_list = pos[2]
            current_num_elem = ref_list[len(dest_list)]  # get current element
            pos = list(range(offset, dimension * current_num_elem + offset))
            dest_list.append([d_type(source_list[p]) for p in pos])

    def __parse_lines(self, lines, list_of_outputs_lists, list_of_data_types, list_of_positions, len_check, ):
        """
        Simply loop through lines and append to class attributes lists. Basic error check if number of lines in the list matches that declared in the file.
        """
        for line in lines:
            values = re.split(' ', line)
            for dest_list, d_type, pos in zip(list_of_outputs_lists, list_of_data_types, list_of_positions):
                self.__list_from_list_at_pos(dest_list, values, d_type, pos)
        for out_list in list_of_outputs_lists:
            if not len_check == len(out_list):
                raise ValueError(f'Error in parsing {inspect.stack()[1].function}')

    def _mesh_format(self):
        """
        Parse mesh_generators field and assign it to the class attribute
        """
        self.mesh_format = self.__get_content(self._mesh_format_markers)

    def _physical_names(self):
        """
        Parse physical_names field and assign it to the class attribute
        """
        self.physical_names = self.__get_content(self._physical_name_markers)

    def _nodes(self):
        """
        Parse nodes  and assign it to the class attributes
        """
        data_str = self.__get_content(self._nodes_markers)
        lines = self.__get_lines(data_str)
        self._number_of_nodes = int(lines.pop(0))
        list_of_outputs_lists = [self._node_numbers, self._node_coordinates]
        list_of_data_types = [int, float]
        list_of_positions = [0, [1, 2, 3]]
        self.__parse_lines(lines, list_of_outputs_lists, list_of_data_types, list_of_positions, self._number_of_nodes)

    def _elements(self):
        """
        Parse elements  and assign it to the class attributes
        """
        data_str = self.__get_content(self._elements_markers)
        lines = self.__get_lines(data_str)
        self._number_of_elements = int(lines.pop(0))
        list_of_outputs_lists = [self._element_numbers, self._element_types, self._element_number_of_tags, self._element_physical_tags, self._element_elementary_tags, self._element_node_numbers]
        list_of_data_types = [int, int, int, int, int, int]
        list_of_positions = [0, 1, 2, 3, 4, (5, 1, self._data_num_nodes_per_element)]
        self.__parse_lines(lines, list_of_outputs_lists, list_of_data_types, list_of_positions, self._number_of_elements)

    def _elements_node_data(self):
        """
        Parse elements data and assign it to the class attributes
        """
        data_str = self.__get_content(self._elements_node_data_markers)
        lines = self.__get_lines(data_str)
        self._numStringTags = int(lines.pop(0))
        self._stringTags = str(lines.pop(0))
        self._numRealTags = int(lines.pop(0))
        self._realTags = float(lines.pop(0))
        self._numIntegerTags = int(lines.pop(0))
        self._integerTags = int(lines.pop(0))
        self._entityDim = int(lines.pop(0))
        self._number_of_elements_data = int(lines.pop(0))
        self._not_sure = int(lines.pop(0))      # not sure what this number is
        list_of_outputs_lists = [self._data_element_tags, self._data_num_nodes_per_element, self._values]
        list_of_data_types = [int, int, float]
        list_of_positions = [0, 1, (2, self._entityDim, self._data_num_nodes_per_element)]
        self.__parse_lines(lines, list_of_outputs_lists, list_of_data_types, list_of_positions, self._number_of_elements_data)

    def __element_for_node(self):
        self._elem_list_for_nodes = []
        self._index_elem = []
        element_node_numbers = pd.DataFrame(self._element_node_numbers)
        for node in self._node_numbers:
            index = pd.Index
            i = -1
            while index.empty:
                i += 1
                index = element_node_numbers[element_node_numbers[i] == node].index
            self._elem_list_for_nodes.append(index[0])
            self._index_elem.append(i)

        # element_node_numbers = pd.DataFrame(self._element_node_numbers)
        # for node in self._node_numbers:
        #     column = []
        #     for i in range(len(element_node_numbers.loc[0, :])):
        #         index = element_node_numbers[element_node_numbers[i] == node].index
        #         column.append(index[0] if not index.empty else float('nan'))
        #     first_elem = np.nanmin(column)
        #     self._elem_list_for_nodes.append(int(first_elem))
        #     self._index_elem.append(column.index(first_elem))

        # for node in self._node_numbers:
        #     self._elem_list_for_nodes.append([i for i in range(len(self._element_node_numbers))
        #                                       if node in self._element_node_numbers[i]][0])
        #     self._index_elem.append(self._element_node_numbers[self._elem_list_for_nodes[-1]].index(node))

        # for node in self._node_numbers:
        #     n_idx = -1
        #     e_idx = 0
        #     while n_idx == -1:
        #         try:
        #             n_idx = self._element_node_numbers[e_idx].index(node)
        #             self._elem_list_for_nodes.append(e_idx)
        #             self._index_elem.append(n_idx)
        #         except ValueError:
        #             e_idx += 1

    def _node_values_dict(self):
        self.regions_dict = {}
        for reg_tag, elem_of_reg in zip(self._element_physical_tags, self._data_element_tags):
            if reg_tag not in self.regions_dict:
                self.regions_dict[reg_tag] = []
            self.regions_dict[reg_tag].append(elem_of_reg)

        self.elements_dict = {}
        for elem_tag, nodes_of_elem in zip(self._data_element_tags, self._element_node_numbers):
            self.elements_dict[elem_tag] = nodes_of_elem

        self.nodes_dict = {}
        for n_num, coors, elem_tag, idx in zip(self._node_numbers, self._node_coordinates,
                                               self._elem_list_for_nodes, self._index_elem):
            self.nodes_dict[n_num] = {}
            for i, key in zip(range(self._entityDim), ['x', 'y', 'z']):
                self.nodes_dict[n_num][key] = coors[i]
            for i, key in zip(range(self._entityDim), ['Vx', 'Vy', 'Vz']):
                self.nodes_dict[n_num][key] = self._values[elem_tag][idx * self._entityDim + i]
            self.nodes_dict[n_num]['e'] = self._data_element_tags[elem_tag]

    def _parse(self):
        """
        Call all parsing functions in the right sequence.
        """
        self._mesh_format()
        self._physical_names()
        self._nodes()
        self._elements_node_data()  # this one needs to be called before _elements method.
        self._elements()
        self.__element_for_node()
        self._node_values_dict()
