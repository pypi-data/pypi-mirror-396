import os
import gmsh
import copy
import numpy as np
import json
import logging

from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import FilesAndFolders as Util
from fiqus.utils.Utils import GeometricFunctions as Func
from fiqus.data import DataFiQuS as dF
from fiqus.data import DataMultipole as dM
from fiqus.data import RegionsModelFiQuS as rM

logger = logging.getLogger(__name__)

class Mesh:
    def __init__(self, data: dF.FDM() = None, mesh_folder: str = None,
                 verbose: bool = False):
        """
        Class to generate mesh
        :param data: FiQuS data model
        :param verbose: If True more information is printed in python console.
        """
        self.data: dF.FDM() = data
        self.mesh_folder = mesh_folder
        self.verbose: bool = verbose

        self.md = dM.MultipoleData()
        self.rc = dM.MultipoleRegionCoordinate()
        self.rm = rM.RegionsModel()
        self.strands = None

        self.gu = GmshUtils(self.mesh_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=self.data.run.verbosity_Gmsh)
        self.occ = gmsh.model.occ
        self.mesh = gmsh.model.mesh

        self.brep_iron_curves = {1: set(), 2: set(), 3: set(), 4: set()}
        self.mesh_parameters = dict.fromkeys(['SJ', 'SICN', 'SIGE', 'Gamma', 'nodes'])
        self.geom_files = os.path.join(os.path.dirname(self.mesh_folder), self.data.general.magnet_name)
        self.model_file = os.path.join(self.mesh_folder, self.data.general.magnet_name)

        # Insulation sequence involving cable insulation only (turn-to-turn, outlying conductor edge)
        self.ins_type_cond = {}
        # Insulation sequence involving quench heaters (outlying or mid-layer/pole)
        qh_keys = {key: {} for key in range(1, self.data.quench_protection.quench_heaters.N_strips + 1)}
        self.ins_type_qh = {'internal_double': {}, 'internal': copy.deepcopy(qh_keys), 'external': copy.deepcopy(qh_keys)}
        # Insulation sequence between blocks (layer-to-layer, pole-to-pole)
        self.ins_type = {'mid_pole': {}, 'mid_winding': {}, 'mid_layer': {}, 'aux': {}}
        self.qh_data, self.wedge_cond = {}, {}

        self.colors = {'wedges': [86, 180, 233],  # sky blue
                       'insul': [119, 136, 153],  # light slate grey
                       'half_turns_pos': [213, 94, 0],  # vermilion
                       'half_turns_neg': [255, 136, 42],  # light vermilion
                       'air': [240, 228, 66],  # yellow
                       'air_inf': [220, 208, 46],  # dark yellow
                       # yoke
                       'BHiron1': [0, 114, 178],  # blue
                       'BHiron2': [0, 158, 115],  # bluish green
                       'BHiron4': [86, 180, 233],  # sky blue
                       # key
                       'BHiron3': [220, 208, 46],  # dark yellow
                       # [230, 159, 0],  # orange
                       # collar
                       'BHiron5': [204, 121, 167],  # hopbush
                       'BHiron6': [0, 114, 178],  # blue
                       'BHiron7': [204, 121, 167]}  # reddish purple

    def clear(self):
        self.md = dM.MultipoleData()
        self.rc = dM.MultipoleRegionCoordinate()
        self.rm = rM.RegionsModel()
        gmsh.clear()

    def ending_step(self, gui: bool = False):
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()

    def loadStrandPositions(self, run_type):
        self.strands = json.load(open(f"{self.geom_files}_{run_type}.strs"))

    def loadAuxiliaryFile(self, run_type):
        self.md = Util.read_data_from_yaml(f"{self.geom_files}_{run_type}.aux", dM.MultipoleData)

    def updateAuxiliaryFile(self, run_type):
        Util.write_data_to_yaml(f'{self.model_file}_{run_type}.aux', self.md.model_dump())

    def saveMeshFile(self, run_type):
        gmsh.write(f'{self.model_file}_{run_type}.msh')

    def saveRegionFile(self, run_type):
        Util.write_data_to_yaml(f'{self.model_file}_{run_type}.reg', self.rm.model_dump())

    def saveRegionCoordinateFile(self, run_type):
        Util.write_data_to_yaml(f'{self.model_file}_{run_type}.reco', self.rc.model_dump())

    def getIronCurvesTags(self):
        for quadrant, qq in self.md.geometries.iron.quadrants.items():
            for _, area in qq.areas.items():
                if area.surface:
                    self.brep_iron_curves[quadrant] |= set(gmsh.model.getAdjacencies(2, area.surface)[1])

    def defineMesh(self, geometry, mesh, run_type):
        thresholds = []
        self.occ.synchronize()

        if mesh.conductors.field.enabled:
            distance_conductors = self.mesh.field.add("Distance")
            self.mesh.field.setNumbers(distance_conductors, "CurvesList",
                                       [line for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items() for layer_nr, layer in coil.layers.items()
                                        for _, block_order in enumerate(layer) for _, line in self.md.geometries.coil.coils[coil_nr].poles[block_order.pole].layers[
                                            layer_nr].windings[block_order.winding].blocks[block_order.block].half_turns.lines.items()]
                                        )
            self.mesh.field.setNumber(distance_conductors, "Sampling", 100)

            threshold_conductors = self.mesh.field.add("Threshold")
            self.mesh.field.setNumber(threshold_conductors, "InField", distance_conductors)
            self.mesh.field.setNumber(threshold_conductors, "SizeMin", mesh.conductors.field.SizeMin)
            self.mesh.field.setNumber(threshold_conductors, "SizeMax", mesh.conductors.field.SizeMax)
            self.mesh.field.setNumber(threshold_conductors, "DistMin", mesh.conductors.field.DistMin)
            self.mesh.field.setNumber(threshold_conductors, "DistMax", mesh.conductors.field.DistMax)
            self.mesh.field.setNumber(threshold_conductors, "StopAtDistMax", 1)
            thresholds.append(threshold_conductors)

        if mesh.wedges.field.enabled:
            distance_wedges = self.mesh.field.add("Distance")
            self.mesh.field.setNumbers(distance_wedges, "CurvesList",
                                       [line for _, coil in self.md.geometries.wedges.coils.items() for _, layer in coil.layers.items() for _, wdg in layer.wedges.items() for _, line in wdg.lines.items()]
                                    )
            self.mesh.field.setNumber(distance_wedges, "Sampling", 100)

            # raise Exception(f"cannot set threshold for wedges field: {[line for _, coil in self.md.geometries.wedges.coils.items() for _, layer in coil.layers.items() for _, wdg in layer.wedges.items() for _, line in wdg.lines.items()]}")

            threshold_wedges = self.mesh.field.add("Threshold")
            self.mesh.field.setNumber(threshold_wedges, "InField", distance_wedges)
            self.mesh.field.setNumber(threshold_wedges, "SizeMin", mesh.wedges.field.SizeMin)
            self.mesh.field.setNumber(threshold_wedges, "SizeMax", mesh.wedges.field.SizeMax)
            self.mesh.field.setNumber(threshold_wedges, "DistMin", mesh.wedges.field.DistMin)
            self.mesh.field.setNumber(threshold_wedges, "DistMax", mesh.wedges.field.DistMax)
            self.mesh.field.setNumber(threshold_wedges, "StopAtDistMax", 1)
            thresholds.append(threshold_wedges)

        if geometry.with_iron_yoke:
            distance_iron = self.mesh.field.add("Distance")
            self.mesh.field.setNumbers(distance_iron, "CurvesList", [line for _, qq in self.brep_iron_curves.items() for line in qq])
            self.mesh.field.setNumber(distance_iron, "Sampling", 100)

            if mesh.iron_field.enabled:

                threshold_iron = self.mesh.field.add("Threshold")
                self.mesh.field.setNumber(threshold_iron, "InField", distance_iron)
                self.mesh.field.setNumber(threshold_iron, "SizeMin", mesh.iron_field.SizeMin)
                self.mesh.field.setNumber(threshold_iron, "SizeMax", mesh.iron_field.SizeMax)
                self.mesh.field.setNumber(threshold_iron, "DistMin", mesh.iron_field.DistMin)
                self.mesh.field.setNumber(threshold_iron, "DistMax", mesh.iron_field.DistMax)
                # the iron field is typically rather coarse so that 'overwriting' other fields is not a problem
                # its distMax however would need to be large for StopAtDistMax to be effective
                #self.mesh.field.setNumber(threshold_iron, "StopAtDistMax", 1)
                thresholds.append(threshold_iron)

        if run_type == 'EM' and mesh.bore_field.enabled:

            distance_bore = self.mesh.field.add("Distance")
            self.mesh.field.setNumbers(distance_bore, "PointsList", [pnt for pnt_name, pnt in self.md.geometries.air.points.items() if 'bore' in pnt_name])
            self.mesh.field.setNumber(distance_bore, "Sampling", 100)

            threshold_bore = self.mesh.field.add("Threshold")
            self.mesh.field.setNumber(threshold_bore, "InField", distance_bore)
            self.mesh.field.setNumber(threshold_bore, "SizeMin", mesh.bore_field.SizeMin)
            self.mesh.field.setNumber(threshold_bore, "SizeMax", mesh.bore_field.SizeMax)
            self.mesh.field.setNumber(threshold_bore, "DistMin", mesh.bore_field.DistMin)
            self.mesh.field.setNumber(threshold_bore, "DistMax", mesh.bore_field.DistMax)
            self.mesh.field.setNumber(threshold_bore, "StopAtDistMax", 1)
            thresholds.append(threshold_bore)

        insulation_mesh_fields = []
        if run_type == 'TH':
            for coil_nr, coil in self.md.geometries.insulation.coils.items():
                for _, group in coil.group.items():
                    # Areas
                    for area_name, area in group.ins.areas.items():
                        if area_name.isdigit():
                            insulation_mesh_fields.append(self.mesh.field.add("Constant"))
                            insulation_mesh_field = insulation_mesh_fields[-1]
                            self.mesh.field.setNumbers(insulation_mesh_field, "SurfacesList", [area.surface])
                            self.mesh.field.setNumber(insulation_mesh_field, "VIn", mesh.insulation.global_size)

        background = self.mesh.field.add("Min")
        self.mesh.field.setNumbers(background, "FieldsList", thresholds + insulation_mesh_fields)
        self.mesh.field.setAsBackgroundMesh(background)

        # Apply transfinite curves and potentially surfaces to conductors and wedges
        if mesh.conductors.transfinite.enabled_for in ['curves', 'curves_and_surfaces']:
            for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items():
                for layer_nr, layer in coil.layers.items():
                    for _, block_order in enumerate(layer):
                        winding = self.md.geometries.coil.coils[coil_nr].poles[block_order.pole].layers[
                            layer_nr].windings[block_order.winding]
                        cable = self.data.conductors[winding.conductor_name].cable
                        for line_key, line in winding.blocks[block_order.block].half_turns.lines.items():
                            if mesh.model_dump().get('isothermal_conductors', False):
                                elements = 1
                            elif any([i in line_key for i in ['i', 'o']]):
                                elements = max(1, round(cable.bare_cable_height_mean / mesh.conductors.transfinite.curve_target_size_height))
                            elif any([i in line_key for i in ['l', 'h']]):
                                elements = max(1, round(cable.bare_cable_width / mesh.conductors.transfinite.curve_target_size_width))
                                
                            self.mesh.setTransfiniteCurve(line, elements)
                        if mesh.conductors.transfinite.enabled_for=='curves_and_surfaces' or mesh.model_dump().get('isothermal_conductors', False):
                            for _, area in winding.blocks[block_order.block].half_turns.areas.items():
                                self.mesh.setTransfiniteSurface(area.surface)
                                self.mesh.setRecombine(2, area.surface)
        
        if 'insulation' in mesh.model_dump() and 'TSA' in mesh.model_dump()["insulation"]:
            # Apply transfinite curves to thin shell lines
            if geometry.use_TSA:
                gts = self.md.geometries.thin_shells
                conductor_target_sizes = {'width': mesh.conductors.transfinite.curve_target_size_width, 'height': mesh.conductors.transfinite.curve_target_size_height}
                wedge_target_sizes = {'width': mesh.wedges.transfinite.curve_target_size_width, 'height': mesh.wedges.transfinite.curve_target_size_height}
                for ts_group, side in zip([gts.mid_layers_ht_to_ht, gts.mid_layers_ht_to_wdg, gts.mid_layers_wdg_to_ht, gts.mid_layers_wdg_to_wdg,
                                           gts.mid_poles, gts.mid_windings, gts.mid_turn_blocks, gts.mid_wedge_turn, gts.mid_layers_aux],
                                          ['height', 'height', 'height', 'height', 'width', 'width', 'width', 'width', 'height']):
                    for ts_name, ts in ts_group.items():
                        for _, line in ts.lines.items() if isinstance(ts, dM.Region) else ts.mid_layers.lines.items():
                            if mesh.isothermal_conductors or mesh.isothermal_wedges:
                                elements = 1
                            else:
                                coords = gmsh.model.getValue(1, line, [i[0] for i in gmsh.model.getParametrizationBounds(1, line)])
                                target_size = wedge_target_sizes[side] if ts_name.count('w') == 2 else conductor_target_sizes[side]
                                elements = max(1, round(Func.points_distance(coords[:2], coords[3:-1]) / target_size))

                            # it's a wedge
                            if ts_name.count('w') == 2 and mesh.wedges.transfinite.enabled_for in ['curves', 'curves_and_surfaces']:
                                self.mesh.setTransfiniteCurve(line, elements)
                            elif ts_name.count('w') != 2 and mesh.conductors.transfinite.enabled_for in ['curves', 'curves_and_surfaces']:
                                self.mesh.setTransfiniteCurve(line, elements)   
            # COMMENTED since this overwrites also the cable transfinite meshes and in general, 
            # restricting the insulation boundaries to be transfinite seems very restrictive due to their complex geometry
            # Apply transfinite curves to insulation boundaries
            # else:
            #     for coil_nr, coil in self.md.geometries.insulation.coils.items():
            #         for group_nr, group in coil.group.items():
            #             cable_height = self.data.conductors[self.md.geometries.coil.coils[coil_nr].poles[
            #                 group.blocks[0][0]].layers[group.blocks[0][1]].windings[group.blocks[0][2]].conductor_name].cable.bare_cable_height_mean
            #             for line in [bnd[1] for bnd in gmsh.model.getBoundary(
            #                     [(2, list(group.ins.areas.values())[0].surface)],  # +
            #                     # [(2, ht.surface) for blk_order in group.blocks for ht in
            #                     #  self.md.geometries.coil.coils[coil_nr].poles[blk_order[0]].layers[blk_order[1]].windings[blk_order[2]].blocks[blk_order[3]].half_turns.areas.values()] +
            #                     # [(2, self.md.geometries.wedges.coils[coil_nr].layers[wdg_order[0]].wedges[wdg_order[1]].areas[str(wdg_order[1])].surface) for wdg_order in group.wedges],
            #                     combined=True, oriented=False)]:
            #                 pnts = gmsh.model.getAdjacencies(1, line)[1]
            #                 length = Func.points_distance(gmsh.model.getValue(0, pnts[0], []), gmsh.model.getValue(0, pnts[1], []))
            #                 self.mesh.setTransfiniteCurve(line,max(1, round(length / (mesh.conductor_target_sizes.width if length > 2 * cable_height else mesh.conductor_target_sizes.height))))

        # Apply transfinite curves to wedges
        if mesh.wedges.transfinite.enabled_for in ['curves', 'curves_and_surfaces']:
            if geometry.with_wedges:
                for coil_nr, coil in self.md.geometries.wedges.coils.items():
                    for layer_nr, layer in coil.layers.items():
                        for _, wedge in layer.wedges.items():
                            pnts = gmsh.model.getAdjacencies(1, wedge.lines['i'])[1]
                            inner_height = Func.points_distance(gmsh.model.getValue(0, pnts[0], []), gmsh.model.getValue(0, pnts[1], []))
                            pnts = gmsh.model.getAdjacencies(1, wedge.lines['l'])[1]
                            width = Func.points_distance(gmsh.model.getValue(0, pnts[0], []), gmsh.model.getValue(0, pnts[1], []))
                            pnts = gmsh.model.getAdjacencies(1, wedge.lines['o'])[1]
                            outer_height = Func.points_distance(gmsh.model.getValue(0, pnts[0], []), gmsh.model.getValue(0, pnts[1], []))
                            for line_key, line in wedge.lines.items():
                                if mesh.model_dump().get('isothermal_wedges', False):
                                    elements = 1
                                elif 'i' in line_key:
                                    elements = max(1, round(inner_height / mesh.wedges.transfinite.curve_target_size_height))
                                elif 'o' in line_key:
                                    elements = max(1, round((inner_height if mesh.wedges.transfinite.enabled_for in ['curves', 'curves_and_surfaces']
                                                            else outer_height) / mesh.wedges.transfinite.curve_target_size_height))
                                elif any([i in line_key for i in ['l', 'h']]):
                                    elements = max(1, round(width / mesh.wedges.transfinite.curve_target_size_width))
                                if mesh.wedges.transfinite.enabled_for in ['curves', 'curves_and_surfaces']:
                                    self.mesh.setTransfiniteCurve(line, elements)
                            if mesh.wedges.transfinite.enabled_for=='curves_and_surfaces' or mesh.model_dump().get('isothermal_wedges', False):
                                self.mesh.setTransfiniteSurface(list(wedge.areas.values())[0].surface)
                                self.mesh.setRecombine(2, list(wedge.areas.values())[0].surface)

    def createPhysicalGroups(self, geometry):
        """
            Creates physical groups by grouping the mirrored entities according to the Roxie domains
        """
        offset: int = 1 if 'symmetry' in geometry.model_dump() else int(1e6)
        pg_tag = offset

        # Create physical groups of iron yoke regions and block insulation
        pg = self.md.domains.physical_groups
        for group_name, surfaces in self.md.domains.groups_entities.iron.items():
            pg.iron.surfaces[group_name] = gmsh.model.addPhysicalGroup(2, surfaces, pg_tag)
            gmsh.model.setPhysicalName(2, pg.iron.surfaces[group_name], group_name)
            color = self.colors[group_name]
            gmsh.model.setColor([(2, i) for i in surfaces], color[0], color[1], color[2])
            pg_tag += 1

        # Create the physical group of air infinite
        if 'symmetry' in geometry.model_dump():
            gmsh.model.setPhysicalName(0, gmsh.model.addPhysicalGroup(
                0, [pnt for pnt_name, pnt in self.md.geometries.air.points.items() if 'bore_field' in pnt_name], pg_tag), 'bore_centers')
            pg_tag += 1
            pg.air_inf_bnd = gmsh.model.addPhysicalGroup(1, [self.md.geometries.air_inf.lines['outer']], pg_tag)
            gmsh.model.setPhysicalName(1, pg.air_inf_bnd, 'air_inf_bnd')
            pg_tag += 1
            pg.air_inf = gmsh.model.addPhysicalGroup(2, [self.md.geometries.air_inf.areas['outer'].surface], pg_tag)
            gmsh.model.setPhysicalName(2, pg.air_inf, 'air_inf')
            gmsh.model.setColor([(2, self.md.geometries.air_inf.areas['outer'].surface)], self.colors['air_inf'][0], self.colors['air_inf'][1], self.colors['air_inf'][2])
            pg_tag += 1
            pg.air = gmsh.model.addPhysicalGroup(2, self.md.domains.groups_entities.air, pg_tag)
            gmsh.model.setPhysicalName(2, pg.air, 'air')
            gmsh.model.setColor([(2, i) for i in self.md.domains.groups_entities.air], self.colors['air'][0], self.colors['air'][1], self.colors['air'][2])
            pg_tag += 1

        # Create physical groups of half turns
        lyr_list_group = []
        for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items():
            lyr_list_group.extend(['cl' + str(coil_nr) + 'ly' + str(lyr) for lyr in list(coil.layers.keys())])
            for layer_nr, layer in coil.layers.items():
                ht_list_group = []
                for nr, block_order in enumerate(layer):
                    wnd = self.md.geometries.coil.coils[coil_nr].poles[block_order.pole].layers[
                        layer_nr].windings[block_order.winding]
                    block = wnd.blocks[block_order.block]
                    block_nr = block_order.block
                    pg.blocks[block_nr] = dM.PoweredBlock()
                    blk_pg = pg.blocks[block_nr]
                    blk_pg.current_sign = block.current_sign
                    blk_pg.conductor = wnd.conductor_name
                    color = self.colors['half_turns_pos'] if block.current_sign > 0 else self.colors['half_turns_neg']
                    ht_list = list(block.half_turns.areas.keys())
                    ht_list_group.extend(ht_list)
                    if nr + 1 < len(layer):
                        if layer[nr + 1].pole == block_order.pole and layer[nr + 1].winding != block_order.winding:
                            ht_list_group.append('w' + str(nr))
                    # Create 2D physical groups of half turns
                    for ht_key, ht in block.half_turns.areas.items():
                        blk_pg.half_turns[int(ht_key)] = dM.PoweredGroup()
                        ht_pg = blk_pg.half_turns[int(ht_key)]
                        # Create physical group and assign name and color
                        ht_pg.tag = gmsh.model.addPhysicalGroup(2, [ht.surface], pg_tag)
                        gmsh.model.setPhysicalName(2, ht_pg.tag, ht_key)
                        gmsh.model.setColor([(2, ht.surface)], color[0], color[1], color[2])
                        pg_tag += 1
                        # Assign thin-shell group
                        # the check for reversed block coil is not tested well
                        if geometry.model_dump().get('correct_block_coil_tsa_checkered_scheme', False) and self.md.geometries.coil.coils[coil_nr].type == 'reversed-block-coil':
                            azimuthal = 'a1' if list(wnd.blocks.keys()).index(block_nr) % 2 == 0 else 'a2'
                        else:
                            azimuthal = 'a1' if lyr_list_group.index('cl' + str(coil_nr) + 'ly' + str(layer_nr)) % 2 == 0 else 'a2'
                        radial = 'r1' if ht_list_group.index(ht_key) % 2 == 0 else 'r2'
                        ht_pg.group = radial + '_' + azimuthal
                    if geometry.model_dump().get('use_TSA', False):
                        # Create 1D physical groups of thin shells
                        for ht_line_key, ht_line in block.half_turns.lines.items():
                            ht_nr = ht_line_key[:-1]
                            # Create half turn line groups
                            line_pg = gmsh.model.addPhysicalGroup(1, [ht_line], pg_tag)
                            gmsh.model.setPhysicalName(1, line_pg, ht_line_key)
                            color = [0, 0, 0] if blk_pg.half_turns[int(ht_nr)].group[:2] == 'r1' else [150, 150, 150]
                            gmsh.model.setColor([(1, ht_line)], color[0], color[1], color[2])
                            pg_tag += 1
                            # Store thin shell tags
                            blk_pg.half_turns[int(ht_nr)].lines[ht_line_key[-1]] = line_pg

        # Create points region for projection
        if 'use_TSA' in geometry.model_dump():
            self.md.domains.physical_groups.half_turns_points = gmsh.model.addPhysicalGroup(
                0, [gmsh.model.getAdjacencies(1, gmsh.model.getAdjacencies(2, ht.surface)[1][0])[1][0]
                    for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items()
                    for layer_nr, layer in coil.layers.items() for block_order in layer
                    for ht_key, ht in self.md.geometries.coil.coils[coil_nr].poles[block_order.pole].layers[
                        layer_nr].windings[block_order.winding].blocks[block_order.block].half_turns.areas.items()], int(4e6))
            gmsh.model.setPhysicalName(0, self.md.domains.physical_groups.half_turns_points, 'points')

        # Create physical groups of insulations
        if not geometry.model_dump().get('use_TSA', True):
            for coil_nr, coil in self.md.geometries.insulation.coils.items():
                for group_nr, group in coil.group.items():
                    # Areas
                    for area_name, area in group.ins.areas.items():
                        if area_name.isdigit():
                            pg.insulations.surfaces[area_name] = gmsh.model.addPhysicalGroup(2, [area.surface], pg_tag)
                            gmsh.model.setPhysicalName(2, pg.insulations.surfaces[area_name], 'insul_' + area_name)
                            gmsh.model.setColor([(2, area.surface)], self.colors['insul'][0], self.colors['insul'][1], self.colors['insul'][2])
                            pg_tag += 1
                    
                    # Boundaries
                    area_name = list(group.ins.areas.keys())[0]  # todo: test for Mono
                    pg.insulations.curves['ext' + area_name] = gmsh.model.addPhysicalGroup(
                        1, [bnd[1] for bnd in gmsh.model.getBoundary([(2, list(group.ins.areas.values())[0].surface)], combined=False, oriented=False)[:len(group.ins.lines)]], pg_tag)
                    gmsh.model.setPhysicalName(1, pg.insulations.curves['ext' + area_name], 'insul_ext' + area_name)
                    pg_tag += 1
                    # todo: NOT COMPLETED: would work if the tags were updated in the Geometry script after saving and loading brep
                    # side_lines = {'i': [], 'o': [], 'l': [], 'h': []}
                    # for line_name, line in group.ins.lines.items():
                    #     side_lines[line_name[-1] if line_name[-1].isalpha() else sorted(line_name)[-1]].append(line)
                    # for side, side_line in side_lines.items():
                    #     pg.insulations.curves[str(group_nr) + side] = gmsh.model.addPhysicalGroup(1, side_line, pg_tag)
                    #     gmsh.model.setPhysicalName(1, pg.insulations.curves[str(group_nr) + side], str(group_nr) + side)
                    #     pg_tag += 1

        # Create physical groups of wedges
        for coil_nr, coil in self.md.geometries.wedges.coils.items():
            for layer_nr, layer in coil.layers.items():
                for wedge_nr, wedge in layer.wedges.items():
                    pg.wedges[wedge_nr] = dM.WedgeGroup()
                    wedge_pg = pg.wedges[wedge_nr]
                    wedge_pg.tag = gmsh.model.addPhysicalGroup(2, [wedge.areas[str(wedge_nr)].surface], pg_tag)
                    gmsh.model.setPhysicalName(2, wedge_pg.tag, 'w' + str(wedge_nr))
                    gmsh.model.setColor([(2, wedge.areas[str(wedge_nr)].surface)],
                                        self.colors['wedges'][0], self.colors['wedges'][1], self.colors['wedges'][2])
                    pg_tag += 1
                    # Assign thin-shell group
                    prev_block_hts = pg.blocks[layer.block_prev[wedge_nr]].half_turns
                    if len(list(prev_block_hts.keys())) > 1:
                        wedge_pg.group = prev_block_hts[list(prev_block_hts.keys())[-2]].group
                    else:
                        prev_group = prev_block_hts[list(prev_block_hts.keys())[0]].group
                        wedge_pg.group = ('r1' if prev_group[1] == '2' else 'r2') + prev_group[prev_group.index('_'):]
                    if geometry.model_dump().get('use_TSA', False):
                        # Create 1D physical groups of thin shells
                        for line_key, line in wedge.lines.items():
                            wedge_pg.lines[line_key] = gmsh.model.addPhysicalGroup(1, [line], pg_tag)
                            gmsh.model.setPhysicalName(1, wedge_pg.lines[line_key], 'w' + str(wedge_nr) + line_key)
                            color = [0, 0, 0] if wedge_pg.group[:2] == 'r1' else [150, 150, 150]
                            gmsh.model.setColor([(1, line)], color[0], color[1], color[2])
                            pg_tag += 1

        # Create physical groups of thin shells
        if geometry.model_dump().get('use_TSA', False):
            gts = self.md.geometries.thin_shells
            # Create physical groups of block mid-layer lines
            block_coil_flag = False
            for ts_name, ts in gts.mid_layers_ht_to_ht.items():
                blk_i, blk_o = ts_name[:ts_name.index('_')], ts_name[ts_name.index('_') + 1:]
                for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items():
                    if (any(int(blk_i) == blk_order.block for blk_order in self.md.geometries.coil.anticlockwise_order.coils[coil_nr].layers[1]) and
                            any(int(blk_o) == blk_order.block for blk_order in self.md.geometries.coil.anticlockwise_order.coils[coil_nr].layers[1])):  # block-coil mid-pole case
                        block_coil_flag = True
                for line_name, line in ts.mid_layers.lines.items():
                    line_pg = gmsh.model.addPhysicalGroup(1, [line], pg_tag)
                    gmsh.model.setPhysicalName(1, line_pg, line_name)
                    pg_tag += 1
                    ht1, ht2 = int(line_name[:line_name.index('_')]), int(line_name[line_name.index('_') + 1:])
                    if ht1 in ts.half_turn_lists[blk_i]:
                        if block_coil_flag:
                            pg.blocks[int(blk_i)].half_turns[ht1].mid_layer_lines.inner[line_name] = line_pg
                        else:
                            pg.blocks[int(blk_i)].half_turns[ht1].mid_layer_lines.outer[line_name] = line_pg
                        pg.blocks[int(blk_o)].half_turns[ht2].mid_layer_lines.inner[line_name] = line_pg
                    else:
                        pg.blocks[int(blk_o)].half_turns[ht1].mid_layer_lines.inner[line_name] = line_pg
                        if block_coil_flag:
                            pg.blocks[int(blk_i)].half_turns[ht2].mid_layer_lines.inner[line_name] = line_pg
                        else:
                            pg.blocks[int(blk_i)].half_turns[ht2].mid_layer_lines.outer[line_name] = line_pg

            # Create physical groups of wedge-to-block mid-layer lines
            for ts_name, ts in gts.mid_layers_wdg_to_ht.items():
                wdg, blk = ts_name.split('_')
                for line_name, line in ts.lines.items():
                    line_pg = gmsh.model.addPhysicalGroup(1, [line], pg_tag)
                    gmsh.model.setPhysicalName(1, line_pg, line_name)
                    pg_tag += 1
                    pg.wedges[int(wdg[1:])].mid_layer_lines.outer[line_name] = line_pg
                    ht = line_name[:line_name.index('_')] if line_name[line_name.index('_') + 1:] == wdg else line_name[line_name.index('_') + 1:]
                    pg.blocks[int(blk)].half_turns[int(ht)].mid_layer_lines.inner[line_name] = line_pg

            # Create physical groups of block-to-wedge mid-layer lines
            for ts_name, ts in gts.mid_layers_ht_to_wdg.items():
                wdg, blk = ts_name.split('_')
                for line_name, line in ts.lines.items():
                    line_pg = gmsh.model.addPhysicalGroup(1, [line], pg_tag)
                    gmsh.model.setPhysicalName(1, line_pg, line_name)
                    pg_tag += 1
                    pg.wedges[int(wdg[1:])].mid_layer_lines.inner[line_name] = line_pg
                    ht = line_name[:line_name.index('_')] if line_name[line_name.index('_') + 1:] == wdg else line_name[line_name.index('_') + 1:]
                    pg.blocks[int(blk)].half_turns[int(ht)].mid_layer_lines.outer[line_name] = line_pg

            # Create physical groups of wedge-to-wedge mid-layer lines
            for ts_name, ts in gts.mid_layers_wdg_to_wdg.items():
                wdg_i, wdg_o = ts_name[1:ts_name.index('_')], ts_name[ts_name.index('_') + 2:]
                line_pg = gmsh.model.addPhysicalGroup(1, [ts.lines[list(ts.lines.keys())[0]]], pg_tag)
                gmsh.model.setPhysicalName(1, line_pg, ts_name)
                pg_tag += 1
                pg.wedges[int(wdg_i)].mid_layer_lines.outer[ts_name] = line_pg
                pg.wedges[int(wdg_o)].mid_layer_lines.inner[ts_name] = line_pg

            # Create non-mid-layer thin shells
            for ts_group_name, ts_group in zip(['mid_pole', 'mid_winding', 'mid_turn', 'mid_turn', 'aux'],
                                               [gts.mid_poles, gts.mid_windings, gts.mid_turn_blocks, gts.mid_wedge_turn, gts.mid_layers_aux]):
                for ts_name, ts in ts_group.items():
                    if '_' in ts_name:
                        el_name1, el_name2 = ts_name.split('_')
                        el_name1, el_name2 = el_name1.strip('w'), el_name2.strip('w')
                    else:  # mid_turn_blocks
                        el_name1, el_name2 = ts_name, ts_name
                    for line_name, line in ts.lines.items():
                        line_pg = gmsh.model.addPhysicalGroup(1, [line], pg_tag)
                        gmsh.model.setPhysicalName(1, line_pg, line_name)
                        pg_tag += 1
                        if ts_group_name == 'aux':
                            ht1 = int(list(ts.points.keys())[0][:-1])
                        else:
                            ht1, ht2 = line_name.split('_')
                            pg.blocks[int(el_name2)].half_turns[int(ht2)].__dict__[ts_group_name + '_lines'][line_name] = line_pg
                        if ts_name[0] == 'w':
                            pg.wedges[int(el_name1)].__dict__[ts_group_name + '_lines'][line_name] = line_pg
                        else:
                            pg.blocks[int(el_name1)].half_turns[int(ht1)].__dict__[ts_group_name + '_lines'][line_name] = line_pg

        # Create physical groups of symmetric boundaries
        if geometry.model_dump().get('symmetry', 'none') != 'none':
            line_tags_normal_free, line_tags_tangent_free = [], []
            if geometry.symmetry == 'xy':
                if len(self.md.geometries.coil.coils[1].poles) == 2:
                    line_tags_normal_free = self.md.domains.groups_entities.symmetric_boundaries.y
                    line_tags_tangent_free = self.md.domains.groups_entities.symmetric_boundaries.x
                elif len(self.md.geometries.coil.coils[1].poles) == 4:  # todo: think about other multi-pole types
                    line_tags_tangent_free = self.md.domains.groups_entities.symmetric_boundaries.x +\
                                         self.md.domains.groups_entities.symmetric_boundaries.y
            elif geometry.symmetry == 'x':
                if 'solenoid' in self.md.geometries.coil.coils[1].type:
                    line_tags_normal_free = self.md.domains.groups_entities.symmetric_boundaries.x
                else:
                    line_tags_tangent_free = self.md.domains.groups_entities.symmetric_boundaries.x
            elif geometry.symmetry == 'y':
                if len(self.md.geometries.coil.coils[1].poles) == 2:
                    line_tags_normal_free = self.md.domains.groups_entities.symmetric_boundaries.y
                elif len(self.md.geometries.coil.coils[1].poles) == 4:
                    line_tags_tangent_free = self.md.domains.groups_entities.symmetric_boundaries.y
            if line_tags_normal_free:
                pg.symmetric_boundaries.normal_free = gmsh.model.addPhysicalGroup(1, line_tags_normal_free, pg_tag)
                gmsh.model.setPhysicalName(1, pg.symmetric_boundaries.normal_free, 'normal_free_bnd')
                pg_tag += 1
            if line_tags_tangent_free:
                pg.symmetric_boundaries.tangential_free = gmsh.model.addPhysicalGroup(1, line_tags_tangent_free, pg_tag)
                gmsh.model.setPhysicalName(1, pg.symmetric_boundaries.tangential_free, 'tangent_free_bnd')
                pg_tag += 1

    def rearrangeThinShellsData(self):
        pg = self.md.domains.physical_groups
        ins_th = self.md.geometries.thin_shells.ins_thickness
        qh = self.data.quench_protection.quench_heaters

        def _store_qh_data(position, thin_shell, ts_tag):
            qh_ins = self.ins_type_qh[position][qh.ids[ht_index]]
            if thin_shell not in qh_ins: qh_ins[thin_shell] = []
            qh_ins[thin_shell].append(ts_tag)
            if thin_shell not in self.qh_data[qh.ids[ht_index]]:
                self.qh_data[qh.ids[ht_index]][thin_shell] = {'conductor': blk_pg.conductor, 'ht_side': qh_side}

        def _store_ts_tags(pg_el, geom_ts_name='', geom_ts_name2=None, ts_grp='', lines='', lines_side=None):
            geom_ts = self.md.geometries.thin_shells.model_dump()[geom_ts_name]
            for ln_name, ln_tag in (pg_el.model_dump()[lines][lines_side] if lines_side else pg_el.model_dump()[lines]).items():
                for ts_name in ts_groups[ts_grp]:
                    if ts_name in geom_ts:
                        if ln_name in (geom_ts[ts_name][geom_ts_name2]['lines'] if geom_ts_name2 else geom_ts[ts_name]['lines']):
                            if ts_name not in self.ins_type[ts_grp]: self.ins_type[ts_grp][ts_name] = []
                            self.ins_type[ts_grp][ts_name].append(ln_tag)
                            break

        # Collect thin shell tags
        # Half turns
        for blk_pg_nr, blk_pg in pg.blocks.items():
            ts_groups = {'mid_wedge_turn': [ts_name for ts_name in self.md.geometries.thin_shells.mid_wedge_turn if blk_pg_nr == int(ts_name.split('_')[1])],
                         'aux': [ts_name for ts_name in ins_th.mid_layer if str(blk_pg_nr) in ts_name.split('_')],
                         'mid_winding': [ts_name for ts_name in ins_th.mid_winding if blk_pg_nr == int(ts_name.split('_')[0])],
                         'mid_pole': [ts_name for ts_name in ins_th.mid_pole if blk_pg_nr == int(ts_name.split('_')[0])],
                         'mid_layer': [ts_name for ts_name in ins_th.mid_layer if ts_name[0] != 'w' and blk_pg_nr == int(ts_name.split('_')[0])
                                       or ts_name[0] == 'w' and ts_name.split('_')[1][0] != 'w' and blk_pg_nr == int(ts_name.split('_')[1])],
                         'mid_layer_qh_i': [ts_name for ts_name in ins_th.mid_layer if ts_name.split('_')[1][0] != 'w' and blk_pg_nr == int(ts_name.split('_')[1])]}
            ht_list = list(blk_pg.half_turns.keys())
            self.ins_type_cond[str(blk_pg_nr)] = {'inner': [], 'outer': [], 'higher': [], 'lower': [], 'mid_turn': []}
            for ht_nr, ht in blk_pg.half_turns.items():
                if ht_nr in qh.turns and qh.N_strips > 0:  # check if a quench heater strip touches the current half-turn
                    ht_index = qh.turns.index(ht_nr)
                    qh_side = qh.turns_sides[ht_index]
                    if qh.ids[ht_index] not in self.qh_data: self.qh_data[qh.ids[ht_index]] = {}
                else: qh_side = ''

                # find conductor type of ht adjacent to wedge
                if ht_list.index(ht_nr) == len(ht_list) - 1 and ht.mid_turn_lines:
                    for line_name, line_tag in ht.mid_turn_lines.items():
                        for ts_name in ts_groups['mid_wedge_turn']:
                            if line_name in self.md.geometries.thin_shells.mid_wedge_turn[ts_name].lines:
                                self.wedge_cond[int(ts_name[1:ts_name.index('_')])] = blk_pg.conductor
                                break

                self.ins_type_cond[str(blk_pg_nr)]['mid_turn'].extend(list(ht.mid_turn_lines.values()))  # mid-turn insulation

                if ht.aux_lines:  # outer mid-layer insulation
                    _store_ts_tags(ht, geom_ts_name='mid_layers_aux', ts_grp='aux', lines='aux_lines')

                if ht.mid_layer_lines.inner and qh_side == 'i':
                    for line_name, line_tag in ht.mid_layer_lines.inner.items():
                        for ts_name in ts_groups['mid_layer_qh_i']:
                            if ts_name in self.md.geometries.thin_shells.mid_layers_ht_to_ht:
                                ts_lines = self.md.geometries.thin_shells.mid_layers_ht_to_ht[ts_name].mid_layers.lines
                            elif ts_name in self.md.geometries.thin_shells.mid_layers_wdg_to_ht:
                                ts_lines = self.md.geometries.thin_shells.mid_layers_wdg_to_ht[ts_name].lines
                            else: ts_lines = []
                            if line_name in ts_lines:
                                _store_qh_data('internal', ts_name, line_tag)
                                break
                elif ht.mid_layer_lines.inner:  # block-coil (!) inner mid-layer insulation
                    _store_ts_tags(ht, geom_ts_name='mid_layers_ht_to_ht', geom_ts_name2='mid_layers', ts_grp='mid_layer', lines='mid_layer_lines', lines_side='inner')
                elif not ht.mid_layer_lines.inner and qh_side == 'i':  # quench heater inner insulation
                    _store_qh_data('external', blk_pg_nr, ht.lines['i'])
                elif not ht.mid_layer_lines.inner:  # inner insulation
                    self.ins_type_cond[str(blk_pg_nr)]['inner'].append(ht.lines['i'])

                if ht.mid_layer_lines.outer and qh_side == 'o':  # mid-layer quench heater insulation
                    for line_name, line_tag in ht.mid_layer_lines.outer.items():
                        for ts_name in ts_groups['mid_layer']:
                            if ts_name in self.md.geometries.thin_shells.mid_layers_ht_to_ht:
                                ts_lines = self.md.geometries.thin_shells.mid_layers_ht_to_ht[ts_name].mid_layers.lines
                            elif ts_name in self.md.geometries.thin_shells.mid_layers_ht_to_wdg:
                                ts_lines = self.md.geometries.thin_shells.mid_layers_ht_to_wdg[ts_name].lines
                            else: ts_lines = []
                            if line_name in ts_lines:
                                _store_qh_data('internal', ts_name, line_tag)
                                break
                elif ht.mid_layer_lines.outer:  # mid-layer insulation
                    for line_name, line_tag in ht.mid_layer_lines.outer.items():
                        for ts_name in ts_groups['mid_layer']:
                            if ts_name in self.md.geometries.thin_shells.mid_layers_ht_to_ht:
                                ts_lines = self.md.geometries.thin_shells.mid_layers_ht_to_ht[ts_name].mid_layers.lines
                            elif ts_name in self.md.geometries.thin_shells.mid_layers_ht_to_wdg:
                                ts_lines = self.md.geometries.thin_shells.mid_layers_ht_to_wdg[ts_name].lines
                            else: ts_lines = []
                            if line_name in ts_lines:
                                if ts_name not in self.ins_type['mid_layer']: self.ins_type['mid_layer'][ts_name] = []
                                self.ins_type['mid_layer'][ts_name].append(line_tag)
                                break
                elif not ht.mid_layer_lines.outer and qh_side == 'o':  # quench heater outer insulation
                    _store_qh_data('external', blk_pg_nr, ht.lines['o'])
                else:  # outer insulation
                    self.ins_type_cond[str(blk_pg_nr)]['outer'].append(ht.lines['o'])

                # mid-pole insulation
                _store_ts_tags(ht, geom_ts_name='mid_poles', ts_grp='mid_pole', lines='mid_pole_lines')

                # mid-winding insulation
                _store_ts_tags(ht, geom_ts_name='mid_windings', ts_grp='mid_winding', lines='mid_winding_lines')

                if ht_list.index(ht_nr) == 0 and len(ht.mid_turn_lines) + len(ht.mid_winding_lines) + len(ht.mid_pole_lines) == 1:  # lower angle external side insulation
                    if qh_side == 'l': _store_qh_data('external', blk_pg_nr, ht.lines['l'])
                    else: self.ins_type_cond[str(blk_pg_nr)]['lower'].append(ht.lines['l'])
                if ht_list.index(ht_nr) == len(ht_list) - 1 and len(ht.mid_turn_lines) + len(ht.mid_winding_lines) + len(ht.mid_pole_lines) == 1:  # higher angle external side insulation
                    if qh_side == 'h': _store_qh_data('external', blk_pg_nr, ht.lines['h'])
                    else: self.ins_type_cond[str(blk_pg_nr)]['higher'].append(ht.lines['h'])

        # Wedges
        for wdg_pg_nr, wdg_pg in pg.wedges.items():
            ts_groups = {'aux': [ts_name for ts_name in ins_th.mid_layer if 'w' + str(wdg_pg_nr) in ts_name.split('_')],
                         'mid_layer': [ts_name for ts_name in ins_th.mid_layer if 'w' + str(wdg_pg_nr) == ts_name.split('_')[0]]}
            self.ins_type_cond['w' + str(wdg_pg_nr)] = {'inner': [], 'outer': [], 'higher': [], 'lower': [], 'mid_turn': []}
            if wdg_pg.aux_lines: _store_ts_tags(wdg_pg, geom_ts_name='mid_layers_aux', ts_grp='aux', lines='aux_lines')
            if not wdg_pg.mid_layer_lines.inner: self.ins_type_cond['w' + str(wdg_pg_nr)]['inner'].append(wdg_pg.lines['i'])
            if wdg_pg.mid_layer_lines.outer:
                for line_name, line_tag in wdg_pg.mid_layer_lines.outer.items():
                    for ts_name in ts_groups['mid_layer']:
                        if ts_name in self.md.geometries.thin_shells.mid_layers_wdg_to_ht:
                            ts_lines = self.md.geometries.thin_shells.mid_layers_wdg_to_ht[ts_name].lines
                        elif ts_name in self.md.geometries.thin_shells.mid_layers_wdg_to_wdg:
                            ts_lines = self.md.geometries.thin_shells.mid_layers_wdg_to_wdg[ts_name].lines
                        else: ts_lines = []
                        if line_name in ts_lines:
                            if ts_name not in self.ins_type['mid_layer']: self.ins_type['mid_layer'][ts_name] = []
                            self.ins_type['mid_layer'][ts_name].append(line_tag)
                            break
            else: self.ins_type_cond['w' + str(wdg_pg_nr)]['outer'].append(wdg_pg.lines['o'])

        # Collect common thin shells for double qh mid-layers
        for qh_nr, ts_groups in self.ins_type_qh['internal'].items():
            for qh_nr2, ts_groups2 in self.ins_type_qh['internal'].items():
                if qh_nr != qh_nr2:
                    common_ts_groups = list(set(ts_groups) & set(ts_groups2))
                    for ts in common_ts_groups:
                        tags, tags2 = ts_groups[ts], ts_groups2[ts]
                        common_tags = list(set(tags) & set(tags2))
                        for tag in common_tags:
                            tags.remove(tag), tags2.remove(tag)
                            if self.qh_data[qh_nr2][ts]['ht_side'] == 'i': qh_name = str(qh_nr) + '_' + str(qh_nr2)
                            else: qh_name = str(qh_nr2) + '_' + str(qh_nr)
                            if qh_name not in self.ins_type_qh['internal_double']: self.ins_type_qh['internal_double'][qh_name] = {}
                            qh_ins_id = self.ins_type_qh['internal_double'][qh_name]
                            if ts not in qh_ins_id: qh_ins_id[ts] = []
                            qh_ins_id[ts].append(tag)

    def assignRegionsTags(self, geometry, mesh):
        def _get_input_insulation_data(i_name, i_type=None):
            ow_idx = next((index for index, couple in enumerate(self.data.magnet.solve.thermal.insulation_TSA.block_to_block.blocks_connection_overwrite)
                           if all(element in couple for element in i_name.split('_'))), None)
            if i_type == 'mid_winding': mid_mat, mid_th = [self.data.magnet.solve.wedges.material], []
            elif ow_idx is not None:
                mid_mat = self.data.magnet.solve.thermal.insulation_TSA.block_to_block.materials_overwrite[ow_idx]
                mid_th = self.data.magnet.solve.thermal.insulation_TSA.block_to_block.thicknesses_overwrite[ow_idx]
            else: mid_mat, mid_th = [self.data.magnet.solve.thermal.insulation_TSA.block_to_block.material], []
            return mid_mat, mid_th

        def _compute_insulation_thicknesses(tot_th, known_ins_th):
            if not mid_thicknesses:
                mid_lyrs = [Func.sig_dig(tot_th - known_ins_th) / len(mid_materials)] * len(mid_materials)
            elif None in mid_thicknesses:
                input_ths = sum([th for th in mid_thicknesses if th is not None])
                mid_lyrs = [th if th is not None else Func.sig_dig(tot_th - known_ins_th - input_ths) / mid_thicknesses.count(None) for th in mid_thicknesses]
            else: mid_lyrs = mid_thicknesses
            zeros = [nbr for nbr, th in enumerate(mid_lyrs) if th < 1e-8]
            if tot_th - known_ins_th - sum(mid_lyrs) < -1e-8:
                raise ValueError("Layer-to-layer insulation exceeds the space between blocks: check 'solve'->'insulation_TSA'->'block_to_block'->'thicknesses_overwrite'")
            else: return mid_lyrs, zeros

        pg = self.md.domains.physical_groups
        qh = self.data.quench_protection.quench_heaters

        # Air and air far field
        if 'bore_field' in mesh.model_dump():
            self.rm.air_far_field.vol.radius_out = float(abs(max(gmsh.model.getValue(0, gmsh.model.getAdjacencies(
                    1, self.md.geometries.air_inf.lines['outer'])[1][0], []), key=abs)))
            self.rm.air_far_field.vol.radius_in = float(abs(max(gmsh.model.getValue(0, gmsh.model.getAdjacencies(
                    1, self.md.geometries.air_inf.lines['inner'])[1][0], []), key=abs)))
            self.rm.air.vol.name = "Air"
            self.rm.air.vol.number = pg.air
            self.rm.air_far_field.vol.names = ["AirInf"]
            self.rm.air_far_field.vol.numbers = [pg.air_inf]
            self.rm.air_far_field.surf.name = "Surface_Inf"
            self.rm.air_far_field.surf.number = pg.air_inf_bnd
            if geometry.model_dump().get('symmetry', 'none') != 'none':
                self.rm.boundaries.symmetry.normal_free.name = 'normal_free_bnd'
                self.rm.boundaries.symmetry.normal_free.number = pg.symmetric_boundaries.normal_free
                self.rm.boundaries.symmetry.tangential_free.name = 'tangent_free_bnd'
                self.rm.boundaries.symmetry.tangential_free.number = pg.symmetric_boundaries.tangential_free

        if 'use_TSA' in geometry.model_dump():
            self.rm.projection_points.name = 'projection_points'
            self.rm.projection_points.number = self.md.domains.physical_groups.half_turns_points

        # Initialize lists
        for group in ['r1_a1', 'r2_a1', 'r1_a2', 'r2_a2']:
            self.rm.powered[group] = rM.Powered()
            self.rm.powered[group].vol.names = []
            self.rm.powered[group].vol.numbers = []
            for cond_name in self.data.conductors.keys(): self.rm.powered[group].conductors[cond_name] = []
            if geometry.with_wedges:
                self.rm.induced[group] = rM.Induced()
                self.rm.induced[group].vol.names = []
                self.rm.induced[group].vol.numbers = []
            if 'bore_field' in mesh.model_dump():
                initial_current = self.data.power_supply.I_initial
                self.rm.powered[group].vol.currents = []
            if geometry.model_dump().get('use_TSA', False):
                self.rm.powered[group].surf_in.names = []
                self.rm.powered[group].surf_in.numbers = []
                self.rm.powered[group].surf_out.names = []
                self.rm.powered[group].surf_out.numbers = []
                if geometry.with_wedges:
                    self.rm.induced[group].surf_in.names = []
                    self.rm.induced[group].surf_in.numbers = []
                    self.rm.induced[group].surf_out.names = []
                    self.rm.induced[group].surf_out.numbers = []
        if geometry.with_iron_yoke:
            self.rm.iron_yoke.vol.names = []
            self.rm.iron_yoke.vol.numbers = []
        if geometry.model_dump().get('use_TSA', False):
            unique_thin_shells = []
            self.rm.thin_shells.second_group_is_next['azimuthally'] = []
            self.rm.thin_shells.second_group_is_next['radially'] = []
            self.rm.thin_shells.normals_directed['azimuthally'] = []
            self.rm.thin_shells.normals_directed['radially'] = []
        else:
            self.rm.insulator.vol.names = []
            self.rm.insulator.vol.numbers = []
            self.rm.insulator.surf.names = []
            self.rm.insulator.surf.numbers = []

        if geometry.model_dump().get('use_TSA', False):
            # Categorize insulation types
            min_h = mesh.insulation.global_size
            # min_h = 1
            # for conductor in self.data.conductors.keys():
            #     min_h = min([self.data.conductors[conductor].cable.th_insulation_along_height,
            #                  self.data.conductors[conductor].cable.th_insulation_along_width, min_h])
            min_h_QH = mesh.insulation.TSA.global_size_QH if mesh.insulation.TSA.global_size_QH else min_h

            # Conductor insulation layers
            for el, ins in self.ins_type_cond.items():
                cond = self.data.conductors[self.wedge_cond[int(el[1:])]].cable if 'w' in el else self.data.conductors[pg.blocks[int(el)].conductor].cable
                for ins_side, tags in ins.items():
                    if tags:
                        side_ins_type = [cond.material_insulation]
                        if ins_side in ['inner', 'outer']: side_ins = [cond.th_insulation_along_width]
                        elif ins_side in ['higher', 'lower']: side_ins = [cond.th_insulation_along_height]
                        else:  # mid_turn
                            side_ins = [cond.th_insulation_along_height, cond.th_insulation_along_height]
                            side_ins_type.append(cond.material_insulation)
                        if ins_side[0] in 'iohl' and el + ins_side[0] in self.data.magnet.solve.thermal.insulation_TSA.exterior.blocks:
                            add_mat_idx = self.data.magnet.solve.thermal.insulation_TSA.exterior.blocks.index(el + ins_side[0])
                            side_ins.extend(self.data.magnet.solve.thermal.insulation_TSA.exterior.thicknesses_append[add_mat_idx])
                            side_ins_type.extend(self.data.magnet.solve.thermal.insulation_TSA.exterior.materials_append[add_mat_idx])
                            if ins_side[0] in 'il': side_ins.reverse(), side_ins_type.reverse()
                        self.rm.thin_shells.insulation_types.layers_number.append(0)
                        self.rm.thin_shells.insulation_types.thin_shells.append(list(set(tags)))
                        self.rm.thin_shells.insulation_types.thicknesses.append([])
                        self.rm.thin_shells.insulation_types.layers_material.append([])
                        for nr, ins_lyr in enumerate(side_ins):
                            tsa_layers = max(mesh.insulation.TSA.minimum_discretizations, round(ins_lyr / min_h))
                            self.rm.thin_shells.insulation_types.layers_number[-1] += tsa_layers
                            self.rm.thin_shells.insulation_types.thicknesses[-1].extend([ins_lyr / tsa_layers] * tsa_layers)
                            self.rm.thin_shells.insulation_types.layers_material[-1].extend([side_ins_type[nr]] * tsa_layers)

            # Mid-pole, mid-winding, and mid-layer insulation layers
            ins_th_dict = self.md.geometries.thin_shells.ins_thickness.model_dump()
            for ins_type, ins in self.ins_type.items():
                for ins_name, tags in ins.items():
                    # Get conductors insulation
                    if ins_name.count('w') == 2:
                        el1, el2 = int(ins_name[1:ins_name.index('_')]), int(ins_name[ins_name.index('_') + 2:])
                        cond1 = self.data.conductors[self.wedge_cond[el1]].cable
                        cond2 = self.data.conductors[self.wedge_cond[el2]].cable
                    elif ins_name.count('w') == 1:
                        el1, el2 = int(ins_name[1:ins_name.index('_')]), int(ins_name[ins_name.index('_') + 1:])
                        cond1 = self.data.conductors[self.wedge_cond[el1]].cable
                        cond2 = self.data.conductors[pg.blocks[el2].conductor].cable
                        if ins_name in self.md.geometries.thin_shells.mid_layers_ht_to_wdg: cond1, cond2 = cond2, cond1
                    else:
                        el1, el2 = int(ins_name[:ins_name.index('_')]), int(ins_name[ins_name.index('_') + 1:])
                        cond1 = self.data.conductors[pg.blocks[el1].conductor].cable
                        cond2 = self.data.conductors[pg.blocks[el2].conductor].cable
                    if ins_type in ['mid_layer', 'aux']:
                        cond_ins1, cond_ins2 = cond1.th_insulation_along_width, cond2.th_insulation_along_width
                    else:
                        cond_ins1, cond_ins2 = cond1.th_insulation_along_height, cond2.th_insulation_along_height
                    # Get insulation layer thickness
                    mid_materials, mid_thicknesses = _get_input_insulation_data(ins_name, i_type=ins_type)
                    ins_thickness = ins_th_dict['mid_layer'][ins_name] / 2 if ins_type == 'aux' else ins_th_dict[ins_type][ins_name]
                    mid_lyr_th, null_idx = _compute_insulation_thicknesses(ins_thickness, cond_ins1 + cond_ins2)
                    for idx in null_idx: mid_lyr_th.pop(idx), mid_materials.pop(idx)
                    side_ins = [cond_ins1] + mid_lyr_th + [cond_ins2]
                    # Get insulation materials
                    side_ins_type = [cond1.material_insulation] + mid_materials + [cond2.material_insulation]
                    # Initialize sublists
                    self.rm.thin_shells.insulation_types.layers_number.append(0)
                    self.rm.thin_shells.insulation_types.thin_shells.append(list(set(tags)))
                    self.rm.thin_shells.insulation_types.thicknesses.append([])
                    self.rm.thin_shells.insulation_types.layers_material.append([])
                    for nr, ins_lyr in enumerate(side_ins):
                        tsa_layers = max(mesh.insulation.TSA.minimum_discretizations, round(ins_lyr / min_h))
                        self.rm.thin_shells.insulation_types.layers_number[-1] += tsa_layers
                        self.rm.thin_shells.insulation_types.thicknesses[-1].extend([ins_lyr / tsa_layers] * tsa_layers)
                        self.rm.thin_shells.insulation_types.layers_material[-1].extend([side_ins_type[nr]] * tsa_layers)

            # Quench heater insulation layers
            for ins_type, ins in self.ins_type_qh.items():
                for qh_nr, ts_groups in ins.items():
                    for ts_name, tags in ts_groups.items():
                        if ins_type != 'external': mid_materials, mid_thicknesses = _get_input_insulation_data(ts_name)
                        if tags:
                            if ins_type == 'external':
                                data = self.qh_data[qh_nr]
                                if str(ts_name) + data[ts_name]['ht_side'] in self.data.magnet.solve.thermal.insulation_TSA.exterior.blocks:
                                    add_mat_idx = self.data.magnet.solve.thermal.insulation_TSA.exterior.blocks.index(str(ts_name) + data[ts_name]['ht_side'])
                                    additional_ths = self.data.magnet.solve.thermal.insulation_TSA.exterior.thicknesses_append[add_mat_idx]
                                    additional_mats = self.data.magnet.solve.thermal.insulation_TSA.exterior.materials_append[add_mat_idx]
                                else: additional_ths, additional_mats = [], []
                                cond = self.data.conductors[data[ts_name]['conductor']].cable
                                ht_ins_th = cond.th_insulation_along_width if data[ts_name]['ht_side'] in 'io' else cond.th_insulation_along_height
                                side_ins = [ht_ins_th] + [h_ins for h_ins in qh.h_ins[qh_nr - 1]] + [qh.h[qh_nr - 1]] + [h_ground_ins for h_ground_ins in qh.h_ground_ins[qh_nr - 1]] + additional_ths
                                side_ins_type = [cond.material_insulation] + [type_ins for type_ins in qh.type_ins[qh_nr - 1]] + ['SS'] +\
                                                [type_ground_ins for type_ground_ins in qh.type_ground_ins[qh_nr - 1]] + additional_mats
                                if data[ts_name]['ht_side'] in 'il': side_ins.reverse(), side_ins_type.reverse()
                                qh_list = [qh_nr]
                            elif ins_type == 'internal':
                                data = self.qh_data[qh_nr]
                                cond = self.data.conductors[data[ts_name]['conductor']].cable
                                cond2 = self.data.conductors[self.wedge_cond[int(ts_name.split('_')[0][1:])] if 'w' in ts_name
                                                             else pg.blocks[int(ts_name.split('_')[1]) if data[ts_name]['ht_side'] == 'o' else int(ts_name.split('_')[0])].conductor].cable
                                side_ins_qh = [h_ins for h_ins in qh.h_ins[qh_nr - 1]] + [qh.h[qh_nr - 1]] + [h_ground_ins for h_ground_ins in qh.h_ground_ins[qh_nr - 1]]
                                mid_lyr_th, null_idx = _compute_insulation_thicknesses(
                                    ins_th_dict['mid_layer'][ts_name], sum([cond.th_insulation_along_width, cond2.th_insulation_along_width] + side_ins_qh))
                                for idx in null_idx: mid_lyr_th.pop(idx), mid_materials.pop(idx)
                                side_ins = [cond.th_insulation_along_width] + side_ins_qh + mid_lyr_th + [cond2.th_insulation_along_width]
                                side_ins_type = [cond.material_insulation] + [type_ins for type_ins in qh.type_ins[qh_nr - 1]] + ['SS'] +\
                                                [type_ground_ins for type_ground_ins in qh.type_ground_ins[qh_nr - 1]] + mid_materials + [cond2.material_insulation]
                                if data[ts_name]['ht_side'] == 'i': side_ins.reverse(), side_ins_type.reverse()
                                qh_list = [qh_nr]
                            elif ins_type == 'internal_double':
                                qh_nr1, qh_nr2 = int(qh_nr.split('_')[0]), int(qh_nr.split('_')[1])
                                data, data2 = self.qh_data[qh_nr1], self.qh_data[qh_nr2]
                                cond = self.data.conductors[data[ts_name]['conductor']].cable
                                cond2 = self.data.conductors[data2[ts_name]['conductor']].cable
                                side_ins_qh = [h_ins for h_ins in qh.h_ins[qh_nr1 - 1]] + [qh.h[qh_nr1 - 1]] + [h_ground_ins for h_ground_ins in qh.h_ground_ins[qh_nr1 - 1]]
                                side_ins_qh2 = [h_ground_ins for h_ground_ins in qh.h_ground_ins[qh_nr2 - 1][::-1]] + [qh.h[qh_nr2 - 1]] + [h_ins for h_ins in qh.h_ins[qh_nr2 - 1][::-1]]
                                mid_lyr_th, null_idx = _compute_insulation_thicknesses(
                                    ins_th_dict['mid_layer'][ts_name], sum([cond.th_insulation_along_width, cond2.th_insulation_along_width] + side_ins_qh + side_ins_qh2))
                                for idx in null_idx: mid_lyr_th.pop(idx), mid_materials.pop(idx)
                                side_ins = [cond.th_insulation_along_width] + side_ins_qh + mid_lyr_th + side_ins_qh2 + [cond2.th_insulation_along_width]
                                side_ins_type = [cond.material_insulation] + [type_ins for type_ins in qh.type_ins[qh_nr1 - 1]] + ['SS'] +\
                                                [type_ground_ins for type_ground_ins in qh.type_ground_ins[qh_nr1 - 1]] + mid_materials +\
                                                [type_ground_ins for type_ground_ins in qh.type_ground_ins[qh_nr2 - 1][::-1]] + ['SS'] +\
                                                [type_ins for type_ins in qh.type_ins[qh_nr2 - 1][::-1]] + [cond2.material_insulation]
                                qh_list = [qh_nr1, qh_nr2]
                            qh_labels = [1 if m == 'SS' else None for m in side_ins_type]
                            ss_indexes = [index for index, value in enumerate(qh_labels) if value == 1]
                            for nr, idx in enumerate(ss_indexes): qh_labels[idx] = qh_list[nr]
                            self.rm.thin_shells.quench_heaters.layers_number.append(0)
                            self.rm.thin_shells.quench_heaters.thin_shells.append(list(set(tags)))
                            self.rm.thin_shells.quench_heaters.thicknesses.append([])
                            self.rm.thin_shells.quench_heaters.layers_material.append([])
                            self.rm.thin_shells.quench_heaters.label.append([])
                            for nr, ins_lyr in enumerate(side_ins):
                                tsa_layers = max(mesh.insulation.TSA.minimum_discretizations_QH, round(ins_lyr / min_h_QH))
                                self.rm.thin_shells.quench_heaters.layers_number[-1] += tsa_layers
                                self.rm.thin_shells.quench_heaters.thicknesses[-1].extend([ins_lyr / tsa_layers] * tsa_layers)
                                self.rm.thin_shells.quench_heaters.layers_material[-1].extend([side_ins_type[nr]] * tsa_layers)
                                self.rm.thin_shells.quench_heaters.label[-1].extend([qh_labels[nr]] * tsa_layers)

        # Powered
        for blk_nr, blk in pg.blocks.items():
            ht_list = list(blk.half_turns.keys())
            for ht_nr, ht in blk.half_turns.items():
                ht_name = f"ht{ht_nr}_{'EM' if 'bore_field' in mesh.model_dump() else 'TH'}"
                self.rm.powered[ht.group].conductors[blk.conductor].append(ht_name)
                self.rm.powered[ht.group].vol.names.append(ht_name)
                self.rm.powered[ht.group].vol.numbers.append(ht.tag)
                if 'bore_field' in mesh.model_dump():
                    self.rm.powered[ht.group].vol.currents.append(initial_current * (1 if blk.current_sign > 0 else -1))
                if geometry.model_dump().get('use_TSA', False):
                    for line in ['l', 'i', 'o', 'h']:
                        # Bare edges
                        self.rm.powered[ht.group].surf_in.names.append(ht_name + line)
                        self.rm.powered[ht.group].surf_in.numbers.append(ht.lines[line])
                        if line in 'io': self.rm.thin_shells.normals_directed['radially'].append(ht.lines[line])
                        else: self.rm.thin_shells.normals_directed['azimuthally'].append(ht.lines[line])
                    # Auxiliary thin shells
                    for line_name, line_tag in ht.aux_lines.items():
                        self.rm.powered[ht.group].surf_in.names.append(line_name)
                        self.rm.powered[ht.group].surf_in.numbers.append(line_tag)
                        self.rm.thin_shells.normals_directed['radially'].append(line_tag)
                    # Thin shells
                    for line_name, line_tag in dict(ht.mid_layer_lines.inner, **ht.mid_layer_lines.outer).items():
                        self.rm.powered[ht.group].surf_out.names.append(line_name)
                        self.rm.powered[ht.group].surf_out.numbers.append(line_tag)
                        self.rm.thin_shells.normals_directed['radially'].append(line_tag)
                    for line_name, line_tag in dict(ht.mid_pole_lines, **ht.mid_winding_lines, **ht.mid_turn_lines).items():
                        self.rm.powered[ht.group].surf_out.names.append(line_name)
                        self.rm.powered[ht.group].surf_out.numbers.append(line_tag)
                        self.rm.thin_shells.normals_directed['azimuthally'].append(line_tag)

                    # Which thin shells or exterior conductor edges precede a second group (r2 or a2)
                    if ht.group[1] == '2':
                        # mid-turn thin shells precede r2
                        for line_name, line_tag in ht.mid_turn_lines.items():
                            if (ht_list.index(ht_nr) != 0 and int(line_name[line_name.index('_') + 1:]) == ht_nr) or\
                                    (ht_list.index(ht_nr) == 0 and 'w' in line_name):
                                self.rm.thin_shells.second_group_is_next['azimuthally'].append(line_tag)
                        # mid-pole thin shells precede r2
                        if ht_list.index(ht_nr) == 0 and ht.mid_pole_lines:
                            self.rm.thin_shells.second_group_is_next['azimuthally'].append(list(ht.mid_pole_lines.values())[0])
                        # conductor edges precede r2
                        elif ht_list.index(ht_nr) == 0 and len(ht.mid_turn_lines) + len(ht.mid_winding_lines) + len(ht.mid_pole_lines) == 1:
                            self.rm.thin_shells.second_group_is_next['azimuthally'].append(ht.lines['l'])
                        # mid-winding thin shells precede r2
                        for line_name, line_tag in ht.mid_winding_lines.items():
                            if int(line_name[line_name.index('_') + 1:]) == ht_nr:
                                self.rm.thin_shells.second_group_is_next['azimuthally'].append(line_tag)
                    elif ht_list.index(ht_nr) == len(ht_list) - 1:
                        # mid-turn thin shells precede r2
                        for line_name, line_tag in ht.mid_turn_lines.items():
                            if 'w' in line_name:
                                self.rm.thin_shells.second_group_is_next['azimuthally'].append(line_tag)
                        # conductor edges precede r2
                        if len(ht.mid_turn_lines) + len(ht.mid_winding_lines) + len(ht.mid_pole_lines) == 1:
                            self.rm.thin_shells.second_group_is_next['azimuthally'].append(ht.lines['h'])
                    if ht.group[4] == '2':
                        # mid-layer thin shells precede a2
                        for line_name, line_tag in ht.mid_layer_lines.inner.items():
                            self.rm.thin_shells.second_group_is_next['radially'].append(line_tag)
                    elif not ht.mid_layer_lines.outer:
                        # conductor edges precede a2
                        self.rm.thin_shells.second_group_is_next['radially'].append(ht.lines['o'])

        if geometry.model_dump().get('use_TSA', False):
            for group in ['r1_a1', 'r2_a1', 'r1_a2', 'r2_a2']:
                unique_thin_shells.extend(self.rm.powered[group].surf_out.numbers)

        # Wedges
        if geometry.with_wedges:
            for wdg_nr, wdg in pg.wedges.items():
                wdg_name = f"w{wdg_nr}_{'EM' if 'bore_field' in mesh.model_dump() else 'TH'}"
                self.rm.induced[wdg.group].vol.names.append(wdg_name)
                self.rm.induced[wdg.group].vol.numbers.append(wdg.tag)
                if geometry.model_dump().get('use_TSA', False):
                    # Bare edges
                    for line in ['l', 'i', 'o', 'h']:
                        self.rm.induced[wdg.group].surf_in.names.append(wdg_name + line)
                        self.rm.induced[wdg.group].surf_in.numbers.append(wdg.lines[line])
                        if line in 'io':
                            self.rm.thin_shells.normals_directed['radially'].append(wdg.lines[line])
                        else:
                            self.rm.thin_shells.normals_directed['azimuthally'].append(wdg.lines[line])
                    # Auxiliary thin shells
                    for line_name, line_tag in wdg.aux_lines.items():
                        self.rm.induced[wdg.group].surf_in.names.append(line_name)
                        self.rm.induced[wdg.group].surf_in.numbers.append(line_tag)
                        self.rm.thin_shells.normals_directed['radially'].append(line_tag)
                    # Thin shells
                    for line_name, line_tag in dict(wdg.mid_layer_lines.inner, **wdg.mid_layer_lines.outer).items():
                        self.rm.induced[wdg.group].surf_out.names.append(line_name)
                        self.rm.induced[wdg.group].surf_out.numbers.append(line_tag)
                        self.rm.thin_shells.normals_directed['radially'].append(line_tag)
                    for line_name, line_tag in wdg.mid_turn_lines.items():
                        self.rm.induced[wdg.group].surf_out.names.append(line_name)
                        self.rm.induced[wdg.group].surf_out.numbers.append(line_tag)
                        self.rm.thin_shells.normals_directed['azimuthally'].append(line_tag)
                    # Which thin shells or exterior conductor edges precede a second group (r2 or a2)
                    if wdg.group[4] == '2':
                        for line_name, line_tag in wdg.mid_layer_lines.inner.items():
                            if line_name.count('w') == 2:
                                self.rm.thin_shells.second_group_is_next['radially'].append(line_tag)
                    elif not wdg.mid_layer_lines.outer:
                        self.rm.thin_shells.second_group_is_next['radially'].append(wdg.lines['o'])
            if geometry.model_dump().get('use_TSA', False):
                for group in ['r1_a1', 'r2_a1', 'r1_a2', 'r2_a2']:
                    unique_thin_shells.extend(self.rm.induced[group].surf_out.numbers)

        # Unique mid layers
        if geometry.model_dump().get('use_TSA', False):
            self.rm.thin_shells.mid_turns_layers_poles = list(set(unique_thin_shells))

        # Insulation
        for group_name, surface in pg.insulations.surfaces.items():
            self.rm.insulator.vol.names.append('ins' + group_name)
            self.rm.insulator.vol.numbers.append(surface)
        if 'insulation' in mesh.model_dump() and 'TSA' in mesh.model_dump()["insulation"]:
            for group_name, curve in pg.insulations.curves.items():
                self.rm.insulator.surf.names.append('ins' + group_name)
                self.rm.insulator.surf.numbers.append(curve)

        # Iron
        for group_name, surface in pg.iron.surfaces.items():
            self.rm.iron_yoke.vol.names.append(group_name)
            self.rm.iron_yoke.vol.numbers.append(surface)

        # Boundary conditions
        if 'insulation' in mesh.model_dump() and 'TSA' in mesh.model_dump()["insulation"]:
            # Initialize lists
            for bc_data, bc_rm in zip(self.data.magnet.solve.thermal.overwrite_boundary_conditions, self.rm.boundaries.thermal):  # b.c. type
                bc_rm[1].bc.names = []
                bc_rm[1].bc.numbers = []
                if bc_data[0] == 'cooling':
                    bc_rm[1].bc.values = []
                    for group in ['1_r1_a1', '2_r1_a1', '1_r2_a1', '2_r2_a1', '1_r1_a2', '2_r1_a2', '1_r2_a2', '2_r2_a2']:
                        bc_rm[1].groups[group] = []
                else:
                    bc_rm[1].bc.value = []
                for group in ['r1_a1', 'r2_a1', 'r1_a2', 'r2_a2']:
                    bc_rm[1].groups[group] = []

            # Apply general cooling and adiabatic
            if self.data.magnet.solve.thermal.He_cooling.enabled:
                cooling_side = {'i': any(coil_side in self.data.magnet.solve.thermal.He_cooling.sides for coil_side in ['inner', 'external']),
                                'o': any(coil_side in self.data.magnet.solve.thermal.He_cooling.sides for coil_side in ['outer', 'external']),
                                'hl': self.data.magnet.solve.thermal.He_cooling.sides == 'external'}
            else:
                cooling_side = {'i': False, 'o': False, 'hl': False}

            def __assign_bnd_tag(el, name, side, bc_type, tag=None):
                line_tag = tag if tag else el.lines[side]
                bnd_list_names[bc_type].append(name + side)
                bnd_list_numbers[bc_type].append(line_tag)
                if side in 'io': new_group = el.group[:3] + 'a1' if el.group[4] == '2' else el.group[:3] + 'a2'
                else: new_group = 'r1' + el.group[2:] if el.group[1] == '2' else 'r2' + el.group[2:]
                bc_rm[bc_type].groups[new_group].append(line_tag)
                for group_name, group in self.rm.thin_shells.groups.items():
                    if line_tag in group:
                        bc_rm[bc_type].groups[el.group[0] + '_' + new_group].append(line_tag)
                        break

            bc_rm = {'Robin': self.rm.boundaries.thermal.cooling, 'Neumann': self.rm.boundaries.thermal.heat_flux}
            bnd_list_names = {'Robin': [], 'Neumann': []}
            bnd_list_numbers = {'Robin': [], 'Neumann': []}
            if geometry.model_dump().get('use_TSA', False):
                # Half turn boundaries
                for coil_nr, coil in self.md.geometries.coil.anticlockwise_order.coils.items():
                    for lyr_nr, orders in coil.layers.items():
                        for order in orders:
                            ht_list = list(pg.blocks[order.block].half_turns.keys())
                            for ht_nr, ht in pg.blocks[order.block].half_turns.items():
                                if not ht.mid_layer_lines.inner:
                                    __assign_bnd_tag(ht, 'ht' + str(ht_nr), 'i', 'Robin' if cooling_side['i'] else 'Neumann')
                                if not ht.mid_layer_lines.outer:
                                    __assign_bnd_tag(ht, 'ht' + str(ht_nr), 'o', 'Robin' if cooling_side['o'] else 'Neumann')
                                if ht_list.index(ht_nr) == 0 and len(ht.mid_turn_lines) + len(ht.mid_winding_lines) + len(ht.mid_pole_lines) == 1:
                                    __assign_bnd_tag(ht, 'ht' + str(ht_nr), 'l', 'Robin' if cooling_side['hl'] else 'Neumann')
                                if ht_list.index(ht_nr) == len(ht_list) - 1 and len(ht.mid_turn_lines) + len(ht.mid_winding_lines) + len(ht.mid_pole_lines) == 1:
                                    __assign_bnd_tag(ht, 'ht' + str(ht_nr), 'h', 'Robin' if cooling_side['hl'] else 'Neumann')
                                if ht.aux_lines:
                                    __assign_bnd_tag(ht, 'ht' + str(ht_nr), 'o', 'Robin' if cooling_side['hl'] else 'Neumann', list(ht.aux_lines.values())[0])
                # Wedge boundaries
                for wdg_nr, wdg in pg.wedges.items():
                    if not wdg.mid_layer_lines.inner:
                        __assign_bnd_tag(wdg, 'wd' + str(wdg_nr), 'i', 'Robin' if cooling_side['i'] else 'Neumann')
                    if not wdg.mid_layer_lines.outer:
                        __assign_bnd_tag(wdg, 'wd' + str(wdg_nr), 'o', 'Robin' if cooling_side['o'] else 'Neumann')
                    if wdg.aux_lines:
                        __assign_bnd_tag(wdg, 'wd' + str(wdg_nr), 'o', 'Robin' if cooling_side['hl'] else 'Neumann', list(wdg.aux_lines.values())[0])
            else:  # insulation case
                for curves_group, tag in pg.insulations.curves.items():
                    if self.data.magnet.solve.thermal.He_cooling.enabled:
                        if self.data.magnet.solve.thermal.He_cooling.sides == 'external': bc_type = 'Robin'
                        else:
                            raise ValueError(f"Cooling side '{self.data.magnet.solve.thermal.He_cooling.sides}' is not supported for meshed insulation models.")
                        # bc_type = 'Robin' if (self.data.magnet.solve.thermal.He_cooling.sides == 'external' or
                        #                       ('inner' in self.data.magnet.solve.thermal.He_cooling.sides and curves_group[-1] == 'i') or
                        #                       ('outer' in self.data.magnet.solve.thermal.He_cooling.sides and curves_group[-1] == 'o')) else 'Neumann'
                    else:
                        bc_type = 'Neumann'
                    bnd_list_names[bc_type].append('ins' + curves_group)
                    bnd_list_numbers[bc_type].append(tag)
            if self.data.magnet.solve.thermal.He_cooling.enabled:
                bc_rm['Robin'].bc.names.append(bnd_list_names['Robin'])
                bc_rm['Robin'].bc.numbers.append(bnd_list_numbers['Robin'])
                bc_rm['Robin'].bc.values.append([self.data.magnet.solve.thermal.He_cooling.heat_transfer_coefficient,
                                                 self.data.magnet.solve.thermal.init_temperature])
            if bnd_list_names['Neumann']:
                bc_rm['Neumann'].bc.names.append(bnd_list_names['Neumann'])
                bc_rm['Neumann'].bc.numbers.append(bnd_list_numbers['Neumann'])
                bc_rm['Neumann'].bc.value.append(0.)

            # Apply specific boundary conditions
            for bc_data, bc_rm in zip(self.data.magnet.solve.thermal.overwrite_boundary_conditions, self.rm.boundaries.thermal):  # b.c. type
                # bc_data is a tuple like: ('temperature', {'const_T1': boundaries, value)})
                # bc_rm is a tuple like: ('temperature', DirichletCondition(names, numbers, value))

                for _, bc in bc_data[1].items():  # all boundary conditions of one b.c. type (e.g., Dirichlet with different temperatures)
                    bnd_list_names = []
                    bnd_list_numbers = []
                    if geometry.model_dump().get('use_TSA', False):
                        for bnd in bc.boundaries:  # all boundaries of one boundary condition
                            if bnd[0] == 'w':
                                if not geometry.with_wedges:
                                    raise Exception('Wedge regions are disabled.')
                                # Fetch the physical group of the wedge
                                pg_el = pg.wedges[int(bnd[1:-1])]
                                name = 'wd' + bnd[1:]
                            else:
                                # Fetch the physical group of the half turn
                                ht_index = self.strands['ht'].index(int(bnd[:-1]))
                                pg_el = pg.blocks[self.strands['block'][ht_index]].half_turns[int(bnd[:-1])]
                                name = 'ht' + bnd
                            line_pg_tag = pg_el.lines[bnd[-1]]
                            bnd_list_names.append(name)
                            bnd_list_numbers.append(line_pg_tag)
                            # Find the half turn group this boundary is assigned to and take the complementary
                            if bnd[-1] in 'io':
                                new_group = pg_el.group[:3] + 'a1' if pg_el.group[4] == '2' else pg_el.group[:3] + 'a2'
                            else:  # ['l', 'h'] todo: if applied to an inner line (i.e., not domain boundaries), extra code needed because the line would belong to two groups
                                new_group = 'r1' + pg_el.group[2:] if pg_el.group[1] == '2' else 'r2' + pg_el.group[2:]
                            # Overwrite general cooling and adiabatic condition
                            if self.data.magnet.solve.thermal.He_cooling.enabled:
                                if name in self.rm.boundaries.thermal.cooling.bc.names[0]:
                                    bnd_idx = self.rm.boundaries.thermal.cooling.bc.names[0].index(name)
                                    self.rm.boundaries.thermal.cooling.bc.names[0].pop(bnd_idx)
                                    bnd_idx = self.rm.boundaries.thermal.cooling.bc.numbers[0].pop(bnd_idx)
                                    self.rm.boundaries.thermal.cooling.groups[new_group].pop(
                                        self.rm.boundaries.thermal.cooling.groups[new_group].index(bnd_idx))
                            if self.data.magnet.solve.thermal.He_cooling.sides != 'external':
                                if name in self.rm.boundaries.thermal.heat_flux.bc.names[0]:
                                    bnd_idx = self.rm.boundaries.thermal.heat_flux.bc.names[0].index(name)
                                    self.rm.boundaries.thermal.heat_flux.bc.names[0].pop(bnd_idx)
                                    bnd_idx = self.rm.boundaries.thermal.heat_flux.bc.numbers[0].pop(bnd_idx)
                                    self.rm.boundaries.thermal.heat_flux.groups[new_group].pop(
                                        self.rm.boundaries.thermal.heat_flux.groups[new_group].index(bnd_idx))
                            # Assign the tag
                            bc_rm[1].groups[new_group].append(line_pg_tag)
                            # Extra grouping for Robin virtual shells
                            if bc_data[0] == 'cooling':
                                for group_name, group in self.rm.thin_shells.groups.items():
                                    if line_pg_tag in group:
                                        bc_rm[1].groups[group_name[0] + '_' + new_group].append(line_pg_tag)
                                        break
                    else:  # the b.c. are assigned to insulation boundaries instead
                        pass  # todo: not supported yet
                    bc_rm[1].bc.names.append(bnd_list_names)
                    bc_rm[1].bc.numbers.append(bnd_list_numbers)
                    if bc_data[0] == 'cooling':
                        bc_rm[1].bc.values.append([bc.heat_transfer_coefficient, self.data.magnet.solve.thermal.init_temperature])
                    elif bc_data[0] == 'temperature':
                        bc_rm[1].bc.value.append(bc.const_temperature)
                    elif bc_data[0] == 'heat_flux':
                        bc_rm[1].bc.value.append(bc.const_heat_flux)

    def setMeshOptions(self, run_type):
        """
            Meshes the generated domain
        """
        mesh = self.data.magnet.mesh
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.Algorithm", 6)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)

    def generateMesh(self):
        gmsh.option.setNumber("General.Terminal", self.verbose)
        self.mesh.generate(2)
        # self.mesh.removeDuplicateNodes()
        # self.occ.synchronize()
        # self.gu.launch_interactive_GUI()

    def checkMeshQuality(self):
        tags = self.mesh.getElements(2)[1][0]

        self.mesh_parameters['SJ'] = min(self.mesh.getElementQualities(elementTags=tags, qualityName='minSJ'))
        self.mesh_parameters['SICN'] = min(self.mesh.getElementQualities(elementTags=tags, qualityName='minSICN'))
        self.mesh_parameters['SIGE'] = min(self.mesh.getElementQualities(elementTags=tags, qualityName='minSIGE'))
        self.mesh_parameters['Gamma'] = min(self.mesh.getElementQualities(elementTags=tags, qualityName='gamma'))
        self.mesh_parameters['nodes'] = len(self.mesh.getNodes()[0])

        # gmsh.plugin.setNumber("AnalyseMeshQuality", "JacobianDeterminant", 1)
        # gmsh.plugin.setNumber("AnalyseMeshQuality", "CreateView", 100)
        # test = gmsh.plugin.run("AnalyseMeshQuality")
        # test2 = gmsh.view.getModelData(test, test)

        # gmsh.logger.getLastError()
        # gmsh.logger.get()

    def saveClosestNeighboursList(self):

        def _closest_node_on_reference(origin_points, reference_points):
            """
            Compute list of lists with each list representing one original node (3 entries for 3 coordinates) and the closest
            reference mesh node (3 entries for 3 coordinates).
            :param origin_points: list of origin point as list of 3 floats per origin node
            :param reference_points: list of coordinates of reference mesh points as list of 3 floats per reference mesh node
            :return: returns list of lists with the closest reference mesh node per origin node
            """
            closest_node = []
            for x in range(0, len(origin_points), 3):
                origin_point = origin_points[x:x + 3]
                # Compute distance list between origin point and reference point list
                dist_lst = [Func.points_distance(origin_point, reference_points[y:y + 3]) for y in range(0, len(reference_points), 3)]
                min_idx = 3 * np.argmin(dist_lst)
                closest_node.append(origin_point + reference_points[min_idx:min_idx + 3])
            return closest_node

        def _get_closest_nodes(side):
            origin_list = self.mesh.getNodesForPhysicalGroup(1, mid_layer)[1].tolist()
            reference_list = self.mesh.getNodesForPhysicalGroup(1, el.lines[side])[1].tolist()
            self.rc.neighbouring_nodes.groups[group].extend(
                [node for node_list in _closest_node_on_reference(origin_list, reference_list) for node in node_list])

        logger.info(f"Info    : {self.data.general.magnet_name} - F i n d i n g   C l o s e s t   N e i g h b o u r s . . .")
        logger.info(f"Info    : Finding closest reference nodes ...")

        self.rc.neighbouring_nodes.groups['1_1'] = []
        self.rc.neighbouring_nodes.groups['2_1'] = []
        self.rc.neighbouring_nodes.groups['1_2'] = []
        self.rc.neighbouring_nodes.groups['2_2'] = []

        for blk_nr, blk in self.md.domains.physical_groups.blocks.items():
            for ht_nr, el in blk.half_turns.items():
                ht_list = list(blk.half_turns.keys())
                group = el.group[1] + '_' + el.group[-1]
                for line_name, mid_layer in el.mid_layer_lines.inner.items(): _get_closest_nodes('i')
                for line_name, mid_layer in el.mid_layer_lines.outer.items(): _get_closest_nodes('o')
                for line_name, mid_layer in el.aux_lines.items(): _get_closest_nodes('o')
                for line_name, mid_layer in el.mid_pole_lines.items(): _get_closest_nodes('l' if ht_list.index(ht_nr) == 0 else 'h')
                for line_name, mid_layer in el.mid_winding_lines.items(): _get_closest_nodes('l' if ht_list.index(ht_nr) == 0 else 'h')
                for line_name, mid_layer in el.mid_turn_lines.items():
                    high = ht_list.index(ht_nr) == len(ht_list) - 1 if 'w' in line_name\
                        else int(line_name[:line_name.index('_')]) == ht_nr
                    _get_closest_nodes('h' if high else 'l')
        for wdg_nr, el in self.md.domains.physical_groups.wedges.items():
            group = el.group[1] + '_' + el.group[-1]
            for line_name, mid_layer in el.mid_layer_lines.inner.items(): _get_closest_nodes('i')
            for line_name, mid_layer in el.mid_layer_lines.outer.items(): _get_closest_nodes('o')
            for line_name, mid_layer in el.aux_lines.items(): _get_closest_nodes('o')
            for line_name, mid_layer in el.mid_turn_lines.items():
                _get_closest_nodes('l' if line_name == list(el.mid_turn_lines.keys())[0] else 'h')

        logger.info(f"Info    : {self.data.general.magnet_name} - E n d   F i n d i n g   C l o s e s t   N e i g h b o u r s")

    def selectMeshNodes(self, elements: str):

        logger.info(f"Info    : {self.data.general.magnet_name} - S e l e c t i n g   M e s h   N o d e s . . .")
        logger.info(f"Info    : Selecting a mesh node per isothermal {elements[:-1]} ...")

        if elements == 'conductors':
            bare_mesh = {'1_1': self.rm.powered['r1_a1'].vol.numbers, '2_1': self.rm.powered['r2_a1'].vol.numbers,
                         '1_2': self.rm.powered['r1_a2'].vol.numbers, '2_2': self.rm.powered['r2_a2'].vol.numbers}
            groups = self.rc.isothermal_nodes.conductors

            # dir + robin + mid_layers
            # potentially all thin shell lines if easier
            line_tags = self.rm.boundaries.thermal.temperature.groups['r1_a1'] + \
                        self.rm.boundaries.thermal.temperature.groups['r1_a2'] + \
                        self.rm.boundaries.thermal.temperature.groups['r2_a1'] + \
                        self.rm.boundaries.thermal.temperature.groups['r2_a2'] + \
                        self.rm.boundaries.thermal.cooling.groups['r1_a1'] + \
                        self.rm.boundaries.thermal.cooling.groups['r1_a2'] + \
                        self.rm.boundaries.thermal.cooling.groups['r2_a1'] + \
                        self.rm.boundaries.thermal.cooling.groups['r2_a2'] + \
                        self.rm.thin_shells.mid_turns_layers_poles
            for tag in line_tags:
                coords = list(self.mesh.getNodesForPhysicalGroup(dim=1, tag=tag)[1])[:3]
                self.rc.isothermal_nodes.thin_shells[tag] = [float(coords[0]), float(coords[1]), float(coords[2])]

        elif elements == 'wedges':
            bare_mesh = {'1_1': self.rm.induced['r1_a1'].vol.numbers, '2_1': self.rm.induced['r2_a1'].vol.numbers,
                         '1_2': self.rm.induced['r1_a2'].vol.numbers, '2_2': self.rm.induced['r2_a2'].vol.numbers}
            groups = self.rc.isothermal_nodes.wedges
        else:
            bare_mesh = {}
            groups = {}

        for group, tags_list in bare_mesh.items():
            groups[group] = {}
            for tag in tags_list:
                coords = list(self.mesh.getNodesForPhysicalGroup(dim=2, tag=tag)[1])[:3]
                groups[group][tag] = [float(coords[0]), float(coords[1]), float(coords[2])]

            for tag in self.rm.boundaries.thermal.cooling.groups['r' + group[0] + '_' + 'a' + group[-1]]:
                coords = list(self.mesh.getNodesForPhysicalGroup(dim=1, tag=tag)[1])[:3]
                groups[group][tag] = [float(coords[0]), float(coords[1]), float(coords[2])]

        logger.info(f"Info    : {self.data.general.magnet_name} - E n d   S e l e c t i n g   M e s h   N o d e s")
        # import time
        # time.sleep(100)
        # TODO: add to pro file automatically

        # self.occ.synchronize()
        # self.gu.launch_interactive_GUI()

