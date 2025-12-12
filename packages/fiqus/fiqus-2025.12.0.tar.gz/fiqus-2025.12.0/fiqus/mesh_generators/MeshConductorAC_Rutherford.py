import timeit
import json
import logging
import math
from enum import Enum
import operator
import itertools
import os
import pickle

import gmsh
import numpy as np

from fiqus.data import RegionsModelFiQuS
from fiqus.utils.Utils import GmshUtils, FilesAndFolders
from fiqus.data.RegionsModelFiQuS import RegionsModel

from fiqus.geom_generators.GeometryConductorAC_Rutherford import RutherfordCable
from fiqus.mesh_generators.MeshConductorAC_Strand_RutherfordCopy import Mesh
from abc import ABC, abstractmethod

occ = gmsh.model.occ
    
class CableMesh(Mesh):
    def __init__(self, fdm, verbose=True):
        super().__init__(fdm, verbose)
        self.geometry_class : RutherfordCable = None # Class from geometry generation step, used to store all information about tags corresponding to everything... To be changed later (probably)
    
    def load_geometry(self, geom_folder):
        """ Generating the geometry file also saves the geometry class as a .pkl file. This geometry class can be loaded to reference the different parts of the geometry for meshing."""
        geom_save_file = os.path.join(geom_folder, f'{self.magnet_name}.pkl')

        with open(geom_save_file, "rb") as geom_save_file: # Unnecessary to return geom instead of setting self.geometry_class
            geom = pickle.load(geom_save_file)
        return geom
    
    def generate_mesh(self, geom_folder):
        self.geometry_class : RutherfordCable = self.load_geometry(geom_folder)
        self.geometry_class.update_tags()
        self.geometry_class.add_physical_groups()

        # Mesh size field for strands:
        strand_field = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumbers(strand_field, "SurfacesList", [strand.surface_tag for strand in self.geometry_class.strands])
        gmsh.model.mesh.field.setNumber(strand_field, "VIn", self.cacdm.mesh.strand_mesh_size_ratio * self.fdm.conductors[self.cacdm.solve.conductor_name].strand.diameter)

        # Mesh size field for coating:
        coating_field = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumbers(coating_field, "SurfacesList", [self.geometry_class.coating.surface_tag])
        gmsh.model.mesh.field.setNumber(coating_field, "VIn", self.cacdm.mesh.coating_mesh_size_ratio * self.fdm.conductors[self.cacdm.solve.conductor_name].strand.diameter)

        # Mesh size field for air:
        air_field = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumbers(air_field, "SurfacesList", [self.geometry_class.air[0].surface_tag])
        gmsh.model.mesh.field.setNumber(air_field, "VIn", self.cacdm.mesh.air_boundary_mesh_size_ratio * self.fdm.conductors[self.cacdm.solve.conductor_name].strand.diameter)

        # Mesh size field for excitation coils:
        coil_field = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumbers(coil_field, "SurfacesList", [coil.surface_tag for coil in self.geometry_class.excitation_coils])
        gmsh.model.mesh.field.setNumber(coil_field, "VIn", 2*self.cacdm.mesh.coating_mesh_size_ratio * self.fdm.conductors[self.cacdm.solve.conductor_name].strand.diameter)

        total_meshSize_field = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(total_meshSize_field, "FieldsList", [strand_field, coating_field, air_field, coil_field])
        
        gmsh.model.mesh.field.setAsBackgroundMesh(total_meshSize_field)

        gmsh.option.setNumber("Mesh.MeshSizeFactor", self.cacdm.mesh.scaling_global)
        gmsh.model.mesh.generate(2)

    def generate_cuts(self):
        """
            Computes the cuts for imposing global quantities (massive or stranded).
        """
        # We need:
        # 1) one cut for the coating,
        # 2) one cut per strand, which should be directly at the interface between the strand and the coating matrix,
        # 3) one cut per excitation coil region.

        # 1) Compute cut for the coating region and oriente it based on the surface orientation
        cable_outer_boundary = self.geometry_class.coating.physical_boundary_tag
        gmsh.model.mesh.addHomologyRequest("Homology", domainTags=[cable_outer_boundary],dims=[1])
        air = self.geometry_class.air[0].physical_surface_tag
        coils = [coil.physical_surface_tag for coil in self.geometry_class.excitation_coils]
        gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[air]+coils,dims=[1])
        cuts = gmsh.model.mesh.computeHomology()
        gmsh.model.mesh.clearHomologyRequests()
        gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains2", str(cuts[0][1]))
        gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains", str(cuts[1][1]))
        gmsh.plugin.run("HomologyPostProcessing")
        self.geometry_class.coating.cut_tag = cuts[1][1] + 1

        # 2) Compute cuts and get the oriented surface of each strand
        # Cuts are computed one by one for each strand.
        # iMPORTANT: the relative cohomology is computed.
        # We consider the boundaries of each strand, relative to all the other strand boundaries and inner air regions
        # so that we ensure to keep the support of the co-chains in interfaces between strands and coating matrix,
        # rather than between strands or adjacent with inner air regions.
        # NB: cuts could also be defined one by one, possibly going through other strands and inner air regions. (But it does not seem to work correctly now.)
        for strand in self.geometry_class.strands:
            gmsh.model.mesh.addHomologyRequest("Homology", domainTags=[strand.physical_surface_tag], subdomainTags=[strand.physical_boundary_tag], dims=[2])
            gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[strand.physical_boundary_tag], subdomainTags=[other_strand.physical_boundary_tag for other_strand in self.geometry_class.strands if other_strand != strand]+[air], dims=[1])
        cuts = gmsh.model.mesh.computeHomology()
        gmsh.model.mesh.clearHomologyRequests()

        homology = cuts[1::2] # The homology results represent the surfaces of the strands
        cuts = cuts[::2] # The (randomly oriented) cuts on the boundary of the strands

        # Extract the tags from the homology and cuts
        homology = [h[1] for h in homology]
        cuts = [c[1] for c in cuts]

        # Format the homology and cuts for the plugin
        homology_formatted = ', '.join(map(str, homology)) 
        cuts_formatted = ', '.join(map(str, cuts))

        # Create an identity matrix for the transformation matrix
        N = len(self.geometry_class.strands)
        identity = '; '.join(', '.join('1' if i == j else '0' for j in range(N)) for i in range(N))

        # Next we get the boundaries of the oriented surfaces, which will also be oriented correctly
        # The result of this operation is the oriented boundaries of the strands
        gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains", homology_formatted)
        gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains2", "")
        gmsh.plugin.setString("HomologyPostProcessing", "TransformationMatrix", identity)
        gmsh.plugin.setNumber("HomologyPostProcessing", "ApplyBoundaryOperatorToResults", 1)
        gmsh.plugin.run("HomologyPostProcessing")
        
        homology_oriented = [homology[-1] + i + 1 for i in range(N)]
        homology_oriented_formatted = ', '.join(map(str, homology_oriented))

        # Finally we get the cuts for each strand as some linear combination of the cuts, which allows inducing currents in each strand separately
        gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains", homology_oriented_formatted)
        gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains2", cuts_formatted)
        gmsh.plugin.setNumber("HomologyPostProcessing", "ApplyBoundaryOperatorToResults", 0)
        gmsh.plugin.run("HomologyPostProcessing")

        for i, strand in enumerate(self.geometry_class.strands):
            # print(f"Strand {strand.physical_surface_name} cut tag: {homology_oriented[-1] + i + 1}")
            strand.cut_tag = int(homology_oriented[-1]) + i + 1

        # 3) Compute cuts for excitation coils (will be modelled as stranded conductors)
        strands = [strand.physical_surface_tag for strand in self.geometry_class.strands]
        coating = self.geometry_class.coating.physical_surface_tag
        for coil in self.geometry_class.excitation_coils:            
            coil_outer_boundary = coil.physical_boundary_tag
            gmsh.model.mesh.addHomologyRequest("Homology", domainTags=[coil_outer_boundary],dims=[1])
            other_coils = [other_coil.physical_surface_tag for other_coil in self.geometry_class.excitation_coils if other_coil != coil]
            gmsh.model.mesh.addHomologyRequest("Cohomology", domainTags=[air]+other_coils+strands+[coating],dims=[1])
            cuts = gmsh.model.mesh.computeHomology()
            gmsh.model.mesh.clearHomologyRequests()
            gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains2", str(cuts[0][1]))
            gmsh.plugin.setString("HomologyPostProcessing", "PhysicalGroupsOfOperatedChains", str(cuts[1][1]))
            gmsh.plugin.run("HomologyPostProcessing")
            coil.cut_tag = cuts[1][1] + 1

    def generate_regions_file(self):
        """
            Generates the .regions file for the GetDP solver.
        """
        regions_model = RegionsModel()
        
        """ -- Initialize data -- """
        regions_model.powered["Strands"] = RegionsModelFiQuS.Powered()
        regions_model.powered["Strands"].vol.numbers = []
        regions_model.powered["Strands"].vol.names = []
        regions_model.powered["Strands"].surf.numbers = []
        regions_model.powered["Strands"].surf.names = []
        regions_model.powered["Strands"].cochain.numbers = []
        regions_model.powered["Strands"].cochain.names = []
        regions_model.powered["Strands"].curve.names = [] # Stores physical points at filament boundary (to fix phi=0)
        regions_model.powered["Strands"].curve.numbers = [] # Stores physical points at filament boundary (to fix phi=0)

        regions_model.powered["Coating"] = RegionsModelFiQuS.Powered()
        regions_model.powered["Coating"].vol.numbers = [self.geometry_class.coating.physical_surface_tag]
        regions_model.powered["Coating"].vol.names = [self.geometry_class.coating.physical_surface_name]
        regions_model.powered["Coating"].surf_out.numbers = [self.geometry_class.coating.physical_boundary_tag]
        regions_model.powered["Coating"].surf_out.names = [self.geometry_class.coating.physical_boundary_name]
        ## regions_model.powered["Coating"].surf_in.numbers = [ ]
        ## regions_model.powered["Coating"].surf_in.names = []
        regions_model.powered["Coating"].cochain.numbers = [self.geometry_class.coating.cut_tag]
        regions_model.powered["Coating"].cochain.names = [f"Cut: Coating"]
        regions_model.powered["Coating"].curve.names = ["EdgePoint: Coating"] # Stores physical points at filament boundary (to fix phi=0)
        regions_model.powered["Coating"].curve.numbers = [self.geometry_class.coating.physical_edge_point_tag] # Stores physical points at filament boundary (to fix phi=0)

        regions_model.air.point.names = []
        regions_model.air.point.numbers = []

        regions_model.powered["ExcitationCoils"] = RegionsModelFiQuS.Powered()
        regions_model.powered["ExcitationCoils"].vol.numbers = []
        regions_model.powered["ExcitationCoils"].vol.names = []
        regions_model.powered["ExcitationCoils"].surf.numbers = []
        regions_model.powered["ExcitationCoils"].surf.names = []
        regions_model.powered["ExcitationCoils"].cochain.numbers = []
        regions_model.powered["ExcitationCoils"].cochain.names = []

        for i, strand in enumerate(self.geometry_class.strands):
            regions_model.powered["Strands"].vol.numbers.append(strand.physical_surface_tag) # Surfaces in powered.vol
            regions_model.powered["Strands"].vol.names.append(strand.physical_surface_name)

            regions_model.powered["Strands"].surf.numbers.append(strand.physical_boundary_tag) # Boundaries in powered.surf
            regions_model.powered["Strands"].surf.names.append(strand.physical_boundary_name)

            regions_model.powered["Strands"].cochain.numbers.append(strand.cut_tag)
            regions_model.powered["Strands"].cochain.names.append(f"Cut: Strand {i}")

            # Add physical point at Strand boundary to fix phi=0
            regions_model.powered["Strands"].curve.names.append(f"EdgePoint: Strand {i}")
            regions_model.powered["Strands"].curve.numbers.append(strand.physical_edge_point_tag)

        
        regions_model.air.vol.number = self.geometry_class.air[0].physical_surface_tag
        regions_model.air.vol.name = self.geometry_class.air[0].physical_surface_name

        regions_model.air.surf.number = self.geometry_class.air[0].physical_boundary_tag
        regions_model.air.surf.name = self.geometry_class.air[0].physical_boundary_name

        for air_region in self.geometry_class.air[1:]:
            regions_model.air.point.names.append(air_region.physical_boundary_name)
            regions_model.air.point.numbers.append(air_region.physical_boundary_tag)
        
        for i, coil in enumerate(self.geometry_class.excitation_coils):
            regions_model.powered["ExcitationCoils"].vol.numbers.append(coil.physical_surface_tag) # Surfaces in powered.vol
            regions_model.powered["ExcitationCoils"].vol.names.append(coil.physical_surface_name)

            regions_model.powered["ExcitationCoils"].surf.numbers.append(coil.physical_boundary_tag) # Boundaries in powered.surf
            regions_model.powered["ExcitationCoils"].surf.names.append(coil.physical_boundary_name)

            regions_model.powered["ExcitationCoils"].cochain.numbers.append(coil.cut_tag)
            regions_model.powered["ExcitationCoils"].cochain.names.append(f"Cut: Coil {i}")

        # Add physical point at matrix boundary to fix phi=0
        ## regions_model.air.point.names = ["Point at matrix boundary"]
        ## regions_model.air.point.numbers = [self.geometry_class.matrix[-1].physicalEdgePointTag]

        FilesAndFolders.write_data_to_yaml(self.regions_file, regions_model.model_dump())