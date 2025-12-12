import os
import gmsh
import numpy as np
import pandas as pd
import json

from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import FilesAndFolders as Util
from fiqus.utils.Utils import GeometricFunctions as Func
from fiqus.data import DataFiQuS as dF
from fiqus.data import DataMultipole as dM
from fiqus.data.DataRoxieParser import FiQuSGeometry
from fiqus.data.DataRoxieParser import Corner
from fiqus.data.DataRoxieParser import Coord
import re

class Geometry:
    def __init__(self, data: dF.FDM() = None, geom: FiQuSGeometry() = None,
                 geom_folder: str = None, verbose: bool = False):
        """
        Class to generate geometry
        :param data: FiQuS data model
        :param geom: ROXIE geometry data
        :param verbose: If True more information is printed in python console.
        """
        self.data: dF.FDM() = data
        self.geom: FiQuSGeometry() = geom.Roxie_Data
        self.geom_folder = geom_folder
        self.verbose: bool = verbose

        self.md = dM.MultipoleData()

        self.gu = GmshUtils(self.geom_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=self.data.run.verbosity_Gmsh)
        self.occ = gmsh.model.occ

        self.model_file = os.path.join(self.geom_folder, self.data.general.magnet_name)

        self.blk_ins_lines = {}  # for meshed insulation
        self.ins_wire_lines = {}  # for meshed insulation
        self.block_coil_mid_pole_blks = {}

        if self.data.magnet.geometry.electromagnetics.symmetry != 'none':
            self.symmetric_loop_lines = {'x': [], 'y': []}
            self.symmetric_bnds = {'x_p': {'pnts': [], 'line_pnts': []}, 'y_p': {'pnts': [], 'line_pnts': []},
                                   'x_n': {'pnts': [], 'line_pnts': []}, 'y_n': {'pnts': [], 'line_pnts': []}}

    def clear(self):
        self.md = dM.MultipoleData()
        self.block_coil_mid_pole_blks = {}
        gmsh.clear()

    def ending_step(self, gui: bool = False):
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()

    def saveHalfTurnCornerPositions(self):
        self.occ.synchronize()
        iH, iL, oH, oL, iHr, iLr, oHr, oLr = [], [], [], [], [], [], [], []
        for po in self.geom.coil.physical_order:
            block = self.geom.coil.coils[po.coil].poles[po.pole].layers[po.layer].windings[
                po.winding].blocks[po.block]
            for halfTurn_nr, halfTurn in block.half_turns.items():
                ht = halfTurn.corners.insulated
                ht_b = halfTurn.corners.bare
                iHr.append([ht_b.iH.x, ht_b.iH.y])
                iLr.append([ht_b.iL.x, ht_b.iL.y])
                oHr.append([ht_b.oH.x, ht_b.oH.y])
                oLr.append([ht_b.oL.x, ht_b.oL.y])
                iH.append([ht.iH.x, ht.iH.y])
                iL.append([ht.iL.x, ht.iL.y])
                oH.append([ht.oH.x, ht.oH.y])
                oL.append([ht.oL.x, ht.oL.y])
        json.dump({'iH': iH, 'iL': iL, 'oH': oH, 'oL': oL,
                   'iHr': iHr, 'iLr': iLr, 'oHr': oHr, 'oLr': oLr}, open(f"{self.model_file}.crns", 'w'))

    def saveStrandPositions(self, run_type):
        symmetry = self.data.magnet.geometry.electromagnetics.symmetry if run_type == 'EM' else 'none'
        ht_nr = 0
        std_nr = 0
        parser_x, parser_y, blocks, ht, std, pole_blocks = [], [], [], [], [], []
        for po in self.geom.coil.physical_order:
            block = self.geom.coil.coils[po.coil].poles[po.pole].layers[po.layer].windings[
                po.winding].blocks[po.block]
            if po.pole == 1: pole_blocks.append(po.block)
            for halfTurn_nr, halfTurn in block.half_turns.items():
                ht_nr += 1
                for strand_group_nr, strand_group in halfTurn.strand_groups.items():
                    for strand_nr, strand in strand_group.strand_positions.items():
                        std_nr += 1
                        blocks.append(po.block)
                        ht.append(ht_nr)
                        std.append(std_nr)
                        parser_x.append(strand.x)
                        parser_y.append(strand.y)
        mirrored = {}
        condition = {2: [1, -1], 3: [1, 1], 4: [-1, 1]}
        if symmetry == 'xy': mirroring = {2: [-1, 1], 3: [-1, -1], 4: [1, -1]}
        elif symmetry == 'x': mirroring = {3: [1, -1], 4: [1, -1]}
        elif symmetry == 'y': mirroring = {2: [-1, 1], 3: [-1, 1]}
        else: mirroring = {}
        if mirroring:
            df = pd.DataFrame({'parser_x': parser_x, 'parser_y': parser_y}, index=std)
            for qdr, mrr in mirroring.items():
                subdf = df[(condition[qdr][0] * df['parser_x'] < 0) & (condition[qdr][1] * df['parser_y'] < 0)]
                for strand, x, y in zip(subdf.index, subdf['parser_x'], subdf['parser_y']):
                    mirrored[strand] = df[(df['parser_x'] == mrr[0] * x) & (df['parser_y'] == mrr[1] * y)].index.item()
        json.dump({'x': parser_x, 'y': parser_y, 'block': blocks, 'ht': ht, 'mirrored': mirrored,
                   'pole_1_blocks': pole_blocks, 'poles': len(self.geom.coil.coils[1].poles)},
                  open(f"{self.model_file}_{run_type}.strs", 'w'))

    def saveBoundaryRepresentationFile(self, run_type):
        self.occ.synchronize()
        gmsh.write(f'{self.model_file}_{run_type}.brep')
        gmsh.clear()

    def loadBoundaryRepresentationFile(self, run_type):
        gmsh.option.setString('Geometry.OCCTargetUnit', 'M')  # set units to meters
        gmsh.open(os.path.join(f'{self.model_file}_{run_type}.brep'))

    def saveAuxiliaryFile(self, run_type):
        Util.write_data_to_yaml(f'{self.model_file}_{run_type}.aux', self.md.model_dump())

    @staticmethod
    def findMidLayerPoint(bc_current, bc_next, center, mean_rad):
        mid_layer = [(bc_current.x + bc_next.x) / 2, (bc_current.y + bc_next.y) / 2]
        mid_rad = Func.points_distance(mid_layer, [center.x, center.y])
        dist_from_mid = mean_rad - mid_rad
        angle = Func.arc_angle_between_point_and_abscissa(mid_layer, [center.x, center.y])
        mid_layer[0] += dist_from_mid * np.cos(angle)
        mid_layer[1] += dist_from_mid * np.sin(angle)
        return mid_layer

    @staticmethod
    def getMidLayerEndpoints(el_current, el_next, center, mid_layer_arc_pnt=None, coil_type='cos-theta', cable_type='Rutherford', is_for_mid_pole=False):
        thin_shell_endpoints = {'higher': list, 'lower': list}
        which_block = {'higher': str, 'lower': str}
        angles = {'higher': float, 'lower': float}
        # Check if the element crosses the x axis
        angles_to_correct = []
        correction_angle = 0
        l_curr = Func.arc_angle_between_point_and_abscissa([el_current.iL.x, el_current.iL.y], center)
        h_curr = Func.arc_angle_between_point_and_abscissa([el_current.iH.x, el_current.iH.y], center)
        l_next = Func.arc_angle_between_point_and_abscissa([el_next.iL.x, el_next.iL.y], center)
        h_next = Func.arc_angle_between_point_and_abscissa([el_next.iH.x, el_next.iH.y], center)
        if abs(l_curr - h_curr) > np.pi:
            angles_to_correct.append('current')
            correction_angle = max(1.05 * (2 * np.pi - l_curr), correction_angle)
        if abs(l_next - h_next) > np.pi:
            angles_to_correct.append('next')
            correction_angle = max(1.05 * (2 * np.pi - l_next), correction_angle)
        for side in thin_shell_endpoints.keys():
            if mid_layer_arc_pnt:
                if side == 'higher':
                    mid_lyr_curr, mid_lyr_next = [el_current.oH, el_current.iH], [el_next.oH, el_next.iH]
                else:
                    mid_lyr_curr, mid_lyr_next = [el_current.oL, el_current.iL], [el_next.oL, el_next.iL]
                if cable_type in ['Mono', 'Ribbon']:
                    pnts_curr = Func.intersection_between_circle_and_line(
                        Func.line_through_two_points([mid_lyr_curr[0].x, mid_lyr_curr[0].y], [mid_lyr_curr[1].x, mid_lyr_curr[1].y]),
                        [center, mid_layer_arc_pnt])
                    pnt_curr = pnts_curr[0] if Func.points_distance(pnts_curr[0], [mid_lyr_curr[0].x, mid_lyr_curr[0].y]) <\
                                               Func.points_distance(pnts_curr[1], [mid_lyr_curr[0].x, mid_lyr_curr[0].y]) else pnts_curr[1]
                    pnts_next = Func.intersection_between_circle_and_line(
                        Func.line_through_two_points([mid_lyr_next[0].x, mid_lyr_next[0].y], [mid_lyr_next[1].x, mid_lyr_next[1].y]),
                        [center, mid_layer_arc_pnt])
                    pnt_next = pnts_next[0] if Func.points_distance(pnts_next[0], [mid_lyr_next[0].x, mid_lyr_next[0].y]) <\
                                               Func.points_distance(pnts_next[1], [mid_lyr_next[0].x, mid_lyr_next[0].y]) else pnts_next[1]
                elif cable_type == 'Rutherford':
                    pnt_curr = Func.intersection_between_circle_and_line(
                        Func.line_through_two_points([mid_lyr_curr[0].x, mid_lyr_curr[0].y], [mid_lyr_curr[1].x, mid_lyr_curr[1].y]),
                        [center, mid_layer_arc_pnt], get_only_closest=True)[0]
                    pnt_next = Func.intersection_between_circle_and_line(
                        Func.line_through_two_points([mid_lyr_next[0].x, mid_lyr_next[0].y], [mid_lyr_next[1].x, mid_lyr_next[1].y]),
                        [center, mid_layer_arc_pnt], get_only_closest=True)[0]
            else:
                if cable_type == 'Rutherford':
                    if coil_type == 'common-block-coil':
                        mid_layer_x = (el_current.oH.x + el_next.iH.x) / 2
                        if side == 'higher':
                            pnt_curr, pnt_next = [mid_layer_x, el_current.iH.y], [mid_layer_x, el_next.iH.y]
                        else:
                            pnt_curr, pnt_next = [mid_layer_x, el_current.iL.y], [mid_layer_x, el_next.iL.y]
                    else:
                        mid_layer_y = (el_current.iH.y + el_next.iH.y) / 2 if is_for_mid_pole else (el_current.oH.y + el_next.iH.y) / 2
                        if side == 'higher':
                            pnt_curr, pnt_next = [el_current.iH.x, mid_layer_y], [el_next.iL.x if is_for_mid_pole else el_next.iH.x, mid_layer_y]
                        else:
                            pnt_curr, pnt_next = [el_current.iL.x, mid_layer_y], [el_next.iH.x if is_for_mid_pole else el_next.iL.x, mid_layer_y]
                elif cable_type in ['Mono', 'Ribbon']:
                    pnt_curr = [(el_current.oH.x + el_next.iH.x) / 2, (el_current.oH.y + el_next.iH.y) / 2] if side == 'higher'\
                        else [(el_current.oL.x + el_next.iL.x) / 2, (el_current.oL.y + el_next.iL.y) / 2]
                    pnt_next = pnt_curr
            angle_curr = Func.arc_angle_between_point_and_abscissa(pnt_curr, center)
            angle_next = Func.arc_angle_between_point_and_abscissa(pnt_next, center)
            if 'current' in angles_to_correct:
                angle_curr = angle_curr + correction_angle - (2 * np.pi if side == 'lower' else 0)
            elif 'next' in angles_to_correct:
                if angle_curr < np.pi / 2: angle_curr += correction_angle
                elif angle_curr > np.pi * 3 / 2: angle_curr = angle_curr + correction_angle - 2 * np.pi
            if 'next' in angles_to_correct:
                angle_next = angle_next + correction_angle - (2 * np.pi if side == 'lower' else 0)
            elif 'current' in angles_to_correct:
                if angle_next < np.pi / 2: angle_next += correction_angle
                elif angle_next > np.pi * 3 / 2: angle_next = angle_next + correction_angle - 2 * np.pi
            if abs(angle_curr - angle_next) < 1e-6:  # todo: check if needed
                thin_shell_endpoints[side], angles[side], which_block[side] = pnt_curr, angle_curr, 'current'
            elif angle_curr * (-1 if side == 'lower' else 1) < angle_next * (-1 if side == 'lower' else 1):
                thin_shell_endpoints[side], angles[side], which_block[side] = pnt_curr, angle_curr, 'current'
            else:
                thin_shell_endpoints[side], angles[side], which_block[side] = pnt_next, angle_next, 'next'
        if angles['higher'] < angles['lower']: return None
        else: return thin_shell_endpoints, which_block

    def constructIronGeometry(self, symmetry):
        """
            Generates points, hyper lines, and curve loops for the iron yoke
        """
        iron = self.geom.iron
        if symmetry == 'xy':
            self.md.geometries.iron.quadrants = {1: dM.Region()}
            list_bnds = ['x_p', 'y_p']
        elif symmetry == 'x':
            self.md.geometries.iron.quadrants = {1: dM.Region(), 2: dM.Region()}
            list_bnds = ['x_p', 'x_n']
        elif symmetry == 'y':
            self.md.geometries.iron.quadrants = {1: dM.Region(), 4: dM.Region()}
            list_bnds = ['y_p', 'y_n']
        else:
            self.md.geometries.iron.quadrants = {1: dM.Region(), 2: dM.Region(), 4: dM.Region(), 3: dM.Region()}
            list_bnds = []
        quadrants = self.md.geometries.iron.quadrants

        lc = 1e-2
        for point_name, point in iron.key_points.items():
            if symmetry in ['x', 'xy']:
                if point.y == 0.:
                    self.symmetric_bnds['x_p']['pnts'].append([point_name, point.x])
            if symmetry in ['y', 'xy']:
                if point.x == 0.:
                    self.symmetric_bnds['y_p']['pnts'].append([point_name, point.y])
            quadrants[1].points[point_name] = self.occ.addPoint(point.x, point.y, 0, lc)
            if symmetry in ['x', 'none']:
                if point.x == 0.:
                    quadrants[2].points[point_name] = quadrants[1].points[point_name]
                else:
                    quadrants[2].points[point_name] = self.occ.copy([(0, quadrants[1].points[point_name])])[0][1]
                    self.occ.mirror([(0, quadrants[2].points[point_name])], 1, 0, 0, 0)
                    if point.y == 0. and symmetry == 'x':
                        self.symmetric_bnds['x_n']['pnts'].append([point_name, point.x])
            if symmetry in ['y', 'none']:
                if point.y == 0.:
                    quadrants[4].points[point_name] = quadrants[1].points[point_name]
                else:
                    quadrants[4].points[point_name] = self.occ.copy([(0, quadrants[1].points[point_name])])[0][1]
                    self.occ.mirror([(0, quadrants[4].points[point_name])], 0, 1, 0, 0)
                    if point.x == 0. and symmetry == 'y':
                        self.symmetric_bnds['y_n']['pnts'].append([point_name, point.y])
            if symmetry == 'none':
                if point.y == 0.:
                    quadrants[3].points[point_name] = quadrants[2].points[point_name]
                elif point.x == 0.:
                    quadrants[3].points[point_name] = quadrants[4].points[point_name]
                else:
                    quadrants[3].points[point_name] = self.occ.copy([(0, quadrants[2].points[point_name])])[0][1]
                    self.occ.mirror([(0, quadrants[3].points[point_name])], 0, 1, 0, 0)

        mirror_x = [1, -1, -1, 1]
        mirror_y = [1, 1, -1, -1]
        symmetric_bnds_order = {'x': [], 'y': []}
        sym_lines_tags = {'x_p': [], 'y_p': [], 'x_n': [], 'y_n': []}
        for line_name, line in iron.hyper_lines.items():
            pt1 = iron.key_points[line.kp1]
            pt2 = iron.key_points[line.kp2]
            if line.type == 'line':
                for quadrant, qq in quadrants.items():
                    if quadrant == 1:
                        qq.lines[line_name] = self.occ.addLine(qq.points[line.kp1], qq.points[line.kp2])
                        if pt1.y == 0. and pt2.y == 0. and 'x_p' in list_bnds:
                            self.symmetric_bnds['x_p']['line_pnts'].append(line.kp1 + '_' + line.kp2)
                            sym_lines_tags['x_p'].append(qq.lines[line_name])
                            symmetric_bnds_order['x'].append(min(pt1.x, pt2.x))
                        elif pt1.x == 0. and pt2.x == 0. and 'y_p' in list_bnds:
                            self.symmetric_bnds['y_p']['line_pnts'].append(line.kp1 + '_' + line.kp2)
                            sym_lines_tags['y_p'].append(qq.lines[line_name])
                            symmetric_bnds_order['y'].append(min(pt1.y, pt2.y))
                    elif quadrant == 2:
                        if pt1.x == 0. and pt2.x == 0.:
                            qq.lines[line_name] = quadrants[1].lines[line_name]
                        else:
                            qq.lines[line_name] = self.occ.addLine(qq.points[line.kp1], qq.points[line.kp2])
                            if pt1.y == 0. and pt2.y == 0. and 'x_n' in list_bnds:
                                self.symmetric_bnds['x_n']['line_pnts'].append(line.kp1 + '_' + line.kp2)
                                sym_lines_tags['x_n'].append(qq.lines[line_name])
                    elif quadrant == 4:
                        if pt1.y == 0. and pt2.y == 0.:
                            qq.lines[line_name] = quadrants[1].lines[line_name]
                        else:
                            qq.lines[line_name] = self.occ.addLine(qq.points[line.kp1], qq.points[line.kp2])
                            if pt1.x == 0. and pt2.x == 0. and 'y_n' in list_bnds:
                                self.symmetric_bnds['y_n']['line_pnts'].append(line.kp1 + '_' + line.kp2)
                                sym_lines_tags['y_n'].append(qq.lines[line_name])
                    else:  # 3
                        if pt1.y == 0. and pt2.y == 0.:
                            qq.lines[line_name] = quadrants[2].lines[line_name]
                        elif pt1.x == 0. and pt2.x == 0.:
                            qq.lines[line_name] = quadrants[4].lines[line_name]
                        else:
                            qq.lines[line_name] = self.occ.addLine(qq.points[line.kp1], qq.points[line.kp2])

            elif line.type == 'arc':
                center = Func.arc_center_from_3_points([pt1.x, pt1.y],
                                                       [iron.key_points[line.kp3].x, iron.key_points[line.kp3].y],
                                                       [pt2.x, pt2.y])
                new_point_name = 'kp' + line_name + '_center'
                arc_coordinates1 = (pt1.x, pt1.y)
                arc_coordinates2 = (pt2.x, pt2.y)
                arc_coordinates3 = (iron.key_points[line.kp3].x, iron.key_points[line.kp3].y)

                # This code addresses a meshing error in MQXA and MB_2COILS that occurs when an arc is defined on any of
                # the axes. The issue arises because the function Func.arc_center_from_3_points does not return exactly
                # zero but a value with a magnitude of approximately 10^-17 when the two points are placed on the axes.
                # Consequently, when using the method self.occ.addCircleArc(), which only takes in three points without
                # specifying a direction, a problem arises. The addCircleArc() function always creates the arc with the
                # smallest angle. However, since center point can be slightly above or below the axis, the arc can
                # inadvertently be drawn in the wrong quadrant, leading to an incorrect result.
                # -----------------------
                # Check that arcs with points on the x-axis are drawn in the first quadrant
                if arc_coordinates3[1] > 0 and arc_coordinates2[1] == 0 and arc_coordinates1[1] == 0 and center[1] > 0:
                    quadrants[1].points[new_point_name] = self.occ.addPoint(center[0], -center[1], 0)
                # Check that arcs with points on the y-axis are drawn in the first quadrant
                elif arc_coordinates3[0] > 0 and arc_coordinates2[0] == 0 and arc_coordinates1[0] == 0 and center[0] > 0:
                    quadrants[1].points[new_point_name] = self.occ.addPoint(-center[0], center[1], 0)
                else:
                    quadrants[1].points[new_point_name] = self.occ.addPoint(center[0], center[1], 0)
                # -----------------------
                # gmsh.model.setEntityName(0, gm.iron.quadrants[1].points[new_point_name], 'iron_' + new_point_name)
                if symmetry in ['x', 'none']:
                    if center[0] == 0.:
                        quadrants[2].points[new_point_name] = quadrants[1].points[new_point_name]
                    else:
                        quadrants[2].points[new_point_name] = self.occ.copy([(0, quadrants[1].points[new_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[2].points[new_point_name])], 1, 0, 0, 0)
                if symmetry in ['y', 'none']:
                    if center[1] == 0.:
                        quadrants[4].points[new_point_name] = quadrants[1].points[new_point_name]
                    else:
                        quadrants[4].points[new_point_name] = self.occ.copy([(0, quadrants[1].points[new_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[4].points[new_point_name])], 0, 1, 0, 0)
                if symmetry == 'none':
                    if center[1] == 0.:
                        quadrants[3].points[new_point_name] = quadrants[2].points[new_point_name]
                    else:
                        quadrants[3].points[new_point_name] = self.occ.copy([(0, quadrants[2].points[new_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[3].points[new_point_name])], 0, 1, 0, 0)

                for quadrant, qq in quadrants.items():
                    qq.lines[line_name] = self.occ.addCircleArc(
                        qq.points[line.kp1], qq.points[new_point_name], qq.points[line.kp2])

            elif line.type == 'circle':
                center = [(pt1.x + pt2.x) / 2, (pt1.y + pt2.y) / 2]
                radius = (np.sqrt(np.square(pt1.x - center[0]) + np.square(pt1.y - center[1])) +
                          np.sqrt(np.square(pt2.x - center[0]) + np.square(pt2.y - center[1]))) / 2

                for quadrant, qq in quadrants.items():
                    qq.lines[line_name] = self.occ.addCircle(
                        mirror_x[quadrant - 1] * center[0], mirror_y[quadrant - 1] * center[1], 0, radius)
                    qq.points['kp' + line_name] = len(qq.points) + 1

            elif line.type == 'ellipticArc':
                a, b = line.arg1, line.arg2
                x1, y1 = pt1.x, pt1.y
                x2, y2 = pt2.x, pt2.y
                x3 = np.power(x1, 2.0)
                y3 = np.power(y1, 2.0)
                x4 = np.power(x2, 2.0)
                y4 = np.power(y2, 2.0)
                a2 = np.power(a, 2.0)
                b2 = np.power(b, 2.0)
                expression = -4.0 * a2 * b2 + a2 * y3 - 2.0 * a2 * y1 * y2 + a2 * y4 + b2 * x3 - 2.0 * b2 * x1 * x2 + b2 * x4
                xc = x1 / 2.0 + x2 / 2.0 - a * np.power(- expression / (a2 * y3 - 2.0 * a2 * y1 * y2 + a2 * y4 + b2 * x3 -
                                                                        2.0 * b2 * x1 * x2 + b2 * x4), 0.5) * (y1 - y2) / (2.0 * b)
                yc = y1 / 2.0 + y2 / 2.0 + b * np.power(- expression / (a2 * y3 - 2.0 * a2 * y1 * y2 + a2 * y4 + b2 * x3
                                                                        - 2.0 * b2 * x1 * x2 + b2 * x4), 0.5) * (x1 - x2) / (2.0 * a)

                center = self.occ.addPoint(xc, yc, 0, lc)
                axis_point_a = self.occ.addPoint(xc + a, yc, 0, lc)
                axis_point_b = self.occ.addPoint(xc, yc + b, 0, lc)

                new_point_name = 'kp' + line_name + '_center'
                new_axis_a_point_name = 'kp' + line_name + '_a'
                new_axis_b_point_name = 'kp' + line_name + '_b'

                quadrants[1].points[new_point_name] = center
                quadrants[1].points[new_axis_a_point_name] = axis_point_a
                quadrants[1].points[new_axis_b_point_name] = axis_point_b

                if symmetry in ['x', 'none']:
                    if xc == 0.:  # Least amount of possible points.
                        quadrants[2].points[new_point_name] = quadrants[1].points[new_point_name]
                        quadrants[2].points[new_axis_a_point_name] = quadrants[1].points[new_axis_a_point_name]
                        quadrants[2].points[new_axis_b_point_name] = quadrants[1].points[new_axis_b_point_name]
                    else:
                        quadrants[2].points[new_point_name] = self.occ.copy([(0, quadrants[1].points[new_point_name])])[0][1]
                        quadrants[2].points[new_axis_a_point_name] = self.occ.copy([(0, quadrants[1].points[new_axis_a_point_name])])[0][1]
                        quadrants[2].points[new_axis_b_point_name] = self.occ.copy([(0, quadrants[1].points[new_axis_b_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[2].points[new_point_name])], 1, 0, 0, 0)
                        self.occ.mirror([(0, quadrants[2].points[new_axis_a_point_name])], 1, 0, 0, 0)
                        self.occ.mirror([(0, quadrants[2].points[new_axis_b_point_name])], 1, 0, 0, 0)
                if symmetry in ['y', 'none']:
                    if yc == 0.:
                        quadrants[4].points[new_point_name] = quadrants[1].points[new_point_name]
                        quadrants[4].points[new_axis_a_point_name] = quadrants[1].points[new_axis_a_point_name]
                        quadrants[4].points[new_axis_b_point_name] = quadrants[1].points[new_axis_b_point_name]
                    else:
                        quadrants[4].points[new_point_name] = self.occ.copy([(0, quadrants[1].points[new_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[4].points[new_point_name])], 0, 1, 0, 0)
                        quadrants[4].points[new_axis_a_point_name] = self.occ.copy([(0, quadrants[1].points[new_axis_a_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[4].points[new_axis_a_point_name])], 0, 1, 0, 0)
                        quadrants[4].points[new_axis_b_point_name] = self.occ.copy([(0, quadrants[1].points[new_axis_b_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[4].points[new_axis_b_point_name])], 0, 1, 0, 0)
                if symmetry == 'none':
                    if yc == 0.:
                        quadrants[3].points[new_point_name] = quadrants[2].points[new_point_name]
                        quadrants[3].points[new_axis_a_point_name] = quadrants[2].points[new_axis_a_point_name]
                        quadrants[3].points[new_axis_b_point_name] = quadrants[2].points[new_axis_b_point_name]
                    else:
                        quadrants[3].points[new_point_name] = self.occ.copy([(0, quadrants[2].points[new_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[3].points[new_point_name])], 0, 1, 0, 0)
                        quadrants[3].points[new_axis_a_point_name] = self.occ.copy([(0, quadrants[2].points[new_axis_a_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[3].points[new_axis_a_point_name])], 0, 1, 0, 0)
                        quadrants[3].points[new_axis_b_point_name] = self.occ.copy([(0, quadrants[2].points[new_axis_b_point_name])])[0][1]
                        self.occ.mirror([(0, quadrants[3].points[new_axis_b_point_name])], 0, 1, 0, 0)

                for quadrant, qq in quadrants.items():
                    qq.lines[line_name] = self.occ.addEllipseArc(
                        qq.points[line.kp1], qq.points[new_point_name], qq.points[new_axis_a_point_name if a > b else new_axis_b_point_name],
                        qq.points[line.kp2])

            else:
                raise ValueError('Hyper line {} not supported'.format(line.type))

        if symmetry != 'none':
            indexes = {'x_p': 1, 'y_p': 1, 'x_n': 1, 'y_n': 1}
            self.md.geometries.air_inf.points['center'] = self.occ.addPoint(0, 0, 0)
            for sym in list_bnds:
                if sym in ['x_p', 'y_p']:
                    quadrant = 1
                elif sym == 'x_n':
                    quadrant = 2
                else:  # 'y_n'
                    quadrant = 4
                sym_lines_tags[sym] = [x for _, x in sorted(zip(symmetric_bnds_order[sym[0]], sym_lines_tags[sym]))]

                self.symmetric_bnds[sym]['pnts'].append(['center', 0])
                self.symmetric_bnds[sym]['pnts'].sort(key=lambda x: x[1])
                self.md.geometries.symmetric_boundaries.lines[sym + '_center'] = self.occ.addLine(
                    self.md.geometries.air_inf.points['center'], quadrants[quadrant].points[self.symmetric_bnds[sym]['pnts'][1][0]])
                sym_lines_tags[sym].insert(0, self.md.geometries.symmetric_boundaries.lines[sym + '_center'])
                for i, pnt in enumerate(self.symmetric_bnds[sym]['pnts'][1:-1]):
                    pnt_next = self.symmetric_bnds[sym]['pnts'][i + 2][0]
                    if not any(pnt[0] in s and pnt_next in s for s in self.symmetric_bnds[sym]['line_pnts']):
                        self.md.geometries.symmetric_boundaries.lines[sym + '_' + pnt[0]] =\
                            self.occ.addLine(quadrants[quadrant].points[pnt[0]], quadrants[quadrant].points[pnt_next])
                        sym_lines_tags[sym].insert(indexes[sym], self.md.geometries.symmetric_boundaries.lines[sym + '_' + pnt[0]])
                    indexes[sym] += 1
            if symmetry == 'xy':
                self.symmetric_loop_lines['x'] = sym_lines_tags['x_p']
                sym_lines_tags['y_p'].reverse()
                self.symmetric_loop_lines['y'] = sym_lines_tags['y_p']
            elif symmetry == 'x':
                sym_lines_tags['x_n'].reverse()
                self.symmetric_loop_lines['x'] = sym_lines_tags['x_n'] + sym_lines_tags['x_p']
            elif symmetry == 'y':
                sym_lines_tags['y_p'].reverse()
                self.symmetric_loop_lines['y'] = sym_lines_tags['y_p'] + sym_lines_tags['y_n']

        for quadrant, qq in quadrants.items():
            for area_name, area in iron.hyper_areas.items():
                qq.areas[area_name] = dM.Area(loop=self.occ.addCurveLoop([qq.lines[line] for line in area.lines]))
                if (iron.hyper_areas[area_name].material not in self.md.domains.groups_entities.iron and
                        iron.hyper_areas[area_name].material != 'BH_air'):
                    self.md.domains.groups_entities.iron[iron.hyper_areas[area_name].material] = []

    def constructWedgeGeometry(self, use_TSA):
        """
            Generates points, hyper lines, and curve loops for the wedges
        """
        def _addMidLayerThinShellPoints(wedge_current):
            def __addThinShellPoints(side_case, mid_layer_ts):
                if side_case == 'outer':
                    mean_rad_current = (Func.points_distance([wedge_current.oH.x, wedge_current.oH.y], wedge_center) +
                                        Func.points_distance([wedge_current.oL.x, wedge_current.oL.y], wedge_center)) / 2
                else:
                    mean_rad_current = (Func.points_distance([wedge_current.iH.x, wedge_current.iH.y], wedge_center) +
                                        Func.points_distance([wedge_current.iL.x, wedge_current.iL.y], wedge_center)) / 2
                are_endpoints = {}
                for wnd_nr, wnd in pole.layers[wedge.order_l.layer + (1 if side_case == 'outer' else -1)].windings.items():
                    blk_nr_next = list(wnd.blocks.keys())[blk_list_current.index(wedge.order_l.block)]
                    blk_next = wnd.blocks[blk_nr_next]
                    ht_list_next = (list(blk_next.half_turns.keys()) if blk_nr_next == list(wnd.blocks.keys())[0] else list(
                        reversed(blk_next.half_turns.keys())))
                    hh = blk_next.half_turns[ht_list_next[-1]].corners.bare
                    ll = blk_next.half_turns[ht_list_next[0]].corners.bare
                    bc_next = Corner(oH=hh.oH, iH=hh.iH, oL=ll.oL, iL=ll.iL)
                    if side_case == 'outer':
                        block_list = self.md.geometries.coil.anticlockwise_order.coils[wedge.order_l.coil].layers[wedge.order_l.layer + 1]
                        blk_index = [blk.block for blk in block_list].index(blk_nr_next)
                        if blk_index + 1 == len(block_list): blk_index = -1
                        for blk in block_list[blk_index + 1:] + block_list[:blk_index + 1]:
                            if blk.winding == block_list[blk_index].winding:
                                ht_index = -1
                                break
                            elif blk.pole != block_list[blk_index].pole:
                                ht_index = 0
                                break
                        hh = blk_next.half_turns[ht_list_next[ht_index]].corners.bare
                        ll = blk_next.half_turns[ht_list_next[0 if ht_index == -1 else -1]].corners.bare
                        mean_rad_next = (Func.points_distance([hh.iH.x, hh.iH.y], wedge_center) +
                                         Func.points_distance([ll.iL.x, ll.iL.y], wedge_center)) / 2
                    else:
                        mean_rad_next = (Func.points_distance([bc_next.oH.x, bc_next.oH.y], wedge_center) +
                                         Func.points_distance([bc_next.oL.x, bc_next.oL.y], wedge_center)) / 2
                    mean_rad = (mean_rad_current + mean_rad_next) / 2
                    mid_layer = self.findMidLayerPoint(wedge_current.oH, bc_next.iH, wedge.corrected_center.outer, mean_rad)\
                        if side_case == 'outer' else self.findMidLayerPoint(wedge_current.iH, bc_next.oH, wedge.corrected_center.inner, mean_rad)
                    are_endpoints[wnd_nr] = self.getMidLayerEndpoints(wedge_current, bc_next, wedge_center, mid_layer_arc_pnt=mid_layer)
                for wnd_nr, wnd in pole.layers[wedge.order_l.layer + (1 if side_case == 'outer' else -1)].windings.items():
                    blk_nr_next = list(wnd.blocks.keys())[blk_list_current.index(wedge.order_l.block)]
                    blk_next = wnd.blocks[blk_nr_next]
                    is_first_blk_next = blk_nr_next == list(wnd.blocks.keys())[0]
                    ht_list_next = (list(blk_next.half_turns.keys()) if is_first_blk_next else list(
                        reversed(blk_next.half_turns.keys())))
                    if are_endpoints[wnd_nr]:  # this is empty if the wedge and the block are not radially adjacent
                        endpoints = are_endpoints[wnd_nr][0]
                        which_entity = are_endpoints[wnd_nr][1]
                        mid_layer_name = 'w' + str(wedge_nr) + '_' + str(blk_nr_next)
                        mid_layer_ts[mid_layer_name] = dM.Region()
                        ts_wdg = mid_layer_ts[mid_layer_name]
                        beg = ('w' + str(wedge_nr) if which_entity['lower'] == 'current' else str(ht_list_next[0])) + 'l'
                        ts_wdg.points[beg] = self.occ.addPoint(endpoints['lower'][0], endpoints['lower'][1], 0)
                        ht_lower_angles = {}
                        for ht_nr, ht in (blk_next.half_turns.items() if is_first_blk_next else reversed(blk_next.half_turns.items())):
                            for pnt1, pnt2, side in zip([[ht.corners.bare.iL.x, ht.corners.bare.iL.y], [ht.corners.bare.iH.x, ht.corners.bare.iH.y]],
                                                        [[ht.corners.bare.oL.x, ht.corners.bare.oL.y], [ht.corners.bare.oH.x, ht.corners.bare.oH.y]],
                                                        ['l', 'h']):
                                line_pars_current = Func.line_through_two_points(pnt1, pnt2)
                                intersect_prev = Func.intersection_between_arc_and_line(
                                    line_pars_current, [wedge_center, endpoints['higher'], endpoints['lower']])
                                if intersect_prev:
                                    ts_wdg.points[str(ht_nr) + side] = self.occ.addPoint(intersect_prev[0][0], intersect_prev[0][1], 0)
                                elif side == 'l':
                                    intrsc = Func.intersection_between_circle_and_line(line_pars_current, [wedge_center, endpoints['lower']], get_only_closest=True)[0]
                                    ht_lower_angles[ht_nr] = Func.arc_angle_between_point_and_abscissa([intrsc[0], intrsc[1]], wedge_center)
                        end = ('w' + str(wedge_nr) if which_entity['higher'] == 'current' else str(ht_list_next[-1])) + 'h'
                        if all('w' in pnt_name for pnt_name in list(ts_wdg.points.keys())):  # only one thin-shell 'within' the facing half-turn
                            wdg_angle_il = Func.arc_angle_between_point_and_abscissa([endpoints['lower'][0], endpoints['lower'][1]], wedge_center)
                            for ht_nr, ht in (blk_next.half_turns.items() if is_first_blk_next else reversed(blk_next.half_turns.items())):
                                if ht_lower_angles[ht_nr] > wdg_angle_il: break
                                prev_nr = str(ht_nr)
                            end = prev_nr + 'h'
                        ts_wdg.points[end] = self.occ.addPoint(endpoints['higher'][0], endpoints['higher'][1], 0)

                        # Create auxiliary thin shells for outliers
                        # if both corners belong to thin shells, continue
                        used_wdg_corners = [False, False]
                        for ep in are_endpoints.values():
                            if ep is not None:
                                if ep[1]['higher'] == 'current': used_wdg_corners[1] = True
                                if ep[1]['lower'] == 'current': used_wdg_corners[0] = True
                        if side_case == 'inner':
                            for ts_name in self.md.geometries.thin_shells.mid_layers_wdg_to_wdg.keys():
                                if ts_name[ts_name.index('_') + 1:] == 'w' + str(wedge_nr):
                                    for ep_key, ep in are_endpoints_wdg[int(ts_name[1:ts_name.index('_')])].items():
                                        if ep is not None:
                                            if ep[1]['higher'] == 'next': used_wdg_corners[1] = True
                                            if ep[1]['lower'] == 'next': used_wdg_corners[0] = True
                        else:
                            if wedge_nr in are_endpoints_wdg:
                                for ep in are_endpoints_wdg[wedge_nr].values():
                                    if ep is not None:
                                        if ep[1]['higher'] == 'current': used_wdg_corners[1] = True
                                        if ep[1]['lower'] == 'current': used_wdg_corners[0] = True
                        if not used_wdg_corners[1]:
                            for wdg_nr, wdg in self.geom.wedges.items():
                                if blk_nr_next == wdg.order_l.block: used_wdg_corners[1] = True
                        if not used_wdg_corners[0]:
                            for wdg_nr, wdg in self.geom.wedges.items():
                                if blk_nr_next == wdg.order_h.block: used_wdg_corners[0] = True
                        if not all(used_wdg_corners):
                            def ___create_aux_mid_layer_point(ss, points):
                                mid_layer_ts_aux[mid_layer_name] = dM.Region()
                                circle_pnt = [endpoints[ss][0], endpoints[ss][1]]
                                inter_pnt = Func.intersection_between_circle_and_line(Func.line_through_two_points(points[0], points[1]),
                                    [[wedge.corrected_center.outer.x, wedge.corrected_center.outer.y], circle_pnt], get_only_closest=True)[0]
                                mid_layer_ts_aux[mid_layer_name].points[str(wedge_nr) + ss[0]] = self.occ.addPoint(inter_pnt[0], inter_pnt[1], 0)
                                mid_layer_ts_aux[mid_layer_name].points['center'] = self.occ.addPoint(wedge_data[wedge_nr][1].x, wedge_data[wedge_nr][1].y, 0)
                                mid_layer_ts_aux[mid_layer_name].lines['w' + str(wedge_nr)] = 0
                            if which_entity['higher'] == 'current' and which_entity['lower'] != 'current':
                                ___create_aux_mid_layer_point('lower', [[wedge_current.iL.x, wedge_current.iL.y],
                                                                        [wedge_current.oL.x, wedge_current.oL.y]])
                            elif which_entity['higher'] != 'current' and which_entity['lower'] == 'current':
                                ___create_aux_mid_layer_point('higher', [[wedge_current.iH.x, wedge_current.iH.y],
                                                                         [wedge_current.oH.x, wedge_current.oH.y]])
                            else:  # whole block 'within' the facing wedge
                                for wdg_nr, wdg in self.geom.wedges.items():
                                    if blk_nr_next == wdg.order_h.block:
                                        ___create_aux_mid_layer_point('higher', [[wedge_current.iH.x, wedge_current.iH.y],
                                                                                 [wedge_current.oH.x, wedge_current.oH.y]])
                                        break
                                    elif blk_nr_next == wdg.order_l.block:
                                        ___create_aux_mid_layer_point('lower', [[wedge_current.iL.x, wedge_current.iL.y],
                                                                                [wedge_current.oL.x, wedge_current.oL.y]])
                                        break

            pole = self.geom.coil.coils[wedge.order_l.coil].poles[wedge.order_l.pole]
            blk_list_current = list(pole.layers[wedge.order_l.layer].windings[wedge.order_l.winding].blocks.keys())
            if wedge.order_l.layer < len(pole.layers):
                __addThinShellPoints('outer', self.md.geometries.thin_shells.mid_layers_wdg_to_ht)
            if wedge.order_l.layer > 1:
                __addThinShellPoints('inner', self.md.geometries.thin_shells.mid_layers_ht_to_wdg)

        wedges = self.md.geometries.wedges
        mid_layer_ts_aux = self.md.geometries.thin_shells.mid_layers_aux
        wedge_data = {}

        wdgs_corners = {}
        for wedge_nr, wedge in self.geom.wedges.items():
            wdgs_corners[wedge_nr] = {}
            corners = wdgs_corners[wedge_nr]
            if wedge.order_l.coil not in wedges.coils:
                wedges.coils[wedge.order_l.coil] = dM.WedgeLayer()
            if wedge.order_l.layer not in wedges.coils[wedge.order_l.coil].layers:
                wedges.coils[wedge.order_l.coil].layers[wedge.order_l.layer] = dM.WedgeRegion()
            wedge_layer = wedges.coils[wedge.order_l.coil].layers[wedge.order_l.layer]
            wedge_layer.wedges[wedge_nr] = dM.Region()
            wedge_reg = wedge_layer.wedges[wedge_nr]
            wedge_layer.block_prev[wedge_nr] = wedge.order_l.block
            wedge_layer.block_next[wedge_nr] = wedge.order_h.block
            wnd = self.geom.coil.coils[wedge.order_l.coil].poles[wedge.order_l.pole].layers[
                wedge.order_l.layer].windings[wedge.order_l.winding]
            wnd_next = self.geom.coil.coils[wedge.order_h.coil].poles[wedge.order_h.pole].layers[
                wedge.order_h.layer].windings[wedge.order_h.winding]
            block = wnd.blocks[wedge.order_l.block]
            block_next = wnd_next.blocks[wedge.order_h.block]
            corners['last_ht'] = int(list(self.md.geometries.coil.coils[wedge.order_l.coil].poles[wedge.order_l.pole].layers[
                                              wedge.order_l.layer].windings[wedge.order_l.winding].blocks[wedge.order_l.block].half_turns.areas.keys())[-1])
            corners['first_ht'] = int(list(self.md.geometries.coil.coils[wedge.order_h.coil].poles[wedge.order_h.pole].layers[
                                               wedge.order_h.layer].windings[wedge.order_h.winding].blocks[wedge.order_h.block].half_turns.areas.keys())[0])
            ht_current = block.half_turns[corners['last_ht']].corners.bare
            ht_next = block_next.half_turns[corners['first_ht']].corners.bare
            d_current = self.data.conductors[wnd.conductor_name].cable.th_insulation_along_width * 2
            d_next = self.data.conductors[wnd_next.conductor_name].cable.th_insulation_along_width * 2
            for pnt_close, pnt_far, wdg_corner, d in zip([ht_current.iH, ht_current.oH, ht_next.iL, ht_next.oL],
                                                         [ht_current.iL, ht_current.oL, ht_next.iH, ht_next.oH],
                                                         ['il', 'ol', 'ih', 'oh'], [d_current, d_current, d_next, d_next]):
                if abs(pnt_far.x - pnt_close.x) > 0.:
                    m = (pnt_far.y - pnt_close.y) / (pnt_far.x - pnt_close.x)
                    b = pnt_close.y - m * pnt_close.x
                    root = np.sqrt(- pnt_close.x ** 2 * m ** 2 - 2 * pnt_close.x * b * m + 2 * pnt_close.x * pnt_close.y * m
                                   - b ** 2 + 2 * b * pnt_close.y - pnt_close.y ** 2 + d ** 2 * m ** 2 + d ** 2)
                    pnt1_x = (pnt_close.x - b * m + pnt_close.y * m + root) / (m ** 2 + 1)
                    pnt1_y = m * pnt1_x + b
                    pnt2_x = (pnt_close.x - b * m + pnt_close.y * m - root) / (m ** 2 + 1)
                    pnt2_y = m * pnt2_x + b
                    corners[wdg_corner] = Coord(x=pnt1_x, y=pnt1_y) if Func.points_distance([pnt1_x, pnt1_y], [pnt_far.x, pnt_far.y]) >\
                        Func.points_distance([pnt_close.x, pnt_close.y], [pnt_far.x, pnt_far.y]) else Coord(x=pnt2_x, y=pnt2_y)
                else:
                    bore_cnt_x = self.geom.coil.coils[wedge.order_l.coil].bore_center.x
                    pnt1_y, pnt2_y = pnt_close.y + d, pnt_close.y - d
                    corners[wdg_corner] = Coord(x=pnt_close.x,
                                                y=pnt1_y if (wdg_corner[-1] == 'l' and pnt_close.x > bore_cnt_x) or
                                                            (wdg_corner[-1] == 'h' and pnt_close.x < bore_cnt_x) else pnt2_y)
                wedge_reg.points[wdg_corner] = self.occ.addPoint(corners[wdg_corner].x, corners[wdg_corner].y, 0)
            inner = Func.corrected_arc_center([self.md.geometries.coil.coils[wedge.order_l.coil].bore_center.x,
                                               self.md.geometries.coil.coils[wedge.order_l.coil].bore_center.y],
                                              [corners['ih'].x, corners['ih'].y], [corners['il'].x, corners['il'].y])
            outer = Func.corrected_arc_center([self.md.geometries.coil.coils[wedge.order_l.coil].bore_center.x,
                                               self.md.geometries.coil.coils[wedge.order_l.coil].bore_center.y],
                                              [corners['oh'].x, corners['oh'].y], [corners['ol'].x, corners['ol'].y])
            wedge_data[wedge_nr] = [Corner(iH=corners['ih'], oH=corners['oh'], iL=corners['il'], oL=corners['ol']), wedge.corrected_center.outer]
            wedge_reg.points['inner_center'] = self.occ.addPoint(inner[0], inner[1], 0)
            wedge_reg.points['outer_center'] = self.occ.addPoint(outer[0], outer[1], 0)
            wedge_reg.lines['h'] = self.occ.addLine(wedge_reg.points['ih'], wedge_reg.points['oh'])
            wedge_reg.lines['l'] = self.occ.addLine(wedge_reg.points['il'], wedge_reg.points['ol'])
            wedge_reg.lines['i'] = self.occ.addCircleArc(wedge_reg.points['ih'], wedge_reg.points['inner_center'], wedge_reg.points['il'])
            wedge_reg.lines['o'] = self.occ.addCircleArc(wedge_reg.points['oh'], wedge_reg.points['outer_center'], wedge_reg.points['ol'])
            wedge_reg.areas[str(wedge_nr)] = dM.Area(loop=self.occ.addCurveLoop(
                [wedge_reg.lines['i'], wedge_reg.lines['l'], wedge_reg.lines['o'], wedge_reg.lines['h']]))

        if use_TSA:
            # Wedge thin shells
            mid_layer_ts = self.md.geometries.thin_shells.mid_layers_wdg_to_wdg
            are_endpoints_wdg = {}
            for coil_nr, coil in self.md.geometries.wedges.coils.items():
                layer_list = list(coil.layers.keys())
                for layer_nr, layer in coil.layers.items():
                    if layer_list.index(layer_nr) + 1 < len(layer_list):
                        for wedge_nr, wedge in layer.wedges.items():
                            are_endpoints_wdg[wedge_nr] = {}
                            are_endpoints = are_endpoints_wdg[wedge_nr]
                            wedge_current = wedge_data[wedge_nr][0]
                            wedge_center = [wedge_data[wedge_nr][1].x, wedge_data[wedge_nr][1].y]
                            mean_rad_current = (Func.points_distance([wedge_current.oH.x, wedge_current.oH.y], wedge_center) +
                                                Func.points_distance([wedge_current.oL.x, wedge_current.oL.y], wedge_center)) / 2
                            for wdg_next_nr, wdg_next in coil.layers[layer_nr + 1].wedges.items():
                                if self.geom.wedges[wedge_nr].order_l.pole == self.geom.wedges[wdg_next_nr].order_l.pole:
                                    wedge_next = wedge_data[wdg_next_nr][0]
                                    mean_rad_next = (Func.points_distance([wedge_next.iH.x, wedge_next.iH.y], wedge_center) +
                                                     Func.points_distance([wedge_next.iL.x, wedge_next.iL.y], wedge_center)) / 2
                                    mean_rad = (mean_rad_current + mean_rad_next) / 2
                                    mid_layer = self.findMidLayerPoint(wedge_current.oH, wedge_next.iH, wedge_data[wedge_nr][1], mean_rad)
                                    are_endpoints[wdg_next_nr] = self.getMidLayerEndpoints(wedge_current, wedge_next, wedge_center, mid_layer_arc_pnt=mid_layer)
                                    if are_endpoints[wdg_next_nr]:  # this is empty if the wedges are not radially adjacent
                                        endpoints = are_endpoints[wdg_next_nr][0]
                                        mid_layer_name = 'w' + str(wedge_nr) + '_w' + str(wdg_next_nr)
                                        mid_layer_ts[mid_layer_name] = dM.Region()
                                        ts = mid_layer_ts[mid_layer_name]
                                        ts.points['center'] = self.occ.addPoint(wedge_center[0], wedge_center[1], 0)
                                        ts.points['beg'] = self.occ.addPoint(endpoints['lower'][0], endpoints['lower'][1], 0)
                                        end = 'w' + str(wedge_nr if are_endpoints[wdg_next_nr][1] == 'current' else wdg_next_nr)
                                        ts.points[end] = self.occ.addPoint(endpoints['higher'][0], endpoints['higher'][1], 0)

            # Half-turn thin shells
            for wedge_nr, wedge in self.geom.wedges.items():
                corners = wdgs_corners[wedge_nr]
                # Mid layer lines
                wedge_center = [self.md.geometries.coil.coils[wedge.order_l.coil].bore_center.x,
                                self.md.geometries.coil.coils[wedge.order_l.coil].bore_center.y]
                _addMidLayerThinShellPoints(Corner(iH=corners['ih'], oH=corners['oh'], iL=corners['il'], oL=corners['ol']))
                # Mid wedge-turn lines
                mid_turn_ts = self.md.geometries.thin_shells.mid_wedge_turn
                for adj_blk, ht, inner, outer in zip([wedge.order_l, wedge.order_h], [corners['last_ht'], corners['first_ht']],
                                                     [corners['il'], corners['ih']], [corners['ol'], corners['oh']]):
                    mid_turn_ts['w' + str(wedge_nr) + '_' + str(adj_blk.block)] = dM.Region()
                    ts = mid_turn_ts['w' + str(wedge_nr) + '_' + str(adj_blk.block)]
                    ht_corners = self.geom.coil.coils[adj_blk.coil].poles[adj_blk.pole].layers[
                        adj_blk.layer].windings[adj_blk.winding].blocks[adj_blk.block].half_turns[ht].corners.bare
                    ht_corners_i = ht_corners.iH if ht == corners['last_ht'] else ht_corners.iL
                    ht_corners_o = ht_corners.oH if ht == corners['last_ht'] else ht_corners.oL
                    mid_inner = [(inner.x + ht_corners_i.x) / 2, (inner.y + ht_corners_i.y) / 2]
                    mid_outer = [(outer.x + ht_corners_o.x) / 2, (outer.y + ht_corners_o.y) / 2]
                    line_name = 'w' + str(wedge_nr) + '_' + str(ht)
                    ts.points[line_name + '_i'] = self.occ.addPoint(mid_inner[0], mid_inner[1], 0)
                    ts.points[line_name + '_o'] = self.occ.addPoint(mid_outer[0], mid_outer[1], 0)

    def constructCoilGeometry(self, run_type):
        """
            Generates points, hyper lines, and curve loops for the coil half-turns
        """
        symmetry = self.data.magnet.geometry.electromagnetics.symmetry if run_type == 'EM' else 'none'
        # Sub domains angles: first key means 'from 0 to x'; second key means 'from x to 2*pi'
        if symmetry == 'xy':
            angle_range = {'to': np.pi / 2, 'from': 2 * np.pi}
        elif symmetry == 'x':
            angle_range = {'to': np.pi, 'from': 2 * np.pi}
        elif symmetry == 'y':
            angle_range = {'to': np.pi / 2, 'from': 3 / 2 * np.pi}
        elif symmetry == 'none':
            angle_range = {'to': 2 * np.pi, 'from': 0}
        else:
            raise Exception('Symmetry plane not supported.')

        def _addMidLayerThinShellPoints(pnt_params, ss, name, case):
            endpnts, cnt = ts_endpoints[name]
            if len(pnt_params) == 3:  # line parameters (cos-theta Rutherford)
                intersect[name] = Func.intersection_between_arc_and_line(pnt_params, [cnt, endpnts['higher'], endpnts['lower']])
                if intersect[name]:
                    intersect[name] = intersect[name][0]
                    pnt_angle = Func.arc_angle_between_point_and_abscissa(intersect[name], cnt)
            elif len(pnt_params) == 4:  # points coordinates (cos-theta Mono)
                wnd_next = list(pole.layers[layer_nr + (1 if case == 'current' else -1)].windings.keys())[
                    list(pole.layers[layer_nr].windings.keys()).index(winding_nr)]
                blk_next = pole.layers[layer_nr + (1 if case == 'current' else -1)].windings[wnd_next].blocks[
                    int(ts_name[ts_name.index('_') + 1:] if case == 'current' else ts_name[:ts_name.index('_')])]
                ht_next = blk_next.half_turns[list(blk_next.half_turns.keys() if is_first_blk else reversed(blk_next.half_turns.keys()))[ht_list.index(halfTurn_nr)]].corners.bare
                coord_next = (ht_next.iL if ss == 'l' else ht_next.iH) if case == 'current' else (ht_next.oL if ss == 'l' else ht_next.oH)
                pnt = [(pnt_params[2 if case == 'current' else 0] + coord_next.x) / 2, (pnt_params[3 if case == 'current' else 1] + coord_next.y) / 2]
                pnt_angle = Func.arc_angle_between_point_and_abscissa(pnt, cnt)
                pnt_angle_h = Func.arc_angle_between_point_and_abscissa(endpnts['higher'], cnt)
                pnt_angle_l = Func.arc_angle_between_point_and_abscissa(endpnts['lower'], cnt)
                intersect[name] = pnt if pnt_angle_h > pnt_angle > pnt_angle_l else None
            else:  # point coordinates (block-coil)
                pnt = [endpnts['higher'][0], pnt_params[1]] if coil.type == 'common-block-coil' else [pnt_params[0], endpnts['higher'][1]]
                if abs(endpnts['higher'][1]) > 1e-6:
                    pnt_angle = Func.arc_angle_between_point_and_abscissa(pnt, cnt)
                    pnt_angle_h = Func.arc_angle_between_point_and_abscissa(endpnts['higher'], cnt)
                    pnt_angle_l = Func.arc_angle_between_point_and_abscissa(endpnts['lower'], cnt)
                else:
                    pnt_angle = abs(pnt_params[0])
                    pnt_angle_h = abs(endpnts['higher'][0])
                    pnt_angle_l = abs(endpnts['lower'][0])
                intersect[name] = pnt if pnt_angle_h > pnt_angle > pnt_angle_l else None
            if intersect[name]:
                mid_layer_ts[name].mid_layers.points[str(halfTurn_nr) + ss] = \
                    self.occ.addPoint(intersect[name][0], intersect[name][1], 0)
                mid_layer_ts[name].point_angles[str(halfTurn_nr) + ss] = Func.sig_dig(pnt_angle)
            if len(pnt_params) == 2 and not intersect[name] and (abs(pnt_angle - pnt_angle_h) < 1e-6 or abs(pnt_angle - pnt_angle_l) < 1e-6):
                intersect[name] = pnt
            return intersect

        def _addMidLayerThinShellGroup(cl, for_mid_pole=False, mid_coil=False):
            is_first_blk_next = block_nr_next == list(winding_next.blocks.keys())[0]
            if 'solenoid' in cl.type:
                ht_list_next = list(reversed(block_next.half_turns.keys()) if layer_nr % 2 == 0 else list(block_next.half_turns.keys()))
            elif cl.type == 'reversed-block-coil':
                ht_list_next = (list(block_next.half_turns.keys()) if not is_first_blk_next else list(reversed(block_next.half_turns.keys())))
            else:
                ht_list_next = (list(block_next.half_turns.keys()) if is_first_blk_next else list(reversed(block_next.half_turns.keys())))
            hh = block_next.half_turns[ht_list_next[-1]].corners.bare
            ll = block_next.half_turns[ht_list_next[0]].corners.bare
            bc_next = Corner(oH=hh.oH, iH=hh.iH, oL=ll.oL, iL=ll.iL)
            if 'block-coil' in cl.type or (cable_type_curr in ['Mono', 'Ribbon'] and not mid_coil):
                center = [cl.bore_center.x, cl.bore_center.y]
                are_endpoints = self.getMidLayerEndpoints(bc_current, bc_next, center, coil_type=cl.type, cable_type=cable_type_curr, is_for_mid_pole=for_mid_pole)
            else:
                mean_rad_next = (Func.points_distance([bc_next.iH.x, bc_next.iH.y], [cl.bore_center.x, cl.bore_center.y]) +
                                 Func.points_distance([bc_next.iL.x, bc_next.iL.y], [cl.bore_center.x, cl.bore_center.y])) / 2
                mean_rad = (mean_rad_current + mean_rad_next) / 2
                mid_layer_h = self.findMidLayerPoint(bc_current.oH, bc_next.iH, cl.bore_center, mean_rad)
                mid_layer_l = self.findMidLayerPoint(bc_current.oL, bc_next.iL, cl.bore_center, mean_rad)
                mid_ht_next_i = int(len(ht_list_next) / 2) if len(ht_list_next) % 2 == 0 else round(len(ht_list_next) / 2)
                mid_ht_next = block_next.half_turns[ht_list_next[mid_ht_next_i - 1]].corners.insulated
                mid_layer_m = self.findMidLayerPoint(mid_ht_current.oH, mid_ht_next.iH, cl.bore_center, mean_rad)
                center = Func.arc_center_from_3_points(mid_layer_h, mid_layer_m, mid_layer_l)
                are_endpoints = self.getMidLayerEndpoints(bc_current, bc_next, center, mid_layer_arc_pnt=mid_layer_h, cable_type=cable_type_curr)
            if are_endpoints:  # this is empty if the blocks are not radially adjacent
                endpoints = are_endpoints[0]
                which_block = are_endpoints[1]
                mid_layer_name = blk_nr + '_' + str(block_nr_next)
                if for_mid_pole:
                    block_coil_mid_pole_next_blks_list[block_nr_next].append(mid_layer_name)
                    block_coil_ts_endpoints[mid_layer_name] = [endpoints, center]
                else:
                    if block_nr_next not in list(next_blks_list.keys()):
                        next_blks_list[block_nr_next] = []
                    next_blks_list[block_nr_next].append(mid_layer_name)
                    ts_endpoints[mid_layer_name] = [endpoints, center]
                mid_layer_ts[mid_layer_name] = dM.MidLayer()
                mid_layer_ts[mid_layer_name].half_turn_lists[blk_nr] = ht_list
                mid_layer_ts[mid_layer_name].half_turn_lists[str(block_nr_next)] = ht_list_next
                beg = (str(ht_list[0]) if which_block['lower'] == 'current' else str(ht_list_next[0])) + 'l'
                mid_layer_ts[mid_layer_name].mid_layers.points[beg] = \
                    self.occ.addPoint(endpoints['lower'][0], endpoints['lower'][1], 0)
                end = (str(ht_list[-1]) if which_block['higher'] == 'current' else str(ht_list_next[-1])) + 'h'
                mid_layer_ts[mid_layer_name].mid_layers.points[end] = \
                    self.occ.addPoint(endpoints['higher'][0], endpoints['higher'][1], 0)
                if not for_mid_pole or (for_mid_pole and abs(endpoints['higher'][1]) > 1e-6):
                    mid_layer_ts[mid_layer_name].point_angles[beg] =\
                        Func.sig_dig(Func.arc_angle_between_point_and_abscissa(endpoints['lower'], center))
                    mid_layer_ts[mid_layer_name].point_angles[end] =\
                        Func.sig_dig(Func.arc_angle_between_point_and_abscissa(endpoints['higher'], center))
                else:
                    mid_layer_ts[mid_layer_name].point_angles[beg] = abs(endpoints['lower'][0])
                    mid_layer_ts[mid_layer_name].point_angles[end] = abs(endpoints['higher'][0])

        # Create anticlockwise order of blocks
        present_blocks = []
        block_corner_angles = {}
        concentric_coils = self.md.geometries.coil.concentric_coils
        acw_order = self.md.geometries.coil.anticlockwise_order.coils
        self.md.geometries.coil.physical_order = self.geom.coil.physical_order
        for coil_nr, coil in self.geom.coil.coils.items():
            # if coil_nr not in block_corner_angles:
            block_corner_angles[coil_nr] = {}
            if (coil.bore_center.x, coil.bore_center.y) not in concentric_coils:
                concentric_coils[(coil.bore_center.x, coil.bore_center.y)] = []
            concentric_coils[(coil.bore_center.x, coil.bore_center.y)].append(coil_nr)
            for pole_nr, pole in coil.poles.items():
                for layer_nr, layer in pole.layers.items():
                    if layer_nr not in block_corner_angles[coil_nr]:
                        block_corner_angles[coil_nr][layer_nr] = {}
                    blk_angles = block_corner_angles[coil_nr][layer_nr]
                    for winding_nr, winding in layer.windings.items():
                        for block_nr, block in winding.blocks.items():
                            blk_angles[block_nr] = {'angle': Func.sig_dig(Func.arc_angle_between_point_and_abscissa(
                                [block.block_corners.iL.x, block.block_corners.iL.y],
                                [coil.bore_center.x, coil.bore_center.y])), 'keys': [pole_nr, winding_nr]}
                            higher_angle = Func.sig_dig(Func.arc_angle_between_point_and_abscissa(
                                [block.block_corners.iH.x, block.block_corners.iH.y],
                                [coil.bore_center.x, coil.bore_center.y]))
                            if ((blk_angles[block_nr]['angle'] <= angle_range['to'] and higher_angle <= angle_range['to']) or
                                    (angle_range['from'] <= blk_angles[block_nr]['angle'] and angle_range['from'] <= higher_angle)):
                                present_blocks.append(block_nr)
        for coil_nr, coil in block_corner_angles.items():
            acw_order[coil_nr] = dM.LayerOrder()
            for layer_nr, layer in coil.items():
                acw_order[coil_nr].layers[layer_nr] = []
                ordered_blocks = [[block_nr, block['angle'], block['keys']] for block_nr, block in layer.items()]
                ordered_blocks.sort(key=lambda x: x[1])
                for blk in ordered_blocks:
                    if blk[0] in present_blocks:
                        acw_order[coil_nr].layers[layer_nr].append(dM.AnticlockwiseOrder(pole=blk[2][0], winding=blk[2][1], block=blk[0]))

        # Check if there are concentric coils
        for bore_center, coils in concentric_coils.items():
            if len(coils) > 1:
                radii = []
                for coil_nr in coils:
                    lyr = self.geom.coil.coils[coil_nr].poles[1].layers[1]
                    blk = list(lyr.windings.keys())[0]
                    radii.append([coil_nr, Func.points_distance(bore_center, [lyr.windings[blk].blocks[blk].block_corners.iL.x, lyr.windings[blk].blocks[blk].block_corners.iL.y])])
                radii.sort(key=lambda x: x[1])
                concentric_coils[bore_center] = [rad[0] for rad in radii]

        if run_type == 'TH' and self.data.magnet.geometry.thermal.use_TSA:
            mid_layer_ts = self.md.geometries.thin_shells.mid_layers_ht_to_ht
            # Collect block couples for block-coil mid-pole thin shells
            block_coil_mid_pole_next_blks_list = {}
            block_coil_ts_endpoints = {}
            for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items():
                if self.geom.coil.coils[coil_nr].type in ['block-coil', 'reversed-block-coil']:
                    self.block_coil_mid_pole_blks[coil_nr] = []
                    first_lyr = list(coil.layers.keys())[0]
                    layer = coil.layers[first_lyr]
                    for nr, block_order in enumerate(layer):
                        blk_next_index = nr + 1 if nr + 1 < len(layer) else 0
                        if layer[blk_next_index].pole != block_order.pole:
                            self.block_coil_mid_pole_blks[coil_nr].append([block_order, layer[blk_next_index]])
                            block_coil_mid_pole_next_blks_list[layer[blk_next_index].block] = []
            # Mid pole lines for block-coils
            for coil_nr, coil in self.block_coil_mid_pole_blks.items():
                coil_geom = self.geom.coil.coils[coil_nr]
                for mid_pole in coil:
                    winding = self.geom.coil.coils[coil_nr].poles[mid_pole[0].pole].layers[1].windings[mid_pole[0].winding]
                    cable_type_curr = self.data.conductors[winding.conductor_name].cable.type
                    block_nr = mid_pole[0].block
                    blk_nr = str(block_nr)
                    block = winding.blocks[block_nr]
                    is_first_blk = block_nr == list(winding.blocks.keys())[0]
                    if coil_geom.type == 'reversed-block-coil':
                        ht_list = (list(block.half_turns.keys()) if not is_first_blk else list(reversed(block.half_turns.keys())))
                    else:
                        ht_list = (list(block.half_turns.keys()) if is_first_blk else list(reversed(block.half_turns.keys())))
                    hh = block.half_turns[ht_list[-1]].corners.bare
                    ll = block.half_turns[ht_list[0]].corners.bare
                    bc_current = Corner(oH=hh.oH, iH=hh.iH, oL=ll.oL, iL=ll.iL)
                    winding_next = self.geom.coil.coils[coil_nr].poles[mid_pole[1].pole].layers[1].windings[mid_pole[1].winding]
                    block_nr_next = mid_pole[1].block
                    block_next = winding_next.blocks[block_nr_next]
                    _addMidLayerThinShellGroup(coil_geom, for_mid_pole=True)

        mid_layer_ts_aux = self.md.geometries.thin_shells.mid_layers_aux
        self.md.geometries.coil.physical_order = self.geom.coil.physical_order
        if run_type == 'TH' and self.data.magnet.geometry.thermal.use_TSA:
            next_blks_list = block_coil_mid_pole_next_blks_list.copy()
            ts_endpoints = block_coil_ts_endpoints.copy()
        for coil_nr, coil in self.geom.coil.coils.items():
            self.md.geometries.coil.coils[coil_nr] = dM.Pole()
            coils = self.md.geometries.coil.coils[coil_nr]
            coils.type = coil.type
            coils.bore_center = coil.bore_center
            for pole_nr, pole in coil.poles.items():
                coils.poles[pole_nr] = dM.Layer()
                poles = coils.poles[pole_nr]
                for layer_nr, layer in pole.layers.items():
                    poles.layers[layer_nr] = dM.Winding()
                    layers = poles.layers[layer_nr]
                    for winding_nr, winding in layer.windings.items():
                        cable_type_curr = self.data.conductors[winding.conductor_name].cable.type
                        layers.windings[winding_nr] = dM.Block(conductor_name=winding.conductor_name, conductors_number=winding.conductors_number)
                        windings = layers.windings[winding_nr]
                        blk_list_current = list(winding.blocks.keys())
                        for block_nr, block in winding.blocks.items():
                            if block_nr in present_blocks:
                                blk_nr = str(block_nr)
                                windings.blocks[block_nr] = dM.BlockData(current_sign=block.current_sign)
                                hts = windings.blocks[block_nr].half_turns
                                is_first_blk = block_nr == list(winding.blocks.keys())[0]
                                if run_type == 'TH' and self.data.magnet.geometry.thermal.use_TSA:
                                    if 'solenoid' in coil.type:
                                        ht_list = (list(reversed(block.half_turns.keys()) if (layer_nr - 1) % 2 == 0 else list(block.half_turns.keys())))
                                    elif coil.type == 'reversed-block-coil':
                                        ht_list = (list(block.half_turns.keys()) if not is_first_blk else list(reversed(block.half_turns.keys())))
                                    else:
                                        ht_list = (list(block.half_turns.keys()) if is_first_blk else list(reversed(block.half_turns.keys())))
                                    hh = block.half_turns[ht_list[-1]].corners.bare
                                    ll = block.half_turns[ht_list[0]].corners.bare
                                    bc_current = Corner(oH=hh.oH, iH=hh.iH, oL=ll.oL, iL=ll.iL)
                                    # Mid layer lines
                                    mean_rad_current = (Func.points_distance([bc_current.oH.x, bc_current.oH.y], [coil.bore_center.x, coil.bore_center.y]) +
                                                        Func.points_distance([bc_current.oL.x, bc_current.oL.y], [coil.bore_center.x, coil.bore_center.y])) / 2
                                    mid_ht_current_i = int(len(ht_list) / 2) if len(ht_list) % 2 == 0 else round(len(ht_list) / 2)
                                    mid_ht_current = block.half_turns[ht_list[mid_ht_current_i - 1]].corners.insulated
                                    concentric_coil = concentric_coils[(coil.bore_center.x, coil.bore_center.y)]
                                    if layer_nr < len(pole.layers):
                                        for winding_nr_next, winding_next in pole.layers[layer_nr + 1].windings.items():
                                            if cable_type_curr == 'Rutherford' or\
                                                    (cable_type_curr in ['Mono', 'Ribbon'] and
                                                     list(pole.layers[layer_nr + 1].windings.keys()).index(winding_nr_next) == list(layer.windings.keys()).index(winding_nr)):
                                                blk_list_next = list(winding_next.blocks.keys())
                                                block_nr_next = blk_list_next[blk_list_current.index(block_nr)]
                                                block_next = winding_next.blocks[block_nr_next]
                                                _addMidLayerThinShellGroup(coil)
                                    elif concentric_coil.index(coil_nr) + 1 < len(concentric_coil):
                                        coil_nr_next = concentric_coil[concentric_coil.index(coil_nr) + 1]
                                        for pole_nr_next, pole_next in self.geom.coil.coils[coil_nr_next].poles.items():
                                            for layer_nr_next, layer_next in pole_next.layers.items():
                                                if layer_nr_next == 1:
                                                    for winding_nr_next, winding_next in layer_next.windings.items():
                                                        for block_nr_next, block_next in winding_next.blocks.items():
                                                            _addMidLayerThinShellGroup(coil, mid_coil=True)
                                else:
                                    blk_ins = windings.blocks[block_nr].insulation
                                    blk_ins.areas[blk_nr] = dM.Area()

                                if 'solenoid' in coil.type:
                                    ht_items = (list(reversed(block.half_turns.items()) if layer_nr - 1 % 2 == 0 else list(block.half_turns.items())))
                                elif coil.type == 'reversed-block-coil':
                                    ht_items = (block.half_turns.items() if not is_first_blk else reversed(block.half_turns.items()))
                                else:
                                    ht_items = (block.half_turns.items() if is_first_blk else reversed(block.half_turns.items()))
                                for halfTurn_nr, halfTurn in ht_items:
                                    ht_nr = str(halfTurn_nr)
                                    ht = halfTurn.corners.insulated
                                    hts.areas[ht_nr] = dM.Area()
                                    ht_b = halfTurn.corners.bare

                                    hts.points[ht_nr + 'ih'] = self.occ.addPoint(ht_b.iH.x, ht_b.iH.y, 0)
                                    hts.points[ht_nr + 'il'] = self.occ.addPoint(ht_b.iL.x, ht_b.iL.y, 0)
                                    hts.points[ht_nr + 'oh'] = self.occ.addPoint(ht_b.oH.x, ht_b.oH.y, 0)
                                    hts.points[ht_nr + 'ol'] = self.occ.addPoint(ht_b.oL.x, ht_b.oL.y, 0)

                                    hts.lines[ht_nr + 'i'] = self.occ.addLine(hts.points[ht_nr + 'ih'], hts.points[ht_nr + 'il'])
                                    hts.lines[ht_nr + 'o'] = self.occ.addLine(hts.points[ht_nr + 'oh'], hts.points[ht_nr + 'ol'])
                                    hts.lines[ht_nr + 'l'] = self.occ.addLine(hts.points[ht_nr + 'il'], hts.points[ht_nr + 'ol'])
                                    hts.lines[ht_nr + 'h'] = self.occ.addLine(hts.points[ht_nr + 'ih'], hts.points[ht_nr + 'oh'])

                                    if run_type == 'TH' and self.data.magnet.geometry.thermal.use_TSA:
                                        intersection = {}
                                        # Create mid layer points and compute their angle to the x-axis
                                        for mid_lyr_type in ['current', 'previous']:
                                            for pnt1, pnt2, side in zip(
                                                    [[ht_b.iH.x, ht_b.iH.y], [ht_b.iL.x, ht_b.iL.y]],
                                                    [[ht_b.oH.x, ht_b.oH.y], [ht_b.oL.x, ht_b.oL.y]], ['h', 'l']):
                                                if (cable_type_curr in ['Mono', 'Ribbon'] and coil.type == 'cos-theta' and
                                                        (layer_nr < len(pole.layers) and mid_lyr_type == 'current' or layer_nr > 1 and mid_lyr_type == 'previous')):
                                                    pnts_input = pnt1 + pnt2
                                                elif coil.type == 'cos-theta' and (cable_type_curr == 'Rutherford' or cable_type_curr in ['Mono', 'Ribbon'] and\
                                                        (layer_nr == len(pole.layers) and mid_lyr_type == 'current' or layer_nr == 1 and mid_lyr_type == 'previous')):
                                                    pnts_input = Func.line_through_two_points(pnt1, pnt2)
                                                elif 'block-coil' in coil.type:
                                                    pnts_input = pnt1
                                                intersect = {}
                                                if mid_lyr_type == 'current':
                                                    # Current mid-layer
                                                    for ts_name in ts_endpoints.keys():
                                                        if blk_nr == ts_name[:ts_name.index('_')]:
                                                            _addMidLayerThinShellPoints(pnts_input, side, ts_name, mid_lyr_type)
                                                elif mid_lyr_type == 'previous':
                                                    # Previous mid-layer
                                                    if block_nr in next_blks_list:
                                                        for ts_name in next_blks_list[block_nr]:
                                                            _addMidLayerThinShellPoints(pnts_input, side, ts_name, mid_lyr_type)
                                                for key, value in intersect.items():
                                                    if key in intersection:
                                                        intersection[key][side] = value
                                                    else:
                                                        intersection[key] = {side: value}

                                        # Search for half turns that face thin shells only partially
                                        def __create_aux_mid_layer_point(ss, points):
                                            mid_layer_ts_aux[key] = dM.Region()
                                            if 'block-coil' in coil.type:
                                                inter_pnt = [points[0], ts_endpoints[key][0][ss][1]]
                                            else:
                                                inter_pnt = Func.intersection_between_circle_and_line(Func.line_through_two_points(points[0], points[1]),
                                                    [ts_endpoints[key][1], ts_endpoints[key][0][ss]], get_only_closest=True)[0]
                                            mid_layer_ts_aux[key].points[str(halfTurn_nr) + ss[0]] = self.occ.addPoint(inter_pnt[0], inter_pnt[1], 0)
                                            mid_layer_ts_aux[key].lines[blk_nr] = 0
                                        for key, value in intersection.items():
                                            first_blk, second_blk = key.split('_')
                                            if 'block-coil' in coil.type: #any(int(second_blk) == blk_order.block for blk_order in acw_order[coil_nr].layers[layer_nr]):  # block-coil mid-pole case
                                                if value['h'] and not value['l']:
                                                    __create_aux_mid_layer_point('lower', [ht_b.iL.x, ht_b.iL.y])
                                                elif value['l'] and not value['h']:
                                                    __create_aux_mid_layer_point('higher', [ht_b.iH.x, ht_b.iH.y])
                                            else:
                                                relevant_blk = int(first_blk) if second_blk == blk_nr else int(second_blk)
                                                if layer_nr == len(pole.layers) and blk_nr == first_blk:
                                                    lyr_blks = acw_order[coil_nr + 1].layers[1]
                                                elif layer_nr == 1 and blk_nr == second_blk:
                                                    lyr_blks = acw_order[coil_nr - 1].layers[len(acw_order[coil_nr - 1].layers)]
                                                else:
                                                    lyr_blks = acw_order[coil_nr].layers[layer_nr + (1 if first_blk == blk_nr else -1)]
                                                for nr, block_order in enumerate(lyr_blks):
                                                    if block_order.block == relevant_blk:
                                                        block_order_curr = block_order
                                                        block_order_prev = lyr_blks[-1] if nr == 0 else lyr_blks[nr - 1]
                                                        block_order_next = lyr_blks[0] if nr + 1 == len(lyr_blks) else lyr_blks[nr + 1]
                                                        break
                                                if value['h'] and not value['l'] and block_order_curr.winding == block_order_prev.winding:
                                                    __create_aux_mid_layer_point('lower', [[ht_b.iL.x, ht_b.iL.y], [ht_b.oL.x, ht_b.oL.y]])
                                                elif value['l'] and not value['h'] and block_order_curr.winding == block_order_next.winding:
                                                    __create_aux_mid_layer_point('higher', [[ht_b.iH.x, ht_b.iH.y], [ht_b.oH.x, ht_b.oH.y]])
                                    else:
                                        blk_ins.points[ht_nr + 'ih'] = self.occ.addPoint(ht.iH.x, ht.iH.y, 0)
                                        blk_ins.points[ht_nr + 'il'] = self.occ.addPoint(ht.iL.x, ht.iL.y, 0)
                                        blk_ins.points[ht_nr + 'oh'] = self.occ.addPoint(ht.oH.x, ht.oH.y, 0)
                                        blk_ins.points[ht_nr + 'ol'] = self.occ.addPoint(ht.oL.x, ht.oL.y, 0)

                                    hts.areas[ht_nr].loop = self.occ.addCurveLoop(
                                        [hts.lines[ht_nr + 'i'],  # inner
                                         hts.lines[ht_nr + 'l'],  # lower
                                         hts.lines[ht_nr + 'o'],  # outer
                                         hts.lines[ht_nr + 'h']])  # higher

                                # Build wire order of the insulation lines of the current block
                                if run_type == 'TH' and not self.data.magnet.geometry.thermal.use_TSA:
                                    ht_list = list(hts.areas.keys())
                                    ht_list.extend(list(reversed(ht_list))[1:])
                                    self.blk_ins_lines[block_nr] = ['l']
                                    for nr, ht_nr in enumerate(ht_list):
                                        if nr + 1 == winding.conductors_number:  # end of first round
                                            self.blk_ins_lines[block_nr].extend([ht_nr + 'i', 'h', ht_nr + 'o'])
                                        else:
                                            if nr + 1 < winding.conductors_number:  # within first round
                                                self.blk_ins_lines[block_nr].extend([ht_nr + 'i', ht_nr + 'i' + ht_list[nr + 1]])
                                            else:  # within second round
                                                self.blk_ins_lines[block_nr].extend([ht_nr + 'o' + ht_list[nr - 1], ht_nr + 'o'])

    def constructInsulationGeometry(self):
        """
            Generates points, hyper lines, and curve loops for the coil insulations
        """
        def _createMidPoleLines(case, cnt=0):
            if 'block-coil' in geom_coil.type:
                if case == 'inner':
                    group.lines['mid_pole_' + case[0]] = self.occ.addLine(ins_pnt[first_ht_curr + case[0] + 'l'], ins_pnt_opposite[last_ht_prev + case[0] + 'h'])
                    ordered_lines[group_nr].append(['mid_pole_' + case[0], (len(coil.layers) * 2) * 1e3 + 5e2, group.lines['mid_pole_' + case[0]]])
                else:
                    group.lines['mid_pole_' + case[0]] = self.occ.addLine(ins_pnt[last_ht_curr + 'ih'], ins_pnt_opposite[first_ht_prev + 'il'])
                    ordered_lines[group_nr].append(['mid_pole_' + case[0], 0, group.lines['mid_pole_' + case[0]]])
            else:
                ht_curr = geom_coil.poles[block_order.pole].layers[layer_nr].windings[block_order.winding].blocks[
                    block_order.block].half_turns[int(first_ht_curr)].corners.insulated
                ht_prev = geom_coil.poles[block_order_prev.pole].layers[layer_nr].windings[block_order_prev.winding].blocks[
                    block_order_prev.block].half_turns[int(last_ht_prev)].corners.insulated
                pnt_curr = [ht_curr.iL.x, ht_curr.iL.y] if case == 'inner' else [ht_curr.oL.x, ht_curr.oL.y]
                pnt_prev = [ht_prev.iH.x, ht_prev.iH.y] if case == 'inner' else [ht_prev.oH.x, ht_prev.oH.y]
                if Func.points_distance(pnt_curr, pnt_prev) > 1e-6:
                    correct_center = Func.corrected_arc_center([self.md.geometries.coil.coils[coil_nr].bore_center.x, self.md.geometries.coil.coils[coil_nr].bore_center.y],
                                                               [ht_curr.iL.x, ht_curr.iL.y] if case == 'inner' else [ht_curr.oL.x, ht_curr.oL.y],
                                                               [ht_prev.iH.x, ht_prev.iH.y] if case == 'inner' else [ht_prev.oH.x, ht_prev.oH.y])
                    ln_name = 'mid_pole_' + str(block_order_prev.block) + '_' + str(block_order.block) + '_' + case[0]
                    group.lines[ln_name] = self.occ.addCircleArc(ins_pnt[first_ht_curr + case[0] + 'l'],
                                                                 self.occ.addPoint(correct_center[0], correct_center[1], 0),
                                                                 ins_pnt_opposite[last_ht_prev + case[0] + 'h'])
                    # self.occ.addLine(ins_pnt[first_ht_curr + case[0] + 'l'], ins_pnt_opposite[last_ht_prev + case[0] + 'h'])
                    cnt += 1 if case == 'inner' else -1
                    ordered_lines[group_nr].append([ln_name, cnt, group.lines[ln_name]])
                return cnt

        def _createMidWindingLines(case, cnt):
            name = 'mid_wind_' + str(block_order_prev.block) + '_' + str(block_order.block) + '_' + case[0]
            # Create corrected center
            blk1 = self.geom.coil.coils[coil_nr].poles[blks_info[str(block_order.block)][0]].layers[
                blks_info[str(block_order.block)][1]].windings[blks_info[str(block_order.block)][2]].blocks[int(str(block_order.block))]
            blk2 = self.geom.coil.coils[coil_nr].poles[blks_info[str(block_order_prev.block)][0]].layers[
                blks_info[str(block_order_prev.block)][1]].windings[blks_info[str(block_order_prev.block)][2]].blocks[int(block_order_prev.block)]
            pnt1 = blk1.half_turns[int(first_ht_curr)].corners.insulated.iL if case == 'inner' else blk1.half_turns[int(first_ht_curr)].corners.insulated.oL
            pnt2 = blk2.half_turns[int(last_ht_prev)].corners.insulated.iH if case == 'inner' else blk2.half_turns[int(last_ht_prev)].corners.insulated.oH
            outer_center = Func.corrected_arc_center([self.md.geometries.coil.coils[coil_nr].bore_center.x,
                                                      self.md.geometries.coil.coils[coil_nr].bore_center.y],
                                                     [pnt1.x, pnt1.y], [pnt2.x, pnt2.y])
            group.lines[name] = self.occ.addCircleArc(ins_pnt[first_ht_curr + case[0] + 'l'],
                                                      self.occ.addPoint(outer_center[0], outer_center[1], 0), ins_pnt_opposite[last_ht_prev + case[0] + 'h'])
            cnt += 1 if case == 'inner' else -1
            ordered_lines[group_nr].append([name, cnt, group.lines[name]])
            return cnt

        def _createInnerOuterLines(case, cnt):
            # Create half turn lines
            idxs = [1, round(len(self.blk_ins_lines[block_order.block]) / 2), 1] if case == 'inner'\
                else [len(self.blk_ins_lines[block_order.block]) - 1, round(len(self.blk_ins_lines[block_order.block]) / 2), -1]
            lns = self.blk_ins_lines[block_order.block][idxs[0]:idxs[1]:idxs[2]]
            for ln_nr, ln_name in enumerate(lns):
                skip_cnt = False
                if ln_name[-1].isdigit():
                    try:
                        group.lines[ln_name] = self.occ.addLine(ins_pnt[ln_name[:ln_name.index(case[0])] + case[0] + 'h'],
                                                                ins_pnt[ln_name[ln_name.index(case[0]) + 1:] + case[0] + 'l'])
                    except:
                        skip_cnt = True
                        next_line = lns[ln_nr + 1]
                        pos = 'first' if next_line[:-1] == ln_name[:ln_name.index(case[0])] else 'second'
                        lns[ln_nr + 1] = next_line + (ln_name[ln_name.index(case[0]) + 1:] + 'l' if pos == 'first' else ln_name[:ln_name.index(case[0])] + 'h')
                elif ln_name[-1] in ['i', 'o']:
                    group.lines[ln_name] = self.occ.addLine(ins_pnt[ln_name + 'l'], ins_pnt[ln_name + 'h'])
                else:
                    group.lines[ln_name] = self.occ.addLine(ins_pnt[ln_name[:ln_name.index(case[0])] + case[0] + ln_name[-1]],
                                                            ins_pnt[ln_name[ln_name.index(case[0]) + 1:-1] + case[0] + ln_name[-1]])
                if not skip_cnt:
                    cnt += 1 if case == 'inner' else -1
                    ordered_lines[group_nr].append([ln_name, cnt, group.lines[ln_name]])
            return cnt

        def _computePointAngle(case):
            points_angles = pa_next if case == 'outer' else pa_prev
            current_ht_h = [current_ht.oH.x, current_ht.oH.y] if case == 'outer' else [current_ht.iH.x, current_ht.iH.y]
            if ht_nr == 0:
                current_ht_l = [current_ht.oL.x, current_ht.oL.y] if case == 'outer' else [current_ht.iL.x, current_ht.iL.y]
                if 'block-coil' in geom_coil.type: current_ht_l[1] = 1 if current_ht_l[1] > 0 else -1
                points_angles[str(block_order.block) + '_' + ht_name + 'l'] = Func.arc_angle_between_point_and_abscissa(current_ht_l, center)
            if ht_nr == len(ht_list) - 1:
                name = ht_name + 'h'
                coord = current_ht_h
            else:  # for mid half turns, get the outer corner
                next_ht_ins = geom_hts[int(ht_list[ht_nr + 1])].corners.insulated
                next_ht = [next_ht_ins.oL.x, next_ht_ins.oL.y] if case == 'outer' else [next_ht_ins.iL.x, next_ht_ins.iL.y]
                condition = (Func.points_distance(current_ht_h, center) > Func.points_distance(next_ht, center))\
                    if case == 'outer' else (Func.points_distance(current_ht_h, center) < Func.points_distance(next_ht, center))
                if condition:
                    name = ht_name + 'h'
                    coord = current_ht_h
                else:
                    name = ht_list[ht_nr + 1] + 'l'
                    coord = next_ht
            if 'block-coil' in geom_coil.type: coord[1] = 1 if coord[1] > 0 else -1
            points_angles[str(block_order.block) + '_' + name] = Func.arc_angle_between_point_and_abscissa(coord, center)

        ins = self.md.geometries.insulation
        for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items():
            aux_coil = self.md.geometries.coil.coils[coil_nr]
            geom_coil = self.geom.coil.coils[coil_nr]
            groups = len(geom_coil.poles)
            count = {}
            ordered_lines = {}
            points_angle = {}
            blks_info = {}
            ending_line = {}
            center = [geom_coil.bore_center.x, geom_coil.bore_center.y]
            if coil_nr not in ins.coils:
                ins.coils[coil_nr] = dM.InsulationGroup()
            ins_groups = ins.coils[coil_nr].group
            for layer_nr, layer in coil.layers.items():
                group_nr = 1
                wnd_nr = len(aux_coil.poles[1].layers[layer_nr].windings)
                ordered_layer = layer[wnd_nr:] + layer[:wnd_nr] if layer[0].pole != layer[-1].pole else layer
                for nr, block_order in enumerate(ordered_layer):
                    blks_info[str(block_order.block)] = [block_order.pole, layer_nr, block_order.winding]
                    # Get previous block in anticlockwise order
                    block_order_prev = ordered_layer[-1] if nr == 0 else ordered_layer[nr - 1]
                    # Update insulation group
                    if block_order.winding == block_order_prev.winding:
                        group_nr = group_nr + 1 if group_nr < groups else 1
                    # Initialize dicts
                    if group_nr not in ins_groups:
                        ins_groups[group_nr] = dM.InsulationRegion()
                        points_angle[group_nr] = {}
                        ordered_lines[group_nr] = []
                        count[group_nr] = [0, (len(coil.layers) + 1) * 1e3]
                    group = ins_groups[group_nr].ins
                    ins_groups[group_nr].blocks.append([block_order.pole, layer_nr, block_order.winding, block_order.block])
                    # Find the wedge
                    if block_order.pole == block_order_prev.pole and block_order.winding != block_order_prev.winding:
                        for wdg, blk in self.md.geometries.wedges.coils[coil_nr].layers[layer_nr].block_prev.items():
                            if blk == block_order_prev.block:
                                ins_groups[group_nr].wedges.append([layer_nr, wdg])
                                break
                    if layer_nr < len(coil.layers):
                        mid_layer_next = str(layer_nr) + '_' + str(layer_nr + 1)
                        if mid_layer_next not in points_angle[group_nr]:
                            points_angle[group_nr][mid_layer_next] = {}
                        pa_next = points_angle[group_nr][mid_layer_next]
                    if layer_nr > 1:
                        mid_layer_prev = str(layer_nr - 1) + '_' + str(layer_nr)
                        pa_prev = points_angle[group_nr][mid_layer_prev]
                    # Get point tags of insulation
                    ins_pnt = aux_coil.poles[block_order.pole].layers[layer_nr].windings[block_order.winding].blocks[
                        block_order.block].insulation.points
                    # Get relevant info for line names
                    first_ht_curr = self.blk_ins_lines[block_order.block][1][:-1]
                    last_ht_prev = list(aux_coil.poles[block_order_prev.pole].layers[
                        layer_nr].windings[block_order_prev.winding].blocks[block_order_prev.block].half_turns.areas.keys())[-1]
                    ins_pnt_opposite = aux_coil.poles[block_order_prev.pole].layers[
                        layer_nr].windings[block_order_prev.winding].blocks[block_order_prev.block].insulation.points
                    if 'cos-theta' == geom_coil.type:
                        # Create lower and higher angle lines
                        if block_order.winding == block_order_prev.winding:
                            group.lines[str(layer_nr) + 'l'] = self.occ.addLine(ins_pnt[first_ht_curr + 'il'], ins_pnt[first_ht_curr + 'ol'])
                            ordered_lines[group_nr].append([str(layer_nr) + 'l', (len(coil.layers) * 2 - layer_nr + 1) * 1e3, group.lines[str(layer_nr) + 'l']])
                            ending_line[group_nr - 1 if group_nr > 1 else groups] =\
                                [ins_pnt_opposite[last_ht_prev + 'ih'], ins_pnt_opposite[last_ht_prev + 'oh']]
                        # Create inner lines of insulation group
                        if layer_nr == 1:
                            if block_order.pole != block_order_prev.pole:
                                count[group_nr][0] = _createMidPoleLines('inner', count[group_nr][0])
                            if block_order.pole == block_order_prev.pole and block_order.winding != block_order_prev.winding:
                                count[group_nr][0] = _createMidWindingLines('inner', count[group_nr][0])
                            count[group_nr][0] = _createInnerOuterLines('inner', count[group_nr][0])
                        # Create outer lines of insulation group
                        if layer_nr == len(coil.layers):
                            if block_order.pole != block_order_prev.pole:
                                count[group_nr][1] = _createMidPoleLines('outer', count[group_nr][1])
                            if block_order.pole == block_order_prev.pole and block_order.winding != block_order_prev.winding:
                                count[group_nr][1] = _createMidWindingLines('outer', count[group_nr][1])
                            count[group_nr][1] = _createInnerOuterLines('outer', count[group_nr][1])
                    elif 'block-coil' in geom_coil.type:
                        last_ht_curr = self.blk_ins_lines[block_order.block][self.blk_ins_lines[block_order.block].index('h') - 1][:-1]
                        first_ht_prev = list(aux_coil.poles[block_order_prev.pole].layers[layer_nr].windings[
                                                 block_order_prev.winding].blocks[block_order_prev.block].half_turns.areas.keys())[0]
                        # Create lower and higher angle lines
                        if block_order.winding == block_order_prev.winding:
                            group.lines[str(layer_nr) + 'l'] = self.occ.addLine(ins_pnt[first_ht_curr + 'il'], ins_pnt[first_ht_curr + 'ol'])
                            ordered_lines[group_nr].append([str(layer_nr) + 'l', (len(coil.layers) * 4 - layer_nr + 1) * 1e3, group.lines[str(layer_nr) + 'l']])
                            ending_line[group_nr - 1 if group_nr > 1 else groups] =\
                                [ins_pnt_opposite[last_ht_prev + 'ih'], ins_pnt_opposite[last_ht_prev + 'oh']]
                            group.lines[str(layer_nr) + 'bh'] = self.occ.addLine(ins_pnt[last_ht_curr + 'ih'], ins_pnt[last_ht_curr + 'oh'])
                            ordered_lines[group_nr].append([str(layer_nr) + 'bh', (len(coil.layers) * 2 + layer_nr) * 1e3, group.lines[str(layer_nr) + 'bh']])
                        # Create inner lines of insulation group
                        if block_order.pole != block_order_prev.pole:
                            if layer_nr == 1:
                                _createMidPoleLines('inner')
                                _createMidPoleLines('outer')
                            group.lines[str(layer_nr) + 'bl'] = self.occ.addLine(ins_pnt[first_ht_curr + 'il'], ins_pnt[first_ht_curr + 'ol'])
                            ordered_lines[group_nr].append([str(layer_nr) + 'bl', (len(coil.layers) * 2 - layer_nr + 1) * 1e3, group.lines[str(layer_nr) + 'bl']])
                        # Create outer lines of insulation group
                        if layer_nr == len(coil.layers):
                            count[group_nr][1] = _createInnerOuterLines(
                                'outer', (len(coil.layers) * 4 - layer_nr + 1) * 1e3 if block_order.winding == block_order_prev.winding else (len(coil.layers) + 1) * 1e3)
                    # Store info about the angle of each point in between layers
                    ht_list = list(aux_coil.poles[block_order.pole].layers[
                        layer_nr].windings[block_order.winding].blocks[block_order.block].half_turns.areas.keys())
                    geom_hts = geom_coil.poles[block_order.pole].layers[
                        layer_nr].windings[block_order.winding].blocks[block_order.block].half_turns
                    for ht_nr, ht_name in enumerate(ht_list):  # half turns in anticlockwise order
                        current_ht = geom_hts[int(ht_name)].corners.insulated
                        if layer_nr < len(coil.layers):  # if it's not the last layer, fetch all outer corners angles
                            _computePointAngle('outer')
                        if layer_nr > 1:  # if it's not the first layer, fetch all inner corners angles
                            _computePointAngle('inner')
                # Create closing lines
                for grp_nr, grp in ending_line.items():
                    ins_groups[grp_nr].ins.lines[str(layer_nr) + 'h'] = self.occ.addLine(grp[0], grp[1])
                    ordered_lines[grp_nr].append([str(layer_nr) + 'h', layer_nr * 1e3, ins_groups[grp_nr].ins.lines[str(layer_nr) + 'h']])
            # Create lines connecting different layers and generate closed loops
            for group_nr, group in points_angle.items():
                ins_group = ins_groups[group_nr].ins
                for mid_l_name, mid_l in group.items():
                    first_layer = mid_l_name[:mid_l_name.index('_')]
                    # Correct angles if the group crosses the abscissa
                    max_angle = max(mid_l.values())
                    max_diff = max_angle - min(mid_l.values())
                    if max_diff > np.pi:
                        for pnt_name, angle in mid_l.items():
                            if angle < max_diff / 2:
                                mid_l[pnt_name] = angle + max_angle
                    # Order points according to angle
                    ordered_pnts = [[pnt_name, angle] for pnt_name, angle in mid_l.items()]
                    ordered_pnts.sort(key=lambda x: x[1])
                    ordered_names = [x[0] for x in ordered_pnts]
                    for case in ['beg', 'end']:
                        past_blocks = []
                        sides = ['l', 'o', 'h', 'l'] if case == 'beg' else ['h', 'i', 'l', 'h']
                        # count = int(first_layer) * 1e3 + 5e2 if case == 'end' else (len(coil.layers) * 2 - int(first_layer)) * 1e3 + 5e2
                        for i in range(2 if 'block-coil' in geom_coil.type else 1):
                            count = int(first_layer) * 1e3 + 5e2 if i == 0 else (len(coil.layers) * 2 + int(first_layer)) * 1e3 + 5e2
                            if case == 'beg':
                                pnt_position = 0 if i == 0 else int(len(ordered_names) / 2)
                            else:
                                pnt_position = -1 if i == 0 else int(len(ordered_names) / 2 - 1)
                            first_block = ordered_names[pnt_position][:ordered_names[pnt_position].index('_')]  # ordered_pnts[pnt_position][0][:ordered_pnts[pnt_position][0].index('_')] #
                            ordered_search_names = ordered_names[pnt_position::1 if case == 'beg' else -1]
                            for nr, pnt in enumerate(ordered_search_names[1:], 1):  # enumerate(ordered_names if case == 'beg' else reversed(ordered_names)):  #
                                current_blk = pnt[:pnt.index('_')]
                                ins_pnt = aux_coil.poles[blks_info[current_blk][0]].layers[blks_info[current_blk][1]].windings[
                                    blks_info[current_blk][2]].blocks[int(current_blk)].insulation.points
                                prev_pnt = ordered_search_names[nr - 1]  # ordered_pnts[nr - 1 if case == 'beg' else - nr][0] #
                                prev_blk = prev_pnt[:prev_pnt.index('_')]
                                start_pnt_name = prev_pnt[prev_pnt.index('_') + 1:-1] + ('o' if str(blks_info[prev_blk][1]) == first_layer else 'i')
                                ins_pnt_prev = aux_coil.poles[blks_info[prev_blk][0]].layers[blks_info[prev_blk][1]].windings[
                                    blks_info[prev_blk][2]].blocks[int(prev_blk)].insulation.points
                                # Create lines when you find the first edge belonging to a block of the opposite layer
                                if blks_info[current_blk][1] != blks_info[first_block][1]:
                                    pnt_tag_name = pnt[pnt.index('_') + 1:-1] + ('o' if str(blks_info[current_blk][1]) == first_layer else 'i') + ('l' if pnt[-1] == 'l' else 'h')
                                    pnt_tag_name_opposite = start_pnt_name + ('l' if prev_pnt[-1] == 'l' else 'h')
                                    opp_blk_ins_lines = self.blk_ins_lines[int(prev_blk)]
                                    indexes = [opp_blk_ins_lines.index(start_pnt_name) + (1 if prev_pnt[-1] == sides[0] else 0),
                                               len(opp_blk_ins_lines) if case == 'beg' else opp_blk_ins_lines.index('h'), 1] if start_pnt_name[-1] == sides[1]\
                                        else [opp_blk_ins_lines.index(start_pnt_name) - (1 if prev_pnt[-1] == sides[0] else 0),
                                              0 if case == 'beg' else opp_blk_ins_lines.index('h'), -1]
                                    if case == 'beg':
                                        if i == 0:
                                            count = (len(coil.layers) * (4 if 'block-coil' in geom_coil.type else 2) - int(first_layer)) * 1e3 + 5e2 - abs(indexes[0] - indexes[1])
                                        else:
                                            count = (len(coil.layers) * 2 - int(first_layer)) * 1e3 + 5e2 - abs(indexes[0] - indexes[1])
                                    else:
                                        count += 1 + abs(indexes[0] - indexes[1])
                                    # Create all remaining lines of the current layer block
                                    for line_name in opp_blk_ins_lines[indexes[0]:indexes[1]:indexes[2]]:
                                        if 'block-coil' in geom_coil.type:
                                            if not line_name[-1].isdigit():
                                                ins_group.lines[line_name] = self.occ.addLine(ins_pnt_prev[line_name + 'l'], ins_pnt_prev[line_name + 'h'])
                                                count += 1 if (case == 'beg' and i == 1) or (case == 'end' and i == 0) else -1
                                                ordered_lines[group_nr].append([line_name, count, ins_group.lines[line_name]])
                                        else:
                                            if line_name[-1].isdigit():
                                                ins_group.lines[line_name] = self.occ.addLine(
                                                    ins_pnt_prev[line_name[:line_name.index(start_pnt_name[-1])] + start_pnt_name[-1] + 'h'],
                                                    ins_pnt_prev[line_name[line_name.index(start_pnt_name[-1]) + 1:] + start_pnt_name[-1] + 'l'])
                                            else:
                                                ins_group.lines[line_name] = self.occ.addLine(ins_pnt_prev[line_name + 'l'], ins_pnt_prev[line_name + 'h'])
                                            count += 1 if case == 'beg' else -1  # if start_pnt_name[-1] == sides[1] else 1
                                            ordered_lines[group_nr].append([line_name, count, ins_group.lines[line_name]])
                                    # Create mid layer line
                                    if 'block-coil' in geom_coil.type:
                                        count_rest = -abs(indexes[0] - indexes[1]) if (case == 'beg' and i == 1) or (case == 'end' and i == 0) else 1 + abs(indexes[0] - indexes[1])
                                    else:
                                        count_rest = -abs(indexes[0] - indexes[1]) if case == 'beg' else 1 + abs(indexes[0] - indexes[1])
                                    line_name = 'mid_layer_' + mid_l_name + ('b' if i == 1 else '') + ('_l' if case == 'beg' else '_h')
                                    ins_group.lines[line_name] = self.occ.addLine(ins_pnt[pnt_tag_name], ins_pnt_prev[pnt_tag_name_opposite])
                                    ordered_lines[group_nr].append([line_name, count + count_rest, ins_group.lines[line_name]])
                                    break
                                # Create all edges of the first block sticking out completely todo: might have to be extended to multiple blocks
                                if current_blk != first_block and current_blk not in past_blocks:
                                    def __createWedgeInsulation(cnt):
                                        # Create the line connecting the blocks (where a wedge is)
                                        line_name = self.blk_ins_lines[int(current_blk)][
                                            (-1 if start_pnt_name[-1] == 'o' else 1) if case == 'beg'
                                            else (round(len(self.blk_ins_lines[int(current_blk)]) / 2) + (1 if start_pnt_name[-1] == 'o' else -1))]
                                        line_name_prev = self.blk_ins_lines[int(prev_blk)][
                                            (round(len(self.blk_ins_lines[int(prev_blk)]) / 2) + (1 if start_pnt_name[-1] == 'o' else -1)) if case == 'beg'
                                            else (-1 if start_pnt_name[-1] == 'o' else 1)]
                                        # Create corrected center
                                        blk1 = geom_coil.poles[blks_info[prev_blk][0]].layers[
                                            blks_info[prev_blk][1]].windings[blks_info[prev_blk][2]].blocks[int(prev_blk)]
                                        blk2 = geom_coil.poles[blks_info[current_blk][0]].layers[
                                            blks_info[current_blk][1]].windings[blks_info[current_blk][2]].blocks[int(current_blk)]
                                        pnt1 = blk1.half_turns[int(line_name_prev[:-1])].corners.insulated.oH if case == 'beg'\
                                            else blk1.half_turns[int(line_name_prev[:-1])].corners.insulated.oL
                                        pnt2 = blk2.half_turns[int(line_name[:-1])].corners.insulated.oL if case == 'beg'\
                                            else blk2.half_turns[int(line_name[:-1])].corners.insulated.oH
                                        outer_center = Func.corrected_arc_center([aux_coil.bore_center.x, aux_coil.bore_center.y],
                                                                                 [pnt2.x, pnt2.y] if case == 'beg' else [pnt1.x, pnt1.y],
                                                                                 [pnt1.x, pnt1.y] if case == 'beg' else [pnt2.x, pnt2.y])
                                        ins_group.lines[line_name_prev + line_name] =\
                                            self.occ.addCircleArc(ins_pnt_prev[line_name_prev + sides[2]],
                                                                  self.occ.addPoint(outer_center[0], outer_center[1], 0), ins_pnt[line_name + sides[3]])
                                        ordered_lines[group_nr].append([line_name_prev + line_name, cnt, ins_group.lines[line_name_prev + line_name]])

                                    count = int(first_layer) * 1e3 + 5e2 if case == 'end' else (len(coil.layers) * 2 - int(first_layer)) * 1e3 + 5e2
                                    past_blocks.append(current_blk)
                                    indexes = [round(len(self.blk_ins_lines[int(prev_blk)]) / 2) + 1,
                                               len(self.blk_ins_lines[int(prev_blk)])] if str(blks_info[prev_blk][1]) == first_layer\
                                        else [1, round(len(self.blk_ins_lines[int(prev_blk)]) / 2)]
                                    if case == 'beg':
                                        count += 1
                                        __createWedgeInsulation(count)
                                    lines = self.blk_ins_lines[int(prev_blk)][indexes[0]:indexes[1]]
                                    side = 'o' if str(blks_info[prev_blk][1]) == first_layer else 'i'
                                    for line_nr, line_name in enumerate(lines):
                                        skip_count = False
                                        if line_name[-1].isdigit():
                                            try:
                                                ins_group.lines[line_name] =\
                                                    self.occ.addLine(ins_pnt_prev[line_name[line_name.index(start_pnt_name[-1]) + 1:] + start_pnt_name[-1] + 'l'],
                                                                     ins_pnt_prev[line_name[:line_name.index(start_pnt_name[-1])] + start_pnt_name[-1] + 'h'])
                                            except:  # points are too close to each other
                                                skip_count = True
                                                next_line = lines[line_nr + 1]
                                                pnt1, pnt2 = line_name.split(side)
                                                pos = 'first' if next_line[:-1] == pnt1 else 'second'
                                                lines[line_nr + 1] = next_line + (pnt2 + 'l' if pos == 'first' else pnt1 + 'h')
                                        elif line_name[-1] in ['i', 'o']:
                                            ins_group.lines[line_name] = self.occ.addLine(ins_pnt_prev[line_name + 'h'], ins_pnt_prev[line_name + 'l'])
                                        else:
                                            ins_group.lines[line_name] = self.occ.addLine(ins_pnt_prev[line_name[:line_name.index(side)] + side + line_name[-1]],
                                                                                          ins_pnt_prev[line_name[line_name.index(side) + 1:-1] + side + line_name[-1]])
                                        if not skip_count:
                                            count += 1  # if start_pnt_name[-1] == sides[1] else -1
                                            ordered_lines[group_nr].append([line_name, count, ins_group.lines[line_name]])
                                    if case == 'end':
                                        count += 1
                                        __createWedgeInsulation(count)

                # Generate closed loops
                ordered_lines[group_nr].sort(key=lambda x: x[1])
                area_name = str((coil_nr - 1) * len(ins_groups) + group_nr)
                ins_group.areas[area_name] = dM.Area()
                if len(points_angle) == 1:
                    ins_group.areas['inner_loop'] = dM.Area(loop=self.occ.addCurveLoop([ins_group.lines[line] for line in [x[0] for x in ordered_lines[group_nr]]
                                                                                        if 'i' in line and line[0].isdigit() or '_i' in line]))
                    ins_group.areas[area_name].loop = self.occ.addCurveLoop([ins_group.lines[line] for line in [x[0] for x in ordered_lines[group_nr]]
                                                                                 if 'o' in line and line[0].isdigit() or '_o' in line])
                else:
                    ins_group.areas[area_name].loop = self.occ.addCurveLoop([ins_group.lines[line] for line in [x[0] for x in ordered_lines[group_nr]]])

    def constructThinShells(self, with_wedges):
        ins_th = self.md.geometries.thin_shells.ins_thickness
        mid_pole_ts = self.md.geometries.thin_shells.mid_poles
        mid_winding_ts = self.md.geometries.thin_shells.mid_windings
        mid_turn_ts = self.md.geometries.thin_shells.mid_turn_blocks
        mid_layer_ts = self.md.geometries.thin_shells.mid_layers_ht_to_ht
        mid_layer_ts_aux = self.md.geometries.thin_shells.mid_layers_aux

        # Create mid-pole and mid-turn thin shells
        for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items():
            for layer_nr, layer in coil.layers.items():
                for nr, blk_order in enumerate(layer):
                    block = self.geom.coil.coils[coil_nr].poles[blk_order.pole].layers[
                        layer_nr].windings[blk_order.winding].blocks[blk_order.block]
                    ht_list = list(self.md.geometries.coil.coils[coil_nr].poles[blk_order.pole].layers[
                                       layer_nr].windings[blk_order.winding].blocks[blk_order.block].half_turns.areas.keys())
                    # Create mid-pole and mid-winding thin shells
                    blk_index_next = nr + 1 if nr + 1 < len(layer) else 0
                    block_order_next = layer[blk_index_next]
                    block_next = self.geom.coil.coils[coil_nr].poles[block_order_next.pole].layers[
                        layer_nr].windings[block_order_next.winding].blocks[block_order_next.block]
                    ht_list_next = list(self.md.geometries.coil.coils[coil_nr].poles[block_order_next.pole].layers[
                                            layer_nr].windings[block_order_next.winding].blocks[block_order_next.block].half_turns.areas.keys())
                    ht_last = int(ht_list[-1])
                    ht_next_first = int(ht_list_next[0])
                    iH = [block.half_turns[ht_last].corners.bare.iH.x, block.half_turns[ht_last].corners.bare.iH.y]
                    iL = [block_next.half_turns[ht_next_first].corners.bare.iL.x, block_next.half_turns[ht_next_first].corners.bare.iL.y]
                    oH = [block.half_turns[ht_last].corners.bare.oH.x, block.half_turns[ht_last].corners.bare.oH.y]
                    oL = [block_next.half_turns[ht_next_first].corners.bare.oL.x, block_next.half_turns[ht_next_first].corners.bare.oL.y]
                    ts_name = str(blk_order.block) + '_' + str(block_order_next.block)
                    for ts, th, condition in zip([mid_pole_ts, mid_winding_ts], [ins_th.mid_pole, ins_th.mid_winding],
                                                 # ['_ly' + str(layer_nr), '_wd' + str(blk_order.winding) + '_wd' + str(block_order_next.winding)],
                                                 [self.geom.coil.coils[coil_nr].type == 'cos-theta' and block_order_next.pole != blk_order.pole,
                                                  (not with_wedges or not self.geom.wedges) and self.geom.coil.coils[coil_nr].type in
                                                  ['cos-theta', 'common-block-coil'] and block_order_next.pole == blk_order.pole and block_order_next.winding != blk_order.winding]):
                        if condition:
                            ts[ts_name] = dM.Region()
                            ts[ts_name].points['i'] = self.occ.addPoint((iH[0] + iL[0]) / 2, (iH[1] + iL[1]) / 2, 0)
                            ts[ts_name].points['o'] = self.occ.addPoint((oH[0] + oL[0]) / 2, (oH[1] + oL[1]) / 2, 0)
                            ts[ts_name].lines[str(ht_last) + '_' + str(ht_next_first)] =\
                                self.occ.addLine(ts[ts_name].points['i'], ts[ts_name].points['o'])
                            # Get insulation thickness
                            th[ts_name] = Func.sig_dig((Func.points_distance(iH, iL) + Func.points_distance(oH, oL)) / 2)
                            # if 'cl' + str(coil_nr) + th_name not in th:
                            #     th['cl' + str(coil_nr) + th_name] = float((Func.points_distance(iH, iL) + Func.points_distance(oH, oL)) / 2)
                    # Create mid-turn thin shells
                    mid_turn_ts[str(blk_order.block)] = dM.Region()
                    ts = mid_turn_ts[str(blk_order.block)]
                    for nr_ht, ht in enumerate(ht_list[:-1]):
                        line_name = ht + '_' + ht_list[nr_ht + 1]
                        current_ht = block.half_turns[int(ht)].corners.bare
                        next_ht = block.half_turns[int(ht_list[nr_ht + 1])].corners.bare
                        mid_inner = [(current_ht.iH.x + next_ht.iL.x) / 2, (current_ht.iH.y + next_ht.iL.y) / 2]
                        mid_outer = [(current_ht.oH.x + next_ht.oL.x) / 2, (current_ht.oH.y + next_ht.oL.y) / 2]
                        mid_length = Func.points_distance(mid_inner, mid_outer)
                        mid_line = Func.line_through_two_points(mid_inner, mid_outer)
                        points = {'inner': list, 'outer': list}
                        for case, current_h, current_l, next_h, next_l, mid_point in zip(
                                ['inner', 'outer'], [current_ht.iH, current_ht.oH], [current_ht.iL, current_ht.oL],
                                [next_ht.iH, next_ht.oH], [next_ht.iL, next_ht.oL], [mid_outer, mid_inner]):
                            current_line = Func.line_through_two_points([current_h.x, current_h.y], [current_l.x, current_l.y])
                            next_line = Func.line_through_two_points([next_h.x, next_h.y], [next_l.x, next_l.y])
                            current_intersect = Func.intersection_between_two_lines(mid_line, current_line)
                            next_intersect = Func.intersection_between_two_lines(mid_line, next_line)
                            points[case] = current_intersect if Func.points_distance(
                                current_intersect, mid_point) < mid_length else next_intersect
                        ts.points[line_name + '_i'] = self.occ.addPoint(points['inner'][0], points['inner'][1], 0)
                        ts.points[line_name + '_o'] = self.occ.addPoint(points['outer'][0], points['outer'][1], 0)
                        ts.lines[line_name] = self.occ.addLine(ts.points[line_name + '_i'], ts.points[line_name + '_o'])

        # Create mid-layer thin shells
        block_coil_mid_pole_list = [str(blks[0].block) + '_' + str(blks[1].block) for coil_nr, coil in self.block_coil_mid_pole_blks.items() for blks in coil]
        for ts_name, ts in mid_layer_ts.items():
            # Order mid-layer thin shell points according to their angle with respect to the x-axis to generate lines
            blk1, blk2 = ts_name.split('_')
            max_angle = max(ts.point_angles.values())
            max_diff = max_angle - min(ts.point_angles.values())
            if max_diff > np.pi:
                for pnt_name, angle in ts.point_angles.items():
                    if angle < max_diff / 2:
                        ts.point_angles[pnt_name] = angle + max_angle
            ordered_pnts = [[pnt_name, ts.point_angles[pnt_name], pnt] for pnt_name, pnt in ts.mid_layers.points.items()]
            ordered_pnts.sort(key=lambda x: x[1])
            for nr, pnt in enumerate(ordered_pnts[:-1]):
                pnt_current = pnt[0]
                pnt_next = ordered_pnts[nr + 1][0]
                if ((pnt_current[-1] == 'l' and pnt_next[-1] == 'h' and ts_name not in block_coil_mid_pole_list) or     # cos-theta
                        (ts_name in block_coil_mid_pole_list and
                         ((pnt_current[-1] == pnt_next[-1] == 'h' and block_coil_mid_pole_list.index(ts_name) == 0) or  # assumes a dipole block-coil
                          (pnt_current[-1] == pnt_next[-1] == 'l' and block_coil_mid_pole_list.index(ts_name) == 1) or  # assumes a dipole block-coil
                          (pnt_current[:-1] == pnt_next[:-1])))):
                    if pnt_current[:-1] == pnt_next[:-1]:
                        relevant_blk = blk2 if int(pnt_current[:-1]) in ts.half_turn_lists[blk1] else blk1
                        if nr > 0:
                            iter_nr = nr - 1
                            while int(ordered_pnts[iter_nr][0][:-1]) not in ts.half_turn_lists[relevant_blk]: iter_nr -= 1
                            line_name = ordered_pnts[iter_nr][0][:-1] + '_' + pnt_current[:-1]
                        else:
                            if len(ordered_pnts) == 2:  # todo: get right ht from relevant_blk for 1-ht blocks
                                line_name = pnt_current[:-1] + '_' + str(ts.half_turn_lists[relevant_blk][0])
                            else:
                                iter_nr = nr + 1
                                while int(ordered_pnts[iter_nr][0][:-1]) not in ts.half_turn_lists[relevant_blk]: iter_nr += 1
                                line_name = pnt_current[:-1] + '_' + ordered_pnts[iter_nr][0][:-1]
                    else:
                        line_name = pnt_current[:-1] + '_' + pnt_next[:-1]
                    ts.mid_layers.lines[line_name] = self.occ.addLine(pnt[2], ordered_pnts[nr + 1][2])
            if ts_name in mid_layer_ts_aux:
                aux_pnt = list(mid_layer_ts_aux[ts_name].points.keys())[0]
                other_pnt = ordered_pnts[0 if aux_pnt[-1] == 'l' else -1]
                other_pnt_coord = gmsh.model.getValue(0, other_pnt[2], [])[:2]  # needs to be a new point
                mid_layer_ts_aux[ts_name].points[other_pnt[0]] = self.occ.addPoint(other_pnt_coord[0], other_pnt_coord[1], 0)
                line_name = list(mid_layer_ts_aux[ts_name].lines.keys())[0]
                try:
                    mid_layer_ts_aux[ts_name].lines[line_name] = \
                        self.occ.addLine(mid_layer_ts_aux[ts_name].points[aux_pnt], mid_layer_ts_aux[ts_name].points[other_pnt[0]])
                except:
                    mid_layer_ts_aux[ts_name].lines.pop(line_name)

        # Create wedge-to-block and block-to-wedge lines
        for wdg_ts in [self.md.geometries.thin_shells.mid_layers_wdg_to_ht, self.md.geometries.thin_shells.mid_layers_ht_to_wdg]:
            for ts_name, ts in wdg_ts.items():
                pnt_list = list(ts.points.keys())
                for nr, pnt in enumerate(pnt_list[:-1]):
                    if pnt[-1] == 'l' and pnt_list[nr + 1][-1] == 'h':
                        ts.lines[pnt[:-1] + '_' + pnt_list[nr + 1][:-1]] = self.occ.addLine(ts.points[pnt], ts.points[pnt_list[nr + 1]])
                if ts_name in mid_layer_ts_aux:
                    aux_pnt = list(mid_layer_ts_aux[ts_name].points.keys())[
                            1 if list(mid_layer_ts_aux[ts_name].points.keys()).index('center') == 0 else 0]
                    other_pnt = pnt_list[0 if aux_pnt[-1] == 'l' else -1]
                    other_pnt_coord = gmsh.model.getValue(0, ts.points[other_pnt], [])[:2]  # needs to be a new point
                    mid_layer_ts_aux[ts_name].points[other_pnt] = self.occ.addPoint(other_pnt_coord[0], other_pnt_coord[1], 0)
                    line_name = list(mid_layer_ts_aux[ts_name].lines.keys())[0]
                    mid_layer_ts_aux[ts_name].lines[line_name] = self.occ.addCircleArc(
                        mid_layer_ts_aux[ts_name].points[aux_pnt], mid_layer_ts_aux[ts_name].points['center'], mid_layer_ts_aux[ts_name].points[other_pnt])

        # Create wedge-to-wedge lines
        for ts_nr, ts in self.md.geometries.thin_shells.mid_layers_wdg_to_wdg.items():
            ts.lines[ts_nr] = self.occ.addCircleArc(ts.points['beg'], ts.points['center'], ts.points[list(ts.points.keys())[-1]])

        # Create mid wedge-turn lines
        mid_turn_ts = self.md.geometries.thin_shells.mid_wedge_turn
        for ts_nr, ts in mid_turn_ts.items():
            line_name = list(ts.points.keys())[0][:-2]
            ts.lines[line_name] = self.occ.addLine(ts.points[line_name + '_i'], ts.points[line_name + '_o'])

        # Get insulation thickness
        for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items():
            geom_coil = self.geom.coil.coils[coil_nr]
            # Get block-coil mid-pole thickness
            if coil_nr in self.block_coil_mid_pole_blks:
                for blk_orders in self.block_coil_mid_pole_blks[coil_nr]:
                    block_y = geom_coil.poles[blk_orders[0].pole].layers[1].windings[blk_orders[0].winding].blocks[blk_orders[0].block].block_corners.iH.y
                    block_next_y = geom_coil.poles[blk_orders[1].pole].layers[1].windings[blk_orders[1].winding].blocks[blk_orders[1].block].block_corners.iH.y
                    ins_th.mid_layer[str(blk_orders[0].block) + '_' + str(blk_orders[1].block)] = Func.sig_dig(abs(block_y - block_next_y))
            # Get mid-layer thickness by intersecting the line passing through i-o of the ht of one side with the line passing through l-h of the ht of the opposite side
            for layer_nr, layer in coil.layers.items():
                for blk_order in layer:
                    for ts_name, ts in mid_layer_ts.items():
                        blk1, blk2 = ts_name.split('_')
                        if blk1 == str(blk_order.block) and ts_name not in block_coil_mid_pole_list:
                            block = geom_coil.poles[blk_order.pole].layers[layer_nr].windings[blk_order.winding].blocks[blk_order.block]
                            if layer_nr < len(coil.layers):
                                for blk_order_next in coil.layers[layer_nr + 1]:
                                    if blk_order_next.block == int(blk2):
                                        block_next = geom_coil.poles[blk_order_next.pole].layers[layer_nr + 1].windings[blk_order_next.winding].blocks[int(blk2)]
                                        break
                            else:
                                for blk_order_next in self.md.geometries.coil.anticlockwise_order.coils[coil_nr + 1].layers[1]:
                                    if blk_order_next.block == int(blk2):
                                        block_next = self.geom.coil.coils[coil_nr + 1].poles[blk_order_next.pole].layers[1].windings[blk_order_next.winding].blocks[int(blk2)]
                                        break
                            distances = []
                            lines = list(ts.mid_layers.lines.keys())
                            for line_name in [lines[0], lines[-1]]:
                                ht_1, ht_2 = int(line_name[:line_name.index('_')]), int(line_name[line_name.index('_') + 1:])
                                ht_char = {'low_p': ht_1, 'high_p': ht_2,
                                           'current': ht_1 if ht_1 in ts.half_turn_lists[blk1] else ht_2,
                                           'next':  ht_2 if ht_1 in ts.half_turn_lists[blk1] else ht_1}
                                hts = {'current': block.half_turns[ht_char['current']].corners.bare,
                                       'next': block_next.half_turns[ht_char['next']].corners.bare}
                                hts_p = {'low_p': [hts['current'].oL, hts['current'].iL] if ht_char['low_p'] == ht_char['current'] else [hts['next'].iL, hts['next'].oL],
                                         'high_p': [hts['current'].oH, hts['current'].iH] if ht_char['high_p'] == ht_char['current'] else [hts['next'].iH, hts['next'].oH],
                                         'low_p_opp': [hts['next'].iL, hts['next'].iH] if ht_char['low_p'] == ht_char['current'] else [hts['current'].oL, hts['current'].oH],
                                         'high_p_opp': [hts['next'].iL, hts['next'].iH] if ht_char['high_p'] == ht_char['current'] else [hts['current'].oL, hts['current'].oH]}
                                low_line = Func.line_through_two_points([hts_p['low_p'][0].x, hts_p['low_p'][0].y],
                                                                        [hts_p['low_p'][1].x, hts_p['low_p'][1].y])
                                high_line = Func.line_through_two_points([hts_p['high_p'][0].x, hts_p['high_p'][0].y],
                                                                         [hts_p['high_p'][1].x, hts_p['high_p'][1].y])
                                distances.extend([Func.points_distance([hts_p['low_p'][0].x, hts_p['low_p'][0].y], Func.intersection_between_two_lines(
                                    low_line, Func.line_through_two_points([hts_p['low_p_opp'][0].x, hts_p['low_p_opp'][0].y], [hts_p['low_p_opp'][1].x, hts_p['low_p_opp'][1].y]))),
                                                  Func.points_distance([hts_p['high_p'][0].x, hts_p['high_p'][0].y], Func.intersection_between_two_lines(
                                    high_line, Func.line_through_two_points([hts_p['high_p_opp'][0].x, hts_p['high_p_opp'][0].y], [hts_p['high_p_opp'][1].x, hts_p['high_p_opp'][1].y])))])
                            ins_th.mid_layer[ts_name] = Func.sig_dig(min(distances))
                    for ts_type, wdg_ts in enumerate([self.md.geometries.thin_shells.mid_layers_wdg_to_ht, self.md.geometries.thin_shells.mid_layers_ht_to_wdg]):
                        for ts_name, ts in wdg_ts.items():
                            wdg, blk = ts_name.split('_')
                            if blk == str(blk_order.block):
                                block = geom_coil.poles[blk_order.pole].layers[layer_nr].windings[blk_order.winding].blocks[blk_order.block]
                                wedge = self.md.geometries.wedges.coils[coil_nr].layers[layer_nr + (1 if ts_type == 1 else -1)].wedges[int(wdg[1:])]
                                pnt_il = gmsh.model.getValue(0, wedge.points['il'], [])[:2]
                                pnt_ol = gmsh.model.getValue(0, wedge.points['ol'], [])[:2]
                                pnt_ih = gmsh.model.getValue(0, wedge.points['ih'], [])[:2]
                                pnt_oh = gmsh.model.getValue(0, wedge.points['oh'], [])[:2]
                                low_line = Func.line_through_two_points(pnt_il, pnt_ol)
                                high_line = Func.line_through_two_points(pnt_ih, pnt_oh)
                                el1_l, el2_l = list(ts.lines.keys())[0].split('_')
                                ht_l = block.half_turns[int(el1_l) if el2_l == wdg else int(el2_l)].corners.bare
                                el1_h, el2_h = list(ts.lines.keys())[-1].split('_')
                                ht_h = block.half_turns[int(el1_h) if el2_h == wdg else int(el2_h)].corners.bare
                                opp_line_l = Func.line_through_two_points([ht_l.iL.x, ht_l.iL.y], [ht_l.iH.x, ht_l.iH.y]) if ts_type == 0\
                                    else Func.line_through_two_points([ht_l.oL.x, ht_l.oL.y], [ht_l.oH.x, ht_l.oH.y])
                                opp_line_h = Func.line_through_two_points([ht_h.iL.x, ht_h.iL.y], [ht_h.iH.x, ht_h.iH.y]) if ts_type == 0 \
                                    else Func.line_through_two_points([ht_h.oL.x, ht_h.oL.y], [ht_h.oH.x, ht_h.oH.y])
                                ins_th.mid_layer[ts_name] = Func.sig_dig(
                                    (Func.points_distance(pnt_ol if ts_type == 0 else pnt_il, Func.intersection_between_two_lines(low_line, opp_line_l)) + 
                                     Func.points_distance(pnt_oh if ts_type == 0 else pnt_ih, Func.intersection_between_two_lines(high_line, opp_line_h))) / 2)

        for coil_nr, coil in self.md.geometries.wedges.coils.items():
            # Get mid-layer thickness by intersecting the line passing through i-o of the wdg of one side with the line passing through l-h of the wdg of the opposite side
            for layer_nr, layer in coil.layers.items():
                for wedge_nr, wedge in layer.wedges.items():
                    for ts_name, ts in self.md.geometries.thin_shells.mid_layers_wdg_to_wdg.items():
                        wdg1, wdg2 = ts_name[1:ts_name.index('_')], ts_name[ts_name.index('_') + 2:]
                        if wdg1 == str(wedge_nr):
                            wedge_next = self.md.geometries.wedges.coils[coil_nr].layers[layer_nr + 1].wedges[int(wdg2)]
                            # pnt_il_next = gmsh.model.getValue(0, wedge_next.points['il'], [])[:2]
                            # pnt_ih_next = gmsh.model.getValue(0, wedge_next.points['ih'], [])[:2]
                            pnt_il = gmsh.model.getValue(0, wedge.points['il'], [])[:2]
                            pnt_ol = gmsh.model.getValue(0, wedge.points['ol'], [])[:2]
                            pnt_ih = gmsh.model.getValue(0, wedge.points['ih'], [])[:2]
                            pnt_oh = gmsh.model.getValue(0, wedge.points['oh'], [])[:2]
                            low_line = Func.line_through_two_points(pnt_il, pnt_ol)
                            high_line = Func.line_through_two_points(pnt_ih, pnt_oh)
                            opp_line = Func.line_through_two_points(gmsh.model.getValue(0, wedge_next.points['il'], [])[:2],
                                                                    gmsh.model.getValue(0, wedge_next.points['ih'], [])[:2])
                            ins_th.mid_layer[ts_name] = Func.sig_dig(
                                (Func.points_distance(pnt_ol, Func.intersection_between_two_lines(low_line, opp_line)) +
                                 Func.points_distance(pnt_oh, Func.intersection_between_two_lines(high_line, opp_line))) / 2)

    def buildDomains(self, run_type, symmetry):
        """
            Generates plane surfaces from the curve loops
        """
        iron = self.geom.iron
        gm = self.md.geometries
        with_iron_yoke = self.data.magnet.geometry.electromagnetics.with_iron_yoke if run_type == 'EM'\
            else self.data.magnet.geometry.thermal.with_iron_yoke
        with_wedges = self.data.magnet.geometry.electromagnetics.with_wedges if run_type == 'EM' \
            else self.data.magnet.geometry.thermal.with_wedges

        # Build iron yoke domains
        if with_iron_yoke:
            for quadrant, qq in gm.iron.quadrants.items():
                for area_name, area in qq.areas.items():
                    build = True
                    loops = [area.loop]
                    for hole_key, hole in iron.hyper_holes.items():
                        if area_name == hole.areas[1]:
                            loops.append(qq.areas[hole.areas[0]].loop)
                        elif area_name == hole.areas[0]:  # or iron.hyper_areas[area_name].material == 'BH_air':
                            build = False
                    if build:
                        area.surface = self.occ.addPlaneSurface(loops)
                        # Group areas per material type
                        self.md.domains.groups_entities.iron[iron.hyper_areas[area_name].material].append(area.surface)

        # Build coil domains
        for coil_nr, coil in gm.coil.coils.items():
            for pole_nr, pole in coil.poles.items():
                for layer_nr, layer in pole.layers.items():
                    for winding_nr, winding in layer.windings.items():
                        for block_key, block in winding.blocks.items():
                            for area_name, area in block.half_turns.areas.items():
                                area.surface = self.occ.addPlaneSurface([area.loop])

        # Build wedges domains
        if with_wedges:
            for coil_nr, coil in gm.wedges.coils.items():
                for layer_nr, layer in coil.layers.items():
                    for wedge_nr, wedge in layer.wedges.items():
                        wedge.areas[str(wedge_nr)].surface = self.occ.addPlaneSurface([wedge.areas[str(wedge_nr)].loop])

        # Build insulation domains
        if run_type == 'TH' and not self.data.magnet.geometry.thermal.use_TSA:
            for coil_nr, coil in gm.insulation.coils.items():
                for group_nr, group in coil.group.items():
                    holes = []
                    for blk in group.blocks:
                        holes.extend([ht.loop for ht_nr, ht in gm.coil.coils[
                            coil_nr].poles[blk[0]].layers[blk[1]].windings[blk[2]].blocks[blk[3]].half_turns.areas.items()])
                    for wdg in group.wedges:
                        holes.extend([wedge.loop for wedge_nr, wedge in gm.wedges.coils[
                            coil_nr].layers[wdg[0]].wedges[wdg[1]].areas.items()])
                    if len(group.ins.areas) == 1:
                        for area_name, area in group.ins.areas.items():
                            area.surface = self.occ.addPlaneSurface([area.loop] + holes)
                    else:
                        for area_name, area in group.ins.areas.items():
                            if area_name.isdigit():
                                area.surface = self.occ.addPlaneSurface([area.loop] + holes + [group.ins.areas['inner_loop'].loop])

        # Create and build air far field
        if run_type == 'EM':
            if self.data.magnet.geometry.electromagnetics.with_iron_yoke:
                for i in iron.key_points:
                    gm.iron.max_radius = max(gm.iron.max_radius, max(iron.key_points[i].x, iron.key_points[i].y))
                greatest_radius = gm.iron.max_radius
            else:  # no iron yoke data available
                for coil_nr, coil in self.geom.coil.coils.items():
                    for pole_nr, pole in coil.poles.items():
                        first_winding = list(pole.layers[len(pole.layers)].windings.keys())[0]
                        first_block = list(pole.layers[len(pole.layers)].windings[first_winding].blocks)[0]
                        gm.coil.max_radius = max(abs(pole.layers[len(pole.layers)].windings[first_winding].blocks[first_block].block_corners.oL.x),
                                                 abs(pole.layers[len(pole.layers)].windings[first_winding].blocks[first_block].block_corners.oL.y),
                                                 gm.coil.max_radius)
                greatest_radius = gm.coil.max_radius
            radius_in = greatest_radius * (2.5 if self.data.magnet.geometry.electromagnetics.with_iron_yoke else 6)
            radius_out = greatest_radius * (3.2 if self.data.magnet.geometry.electromagnetics.with_iron_yoke else 8)
            air_inf_center_x, air_inf_center_y = 0, 0
            for coil_nr, coil in self.md.geometries.coil.coils.items():
                air_inf_center_x += coil.bore_center.x
                air_inf_center_y += coil.bore_center.y
                gm.air.points['bore_center' + str(coil_nr)] = self.occ.addPoint(coil.bore_center.x, coil.bore_center.y, 0.)
            air_inf_center = [air_inf_center_x / len(self.md.geometries.coil.coils), air_inf_center_y / len(self.md.geometries.coil.coils)]
            if symmetry == 'none':
                gm.air_inf.lines['inner'] = self.occ.addCircle(air_inf_center[0], air_inf_center[1], 0., radius_in)
                gm.air_inf.lines['outer'] = self.occ.addCircle(air_inf_center[0], air_inf_center[1], 0., radius_out)
                gm.air_inf.areas['inner'] = dM.Area(loop=self.occ.addCurveLoop([gm.air_inf.lines['inner']]))
                gm.air_inf.areas['outer'] = dM.Area(loop=self.occ.addCurveLoop([gm.air_inf.lines['outer']]))
                gm.air_inf.areas['outer'].surface = self.occ.addPlaneSurface([gm.air_inf.areas['outer'].loop, gm.air_inf.areas['inner'].loop])
            else:
                pnt1 = [1, 0] if symmetry in ['xy', 'x'] else [0, -1]
                pnt2 = [0, 1] if symmetry in ['xy', 'y'] else [-1, 0]
                gm.air.points['pnt1'] = self.occ.addPoint(pnt1[0] * radius_in, pnt1[1] * radius_in, 0)
                gm.air.points['pnt2'] = self.occ.addPoint(pnt2[0] * radius_in, pnt2[1] * radius_in, 0)
                gm.air_inf.points['pnt1'] = self.occ.addPoint(pnt1[0] * radius_out, pnt1[1] * radius_out, 0)
                gm.air_inf.points['pnt2'] = self.occ.addPoint(pnt2[0] * radius_out, pnt2[1] * radius_out, 0)
                gm.air.lines['ln1'] = self.occ.addLine(gm.air.points['pnt1'], gm.air_inf.points['pnt1'])
                gm.air.lines['ln2'] = self.occ.addLine(gm.air.points['pnt2'], gm.air_inf.points['pnt2'])
                if not self.data.magnet.geometry.electromagnetics.with_iron_yoke:
                    gm.air_inf.points['center'] = self.occ.addPoint(0, 0, 0)
                gm.air_inf.lines['inner'] = self.occ.addCircleArc(gm.air.points['pnt2'], gm.air_inf.points['center'], gm.air.points['pnt1'])
                gm.air_inf.lines['outer'] = self.occ.addCircleArc(gm.air_inf.points['pnt2'], gm.air_inf.points['center'], gm.air_inf.points['pnt1'])

                if symmetry in ['xy', 'x']:
                    gm.air.lines['x_p'] = self.occ.addLine(self.md.geometries.air_inf.points['center'] if 'solenoid' in self.geom.coil.coils[1].type else
                                                           gm.iron.quadrants[1].points[self.symmetric_bnds['x_p']['pnts'][-1][0]], gm.air.points['pnt1'])
                    self.symmetric_loop_lines['x'].append(gm.air.lines['x_p'])
                else:  # y
                    gm.air.lines['y_n'] = self.occ.addLine(gm.iron.quadrants[4].points[self.symmetric_bnds['y_n']['pnts'][-1][0]], gm.air.points['pnt1'])
                    self.symmetric_loop_lines['y'].append(gm.air.lines['y_n'])
                if symmetry in ['xy', 'y']:
                    gm.air.lines['y_p'] = self.occ.addLine(gm.iron.quadrants[1].points[self.symmetric_bnds['y_p']['pnts'][-1][0]], gm.air.points['pnt2'])
                    self.symmetric_loop_lines['y'].insert(0, gm.air.lines['y_p'])
                else:  # x
                    gm.air.lines['x_n'] = self.occ.addLine(self.md.geometries.air_inf.points['center'] if 'solenoid' in self.geom.coil.coils[1].type else
                                                           gm.iron.quadrants[2].points[self.symmetric_bnds['x_n']['pnts'][-1][0]], gm.air.points['pnt2'])
                    self.symmetric_loop_lines['x'].insert(0, gm.air.lines['x_n'])

                inner_lines = self.symmetric_loop_lines['x'] + [gm.air_inf.lines['inner']] + self.symmetric_loop_lines['y']\
                    if symmetry == 'xy' else self.symmetric_loop_lines[symmetry] + [gm.air_inf.lines['inner']]
                gm.air_inf.areas['inner'] = dM.Area(loop=self.occ.addCurveLoop(inner_lines))
                gm.air_inf.areas['outer'] = dM.Area(loop=self.occ.addCurveLoop(
                    [gm.air.lines['ln1'], gm.air_inf.lines['outer'], gm.air.lines['ln2'], gm.air_inf.lines['inner']]))
                gm.air_inf.areas['outer'].surface = self.occ.addPlaneSurface([gm.air_inf.areas['outer'].loop])
            # self.md.domains.groups_entities.air_inf = [gm.air_inf.areas['outer'].surface]
            gm.air_inf.areas['inner'].surface = self.occ.addPlaneSurface([gm.air_inf.areas['inner'].loop])

        # self.occ.synchronize()
        # self.gu.launch_interactive_GUI()

    def fragment(self):
        """
            Fragment and group air domains
        """
        # Collect surfaces to be subtracted by background air
        holes = []

        # Iron
        for group_name, surfaces in self.md.domains.groups_entities.iron.items():
            holes.extend([(2, s) for s in surfaces])
        # Coils
        for coil_nr, coil in self.md.geometries.coil.coils.items():
            for pole_nr, pole in coil.poles.items():
                for layer_nr, layer in pole.layers.items():
                    for winding_nr, winding in layer.windings.items():
                        for block_key, block in winding.blocks.items():
                            for area_name, area in block.half_turns.areas.items():
                                holes.append((2, area.surface))
        # Wedges
        for coil_nr, coil in self.md.geometries.wedges.coils.items():
            for layer_nr, layer in coil.layers.items():
                for wedge_nr, wedge in layer.wedges.items():
                    for area_name, area in wedge.areas.items():
                        holes.append((2, area.surface))
        # Insulation
        # if run_type == 'TH' and not self.data.magnet.geometry.thermal.use_TSA:
        #     for coil_nr, coil in self.md.geometries.insulation.coils.items():
        #         for group_nr, group in coil.group.items():
        #             for area_name, area in group.ins.areas.items():
        #                 holes.append((2, area.surface))

        # Fragment
        fragmented = self.occ.fragment([(2, self.md.geometries.air_inf.areas['inner'].surface)], holes)[1]
        self.occ.synchronize()

        self.md.domains.groups_entities.air = []
        existing_domains = [e[0][1] for e in fragmented[1:]]
        for e in fragmented[0]:
            if e[1] not in existing_domains:
                self.md.domains.groups_entities.air.append(e[1])

    def updateTags(self, run_type, symmetry):

        # Update half turn line tags
        for coil_nr, coil in self.md.geometries.coil.coils.items():
            for pole_nr, pole in coil.poles.items():
                for layer_nr, layer in pole.layers.items():
                    for winding_nr, winding in layer.windings.items():
                        for block_key, block in winding.blocks.items():
                            hts = block.half_turns
                            # Get half turn ID numbers
                            area_list = list(hts.areas.keys())
                            for nr, ht_nr in enumerate(area_list):
                                first_tag = int(min(gmsh.model.getAdjacencies(2, hts.areas[ht_nr].surface)[1]))
                                hts.lines[ht_nr + 'i'] = first_tag
                                hts.lines[ht_nr + 'l'] = first_tag + 1
                                hts.lines[ht_nr + 'o'] = first_tag + 2
                                hts.lines[ht_nr + 'h'] = first_tag + 3

        # Update insulation line tags
        if run_type == 'TH' and not self.data.magnet.geometry.thermal.use_TSA:
            pass  # todo

        # Update wedge line tags
        for coil_nr, coil in self.md.geometries.wedges.coils.items():
            for layer_nr, layer in coil.layers.items():
                for wedge_nr, wedge in layer.wedges.items():
                    lines_tags = list(gmsh.model.getAdjacencies(2, wedge.areas[str(wedge_nr)].surface)[1])
                    lines_tags.sort(key=lambda x: x)
                    wedge.lines['i'] = int(lines_tags[0])
                    wedge.lines['l'] = int(lines_tags[1])
                    wedge.lines['o'] = int(lines_tags[2])
                    wedge.lines['h'] = int(lines_tags[3])

        if run_type == 'EM':
            def _get_bnd_lines():
                return [pair[1] for pair in self.occ.getEntitiesInBoundingBox(corner_min[0], corner_min[1], corner_min[2],
                                                                              corner_max[0], corner_max[1], corner_max[2], dim=1)]

            tol = 1e-6
            # Update tags of air and air_inf arcs and their points
            lines_tags = gmsh.model.getAdjacencies(2, self.md.geometries.air_inf.areas['outer'].surface)[1]
            self.md.geometries.air_inf.lines['outer'] = int(lines_tags[0 if symmetry == 'none' else 1])
            self.md.geometries.air_inf.lines['inner'] = int(lines_tags[1 if symmetry == 'none' else 3])
            if symmetry == 'none':  # todo: check if this holds for symmetric models too
                for coil_nr, coil in self.md.geometries.coil.coils.items():
                    self.md.geometries.air.points['bore_center' + str(coil_nr)] += 2
            else:
                pnt_tags = list(gmsh.model.getAdjacencies(1, self.md.geometries.air_inf.lines['outer'])[1])
                indexes = [0, 1, 0] if 'x' in symmetry else [1, 0, 1]
                pnts = [0, 1] if gmsh.model.getValue(0, pnt_tags[indexes[0]], [])[indexes[2]] >\
                                 gmsh.model.getValue(0, pnt_tags[indexes[1]], [])[indexes[2]] else [1, 0]
                self.md.geometries.air_inf.points['pnt1'] = int(pnt_tags[pnts[0]])
                self.md.geometries.air_inf.points['pnt2'] = int(pnt_tags[pnts[1]])
                pnt_tags = list(gmsh.model.getAdjacencies(1, self.md.geometries.air_inf.lines['inner'])[1])
                pnts = [0, 1] if gmsh.model.getValue(0, pnt_tags[indexes[0]], [])[indexes[2]] > \
                                 gmsh.model.getValue(0, pnt_tags[indexes[1]], [])[indexes[2]] else [1, 0]
                self.md.geometries.air.points['pnt1'] = int(pnt_tags[pnts[0]])
                self.md.geometries.air.points['pnt2'] = int(pnt_tags[pnts[1]])
                for coil_nr, coil in self.md.geometries.coil.coils.items():
                    self.md.geometries.air.points['bore_center' + str(coil_nr)] =(
                        self.occ.getEntitiesInBoundingBox(-tol + coil.bore_center.x, -tol + coil.bore_center.y, -tol,
                                                          tol + coil.bore_center.x, tol + coil.bore_center.y, tol, dim=0))[0][1]

            # Group symmetry boundary lines per type
            if symmetry == 'xy':
                corner_min = [-tol, -tol, -tol]
                corner_max = [gmsh.model.getValue(0, self.md.geometries.air_inf.points['pnt1'], [])[0] + tol, tol, tol]
                self.md.domains.groups_entities.symmetric_boundaries.x = _get_bnd_lines()
                corner_max = [tol, gmsh.model.getValue(0, self.md.geometries.air_inf.points['pnt2'], [])[1] + tol, tol]
                self.md.domains.groups_entities.symmetric_boundaries.y = _get_bnd_lines()
            elif symmetry == 'x':
                x_coord = gmsh.model.getValue(0, self.md.geometries.air_inf.points['pnt1'], [])[0]
                corner_min = [- x_coord - tol, -tol, -tol]
                corner_max = [x_coord + tol, tol, tol]
                self.md.domains.groups_entities.symmetric_boundaries.x = _get_bnd_lines()
            elif symmetry == 'y':
                y_coord = gmsh.model.getValue(0, self.md.geometries.air_inf.points['pnt2'], [])[1]
                corner_min = [-tol, - y_coord - tol, -tol]
                corner_max = [tol, y_coord + tol, tol]
                self.md.domains.groups_entities.symmetric_boundaries.y = _get_bnd_lines()

        # self.occ.synchronize()
        # self.gu.launch_interactive_GUI()
