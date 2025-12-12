import sys
import os
import getpass
import platform
import shutil
import logging
import re

import numpy as np
from pathlib import Path
from time import sleep
import multiprocessing

import pandas as pd
import ruamel.yaml
import gmsh
import json

from fiqus.data.DataSettings import DataSettings
from fiqus.data.DataFiQuS import FDM

logger = logging.getLogger(__name__)


class LoggingFormatter(logging.Formatter):
    """
    Logging formatter class
    """
    grey = "\x1b[38;20m"  # debug level
    white = "\x1b[37;20m"  # info level
    yellow = "\x1b[33;20m"  # warning level
    red = "\x1b[31;20m"  # error level
    bold_red = "\x1b[31;1m"  # critical level

    reset = "\x1b[0m"
    format = '%(asctime)s | %(levelname)s | %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: white + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class FilesAndFolders:
    @staticmethod
    def read_data_from_yaml(full_file_path, data_class):
        with open(full_file_path, 'r') as stream:
            yaml = ruamel.yaml.YAML(typ='safe', pure=True)
            yaml_str = yaml.load(stream)
            if "magnet" in yaml_str:
                yaml_str["magnet"]["input_file_path"] = str(full_file_path)

        return data_class(**yaml_str)

    @staticmethod
    def write_data_to_yaml(full_file_path, dict_of_data_class, list_exceptions=[]):
        def my_represent_none(self, data):
            """
            Change data representation from empty string to "null" string
            """
            return self.represent_scalar('tag:yaml.org,2002:null', 'null')

        def flist(x):
            """
            Define a commented sequence to allow writing a list in a single row
            """
            retval = ruamel.yaml.comments.CommentedSeq(x)
            retval.fa.set_flow_style()  # fa -> format attribute
            return retval

        def list_single_row_recursively(data_dict: dict, exceptions: list):
            """
            Write lists in a single row
            :param data_dict: Dictionary to edit
            :param exceptions: List of strings defining keys that will not be written
            in a single row
            :return:
            """
            for key, value in data_dict.items():
                if isinstance(value, list) and (key not in exceptions):
                    data_dict[key] = flist(value)
                elif isinstance(value, np.ndarray):
                    data_dict[key] = flist(value.tolist())
                elif isinstance(value, dict):
                    data_dict[key] = list_single_row_recursively(value, exceptions)

            return data_dict

        yaml = ruamel.yaml.YAML()
        yaml.default_flow_style = False
        yaml.emitter.alt_null = 'Null'
        yaml.representer.add_representer(type(None), my_represent_none)
        dict_of_data_class = list_single_row_recursively(dict_of_data_class, exceptions=list_exceptions)
        with open(full_file_path, 'w') as yaml_file:
            yaml.dump(dict_of_data_class, yaml_file)

    @staticmethod
    def write_data_model_to_yaml(full_file_path, data_model, with_comments=True, by_alias=True):
        if data_model:
            # Set up YAML instance settings:
            yamlInstance = ruamel.yaml.YAML()

            # Convert the model_data to a ruamel.yaml object/dictionary:
            if with_comments:
                path_object = Path(full_file_path)
                # Add pydantic descriptions to the yaml file as comments:
                dummy_yaml_file_to_create_ruamel_object = (
                    path_object.resolve().parent.joinpath("dummy.yaml")
                )
                with open(dummy_yaml_file_to_create_ruamel_object, "w") as stream:
                    yamlInstance.dump(data_model.dict(by_alias=by_alias), stream)

                # Read the file:
                with open(dummy_yaml_file_to_create_ruamel_object, "r") as stream:
                    # Read the yaml file and store the date inside ruamel_yaml_object:
                    # ruamel_yaml_object is a special object that stores both the data and
                    # comments. Even though the data might be changed or added, the same
                    # object will be used to create the new YAML file to store the comments.
                    ruamel_yaml_object = yamlInstance.load(
                        dummy_yaml_file_to_create_ruamel_object
                    )

                os.remove(dummy_yaml_file_to_create_ruamel_object)

                def iterate_fields(model, ruamel_yaml_object):
                    for currentPydanticKey, value in model.model_fields.items():
                        if value.alias and by_alias:
                            currentDictionaryKey = value.alias
                        else:
                            currentDictionaryKey = currentPydanticKey

                        if value.description:
                            ruamel_yaml_object.yaml_add_eol_comment(
                                value.description,
                                currentDictionaryKey,
                            )

                        if hasattr(getattr(model, currentPydanticKey), "model_fields"):
                            new_ruamel_yaml_object = iterate_fields(
                                getattr(model, currentPydanticKey),
                                ruamel_yaml_object[currentDictionaryKey],
                            )

                            ruamel_yaml_object[currentDictionaryKey] = new_ruamel_yaml_object

                        elif isinstance(getattr(model, currentPydanticKey), list):
                            for i, item in enumerate(getattr(model, currentPydanticKey)):
                                if hasattr(item, "model_fields"):
                                    new_ruamel_yaml_object = iterate_fields(
                                        item,
                                        ruamel_yaml_object[currentDictionaryKey][i],
                                    )

                                    ruamel_yaml_object[currentDictionaryKey][i] = new_ruamel_yaml_object

                    return ruamel_yaml_object

                iterate_fields(data_model, ruamel_yaml_object)
                for currentPydanticKey, value in data_model.model_fields.items():
                    if value.alias and by_alias:
                        currentDictionaryKey = value.alias
                    else:
                        currentDictionaryKey = currentPydanticKey

                    if hasattr(getattr(data_model, currentPydanticKey), "model_fields"):
                        ruamel_yaml_object[currentDictionaryKey] = iterate_fields(
                            getattr(data_model, currentPydanticKey),
                            ruamel_yaml_object[currentDictionaryKey],
                        )

                data_dict = ruamel_yaml_object

            else:
                data_dict = data_model.dict(by_alias=by_alias)

            yamlInstance.indent(sequence=4, offset=2)
            with open(full_file_path, 'w') as yaml_file:
                yamlInstance.dump(data_dict, yaml_file)

    @staticmethod
    def prep_folder(folder_full_path, clear: bool = False):
        if clear:
            if os.path.exists(folder_full_path):
                shutil.rmtree(folder_full_path)  # delete directory
        if not os.path.exists(folder_full_path):
            os.makedirs(folder_full_path)  # make new directory

    @staticmethod
    def get_folder_path(folder_type, folder, folder_key, overwrite, required_folder):
        """
        Method for ...
        :param folder_type:
        :type folder_type:
        :param folder:
        :type folder:
        :param folder_key:
        :type folder_key:
        :param overwrite:
        :type overwrite:
        :param required_folder:
        :type required_folder:
        :return:
        :rtype:
        """
        if required_folder and not (folder_key and overwrite):
            all_dirs = [x.parts[-1] for x in Path(folder).iterdir() if x.is_dir()]
            all_relevant_dirs = [x for x in all_dirs if x.startswith(f"{folder_type}_{folder_key}")]
            if f"{folder_type}_{folder_key}" in all_relevant_dirs:
                new_folder_key = f"{folder_key}_{len(all_relevant_dirs) + 1}"
                folder_key = new_folder_key

        folder_path = os.path.join(folder, folder_type + '_' + str(folder_key))
        # Disable the line below to avoid deleting the folder # TODO: add logic to control this at a higher level
        FilesAndFolders.prep_folder(folder_path, overwrite and required_folder)
        return folder_path

    @staticmethod
    def compute_folder_key(folder_type, folder, overwrite):
        # Find all the directories in the folder
        all_dirs = [x.parts[-1] for x in Path(folder).iterdir() if x.is_dir()]

        # Find all the directiories that start with the folder_type (e.g. geometry, mesh, solution)
        # Then combine them into a single string with a custom seperator (se@p)
        # Seperators are used to guarantee the directories can be split later
        all_relevant_dirs = " se@p ".join([x for x in all_dirs if x.startswith(f"{folder_type}_")])
        all_relevant_dirs = f"{all_relevant_dirs} se@p "

        # Find all the integer keys in the relevant directories
        integers_in_relevant_dirs = re.findall(rf'{folder_type}_(\d+) se@p ', all_relevant_dirs)

        if integers_in_relevant_dirs is None:
            # If there are no integers in the relevant directories, set the key to 1
            folder_key = 1
        else:
            # Make a list of integers out of the integers in the relevant directories
            integers_in_relevant_dirs = [int(x) for x in integers_in_relevant_dirs]

            # Sort the integers in the relevant directories
            integers_in_relevant_dirs.sort()

            if overwrite:
                # If overwrite is true, set the key to the largest integer in the
                # so that the folder with the largest integer key is overwritten
                if len(integers_in_relevant_dirs) == 0:
                    folder_key = 1
                else:
                    folder_key = max(integers_in_relevant_dirs)
            else:
                # If overwrite is false, then find the smallest integer key that is not
                # in the list of integers in the relevant directories
                folder_key = 1
                for i in integers_in_relevant_dirs:
                    if folder_key < i:
                        break
                    folder_key += 1

        return folder_key

    @staticmethod
    def print_welcome_graphics():
        logger.info(r" _____ _  ___        ____ ")
        logger.info(r"|  ___(_)/ _ \ _   _/ ___| ")
        logger.info(r"| |_  | | | | | | | \___ \ ")
        logger.info(r"|  _| | | |_| | |_| |___) |")
        logger.info(r"|_|   |_|\__\_\\__,_|____/ ")
        logger.info("")


class CheckForExceptions:

    @staticmethod
    def check_inputs(run):  # RunFiQuS()
        # """
        # This method raises errors when geometry, mesh or solution folders inputs are incorrect. Warnings are disabled as a trial.
        # :param run: FDM.run object
        # :type run: FDM.run
        # """
        if run.type == 'start_from_yaml':
            pass
        #     if run.geometry and not run.overwrite:
        #         warnings.warn("Warning: Geometry folder is needed only if it has to be overwritten. Ignoring it...")
        #     if run.solution or run.mesh:
        #         warnings.warn("Warning: Mesh and Solution folders are not needed. Ignoring them...")
        # elif run.type == 'geometry_only':
        #     if run.solution or run.mesh:
        #         warnings.warn("Warning: Mesh and Solution folders are not needed. Ignoring them...")
        # elif run.type == 'geometry_and_mesh':
        #     if run.geometry and not run.overwrite:
        #         warnings.warn("Warning: Geometry folder is needed only if it has to be overwritten. Ignoring it...")
        #     if run.mesh:
        #         warnings.warn("Warning: Mesh folder is not needed. Ignoring it...")
        elif run.type == 'mesh_and_solve_with_post_process':
            if not run.geometry:
                raise Exception('Full path to Geometry not provided. '
                                'Insert options -> reference_files -> geometry.')
            # if run.mesh and not run.overwrite:
            #     warnings.warn("Warning: Mesh folder is needed only if it has to be overwritten. Ignoring it...")
            # if run.solution:
            #     warnings.warn("Warning: Solution folder is not needed. Ignoring it...")
        elif run.type == 'mesh_only':
            if not run.geometry:
                raise Exception('Full path to Mesh not provided. '
                                'Insert options -> reference_files -> geometry.')
            # if run.solution:
            #     warnings.warn("Warning: Solution folder is not needed. Ignoring it...")
        elif run.type == 'solve_with_post_process':
            if not run.mesh or not run.geometry:
                raise Exception('Full path to Mesh not provided. '
                                'Insert options -> reference_files -> geometry and mesh.')
            # if run.solution and not run.overwrite:
            #     warnings.warn("Warning: Solution folder is needed only if it has to be overwritten. Ignoring it...")
        elif run.type == 'solve_only':
            if not run.mesh or not run.geometry:
                raise Exception('Full path to Mesh not provided. '
                                'Insert options -> reference_files -> geometry and mesh.')
            # if run.solution and not run.overwrite:
            #     warnings.warn("Warning: Solution folder is needed only if it has to be overwritten. Ignoring it...")
        elif run.type == 'post_process_only':
            if not run.mesh or not run.geometry or not run.solution:
                raise Exception('Full path to Solution not provided. '
                                'Insert options -> reference_files -> geometry, mesh, and solution.')

    @staticmethod
    def check_overwrite_conditions(folder_type, folder, folder_key):
        """
        This method prints warning related to overwrite conditions settings. This is disabled as a trial.
        :param folder_type:
        :type folder_type:
        :param folder:
        :type folder:
        :param folder_key:
        :type folder_key:
        """
        pass
        # if folder_key:
        #     if not os.path.exists(os.path.join(folder, folder_type + '_' + str(folder_key))):
        #         warnings.warn(
        #             f'The folder {folder_type}_{folder_key} does not exist. Creating it...')
        # else:
        #     warnings.warn(
        #         f'Reference number of the folder {folder_type} not provided. '
        #         f'Overwriting the latest {folder_type} folder...')


class GeometricFunctions:

    @staticmethod
    def sig_dig(n, precision=8):
        return float(np.format_float_positional(n, precision=precision))

    @staticmethod
    def points_distance(a, b):
        """
            Computes the distance between two points a and b
            :param a: list of x and y coordinates
            :param b: list of x and y coordinates
        """
        a = np.array(a)
        b = np.array(b)
        return np.linalg.norm(a - b)

    @staticmethod
    def line_through_two_points(point1, point2):
        """
            Finds coefficients of the line through two points [x1,y1] and [x2,y2]
            :param point1: 2-element list defining x/y positions of the 1st point
            :param point2: 2-element list defining x/y positions of the 2nd point
            :return: 3-element list defining the A, B, and C coefficients of the line, as in: A*x + B*y + C = 0
        """
        x1, y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]
        if x2 == x1:
            A = 1
            B = 0
            C = - x1
        elif y2 == y1:
            A = 0
            B = 1
            C = - y1
        else:
            A = - (y2 - y1) / (x2 - x1)
            B = + 1
            C = - (x2 * y1 - x1 * y2) / (x2 - x1)
        return [float(A), float(B), float(C)]

    @staticmethod
    def centroid(X, Y):
        """
            Computes the centroid coordinates of a non-self-intersecting closed polygon
            :param X: list of x coordinate of the vertices
            :param Y: list of y coordinate of the vertices
        """
        sum_A, sum_Cx, sum_Cy = 0, 0, 0
        for i in range(len(X)):
            index = i + 1 if i != len(X) - 1 else 0
            A = X[i] * Y[index] - X[index] * Y[i]
            sum_Cx += (X[i] + X[index]) * A
            sum_Cy += (Y[i] + Y[index]) * A
            sum_A += A
        factor = 1 / (3 * sum_A)
        return [factor * sum_Cx, factor * sum_Cy]

    @staticmethod
    def arc_center_from_3_points(a, b, c):
        """
            Computes the center coordinates of an arc passing through three points
            :param a: list of x and y coordinates of one arc point
            :param b: list of x and y coordinates of one arc point
            :param c: list of x and y coordinates of one arc point
        """
        ab = [a[0] - b[0], a[1] - b[1]]
        ac = [a[0] - c[0], a[1] - c[1]]
        sac = [a[0] * a[0] - c[0] * c[0], a[1] * a[1] - c[1] * c[1]]
        sba = [b[0] * b[0] - a[0] * a[0], b[1] * b[1] - a[1] * a[1]]
        yy = (sac[0] * ab[0] + sac[1] * ab[0] + sba[0] * ac[0] + sba[1] * ac[0]) / \
             (2 * ((c[1] - a[1]) * ab[0] - (b[1] - a[1]) * ac[0]))
        xx = (sac[0] * ab[1] + sac[1] * ab[1] + sba[0] * ac[1] + sba[1] * ac[1]) / \
             (2 * ((c[0] - a[0]) * ab[1] - (b[0] - a[0]) * ac[1]))
        return [-xx, -yy]

    @staticmethod
    def corrected_arc_center(C, pnt1, pnt2):
        """
            Computes the center coordinates of an arc from two points and a guessed center
            :param C: list of x and y coordinates of guessed center
            :param pnt1: list of x and y coordinates of first arc point
            :param pnt2: list of x and y coordinates of second arc point
        """
        if pnt1[1] < 0:
            pnt_tmp = pnt1.copy()
            pnt1 = pnt2.copy()
            pnt2 = pnt_tmp
        radius = (np.sqrt(np.square(pnt1[0] - C[0]) + np.square(pnt1[1] - C[1])) +
                  np.sqrt(np.square(pnt2[0] - C[0]) + np.square(pnt2[1] - C[1]))) / 2
        d = [0.5 * abs((pnt2[0] - pnt1[0])), 0.5 * abs((pnt1[1] - pnt2[1]))]
        aa = np.sqrt(np.square(d[0]) + np.square(d[1]))
        bb = np.sqrt(np.square(radius) - np.square(aa))
        M = [pnt1[0] + d[0]]
        if pnt2[1] < pnt1[1]:
            M.append(pnt2[1] + d[1])
            sign = [-1, -1] if pnt2[1] >= 0. else [1, 1]
        else:
            M.append(pnt1[1] + d[1])
            sign = [1, -1] if pnt2[1] >= 0. else [-1, 1]
        return [M[0] + sign[0] * bb * d[1] / aa, M[1] + sign[1] * bb * d[0] / aa]

    @staticmethod
    def arc_angle_between_point_and_abscissa(p, c):
        """
            Returns the angle of an arc with center c and endpoints at (cx + radius, cy) and (px, py)
            :param p: list of x and y coordinates of a point
            :param c: list of x and y coordinates of the arc center
        """
        theta = np.arctan2(p[1] - c[1], p[0] - c[0])
        return theta + (2 * np.pi if theta < 0 else 0)

    @staticmethod
    def intersection_between_two_lines(line1, line2):
        """
            Finds the intersection point between two lines
            :param line1: list of A, B, C (A*x + B*y + C = 0)
            :param line2: list of A, B, C (A*x + B*y + C = 0)
        """
        if line1[1] == 0.0:
            x = - line1[2] / line1[0]
            y = - (line2[0] * x + line2[2]) / line2[1]
        elif line2[1] == 0.0:
            x = - line2[2] / line2[0]
            y = - (line1[0] * x + line1[2]) / line1[1]
        else:
            a = - line1[0] / line1[1]
            c = - line1[2] / line1[1]
            b = - line2[0] / line2[1]
            d = - line2[2] / line2[1]
            x = (d - c) / (a - b)
            y = a * x + c
        return [x, y]

    @staticmethod
    def intersection_between_circle_and_line(line, circle, get_only_closest: bool = False):
        """
            Finds the intersection point/s between a circle and a line
            :param line: list of A, B, C (A*x + B*y + C = 0)
            :param circle: list of lists (x and y coordinates of the center, and point)
            :param get_only_closest: boolean to return only closest intersection point to the circle point
        """
        vertical = line[1] == 0
        c, d = circle
        r = GeometricFunctions.points_distance(c, d)
        intersect = []
        if vertical:
            m = - line[2] / line[0]
            delta = r ** 2 + 2 * m * c[0] - m ** 2 - c[0] ** 2
        else:
            m, b = - line[0] / line[1], - line[2] / line[1]
            A = m ** 2 + 1
            B = 2 * (m * b - c[0] - m * c[1])
            C = b ** 2 - r ** 2 + c[0] ** 2 + c[1] ** 2 - 2 * c[1] * b
            delta = B ** 2 - 4 * A * C

        if delta < 0:  # no intersection with the circle
            return None
        elif delta == 0:  # tangent to the circle
            x0 = m if vertical else - B / 2 / A
            y0 = c[1] if vertical else m * x0 + b
            intersect.append([x0, y0])
        else:  # two intersections with the circle
            x1 = m if vertical else (- B + np.sqrt(delta)) / 2 / A
            y1 = np.sqrt(delta) + c[1] if vertical else m * x1 + b
            x2 = m if vertical else (- B - np.sqrt(delta)) / 2 / A
            y2 = - np.sqrt(delta) + c[1] if vertical else m * x2 + b
            intersect.append([x1, y1])
            intersect.append([x2, y2])
            if get_only_closest:
                distance1 = GeometricFunctions.points_distance(d, intersect[0])
                distance2 = GeometricFunctions.points_distance(d, intersect[1])
                if distance1 > distance2:
                    intersect.pop(0)
                else:
                    intersect.pop(1)
        return intersect

    @staticmethod
    def intersection_between_arc_and_line(line, arc):
        """
            Finds the intersection point/s between an arc and a line
            :param line: list of A, B, C (A*x + B*y + C = 0)
            :param arc: list of lists (x and y coordinates of the center, high-angle endpoint, and low-angle endpoint)
        """
        vertical = line[1] == 0
        c, d, e = arc
        r = GeometricFunctions.points_distance(c, d)
        angle_d = GeometricFunctions.arc_angle_between_point_and_abscissa(d, c)
        angle_e = GeometricFunctions.arc_angle_between_point_and_abscissa(e, c)
        intersect = []
        if vertical:
            m = - line[2] / line[0]
            delta = r ** 2 + 2 * m * c[0] - m ** 2 - c[0] ** 2
        else:
            m, b = - line[0] / line[1], - line[2] / line[1]
            A = m ** 2 + 1
            B = 2 * (m * b - c[0] - m * c[1])
            C = b ** 2 - r ** 2 + c[0] ** 2 + c[1] ** 2 - 2 * c[1] * b
            delta = B ** 2 - 4 * A * C

        if delta < 0:  # no intersection with the circle
            return None
        elif delta == 0:  # tangent to the circle
            x0 = m if vertical else - B / 2 / A
            y0 = c[1] if vertical else m * x0 + b
            angle0 = GeometricFunctions.arc_angle_between_point_and_abscissa([x0, y0], c)
            intersect0 = True if angle_e < angle0 < angle_d else False
            if intersect0:
                intersect.append([x0, y0])
            else:  # no intersection with the arc
                return None
        else:  # two intersections with the circle
            x1 = m if vertical else (- B + np.sqrt(delta)) / 2 / A
            y1 = np.sqrt(delta) + c[1] if vertical else m * x1 + b
            angle1 = GeometricFunctions.arc_angle_between_point_and_abscissa([x1, y1], c)
            intersect1 = True if (angle_e < angle1 < angle_d) or abs(angle1 - angle_e) < 1e-6 or abs(angle1 - angle_d) < 1e-6 else False
            x2 = m if vertical else (- B - np.sqrt(delta)) / 2 / A
            y2 = - np.sqrt(delta) + c[1] if vertical else m * x2 + b
            angle2 = GeometricFunctions.arc_angle_between_point_and_abscissa([x2, y2], c)
            intersect2 = True if (angle_e < angle2 < angle_d) or abs(angle2 - angle_e) < 1e-6 or abs(angle2 - angle_d) < 1e-6 else False
            if not intersect1 and not intersect2:  # no intersection with the arc
                return None
            if intersect1:  # first point intersecting the arc
                intersect.append([x1, y1])
            if intersect2:  # second point intersecting the arc
                intersect.append([x2, y2])

        return intersect


class GmshUtils:

    def __init__(self, model_name='dummy_name', verbose=True):
        self.model_name = model_name
        self.verbose = verbose

    def initialize(self, verbosity_Gmsh: int = 5):
        """
        Initialize Gmsh with options for FiQuS
        :param verbosity_Gmsh: Input file run.verbosity_Gmsh
        :type verbosity_Gmsh: int
        """
        if not gmsh.is_initialized():
            gmsh.initialize(sys.argv)
            gmsh.model.add(str(self.model_name))
            num_threads = multiprocessing.cpu_count()
            gmsh.option.setNumber('General.NumThreads', num_threads)  # enable multithreading (this seems to be only for meshing)
            gmsh.option.setNumber('Mesh.MaxNumThreads1D', num_threads)
            gmsh.option.setNumber('Mesh.MaxNumThreads2D', num_threads)
            gmsh.option.setNumber('Mesh.MaxNumThreads3D', num_threads)
            gmsh.option.setNumber('Geometry.OCCParallel', 1)
            gmsh.option.setNumber('Geometry.ToleranceBoolean', 0.000001)
            gmsh.option.setString('Geometry.OCCTargetUnit', 'M')
            gmsh.option.setNumber("General.Verbosity", verbosity_Gmsh)
            if self.verbose:
                gmsh.option.setNumber('General.Terminal', 1)
            else:
                gmsh.option.setNumber('General.Terminal', 0)

    def check_for_event(self):  # pragma: no cover
        action = gmsh.onelab.getString("ONELAB/Action")
        if len(action) and action[0] == "check":
            gmsh.onelab.setString("ONELAB/Action", [""])
            if self.verbose:
                print("-------------------check----------------")
            gmsh.fltk.update()
            gmsh.graphics.draw()
        if len(action) and action[0] == "compute":
            gmsh.onelab.setString("ONELAB/Action", [""])
            if self.verbose:
                print("-------------------compute----------------")
            gmsh.onelab.setChanged("Gmsh", 0)
            gmsh.onelab.setChanged("GetDP", 0)
            gmsh.fltk.update()
            gmsh.graphics.draw()
        return True

    def launch_interactive_GUI(self, close_after=-1):  # pragma: no cover
        gmsh.fltk.initialize()
        while gmsh.fltk.isAvailable() and self.check_for_event():
            gmsh.fltk.wait()
            if close_after >= 0:
                sleep(close_after)
                gmsh.fltk.finalize()
        gmsh.finalize()


class RoxieParsers:
    def __init__(self, conductor, block, xyCorner):
        self.conductor = conductor
        self.block = block
        self.xyCorner = xyCorner

    @staticmethod
    def parseMap2d(map2dFile: Path, physical_quantity: str = 'magnetic_flux_density'):
        """
            Generates pandas data frame with map2d content
            :param map2dFile: path of map2dFile containing the content to parse
            :param physical_quantity: magnetic_flux_density or temperature
        """
        physical_quantities_abbreviations = {'magnetic_flux_density': ('BX/T', 'BY/T'), 'temperature': ('T/K', '-')}
        columns = ['BL.', 'COND.', 'NO.', 'X-POS/MM', 'Y-POS/MM'] + \
                  [abbr for abbr in physical_quantities_abbreviations[physical_quantity]] + \
                  ['AREA/MM**2', 'CURRENT', 'FILL FAC.']
        return pd.read_csv(map2dFile, sep=r"\s{2,}|(?<=2) |(?<=T) ", engine='python', usecols=columns)

    @staticmethod
    def parseCond2d(cond2dFile: Path):
        """
            Read input file and return list of ConductorPosition objects

            # input: fileName
            # output: conductorPositionsList

        """
        # conductorStartKeyword = "CONDUCTOR POSITION IN THE CROSS-SECTION"
        blockStartKeyword = "BLOCK POSITION IN THE CROSS-SECTION"

        fileContent = open(cond2dFile, "r").read()

        # separate rows
        fileContentByRow = fileContent.split("\n")

        # Find block definition
        for i in range(len(fileContentByRow)):
            if blockStartKeyword in fileContentByRow[i]:
                startOfBlockDefinitionIndex = i

        # separate part of the data with conductor position information
        conductorPositions = fileContentByRow[5:startOfBlockDefinitionIndex - 2]

        # drop every 5th row
        conductorPositionsFourVertices = list(conductorPositions)
        del conductorPositionsFourVertices[4::5]

        # arrange data in a list of lists
        outputConductorPositions = []
        for row in conductorPositionsFourVertices:
            rowSplitStr = row.split(',')
            rowSplitFloat = [float(elem) for elem in rowSplitStr]
            outputConductorPositions.append(rowSplitFloat)

        # arrange data from list to numpy.array
        outputConductorPositionsMatrix = np.array(outputConductorPositions)

        # input: outputConductorPositions
        # output: conductorPositionsList
        conductorPositionsList = []
        for i in range(0, len(outputConductorPositions), 4):
            out = outputConductorPositions[i]
            conductor = int(out[1])
            block = int(out[2])
            xyCorner = outputConductorPositionsMatrix[i:i + 4, 4:6]
            conductorPositionsList.append(RoxieParsers(conductor, block, xyCorner))

        return conductorPositionsList


def initialize_logger(work_folder: str = None, time_stamp: str = None, verbose: bool = True, ):
    """
    THis is logger function to write FiQuS log files.

    :param work_folder: Folder where the log file is written to
    :type work_folder: str
    :param time_stamp: time stamp put in the log file name
    :type time_stamp: str
    :param verbose: if true INFO level logs are printed, if false only WARNING level logs are printed to the console
    :type verbose: bool
    :return: logger object
    :rtype: object
    """

    logger = logging.getLogger()

    while logger.hasHandlers():
        handler = logger.handlers[0]
        logger.removeHandler(handler)
        handler.close()

    if verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(LoggingFormatter())
    logger.addHandler(stdout_handler)

    FilesAndFolders.prep_folder(work_folder)
    FilesAndFolders.prep_folder(os.path.join(work_folder, "logs"))
    file_handler = logging.FileHandler(os.path.join(work_folder, "logs", f"{time_stamp}.FiQuS.log"))
    file_handler.setLevel(logging.INFO)
    fileFormatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    file_handler.setFormatter(fileFormatter)
    logger.addHandler(file_handler)

    errorsAndWarnings_file_handler = logging.FileHandler(os.path.join(work_folder, "logs", f"ERRORS_WARNINGS_{time_stamp}.FiQuS.log"))
    errorsAndWarnings_file_handler.setLevel(logging.WARNING)
    errorsAndWarnings_file_handler.setFormatter(fileFormatter)
    logger.addHandler(errorsAndWarnings_file_handler)

    return logger


def create_json_schema(data_model: FDM):
    """
    Create the JSON Schema from a Pydantic data model
    :param data_model: FDM
    :type data_model: FDM
    """

    # Generate the raw JSON schema from the Pydantic model
    json_schema_dict = data_model.model_json_schema()

    # Replace anyOf with oneOf for better compatibility
    json_schema_str = json.dumps(json_schema_dict)
    json_schema_str = json_schema_str.replace("anyOf", "oneOf")

    # Pretty-print the schema with proper indentation
    pretty_json_schema = json.dumps(json.loads(json_schema_str), indent=4, ensure_ascii=False)

    # Define the output folder for the schema
    docs_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs"
    )

    # Create the _inputs folder for the JSON schema
    json_schema_file_path = os.path.join(docs_folder, "schema.json")
    os.makedirs(os.path.dirname(json_schema_file_path), exist_ok=True)

    # Write the prettified JSON schema to a file
    with open(json_schema_file_path, "w", encoding="utf-8") as file:
        file.write(pretty_json_schema)

def get_data_settings(GetDP_path=None, settings=None):
    user_name = getpass.getuser()

    if user_name == 'root':
        user_name = 'SYSTEM'
    elif user_name == 'MP-WIN-02$':
        user_name = 'MP_WIN_02'
    if not settings:
        path_to_settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tests", f"settings.{user_name}.yaml")
        try:
            settings = FilesAndFolders.read_data_from_yaml(path_to_settings_file, DataSettings)
        except:
            with open(settings.error.log, 'a') as file:
                # Append the string to the file
                file.write(f'Could not find: {path_to_settings_file}' + '\n')
            raise ValueError(f'File: {path_to_settings_file} does not exist.')

    if platform.system() == 'Windows':
        if GetDP_path:
            settings.GetDP_path = GetDP_path
    elif platform.system() == 'Linux':
        if GetDP_path:
            settings.GetDP_path = GetDP_path
        else:
            settings.GetDP_path = 'getdp'
    elif platform.system() == 'Darwin':
        if GetDP_path:
            settings.GetDP_path = GetDP_path
    else:
        raise ValueError(f'Python claims that you are running on operating system: {platform.system()} and it is not supported by FiQuS!')

    return settings
