import os
import logging
import timeit

import gmsh
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.interpolate import griddata
import matplotlib
import matplotlib.pyplot as plt

from fiqus.mains.MainPancake3D import Base
from fiqus.utils.Utils import GmshUtils
from fiqus.parsers.ParserGetDPTimeTable import ParserGetDPTimeTable
from fiqus.parsers.ParserGetDPOnSection import ParserGetDPOnSection

logger = logging.getLogger(__name__)


class TimeSeriesData:
    def __init__(
        self, timeValues, values, quantityName, units, title=None, fileName=None
    ):
        """ """
        self.t = timeValues
        self.values = values
        self.quantityName = quantityName
        self.units = units
        self.title = title
        self.fileName = fileName

    def plot(self, dir):
        plt.rcParams.update({"font.size": 10})
        plt.style.use("_mpl-gallery")
        fig, ax = plt.subplots(figsize=(5.95, 3))
        ax.plot(self.t, self.values, marker="o")
        ax.set_xlabel(f"Time (s)")
        ax.set_ylabel(f"{self.quantityName} ({self.units})")
        if self.title:
            ax.set_title(self.title)

        # Save the plot:
        if self.fileName is None:
            quantityName = self.quantityName.replace(" ", "_")
            filePath = os.path.join(dir, f"{quantityName}_TimeSeriesPlot.pdf")
        else:
            filePath = os.path.join(dir, f"{self.fileName}_TimeSeriesPlot.pdf")

        plt.savefig(filePath, bbox_inches="tight", pad_inches=0)
        plt.close("all")


class MagneticField:
    def __init__(
        self,
        pointsForMagnitudes,
        magnitudes,
        pointsForVectors,
        vectors,
        units,
        title=None,
        interpolationMethod="linear",
        colormap="jet",
        planeNormal=None,
    ):
        self.pointsForMagnitudes = pointsForMagnitudes
        self.magnitudes = magnitudes
        self.pointsForVectors = pointsForVectors
        self.vectors = vectors
        self.units = units
        self.title = title
        self.interpolationMethod = interpolationMethod
        self.colormap = colormap
        self.planeNormal = planeNormal

    def plot(self, dir, streamlines=True):
        start_time = timeit.default_timer()
        logger.info(f"Plotting {self.title} has been started.")
        plt.rcParams.update({"font.size": 10})
        plt.style.use("_mpl-gallery")

        points = self.pointsForMagnitudes
        magnitudes = self.magnitudes

        xArray = points[:, 0]
        yArray = points[:, 1]

        cropFactorVertical = 0.75
        cropFactorHorizontal = 0.66
        num_of_grid_points_in_y = 90

        # Put parsed values on a grid:
        aspectRatio = (xArray.max() - xArray.min()) / (yArray.max() - yArray.min())
        xLinSpace = np.linspace(
            xArray.min() * cropFactorHorizontal,
            xArray.max() * cropFactorHorizontal,
            round(num_of_grid_points_in_y * aspectRatio),
        )
        yLinSpace = np.linspace(
            yArray.min() * cropFactorVertical,
            yArray.max() * cropFactorVertical,
            num_of_grid_points_in_y,
        )
        grid_x, grid_y = np.meshgrid(xLinSpace, yLinSpace)
        grid_z = griddata(points, magnitudes, (grid_x, grid_y), method="linear")

        # Then interpolate the grid values:
        grid_points = np.array([grid_x.flatten(), grid_y.flatten()]).T
        grid_values = grid_z.flatten()
        xLinSpace = np.linspace(
            xArray.min() * cropFactorHorizontal,
            xArray.max() * cropFactorHorizontal,
            round(num_of_grid_points_in_y * aspectRatio) * 6,
        )
        yLinSpace = np.linspace(
            yArray.min() * cropFactorVertical,
            yArray.max() * cropFactorVertical,
            num_of_grid_points_in_y * 6,
        )
        grid_x, grid_y = np.meshgrid(xLinSpace, yLinSpace)
        grid_z = griddata(
            grid_points,
            grid_values,
            (grid_x, grid_y),
            method=self.interpolationMethod,
        )

        fig, ax = plt.subplots(figsize=(5.95, 4.165))

        # cs = ax.contourf(
        #     grid_x, grid_y, grid_z, cmap=matplotlib.colormaps[self.colormap], levels=np.linspace(0, 0.8, 16)
        # )
        cs = ax.imshow(
            grid_z,
            cmap=matplotlib.colormaps[self.colormap],
            extent=[
                xArray.min() * cropFactorHorizontal * 1000,
                xArray.max() * cropFactorHorizontal * 1000,
                yArray.min() * cropFactorVertical * 1000,
                yArray.max() * cropFactorVertical * 1000,
            ],
            origin="lower",
            aspect="auto",
        )
        ax.set_aspect("equal")
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("z (mm)")

        fig.colorbar(
            cs,
            ax=ax,
            label=f"Magnitude of the Magnetic Field ({self.units})",
            location="bottom",
        )

        # # Create a Rectangle patch for each coil:
        # rect1 = patches.Rectangle((5.0e-3*1000, -4.042e-3/2*1000), 120.0e-6*60*1000, 4.042e-3*1000, linewidth=2, edgecolor='k', facecolor='none')
        # rect2 = patches.Rectangle((-5.0e-3*1000, -4.042e-3/2*1000), -120.0e-6*60*1000, 4.042e-3*1000, linewidth=2, edgecolor='k', facecolor='none')
        # # Add the patch to the Axes
        # ax.add_patch(rect1)
        # ax.add_patch(rect2)

        if streamlines:
            points = self.pointsForVectors
            vectors = self.vectors
            uValues = vectors[:, 0]
            vValues = vectors[:, 1]
            grid_u = griddata(
                points, uValues, (grid_x, grid_y), method=self.interpolationMethod
            )
            grid_v = griddata(
                points, vValues, (grid_x, grid_y), method=self.interpolationMethod
            )

            ax.streamplot(
                grid_x * 1000,
                grid_y * 1000,
                grid_u,
                grid_v,
                color="white",
                linewidth=0.8,
                density=1.0,
            )

        if self.title:
            ax.set_title(self.title)

        # Save the plot:
        time = self.title.split(" ")[-2]
        plotFileName = os.path.join(
            dir, f"Magnetic_Field_On_A_Cut_Plane_at_{time}_s.pdf"
        )
        plt.savefig(plotFileName, bbox_inches="tight", pad_inches=0)
        plt.close("all")
        end_time = timeit.default_timer()
        time_span = end_time - start_time
        logger.info(f"Plotting {self.title} has been finished in {time_span:.2f} s.")


class Postprocess(Base):
    def __init__(
        self,
        fdm,
        geom_folder,
        mesh_folder,
        solution_folder,
    ) -> None:
        super().__init__(fdm, geom_folder, mesh_folder, solution_folder)

    def plotTimeSeriesPlots(self):
        start_time = timeit.default_timer()
        logger.info("Plotting time series plots has been started.")

        for timeSeriesPlot in self.pp.timeSeriesPlots:
            filePath = os.path.join(
                self.solution_folder, timeSeriesPlot.fileName + "-TimeTableFormat.csv"
            )

            if hasattr(timeSeriesPlot, 'position'):
                if hasattr(timeSeriesPlot.position, 'turnNumber'):
                    title = (
                        f"{timeSeriesPlot.quantityProperName} at turn"
                        f" {timeSeriesPlot.position.turnNumber}"
                    )
                else:
                    title = (
                        f"{timeSeriesPlot.quantityProperName} at"
                        f" ({timeSeriesPlot.position.x}, {timeSeriesPlot.position.y},"
                        f" {timeSeriesPlot.position.z})"
                    )
            else:
                title = f"{timeSeriesPlot.quantityProperName}"

            # Parse data:
            parser = ParserGetDPTimeTable(filePath)
            timeValues = parser.time_values
            scalarvalues = parser.get_equivalent_scalar_values()

            if parser.data_type == "vector":
                title = title + " (Magnitudes of 3D Vectors)"

            elif parser.data_type == "tensor":
                title = title + " (Von Misses Equivalents of Rank 2 Tensors)"

            data = TimeSeriesData(
                timeValues=timeValues,
                values=scalarvalues,
                quantityName=timeSeriesPlot.quantityProperName,
                units=timeSeriesPlot.units,
                title=title,
            )
            data.plot(dir=self.solution_folder)

        end_time = timeit.default_timer()
        time_span = end_time - start_time
        logger.info(
            f"Plotting time series plots has been finished in {time_span:.2f} s."
        )

        if self.python_postprocess_gui:
            gmsh.initialize()
            gmsh.option.setNumber("Geometry.Volumes", 0)
            gmsh.option.setNumber("Geometry.Surfaces", 0)
            gmsh.option.setNumber("Geometry.Curves", 0)
            gmsh.option.setNumber("Geometry.Points", 0)
            posFiles = [
                fileName
                for fileName in os.listdir(self.solution_folder)
                if fileName.endswith(".pos")
            ]
            for posFile in posFiles:
                gmsh.open(os.path.join(self.solution_folder, posFile))

            self.gu = GmshUtils(self.solution_folder)
            self.gu.launch_interactive_GUI()
            gmsh.finalize()

    def plotMagneticFieldOnCutPlane(self):
        start_time = timeit.default_timer()
        logger.info("Parsing magnetic field on the cut plane has been started.")

        magnitudeFilePath = os.path.join(
            self.solution_folder, "magneticFieldOnCutPlaneMagnitude-DefaultFormat.pos"
        )
        vectorFilePath = os.path.join(
            self.solution_folder, "magneticFieldOnCutPlaneVector-DefaultFormat.pos"
        )

        magnitudeParser = ParserGetDPOnSection(
            magnitudeFilePath, data_type="scalar", depth=1
        )
        magnitudeParser.project_values_on_a_plane(
            plane_normal=self.pp.magneticFieldOnCutPlane.planeNormal,
            plane_x_axis_unit_vector=self.pp.magneticFieldOnCutPlane.planeXAxisUnitVector,
        )

        if self.pp.magneticFieldOnCutPlane.streamLines:
            vectorParser = ParserGetDPOnSection(
                vectorFilePath, data_type="vector", depth=1
            )
            vectorParser.project_values_on_a_plane(
                plane_normal=self.pp.magneticFieldOnCutPlane.planeNormal,
                plane_x_axis_unit_vector=self.pp.magneticFieldOnCutPlane.planeXAxisUnitVector,
            )

        end_time = timeit.default_timer()
        time_span = end_time - start_time
        logger.info(
            "Parsing magnetic field on the cut plane has been finished in"
            f" {time_span:.2f} s."
        )
        for timeStep in range(2, len(magnitudeParser.time_values)):
            time = magnitudeParser.time_values[timeStep]
            if (
                self.pp.magneticFieldOnCutPlane.timesToBePlotted is None
                or time in self.pp.magneticFieldOnCutPlane.timesToBePlotted
            ):
                magnitudePoints = magnitudeParser.points
                magnitudes = magnitudeParser.get_values_at_time_step(timeStep)
                vectorPoints = vectorParser.points
                vectors = vectorParser.get_values_at_time_step(timeStep)

                magneticFieldOnCutPlane = MagneticField(
                    pointsForMagnitudes=magnitudePoints,
                    magnitudes=magnitudes,
                    pointsForVectors=vectorPoints,
                    vectors=vectors,
                    units="T",
                    title=(
                        "Magnetic Field On Plane"
                        f" {self.pp.magneticFieldOnCutPlane.planeNormal[0]}x + "
                        f" {self.pp.magneticFieldOnCutPlane.planeNormal[1]}y + "
                        f" {self.pp.magneticFieldOnCutPlane.planeNormal[2]}z = 0 at"
                        f" {time:.2f} s"
                    ),
                    interpolationMethod=self.pp.magneticFieldOnCutPlane.interpolationMethod,
                    colormap=self.pp.magneticFieldOnCutPlane.colormap,
                    planeNormal=self.pp.magneticFieldOnCutPlane.planeNormal,
                )
                magneticFieldOnCutPlane.plot(
                    dir=self.solution_folder,
                    streamlines=self.pp.magneticFieldOnCutPlane.streamLines,
                )
