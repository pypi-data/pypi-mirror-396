import os
import math
import csv

import gmsh
import json
import numpy as np
import pandas as pd
from pathlib import Path

from fiqus.geom_generators.GeometryCCT import Winding, FQPL
from fiqus.data.DataWindingsCCT import WindingsInformation
from fiqus.parsers.ParserDAT import ParserDAT
from fiqus.utils.Utils import GmshUtils, FilesAndFolders


class Post_Process:
    def __init__(self, fdm, verbose=True):
        """
        Class to cct models postprocessing
        :param fdm: FiQuS data model
        :param verbose: If True more information is printed in python console.
        """
        self.cctdm = fdm.magnet
        self.model_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name

        self.verbose = verbose
        self.gu = GmshUtils(self.model_folder, self.verbose)
        self.gu.initialize()
        self.masks_fqpls = {}
        self.pos_names = []
        for variable, volume, file_ext in zip(self.cctdm.postproc.variables, self.cctdm.postproc.volumes, self.cctdm.postproc.file_exts):
            self.pos_names.append(f'{variable}_{volume}.{file_ext}')
        self.pos_name = self.pos_names[0]
        self.field_map_3D = os.path.join(self.model_folder, 'field_map_3D.csv')
        self.model_file = self.field_map_3D
        self.geom_folder = Path(self.model_folder).parent.parent
        # csv output definition for fields
        self.csv_ds = {'ds [m]': None}  # length of each hexahedron
        self.csv_sAve = {'sAvePositions [m]': None}  # cumulative positions along the electrical order of the center of each hexahedron
        self.csv_3Dsurf = {  # basically this is the mapping of coordinates of corners to output. This dictionary defines which corner of hexahedra gets
                             # used and which coordinate for each name like 'x3Dsurf 1'. Look into Hexahedron.py base class for drawing of corner numbering
            'x3Dsurf 1 [m]': {5: 'x'},
            'x3Dsurf 2 [m]': {6: 'x'},
            'y3Dsurf 1 [m]': {5: 'y'},
            'y3Dsurf 2 [m]': {6: 'y'},
            'z3Dsurf 1 [m]': {5: 'z'},
            'z3Dsurf 2 [m]': {6: 'z'},
            'x3Dsurf_2 1 [m]': {7: 'x'},
            'x3Dsurf_2 2 [m]': {6: 'x'},
            'y3Dsurf_2 1 [m]': {7: 'y'},
            'y3Dsurf_2 2 [m]': {6: 'y'},
            'z3Dsurf_2 1 [m]': {7: 'z'},
            'z3Dsurf_2 2 [m]': {6: 'z'}}
        self.csv_nodeToTurns = {'nodeToHalfTurn [-]': None,  # hexahedron (node) mapping to "Electrical" turns (electrical order)
                                'nodeToPhysicalTurn [-]': None}  # hexahedron (node) mapping to "Physical" turns (this is used for defining thermal connections between turns)
        self.csv_TransportCurrent = {'TransportCurrent [A]': None}  # Transport current in the turn (not channel) for which the magnetic field was calculated.
        # The above does not need to be changed for running models at different current.
        self.csv_Bs = {
            # lists with magnetic field flux density components along cartesian coordinates (x, y, z) and l, h, w i.e. length, height and width of the channel (or wires if aligned with channel).
            # x, y, z is used for display, l, h, w are used in LEDET for Ic scaling (well only h and w for perpendicular field).
            'Bx [T]': 'Vx',
            'By [T]': 'Vy',
            'Bz [T]': 'Vz',
            'Bl [T]': 'Vl',
            'Bh [T]': 'Vh',
            'Bw [T]': 'Vw',
        }
        self.headers_dict = {**self.csv_ds, **self.csv_sAve, **self.csv_3Dsurf, **self.csv_nodeToTurns, **self.csv_TransportCurrent, **self.csv_Bs}
        self.data_for_csv = {}
        self.precision_for_csv = {}
        # -------- make keys in data for csv ----
        for key in list(self.headers_dict.keys()):
            self.precision_for_csv[key] = '%.6f'  # data will be written to csv output file with 6 decimal places, i.e. down to um and uT level.
        for key in list(self.csv_ds.keys()):
            self.data_for_csv[key] = []
        for key in list(self.csv_sAve.keys()):
            self.data_for_csv[key] = []
        for key in list(self.csv_3Dsurf.keys()):
            self.data_for_csv[key] = []
        for key in list(self.csv_nodeToTurns.keys()):
            self.data_for_csv[key] = []
        for key in list(self.csv_TransportCurrent.keys()):
            self.data_for_csv[key] = []
        for key in list(self.csv_Bs.keys()):
            self.data_for_csv[key] = []
        self.distance_key = list(self.csv_ds.keys())[0]
        self.sAve_key = list(self.csv_sAve.keys())[0]

    @staticmethod
    def _get_fields(coord_center, normals):
        """
        Helper funciton to probe magnetic field solution form gmsh view and calculate magnetic field along the height, width and length of the channel section (hex element)
        :param coord_center: dictionary with 'x', 'y' and 'z' coordinates stored as lists with items for each hexahedra. Magnetic field is probed at these locations.
        :param normals:  dictionary with normals along the height, width and length stored per coordinate direction 'n_x', 'n_y' and 'n_z' and lists with items for each hexahedra.
        :return: tuple with list of Bxs, Bys, Bzs, Bhs, Bws, Bls
        """
        Bxs = []
        Bys = []
        Bzs = []
        Bhs = []
        Bws = []
        Bls = []
        view_tag = gmsh.view.getTags()[0]
        for v, _ in enumerate(coord_center['x']):
            field = gmsh.view.probe(view_tag, coord_center['x'][v], coord_center['y'][v], coord_center['z'][v])[0]
            Bx = field[0]
            By = field[1]
            Bz = field[2]
            Bmod = math.sqrt(Bx ** 2 + By ** 2 + Bz ** 2)
            Bh = abs(Bx * normals['normals_h']['n_x'][v] + By * normals['normals_h']['n_y'][v] + Bz * normals['normals_h']['n_z'][v])
            Bw = abs(Bx * normals['normals_w']['n_x'][v] + By * normals['normals_w']['n_y'][v] + Bz * normals['normals_w']['n_z'][v])
            Bl = math.sqrt(abs(Bmod ** 2 - Bh ** 2 - Bw ** 2))  # sometimes it is very small and negative, so force it to be positive before taking the root.
            for arr, val in zip([Bxs, Bys, Bzs, Bhs, Bws, Bls], [Bx, By, Bz, Bh, Bw, Bl]):
                arr.append(val)
        return Bxs, Bys, Bzs, Bhs, Bws, Bls

    @staticmethod
    def _plot_fields_in_views(p_name, global_channel_pos, coord_center, Bxs, Bys, Bzs):
        """
        Add gmsh list data view with name 'B cartesian {p_name}, {global_channel_pos}' at coordinates stored in coord_center and magnetic field values from list Bxs, Bys, Bzs
        :param p_name: string with powered region name
        :param global_channel_pos: integer with wire position in the channel
        :param coord_center: dictionary with 'x', 'y' and 'z' coordinates stored as lists with items for each hexahedra. Magnetic field is plotted at these locations.
        :param Bxs: list of magnetic field along the x axis to use in the view
        :param Bys: list of magnetic field along the y axis to use in the view
        :param Bzs: list of magnetic field along the z axis to use in the view
        :return: none, adds view to currently initialized gmsh model and synchronizes
        """
        data_cartesian = []
        for v, _ in enumerate(coord_center['x']):
            data_cartesian.append(coord_center['x'][v])
            data_cartesian.append(coord_center['y'][v])
            data_cartesian.append(coord_center['z'][v])
            data_cartesian.append(Bxs[v])
            data_cartesian.append(Bys[v])
            data_cartesian.append(Bzs[v])
        gmsh.view.addListData(gmsh.view.add(f'B cartesian {p_name}, {global_channel_pos}'), "VP", len(data_cartesian) // 6, data_cartesian)
        gmsh.model.occ.synchronize()

    @staticmethod
    def _plot_turns_in_view(data_turns, coord_center, turns_for_ch_pos):
        """
        Add gmsh list data view with name 'Turn numbering' at coordinates stored in coord_center and values from turns_for_ch_pos
        :param data_turns: This is list to which the data gets appended so at the end one view with all the turns labeled is created with looping through turns in the channels.
        :param coord_center: dictionary with 'x', 'y' and 'z' coordinates stored as lists with items for each hexahedra. Magnetic field is plotted at these locations.
        :param turns_for_ch_pos: Lists with turn numbers to plot in the view.
        :return: none, adds view to currently initialized gmsh model and synchronizes
        """
        for v, _ in enumerate(coord_center['x']):
            data_turns.append(coord_center['x'][v])
            data_turns.append(coord_center['y'][v])
            data_turns.append(coord_center['z'][v])
            data_turns.append(turns_for_ch_pos[v])
        gmsh.view.addListData(gmsh.view.add('Turn numbering'), "SP", len(data_turns) // 4, data_turns)
        gmsh.model.occ.synchronize()

    @staticmethod
    def _check_normals_match_corners(coord_center, normals_dict, p_name):
        """
        This is error checking function. Coord_centers are calculated in this class 'on the 'fly' form cctdm file. Normals are generated form geom_generators before meshing, then saved to file and now loaded here.
        There is a chance that thses could get 'out of sync'.         A basic check of the length (i.e. number of hexahedra involved is performed) of these lists is performed.
        This will only detect if number of turns or discretization of each powered geom_generators has changed.
        :param coord_center: list with coordinate centers. The content is not used only list length is queried.
        :param normals_dict: list with normals read form json file. The content is not used only list length is queried.
        :param p_name: string with powered volume name. Only used for error message display to say which region is not matching.
        :return: None, prints error to the python console, if any.
        """
        for cord in ['x', 'y', 'z']:
            if coord_center[cord].size != len(normals_dict['normals_h'][cord]) or coord_center[cord].size != len(normals_dict['normals_w'][cord]):
                raise ValueError(f'Number of volumes in normals does not match the magnet definition for {p_name} winding!')

    @staticmethod
    def _calc_coord_center_and_ds(corners_lists):
        """
        Calculates a geometrical centre of each hexahedron base on its corners coordinates
        :param corners_lists: lists of lists corresponding to a list of hexahedrons with each list containing 8 corner coordinates for each of the 8 points in the corners of hexahedron
        :return: coord_center: dictionary with 'x', 'y' and 'z' coordinates stored as lists with items for each hexahedra. and ds
        """
        coord_center = {}
        for cord in ['x', 'y', 'z']:
            coord_center[cord] = np.mean(corners_lists[cord], axis=0)  # coordinates center
        surf_close = {}
        surf_far = {}
        for cord in ['x', 'y', 'z']:
            surf_close[cord] = np.mean(corners_lists[cord][0:4], axis=0)  # coordinates surface close
            surf_far[cord] = np.mean(corners_lists[cord][4:8], axis=0)  # coordinates surface far
        ds = np.sqrt(np.square(surf_close['x'] - surf_far['x']) + np.square(surf_close['y'] - surf_far['y']) + np.square(surf_close['z'] - surf_far['z']))
        return coord_center, ds

    def _load_to_fields_csv_ds(self, ds, h3Dsurf, nodeToHalfTurn, nodeToPhysicalTurn, current, Bxs, Bys, Bzs, Bls, Bhs, Bws, s_ave):
        """
        Method to load data to csv dictionary to be dumped to a csv file.
        :param ds: length of each hexahedron
        :param h3Dsurf: dict with coordinates to export
        :param nodeToHalfTurn: hexahedron (node) mapping to "Electrical" turns (electrical order)
        :param nodeToPhysicalTurn: hexahedron (node) mapping to "Physical" turns (this is used for defining thermal connections between turns)
        :param current: Transport current in the turn (not channel) for which the magnetic field was calculated. It does not need to be changed for running models at different current.
        :param Bxs: list of magnetic flux density component along x direction
        :param Bys: list of magnetic flux density component along y direction
        :param Bzs: list of magnetic flux density component along z direction
        :param Bls: list of magnetic flux density component along l (length) of wire direction
        :param Bhs: list of magnetic flux density component along h (height) of wire direction
        :param Bws: list of magnetic flux density component along w (wight) of wire direction
        :param s_ave: cumulative positions along the electrical order of the center of each hexahedron
        :return: nothing, appends data to this class attribute data_for_csv
        """
        for arr, key in zip([ds, s_ave], list(self.csv_ds.keys()) + list(self.csv_sAve.keys())):
            self.data_for_csv[key].extend(arr)
        for key, dict_what in self.csv_3Dsurf.items():
            for p_n, p_c in dict_what.items():
                self.data_for_csv[key].extend(h3Dsurf[p_c][p_n])
        for arr, key in zip([Bxs, Bys, Bzs, Bls, Bhs, Bws, current, nodeToHalfTurn, nodeToPhysicalTurn], list(self.csv_Bs.keys()) + list(self.csv_TransportCurrent.keys()) + list(self.csv_nodeToTurns.keys())):
            self.data_for_csv[key].extend(arr)

    def _save_fields_csv(self):
        """
        Helper method to save csv file from data_for_csv class attribute.
        :return: nothing, saves csv to file with name magnet_name(from yaml input file)_total_n_turns.csv
        """
        # csv_file_path = os.path.join(self.model_folder, f'{self.magnet_name[:self.magnet_name.index("_")]}_{int(total_n_turns)}.csv')

        df = pd.DataFrame(self.data_for_csv)
        for column in df:
            df[column] = df[column].map(lambda x: self.precision_for_csv[column] % x)
        # put NaN at the end of some columns to match what LEDET needs.
        df.loc[df.index[-1], self.distance_key] = 'NaN'
        df.loc[df.index[-1], self.sAve_key] = 'NaN'
        # df.loc[df.index[-1], list(self.csv_nodeToTurns.keys())[0]] = 'NaN'
        for h in list(self.csv_nodeToTurns.keys()):
            df.loc[df.index[-1], h] = 'NaN'
        df.loc[df.index[-1], list(self.csv_TransportCurrent.keys())[0]] = 'NaN'
        for h in list(self.csv_Bs.keys()):
            df.loc[df.index[-1], h] = 'NaN'
        df.to_csv(self.field_map_3D, index=False, sep=',')  # , float_format='%.7f')

    @staticmethod
    def _trim_array(array, mask):
        return list(np.array(array)[mask])

    @staticmethod
    def _all_equal(iterator):
        iterator = iter(iterator)
        try:
            first = next(iterator)
        except StopIteration:
            return True
        return all(first == x for x in iterator)

    def postporcess_inductance(self):
        """
        Function to postprocess .dat file with inductance saved by GetDP to selfMutualInductanceMatrix.csv required by LEDET for CCT magnet solve
        :return: Nothing, writes selfMutualInductanceMatrix.csv file on disc.
        :rtype: None
        """
        inductance_file_from_getdp = os.path.join(self.model_folder, 'Inductance.dat')
        channels_inductance = ParserDAT(inductance_file_from_getdp).pqv    # postprocessed quantity value (pqv) for Inductance.dat contains magnet self-inductance  (channel, not wire turns)

        total_n_turns_channel = 0   # including fqpls
        for n_turns in self.cctdm.geometry.windings.n_turnss:
            total_n_turns_channel = total_n_turns_channel + n_turns
        if self._all_equal(self.cctdm.postproc.windings_wwns) and self._all_equal(self.cctdm.postproc.windings_whns):
            number_of_turns_in_channel = self.cctdm.postproc.windings_wwns[0] * self.cctdm.postproc.windings_whns[0]
        total_n_turns_channel = int(total_n_turns_channel)
        total_n_turns_channel_and_fqpls = total_n_turns_channel

        #windings_inductance = channels_inductance * total_n_turns_windings**2
        windings_inductance = channels_inductance * number_of_turns_in_channel**3   # scaling with square for number of turns in the channel as the model has current in the channel but not number of turns


        geometry_folder = Path(self.model_folder).parent.parent
        winding_information_file = os.path.join(geometry_folder, f"{self.magnet_name}.wi")
        cctwi = FilesAndFolders.read_data_from_yaml(winding_information_file, WindingsInformation)
        windings_avg_length = cctwi.windings_avg_length
        windings_inductance_per_m = windings_inductance / windings_avg_length

        print(f"Channels self-inductance: {channels_inductance} H")
        print(f"Number of turns in channel: {number_of_turns_in_channel} H")
        print(f"Total number of channel turns: {total_n_turns_channel} turns")
        print(f"Total number of inductance blocks: {total_n_turns_channel}")
        print(f"Windings self-inductance: {windings_inductance} H")
        print(f"Windings self-inductance per meter: {windings_inductance_per_m} H/m")
        print(f"Magnetic length: {windings_avg_length} m")

        fqpls_dummy_inductance_block = 1e-9    # H/m   (H per meter of magnet!)
        for _ in self.cctdm.geometry.fqpls.names:
            total_n_turns_channel_and_fqpls = total_n_turns_channel_and_fqpls + 1
            windings_inductance_per_m = windings_inductance_per_m - fqpls_dummy_inductance_block        # subtracting fqpls as they will be added later to the matrix

        win_ind_for_matrix = windings_inductance_per_m / total_n_turns_channel**2
        M_matrix = np.ones(shape=(total_n_turns_channel_and_fqpls, total_n_turns_channel_and_fqpls)) * win_ind_for_matrix
        M_matrix[:, total_n_turns_channel:total_n_turns_channel_and_fqpls] = 0.0       # mutual inductance of windings to fqpl set to zero for the columns
        M_matrix[total_n_turns_channel:total_n_turns_channel_and_fqpls, :] = 0.0       # mutual inductance of windings to fqpl set to zero for the rows
        for ij in range(total_n_turns_channel, total_n_turns_channel_and_fqpls, 1):
            M_matrix[ij, ij] = fqpls_dummy_inductance_block                                         # self-inductance of fqpls inductance block
        # below code is the same as in BuilderLEDET in steam_sdk
        csv_write_path = os.path.join(self.model_folder, 'selfMutualInductanceMatrix.csv')
        print(f'Saving square matrix of size {total_n_turns_channel_and_fqpls}x{total_n_turns_channel_and_fqpls} into: {csv_write_path}')
        with open(csv_write_path, 'w', newline='') as file:
            reader = csv.writer(file)
            reader.writerow(["# Extended self mutual inductance matrix [H/m]"])
            for i in range(M_matrix.shape[0]):
                reader.writerow(M_matrix[i])

    def postprocess_fields(self, gui=False):
        """
        Methods to calculated 'virtual' turn positions in the channels and output information for about them for LEDET as a csv file.
        :param gui: if True, graphical user interface (gui) of gmsh is shown with views created
        :return: nothing, writes csv to file
        """
        winding_order = self.cctdm.postproc.winding_order
        total_n_turns = 0
        for n_turns, wwn, whn in zip(self.cctdm.geometry.windings.n_turnss, self.cctdm.postproc.windings_wwns, self.cctdm.postproc.windings_whns):
            total_n_turns = total_n_turns + n_turns * wwn * whn

        gmsh.open(self.pos_name)
        global_channel_pos = 1
        # data_turns = []  # used in self._plot_turns_in_view() - do not delete
        csv_data_dict = {}
        s_max = 0
        for w_i, w_name in enumerate(self.cctdm.geometry.windings.names):  # + self.cctwi.f_names:
            normals_path = os.path.join(self.geom_folder, f"{w_name}.normals")
            with open(normals_path, "r", encoding="cp1252") as f:
                normals_dict = json.load(f)
            winding_obj = Winding(self.cctdm, w_i, post_proc=True)
            ww2 = self.cctdm.geometry.windings.wwws[w_i] / 2  # half of channel width
            wh2 = self.cctdm.geometry.windings.wwhs[w_i] / 2  # half of channel height
            wwns = self.cctdm.postproc.windings_wwns[w_i]  # number of wires in width direction
            whns = self.cctdm.postproc.windings_whns[w_i]  # number of wires in height direction
            wsw = self.cctdm.geometry.windings.wwws[w_i] / wwns  # wire size in width
            wsh = self.cctdm.geometry.windings.wwhs[w_i] / whns  # wire size in height
            for i_w in range(wwns):
                for i_h in range(whns):
                    corner_i = 0
                    corners_lists = {'x': [], 'y': [], 'z': []}
                    for far in [False, True]:
                        for ii_w, ii_h in zip([0, 0, 1, 1], [0, 1, 1, 0]):
                            wt = (-ww2 + (ii_w + i_w) * wsw) / ww2
                            ht = (-wh2 + (ii_h + i_h) * wsh) / wh2
                            corner_i += 1
                            xs, ys, zs, turns_from_rotation = winding_obj.calc_turns_corner_coords(wt, ht, far=far)
                            zs = [z - winding_obj.z_corr for z in zs]
                            corners_lists['x'].append(xs)
                            corners_lists['y'].append(ys)
                            corners_lists['z'].append(zs)
                    nodeToPhysicalTurn = [(global_channel_pos - 1) * self.cctdm.geometry.windings.n_turnss[w_i] + t for t in turns_from_rotation]
                    nodeToHalfTurn = [winding_order.index(global_channel_pos) * self.cctdm.geometry.windings.n_turnss[w_i] + t for t in turns_from_rotation]
                    coord_center, ds = self._calc_coord_center_and_ds(corners_lists)
                    self._check_normals_match_corners(coord_center, normals_dict, w_name)
                    # if global_channel_pos == 1:
                    #     s_ave_elem_len = np.copy(ds)
                    #     s_ave_elem_len[0] = s_ave_elem_len[0] / 2
                    #     s_ave = np.cumsum(s_ave_elem_len)
                    # else:
                    #     s_ave = np.cumsum(ds) + s_max
                    # s_max = np.max(s_ave)
                    current = [abs(self.cctdm.solve.windings.currents[w_i]) / (wwns * whns)] * len(nodeToHalfTurn)
                    Bxs, Bys, Bzs, Bhs, Bws, Bls = self._get_fields(coord_center, normals_dict)
                    if gui:
                        self._plot_fields_in_views(w_name, global_channel_pos, coord_center, Bxs, Bys, Bzs)
                        # self._plot_turns_in_view(data_turns, coord_center, nodeToHalfTurn)
                    csv_data_dict[winding_order.index(global_channel_pos) + 1] = ds, corners_lists, nodeToHalfTurn, nodeToPhysicalTurn, current, Bxs, Bys, Bzs, Bls, Bhs, Bws
                    global_channel_pos += 1
        for f_i, f_name in enumerate(self.cctdm.geometry.fqpls.names):
            # ----- calculate centers of coordinates for hexes of fqpl
            fqpl_obj = FQPL(self.cctdm, f_i)
            corners_lists = {'x': [], 'y': [], 'z': []}
            for corner_i in range(8):
                for cord in ['x', 'y', 'z']:
                    corners_lists[cord].append([v_dict[corner_i][cord] for v_dict in fqpl_obj.hexes.values()])
            coord_center, ds = self._calc_coord_center_and_ds(corners_lists)
            normals_path = os.path.join(self.geom_folder, f"{f_name}.normals")
            with open(normals_path, "r", encoding="cp1252") as f:
                normals_dict = json.load(f)
            self._check_normals_match_corners(coord_center, normals_dict, f_name)
            Bxs, Bys, Bzs, Bhs, Bws, Bls = self._get_fields(coord_center, normals_dict)
            self.masks_fqpls[f_i] = []          # dictionary to keep masks for trimming one end of fqpls that is long to extend to the end of air region, but not needed that long in simulations
            for z_close, z_far in zip(corners_lists['z'][0], corners_lists['z'][-1]):
                if z_close > -self.cctdm.geometry.fqpls.z_ends[f_i] * self.cctdm.postproc.fqpl_export_trim_tol[f_i] and z_far > -self.cctdm.geometry.fqpls.z_ends[f_i] * self.cctdm.postproc.fqpl_export_trim_tol[f_i]:
                    self.masks_fqpls[f_i].append(True)
                else:
                    self.masks_fqpls[f_i].append(False)
            self.masks_fqpls[f_i] = np.array(self.masks_fqpls[f_i], dtype=bool)
            for cord in ['x', 'y', 'z']:
                for corner_i, corner in enumerate(corners_lists[cord]):
                    corners_lists[cord][corner_i] = list(np.array(corner)[self.masks_fqpls[f_i]])
            lists_to_trim = [Bxs, Bys, Bzs, Bhs, Bws, Bls, ds]
            for idx, array in enumerate(lists_to_trim):
                lists_to_trim[idx] = self._trim_array(array, self.masks_fqpls[f_i])
            [Bxs, Bys, Bzs, Bhs, Bws, Bls, ds] = lists_to_trim
            for cord in ['x', 'y', 'z']:
                coord_center[cord] = self._trim_array(coord_center[cord], self.masks_fqpls[f_i])
            # s_ave = np.cumsum(ds) + s_max
            # s_max = np.max(s_ave)
            go_dict = {'from': 0, 'to': len(Bxs)//2}       # fqpl 'go' part
            ret_dict = {'from': len(Bxs)//2, 'to': len(Bxs)}
            for go_ret in [go_dict, ret_dict]:
                total_n_turns += 1
                ds_half = ds[go_ret['from']:go_ret['to']]
                corners_lists_half = {}
                for cord in ['x', 'y', 'z']:
                    corners_lists_half[cord] = []
                    for corner_i, corner in enumerate(corners_lists[cord]):
                        corners_lists_half[cord].append(corner[go_ret['from']:go_ret['to']])
                nodeToHalfTurn = [total_n_turns] * len(Bxs[go_ret['from']:go_ret['to']])  # total expected number of turns + one + fqpl number
                nodeToPhysicalTurn = [total_n_turns] * len(Bxs[go_ret['from']:go_ret['to']])
                current = [self.cctdm.solve.fqpls.currents[f_i]] * len(Bxs[go_ret['from']:go_ret['to']])
                Bxs_half = Bxs[go_ret['from']:go_ret['to']]
                Bys_half = Bys[go_ret['from']:go_ret['to']]
                Bzs_half = Bzs[go_ret['from']:go_ret['to']]
                Bls_half = Bls[go_ret['from']:go_ret['to']]
                Bhs_half = Bhs[go_ret['from']:go_ret['to']]
                Bws_half = Bws[go_ret['from']:go_ret['to']]
                #s_ave_half = s_ave[go_ret['from']:go_ret['to']]
                csv_data_dict[total_n_turns] = ds_half, corners_lists_half, nodeToHalfTurn, nodeToPhysicalTurn, current, Bxs_half, Bys_half, Bzs_half, Bls_half, Bhs_half, Bws_half
            if gui:
                self._plot_fields_in_views(f_name, global_channel_pos, coord_center, Bxs, Bys, Bzs)
            global_channel_pos += 1

        ds_global = []
        csv_data_sorded = dict(sorted(csv_data_dict.items())).values()# sorted list of tuples with the csv data
        for tuple_with_values in csv_data_sorded:
            ds_global.append(tuple_with_values[0])      # 0 index in tuple is for ds, changing to list to easily extend.

        s_ave_global = []
        s_max = -ds_global[0][0]/2 # make a s_max to a negative half of the length of the first hexahedra. This is to set the first s_ave max to a half of the first ds element
        for ds_i, ds_np in enumerate(ds_global):
            s_ave_np = np.cumsum(ds_np) + s_max
            s_ave_global.append(s_ave_np)
            s_max = np.max(s_ave_np)

        for sorted_v_tuple, s_ave_np in zip(csv_data_sorded, s_ave_global):
            self._load_to_fields_csv_ds(*sorted_v_tuple, s_ave_np)  # this is to avoid rearranging s_ave by electrical order

        #el_order_half_turns = [int(t) for t in list(pd.unique(self.data_for_csv['nodeToPhysicalTurn [-]']))]
        #json.dump({'el_order_half_turns': el_order_half_turns}, open(os.path.join(self.model_folder, "el_order_half_turns.json"), 'w'))
        self._save_fields_csv()
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()

