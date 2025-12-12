import re
import copy

import numpy as np
import json
from operator import itemgetter

class ParserCOND:
    """
    Class for operations on Opera compatible conductor files
    """
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.br8 = [['SHAPE'],  # 'DEFINE' is keyword is ignored only the shape is propagated
                                ['XCENTRE', 'YCENTRE', 'ZCENTRE', 'PHI1', 'THETA1', 'PSI1'],
                                ['XCEN2', 'YCEN2', 'ZCEN2'],
                                ['THETA2', 'PHI2', 'PSI2'],
                                ['XP1', 'YP1', 'ZP1'],
                                ['XP2', 'YP2', 'ZP2'],
                                ['XP3', 'YP3', 'ZP3'],
                                ['XP4', 'YP4', 'ZP4'],
                                ['XP5', 'YP5', 'ZP5'],
                                ['XP6', 'YP6', 'ZP6'],
                                ['XP7', 'YP7', 'ZP7'],
                                ['XP8', 'YP8', 'ZP8'],
                                ['CURD', 'SYMMETRY'], # 'DRIVELABEL' is done separately due a possibility of a space in the string
                                ['IRXY', 'IRYZ', 'IRZX'],
                                ['TOLERANCE']]
        self.br8_def_txt = 'DEFINE BR8'
        self.drive_count = 0
        self.vertices_to_surf = [[1, 5, 8, 4], [2, 6, 7, 3], [2, 6, 5, 1], [3, 7, 8, 4], [1, 2, 3, 4], [5, 6, 7, 8]]
        self.vertices_to_lines = [[[1, 2], [5, 6], [8, 7], [4, 3]], [[1, 2], [5, 6], [8, 7], [4, 3]], [[1, 4], [2, 3], [6, 7], [5, 8]], [[1, 4], [2, 3], [6, 7], [5, 8]], [[1, 5], [2, 6], [3, 7], [4, 8]], [[1, 5], [2, 6], [3, 7], [4, 8]]]   # only z direction supported for now
        self._sur_names = ['x-', 'x+', 'y-', 'y+', 'z-', 'z+']
        self._op_sign = {'+': '-', '-': '+'}
        self._sign = {'+': 1, '-': -1}

    @staticmethod
    def scale_bricks(cond_dict, factor):
        """
        Scales the conductor file model by a factor
        :param cond_dict: conductor dictionary
        :param factor: factor, e.g. 0.001 to change conductor file from mm to m
        :return: conductor dictionary
        """
        append = False
        for idx, _ in enumerate(list(cond_dict.keys())):
            P1, P2, P3, P4, P5, P6, P7, P8 = ParserCOND.get_points_cond_dict(cond_dict, idx)
            arrays = [P1, P2, P3, P4, P5, P6, P7, P8]
            for i in range(len(arrays)):
                arrays[i] *= factor
            P1, P2, P3, P4, P5, P6, P7, P8 = arrays
            cond_dict = ParserCOND.set_points_cond_dict(cond_dict, idx, append, P1, P2, P3, P4, P5, P6, P7, P8)
        return cond_dict

    @staticmethod
    def merge_if_straight(bricks_dict, direction='z'):
        """
        Merges multiple bricks if they are on the straight line, i.e. if after merge the shape does not change
        :param bricks_dict: dictionary of bricks
        :type bricks_dict: dict
        :param direction: direction to look for, eg 'z'
        :type direction: str
        :return: dictionary of bricks
        :rtype: dict
        """

        coord_pos = {'x': 0, 'y': 1, 'z': 2}

        def merge_and_delete(bricks_dict, brick_i_from, brick_i_to):
            brick_from = bricks_dict[brick_i_from]
            brick_to = bricks_dict[brick_i_to]
            for p_num in range(4, 8):
                for cord in ['XP', 'YP', 'ZP']:
                    brick_from[f'{cord}{p_num + 1}'] = brick_to[f'{cord}{p_num + 1}']
            for brick_i in range(brick_i_from + 1, brick_i_to + 1):
                del bricks_dict[brick_i]
            return bricks_dict


        #num_bricks = len(bricks_dict.keys())
        brick_i_list = copy.deepcopy(list(bricks_dict.keys()))
        print(f'Started with {len(brick_i_list)}')
        brick_i_from = -1
        brick_i_to = -1
        for brick_i in brick_i_list:
            P1, P2, P3, P4, P5, P6, P7, P8 = ParserCOND.get_points_cond_dict(bricks_dict, brick_i, bynumber=True)
            if direction == 'z':
                if (P1[coord_pos['z']] == P2[coord_pos['z']] == P3[coord_pos['z']] == P4[coord_pos['z']]) and (P5[coord_pos['z']] == P6[coord_pos['z']] == P7[coord_pos['z']] == P8[coord_pos['z']]):
                    straight = True
                else:
                    straight = False
            else:
                raise ValueError(f"Direction {direction} is not yet implemented!")

            if straight and brick_i_from <= 0:
                brick_i_from = brick_i
            if (not straight and brick_i_from > 0) or (straight and brick_i_from > 0 and brick_i == max(brick_i_list)):
                brick_i_to = brick_i-1

            if brick_i_from > 0 and brick_i_to > 0:
                bricks_dict = merge_and_delete(bricks_dict, brick_i_from, brick_i_to)
                brick_i_from = -1
                brick_i_to = -1
        combined_bricks_dict = {}
        for brick_new_i, brick in enumerate(bricks_dict.values()):
            combined_bricks_dict[brick_new_i] = brick
        print(f'Ended with {len(list(combined_bricks_dict.keys()))}')
        return combined_bricks_dict

    def extend_terminals(self, cond_dict, extend_list):
        """
        Extends terminals by creating additional bricks starting at index brick start towards direction, until a position in m and uses number of bricks to get there.
        :param cond_dict: conductor dictionary
        :type cond_dict: dict
        :param extend_list: [index, direction, until position, number bricks] for example [0, 'z-', -1.25, 8] or [-1, 'z+', 0.25, 8]
        :type extend_list: list
        :return: conductor dictionary
        :rtype: dict
        """
        additional_bricks = []
        for extend in extend_list:
            index = extend[0]
            plane = extend[1]
            coord_ext_to = extend[2]
            n_bricks = extend[3]
            index_brick = list(cond_dict.keys())[index]
            brick = cond_dict[index_brick]
            points = self.vertices_to_surf[self._sur_names.index(plane)]
            op_points = self.vertices_to_surf[self._sur_names.index(plane[0] + self._op_sign[plane[1]])]
            coord = 'Z' #str.upper(plane[0])
            coord_0 = float(brick[f'{coord}P{points[0]}'])
            for point in points[1:]:
                coord_i = float(brick[f'{coord}P{point}'])
                if coord_i - coord_0 > 1e-6:
                    raise ValueError(f"This method only works on planes parallel to extension direction. Use straighten bricks method of this class first")
            #coord_dist = coord_ext_to-abs(coord_0)
            dist = coord_ext_to - coord_0
            if dist > 0:
                sign = -1
            else:
                sign = 1
            coord_dist = abs(coord_ext_to - coord_0)
            bricks_new = {}
            for n_b in range(n_bricks):
                new_brick = copy.deepcopy(brick)
                for p, op in zip(points, op_points):
                    for coord in ['X', 'Y', 'Z']:
                        new_brick[f'{coord}P{op}'] = brick[f'{coord}P{p}']
                        new_brick[f'{coord}P{p}'] = brick[f'{coord}P{p}']
                    new_brick[f'{coord}P{p}'] = str(float(brick[f'{coord}P{p}']) - sign * coord_dist / n_bricks)
                brick = copy.deepcopy(new_brick)
                bricks_new[n_b] = new_brick
            additional_bricks.append(bricks_new)
        idx = 0
        out_cond_dict = {}
        # start
        keys_list = list(additional_bricks[0].keys())
        keys_list.reverse()
        for key in keys_list:
            out_cond_dict[idx] = additional_bricks[0][key]
            idx += 1
        for brick in cond_dict.values():
            out_cond_dict[idx] = brick
            idx += 1
        for brick in additional_bricks[1].values():
            out_cond_dict[idx] = brick
            idx += 1
        return out_cond_dict

    def add_short_bricks_for_connections(self, cond_dict, connect_list):
        """
        Extends terminals by creating additional bricks starting at index brick start towards direction, until a position in m and uses number of bricks to get there.
        :param cond_dict: conductor dictionary
        :type cond_dict: dict
        :param connect_list: [index, direction, by brick dim along, number bricks] for example [0, 'z-', 'y', 8] or [-1, 'z+', 'x', 8]
        :type connect_list: list
        :return: conductor dictionary
        :rtype: dict
        """
        additional_bricks = []
        for connect in connect_list:
            index = connect[0]
            plane = connect[1]

            index_brick = list(cond_dict.keys())[index]
            brick = cond_dict[index_brick]
            points = self.vertices_to_surf[self._sur_names.index(plane)]
            op_points = self.vertices_to_surf[self._sur_names.index(plane[0] + self._op_sign[plane[1]])]
            coord = str.upper(plane[0])
            coord_0 = float(brick[f'{coord}P{points[0]}'])
            for point in points[1:]:
                coord_i = float(brick[f'{coord}P{point}'])
                if coord_i - coord_0 > 1e-6:
                    raise ValueError(f"This method only works on planes parallel to extension direction. Use straighten bricks method of this class first")
            along_coord = connect[2]

            points_along = self.vertices_to_surf[self._sur_names.index(f'{along_coord}+')]
            op_points_along = self.vertices_to_surf[self._sur_names.index(f'{along_coord}-')]
            point_a = []
            point_op = []
            for coord in ['X', 'Y', 'Z']:
                avg = []
                for p_along in points_along:
                    avg.append(float(brick[f'{coord}P{p_along}']))
                point_a.append(np.mean(avg))
                avg = []
                for op_p_along in op_points_along:
                    avg.append(float(brick[f'{coord}P{op_p_along}']))
                point_op.append(np.mean(avg))

            coord_dist = np.sqrt((point_op[0] - point_a[0]) ** 2 + (point_op[1] - point_a[1]) ** 2 + (point_op[2] - point_a[2]) ** 2)
            bricks_new = {}
            n_bricks = 1
            for n_b in range(n_bricks):
                new_brick = copy.deepcopy(brick)
                for p, op_p in zip(points, op_points):
                    new_brick[f'{coord}P{op_p}'] = str(new_brick[f'{coord}P{p}'])
                for p in points:
                    new_brick[f'{coord}P{p}'] = str(float(new_brick[f'{coord}P{p}']) + self._sign[plane[1]] * coord_dist / n_bricks)
                brick = copy.deepcopy(new_brick)
                bricks_new[n_b] = new_brick
            additional_bricks.append(bricks_new)
        idx = 0
        out_cond_dict = {}
        # start
        keys_list = list(additional_bricks[0].keys())
        keys_list.reverse()
        for key in keys_list:
            out_cond_dict[idx] = additional_bricks[0][key]
            idx += 1
        for brick in cond_dict.values():
            out_cond_dict[idx] = brick
            idx += 1
        for brick in additional_bricks[1].values():
            out_cond_dict[idx] = brick
            idx += 1
        return out_cond_dict

    def add_short_bricks_by_distance(self, cond_dict, short_brick_list):
        """
        Extends terminals by creating additional bricks starting at index brick start towards direction, until a position in m and uses number of bricks to get there.
        :param cond_dict: conductor dictionary
        :type cond_dict: dict
        :param connect_list: [index, direction, distance, number bricks] for example [0, 'z-', 0.001, 8] or [-1, 'z+', 0.001, 8]
        :type connect_list: list
        :return: conductor dictionary
        :rtype: dict
        """
        append = True
        for end in short_brick_list:
            idx, direction, distance = end
            P1, P2, P3, P4, P5, P6, P7, P8 = ParserCOND()._extend_brick_size(cond_dict, append, hexa_idx=idx, extension_distance=distance, extension_direction=direction)
            cond_dict = ParserCOND.set_points_cond_dict(cond_dict, idx, append, P1, P2, P3, P4, P5, P6, P7, P8)
        dict_out = {}
        for (idx, _), key in zip(enumerate(list(cond_dict.keys())), cond_dict.keys()):
            dict_out[idx] = cond_dict[key]
        return dict_out

    @staticmethod
    def resample_bricks(bricks_dict, f=1):
        """
        Combined number of bricks f into single brick
        :param bricks_dict: dictionary of bricks
        :type bricks_dict: dict
        :param f: how many bricks are combined
        :type f: int
        :return: dictionary of bricks
        :rtype: dict
        """
        num_bricks = len(bricks_dict.keys())
        for brick_ii in range(num_bricks):
            if brick_ii % f == 0:
                if brick_ii + f < num_bricks:
                    brick_i_from = brick_ii
                    brick_i_to = brick_ii + f - 1
                else:
                    brick_i_from = brick_ii
                    brick_i_to = num_bricks - 1
                brick_from = bricks_dict[brick_i_from]
                brick_to = bricks_dict[brick_i_to]
                for p_num in range(4, 8):
                    for cord in ['XP', 'YP', 'ZP']:
                        brick_from[f'{cord}{p_num + 1}'] = brick_to[f'{cord}{p_num + 1}']
                for brick_i in range(brick_i_from + 1, brick_i_to + 1):
                    del bricks_dict[brick_i]
            elif brick_ii > brick_i:
                if brick_ii < num_bricks - f:
                    del bricks_dict[brick_ii]
        combined_bricks_dict = {}
        for brick_new_i, brick in enumerate(bricks_dict.values()):
            combined_bricks_dict[brick_new_i] = brick
        #del combined_bricks_dict[brick_new_i]
        return combined_bricks_dict

    def get_br8_dict(self):
        """
        Creates conductor dict with some default values that are not yet used in FiQuS
        :return: conductor dictionary
        :rtype: dict
        """
        dict_out = {}
        for keys in self.br8:
            for key in keys:
                dict_out[key] = str(0.0)
        for key, value in zip(['SHAPE', 'SYMMETRY', 'IRXY', 'IRYZ', 'IRZX', 'TOLERANCE'], ['BR8', 1, 0, 0, 0, 1e-6]):
            dict_out[key] = str(value)
        return dict_out

    def write_cond(self, input_dict, cond_file_path):
        """
        Write conductor dictionary to a conductor file
        :param input_dict: conductor dictionary
        :type input_dict: dict
        :param cond_file_path: full path to the output conductor file
        :type cond_file_path: str
        :return: None, only writes file on disk
        :rtype: None
        """
        if self.verbose:
            print(f'Writing: {cond_file_path}')
        with open(cond_file_path, mode='w') as f:
            f.write('CONDUCTOR' + '\n')
            for _, value in input_dict.items():
                if value['SHAPE'] == 'BR8' or value['SHAPE'] == self.br8_def_txt:
                    params_list = self.br8
                    value['SHAPE'] = self.br8_def_txt
                else:
                    raise ValueError(f"FiQuS ParserCOND can not parse parse {value['SHAPE']} shape, yet!")
                lines = []
                for params in params_list:
                    line = ''
                    for param in params:
                        line += value[param] + ' '
                        if param == 'SYMMETRY':
                            line += f"'drive {str(self.drive_count)}'"
                    lines.append(line.strip() + '\n')   # strip space at the end (added 3 lines above) and add end of line to go to the new line
                f.writelines(lines)
            f.write('QUIT')
        self.drive_count += 1

    def read_cond(self, cond_file_path):
        """
        Reads conductor file and returns it as conductor dict
        :param cond_file_path: full path to the input conductor file
        :type cond_file_path:  str
        :return: conductor dictionary
        :rtype: dict
        """
        with open(cond_file_path, mode='r') as f:
            file_contents = f.read()
        #file_contents = re.sub('\n', "#", file_contents)    # replace end of lines with #
        file_contents = re.sub("'", '"', file_contents)     # replace ' (expected around DRIVELABEL string) with "
        lines = re.split('\n', file_contents)                # split on hases

        if lines.pop(0) != 'CONDUCTOR':
            raise ValueError(f'The file {cond_file_path} is not a valid Opera conductor file!')
        if lines.pop(-1) != 'QUIT':
            raise ValueError(f'The file {cond_file_path} is not a valid Opera conductor file!')

        if lines[0] == self.br8_def_txt:
            parameters_lists = self.br8
        else:
            raise ValueError(f'FiQuS ParserCOND can not parse parse {lines[0]} shape, yet!')

        num_lines = len(parameters_lists)
        num_of_shapes, rest = divmod(len(lines), num_lines)
        if rest != 0:
            raise ValueError(f'FiQuS ParserCOND can not parse parse conductor file with mixed shape types, yet!')

        output_dict = {}
        for block_i in range(num_of_shapes):
            output_dict[block_i] = {}
            blol = list(itemgetter(*range(block_i*num_lines, (block_i+1)*num_lines))(lines))    # blol = block list of lines
            for par_i, params_list_line in enumerate(parameters_lists):
                entry_list = re.split(' ', blol[par_i])
                if par_i == 0:
                    output_dict[block_i][params_list_line[0]] = entry_list[1]
                else:
                    for par, entry in zip(params_list_line, entry_list):
                        output_dict[block_i][par] = entry
                if par_i == 12:    # if this is the line with DRIVELABEL definiton that coudl contain a space character so need a different treatment
                    output_dict[block_i]['DRIVELABEL'] = blol[par_i][blol[par_i].find('"') + 1:-1]   # Get the content of line from the first found '"' character to the end of the file.
        return output_dict

    @staticmethod
    def get_points_cond_dict(cond_dict, hexa=None, bynumber=False):
        """
        Gets point, defined as numpy array with three coordinates for the 8-noded brick
        :param cond_dict: conductor dictionary
        :type cond_dict: dict
        :param hexa_idx: brick index
        :type hexa_idx: int
        :return: tuple with numpy arrays, each with tree coordinates of points in cartesian
        :rtype: tuple with arrays
        """
        if bynumber:
            hexa_number = hexa
        else:   # i.e. by index
            hexa_number = list(cond_dict.keys())[hexa]
        P1 = np.array([float(cond_dict[hexa_number]['XP1']), float(cond_dict[hexa_number]['YP1']), float(cond_dict[hexa_number]['ZP1'])])
        P2 = np.array([float(cond_dict[hexa_number]['XP2']), float(cond_dict[hexa_number]['YP2']), float(cond_dict[hexa_number]['ZP2'])])
        P3 = np.array([float(cond_dict[hexa_number]['XP3']), float(cond_dict[hexa_number]['YP3']), float(cond_dict[hexa_number]['ZP3'])])
        P4 = np.array([float(cond_dict[hexa_number]['XP4']), float(cond_dict[hexa_number]['YP4']), float(cond_dict[hexa_number]['ZP4'])])
        P5 = np.array([float(cond_dict[hexa_number]['XP5']), float(cond_dict[hexa_number]['YP5']), float(cond_dict[hexa_number]['ZP5'])])
        P6 = np.array([float(cond_dict[hexa_number]['XP6']), float(cond_dict[hexa_number]['YP6']), float(cond_dict[hexa_number]['ZP6'])])
        P7 = np.array([float(cond_dict[hexa_number]['XP7']), float(cond_dict[hexa_number]['YP7']), float(cond_dict[hexa_number]['ZP7'])])
        P8 = np.array([float(cond_dict[hexa_number]['XP8']), float(cond_dict[hexa_number]['YP8']), float(cond_dict[hexa_number]['ZP8'])])
        return P1, P2, P3, P4, P5, P6, P7, P8

    @staticmethod
    def set_points_cond_dict(cond_dict, hexa_idx, append, P1, P2, P3, P4, P5, P6, P7, P8):
        """
        Sets point, defined as numpy array with three coordinates for the 8-noded brick
        :param cond_dict: conductor dictionary
        :type cond_dict: dict
        :param hexa_idx: brick index
        :type hexa_idx: int
        :return: tuple with numpy arrays, each with tree coordinates of points in cartesian
        :rtype: tuple with arrays
        """
        points = [P1, P2, P3, P4, P5, P6, P7, P8]
        point_idx = [1, 2, 3, 4, 5, 6, 7, 8]
        coords = ['XP', 'YP', 'ZP']
        coord_idx = [0, 1, 2]
        hexa_number = list(cond_dict.keys())[hexa_idx]
        if append:
            hexa = copy.deepcopy(cond_dict[hexa_number])
        else:
            hexa = cond_dict[hexa_number]
        for point, point_i in zip(points, point_idx):
            for corr, corr_i in zip(coords, coord_idx):
                hexa[f'{corr}{point_i}'] = str(point[corr_i])

        if append:
            if hexa_idx == 0:
                new_hexa_idx = hexa_number-1
            elif hexa_idx == -1:
                new_hexa_idx = hexa_number+1
            cond_dict[new_hexa_idx] = hexa
            cond_dict = dict(sorted(cond_dict.items(), key=lambda x: int(x[0])))
        return cond_dict

    @staticmethod
    def _extend_brick_size(cond_dict, append, hexa_idx, extension_distance=0, extension_direction='top'):
        """
        Gets point, defined as numpy array with three coordinates for the 8-noded brick
        :param cond_dict: conductor dictionary
        :type cond_dict: dict
        :param hexa_idx: brick index
        :type hexa_idx: int
        :param extension_distance: distance in mm to extend the brick
        :type extension_distance: float
        :param extension_direction: string specifying the direction of the extension, the default is 'outer'
        :type extension_direction: str
        :return: tuple with numpy arrays, each with tree coordinates of points in cartesian
        :rtype: tuple with arrays
        """
        P1, P2, P3, P4, P5, P6, P7, P8 = ParserCOND.get_points_cond_dict(cond_dict, hexa_idx)

        if extension_direction == 'top': # north
            line1_direction = P4 - P1
            line2_direction = P3 - P2
            line3_direction = P8 - P5
            line4_direction = P7 - P6
            if append:
                P4 = P1.copy()
                P3 = P2.copy()
                P8 = P5.copy()
                P7 = P6.copy()
            P1 = P1 + line1_direction / np.linalg.norm(line1_direction) * extension_distance
            P2 = P2 + line2_direction / np.linalg.norm(line2_direction) * extension_distance
            P5 = P5 + line3_direction / np.linalg.norm(line3_direction) * extension_distance
            P6 = P6 + line4_direction / np.linalg.norm(line4_direction) * extension_distance
        elif extension_direction == 'bottom': # south
            line1_direction = P1 - P4
            line2_direction = P2 - P3
            line3_direction = P5 - P8
            line4_direction = P6 - P7
            if append:
                P1 = P4.copy()
                P2 = P3.copy()
                P5 = P8.copy()
                P6 = P7.copy()
            P4 = P4 + line1_direction / np.linalg.norm(line1_direction) * extension_distance
            P3 = P3 + line2_direction / np.linalg.norm(line2_direction) * extension_distance
            P8 = P8 + line3_direction / np.linalg.norm(line3_direction) * extension_distance
            P7 = P7 + line4_direction / np.linalg.norm(line4_direction) * extension_distance
        elif extension_direction == 'close':
            line1_direction = P1 - P5
            line2_direction = P2 - P6
            line3_direction = P3 - P7
            line4_direction = P4 - P8
            if append:
                P1 = P5.copy()
                P2 = P6.copy()
                P3 = P7.copy()
                P4 = P8.copy()
            P5 = P5 + line1_direction / np.linalg.norm(line1_direction) * extension_distance
            P6 = P6 + line2_direction / np.linalg.norm(line2_direction) * extension_distance
            P7 = P7 + line3_direction / np.linalg.norm(line3_direction) * extension_distance
            P8 = P8 + line4_direction / np.linalg.norm(line4_direction) * extension_distance
        elif extension_direction == 'far':
            line1_direction = P5 - P1
            line2_direction = P6 - P2
            line3_direction = P7 - P3
            line4_direction = P8 - P4
            if append:
                P5 = P1.copy()
                P6 = P2.copy()
                P7 = P3.copy()
                P8 = P4.copy()
            P1 = P1 + line1_direction / np.linalg.norm(line1_direction) * extension_distance
            P2 = P2 + line2_direction / np.linalg.norm(line2_direction) * extension_distance
            P3 = P3 + line3_direction / np.linalg.norm(line3_direction) * extension_distance
            P4 = P4 + line4_direction / np.linalg.norm(line4_direction) * extension_distance
        elif extension_direction == 'west':
            line1_direction = P4 - P3
            line2_direction = P8 - P7
            line3_direction = P5 - P6
            line4_direction = P1 - P2
            if append:
                P4 = P3.copy()
                P8 = P7.copy()
                P5 = P6.copy()
                P1 = P2.copy()
            P3 = P3 + line1_direction / np.linalg.norm(line1_direction) * extension_distance
            P7 = P7 + line2_direction / np.linalg.norm(line2_direction) * extension_distance
            P6 = P6 + line3_direction / np.linalg.norm(line3_direction) * extension_distance
            P2 = P2 + line4_direction / np.linalg.norm(line4_direction) * extension_distance
        elif extension_direction == 'east':
            line1_direction = P3 - P4
            line2_direction = P7 - P8
            line3_direction = P6 - P5
            line4_direction = P2 - P1
            if append:
                P3 = P4.copy()
                P7 = P8.copy()
                P6 = P5.copy()
                P2 = P1.copy()
            P4 = P4 + line1_direction / np.linalg.norm(line1_direction) * extension_distance
            P8 = P8 + line2_direction / np.linalg.norm(line2_direction) * extension_distance
            P5 = P5 + line3_direction / np.linalg.norm(line3_direction) * extension_distance
            P1 = P1 + line4_direction / np.linalg.norm(line4_direction) * extension_distance
        elif extension_direction == 'none':
            pass
        else:
            raise Exception(f"Only extension_direction='top', 'bottom', 'close', 'far' or 'none are supported, but the {extension_direction} was requested!")
        return P1, P2, P3, P4, P5, P6, P7, P8

    @staticmethod
    def extend_brick_idx(cond_dict, list_for_extension):
        """
        Extends or shortens a brick of idx
        list_for_extension is [idx, 'direction', distance], for example [0, 'far', 0.0015]
        """
        append = False
        for end in list_for_extension:
            idx, direction, distance = end
            P1, P2, P3, P4, P5, P6, P7, P8 = ParserCOND()._extend_brick_size(cond_dict, append, hexa_idx=idx, extension_distance=distance, extension_direction=direction)
            cond_dict = ParserCOND.set_points_cond_dict(cond_dict, idx, append, P1, P2, P3, P4, P5, P6, P7, P8)
        return cond_dict

    @staticmethod
    def extend_all_bricks(cond_dict, extension_distance=0.0, extension_direction='top', trim_list=[None, None]):
        """
        Extends a single brick by extension distance in the out pointing normal to the extension direction surface
        :param trim_list: decides to trim the which bricks get extended, if all use [None, None], if not last use [None, -1]
        :type trim_list: list
        :param cond_dict: conductor dictionary with bricks to extend
        :type cond_dict: dict
        :param extension_distance: distance to extend in m
        :type extension_distance: float
        :param extension_direction: extension direction as a keyword, only 'top' coded at the moment
        :type extension_direction: str
        :return: conductor dictionary with extended bricks
        :rtype: dict
        """
        append = False
        dict_keys = list(cond_dict.keys())[trim_list[0]:trim_list[1]]
        cond_dict_to_ext = {}
        for key in dict_keys:
            cond_dict_to_ext[key] = cond_dict[key]
        for idx, _ in enumerate(list(cond_dict_to_ext.keys())):
            P1, P2, P3, P4, P5, P6, P7, P8 = ParserCOND()._extend_brick_size(cond_dict_to_ext, append, hexa_idx=idx, extension_distance=extension_distance, extension_direction=extension_direction)
            cond_dict_to_ext = ParserCOND.set_points_cond_dict(cond_dict_to_ext, idx, append, P1, P2, P3, P4, P5, P6, P7, P8)
        for idx, brick in cond_dict_to_ext.items():
            cond_dict[key]=brick
        return cond_dict

    @staticmethod
    def trim_cond_dict(cond_dict, t_from, t_to):
        """
        Function to split conductor dictionary using t_from and t_to integers
        :param cond_dict: conductor dictionary
        :type cond_dict: dict
        :param t_from: output bricks starting from this index
        :type t_from: int
        :param t_to: output bricks up to this index
        :type t_to: int
        :return: trimmed conductor dictionary
        :rtype: dict
        """
        hex_list = list(cond_dict.keys())
        if t_to == 0:
            t_to = None  # this is to give all the last elements, i.e. no trimming from the end.
        elif t_to == -1:
            t_to = None
        trimmed_hex_list = hex_list[t_from:t_to]
        trimmed_cond_dict = {}
        for key in trimmed_hex_list:
            trimmed_cond_dict[key] = cond_dict[key]
        return trimmed_cond_dict

    def write_json(self, json_file_path):
        """
        Method for writing conductor bricks into a file. This is only used for testing the parser conductor functionality
        :param json_file_path: path to json output file
        :type json_file_path: str
        :return: none, only writes file to disk
        :rtype: none
        """
        json.dump(self.bricks, open(json_file_path, 'w'), sort_keys=False)

    @staticmethod
    def read_json(json_file_path):
        """
        Method for reading the json file. The string values for the key names in json are converted to integers
        :param json_file_path: full path to json file
        :type json_file_path: str
        :return: dictionary with values read from json, with keys as integers
        :rtype: dict
        """
        def jsonKeys2int(x):
            """
            Helper function for converting keys from strings to integers
            :param x: input dictionary
            :type x: dict
            :return: dictionary with key changed from str to int
            :rtype: dict
            """
            return {int(k): v for k, v in x.items()}    # change dict keys from strings to integers
        return jsonKeys2int(json.load(open(json_file_path)))

    @staticmethod
    def merge_conductor_dicts(cond_dict_list):
        output_dict = {}
        brick_i = 1
        for cond_dict in cond_dict_list:
            for brick in cond_dict.values():
                output_dict[brick_i] = brick
                brick_i += 1
        return output_dict

    @staticmethod
    def reverse_bricks(cond_dict):
        """
        Reverses sequence of bricks
        @param cond_dict: conductor dictionary
        @return: reversed conductor dictionary
        """
        keys = cond_dict.keys()
        values = [cond_dict[key] for key in keys]
        reversed_values = values[::-1]
        for key, value in zip(keys, reversed_values):
            cond_dict[key] = value
        return cond_dict

    @staticmethod
    def make_layer_jump_between(cond_dict_1, cond_dict_2, idx_from_to):
        idx_from, idx_to = idx_from_to
        P1_1, P2_1, P3_1, P4_1, P5_1, P6_1, P7_1, P8_1 = ParserCOND().get_points_cond_dict(cond_dict_1, hexa=idx_from, bynumber=False)
        P1_2, P2_2, P3_2, P4_2, P5_2, P6_2, P7_2, P8_2 = ParserCOND().get_points_cond_dict(cond_dict_2, hexa=idx_to, bynumber=False)
        # print([P1_1, P2_1, P3_1, P4_1, P5_1, P6_1, P7_1, P8_1])
        # print([P1_2, P2_2, P3_2, P4_2, P5_2, P6_2, P7_2, P8_2])
        P1_avg = [0.0, 0.0, 0.0]
        P2_avg = [0.0, 0.0, 0.0]
        P3_avg = [0.0, 0.0, 0.0]
        P4_avg = [0.0, 0.0, 0.0]
        for P_1, P_2, P_a in zip([P1_1, P2_1, P3_1, P4_1], [P1_2, P2_2, P3_2, P4_2], [P1_avg, P2_avg, P3_avg, P4_avg]):
            for i in range(3):
                P_a[i] = (P_1[i] + P_2[i])/2

        ParserCOND().set_points_cond_dict(cond_dict_1, idx_from, False, P1_avg, P2_avg, P3_avg, P4_avg, P5_1, P6_1, P7_1, P8_1)
        ParserCOND().set_points_cond_dict(cond_dict_2, idx_to, False, P1_avg, P2_avg, P3_avg, P4_avg, P5_2, P6_2, P7_2, P8_2)

        return cond_dict_1, cond_dict_2

    @staticmethod
    def combine_bricks(cond_dict, from_to_list):
        """
        Combines bricks into single brick approximating its size by taking the corners of the first and last surface
        :param cond_dict: conductor dictionary input
        :type cond_dict: dict
        :param from_to_list: list of lists specifying indexes at the start and end of the dictionary, e.g. [[0, 2], [-3, -1]] means combined brick from 0th to 2nd at the start and from -3rd to -1st at the end.
        :type from_to_list: list
        :return: conductor dictionary output
        :rtype: dict
        """
        for soe_i, p_nums in zip([0, 1], [range(0, 4), range(4, 8)]):  # soe = start or end (of the winding)
            brick_i_from = list(cond_dict.keys())[from_to_list[soe_i][0]]
            brick_i_to = list(cond_dict.keys())[from_to_list[soe_i][1]]
            brick_from = cond_dict[brick_i_from]
            brick_to = cond_dict[brick_i_to]
            for p_num in p_nums:
                for cord in ['XP', 'YP', 'ZP']:
                    if soe_i == 0:  # start
                        brick_to[f'{cord}{p_num + 1}'] = brick_from[f'{cord}{p_num + 1}']
                    elif soe_i == 1:  # end
                        brick_from[f'{cord}{p_num + 1}'] = brick_to[f'{cord}{p_num + 1}']
            for brick_i in range(brick_i_from + soe_i, brick_i_to + soe_i):
                del cond_dict[brick_i]
        combined_bricks_dict = {}
        for brick_new_i, brick in enumerate(cond_dict.values()):
            combined_bricks_dict[brick_new_i] = brick
        return combined_bricks_dict

    def straighten_brick(self, cond_dict, index_and_plane_list):
        """
        :param cond_dict: conductor dictionary
        :type cond_dict: dict
        :param index_and_plane_list: this is list, typically [0, 'z-'] or [-1, 'z+']. Index can be either 0 or -1 and plane can be either 'z-' or 'z+'
        :type index_and_plane_list: list
        :return: conductor dictionary
        :rtype: dict
        """
        for index_and_plane in index_and_plane_list:
            index = index_and_plane[0]
            if index not in [0, -1]:
                raise ValueError(f'Index can be either 0 or -1, but {index} was given!')
            plane = index_and_plane[1]
            # if plane not in ['z-', 'z+']:
            #     raise ValueError(f"Plane can be either 'z-' or 'z+', but {plane} was given!")

            brick_index = list(cond_dict.keys())[index_and_plane[0]]
            brick = cond_dict[brick_index]
            points = self.vertices_to_surf[self._sur_names.index(plane)]
            lines = self.vertices_to_lines[self._sur_names.index(plane)]
            coord = 'Z' #str.upper(plane[0])
            values = []
            def find_intersection_point(line, coord, z):
                v = {'X': float(brick[f'XP{line[1]}']) - float(brick[f'XP{line[0]}']),
                     'Y': float(brick[f'YP{line[1]}']) - float(brick[f'YP{line[0]}']),
                     'Z': float(brick[f'ZP{line[1]}']) - float(brick[f'ZP{line[0]}'])}
                t = (z - float(brick[f'{coord}P{line[0]}'])) / v[coord]
                x = float(brick[f'XP{line[0]}']) + t * v['X']
                y = float(brick[f'YP{line[0]}']) + t * v['Y']
                return (str(x), str(y), str(z))
            for point in points:
                value = float(brick[f'{coord}P{point}'])
                values.append(value)
            z = np.mean(values)
            for point, line in zip(points, lines):
                brick[f'XP{point}'], brick[f'YP{point}'], brick[f'ZP{point}'] = find_intersection_point(line, coord, z)
            cond_dict[brick_index] = brick
        return cond_dict

    @staticmethod
    def _make_combined_dict(from_cond_dict, to_cond_dict):
        new_key = 0
        from_cond_dict_out = {}
        for brick in from_cond_dict.values():
            from_cond_dict_out[new_key]=brick
            new_key+=1
        combined_dict = {}
        combined_dict.update({f'{key}': value for key, value in from_cond_dict_out.items()})
        last_key = list(from_cond_dict_out.keys())[-1]
        combined_dict.update({f'{key+last_key+1}': value for key, value in to_cond_dict.items()})
        return combined_dict

    def add_link_brick(self, twin_cond_dict, lists_for_connections, skip=False):
        """
        Adds link bricks
        :param twin_cond_dict: twin dictionary of type {first_winding_name: first_winding_bricks_dict, second_winding_name: second_winding_bricks_dict}
        :type twin_cond_dict: dict
        :param lists_for_connections: list of lists of lists of type [[[-1, 'y-', False], [-1, 'y-', True]], [[0, 'y-', False], [0, 'y-', True]]], where:
        [[start terminals],[end terminals]], for terminal end: [[brick id from, surface direction from, swap points to opposite side flag from], [brick id to, surface direction to, swap points to opposite side flag to]]
        :type lists_for_connections: list
        :return:
        :rtype:
        """
        if len(twin_cond_dict) != 2:
            raise ValueError(f'The twin_cond_dict can only contain two conductor sets, but it contains: {len(twin_cond_dict)} conductor sets')

        new_bricks_dict ={}
        for idx, end in enumerate(lists_for_connections):
            from_cond_dict = list(twin_cond_dict.values())[0]
            from_def = end[0]
            from_brick_index = list(from_cond_dict.keys())[from_def[0]]
            from_brick = from_cond_dict[from_brick_index]
            from_points = self.vertices_to_surf[self._sur_names.index(from_def[1])]
            from_points_op = self.vertices_to_surf[self._sur_names.index(from_def[1][0]+self._op_sign[from_def[1][1]])]
            to_cond_dict = list(twin_cond_dict.values())[1]
            to_def = end[1]
            to_brick_index = list(to_cond_dict.keys())[to_def[0]]
            to_brick = to_cond_dict[to_brick_index]
            to_points = self.vertices_to_surf[self._sur_names.index(to_def[1])]
            to_points_op = self.vertices_to_surf[self._sur_names.index(to_def[1][0] + self._op_sign[to_def[1][1]])]
            new_brick = copy.deepcopy(from_brick)

            for coord in ['X', 'Y', 'Z']:
                if from_def[2]:  #swap points to opposite side flag from
                    for d, s in zip(from_points_op, [from_points[1],from_points[0],from_points[3],from_points[2]]):
                        new_brick[f'{coord}P{d}'] = from_brick[f'{coord}P{s}']
                else:
                    for d, s in zip(from_points, from_points):
                        new_brick[f'{coord}P{d}'] = from_brick[f'{coord}P{s}']
                if to_def[2]: #swap points to opposite side flag to
                    for d, s in zip(to_points, list(reversed(to_points_op))):
                        new_brick[f'{coord}P{d}'] = to_brick[f'{coord}P{s}']
                else:
                    for d, s in zip(to_points, to_points):
                        new_brick[f'{coord}P{d}'] = to_brick[f'{coord}P{s}']
            new_bricks_dict[idx] = new_brick

        if not skip:
            for key, new_brick in new_bricks_dict.items():
                if key == 0:
                    first_key = list(list(twin_cond_dict.values())[0].keys())[0]
                    from_cond_dict[first_key-1] = new_brick
                else:
                    last_key = list(list(twin_cond_dict.values())[0].keys())[-2]
                    from_cond_dict[last_key+1] = new_brick
            from_cond_dict = {key: from_cond_dict[key] for key in sorted(from_cond_dict)}
        combined_dict = ParserCOND._make_combined_dict(from_cond_dict, to_cond_dict)
        return from_cond_dict, to_cond_dict, combined_dict