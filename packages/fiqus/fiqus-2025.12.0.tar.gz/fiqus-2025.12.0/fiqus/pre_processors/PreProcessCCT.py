import math
import os
import timeit
import json
import gmsh
import numpy as np
from fiqus.utils.Utils import FilesAndFolders as uff
from fiqus.utils.Utils import GmshUtils
from fiqus.data.DataWindingsCCT import WindingsInformation         # for volume information


class Pre_Process:
    def __init__(self, fdm, verbose=True):
        """
        Class to preparing brep files by adding terminals.
        :param fdm: FiQuS data model
        :param verbose: If True more information is printed in python console.
        """
        self.cctdm = fdm.magnet
        self.model_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name
        winding_info_file = os.path.join(self.model_folder, f'{self.magnet_name}.wi')
        self.cctwi = uff.read_data_from_yaml(winding_info_file, WindingsInformation)
        self.verbose = verbose
        self.gu = GmshUtils(self.model_folder, self.verbose)
        self.gu.initialize()

    def calculate_normals(self, gui=False):
        """
        Calculates normals for the cct channel directions, i.e. along winding direction, along radial direction of the former (height) and along axial direction (width). Normals are saved to a .json
        file and used later for post-processing of magnetic field into components along channel length, height and width. Note that this function does not give the correct 'sign of normals', i.e.
        normals facing inwards or outwards of the surface are not properly distinguished. The normals along the length are not reliable and only along the height and width are used for calculations and
        the field along the length is taken as a remaining field.
        This function needs full geom_generators .brep file and volume information files (.vi) for each individual powered volume.
        :param gui: if True, the gmsh graphical user interface is shown at the end and normals are displayed as a view
        :return: Nothing, a file for each powered geom_generators brep is
        """
        if self.verbose:
            print('Calculating Normals Started')
            start_time = timeit.default_timer()
        gmsh.open(os.path.join(self.model_folder, f'{self.magnet_name}.brep'))

        def _calc_normals_dir(tags_for_normals_in, surfs_idx, surfs_scale):
            v_to_suf = [[0, 1, 2, 3], [0, 1, 5, 4], [4, 5, 6, 7], [3, 7, 6, 2], [0, 3, 7, 4], [1, 5, 6, 2]]
            norm_e_x = []   # normal along x of volume
            norm_e_y = []
            norm_e_z = []
            norm_dict = {}
            normals_view = []  # this remains an empty list if view is False
            coor_e_x = []   # coordinate x of the center of volume
            coor_e_y = []
            coor_e_z = []
            for vol_tag in tags_for_normals_in:
                all_surf_tags = gmsh.model.getAdjacencies(3, vol_tag)[1]
                surf_tags = [all_surf_tags[index] for index in surfs_idx]
                norm = []
                node_coord = []
                vol_line_tags = []
                for surf_tag in all_surf_tags:
                    line_tags_new = gmsh.model.getAdjacencies(2, surf_tag)[1]
                    for line_tag in line_tags_new:
                        if line_tag not in vol_line_tags:
                            vol_line_tags.append(line_tag)
                point_tags = []
                for line_tag in vol_line_tags:
                    point_tags_new = gmsh.model.getAdjacencies(1, line_tag)[1]
                    for point_tag in point_tags_new:
                        if point_tag not in point_tags:
                            point_tags.append(int(point_tag))
                for surf_i, surf_tag, scale in zip(surfs_idx, surf_tags, surfs_scale):
                    p_idx = v_to_suf[surf_i]
                    s_node_coord = []
                    for p_i in p_idx:
                        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(0, point_tags[p_i])
                        s_node_coord.append((xmin + xmax) / 2)
                        s_node_coord.append((ymin + ymax) / 2)
                        s_node_coord.append((zmin + zmax) / 2)
                    parametricCoord = gmsh.model.getParametrization(2, surf_tag, s_node_coord)
                    s_norm = gmsh.model.getNormal(surf_tag, parametricCoord)
                    norm.extend(scale*s_norm)
                    node_coord.extend(s_node_coord)
                coor_s_x = []   # coordinates surface x
                coor_s_y = []
                coor_s_z = []
                norm_s_x = []   # normals surface x
                norm_s_y = []
                norm_s_z = []

                for i in range(0, len(node_coord), 3):
                    coor_s_x.append(node_coord[i])
                    coor_s_y.append(node_coord[i+1])
                    coor_s_z.append(node_coord[i+2])
                    norm_s_x.append(norm[i])
                    norm_s_y.append(norm[i+1])
                    norm_s_z.append(norm[i+2])

                coor_e_x.append(np.mean(coor_s_x))
                coor_e_y.append(np.mean(coor_s_y))
                coor_e_z.append(np.mean(coor_s_z))
                # norm_e_x.append(np.mean(norm_s_x))
                # norm_e_y.append(np.mean(norm_s_y))
                # norm_e_z.append(np.mean(norm_s_z))

                # norm_e_x.append(np.sqrt(np.sum(np.square(norm_s_x)))/(2*np.sqrt(2)))
                # norm_e_y.append(np.sqrt(np.sum(np.square(norm_s_y)))/(2*np.sqrt(2)))
                # norm_e_z.append(np.sqrt(np.sum(np.square(norm_s_z)))/(2*np.sqrt(2)))
                v_x = np.sum(norm_s_x)
                v_y = np.sum(norm_s_y)
                v_z = np.sum(norm_s_z)
                ampl = math.sqrt(v_x**2 + v_y**2 + v_z**2)

                norm_e_x.append(v_x/ampl)
                norm_e_y.append(v_y/ampl)
                norm_e_z.append(v_z/ampl)

            for i in range(len(coor_e_x)):
                normals_view.append(coor_e_x[i])
                normals_view.append(coor_e_y[i])
                normals_view.append(coor_e_z[i])
                normals_view.append(norm_e_x[i])
                normals_view.append(norm_e_y[i])
                normals_view.append(norm_e_z[i])
            norm_dict['x'] = coor_e_x
            norm_dict['y'] = coor_e_y
            norm_dict['z'] = coor_e_z
            norm_dict['n_x'] = norm_e_x
            norm_dict['n_y'] = norm_e_y
            norm_dict['n_z'] = norm_e_z
            return norm_dict, normals_view
        """
        This is helper function called in a loop below.
        """
        max_tag = 0
        for f_name in self.cctwi.w_names+self.cctwi.f_names:
            vol_tags = json.load(open(os.path.join(self.model_folder, f'{f_name}.vi')))
            export_tags = vol_tags['export']
            tags_for_normals = [e + max_tag for e in export_tags]
            max_tag = np.max(vol_tags['all']) + max_tag
            surfs_idx_l = [0, 2]    # along length of the former groove
            if f_name in self.cctwi.w_names:
                surfs_scale_l = [1, 1]
            elif f_name in self.cctwi.f_names:
                surfs_scale_l = [1, -1]     # change direction for fqpl
            norm_l, norm_view_l = _calc_normals_dir(tags_for_normals, surfs_idx_l, surfs_scale_l)
            surfs_idx_h = [1, 3]         # along height of the former groove
            surfs_scale_h = [1, -1]
            norm_h, norm_view_h = _calc_normals_dir(tags_for_normals, surfs_idx_h, surfs_scale_h)
            surfs_idx_w = [4, 5]        # along width of the former groove
            surfs_scale_w = [1, -1]
            norm_w, norm_view_w = _calc_normals_dir(tags_for_normals, surfs_idx_w, surfs_scale_w)
            normals_dict = {'normals_l': norm_l, 'normals_h': norm_h, 'normals_w': norm_w}
            json.dump(normals_dict, open(f"{os.path.join(self.model_folder, f_name)}.normals", 'w'))
            if gui:
                normals_all = [norm_view_l, norm_view_h, norm_view_w]
                self.__add_normals_view(f_name, normals_all)
        if self.verbose:
            print(f'Calculating Normals Took {timeit.default_timer() - start_time:.2f} s')
        if gui:
            self.gu.launch_interactive_GUI()

    @staticmethod
    def __add_normals_view(name, normals_all, norm_list=[0, 1, 2]):
        """
        THis adds new view in gmsh.
        :param name: name of view
        :param normals_all: dictionary with normals
        :param norm_list: which normals to plot. Default is: [0, 1, 2] corresponds to [n_l, n_h, n_w]. If this array is shorter the corresponding normals are skipped in views.
        :return:
        """
        norm_names_all = [f"{name}_n_l", f"{name}_n_h", f"{name}_n_w"]
        norm_names = [norm_names_all[index] for index in norm_list]
        normals = [normals_all[index] for index in norm_list]
        for view_name, view_data in zip(norm_names, normals):
            gmsh.view.addListData(gmsh.view.add(view_name), "VP", len(view_data) // 6, view_data)
        gmsh.model.occ.synchronize()
