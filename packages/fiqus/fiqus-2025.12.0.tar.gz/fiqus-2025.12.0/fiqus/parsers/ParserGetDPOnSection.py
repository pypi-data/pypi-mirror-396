import numpy as np

import re
import math
from typing import Literal


class ParserGetDPOnSection:
    """
    This class parses GetDP's TimeTable format output files.
    """

    def __init__(self, filePath, data_type: Literal["scalar", "vector"], depth):
        self.time_values = []
        self.data_type = data_type
        self.depth = depth

        if self.depth not in [0, 1]:
            raise NotImplementedError("Only depth = 0 and depth = 1 is implemented.")

        # Check GMSH documentation for object types:
        if self.depth == 0:
            if self.data_type == "scalar":
                lineName = "SP"  # scalar point
            elif self.data_type == "vector":
                lineName = "VP"  # vector point
        elif self.depth == 1:
            if self.data_type == "scalar":
                lineName = "ST"
            elif self.data_type == "vector":
                lineName = "VT"

        # Parse data:
        with open(filePath) as file:
            data = file.read()

        time_values_line = re.search(r"TIME\{(.*)\}", data)[0]
        time_values = re.findall(r"TIME\{(.*)\}", time_values_line)
        self.time_values = [
            float(time_value) for time_value in time_values[0].split(",")
        ]
        data = data.replace(time_values_line, "")

        points = re.findall(lineName + r"\((.*)\){.*\..*}", data)
        points = [point.split(",") for point in points]
        self.points = np.array(points, dtype=float)

        if self.depth == 1:
            length = np.shape(self.points)[1]
            step = int(length / 3)
            self.points = (
                self.points[:, 0:step]
                + self.points[:, step : 2 * step]
                + self.points[:, 2 * step : 3 * step]
            ) / 3

        values = re.findall(lineName + r"\(.*\){(.*\..*)}", data)
        values = [value.split(",") for value in values]
        self.values = np.array(values, dtype=float)

        if self.depth == 1:
            length = np.shape(self.values)[1]
            step = int(length / 3)
            self.values = (
                self.values[:, 0:step]
                + self.values[:, step : 2 * step]
                + self.values[:, 2 * step : 3 * step]
            ) / 3

        # Somehow, even with depth 0, we get duplicate magnitudes for different points.
        # We need to remove them for better plotting:
        _, unique_indices = np.unique(
            self.values[:, np.shape(self.values)[1] // 2], return_index=True
        )
        self.values = self.values[unique_indices, :]
        self.points = self.points[unique_indices, :]

    def get_values_at_time(self, time):
        """
        Returns the values at the specified time.
        """
        if self.points.shape[1] != 2:
            raise ValueError(
                "Use project_values_on_a_plane() before calling get_values_at_time()!"
            )

        for index, time_value in enumerate(self.time_values):
            if math.isclose(float(time_value), float(time), abs_tol=1e-10):
                return self.values[:, index]

    def get_values_at_time_step(self, time_step):
        """
        Returns the values at the specified time step.
        """
        if self.points.shape[1] != 2:
            raise ValueError(
                "Use project_values_on_a_plane() before calling get_values_at_time()!"
            )

        if self.data_type == "scalar":
            return self.values[:, time_step]
        elif self.data_type == "vector":
            return self.values[:, time_step * 2 : time_step * 2 + 2]

    def project_values_on_a_plane(self, plane_normal, plane_x_axis_unit_vector):
        """ """

        class unitVector:
            def __init__(self, u, v, w) -> None:
                length = math.sqrt(u**2 + v**2 + w**2)
                self.u = u / length
                self.v = v / length
                self.w = w / length

            def rotate(self, theta, withRespectTo):
                # Rotate with respect to the withRespectTo vector by theta degrees:
                # https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle
                a = withRespectTo.u
                b = withRespectTo.v
                c = withRespectTo.w

                rotationMatrix = np.array(
                    [
                        [
                            math.cos(theta) + a**2 * (1 - math.cos(theta)),
                            a * b * (1 - math.cos(theta)) - c * math.sin(theta),
                            a * c * (1 - math.cos(theta)) + b * math.sin(theta),
                        ],
                        [
                            b * a * (1 - math.cos(theta)) + c * math.sin(theta),
                            math.cos(theta) + b**2 * (1 - math.cos(theta)),
                            b * c * (1 - math.cos(theta)) - a * math.sin(theta),
                        ],
                        [
                            c * a * (1 - math.cos(theta)) - b * math.sin(theta),
                            c * b * (1 - math.cos(theta)) + a * math.sin(theta),
                            math.cos(theta) + c**2 * (1 - math.cos(theta)),
                        ],
                    ]
                )
                vector = np.array([[self.u], [self.v], [self.w]])
                rotatedVector = rotationMatrix @ vector
                return unitVector(
                    rotatedVector[0][0],
                    rotatedVector[1][0],
                    rotatedVector[2][0],
                )

            def __pow__(self, otherUnitVector):
                # Cross product:
                u = self.v * otherUnitVector.w - self.w * otherUnitVector.v
                v = self.w * otherUnitVector.u - self.u * otherUnitVector.w
                w = self.u * otherUnitVector.v - self.v * otherUnitVector.u
                return unitVector(u, v, w)

            def __mul__(self, otherUnitVector) -> float:
                # Dot product:
                return (
                    self.u * otherUnitVector.u
                    + self.v * otherUnitVector.v
                    + self.w * otherUnitVector.w
                )

        if len(plane_normal) != 3:
            raise ValueError(
                "planeNormal for magneticFieldOnCutPlane must be a list of"
                " three numbers!"
            )

        if len(plane_x_axis_unit_vector) != 3:
            raise ValueError(
                "planeXAxis for magneticFieldOnCutPlane must be a list of"
                " three numbers!"
            )

        plane_normal = unitVector(plane_normal[0], plane_normal[1], plane_normal[2])
        plane_x_axis = unitVector(
            plane_x_axis_unit_vector[0],
            plane_x_axis_unit_vector[1],
            plane_x_axis_unit_vector[2],
        )

        # Rotate perperndicular vector with respect to the plane's normal vector
        # by 90 degrees to find the second perpendicular vector:
        plane_y_axis = plane_x_axis.rotate(math.pi / 2, plane_normal)

        # Build the transformation matrix to change from the global coordinate
        # system to the plane's coordinate system:
        transformationMatrix = np.array(
            [
                [plane_x_axis.u, plane_x_axis.v, plane_x_axis.w],
                [plane_y_axis.u, plane_y_axis.v, plane_y_axis.w],
                [plane_normal.u, plane_normal.v, plane_normal.w],
            ]
        )
        points = self.points.transpose()
        new_points = transformationMatrix @ points
        new_points = new_points.transpose()
        self.points = new_points[:, 0:2]

        if self.data_type == "vector":
            reshaped_values = self.values
            reshaped_values = reshaped_values.reshape(
                (len(self.values) * len(self.time_values), 3)
            )
            reshaped_values = reshaped_values.transpose()
            new_values = transformationMatrix @ reshaped_values
            new_values = new_values.transpose()
            new_values = new_values[:, 0:2]
            self.values = new_values.reshape(
                np.shape(self.values)[0], int(np.shape(self.values)[1] / 3 * 2)
            )
