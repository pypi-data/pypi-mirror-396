import os
import copy
import math
import collections
import logging

import json
import timeit
import numpy as np
import gmsh

from fiqus.data import RegionsModelFiQuS as Reg_Mod_FiQ
from fiqus.data.DataWindingsCCT import WindingsInformation  # for winding information
from fiqus.utils.Utils import FilesAndFolders as uff
from fiqus.utils.Utils import GmshUtils

logger = logging.getLogger(__name__)
class Hexahedrons:

    def __init__(self):
        """
        Points generator for CCT windings to give hexahedron volumes for hexahedron meshing in Gmsh.
        """
        self.vertices_to_surf = [[0, 4, 7, 3], [1, 5, 6, 2], [1, 5, 4, 0], [2, 6, 7, 3], [0, 1, 2, 3], [4, 5, 6, 7]]
        # Node ordering following Gmsh for hexahedron https://gmsh.info/doc/texinfo/gmsh.html#Legacy-formats --> node ordering
        # above _vertices_to_surf is only used for manipulation of the hexahedra points on the data model level. Gmsh uses points connections and line connections for creating surfaces

        self.hexes = {}
        self._corner_points = {}
        self._sur_names = ['x-', 'x+', 'y-', 'y+', 'z-', 'z+']
        self._op_sign = {'+': '-', '-': '+'}
        self._sign = {1: '+', -1: '-'}

    def _add_corner_points(self, corner_num, x, y, z, ct):
        self._corner_points[corner_num] = {'x': x, 'y': y, 'z': z, 'ct': ct}  # ct is channel turn

    def _generate_hexes(self):
        for h in range(len(self._corner_points[0]['x'])):
            self.hexes[h] = {}
            for p_num, p_coor in self._corner_points.items():
                self.hexes[h][p_num] = {}
                for coor in ['x', 'y', 'z']:
                    self.hexes[h][p_num][coor] = p_coor[coor][h]
            self.hexes[h]['ct'] = p_coor['ct'][h]
        return p_coor['ct'][h]

    def _add_elem_to_elem(self, start_elem, dir_str, dist):
        """
        :param start_elem: idx of start element
        :param dir_str: direction of adding element, options are: 'x-', 'x+', 'y-', 'y+', 'z-', 'z+'
        :param dist: length of new element in the direction specified above [m]
        :return: index of created element
        """
        op_dir = dir_str[0] + self._op_sign[dir_str[1]]
        new_elem = start_elem + math.copysign(1, start_elem)
        self.hexes[new_elem] = {}
        source_points = self.vertices_to_surf[self._sur_names.index(dir_str)]
        destination_points = self.vertices_to_surf[self._sur_names.index(op_dir)]
        for d_p, s_p in zip(destination_points + source_points, source_points + source_points):
            self.hexes[new_elem][d_p] = copy.deepcopy(self.hexes[start_elem][s_p])
        for s_p in source_points:  # modif_points:
            self.hexes[new_elem][s_p][dir_str[0]] = self.hexes[new_elem][s_p][dir_str[0]] + dist
        self.hexes[new_elem]['ct'] = self.hexes[start_elem]['ct']
        return new_elem

    def _reorder_and_renumber_hexes(self):
        self.hexes = collections.OrderedDict(sorted(self.hexes.items()))
        first_hex_num = list(self.hexes.keys())[0]
        temp_dict = {}
        for h_num, h_dict in self.hexes.items():
            temp_dict[h_num - first_hex_num + 1] = h_dict
        self.hexes = temp_dict
        for h_num, h_dict in self.hexes.items():
            turn = h_dict.pop('ct', None)
            self.hexes[h_num] = collections.OrderedDict(sorted(h_dict.items()))
            self.hexes[h_num]['ct'] = turn


class Winding(Hexahedrons):

    def __init__(self, cctdm, layer, post_proc=False):

        super(Winding, self).__init__()
        self.cctdm = cctdm
        self.layer = layer
        self.post_proc = post_proc
        self.z_corr = 0
        self._populate_corners()
        self.z_corr = self._center_z_and_offset()
        self._generate_hexes()

    def _populate_corners(self):
        r"""
        Generates hexahedron with 8 corners numbered 0-7. The size of hexahedron is taken from groove size of cct as specified in yaml. The length is from number of elements per turn.
               y (v)
            3----------2
            |\     ^   |\
            | \    |   | \
            |  \   |   |  \
            |   7------+---6
            |   |  +-- |-- | -> x (u)
            0---+---\--1   |
             \  |    \  \  |
              \ |     \  \ |
               \|      z(w)\|
                4----------5

        :return: none
        """
        self._sign_of_rot = math.copysign(1, self.cctdm.geometry.windings.alphas[self.layer])
        if self._sign_of_rot > 0:
            corner_seq = {
                0: {'w_s': -1, 'h_s': -1, 'far': False},  # 'blcf'
                1: {'w_s': -1, 'h_s': 1, 'far': False},  # 'brcf'
                2: {'w_s': 1, 'h_s': 1, 'far': False},  # 'trcf'
                3: {'w_s': 1, 'h_s': -1, 'far': False},  # 'tlcf'
                4: {'w_s': -1, 'h_s': -1, 'far': True},  # bottom left corner close   #'blcc'
                5: {'w_s': -1, 'h_s': 1, 'far': True},  # bottom right corner close      #'brcc'
                6: {'w_s': 1, 'h_s': 1, 'far': True},  # top right corner close     #'trcc'
                7: {'w_s': 1, 'h_s': -1, 'far': True},  # top right corner close  #'tlcc'
            }
        else:
            corner_seq = {
                0: {'w_s': 1, 'h_s': 1, 'far': False},  # 'trcf'
                1: {'w_s': 1, 'h_s': -1, 'far': False},  # 'brcf'
                2: {'w_s': -1, 'h_s': -1, 'far': False},  # 'blcf'
                3: {'w_s': -1, 'h_s': 1, 'far': False},  # 'tlcf'
                4: {'w_s': 1, 'h_s': 1, 'far': True},  # top right corner close     #'trcc'
                5: {'w_s': 1, 'h_s': -1, 'far': True},  # bottom right corner close  #'brcc'
                6: {'w_s': -1, 'h_s': -1, 'far': True},  # bottom left corner close   #'blcc'
                7: {'w_s': -1, 'h_s': 1, 'far': True},  # top left corner close      #'tlcc'
            }
        for corner_num, corner_dict in corner_seq.items():
            self._add_corner_points(corner_num, *self.calc_turns_corner_coords(corner_dict['w_s'], corner_dict['h_s'], far=corner_dict['far']))

    def calc_turns_corner_coords(self, w_s=1, h_s=1, far=False):
        """
        Based on https://doi.org/10.1016/j.cryogenics.2020.103041
        :param h_s: wire height sign
        :param w_s: wire width sign
        :param far: for far surface set to True, for close surface set to False. This refers to walls of hexagon.
        :return:
        """
        r_wm = self.cctdm.geometry.windings.r_wms[self.layer]  # radius of winding layer, in the middle of the conductor groove [m]
        w_i = self.cctdm.geometry.windings.lps[self.layer]  # layer pitch [m]
        n_turns = self.cctdm.geometry.windings.n_turnss[self.layer]  # number of turns [-]
        nept = self.cctdm.geometry.windings.ndpts[self.layer] - 1  # number of elements per turn [-]
        alpha = self.cctdm.geometry.windings.alphas[self.layer] * np.pi / 180  # inclination of the winding [deg]
        theta_0 = 0  # offset start at theta_0, i.e. angular position of the beginning of the 1st turn[deg]
        z_0 = 0  # offset start at z_0, i.e. axial position of the beginning of the 1st turn [m]
        hh = 0.5 * h_s * self.cctdm.geometry.windings.wwhs[self.layer]  # half of h (groove height)
        hw = 0.5 * w_s * self.cctdm.geometry.windings.wwws[self.layer]  # half of w (groove width)
        tot_angle = 2 * np.pi * (n_turns + 1 / nept)
        tot_points = int(nept * n_turns) + 1
        if alpha > 0:
            theta = np.linspace(0, tot_angle, tot_points, endpoint=False)
        else:
            theta = np.linspace(0 + np.pi, tot_angle + np.pi, tot_points, endpoint=False)  # this rotates terminals for opposite inclination to be on the opposite side
        if far:
            theta = theta[1:]  # give all points but the first one, so the far surface can be created
        else:
            theta = theta[:-1]  # give all the points but the last one so a near surface can be created
        if theta.size < 2:
            raise ValueError(f'Combination of number of division points per turn (ndpts) and number of turns (n_turnss) must result in at least 2 Hexahedrons, but inputs result in only {theta.size}!')
        C = r_wm * np.arctan(alpha) * np.cos(theta - theta_0) + w_i / (2 * np.pi)
        D = np.sqrt(r_wm ** 2 + np.square(C))
        # --  x, y, z points coordinates
        xs = (r_wm + hh) * np.cos(theta) - np.sin(theta) * hw * C / D
        ys = (r_wm + hh) * np.sin(theta) + np.cos(theta) * hw * C / D
        zs = r_wm * np.sin(theta - theta_0) / np.tan(alpha) + w_i * (theta - theta_0) / (2 * np.pi) + z_0 - hw * r_wm / D  # original formula
        if alpha > 0:
            channel_turn = np.ceil((theta - 2 * np.pi / (nept + 1)) / (2 * np.pi))
            # channel_turn[0] = channel_turn[1]  # make the hex at theta 0 to belong to the first turn.
        else:
            channel_turn = np.ceil((theta - np.pi - 2 * np.pi / (nept + 1)) / (2 * np.pi))
        channel_turn[0] = channel_turn[1]  # make the hex at theta 0 to belong to the first turn.
        return xs.tolist(), ys.tolist(), zs.tolist(), list(map(int, channel_turn))

    def _center_z_and_offset(self, offset=0):
        z_mins = []
        z_maxs = []
        for c_val in self._corner_points.values():
            z_mins.append(np.min(c_val['z']))
            z_maxs.append(np.max(c_val['z']))
        z_min_wind = np.min(np.array(z_mins))
        z_max_wind = np.max(np.array(z_maxs))
        z_centre = (z_min_wind + z_max_wind) / 2
        if not self.post_proc:
            for c_key, c_val in self._corner_points.items():
                self._corner_points[c_key]['z'] = (c_val['z'] - z_centre + offset).tolist()
        z_mins = []
        z_maxs = []
        for c_val in self._corner_points.values():
            z_mins.append(np.min(c_val['z']))
            z_maxs.append(np.max(c_val['z']))
        self.z_min_winding_layer = np.min(np.array(z_mins))
        self.z_max_winding_layer = np.max(np.array(z_maxs))
        return z_centre + offset


class FQPL(Hexahedrons):
    def __init__(self, cctdm, layer):
        """
        FQPL hex generator
        :param cctdm: cct data model object parsed from yaml input file
        :param layer:   loop number, integer
        """
        super(FQPL, self).__init__()
        self.cctdm = cctdm
        self.layer = layer
        self._calc_z_unit_len()
        self._populate_corners()
        self._generate_hexes()
        self._generate_fqpl()
        self._rotate_fqpl()
        self._reorder_and_renumber_hexes()
        self._clean_attr()

    def _calc_z_unit_len(self):
        if self.cctdm.geometry.fqpls.z_starts[self.layer] == 'z_min':
            self.near = self.cctdm.geometry.air.z_min
            self.z_unit_len = (self.cctdm.geometry.fqpls.z_ends[self.layer] - self.near - self.cctdm.geometry.fqpls.fwws[self.layer]) / self.cctdm.geometry.fqpls.fndpls[self.layer]

        elif self.cctdm.geometry.fqpls.z_starts[self.layer] == 'z_max':
            self.near = self.cctdm.geometry.air.z_max
            self.z_unit_len = (self.near - self.cctdm.geometry.fqpls.z_ends[self.layer] - self.cctdm.geometry.fqpls.fwws[self.layer]) / self.cctdm.geometry.fqpls.fndpls[self.layer]
        else:
            raise ValueError(f'fqpl.z_starts parameter must be a string equal to z_min or z_max, but {self.cctdm.geometry.fqpls.z_starts[self.layer]} was given!')

        self.extrusion_sign = math.copysign(1, self.cctdm.geometry.fqpls.z_ends[self.layer] - self.near)

    def _calc_first_corner_coords(self, w_s, h_s, far, offset):
        x = [self.cctdm.geometry.fqpls.r_ins[self.layer] + self.cctdm.geometry.fqpls.fwhs[self.layer] * h_s]  # not rotated coordinate
        y = [self.cctdm.geometry.fqpls.fwws[self.layer] * w_s]  # not rotated coordinate
        if far:
            z = [self.near - self.z_unit_len + offset]
        else:
            z = [self.near + offset]
        return x, y, z, [1]

    def _populate_corners(self):
        r"""
        Generates hexahedron with 8 corners numbered 0-7. The size of hexahedron is taken from groove size of cct as specified in yaml. The length is from number of elements per turn.
               y (v)
            3----------2
            |\     ^   |\
            | \    |   | \
            |  \   |   |  \
            |   7------+---6
            |   |  +-- |-- | -> x (u)
            0---+---\--1   |
             \  |    \  \  |
              \ |     \  \ |
               \|      z(w)\|
                4----------5

        :return: none
        """
        if self.extrusion_sign > 0:
            offset = self.z_unit_len
            corner_seq = {
                0: {'w_s': -0.5, 'h_s': 0, 'far': True},  # 'blcf'
                1: {'w_s': -0.5, 'h_s': 1, 'far': True},  # 'tlcf'
                2: {'w_s': 0.5, 'h_s': 1, 'far': True},  # 'trcf'
                3: {'w_s': 0.5, 'h_s': 0, 'far': True},  # 'brcf'
                4: {'w_s': -0.5, 'h_s': 0, 'far': False},  # bottom left corner close   #'blcc'
                5: {'w_s': -0.5, 'h_s': 1, 'far': False},  # top left corner close      #'tlcc'
                6: {'w_s': 0.5, 'h_s': 1, 'far': False},  # top right corner close     #'trcc'
                7: {'w_s': 0.5, 'h_s': 0, 'far': False},  # bottom right corner close  #'brcc'
            }
        else:
            offset = 0
            corner_seq = {
                0: {'w_s': -0.5, 'h_s': 0, 'far': False},  # 'blcf'
                1: {'w_s': -0.5, 'h_s': 1, 'far': False},  # 'tlcf'
                2: {'w_s': 0.5, 'h_s': 1, 'far': False},  # 'trcf'
                3: {'w_s': 0.5, 'h_s': 0, 'far': False},  # 'brcf'
                4: {'w_s': -0.5, 'h_s': 0, 'far': True},  # bottom left corner close   #'blcc'
                5: {'w_s': -0.5, 'h_s': 1, 'far': True},  # top left corner close      #'tlcc'
                6: {'w_s': 0.5, 'h_s': 1, 'far': True},  # top right corner close     #'trcc'
                7: {'w_s': 0.5, 'h_s': 0, 'far': True},  # bottom right corner close  #'brcc'
            }
        for corner_num, corner_dict in corner_seq.items():
            self._add_corner_points(corner_num, *self._calc_first_corner_coords(corner_dict['w_s'], corner_dict['h_s'], corner_dict['far'], offset))

    def _get_ref_point(self, elem_number, surf_n_dir_str, coord, dist):
        """
        Gets center point for a surface 'pointing' in the direction surf_n_dir_str of hex with elem_number. It then moves that point into along coordinate coord and by distance dist
        :param elem_number: hex number to take the surface from
        :param surf_n_dir_str: 'direction of surface' (kind of normal), options are: 'x-', 'x+', 'y-', 'y+', 'z-', 'z+'
        :param coord: direction to more the point in, options are: 'x', 'y', 'z'
        :param dist: distance to move the point, this is positive or negative float
        :return:
        """
        source_points = self.vertices_to_surf[self._sur_names.index(surf_n_dir_str)]  # get the indexes 4 points for the surface points in direction surf_n_dir_str
        points_coor = [self.hexes[elem_number][point] for point in source_points]  # get the points, they contain coordinates
        xs = []
        ys = []
        zs = []
        for point in points_coor:  # get coordinates into list for each axis
            for cor_list, coor in zip([xs, ys, zs], ['x', 'y', 'z']):
                cor_list.append(point[coor])
        p = {'x': np.mean(xs), 'y': np.mean(ys), 'z': np.mean(zs)}  # get averages of each axis coordinate, giving the center of the surface
        p[coord] = p[coord] + dist
        return p

    def _add_elem_with_rot(self, elem_number, surf_n_dir_str, add_ax, angle, ref_p_coor):
        """
        :param elem_number: idx of start element
        :param surf_n_dir_str: direction of adding element, options are: 'x-', 'x+', 'y-', 'y+', 'z-', 'z+'
        :param ref_p_coor: length of new element in the direction specified above [m]
        :return: index of created element
        """
        mod_coor = [surf_n_dir_str[0], add_ax]
        # mod_coor.remove(surf_n_dir_str[0])  # get the other two coordinates that arenet the direction of the surface to take

        angle_rad = np.deg2rad(angle)
        op_dir = surf_n_dir_str[0] + self._op_sign[surf_n_dir_str[1]]
        new_elem = elem_number + math.copysign(1, elem_number)
        self.hexes[new_elem] = {}
        source_points = self.vertices_to_surf[self._sur_names.index(surf_n_dir_str)]
        destination_points = self.vertices_to_surf[self._sur_names.index(op_dir)]
        for d_p, s_p in zip(destination_points + source_points, source_points + source_points):
            self.hexes[new_elem][d_p] = copy.deepcopy(self.hexes[elem_number][s_p])
        for s_p in source_points:  # modif_points:
            v1 = self.hexes[new_elem][s_p][mod_coor[0]]
            v2 = self.hexes[new_elem][s_p][mod_coor[1]]
            v1_ofset = ref_p_coor[mod_coor[0]]
            v2_ofset = ref_p_coor[mod_coor[1]]
            v1 = v1 - v1_ofset
            v2 = v2 - v2_ofset
            v1_new = np.cos(angle_rad) * v1 - np.sin(angle_rad) * v2
            v2_new = np.sin(angle_rad) * v1 + np.cos(angle_rad) * v2
            v1 = v1_new + v1_ofset
            v2 = v2_new + v2_ofset
            self.hexes[new_elem][s_p][mod_coor[0]] = v1
            self.hexes[new_elem][s_p][mod_coor[1]] = v2
        self.hexes[new_elem]['ct'] = self.hexes[elem_number]['ct']
        return new_elem

    def _generate_fqpl(self):
        new_elem = self._add_elem_to_elem(0, 'z+', self.extrusion_sign * self.z_unit_len)
        for _ in range(self.cctdm.geometry.fqpls.fndpls[self.layer] - 2):
            new_elem = self._add_elem_to_elem(new_elem, 'z+', self.extrusion_sign * self.z_unit_len)
        coord = 'x'
        ref_point = self._get_ref_point(new_elem, 'z+', coord, self.cctdm.geometry.fqpls.r_bs[self.layer])  # centre of rotation pint.
        n_seg = 10
        angle = 180 / n_seg
        for _ in range(n_seg):
            new_elem = self._add_elem_with_rot(new_elem, 'z+', coord, self.extrusion_sign * angle, ref_point)
        for _ in range(self.cctdm.geometry.fqpls.fndpls[self.layer]):
            new_elem = self._add_elem_to_elem(new_elem, 'z+', -self.extrusion_sign * self.z_unit_len)

    def _rotate_fqpl(self):
        for h_num, h_dict in self.hexes.items():
            channel_turn = h_dict.pop('ct', None)
            for p_num, p_dict in h_dict.items():
                xx = p_dict['x']
                yy = p_dict['y']
                x = xx * np.cos(np.deg2rad(self.cctdm.geometry.fqpls.thetas[self.layer])) - yy * np.sin(np.deg2rad(self.cctdm.geometry.fqpls.thetas[self.layer]))  # rotated coordinate
                y = xx * np.sin(np.deg2rad(self.cctdm.geometry.fqpls.thetas[self.layer])) + yy * np.cos(np.deg2rad(self.cctdm.geometry.fqpls.thetas[self.layer]))  # rotated coordinate
                self.hexes[h_num][p_num]['x'] = x
                self.hexes[h_num][p_num]['y'] = y
            self.hexes[h_num]['ct'] = channel_turn

    def _clean_attr(self):
        del self.cctdm
        del self.layer
        del self.near
        del self.z_unit_len


class Generate_BREPs:
    def __init__(self, fdm, verbose=True):
        """
        Class to generate (build) Windings and Formers (WF) of a canted cosine theta (CCT) magnet and save them to brep files
        :param fdm: fiqus data model
        :param verbose: If True more information is printed in python console.
        """
        self.cctdm = fdm.magnet
        self.model_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name

        self.verbose = verbose
        self.cctwi = WindingsInformation()
        self.cctwi.magnet_name = self.magnet_name
        self.transl_dict = {'vol': '', 'surf': '_bd', 'surf_in': '_in', 'surf_out': '_out', 'cochain': '_cut'}
        self.gu = GmshUtils(self.model_folder, self.verbose)
        self.gu.initialize()
        self.formers = []
        self.air = []
        gmsh.option.setString('Geometry.OCCTargetUnit', 'M')

    def generate_windings_or_fqpls(self, type_str):
        """
        Generates windings brep files, as many as number of entries in the yaml file for windings.
        :param type_str: What to generate, options are: 'windings' or 'fqpls'
        :return: None, saves brep to disk
        """
        if self.verbose:
            print(f'Generating {type_str} started')
            start_time = timeit.default_timer()

        def generate_geom(worf_in, names_in):
            worf_tags_dict_in = {}
            for worf_num, worf_in in enumerate(worf_in):
                worf_tags_dict_in[worf_num] = self.generate_hex_geom(worf_in)
                gmsh.model.occ.synchronize()
                gmsh.write(os.path.join(self.model_folder, f'{names_in[worf_num]}.brep'))
                gmsh.clear()
            return worf_tags_dict_in

        if self.cctdm.geometry.windings.names and type_str == 'windings':
            worf = [Winding(self.cctdm, i) for i, _ in enumerate(self.cctdm.geometry.windings.names)]        # worf = winding or fqpl
            names = [name for name in self.cctdm.geometry.windings.names]
            for w in worf:
                if self.cctdm.geometry.air.z_min > w.z_min_winding_layer or w.z_max_winding_layer > self.cctdm.geometry.air.z_max:
                    raise ValueError(f'{self.cctdm.geometry.air.name} region dimensions are too s mall to fit the windings turns. Please extend z_min and/or z_max')
                else:
                    pass
            worf_tags_dict = generate_geom(worf, names)

        if self.cctdm.geometry.fqpls.names and type_str == 'fqpls':
            worf = [FQPL(self.cctdm, i) for i, _ in enumerate(self.cctdm.geometry.fqpls.names)]  # worf = winding or fqpl
            names = [name for name in self.cctdm.geometry.fqpls.names]
            worf_tags_dict = generate_geom(worf, names)

        w_z_maxs = []
        w_z_mins = []
        if type_str == 'windings':
            for winding in worf:
                w_z_maxs.append(winding.z_max_winding_layer)
                w_z_mins.append(winding.z_min_winding_layer)
            self.cctwi.windings_avg_length = float(np.mean(w_z_maxs) - np.mean(w_z_mins))
            self.cctwi.windings.names = names
            self.cctwi.windings.t_in.vol_st = []
            self.cctwi.windings.t_in.surf_st = []
            self.cctwi.windings.t_out.vol_st = []
            self.cctwi.windings.t_out.surf_st = []
            self.cctwi.windings.t_in.vol_et = []
            self.cctwi.windings.t_in.surf_et = []
            self.cctwi.windings.t_out.vol_et = []
            self.cctwi.windings.t_out.surf_et = []
            self.cctwi.windings.t_in.lc_et = []
            self.cctwi.windings.t_out.lc_et = []
            self.cctwi.windings.t_in.ndpterms = self.cctdm.geometry.windings.ndpt_ins
            self.cctwi.windings.t_out.ndpterms = self.cctdm.geometry.windings.ndpt_outs
            self.cctwi.windings.t_in.z_air = self.cctdm.geometry.air.z_min
            self.cctwi.windings.t_out.z_air = self.cctdm.geometry.air.z_max
            for winding_num, winding_dict in worf_tags_dict.items():
                first_vol = list(winding_dict.keys())[0]
                last_vol = list(winding_dict.keys())[-1]
                self.cctwi.windings.t_in.vol_st.append(winding_dict[first_vol]['v_t'])
                self.cctwi.windings.t_in.surf_st.append(winding_dict[first_vol]['sf_ts'][0])
                self.cctwi.windings.t_out.vol_st.append(winding_dict[last_vol]['v_t'])
                self.cctwi.windings.t_out.surf_st.append(winding_dict[last_vol]['sf_ts'][2])
                self.cctwi.windings.t_in.vol_et.append(winding_dict[first_vol]['v_t'])
                self.cctwi.windings.t_in.surf_et.append(winding_dict[first_vol]['sf_ts'][0])
                self.cctwi.windings.t_out.vol_et.append(winding_dict[last_vol]['v_t'])
                self.cctwi.windings.t_out.surf_et.append(winding_dict[last_vol]['sf_ts'][2])

            lc_st_neg_alpha = [[1, 0], [0, 3], [3, 2], [2, 1], [6, 4], [4, 5], [5, 7], [7, 6], [1, 6], [0, 4], [3, 5], [2, 7]]
            lc_st_pos_alpha = [[3, 1], [1, 0], [0, 2], [2, 3], [7, 4], [4, 5], [5, 6], [6, 7], [3, 7], [1, 4], [0, 5], [2, 6]]
            lc_et_neg_alpha = [[5, 7], [7, 6], [6, 4], [4, 5], [1, 3], [3, 2], [2, 0], [0, 1], [5, 1], [7, 3], [6, 2], [4, 0]]
            lc_et_pos_alpha = [[5, 7], [7, 6], [6, 4], [4, 5], [1, 3], [3, 2], [2, 0], [0, 1], [5, 1], [7, 3], [6, 2], [4, 0]]
            # [[1, 2], [2, 3], [3, 4], [4, 1], [5, 6], [6, 7], [7, 8], [8, 5], [1, 5], [2, 6], [3, 7], [4, 8]]
            # [[2, 1], [1, 4], [4, 3], [3, 2], [6, 5], [5, 8], [8, 7], [7, 6], [2, 6], [1, 5], [4, 8], [3, 7]]

            lc_et_pos_corr = [[1, 0], [0, 3], [3, 2], [2, 1], [5, 4], [4, 7], [7, 6], [6, 5], [1, 5], [0, 4], [3, 7], [2, 6]]

            self.cctwi.windings.t_in.lc_st = []
            self.cctwi.windings.t_out.lc_st = []
            for alpha in self.cctdm.geometry.windings.alphas:
                if alpha > 0:
                    self.cctwi.windings.t_in.lc_st.append(lc_st_pos_alpha)
                    self.cctwi.windings.t_out.lc_st.append(lc_st_pos_alpha)
                    self.cctwi.windings.t_in.lc_et.append(lc_et_pos_corr)
                    self.cctwi.windings.t_out.lc_et.append(lc_et_pos_alpha)
                else:
                    self.cctwi.windings.t_in.lc_st.append(lc_st_neg_alpha)
                    self.cctwi.windings.t_out.lc_st.append(lc_st_neg_alpha)
                    self.cctwi.windings.t_in.lc_et.append(lc_et_neg_alpha)
                    self.cctwi.windings.t_out.lc_et.append(lc_et_pos_corr)

        if self.verbose:
            print(f'Generating {type_str} took {timeit.default_timer() - start_time:.2f} s')

    def save_volume_info(self):
        if self.cctdm.geometry.fqpls.names:
            fqpls = self.cctdm.geometry.fqpls.names
        else:
            fqpls = []

        self.cctwi.w_names = self.cctdm.geometry.windings.names
        self.cctwi.f_names = fqpls
        self.cctwi.formers = self.cctdm.geometry.formers.names
        self.cctwi.air = self.cctdm.geometry.air.name

        volume_info_file = os.path.join(self.model_folder, f'{self.cctwi.magnet_name}.wi')
        uff.write_data_to_yaml(volume_info_file, self.cctwi.model_dump())

    def generate_formers(self):
        if self.cctdm.geometry.formers.r_ins:
            if self.verbose:
                print('Generating Formers Started')
                start_time = timeit.default_timer()

            for f_i, _ in enumerate(self.cctdm.geometry.formers.r_ins):
                z = self.cctdm.geometry.formers.z_mins[f_i]
                dz = self.cctdm.geometry.formers.z_maxs[f_i] - self.cctdm.geometry.formers.z_mins[f_i]
                cylin_out = (3, gmsh.model.occ.addCylinder(0, 0, z, 0, 0, dz, self.cctdm.geometry.formers.r_outs[f_i], angle=2 * math.pi))  # add cylinder to align to existing bodies in the pro file
                cylin_in = (3, gmsh.model.occ.addCylinder(0, 0, z, 0, 0, dz, self.cctdm.geometry.formers.r_ins[f_i], angle=2 * math.pi))  # add another cylinder to subtract from the first one to make a tube
                cylinder = gmsh.model.occ.cut([cylin_out], [cylin_in], removeObject=True)  # subtract cylinders to make a tube
                self.formers.append(cylinder[0][0])  # keep just the tag and append
                gmsh.model.occ.synchronize()
                gmsh.write(os.path.join(self.model_folder, f'{self.cctdm.geometry.formers.names[f_i]}.brep'))
                gmsh.clear()
            if self.verbose:
                print(f'Generating formers took {timeit.default_timer() - start_time:.2f} s')

    def generate_air(self):
        if self.cctdm.geometry.air.ar:
            if self.verbose:
                print('Generating air started')
                start_time = timeit.default_timer()
            if self.cctdm.geometry.air.sh_type == 'cylinder':
                self.air = [(3, gmsh.model.occ.addCylinder(0, 0, self.cctdm.geometry.air.z_min, 0, 0, self.cctdm.geometry.air.z_max - self.cctdm.geometry.air.z_min, self.cctdm.geometry.air.ar, angle=2 * math.pi))]
            elif self.cctdm.geometry.air.sh_type == 'cuboid':
                air_box_size = [-self.cctdm.geometry.air.ar / 2, -self.cctdm.geometry.air.ar / 2, self.cctdm.geometry.air.z_min, self.cctdm.geometry.air.ar, self.cctdm.geometry.air.ar,
                                self.cctdm.geometry.air.z_max - self.cctdm.geometry.air.z_min]  # list of box size with: x, y, z, dx, dy, dz
                self.air = [(3, gmsh.model.occ.addBox(*air_box_size))]
            else:
                raise ValueError(f'Shape type: {self.cctdm.geometry.air.sh_type} is not supported!')
            gmsh.model.occ.synchronize()
            gmsh.write(os.path.join(self.model_folder, f'{self.cctdm.geometry.air.name}.brep'))
            gmsh.clear()
            if self.verbose:
                print(f'Generating air took {timeit.default_timer() - start_time:.2f} s')

    def generate_regions_file(self):
        if self.verbose:
            print('Generating Regions File Started')
            start_time = timeit.default_timer()
        cctrm = Reg_Mod_FiQ.RegionsModel()
        vrt = 1000000  # volume region tag start
        srt = 2000000  # surface region tag start
        lrt = 3000000  # line region tag start
        # -------- powered ----------
        # volumes
        cctrm.powered['cct'] = Reg_Mod_FiQ.Powered()
        cctrm.powered['cct'].vol.names = [name + self.transl_dict['vol'] for name in self.cctdm.geometry.windings.names + self.cctdm.geometry.fqpls.names]
        cctrm.powered['cct'].vol.currents = self.cctdm.solve.windings.currents + self.cctdm.solve.fqpls.currents
        cctrm.powered['cct'].vol.sigmas = self.cctdm.solve.windings.sigmas + self.cctdm.solve.fqpls.sigmas
        cctrm.powered['cct'].vol.mu_rs = self.cctdm.solve.windings.mu_rs + self.cctdm.solve.fqpls.mu_rs
        reg = []
        for _ in self.cctdm.geometry.windings.names + self.cctdm.geometry.fqpls.names:
            reg.append(vrt)
            vrt += 1
        cctrm.powered['cct'].vol.numbers = reg
        # surfaces
        cctrm.powered['cct'].surf_in.names = [name + self.transl_dict['surf_in'] for name in self.cctdm.geometry.windings.names + self.cctdm.geometry.fqpls.names]
        cctrm.powered['cct'].surf_out.names = [name + self.transl_dict['surf_out'] for name in self.cctdm.geometry.windings.names + self.cctdm.geometry.fqpls.names]
        reg = []
        for _ in self.cctdm.geometry.windings.names + self.cctdm.geometry.fqpls.names:
            reg.append(srt)
            srt += 1
        cctrm.powered['cct'].surf_in.numbers = reg
        reg = []
        for _ in self.cctdm.geometry.windings.names + self.cctdm.geometry.fqpls.names:
            reg.append(srt)
            srt += 1
        cctrm.powered['cct'].surf_out.numbers = reg

        # -------- induced ----------
        # volumes
        cctrm.induced['cct'] = Reg_Mod_FiQ.Induced()
        cctrm.induced['cct'].vol.names = [name + self.transl_dict['vol'] for name in self.cctdm.geometry.formers.names]
        cctrm.induced['cct'].vol.sigmas = self.cctdm.solve.formers.sigmas
        cctrm.induced['cct'].vol.mu_rs = self.cctdm.solve.formers.mu_rs
        reg = []
        for _ in self.cctdm.geometry.formers.names:
            reg.append(vrt)
            vrt += 1
        cctrm.induced['cct'].vol.numbers = reg

        # -------- air ----------
        # volumes
        cctrm.air.vol.name = self.cctdm.geometry.air.name + self.transl_dict['vol']
        cctrm.air.vol.sigma = self.cctdm.solve.air.sigma
        cctrm.air.vol.mu_r = self.cctdm.solve.air.mu_r
        cctrm.air.vol.number = vrt
        vrt += 1

        # surface
        cctrm.air.surf.name = self.cctdm.geometry.air.name + self.transl_dict['surf']
        cctrm.air.surf.number = srt
        srt += 1

        # # center line
        # cctrm.air.line.name = 'Center_line'
        # cctrm.air.line.number = lrt
        # lrt += 1
        lrt = srt

        # --------- cuts -------
        # these need to be done at the end with the highest surface tags
        cctrm.powered['cct'].cochain.names = [name + self.transl_dict['cochain'] for name in self.cctdm.geometry.windings.names + self.cctdm.geometry.fqpls.names]
        reg = []
        for _ in self.cctdm.geometry.windings.names + self.cctdm.geometry.fqpls.names:
            reg.append(lrt)
            lrt += 1
        cctrm.powered['cct'].cochain.numbers = reg
        # induced cuts
        cctrm.induced['cct'].cochain.names = [name + self.transl_dict['cochain'] for name in self.cctdm.geometry.formers.names]
        reg = []
        for _ in self.cctdm.geometry.formers.names:
            reg.append(lrt)
            lrt += 1
        cctrm.induced['cct'].cochain.numbers = reg

        uff.write_data_to_yaml(os.path.join(self.model_folder, f'{self.cctwi.magnet_name}.regions'), cctrm.model_dump())

        if self.verbose:
            print(f'Generating Regions File Took {timeit.default_timer() - start_time:.2f} s')

    @staticmethod
    def generate_hex_geom(hexes_dict,
                          cons_for_lines=[[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]],
                          vol_tag=-1):
        """
        Generates hexahedra volumes from data in hexes dict
        :param hexes_dict: dictionary of data generated by either Winding or FQPL class in Hexahedrons.py
        :param cons_for_lines: line connection defined as list of list in terms of point numbers to connect in the hexahedron
        :param vol_tag: volume tag to use for generated volume of hexahedron
        :return: dictionary with tags of created volumes, surface loops, surface fillings, closed loops, lines, points and channel turn (i.e. turn number of CCT winding).
        """
        tags_dict = {}
        for h_num, h_dict in hexes_dict.hexes.items():
            p_ts = []  # Point tags
            channel_turn = h_dict.pop('ct', None)
            for p_num, p_dict in h_dict.items():
                p_ts.append(gmsh.model.occ.addPoint(p_dict['x'], p_dict['y'], p_dict['z']))

            l_ts = []   # Line tags
            for p_c in cons_for_lines:  # point connections to make a line
                l_ts.append(gmsh.model.occ.addLine(p_ts[p_c[0]], p_ts[p_c[1]]))

            cl_ts = []  # Curved Loops tags
            for l_c in [[0, 1, 2, 3], [4, 5, 6, 7], [3, 8, 7, 11], [1, 9, 5, 10], [0, 8, 4, 9], [2, 11, 6, 10]]:  # line connections to make a curved loop
                cl_ts.append(gmsh.model.occ.addCurveLoop([l_ts[l_c[0]], l_ts[l_c[1]], l_ts[l_c[2]], l_ts[l_c[3]]]))
            sf_ts = []  # Surface Filling tags
            for cl_t in cl_ts:
                sf_ts.append(gmsh.model.occ.addSurfaceFilling(cl_t, degree=3, tol2d=0.000001, tol3d=0.00001, tolAng=0.001, tolCurv=0.05))
            sl_t = gmsh.model.occ.addSurfaceLoop(sf_ts, sewing=True)
            v_t = gmsh.model.occ.addVolume([sl_t], vol_tag)
            tags_dict[int(h_num)] = {'v_t': v_t, 'sl_t': sl_t, 'sf_ts': sf_ts, 'cl_ts': cl_ts, 'l_ts': l_ts, 'p_ts': p_ts, 'ct': channel_turn}
        return tags_dict


class Prepare_BREPs:
    def __init__(self, fdm, verbose=True) -> object:
        """
        Class to preparing brep files by adding terminals.
        :param fdm: FiQuS data model
        :param verbose: If True more information is printed in python console.
        """

        self.cctdm = fdm.magnet
        self.model_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name

        self.verbose = verbose
        self.winding_info_file = os.path.join(self.model_folder, f'{self.magnet_name}.wi')
        self.cctwi = uff.read_data_from_yaml(self.winding_info_file, WindingsInformation)
        self.gu = GmshUtils(self.model_folder, self.verbose)
        self.gu.initialize()
        self.model_file = os.path.join(self.model_folder, f'{self.magnet_name}.brep')

    @staticmethod
    def get_pts_for_sts(surface_tags):
        """
        Get point tags for surface tags
        :param surface_tags: list of surface tags to get point tags
        :return: list of point tags belonging to the surfaces in the list
        """
        vol_line_tags = []
        vol_line_tags_i = 0
        vol_line_tags_idx = []
        for surf_tag in surface_tags:
            line_tags_new = gmsh.model.getAdjacencies(2, surf_tag)[1]
            for line_tag in line_tags_new:
                vol_line_tags_i += 1
                if line_tag not in vol_line_tags:
                    vol_line_tags.append(line_tag)
                    vol_line_tags_idx.append(vol_line_tags_i)
        point_tags = []
        point_tags_i = 0
        point_tags_idx = []
        for line_tag in vol_line_tags:
            point_tags_new = gmsh.model.getAdjacencies(1, line_tag)[1]
            for point_tag in point_tags_new:
                point_tags_i += 1
                if point_tag not in point_tags:
                    point_tags.append(point_tag)
                    point_tags_idx.append(point_tags_i)
        return point_tags, vol_line_tags_idx, point_tags_idx

    def straighten_terminal(self, gui=False):
        """
        Extends winding geom_generators to the air region boundary by extending the geom_generators with 'terminals' geom_generators up to the air boundary surfaces
        By default this extends along the z axis and makes the final surface normal to the z axis.
        :return: None, saves breps with straighten terminals to disk
        """

        for i, name in enumerate(self.cctwi.windings.names):
            if self.verbose:
                print(f'Straightening terminals of {name} started')
                start_time = timeit.default_timer()
            gmsh.open(os.path.join(self.model_folder, f'{name}.brep'))
            for terminal in [self.cctwi.windings.t_in, self.cctwi.windings.t_out]:
                vol_tag = terminal.vol_st[i]
                vol_surf_tags = gmsh.model.getAdjacencies(3, vol_tag)[1]
                surf_tag = terminal.surf_st[i]
                if surf_tag not in vol_surf_tags:
                    raise ValueError(f'Surface tag of {surf_tag} given for volume in of {vol_tag} does not belong to the volume!')
                # surf_point_tags = self.get_pts_for_sts([surf_tag])      # only 'powered' surface
                surf_point_tags, surf_line_tags_idx, surf_point_tags_idx = self.get_pts_for_sts([surf_tag])  # only 'powered' surface
                vol_point_tags, vol_line_tags_idx, vol_point_tags_idx = self.get_pts_for_sts(vol_surf_tags)  # all tags of hex
                vol_point_dict = {}
                for p_tag in vol_point_tags:
                    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(0, p_tag)
                    vol_point_dict[p_tag] = {'x': (xmin + xmax) / 2, 'y': (ymin + ymax) / 2, 'z': (zmin + zmax) / 2}
                z = []
                y = []
                x = []
                for p_tag in surf_point_tags:  # calculate average z position for the terminal surface
                    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(0, p_tag)
                    x.append((xmin + xmax) / 2)
                    y.append((ymin + ymax) / 2)
                    z.append((zmin + zmax) / 2)
                x_avg = np.mean(x)
                y_avg = np.mean(y)
                z_avg = np.mean(z)
                sign_x = [math.copysign(1, x_i - x_avg) for x_i in x]
                sign_y = [math.copysign(1, y_i - y_avg) for y_i in y]
                dist_x = []
                dist_y = []
                for j in range(len(x) - 1):
                    dist_x.append(math.sqrt((x[j] - x[j + 1]) ** 2))
                    dist_y.append(math.sqrt((y[j] - y[j + 1]) ** 2))
                eq_len = self.cctdm.geometry.windings.wwhs[i] / 2
                y_shift_sign = math.copysign(1, -terminal.z_air * self.cctdm.geometry.windings.alphas[i])
                new_x = [x_avg + s_x * eq_len for s_x in sign_x]
                new_y = [y_avg + s_y * eq_len + y_shift_sign * eq_len - y_shift_sign * dist_y[0] / 2 for s_y in sign_y]
                for p_tag, x_n, y_n in zip(surf_point_tags, new_x, new_y):  # assign z_avg to only points on the terminal surface
                    vol_point_dict[p_tag]['x'] = x_n
                    vol_point_dict[p_tag]['y'] = y_n
                    vol_point_dict[p_tag]['z'] = z_avg
                gmsh.model.occ.remove([(3, terminal.vol_st[i])], recursive=True)
                gmsh.model.occ.synchronize()
                hexes = Hexahedrons()  # create hex class instance to be able to reuse existing code for generating hexes geom_generators
                hexes.hexes[0] = {}  # only one winding layer is involved per iteration, so hardcoded 0 index
                for p_i, (_, p_dict) in enumerate(vol_point_dict.items()):
                    hexes.hexes[0][p_i] = p_dict
                Generate_BREPs.generate_hex_geom(hexes, cons_for_lines=terminal.lc_st[i], vol_tag=terminal.vol_st[i])
                gmsh.model.occ.synchronize()
            gmsh.write(os.path.join(self.model_folder, f'{name}.brep'))
            if self.verbose:
                print(f'Straightening terminals of {name} took {timeit.default_timer() - start_time:.2f} s')
        if gui:
            gmsh.model.occ.synchronize()
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()

    def extend_terms(self, operation='extend', gui=False, ):
        self.cctwi = uff.read_data_from_yaml(self.winding_info_file, WindingsInformation)  # this is repeated as the operation over the data for the case add, so an original data for extend operation needs to be loaded.
        if operation == 'add':
            for terminal in [self.cctwi.windings.t_in, self.cctwi.windings.t_out]:
                terminal.ndpterms = [1] * len(terminal.ndpterms)
                terminal.z_air = terminal.z_add
        elif operation == 'extend':
            pass
        file_in_postfix = ''
        file_out_postfix = ''
        for i, name in enumerate(self.cctwi.windings.names):
            if self.verbose:
                print(f'Extending terminals of {name} started')
                start_time = timeit.default_timer()
            gmsh.open(os.path.join(self.model_folder, f'{name}{file_in_postfix}.brep'))
            volumes = [vol[1] for vol in gmsh.model.getEntities(dim=3)]
            for oper, terminal in enumerate([self.cctwi.windings.t_in, self.cctwi.windings.t_out]):
                vol_tag = terminal.vol_et[i]
                vol_surf_tags = gmsh.model.getAdjacencies(3, vol_tag)[1]
                surf_tag = terminal.surf_et[i]
                if surf_tag not in vol_surf_tags:
                    raise ValueError(f'Surface tag of {surf_tag} given for volume in of {vol_tag} does not belong to the volume!')
                surf_point_tags, surf_line_tags_idx, surf_point_tags_idx = self.get_pts_for_sts([surf_tag])
                surf_point_tags = sorted(surf_point_tags)
                vol_point_tags, vol_line_tags_idx, vol_point_tags_idx = self.get_pts_for_sts(vol_surf_tags)
                vol_point_tags = sorted(vol_point_tags)
                surf_point_tags_idx_pw = [i for i, e in enumerate(vol_point_tags) if e in set(surf_point_tags)]  # powered
                surf_point_tags_idx_oth = [i for i, e in enumerate(vol_point_tags) if e not in set(surf_point_tags)]  # other (opposite powered)
                vol_point_dict = {}
                for idx_pw, p_tag in zip(surf_point_tags_idx_pw, surf_point_tags):
                    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(0, p_tag)
                    vol_point_dict[idx_pw] = {'x': (xmin + xmax) / 2, 'y': (ymin + ymax) / 2, 'z': (zmin + zmax) / 2}
                z_ext = round((terminal.z_air - zmin) / terminal.ndpterms[i], 8)
                for idx_oth, p_tag in zip(surf_point_tags_idx_oth, surf_point_tags):
                    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(0, p_tag)
                    vol_point_dict[idx_oth] = {'x': (xmin + xmax) / 2, 'y': (ymin + ymax) / 2, 'z': (zmin + zmax) / 2 + z_ext}
                hexes = Hexahedrons()  # create hex class instance to be able to reuse existing code for generating hexes geom_generators
                for h in range(terminal.ndpterms[i]):
                    hexes.hexes[h] = {}
                    for p_i, (_, p_dict) in enumerate(vol_point_dict.items()):
                        hexes.hexes[h][p_i] = copy.deepcopy(p_dict)
                    for p_t, p_dict in vol_point_dict.items():
                        p_dict['z'] = p_dict['z'] + z_ext
                for idx_oth in range(4, 8):
                    z_air = terminal.z_air
                    hexes.hexes[h][idx_oth]['z'] = z_air
                tags_dict = Generate_BREPs.generate_hex_geom(hexes, cons_for_lines=terminal.lc_et[i], vol_tag=-1)
                new_volumes = []
                for _, hex_dict in tags_dict.items():
                    new_volumes.append(hex_dict['v_t'])
                gmsh.model.occ.synchronize()
                if oper == 0:  # this vol_in is needed for reordering volumes later
                    vol_in = new_volumes
            renumbered_vols = []
            other_vols = list(set(volumes) - set(vol_in))
            max_tag = gmsh.model.occ.getMaxTag(3)
            for vol in other_vols:
                gmsh.model.setTag(3, vol, vol + max_tag)
                renumbered_vols.append(vol + max_tag)
            for n_tag, vol in enumerate(reversed(vol_in)):
                gmsh.model.setTag(3, vol, n_tag + 1)
            max_term_tag = len(vol_in) + 1
            spiral_volumes = []
            for n_tag, vol in enumerate(renumbered_vols):
                gmsh.model.setTag(3, vol, n_tag + max_term_tag)
                spiral_volumes.append(n_tag + max_term_tag)
            gmsh.write(os.path.join(self.model_folder, f'{name}{file_out_postfix}.brep'))
            if self.verbose:
                print(f'Straightening terminals of {name} took {timeit.default_timer() - start_time:.2f} s')
                print(f'Writing volume information file: {name}.vi ')
            vi = {'export': spiral_volumes, 'all': [vol[1] for vol in gmsh.model.getEntities(dim=3)]}
            json.dump(vi, open(f"{os.path.join(self.model_folder, name)}.vi", 'w'))
            if self.verbose:
                print(f'Done writing volume information file: {name}.vi ')
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()

    def save_fqpl_vi(self):
        for f_name in self.cctdm.geometry.fqpls.names:
            if self.verbose:
                print(f'Writing volume information file: {f_name}.vi ')
            gmsh.open(os.path.join(self.model_folder, f'{f_name}.brep'))
            volumes = [vol[1] for vol in gmsh.model.getEntities(dim=3)]
            export = volumes
            vi = {'export': export, 'all': volumes}
            json.dump(vi, open(f"{os.path.join(self.model_folder, f_name)}.vi", 'w'))
            if self.verbose:
                print(f'Done writing volume information file: {f_name}.vi ')
        gmsh.clear()

    def fragment(self, gui=False):
        if self.verbose:
            print('Loading files in preparation for fragment operation')
        for f_name in self.cctwi.w_names + self.cctwi.f_names:
            gmsh.merge(os.path.join(self.model_folder, f'{f_name}.brep'))
        num_vol = np.max([vol[1] for vol in gmsh.model.getEntities(dim=3)])
        for f_name in self.cctwi.formers:
            gmsh.merge(os.path.join(self.model_folder, f'{f_name}.brep'))
            num_vol += 1
        gmsh.merge(os.path.join(self.model_folder, f'{self.cctwi.air}.brep'))
        num_vol += 1
        entities = gmsh.model.getEntities(dim=3)
        if len(entities) != num_vol:
            raise ValueError('Not consistent volumes numbers in brep and json files!')
        objectDimTags = [entities[-1]]
        toolDimTags = entities[:-1]
        # central_line = [(1, 3898)]
        # toolDimTags = toolDimTags+central_line
        if self.verbose:
            print(f'Fragmenting {self.magnet_name} started')
            start_time = timeit.default_timer()
        gmsh.model.occ.fragment(objectDimTags, toolDimTags, removeObject=True, removeTool=True)
        gmsh.model.occ.synchronize()
        if self.verbose:
            print(f'Fragmenting {self.magnet_name} took {timeit.default_timer() - start_time:.2f} s')

        gmsh.write(self.model_file)
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()

    def load_geometry(self, gui=False):
        gmsh.open(self.model_file)
        if gui:
            self.gu.launch_interactive_GUI()
