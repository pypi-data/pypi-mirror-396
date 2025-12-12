import math
import os
import timeit
import json
from typing import List, Any
from pathlib import Path

import gmsh
import numpy as np
from fiqus.utils.Utils import FilesAndFolders as uff
from fiqus.utils.Utils import GmshUtils
from fiqus.data.DataWindingsCCT import WindingsInformation  # for volume information
from fiqus.data.RegionsModelFiQuS import RegionsModel


class Mesh:
    def __init__(self, fdm, verbose=True):
        """
        Class to preparing brep files by adding terminals.
        :param fdm: FiQuS data model
        :param verbose: If True more information is printed in python console.
        """
        self.cctdm = fdm.magnet
        self.model_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name

        self.geom_folder = Path(self.model_folder).parent

        self.verbose = verbose
        regions_file = os.path.join(self.geom_folder, f'{self.magnet_name}.regions')
        self.cctrm = uff.read_data_from_yaml(regions_file, RegionsModel)
        winding_info_file = os.path.join(self.geom_folder, f'{self.magnet_name}.wi')
        self.cctwi = uff.read_data_from_yaml(winding_info_file, WindingsInformation)
        self.gu = GmshUtils(self.model_folder, self.verbose)
        self.gu.initialize()
        self.model_file = f"{os.path.join(self.model_folder, self.magnet_name)}.msh"
        self.formers = []
        self.powered_vols = []
        self.air_boundary_tags = []

    def _find_surf(self, volume_tag):
        for surf in gmsh.model.getBoundary([(3, volume_tag)], oriented=False):
            _, _, zmin, _, _, zmax = gmsh.model.occ.getBoundingBox(*surf)
            z = (zmin + zmax) / 2
            if math.isclose(z, self.cctdm.geometry.air.z_min, rel_tol=1e-5) or math.isclose(z, self.cctdm.geometry.air.z_max, rel_tol=1e-5):
                return surf[1]

    def generate_physical_groups(self, gui=False):
        if self.verbose:
            print('Generating Physical Groups Started')
            start_time = timeit.default_timer()
        r_types = ['w' for _ in self.cctwi.w_names] + ['f' for _ in self.cctwi.f_names]  # needed for picking different pow_surf later on
        vol_max_loop = 0

        for i, (f_name, r_type, r_name, r_tag) in enumerate(zip(self.cctwi.w_names + self.cctwi.f_names, r_types, self.cctrm.powered['cct'].vol.names, self.cctrm.powered['cct'].vol.numbers)):
            vol_dict = json.load(open(f"{os.path.join(self.geom_folder, f_name)}.vi"))
            volumes_file = np.array(vol_dict['all'])
            vol_max_file = np.max(volumes_file)
            vols_to_use = volumes_file + vol_max_loop
            v_tags = (list(map(int, vols_to_use)))
            vol_max_loop = vol_max_file + vol_max_loop
            self.powered_vols.extend(v_tags)  # used later for meshing
            gmsh.model.addPhysicalGroup(dim=3, tags=v_tags, tag=r_tag)
            gmsh.model.setPhysicalName(dim=3, tag=r_tag, name=r_name)
            powered_in_surf = self._find_surf(v_tags[0])
            gmsh.model.addPhysicalGroup(dim=2, tags=[powered_in_surf], tag=self.cctrm.powered['cct'].surf_in.numbers[i])
            gmsh.model.setPhysicalName(dim=2, tag=self.cctrm.powered['cct'].surf_in.numbers[i], name=self.cctrm.powered['cct'].surf_in.names[i])
            powered_out_surf = self._find_surf(v_tags[-1])
            gmsh.model.addPhysicalGroup(dim=2, tags=[powered_out_surf], tag=self.cctrm.powered['cct'].surf_out.numbers[i])
            gmsh.model.setPhysicalName(dim=2, tag=self.cctrm.powered['cct'].surf_out.numbers[i], name=self.cctrm.powered['cct'].surf_out.names[i])

        vol_max_loop = v_tags[-1]

        for r_name, r_tag in zip(self.cctrm.induced['cct'].vol.names, self.cctrm.induced['cct'].vol.numbers):
            vol_max_loop += 1
            self.formers.append(vol_max_loop)
            gmsh.model.addPhysicalGroup(dim=3, tags=[vol_max_loop], tag=r_tag)
            gmsh.model.setPhysicalName(dim=3, tag=r_tag, name=r_name)

        vol_max_loop += 1
        gmsh.model.addPhysicalGroup(dim=3, tags=[vol_max_loop], tag=self.cctrm.air.vol.number)
        gmsh.model.setPhysicalName(dim=3, tag=self.cctrm.air.vol.number, name=self.cctrm.air.vol.name)
        abt = gmsh.model.getEntities(2)[-3:]
        self.air_boundary_tags = [surf[1] for surf in abt]
        gmsh.model.addPhysicalGroup(dim=2, tags=self.air_boundary_tags, tag=self.cctrm.air.surf.number)
        gmsh.model.setPhysicalName(dim=2, tag=self.cctrm.air.surf.number, name=self.cctrm.air.surf.name)

        # air_line_tags = []
        # for air_boundary_tag in self.air_boundary_tags:
        #     air_line_tags.extend(gmsh.model.getBoundary([(2, air_boundary_tag)], oriented=False)[1])
        # self.air_center_line_tags = [int(np.max(air_line_tags) + 1)]  # this assumes that the above found the lines of air boundary but not the one in the middle that is just with the subsequent tag
        # gmsh.model.addPhysicalGroup(dim=1, tags=self.air_center_line_tags, tag=self.cctrm.air.line.number)
        # gmsh.model.setPhysicalName(dim=1, tag=self.cctrm.air.line.number, name=self.cctrm.air.line.name)

        gmsh.model.occ.synchronize()
        if gui:
            self.gu.launch_interactive_GUI()
        if self.verbose:
            print(f'Generating Physical Groups Took {timeit.default_timer() - start_time:.2f} s')

    def generate_mesh(self, gui=False):
        if self.verbose:
            print('Generating Mesh Started')
            start_time = timeit.default_timer()
        # gmsh.option.setNumber("Mesh.AngleToleranceFacetOverlap", 0.01)
        gmsh.option.setNumber("Mesh.Algorithm", 5)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        gmsh.option.setNumber("Mesh.AllowSwapAngle", 20)
        line_tags_transfinite = []
        num_div_transfinite = []
        line_tags_mesh: List[Any] = []
        point_tags_mesh = []
        for vol_tag in self.powered_vols:
            vol_surf_tags = gmsh.model.getAdjacencies(3, vol_tag)[1]
            for surf_tag in vol_surf_tags:
                line_tags = gmsh.model.getAdjacencies(2, surf_tag)[1]
                # line_tags_mesh.extend(line_tags)
                line_lengths = []
                for line_tag in line_tags:
                    point_tags = gmsh.model.getAdjacencies(1, line_tag)[1]
                    if line_tag not in line_tags_mesh:
                        line_tags_mesh.append(line_tag)
                    x = []
                    y = []
                    z = []
                    for p, point_tag in enumerate(point_tags):
                        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(0, point_tag)
                        x.append((xmin + xmax) / 2)
                        y.append((ymin + ymax) / 2)
                        z.append((zmin + zmax) / 2)
                        if point_tag not in point_tags_mesh:
                            point_tags_mesh.append(point_tag)
                    line_lengths.append(math.sqrt((x[0] - x[1]) ** 2 + (y[0] - y[1]) ** 2 + (z[0] - z[1]) ** 2))
                    # num_div = math.ceil(dist / self.cctdm.mesh_generators.MeshSizeWindings) + 1
                l_length_min = np.min(line_lengths)
                for line_tag, l_length in zip(line_tags, line_lengths):
                    aspect = l_length / l_length_min
                    if aspect > self.cctdm.mesh.MaxAspectWindings:
                        num_div = math.ceil(l_length / (l_length_min * self.cctdm.mesh.MaxAspectWindings)) + 1
                        if line_tag in line_tags_transfinite:
                            idx = line_tags_transfinite.index(line_tag)
                            num_div_set = num_div_transfinite[idx]
                            if num_div_set < num_div:
                                num_div_transfinite[idx] = num_div
                        else:
                            line_tags_transfinite.append(line_tag)
                            num_div_transfinite.append(num_div)
        for line_tag, num_div in zip(line_tags_transfinite, num_div_transfinite):
            gmsh.model.mesh.setTransfiniteCurve(line_tag, num_div)

        gmsh.model.setColor([(1, i) for i in line_tags_mesh], 255, 0, 0)  # , recursive=True)  # Red

        # gmsh.model.mesh.setTransfiniteCurve(self.air_center_line_tags[0], 15)
        # gmsh.model.setColor([(1, i) for i in self.air_center_line_tags], 0, 0, 0)

        sld = gmsh.model.mesh.field.add("Distance")  # straight line distance
        gmsh.model.mesh.field.setNumbers(sld, "CurvesList", line_tags_mesh)
        # gmsh.model.mesh_generators.field.setNumbers(1, "PointsList", point_tags_mesh)
        gmsh.model.mesh.field.setNumber(sld, "Sampling", 100)
        slt = gmsh.model.mesh.field.add("Threshold")  # straight line threshold
        gmsh.model.mesh.field.setNumber(slt, "InField", sld)
        gmsh.model.mesh.field.setNumber(slt, "SizeMin", self.cctdm.mesh.ThresholdSizeMin)
        gmsh.model.mesh.field.setNumber(slt, "SizeMax", self.cctdm.mesh.ThresholdSizeMax)
        gmsh.model.mesh.field.setNumber(slt, "DistMin", self.cctdm.mesh.ThresholdDistMin)
        gmsh.model.mesh.field.setNumber(slt, "DistMax", self.cctdm.mesh.ThresholdDistMax)
        # gmsh.model.mesh_generators.field.add("Min", 7)
        # gmsh.model.mesh_generators.field.setNumbers(7, "FieldsList", [slt])
        gmsh.model.mesh.field.setAsBackgroundMesh(slt)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.OptimizeNetgen", 0)
        gmsh.model.mesh.generate(3)
        if self.verbose:
            print(f'Generating Mesh Took {timeit.default_timer() - start_time:.2f} s')
        if gui:
            self.gu.launch_interactive_GUI()

    def generate_cuts(self, gui=False):
        if self.verbose:
            print('Generating Cuts Started')
            start_time = timeit.default_timer()
        for vol, surf_in, surf_out in zip(self.cctrm.powered['cct'].vol.numbers, self.cctrm.powered['cct'].surf_in.numbers, self.cctrm.powered['cct'].surf_out.numbers):
            gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[vol], subdomainTags=[surf_in, surf_out], dims=[1, 2, 3])
        for vol in self.cctrm.induced['cct'].vol.numbers:
            gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[vol], dims=[1, 2, 3])
        gmsh.model.mesh.computeHomology()
        if self.verbose:
            print(f'Generating Cuts Took {timeit.default_timer() - start_time:.2f} s')
        if gui:
            self.gu.launch_interactive_GUI()

    def save_mesh(self, gui=False):
        if self.verbose:
            print('Saving Mesh Started')
            start_time = timeit.default_timer()
        gmsh.write(self.model_file)
        if self.verbose:
            print(f'Saving Mesh Took {timeit.default_timer() - start_time:.2f} s')
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()

    def load_mesh(self, gui=False):
        gmsh.open(self.model_file)
        if gui:
            self.gu.launch_interactive_GUI()
