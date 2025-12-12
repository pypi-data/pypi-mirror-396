import os
import math
import logging
import json
import shutil
import timeit
import pickle

import numpy as np
import gmsh
from itertools import zip_longest

import fiqus.data.DataFiQuSConductorAC_Strand as geom
from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import FilesAndFolders
from fiqus.parsers.ParserCOND import ParserCOND
from fiqus.data import RegionsModelFiQuS as Reg_Mod_FiQ
from fiqus.utils.Utils import FilesAndFolders as UFF
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import (Dict, List)

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import fiqus.geom_generators.GeometryConductorAC_Strand_RutherfordCopy as StrandGeom

logger = logging.getLogger('FiQuS')

class RoundedQuadrilateral(StrandGeom.Surface):
    def __init__(self, corner_points, corner_arc_rad):
        super().__init__()
        self.corner_points = corner_points
        self.r = corner_arc_rad
        self.boundary_curves = self.generate_boundary_curves()
    
    def generate_boundary_curves(self):
        if self.r == 0: # If the trapezoid is not rounded, return the edge lines.
            return [StrandGeom.Line.create_or_get(self.corner_points[i], self.corner_points[(i+1)%4]) for i in range(4)]
        corner_circle_arcs = []
        boundary_curves = []

        for i, p in enumerate(self.corner_points): # Create the corner circle arcs
            p_prev = self.corner_points[(i-1)%4] # Previous point in the list of corner points
            p_next = self.corner_points[(i+1)%4] # Next point in the list of corner points
            v1 = (p_prev - p) / np.linalg.norm(p_prev - p) # Unit vector from p to p_prev
            v2 = (p_next - p) / np.linalg.norm(p_next - p) # Unit vector from p to p_next
            angle = np.arccos(np.dot(v1, v2)) # Angle between v1 and v2
            circle_arc_center = p + self.r / np.sin(angle/2) * (v1 + v2) / np.linalg.norm(v1 + v2) # Center of the circle arc
            arc_p1 = p + v1*np.dot(v1, circle_arc_center - p) # First point on the circle arc
            arc_p2 = p + v2*np.dot(v2, circle_arc_center - p) # Second point on the circle arc
            # The rounded corners should be represented as circle-arcs, but must be ellipse-arcs to allow for snapping close points together.
            # Circle-arcs would need the points to be exact.
            arc = StrandGeom.EllipseArc(arc_p1, circle_arc_center, arc_p1, arc_p2) # Create the rounded corner ellipse-arc
            if np.linalg.norm(arc.P1.pos-arc.C.pos) < np.linalg.norm(arc.P2.pos-arc.C.pos):# Make sure that the major axis is greater than the minor axis
                arc.M = arc.P2
                arc.points[-1] = arc.M
                
            if i > 0:
                if corner_circle_arcs[i-1].P2 is not arc.P1:
                    # If the subsequent circle-arcs are not connected we want to connect them with a line element
                    line = StrandGeom.Line.create_or_get(corner_circle_arcs[i-1].P2, arc.P1) # Create the edge line
                    boundary_curves.append(line)

            boundary_curves.append(arc)
            corner_circle_arcs.append(arc)
            
        if corner_circle_arcs[-1].P2 is not corner_circle_arcs[0].P1:
            line = StrandGeom.Line.create_or_get(corner_circle_arcs[-1].P2, corner_circle_arcs[0].P1)
            boundary_curves.append(line)
        
        return boundary_curves

    @classmethod
    def get_max_arc_radius(cls, corner_points):
        """	
            Returns the maximum radius of the circle arc that can be used to round the corners.
        """
        # With increasing radius of the circle arc, the center of a circle arc will move along the bisector of the angle between the two lines that meet at the corner.
        # At some maximum radius, two or more circle arc centers will coincide, and at any larger radius, the circle arcs will overlap, rendering the quadrilateral invalid.
        # The maximum radius of the circle-arcs is therefore the minimum radius where two or more circle arc centers coincide.
        
        # 1) Find the bisectors of the angles between the lines that meet at the corners.
        bisectors = []
        bisector_angles = []
        for i, p in enumerate(corner_points):
            p_prev = corner_points[(i-1)%4] # Previous point in the list of corner points
            p_next = corner_points[(i+1)%4] # Next point in the list of corner points
            v1 = (p_prev - p) / np.linalg.norm(p_prev - p) # Unit vector from p to p_prev
            v2 = (p_next - p) / np.linalg.norm(p_next - p) # Unit vector from p to p_next
            angle = np.arccos(np.dot(v1, v2)) # Angle between v1 and v2
            bisector_angles.append(angle/2)
            bisector = (v1 + v2) / np.linalg.norm(v1 + v2) # unit vector from p towards the circle arc center
            bisectors.append(bisector)

        # 2) Find the radii for which the circle-arc centers will lie at the points where the bisectors intersect
        # The smallest such radius is the maximum radius of the circle arc that can be used to round the corners of the quadrilateral.
        r = []
        for i, v1 in enumerate(bisectors):
            for j, v2 in enumerate(bisectors[i+1:]):
                j = j+i+1
                p1 = corner_points[i]
                angle1 = bisector_angles[i]

                p2 = corner_points[j]
                angle2 = bisector_angles[j]

                r_max = np.linalg.norm(p2-p1) / np.linalg.norm(v1/np.sin(angle1) - v2/np.sin(angle2)) # The radius for which two circle arc centers coincide at the intersection of the bisectors
                r.append(r_max)
        return min(r) # The smallest radius at which two or more circle arc centers coincide
    
    @classmethod
    def get_area(cls, corner_points, r):
        """
            Returns the area of a rounded quadrilateral with the given corner points and corner arc radius.
        """
        corner_points = corner_points[:, :2] # Remove the z-coordinate from the corner points
        # Area of the quadrilateral without rounded corners is calculated using the shoelace formula:
        quadrilateral_area = 0.5 * np.abs(np.dot(corner_points[:, 0], np.roll(corner_points[:, 1], -1)) - np.dot(corner_points[:, 1], np.roll(corner_points[:, 0], -1)))

        # When the corners are rounded, the area of the quadrilateral is reduced by r^2 * k(angle/2) (for each corner), 
        # where r is the radius of the circle arcs and k(angle/2) is a factor that depends on the angle between the two lines that meet at the corner.
        k = lambda angle: np.pi/2 - angle - 1/np.tan(angle)
        area = quadrilateral_area
        for i, p in enumerate(corner_points):
            p_prev = corner_points[(i-1)%4] # Previous point in the list of corner points
            p_next = corner_points[(i+1)%4] # Next point in the list of corner points
            v1 = (p_prev - p) / np.linalg.norm(p_prev - p) # Unit vector from p to p_prev
            v2 = (p_next - p) / np.linalg.norm(p_next - p) # Unit vector from p to p_next
            angle = np.arccos(np.dot(v1, v2)) # Angle between v1 and v2
            area += r**2 * k(angle/2)

        return area
                
    @classmethod
    def get_arc_radius(cls, desired_area, corner_points):
        """
            Returns the radius of the circle arc that is required to create a rounded quadrilateral with the desired area.
        """
        corner_points = corner_points[:, :2]
        # Area of the quadrilateral without rounded corners is calculated using the shoelace formula:
        quadrilateral_area = 0.5 * np.abs(np.dot(corner_points[:, 0], np.roll(corner_points[:, 1], -1)) - np.dot(corner_points[:, 1], np.roll(corner_points[:, 0], -1)))

        # When the corners are rounded, the area of the quadrilateral is reduced by r^2 * k(angle/2) for each corner, 
        # where r is the radius of the circle arcs and k(angle/2) is a factor that depends on the angle between the two lines that meet at the corner.
        k = lambda angle: np.pi/2 - angle - 1/np.tan(angle)
        angles = []
        for i, p in enumerate(corner_points):
            p_prev = corner_points[(i-1)%4] # Previous point in the list of corner points
            p_next = corner_points[(i+1)%4] # Next point in the list of corner points
            v1 = (p_prev - p) / np.linalg.norm(p_prev - p) # Unit vector from p to p_prev
            v2 = (p_next - p) / np.linalg.norm(p_next - p) # Unit vector from p to p_next
            angle = np.arccos(np.dot(v1, v2)) # Angle between v1 and v2
            angles.append(angle)
        r = np.sqrt( (desired_area - (quadrilateral_area+1e-10) )/ sum([k(angle/2) for angle in angles]) ) # Radius of the circle arc that is required to create a rounded trapezoid with the desired area.
        return r

class RutherfordCable:
    def __init__(self) -> None:
        self.strands : List[StrandGeom.Surface] = []
        self.air : List[StrandGeom.Surface] = [] # TODO: This needs to be a list of all the air-surfaces (including the air between the strands). They must all be added to the physical group 'Air'.
        self.coating : StrandGeom.Surface = None

        self.excitation_coils : List[StrandGeom.Surface] = []

        self.cable_boundary_physical_group_tag = None
        self.cable_boundary_physical_group_name = None
        self.cable_boundary_curve_tags = []
        self.cable_boundary_curve_loop_tag = None

        # Coating
        # self.coating_curve_tags = []
        # self.coating_surface_tag = None
        # self.coating_curve_loop_tag = None
        # self.coating_physical_group_tag = None

    def create_geometry(self, N_strands_per_layer, cable_width, cable_height_min, cable_height_max, strand_area, min_roundness_fraction, coating_thickness, coating_corner_arc_radius, air_radius, keep_strand_area, coil_center_points, coil_widths, coil_heights):
        """
            Creates the geometry of the Rutherford cable.
        """

        strand_height_min = cable_height_min / 2
        strand_height_max = cable_height_max / 2

        if not keep_strand_area:
            avg_height = (strand_height_min + strand_height_max) / 2
            strand_width = cable_width / N_strands_per_layer
            max_arc_rad = RoundedQuadrilateral.get_max_arc_radius(np.array([[0, 0, 0], [strand_width, 0, 0], [strand_width, avg_height, 0], [0, avg_height, 0]]))
            strand_area = RoundedQuadrilateral.get_area(np.array([[0, 0, 0], [strand_width, 0, 0], [strand_width, avg_height, 0], [0, avg_height, 0]]), min_roundness_fraction * max_arc_rad)

        # The rutherford cable strands will now be created as a series of trapezoids.
        height = lambda x: strand_height_min + (strand_height_max-strand_height_min)/cable_width*x # Height of the trapezoids as a function of the x-coordinate
        w1 = cable_width/(N_strands_per_layer) # Strand width (unaltered)
        delta_w = 0

        #1) Check if the first strand can be created without altering the width. 
        # If the first strand, with minimum arc-radius, has an area below the specified area, the width of the first strand must be increased.
        s1_max_arc_rad = RoundedQuadrilateral.get_max_arc_radius(np.array([[0, 0, 0], [w1, 0, 0], [w1, height(w1), 0], [0, height(0), 0]]))
        s1_min_arc_rad = min_roundness_fraction*s1_max_arc_rad
        s1_area_squared = RoundedQuadrilateral.get_area(np.array([[0, 0, 0], [w1, 0, 0], [w1, height(w1), 0], [0, height(0), 0]]), s1_min_arc_rad)

        if s1_area_squared < strand_area - 1e-10:
            # print("The first strand cannot be created without altering the width.")
            # If the first strand cannot be created without altering the width, the width must be adjusted
            # by finding the width that gives the specified area for the first strand, given that it is fully squared.
            w1 = cable_width*(np.sqrt(strand_height_min**2 + 2*(strand_area+s1_min_arc_rad**2*(np.pi-2))*(strand_height_max-strand_height_min)/cable_width) - strand_height_min)/(strand_height_max-strand_height_min) # Width of the first strand
            delta_w = 2*(cable_width-N_strands_per_layer*w1)/(N_strands_per_layer*(N_strands_per_layer-1)) # The remaining strand widths will be incremented by delta_w to keep the total width constant.
        
        #2) Check if the area of the first strand, when fully rounded, is greater than the specified area.
        # If it is, then the geometry can not be made since the smallest strand is greater than the specified area.
        s1_rounded_arc_radius = RoundedQuadrilateral.get_max_arc_radius(np.array([[0, 0, 0], [w1, 0, 0], [w1, height(w1), 0], [0, height(0), 0]]))
        s1_area_rounded = RoundedQuadrilateral.get_area(np.array([[0, 0, 0], [w1, 0, 0], [w1, height(w1), 0], [0, height(0), 0]]), s1_rounded_arc_radius)
        if s1_area_rounded > strand_area:
            raise Exception(f"The area of the smallest possible strand is greater than the specified area by a factor of {s1_area_rounded/strand_area}.")

        x = lambda n: n*w1 + n*(n-1)/2*delta_w # Function for the x-coordinate of the leftmost point of strand n (the width of strand n is x(n+1)-x(n))

        #3) Check if the last strand, when fully squared, is smaller than the specified area. 
        # If it is, then the geometry can not be made since the largest strand is smaller than the specified area.
        sN_area_squared = RoundedQuadrilateral.get_area(np.array([[x(N_strands_per_layer-1), 0, 0], [x(N_strands_per_layer), 0, 0], [x(N_strands_per_layer), height(x(N_strands_per_layer)), 0], [x(N_strands_per_layer-1), height(x(N_strands_per_layer-1)), 0]]), 0)
        if sN_area_squared < strand_area  - 1e-10:
            raise Exception(f"The area of the last strand is less than the specified area by a factor of {sN_area_squared/strand_area}.")
        
        #4) Check if the last strand, when fully rounded, has an area greater than the specified area. 
        # If it does, then the geometry can not be made since the last strand is larger than the specified area.
        # This problem should only arise if the last strand is elongated in the y-direction. In which case the cable is 'pulled', not compressed.
        sN_rounded_arc_radius = RoundedQuadrilateral.get_max_arc_radius(np.array([[x(N_strands_per_layer-1), 0, 0], [x(N_strands_per_layer), 0, 0], [x(N_strands_per_layer), height(x(N_strands_per_layer)), 0], [x(N_strands_per_layer-1), height(x(N_strands_per_layer-1)), 0]]))
        sN_area_rounded = RoundedQuadrilateral.get_area(np.array([[x(N_strands_per_layer-1), 0, 0], [x(N_strands_per_layer), 0, 0], [x(N_strands_per_layer), height(x(N_strands_per_layer)), 0], [x(N_strands_per_layer-1), height(x(N_strands_per_layer-1)), 0]]), sN_rounded_arc_radius)
        if sN_area_rounded > strand_area:
            raise Exception(f"The minimum area of the last strand is greater than the specified area by a factor of {sN_area_rounded/strand_area}.")

        #5) Create the strands
        for layer in range(2):
            for n in range(N_strands_per_layer):
                sign = 1 if layer == 0 else -1 # Sign of the height of the strand (the second layer is inverted)
                strand_corner_points = np.array([[x(n), 0, 0], [x(n+1), 0, 0], [x(n+1), sign*height(x(n+1)), 0], [x(n), sign*height(x(n)), 0]])
                if layer == 1:
                    strand_corner_points = strand_corner_points[::-1] # Reverse the order of the corner points in the second layer 
                r = RoundedQuadrilateral.get_arc_radius(strand_area, strand_corner_points) # Radius of the circle arc that is required to create a rounded trapezoid with the desired area.
                if r <= max((x(n+1) - x(n))/1e4, StrandGeom.Point.point_snap_tolerance): 
                    r = 0 # If the radius is very small, it is likely due to numerical errors and should be set to zero.
                strand = RoundedQuadrilateral(strand_corner_points, r)
                self.strands.append(strand)

        # 6) Reverse the second half of the list of strands to make the second layer of strands inverted. This is to have the strands in the correct counter-clockwise order.
        self.strands = self.strands[:N_strands_per_layer] + self.strands[N_strands_per_layer:][::-1]

        StrandGeom.Surface.replace_overlapping_edges() # Replace overlapping edges of the strands

        # 7) Create a region representing a coating around the cable.
        # a) Create the corner points of the trapezoid
        corner_points = np.array([[-coating_thickness, strand_height_min+coating_thickness, 0], [-coating_thickness, -strand_height_min-coating_thickness, 0], [cable_width+coating_thickness, -strand_height_max-coating_thickness, 0], [cable_width+coating_thickness, strand_height_max+coating_thickness, 0]])
        # b) Create the trapezoid
        self.coating = RoundedQuadrilateral(corner_points, coating_corner_arc_radius)
        # c) Get the combined boundary curves of the cable
        cable_boundary_curves = sum([strand.boundary_curves for strand in self.strands], [])
        # Subtract all curves that are shared between multiple strands
        shared_curves = set([curve for curve in cable_boundary_curves if cable_boundary_curves.count(curve) > 1])
        cable_boundary_curves = list(set(cable_boundary_curves) - shared_curves)
                
        cable_boundary_loops = StrandGeom.Curve.get_closed_loops(cable_boundary_curves) # Get the closed loops that make up the boundaries between the air region and the strands.
        outer_cable_boundary = max(cable_boundary_loops, key=len) # The outer cable-air boundary is the longest closed loop.
        
        # d) Set the outer cable boundary as the inner boundary of the coating
        # self.coating.inner_boundary_curves.append(outer_cable_boundary) # Do not append! Mysterious error will occur...
        self.coating.inner_boundary_curves = [outer_cable_boundary]

        # 8) Create optional excitation coils with source current
        if coil_center_points:
            n_coils = len(coil_center_points)
        else:
            n_coils = 0
        for n in range(n_coils):
            excitation_coil = StrandGeom.Rectangle(coil_center_points[n], coil_widths[n], coil_heights[n])
            self.excitation_coils.append(excitation_coil)

        # 9) Create the air region
        # a) Create a disk that represents the outer air region
        outer_air_region = StrandGeom.Disk([cable_width/2,0,0], air_radius)
        # b) Set the inner boundary of the air region
        outer_air_region.inner_boundary_curves.append(self.coating.boundary_curves)
        for n in range(n_coils):
            outer_air_region.inner_boundary_curves.append(self.excitation_coils[n].boundary_curves)
        self.air.append(outer_air_region)
        # c) Create the inner air regions (the air between the strands)
        air_boundaries = cable_boundary_loops
        air_boundaries.remove(outer_cable_boundary) # Remove the outer cable boundary from the list of air boundaries.
        for air_boundary in air_boundaries:
            air_region = StrandGeom.Surface(air_boundary)
            self.air.append(air_region)

    def write_geom_to_yaml(self, file_path):
        # This function writes the geometry to a yaml file. 
        # The yaml file contains the coordinates of the points, the type of the curves and the indices of the points that make up the curves and the indices of the curves that make up the areas.
        # Note: Only the strands are written to the yaml file. The air region is not included.
        strands = self.strands
        strand_curves = [curve for strand in strands for curve in strand.boundary_curves]
        strand_points = [point for curve in strand_curves for point in curve.points]

        points = {}
        curves = {}
        areas = {}

        for p, point in enumerate(StrandGeom.Point.points_registry):
            if point in strand_points:
                points[p] = {"Coordinates": point.pos.tolist()}

        for c, curve in enumerate(StrandGeom.Curve.curves_registry):
            if curve in strand_curves:
                curves[c] = {"Type": curve.__class__.__name__, "Points": []}
                for point in curve.points:
                    point_id = StrandGeom.Point.points_registry.index(point)
                    curves[c]["Points"].append(point_id)

        for a, area in enumerate(StrandGeom.Surface.surfaces_registry):
            if area in strands:
                areas[a] = {"Boundary": []}
                for curve in area.boundary_curves:
                    curve_id = StrandGeom.Curve.curves_registry.index(curve)
                    areas[a]["Boundary"].append(curve_id)
        
        geom_dict = {"Points": points, "Curves": curves, "Areas": areas}

        UFF.write_data_to_yaml(file_path, geom_dict)

    @classmethod
    def read_geom_from_yaml(cls, file_path):
        # This function loads the geometry from a yaml file.
        # The yaml file contains the coordinates of the points, the type of the curves and the indices of the points that make up the curves 
        # and the indices of the curves that make up the strands.
        geom_data = UFF.read_data_from_yaml(file_path, StrandGeom.Geom)
        point_coords = [p.Coordinates for p in geom_data.Points.values()]
        for pos in point_coords:
            StrandGeom.Point.create_or_get(pos)

        for curve in geom_data.Curves.values():
            curve_type = curve.Type
            points = [StrandGeom.Point.points_registry[p] for p in curve.Points]
            globals()[curve_type].create_or_get(*points) # Creates a curve-entity of the specified type (which is added to the curve-registry).
        
        rutherford_cable = cls()
        for area in geom_data.Areas.values():
            boundary_curves = [StrandGeom.Curve.curves_registry[c] for c in area.Boundary]
            a = StrandGeom.Surface(boundary_curves)
            rutherford_cable.strands.append(a)
        
        return rutherford_cable
        
    def create_gmsh_instance(self):

        # When creating the gmsh instances of the strands, curve loops are created for each strand.
        # The curve loops are oriented according to the orientation of the first curve in the loop and determine the orientation of the surface. 
        # We want all the strands to have the same orientation, so we need to make sure that the curve loops are oriented in the same direction.
        # To do this, we will check the orientation of the first curve in each strand boundary. 
        # If the orientation is not counter-clockwise, we will 'roll' the curves in the boundary until the first curve is counter-clockwise.

        surfaces = self.strands + [self.coating] + self.air + self.excitation_coils
        # StrandGeom.Surface.set_correct_boundary_orientation(surfaces)

        for s in surfaces:
            # Determine orientation by:
            # 1) Find the centroid of the boundary curves.
            # 2) Look at the cross-product of the vectors from the centroid to the start and end points of the first curve.
            # 3) If the cross-product is positive, the orientation is counter-clockwise. If it is negative, the orientation is clockwise.
            # centroid = np.mean(sum([[curve.P1.pos, curve.P2.pos] for curve in s.boundary_curves], []), axis=0)
            # first_curve = s.boundary_curves[0]
            # v1 = first_curve.P1.pos - centroid
            # v2 = first_curve.P2.pos - centroid
            # orientation = np.sign(np.cross(v1, v2)[2])

            # if orientation < 0:
            #     print("here for surface ", s)
                # If the orientation is not counter-clockwise, check the next curve in the boundary.
                # for i in range(1, len(s.boundary_curves)):
                #     next_curve = s.boundary_curves[i]
                #     v1 = next_curve.P1.pos - centroid
                #     v2 = next_curve.P2.pos - centroid
                #     orientation = np.sign(np.cross(v1, v2)[2])
                #     if orientation > 0:
                #         s.boundary_curves = s.boundary_curves[i:] + s.boundary_curves[:i] # Roll the curves in the boundary until the first curve is counter-clockwise.
                #         break

            s.create_gmsh_instance()

    def add_coating(self):
        """ 
        This function adds a coating around the entire cable. The coating is added as a surface that surrounds the cable.
        We can add the coating by getting the combined outer boundary of the cable, scaling it up while keeping the center fixed, and creating a surface from the scaled boundary.
        Alternatively we can simply add a trapezoid that surrounds the cable.

        """
        gmsh.model.occ.synchronize() # Synchronize the OCC model with the GMSH model.

        # 1) Get the curves that make up the boundary of the cable.
        strands = [strand.surface_tag for strand in self.strands]
        strand_comnbined_boundary_tags = [tag for dim, tag in gmsh.model.get_boundary([(2, strand) for strand in strands], combined=True)]
        strand_combined_boundary_curves = [StrandGeom.Curve.get_curve_from_tag(tag) for tag in strand_comnbined_boundary_tags] 

        air_boundaries = StrandGeom.Curve.get_closed_loops(strand_combined_boundary_curves) # Get the closed loops that make up the boundaries between the air region and the strands.
        outer_cable_air_boundary = max(air_boundaries, key=len) # The outer cable-air boundary is the longest closed loop.

        self.cable_boundary_curve_tags = [curve.tag for curve in outer_cable_air_boundary]
        self.cable_boundary_curve_loop_tag = gmsh.model.occ.addCurveLoop(self.cable_boundary_curve_tags)
        

        # 1.1) Find the strand which each curve in the boundary belongs to and store this in a dictionary.
        curve_strand_dict = {}
        for curve in outer_cable_air_boundary:
            for strand in self.strands:
                if curve in strand.boundary_curves:
                    curve_strand_dict[curve] = strand
                    break

        # 2) Create copies of each curve in the boundary
        cable_outline_curves = gmsh.model.occ.copy([(1, curve.tag) for curve in outer_cable_air_boundary])


        # 3) Scale the curves individually by a scaling factor, around the center of mass of the strand they belong to.
        scaling_factor = 1.1

        for new_curve, curve in zip(cable_outline_curves, outer_cable_air_boundary):
            strand = curve_strand_dict[curve]
            center_of_mass = gmsh.model.occ.get_center_of_mass(2, strand.surface_tag)
            gmsh.model.occ.dilate([(1, new_curve[1])], center_of_mass[0], center_of_mass[1], center_of_mass[2], scaling_factor, scaling_factor, scaling_factor)

        # 4) Fuse the scaled curves 
        fused_curve = gmsh.model.occ.fuse([curve for curve in cable_outline_curves[:len(cable_outline_curves)//2]], [curve for curve in cable_outline_curves[len(cable_outline_curves)//2:]])[0]
        logger.info(f"Fused curve: {fused_curve}")

        gmsh.model.occ.synchronize()
        # 5) Now we remove curves which do not belong to the fused curve.
        # These curves have one point which is shared by three curves and one point which is only on one curve.
        # 5.1) Create a dictionary with the points and the curves they belong to.
        point_curves_dict = {}
        for curve in fused_curve:
            logger.info(f"Curve: {curve}, Boundary points: {gmsh.model.getBoundary([curve])}")
            for point in gmsh.model.getBoundary([curve]):
                if point not in point_curves_dict:
                    point_curves_dict[point] = []
                point_curves_dict[point].append(curve)
        logger.info(f"Point curves dict: {point_curves_dict}")
        # 5.2) Find the curves corresponding to points which lie only on one curve.
        single_point_curves = [curve for point, curves in point_curves_dict.items() if len(curves) == 1 for curve in curves]
        logger.info(f"Single point curves: {single_point_curves}")
        # 5.3) Remove the single point curves
        gmsh.model.occ.remove([curve for curve in single_point_curves])

        # 6) Create a surface from the fused curve
        # Remove the deleted curves from the list of curves
        self.coating_curve_tags = [curve[1] for curve in fused_curve if curve not in single_point_curves]
        self.coating_curve_loop_tag = gmsh.model.occ.addCurveLoop(self.coating_curve_tags)
        self.coating_surface_tag = gmsh.model.occ.add_plane_surface([self.coating_curve_loop_tag, self.cable_boundary_curve_loop_tag])
        logger.info(f"Coating surface: {self.coating_surface_tag}")

    def add_coating2(self, cable_width, cable_height_min, cable_height_max, coating_thickness):
        gmsh.model.occ.synchronize() # Synchronize the OCC model with the GMSH model.
        # Create a trapezoidal surface that surrounds the cable.
        strand_height_min = cable_height_min / 2
        strand_height_max = cable_height_max / 2
        # 1) Create the corner points of the trapezoid
        corner_points = np.array([[-coating_thickness, strand_height_min+coating_thickness, 0], [-coating_thickness, -strand_height_min-coating_thickness, 0], [cable_width+coating_thickness, -strand_height_max-coating_thickness, 0], [cable_width+coating_thickness, strand_height_max+coating_thickness, 0]])
        # 2) Create the trapezoid
        coating = RoundedQuadrilateral(corner_points, 0)
        # for c in coating.boundary_curves: # Add the boundary curves gmsh instances to the coating.
        #     c.create_gmsh_instance()

        # 3) Get the outer boundary of the cable
        strands = [strand.surface_tag for strand in self.strands]
        strand_comnbined_boundary_tags = [tag for dim, tag in gmsh.model.get_boundary([(2, strand) for strand in strands], combined=True)]
        strand_combined_boundary_curves = [StrandGeom.Curve.get_curve_from_tag(tag) for tag in strand_comnbined_boundary_tags] 

        air_boundaries = StrandGeom.Curve.get_closed_loops(strand_combined_boundary_curves) # Get the closed loops that make up the boundaries between the air region and the strands.
        outer_cable_boundary = max(air_boundaries, key=len) # The outer cable-air boundary is the longest closed loop.

        # 4) Add the boundary curves of the cable to the coating inner boundary
        # coating.inner_boundary_curves.append([curve for curve in outer_cable_boundary])
        

        # 5) Create the curve loops of the coating
        # coating.curve_loop_tag = StrandGeom.Surface.create_or_get_curve_loop(coating.boundary_curves) #gmsh.model.occ.addCurveLoop([c.tag for c in coating.boundary_curves])
        # coating.inner_curve_loop_tags.append(StrandGeom.Surface.create_or_get_curve_loop(outer_cable_boundary)) #(gmsh.model.occ.addCurveLoop([c.tag for c in outer_cable_boundary]))
        coating.create_gmsh_instance()

        # 6) Create the surface of the coating
        # coating.surface_tag = gmsh.model.occ.addPlaneSurface([coating.curve_loop_tag, coating.inner_curve_loop_tags[0]])

        self.coating = coating



    # def add_air(self, cable_width, air_radius):
    #     # Note: This must be done after the strand gmsh instances have been created.
    #     gmsh.model.occ.synchronize() # Synchronize the OCC model with the GMSH model.

    #     # Get the curves that make up the boundary of the 'fused' strands. This is the boundary separating the strands from the air.
    #     strands = [strand.surface_tag for strand in self.strands]
    #     strand_comnbined_boundary_tags = [tag for dim, tag in gmsh.model.get_boundary([(2, strand) for strand in strands], combined=True)]
    #     strand_combined_boundary_curves = [StrandGeom.Curve.get_curve_from_tag(tag) for tag in strand_comnbined_boundary_tags] 

    #     air_boundaries = StrandGeom.Curve.get_closed_loops(strand_combined_boundary_curves) # Get the closed loops that make up the boundaries between the air region and the strands.
    #     outer_cable_air_boundary = max(air_boundaries, key=len) # The outer cable-air boundary is the longest closed loop.
    #     air_boundaries.remove(outer_cable_air_boundary) # Remove the outer air boundary from the list of air boundaries.

    #     outer_air_region = StrandGeom.Disk([cable_width/2,0,0], air_radius) # Create the body of the outer air region.
    #     for c in outer_air_region.boundary_curves: # Add the boundary curves gmsh instances to the outer air region.
    #         c.create_gmsh_instance()
    #     outer_air_region.inner_boundary_curves.append([curve for curve in outer_cable_air_boundary])

    #     outer_air_region.curve_loop_tag = gmsh.model.occ.addCurveLoop([c.tag for c in outer_air_region.boundary_curves]) # Create the outer curve loop of the outer air region.
    #     outer_air_region.inner_curve_loop_tags.append(gmsh.model.occ.addCurveLoop([c.tag for c in outer_cable_air_boundary])) # Create the inner curve loop of the outer air region. This is the outline of the entire cable.
    #     outer_air_region.surface_tag = gmsh.model.occ.addPlaneSurface([outer_air_region.curve_loop_tag, outer_air_region.inner_curve_loop_tags[0]])

    #     self.air.append(outer_air_region) # Add the outer air region to the list of air regions.

    #     # Create the inner air regions:
    #     for air_boundary in air_boundaries:
    #         air_region = StrandGeom.Surface(air_boundary)
    #         air_region.create_gmsh_instance()
    #         self.air.append(air_region)

    def add_air2(self, cable_width, air_radius):
        # Note: This must be done after the strand gmsh instances have been created.
        gmsh.model.occ.synchronize() # Synchronize the OCC model with the GMSH model.

        # Get the curves that make up the boundary of the 'fused' strands. This is the boundary separating the strands from the air.
        strands = [strand.surface_tag for strand in self.strands]
        strand_comnbined_boundary_tags = [tag for dim, tag in gmsh.model.get_boundary([(2, strand) for strand in strands], combined=True)]
        strand_combined_boundary_curves = [StrandGeom.Curve.get_curve_from_tag(tag) for tag in strand_comnbined_boundary_tags] 

        air_boundaries = StrandGeom.Curve.get_closed_loops(strand_combined_boundary_curves) # Get the closed loops that make up the boundaries between the air region and the strands.
        outer_cable_air_boundary = max(air_boundaries, key=len) # The outer cable-air boundary is the longest closed loop.
        air_boundaries.remove(outer_cable_air_boundary) # Remove the outer air boundary from the list of air boundaries.

        outer_air_region = StrandGeom.Disk([cable_width/2,0,0], air_radius) # Create the body of the outer air region.
        for c in outer_air_region.boundary_curves: # Add the boundary curves gmsh instances to the outer air region.
            c.create_gmsh_instance()
        # outer_air_region.inner_boundary_curves.append([curve for curve in outer_cable_air_boundary])
        outer_air_region.inner_boundary_curves.append(self.coating.boundary_curves)

        outer_air_region.curve_loop_tag = gmsh.model.occ.addCurveLoop([c.tag for c in outer_air_region.boundary_curves]) # Create the outer curve loop of the outer air region.
        # outer_air_region.inner_curve_loop_tags.append(gmsh.model.occ.addCurveLoop([c.tag for c in outer_cable_air_boundary])) # Create the inner curve loop of the outer air region. This is the outline of the entire cable.
        outer_air_region.inner_curve_loop_tags.append(self.coating.curve_loop_tag)
        outer_air_region.surface_tag = gmsh.model.occ.addPlaneSurface([outer_air_region.curve_loop_tag, outer_air_region.inner_curve_loop_tags[0]])

        self.air.append(outer_air_region) # Add the outer air region to the list of air regions.

        # Create the inner air regions:
        for air_boundary in air_boundaries:
            air_region = StrandGeom.Surface(air_boundary)
            air_region.create_gmsh_instance()
            self.air.append(air_region)


    # def add_air(self, cable_width, air_radius):
    #     # Note: This must be done after the strand gmsh instances have been created.
    #     gmsh.model.occ.synchronize() # Synchronize the OCC model with the GMSH model.

    #     # # Get the curves that make up the boundary of the 'fused' strands. This is the boundary separating the strands from the air.
    #     strands = [strand.surface_tag for strand in self.strands]
    #     strand_comnbined_boundary_tags = [tag for dim, tag in gmsh.model.get_boundary([(2, strand) for strand in strands], combined=True)]
    #     strand_combined_boundary_curves = [StrandGeom.Curve.get_curve_from_tag(tag) for tag in strand_comnbined_boundary_tags] 

    #     air_boundaries = StrandGeom.Curve.get_closed_loops(strand_combined_boundary_curves) # Get the closed loops that make up the boundaries between the air region and the strands.
    #     outer_cable_air_boundary = max(air_boundaries, key=len) # The outer cable-air boundary is the longest closed loop.
    #     air_boundaries.remove(outer_cable_air_boundary) # Remove the outer air boundary from the list of air boundaries.

    #     outer_air_region = StrandGeom.Disk([cable_width/2,0,0], air_radius) # Create the body of the outer air region.
    #     for c in outer_air_region.boundary_curves: # Add the boundary curves gmsh instances to the outer air region.
    #         c.create_gmsh_instance()
    #     # outer_air_region.inner_boundary_curves.append([curve for curve in outer_cable_air_boundary])

    #     outer_air_region.curve_loop_tag = gmsh.model.occ.addCurveLoop([c.tag for c in outer_air_region.boundary_curves]) # Create the outer curve loop of the outer air region.
    #     outer_air_region.inner_curve_loop_tags.append(self.coating_curve_loop_tag) # Create the inner curve loop of the outer air region. This is the outline of the entire cable.
    #     outer_air_region.surface_tag = gmsh.model.occ.addPlaneSurface([outer_air_region.curve_loop_tag, outer_air_region.inner_curve_loop_tags[0]])

    #     self.air.append(outer_air_region) # Add the outer air region to the list of air regions.

    #     # Create the inner air regions:
    #     for air_boundary in air_boundaries:
    #         air_region = StrandGeom.Surface(air_boundary)
    #         air_region.create_gmsh_instance()
    #         self.air.append(air_region)

    def update_tags(self):
        # for strand in self.strands:
        #     strand.update_tags()

        # for air in self.air:
        #     air.update_tags()
        surfaces = self.strands + self.air + [self.coating] + self.excitation_coils
        StrandGeom.Surface.update_tags(surfaces)

    def add_physical_groups(self):
        # Add physical groups for the strands and the air regions.
        # The strands each have a physical boundary and a physical surface.
        for i, strand in enumerate(self.strands):
            strand.add_physical_boundary(name=f"Boundary: Strand {i}")
            strand.add_physical_surface(name=f"Surface: Strand {i}")

            strand.physical_edge_point_tag = gmsh.model.addPhysicalGroup(0, [strand.boundary_curves[0].P1.tag])

        # The air region is composed of multiple surfaces: The outer air region and the inner air regions between strands.
        # The air has an outer physical boundary and all the air regions share a physical surface.
        self.air[0].add_physical_boundary(f"Outer boundary: Air")
        self.air[0].physical_surface_tag = gmsh.model.add_physical_group(2, [air.surface_tag for air in self.air], name = "Surface: Air")
        self.air[0].physical_surface_name = "Surface: Air"
        for i, air in enumerate(self.air[1:]):
            # air.add_physical_boundary(f"Boundary: Inner air-region {i}")
            air.physical_surface_tag = self.air[0].physical_surface_tag
            air.physical_surface_name = "Surface: Air"
            air.add_physical_boundary(f"Boundary: Inner air-region {i}")
        
        # Add a physical boundary for the entire cable boundary
        # self.cable_boundary_physical_group_tag = gmsh.model.addPhysicalGroup(1, , name = "Boundary: Cable")
        # self.cable_boundary_physical_group_name = "Boundary: Cable"

        # if self.coating:
        # Add a physical surface and boundary for the coating
        self.coating.add_physical_surface("Surface: Cable coating")
        self.coating.add_physical_boundary("Boundary: Cable coating")
        self.coating.physical_edge_point_tag = gmsh.model.addPhysicalGroup(0, [self.coating.boundary_curves[0].P1.tag])

        # self.cable_boundary_physical_group_tag = gmsh.model.addPhysicalGroup(1, self.coating_curve_tags, name = "Boundary: Cable coating")
        # self.cable_boundary_physical_group_name = "Boundary: Cable coating"

        # # Add a physical surface for the coating
        # self.coating_physical_group_tag = gmsh.model.addPhysicalGroup(2, [self.coating_surface_tag], name = "Surface: Cable coating")

        # Add physical groups for the excitation coil regions
        for i, coil in enumerate(self.excitation_coils):
            coil.add_physical_boundary(name=f"Boundary: Excitation coil {i}")
            coil.add_physical_surface(name=f"Surface: Excitation coil {i}")


    def save(self, save_file):
        with open(save_file, "wb") as geom_save_file:
            pickle.dump(self, geom_save_file)
            logger.info(f"Geometry saved to file {save_file}")

class Geometry(StrandGeom.Geometry):
    def generate_cable_geometry(self, gui=False):
        """
        Generates the geometry of a Rutherford cable.
        """
        # gmsh.option.setNumber("Geometry.Tolerance", 1e-12)
        conductor_name = self.cacdm.solve.conductor_name
        cable_width = self.fdm.conductors[conductor_name].cable.bare_cable_width
        cable_height_min = self.fdm.conductors[conductor_name].cable.bare_cable_height_low
        cable_height_max = self.fdm.conductors[conductor_name].cable.bare_cable_height_high
        cable_strands_per_layer = self.fdm.conductors[conductor_name].cable.n_strands_per_layers
        strand_diameter = self.fdm.conductors[conductor_name].strand.diameter
        strand_area = (strand_diameter/2)**2 * np.pi
        air_radius = self.cacdm.geometry.air_radius
        coating_thickness = self.cacdm.geometry.coating_thickness
        coating_corner_arc_radius = self.cacdm.geometry.coating_corner_arc_radius
        keep_strand_area = self.cacdm.geometry.keep_strand_area
        coil_center_points = self.cacdm.geometry.excitation_coils.centers
        coil_widths = self.cacdm.geometry.excitation_coils.widths
        coil_heights = self.cacdm.geometry.excitation_coils.heights
        StrandGeom.Point.point_snap_tolerance = strand_diameter*self.cacdm.geometry.point_snap_tolerance_relative_to_strand_diameter
        min_roundness_factor = self.cacdm.geometry.min_roundness_factor

        
        if self.cacdm.geometry.io_settings.load.load_from_yaml:
            filename = self.cacdm.geometry.io_settings.load.filename
            RC = RutherfordCable.read_geom_from_yaml(os.path.join(self.inputs_folder, filename))
        else:
            RC = RutherfordCable()
            RC.create_geometry(cable_strands_per_layer, cable_width, cable_height_min, cable_height_max, strand_area+1e-10, min_roundness_factor, coating_thickness, coating_corner_arc_radius, air_radius, keep_strand_area, coil_center_points, coil_widths, coil_heights)

        
        RC.create_gmsh_instance()

        # Cut the coating to remove overlap with the strands
        # gmsh.model.occ.cut([(2, RC.coating.surface_tag)], [(2, strand.surface_tag) for strand in RC.strands]+[(2, air.surface_tag) for air in RC.air[1:]], removeTool=False) 

        # RC.add_coating2(cable_width, cable_height_min, cable_height_max, 1e-5)

        # RC.add_coating()

        # RC.add_air(cable_width, air_radius)
        # RC.add_air2(cable_width, air_radius)

        # for strand in RC.strands + RC.air:
        #     strand.update_tags()
        

        if self.cacdm.geometry.io_settings.save.save_to_yaml:
            filename = self.cacdm.geometry.io_settings.save.filename
            RC.write_geom_to_yaml(os.path.join(self.geom_folder, filename))


        gmsh.model.occ.synchronize()
        

        RC.add_physical_groups()
        # RC.add_physical_groups2()
        gmsh.write(self.geom_file)
        RC.save(os.path.join(self.geom_folder, f'{self.magnet_name}.pkl'))
        
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            if gmsh.isInitialized():
                gmsh.clear()
                gmsh.finalize()