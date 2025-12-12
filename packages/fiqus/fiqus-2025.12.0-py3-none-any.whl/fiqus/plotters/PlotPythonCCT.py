import os
from operator import le, ge

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from fiqus.geom_generators.GeometryCCT import Winding, FQPL


class PlotPythonCCT:
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
        # self.gu = GmshUtils(self.model_folder, self.verbose)
        # self.gu.initialize()

    def plot_elements_file(self, lfes=None):
        field_map_3D_csv = 'field_map_3D.csv'
        df = pd.read_csv(field_map_3D_csv, delimiter=',', engine='python')
        sAvePositions = df['sAvePositions [m]'].to_numpy(dtype='float')[:-1]  # [:-1] to remove last nan
        ph_order = df['nodeToPhysicalTurn [-]'].to_numpy(dtype='int')[:-1]  # physical turns, [:-1] to remove last nan
        el_order = df['nodeToHalfTurn [-]'].to_numpy(dtype='int')[:-1]  # electric order turns, [:-1] to remove last nan
        x3Dsurf_1 = df['x3Dsurf 1 [m]'].to_numpy(dtype='float')
        y3Dsurf_1 = df['y3Dsurf 1 [m]'].to_numpy(dtype='float')
        z3Dsurf_1 = df['z3Dsurf 1 [m]'].to_numpy(dtype='float')
        el_order_unique = np.unique(el_order)

        per_turn = False

        fig = plt.figure(figsize=(16, 10))
        ax = fig.add_subplot(111, projection='3d', proj_type='ortho')

        if per_turn:
            colors = cm.rainbow(np.linspace(0, 1, np.shape(el_order_unique)[0]))
            for idx_turn, el_u in enumerate(el_order_unique.tolist()):
                indexes = np.where(el_u == el_order)[0]
                min_idx=np.min(indexes)
                max_idx=np.max(indexes+2)
                ax.plot(x3Dsurf_1[min_idx:max_idx], y3Dsurf_1[min_idx:max_idx], z3Dsurf_1[min_idx:max_idx], color=colors[idx_turn])
        else:
            ax.plot(x3Dsurf_1, y3Dsurf_1, z3Dsurf_1)
        # colors = cm.rainbow(np.linspace(0, 1, np.shape(x3Dsurf_1)[0]))
        # # ax.plot(x3Dsurf_1, y3Dsurf_1, z3Dsurf_1)

        # for idx in range(np.shape(x3Dsurf_1)[0]-1):
        #     ax.plot([x3Dsurf_1[idx], x3Dsurf_1[idx+1]], [y3Dsurf_1[idx], y3Dsurf_1[idx+1]], [z3Dsurf_1[idx], z3Dsurf_1[idx+1]], color=colors[idx])
        # xmin, xmax, ymin, ymax, zmin, zmax = (0, 0, 0, 0, 0, 0)
        # #colors = cm.rainbow(np.linspace(0, 1, len(objects_list)))
        # ax.set_box_aspect((xmax - xmin, ymax - ymin, zmax - zmin))  # set axis to data aspect ratio
        # ax.set_xlim([xmin, xmax])
        # ax.set_ylim([ymin, ymax])
        # ax.set_zlim([zmin, zmax])
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_zlabel('z (m)')
        ax.view_init(elev=90, azim=0, vertical_axis='x')
        plt.show()
        pass

    def plot_elements_computed(self, lfes=None):
        """
        Makes a plot oh hexahedra by calculating 'on the fly' what is defined in the yaml data model for cct magnet.
        :param lfes: list with numbers of elements to put text labels on. For two windings an example would be [[3], [9]] to plot 3rd hex in the first winding and 9th in the second
        :return: Nothing. A matplotlib graph pops up on the screen.
        """

        windings = []
        fqpls = []
        for ww, _ in enumerate(self.cctdm.geometry.windings.names):
            winding_obj = Winding(self.cctdm, ww, post_proc=True)
            windings.append(winding_obj)
        for ff, _ in enumerate(self.cctdm.geometry.fqpls.names):
            fqpl_obj = FQPL(self.cctdm, ff)
            fqpls.append(fqpl_obj)
        objects_list = windings + fqpls
        if not lfes:
            lfes = [[] for _ in objects_list]  # make it work if lfes is not supplied as input.

        def val_check(var, array, oper, func):
            new = func(array)
            if oper(new, var):
                return new
            else:
                return var

        fig = plt.figure(figsize=(16, 10))
        ax = fig.add_subplot(111, projection='3d', proj_type='ortho')
        xmin, xmax, ymin, ymax, zmin, zmax = (0, 0, 0, 0, 0, 0)
        colors = cm.rainbow(np.linspace(0, 1, len(objects_list)))
        for obj, lfe, fc in zip(objects_list, lfes, colors):
            xs = []
            ys = []
            zs = []
            hexes = obj.hexes
            vts = obj.vertices_to_surf
            for elem_num, points_dict in hexes.items():
                list_of_coor_tuples = []
                points_dict.pop('ct', None)  # removing turn from dict
                for p_num, p_coords in points_dict.items():

                    list_of_coor_tuples.append((p_coords['x'], p_coords['y'], p_coords['z']))
                    if elem_num in lfe:
                        ax.scatter(p_coords['x'], p_coords['y'], p_coords['z'])
                        ax.text(p_coords['x'], p_coords['y'], p_coords['z'], f'{p_num}', zdir='z')
                    for coor_acc, coor_key in zip([xs, ys, zs], ['x', 'y', 'z']):
                        coor_acc.append(p_coords[coor_key])
                poly3d = [[list_of_coor_tuples[vts[ix][iy]] for iy in range(len(vts[0]))] for ix in range(len(vts))]
                ax.add_collection3d(Poly3DCollection(poly3d, edgecolors='k', facecolors=fc, linewidths=0.5, alpha=0.5))
            xmin = val_check(xmin, xs, le, np.min)
            xmax = val_check(xmax, xs, ge, np.max)
            ymin = val_check(ymin, ys, le, np.min)
            ymax = val_check(ymax, ys, ge, np.max)
            zmin = val_check(zmin, zs, le, np.min)
            zmax = val_check(zmax, zs, ge, np.max)
        ax.set_box_aspect((xmax - xmin, ymax - ymin, zmax - zmin))  # set axis to data aspect ratio
        ax.set_xlim([xmin, xmax])
        ax.set_ylim([ymin, ymax])
        ax.set_zlim([zmin, zmax])
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_zlabel('z (m)')
        ax.view_init(elev=90, azim=0, vertical_axis='x')
        plt.show()