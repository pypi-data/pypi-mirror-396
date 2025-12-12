import os
from pathlib import Path
import gmsh
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection

from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import GeometricFunctions as Func
from fiqus.utils.Utils import RoxieParsers
from fiqus.utils.Utils import FilesAndFolders as Util
from fiqus.data import DataFiQuS as dF
from fiqus.data import DataMultipole as dM
from fiqus.data import RegionsModelFiQuS as rM


class PostProcess:
    def __init__(self, data: dF.FDM() = None, solution_folder: str = None, verbose: bool = False):
        """
        Class to post process results
        :param data: FiQuS data model
        :param verbose: If True more information is printed in python console.
        """
        self.data: dF.FDM() = data
        self.solution_folder = solution_folder
        self.verbose: bool = verbose
        self.md = dM.MultipoleData()
        self.rm = rM.RegionsModel()

        self.gu = GmshUtils(self.solution_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=self.data.run.verbosity_Gmsh)

        self.brep_iron_curves = {1: set(), 2: set(), 3: set(), 4: set()}
        self.strands = None
        self.crns = None
        self.avg_temperatures = pd.DataFrame()
        self.postprocess_parameters = dict.fromkeys(['overall_error', 'minimum_diff', 'maximum_diff'])
        self.mesh_folder = os.path.dirname(self.solution_folder)
        self.geom_files = os.path.join(os.path.dirname(self.mesh_folder), self.data.general.magnet_name)
        self.mesh_files = os.path.join(self.mesh_folder, self.data.general.magnet_name)
        self.model_file = os.path.join(self.solution_folder, self.data.general.magnet_name)
        self.postproc_settings = pd.DataFrame()

        self.supported_variables = {'magnetic_flux_density': 'b',
                                    'temperature': 'T'}
        if any([var not in self.supported_variables.values()
                for var in self.data.magnet.postproc.electromagnetics.variables + self.data.magnet.postproc.thermal.variables]):
            pass
            # raise Exception(f"The interpolation of the field at the strands locations can not be executed: "
            #                 f"a variable listed in 'post_processors' -> 'variables' is not supported. "
            #                 f"Supported variables are: {self.supported_variables.values()}")
        self.physical_quantities_abbreviations = \
            {'magnetic_flux_density': ('BX/T', 'BY/T'),
             'temperature':           ('T/K', '-')}
        self.physical_quantity = None
        self.formatted_headline = "{0:>5}{1:>8}{2:>7}{3:>12}{4:>13}{5:>8}{6:>11}{7:>16}{8:>8}{9:>10}\n\n"
        self.formatted_content = "{0:>6}{1:>6}{2:>7}{3:>13}{4:>13}{5:>11}{6:>11}{7:>11}{8:>9}{9:>8}\n"
        self.map2d_headline_names = []

    def prepare_settings(self, settings):
        self.postproc_settings = pd.DataFrame({
            'variables': settings.variables,
            'volumes': settings.volumes})
        if 'compare_to_ROXIE' in settings.model_dump():
            self.physical_quantity = 'magnetic_flux_density'
        else:
            self.physical_quantity = 'temperature'
        self.map2d_headline_names = ['BL.', 'COND.', 'NO.', 'X-POS/MM', 'Y-POS/MM'] + \
                                    [abbr for abbr in self.physical_quantities_abbreviations[self.physical_quantity]] + \
                                    ['AREA/MM**2', 'CURRENT', 'FILL FAC.']

        if settings.plot_all != 'false':
            self.fiqus = None
            self.roxie = None
            fig1 = plt.figure(1)
            self.ax = fig1.add_subplot()
            self.ax.set_xlabel('x [cm]')  # adjust other plots to cm
            self.ax.set_ylabel('y [cm]')
            # self.ax.set_xlim(0, 0.09)  # todo
            # self.ax.set_ylim(0, 0.09)

            if not settings.model_dump().get('take_average_conductor_temperature', False):
                if settings.model_dump().get('compare_to_ROXIE', False):
                    fig2 = plt.figure(2)
                    self.ax2 = fig2.add_subplot(projection='3d')
                    self.ax2.set_xlabel('x [m]')
                    self.ax2.set_ylabel('y [m]')
                    self.ax2.set_zlabel('Absolute Error [T]')
                    self.fig4 = plt.figure(4)
                    self.ax4 = plt.axes()
                    self.ax4.set_xlabel('x [cm]')
                    self.ax4.set_ylabel('y [cm]')
                    self.ax4.set_aspect('equal', 'box')
                fig3 = plt.figure(3)
                self.ax3 = fig3.add_subplot(projection='3d')
                self.ax3.set_xlabel('x [m]')
                self.ax3.set_ylabel('y [m]')
                self.ax3.set_zlabel('norm(B) [T]' if 'compare_to_ROXIE' in settings.model_dump() else '')

        if 'compare_to_ROXIE' in settings.model_dump() and 'b' in settings.variables:
            b_index = settings.variables.index('b')
            file_to_open = os.path.join(self.solution_folder, f"b_{settings.volumes[b_index]}.pos")
        elif 'T' in settings.variables:
            T_index = settings.variables.index('T')
            file_to_open = os.path.join(self.solution_folder, f"T_{settings.volumes[T_index]}.pos")
            
        gmsh.open(file_to_open)

    def clear(self):
        self.md = dM.MultipoleData()
        self.rm = rM.RegionsModel()
        plt.close('all')
        gmsh.clear()

    def ending_step(self, gui: bool = False):
        if gui:
            self.gu.launch_interactive_GUI()
        else:
            gmsh.clear()
            gmsh.finalize()

    def loadAuxiliaryFile(self, run_type):
        self.md = Util.read_data_from_yaml(f"{self.mesh_files}_{run_type}.aux", dM.MultipoleData)

    def loadRegionFile(self):
        self.rm = Util.read_data_from_yaml(f"{self.mesh_files}_TH.reg", rM.RegionsModel)

    def loadStrandPositions(self, run_type):
        self.strands = json.load(open(f"{self.geom_files}_{run_type}.strs"))

    def loadHalfTurnCornerPositions(self):
        self.crns = json.load(open(f"{self.geom_files}.crns"))

    def plotHalfTurnGeometry(self, compare_to_ROXIE):
        for i in range(len(self.crns['iH'])):
            self.ax.add_line(lines.Line2D([self.crns['iH'][i][0], self.crns['iL'][i][0]],
                                          [self.crns['iH'][i][1], self.crns['iL'][i][1]], color='green'))
            self.ax.add_line(lines.Line2D([self.crns['oH'][i][0], self.crns['oL'][i][0]],
                                          [self.crns['oH'][i][1], self.crns['oL'][i][1]], color='green'))
            self.ax.add_line(lines.Line2D([self.crns['oL'][i][0], self.crns['iL'][i][0]],
                                          [self.crns['oL'][i][1], self.crns['iL'][i][1]], color='green'))
            self.ax.add_line(lines.Line2D([self.crns['iH'][i][0], self.crns['oH'][i][0]],
                                          [self.crns['iH'][i][1], self.crns['oH'][i][1]], color='green'))
            cc_fiqus = Func.centroid([self.crns['iH'][i][0], self.crns['iL'][i][0],
                                      self.crns['oL'][i][0], self.crns['oH'][i][0]],
                                     [self.crns['iH'][i][1], self.crns['iL'][i][1],
                                      self.crns['oL'][i][1], self.crns['oH'][i][1]])

            if compare_to_ROXIE:
                self.ax.add_line(lines.Line2D([self.crns['iHr'][i][0], self.crns['iLr'][i][0]],
                                              [self.crns['iHr'][i][1], self.crns['iLr'][i][1]],
                                              color='red', linestyle='dashed'))
                self.ax.add_line(lines.Line2D([self.crns['oHr'][i][0], self.crns['oLr'][i][0]],
                                              [self.crns['oHr'][i][1], self.crns['oLr'][i][1]],
                                              color='red', linestyle='dashed'))
                self.ax.add_line(lines.Line2D([self.crns['oLr'][i][0], self.crns['iLr'][i][0]],
                                              [self.crns['oLr'][i][1], self.crns['iLr'][i][1]],
                                              color='red', linestyle='dashed'))
                self.ax.add_line(lines.Line2D([self.crns['iHr'][i][0], self.crns['oHr'][i][0]],
                                              [self.crns['iHr'][i][1], self.crns['oHr'][i][1]],
                                              color='red', linestyle='dashed'))
                self.ax.text((self.crns['oLr'][i][0] + self.crns['iLr'][i][0]) / 2,
                             (self.crns['oLr'][i][1] + self.crns['iLr'][i][1]) / 2,
                             'R' + str(i + 1), style='italic', bbox={'facecolor': 'red', 'pad': 2})
                self.ax.text((self.crns['iHr'][i][0] + self.crns['oHr'][i][0]) / 2,
                             (self.crns['iHr'][i][1] + self.crns['oHr'][i][1]) / 2,
                             'L' + str(i + 1), style='italic', bbox={'facecolor': 'red', 'pad': 2})
                cc_roxie = Func.centroid(
                    [self.crns['iHr'][i][0], self.crns['iLr'][i][0], self.crns['oLr'][i][0], self.crns['oHr'][i][0]],
                    [self.crns['iHr'][i][1], self.crns['iLr'][i][1], self.crns['oLr'][i][1], self.crns['oHr'][i][1]])
                self.roxie = self.ax.scatter(cc_roxie[0], cc_roxie[1], edgecolor='r', facecolor='none')

            self.fiqus = self.ax.scatter(cc_fiqus[0], cc_fiqus[1], c="green")

    def postProcess(self, postproc):
        df_ref = pd.DataFrame()
        model_file_extension = 'EM' if 'compare_to_ROXIE' in postproc.model_dump() else 'TH'

        if postproc.model_dump().get('compare_to_ROXIE', False):
            # flag_self_field = False
            # path_map2d = Path(postproc.compare_to_ROXIE, "MQXA_All_" +
            #                   f"{'WithIron_' if self.data.magnet.geometry.with_iron_yoke else 'NoIron_'}" +
            #                   f"{'WithSelfField' if flag_self_field else 'NoSelfField'}" +
            #                   f"{'' if flag_contraction else '_no_contraction'}" + ".map2d")
            df_ref = RoxieParsers.parseMap2d(map2dFile=Path(postproc.compare_to_ROXIE), physical_quantity='magnetic_flux_density')
            BB_roxie = np.linalg.norm(df_ref[['BX/T', 'BY/T']].values, axis=1)
            if postproc.plot_all != 'false':
                path_cond2d = Path(os.path.join(os.path.dirname(postproc.compare_to_ROXIE), self.data.general.magnet_name + ".cond2d"))
                # path_cond2d = Path(os.path.dirname(postproc.compare_to_ROXIE), "MQXA_All_NoIron_NoSelfField" +
                #                    f"{'' if flag_contraction else '_no_contraction'}" + ".cond2d")
                if os.path.isfile(path_cond2d):
                    conductorPositionsList = RoxieParsers.parseCond2d(path_cond2d)

        # Collect strands coordinates
        strands_x = df_ref['X-POS/MM'] / 1e3 if postproc.model_dump().get('compare_to_ROXIE', False) else self.strands['x']
        strands_y = df_ref['Y-POS/MM'] / 1e3 if postproc.model_dump().get('compare_to_ROXIE', False) else self.strands['y']

        # Probe physical quantity values from view and region areas
        physical_quantity_values = {'x': [], 'y': []}
        cond_areas, current_signs = [], []
        if postproc.model_dump().get('take_average_conductor_temperature', False):
            half_turns = {name[:-3]: str(values.vol.numbers[i])
                          for group, values in self.rm.powered.items() for i, name in enumerate(values.vol.names)}
            self.avg_temperatures = pd.concat([pd.read_csv(os.path.join(self.solution_folder, 'T_avg', 'T_avg_0.txt'),
                                                           delimiter=r'\s+', header=None, usecols=[0], names=['Time'])] +
                                              [pd.read_csv(os.path.join(self.solution_folder, 'T_avg', f'T_avg_{i}.txt'),
                                                           delimiter=r'\s+', header=None, usecols=[1], names=[ht.upper()]) for i, ht in enumerate(half_turns)], axis=1)
            self.avg_temperatures['Time'] = pd.read_csv(os.path.join(self.solution_folder, 'T_avg', 'T_avg_0.txt'),
                                                        delimiter=r'\s+', header=None, usecols=[0], names=['Time'])['Time']
            self.avg_temperatures = self.avg_temperatures[['Time'] + ['HT' + str(i) for i in range(1, self.strands['ht'][-1] + 1)]]
            columns_to_format = self.avg_temperatures.columns[1:]
            self.avg_temperatures[columns_to_format] = self.avg_temperatures[columns_to_format].round(4)
            self.avg_temperatures.to_csv(os.path.join(self.solution_folder, 'half_turn_temperatures_over_time.csv'), index=False)
        else:
            print(f"Info    : {self.data.general.magnet_name} - I n t e r p o l a t i n g . . .")
            print(f"Info    : Interpolating {'magnetic flux density' if 'compare_to_ROXIE' in postproc.model_dump() else 'temperature'} ...")

            # view = gmsh.view.getTags()[0] if len(postproc.variables) == 1 else self.postproc_settings[
            #     (self.postproc_settings['variables'] == self.supported_variables[self.physical_quantity]) &
            #     (self.postproc_settings['volumes'] == 'Omega_p')].index[0]

            view = gmsh.view.getTags()[0]
            for i in range(len(strands_x)):
                is_new_conductor = i == 0 or self.strands['ht'][i] != self.strands['ht'][i - 1]
                is_new_block = i == 0 or self.strands['block'][i] != self.strands['block'][i - 1]

                # Print update
                if is_new_block:
                    perc = round(self.strands['block'][i] / self.strands['block'][-1] * 100)
                    print(f"Info    : [{' ' if perc < 10 else ''}{' ' if perc < 100 else ''}{perc}%] Interpolating within block {self.strands['block'][i]}")

                # Probe
                probe_data = gmsh.view.probe(view, strands_x[i], strands_y[i], 0)[0]
                if 'compare_to_ROXIE' in postproc.model_dump():
                    physical_quantity_values['x'].append(probe_data[0])
                    physical_quantity_values['y'].append(probe_data[1])
                else:
                    physical_quantity_values['x'].append(probe_data[0])
                    physical_quantity_values['y'].append(0)

                # Plot conductor and block identifiers
                if postproc.model_dump().get('compare_to_ROXIE', False) and postproc.plot_all != 'false':
                    if is_new_conductor:
                        self.ax.text(df_ref['X-POS/MM'][i] / 1e3, df_ref['Y-POS/MM'][i] / 1e3, str(self.strands['ht'][i]),
                                     style='italic', bbox={'facecolor': 'blue', 'pad': 3})
                    if is_new_block:
                        mid_strand_index = round(self.strands['ht'].count(self.strands['ht'][i]) / 2)
                        self.ax.text(df_ref['X-POS/MM'][i + mid_strand_index] / 1e3, df_ref['Y-POS/MM'][i + mid_strand_index] / 1e3,
                                     str(self.strands['block'][i]), style='italic', bbox={'facecolor': 'green', 'pad': 3})

                # Get current sign
                current_signs.append(self.md.domains.physical_groups.blocks[self.strands['block'][i]].current_sign)

                # Get region area
                if is_new_conductor:
                    gmsh.plugin.setNumber("MeshVolume", "Dimension", 2)
                    gmsh.plugin.setNumber("MeshVolume", "PhysicalGroup",
                                          self.md.domains.physical_groups.blocks[self.strands['block'][i]].half_turns[self.strands['ht'][i]].tag)
                    gmsh.plugin.run("MeshVolume")
                    cond_areas.append(gmsh.view.getListData(gmsh.view.getTags()[-1])[2][-1][-1])
                else:
                    cond_areas.append(cond_areas[-1])

            print(f"Info    : {self.data.general.magnet_name} - E n d   I n t e r p o l a t i n g")

            # Assemble map2d content
            strands_nr = 0
            content = []
            for i, ht in enumerate(self.strands['ht']):
                if i == 0 or ht != self.strands['ht'][i - 1]:
                    strands_nr = self.strands['ht'].count(ht)
                content.append(self.formatted_content.format(
                    int(self.strands['block'][i]),                  # bl
                    int(ht),                                        # cond
                    int(i + 1),                                     # no
                    f"{strands_x[i] * 1e3:.4f}",                    # x
                    f"{strands_y[i] * 1e3:.4f}",                    # y
                    f"{physical_quantity_values['x'][i]:.4f}",      # pq_x
                    f"{physical_quantity_values['y'][i]:.4f}",      # pq_y
                    f"{cond_areas[i] / strands_nr * 1e6:.4f}",      # area
                    f"{current_signs[i] * self.data.power_supply.I_initial / strands_nr:.2f}",                  # curr
                    f"{df_ref['FILL FAC.'][i] if postproc.model_dump().get('compare_to_ROXIE', False) else 0:.4f}"))    # fill_fac

            # Save map2d file
            with open(f"{self.model_file}_{model_file_extension}.map2d", 'w') as file:
                file.write(self.formatted_headline.format(*self.map2d_headline_names))
                file.writelines(content)
            print(f"Info    : Map2D file saved.")
            print(f"WARNING : [Map2D] All strand surface areas are equal within a conductor. Refer to the ROXIE map2d file for actual values")
            if not postproc.model_dump().get('compare_to_ROXIE', True):
                print(f"WARNING : [Map2D] No data is available for Filling Factor. Refer to the ROXIE map2d file for correct values")

        # Compute errors
        pq = np.linalg.norm(np.column_stack((np.array(physical_quantity_values['x']), np.array(physical_quantity_values['y']))), axis=1)
        if postproc.model_dump().get('compare_to_ROXIE', False):
            BB_err = pq - BB_roxie
            self.postprocess_parameters['overall_error'] = np.mean(abs(BB_err))
            self.postprocess_parameters['minimum_diff'] = np.min(BB_err)
            self.postprocess_parameters['maximum_diff'] = np.max(BB_err)

        if postproc.plot_all != 'false':
            if postproc.model_dump().get('take_average_conductor_temperature', False):
                min_value = self.avg_temperatures.iloc[:, 1:].min().min()
                max_value = self.avg_temperatures.iloc[:, 1:].max().max()
                ht_polygons = [patches.Polygon(np.array([(self.crns['iHr'][i][0], self.crns['iHr'][i][1]),
                                                         (self.crns['iLr'][i][0], self.crns['iLr'][i][1]),
                                                         (self.crns['oLr'][i][0], self.crns['oLr'][i][1]),
                                                         (self.crns['oHr'][i][0], self.crns['oHr'][i][1])]) * 1e2,
                                               closed=True) for i in range(len(self.crns['iHr']))]
                collection = PatchCollection(ht_polygons)
                self.ax.add_collection(collection)
                cmap = plt.get_cmap('plasma')
                norm = plt.Normalize(vmin=min_value, vmax=max_value)
                cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=self.ax)
                cbar.set_label('Temperature [K]')
                self.ax.autoscale_view()
                for i in range(self.avg_temperatures['Time'].size):
                    collection.set_facecolor(cmap(norm(self.avg_temperatures.iloc[i, 1:])))
                    if postproc.plot_all == 'true':
                        plt.pause(0.05)

            else:
                self.plotHalfTurnGeometry(postproc.model_dump().get('compare_to_ROXIE', False))
                map2d_strands = self.ax.scatter(strands_x, strands_y, edgecolor='black', facecolor='black', s=10)

                scatter3D_pos = self.ax3.scatter3D(strands_x, strands_y, pq, c=pq, cmap='Greens', vmin=0, vmax=10)

                if postproc.model_dump().get('compare_to_ROXIE', False):
                    if os.path.isfile(path_cond2d):
                        conductors_corners = [condPos.xyCorner for condPos in conductorPositionsList]
                        for corners in conductors_corners:
                            for corner in range(len(corners)):
                                self.ax.scatter(corners[corner][0] / 1e3, corners[corner][1] / 1e3, edgecolor='black', facecolor='black', s=10)

                    self.ax2.scatter3D(strands_x, strands_y, BB_err, c=BB_err, cmap='viridis')  # , vmin=-0.2, vmax=0.2)
                    scatter4 = self.ax4.scatter(np.array(strands_x) * 1e2, np.array(strands_y) * 1e2, s=1, c=np.array(BB_err) * 1e3, cmap='viridis')
                    scatter3D_pos_roxie = self.ax3.scatter3D(strands_x, strands_y, BB_roxie, c=BB_roxie, cmap='Reds', vmin=0, vmax=10)

                    cax4 = self.fig4.add_axes((self.ax4.get_position().x1 + 0.02, self.ax4.get_position().y0,
                                               0.02, self.ax4.get_position().height))
                    cbar = plt.colorbar(scatter4, cax=cax4)
                    cbar.ax.set_ylabel('Absolute error [mT]', rotation=270)
                    self.ax3.legend([scatter3D_pos, scatter3D_pos_roxie], ['FiQuS', 'ROXIE'], numpoints=1)
                    self.ax.legend([self.fiqus, self.roxie, map2d_strands], ['FiQuS', 'ROXIE'], numpoints=1)
                    self.fig4.savefig(f"{os.path.join(self.solution_folder, self.data.general.magnet_name)}.svg", bbox_inches='tight')

            if postproc.plot_all == 'true':
                plt.show()

        # os.remove(os.path.join(self.solution_folder, 'b_Omega_p.pos'))
        # os.remove(f"{os.path.join(self.solution_folder, self.data.general.magnet_name)}.pre")
        # os.remove(f"{os.path.join(os.path.dirname(self.solution_folder), self.data.general.magnet_name)}.msh")

    def completeMap2d(self):
        def _quadrant(x, y):
            if x < 0 and y < 0: return 3
            elif x < 0: return 2
            elif y < 0: return 4
            else: return 1

        if self.data.magnet.geometry.electromagnetics.symmetry == 'xy':
            if self.strands['poles'] == 2:
                mirror_components = {2: [-1, 1], 3: [1, 1], 4: [-1, 1]}
            elif self.strands['poles'] == 4:
                mirror_components = {2: [1, -1], 3: [-1, -1], 4: [-1, 1]}
        elif self.data.magnet.geometry.electromagnetics.symmetry == 'x':
            if self.strands['poles'] == 2:
                mirror_components = {3: [-1, 1], 4: [-1, 1]}
            elif self.strands['poles'] == 4:
                mirror_components = {3: [-1, 1], 4: [-1, 1]}
        elif self.data.magnet.geometry.electromagnetics.symmetry == 'y':
            if self.strands['poles'] == 2:
                mirror_components = {2: [-1, 1], 3: [-1, 1]}
            elif self.strands['poles'] == 4:
                mirror_components = {2: [1, -1], 3: [1, -1]}
        else:
            mirror_components = {}

        print(f"Info    : {self.data.general.magnet_name} - M i r r o r i n g . . .")
        print(f"Info    : Mirroring by symmetry ...")
        blocks_nr = self.strands['block'][-1]

        with open(f"{self.model_file}_EM.map2d", 'r') as file:
            file_content = file.read()
            content_by_row = file_content.split('\n')
        new_content = [content_by_row[0] + '\n' + content_by_row[1] + '\n']
        prev_block: int = 0
        for row in content_by_row[2:-1]:
            entries = row.split()
            str_nr, x_coord, y_coord = entries[2], float(entries[3]), float(entries[4])
            qdr = _quadrant(x_coord, y_coord)
            if qdr in mirror_components:
                #found = re.search(f" {str(abs(x_coord))} +{str(abs(y_coord))}", file_content)
                #BB = [row_ref for row_ref in content_by_row if f" {abs(x_coord):.4f}       {abs(y_coord):.4f}" in row_ref][0].split()[5:7]
                BB = content_by_row[self.strands['mirrored'][str_nr] + 1].split()[5:7]
                row = row.replace(entries[5], f'{mirror_components[qdr][0] * float(BB[0]):.4f}')
                row = row.replace(entries[6], f'{mirror_components[qdr][1] * float(BB[1]):.4f}')
            if int(entries[0]) > prev_block:
                perc = round(int(entries[0]) / blocks_nr * 100)
                print("Info    : [" + f"{' ' if perc < 10 else ''}" + f"{' ' if perc < 100 else ''}" + f"{perc}" +
                      "%] Mirroring within block" + f"{entries[0]}")
                prev_block = int(entries[0])
            new_content.append(row + '\n')
        with open(f"{self.model_file}_EM.map2d", 'w') as file:
            file.writelines(new_content)
        print(f"Info    : {self.data.general.magnet_name} - E n d   M i r r o r i n g")
