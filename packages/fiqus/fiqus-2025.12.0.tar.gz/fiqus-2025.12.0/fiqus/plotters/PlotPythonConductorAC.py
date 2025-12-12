import os, re, datetime, getpass, logging, sys
import numpy as np
import subprocess as sp
import matplotlib.pyplot as plt

from scipy import interpolate, constants
from dataclasses import dataclass
from matplotlib.ticker import FuncFormatter
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_pdf import PdfPages, Stream, PdfFile
from fiqus.utils.Utils import FilesAndFolders


@dataclass
class PlotData:
    x_data: np.ndarray
    y_data: np.ndarray
    label: str
    color: np.ndarray
    linestyle: str = '-'


class PDFreport:
    def __init__(self, filepath, title='PostprocReport'):
        self.creation_date = datetime.datetime.now()
        self.author = getpass.getuser()
        self.file = os.path.join(filepath, str(title) + '.pdf')
        self.pdf = PdfPages(self.file)
        # init metadata
        self.add_metadata()

    def multi_sim_report(self):
        sims = self.plotter.simulation_collection

    def add_table(self, title, data, row_header=None, col_header=None):
        title_text = title
        footer_text = self.author + ' - ' + str(datetime.datetime.now())
        fig_background_color = 'white'
        fig_border = 'steelblue'

        column_headers = ['taus (s)', 'kappas (A)', 'alphas']
        row_headers = []
        # while I'm at it.
        cell_text = []
        for idx, row in enumerate(data):
            cell_text.append([f'{x:f}' for x in row])
            row_headers.append('k=' + str(idx + 1))
        # Get some lists of color specs for row and column headers
        rcolors = plt.cm.BuPu(np.full(len(row_headers), 0.1))
        ccolors = plt.cm.BuPu(np.full(len(column_headers), 0.1))  # Create the figure. Setting a small pad on tight_layout
        # seems to better regulate white space. Sometimes experimenting
        # with an explicit figsize here can produce better outcome.
        plt.figure(linewidth=2, edgecolor=fig_border, facecolor=fig_background_color, tight_layout={'pad': 1}, figsize=(5, 3))
        the_table = plt.table(cellText=cell_text, rowLabels=row_headers, rowColours=rcolors, rowLoc='right',
                              colColours=ccolors, colLabels=column_headers, loc='center')
        # Scaling is the only influence we have over top and bottom cell padding.
        # Make the rows taller (i.e., make cell y scale larger).
        the_table.scale(1, 1.5)  # Hide axes
        ax = plt.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)  # Hide axes border
        plt.box(on=None)  # Add title
        plt.suptitle(title_text)  # Add footer
        plt.figtext(0.95, 0.05, footer_text, horizontalalignment='right', size=6, weight='light')  # Force the figure to update, so backends center objects correctly within the figure.
        # Without plt.draw() here, the title will center on the axes and not the figure.
        plt.draw()  # Create image. plt.savefig ignores figure edge and face colors, so map them.
        fig = plt.gcf()
        self.savefigs()
        plt.close()

    def savefigs(self):
        """ Save all open figures one on each page """
        for i in plt.get_fignums():
            self.pdf.savefig(i)

    def add_metadata(self):
        d = self.pdf.infodict()
        d['Title'] = 'Report'
        d['Author'] = getpass.getuser()
        d['CreationDate'] = datetime.datetime.now()

    def __del__(self):
        """ save all generated figures and close report on destruction """
        self.savefigs()
        self.pdf.close()


class PlotPythonConductorAC:
    """
    This class handles various plots for single simulation CACStrand models.
    """

    def __init__(self, fdm, outputs_folder_path='', simulation_data=None, flux_model=None) -> None:
        self.fdm = fdm
        self.outputs_folder_path = os.path.join(outputs_folder_path, fdm.magnet.postproc.output_folder)  # This is the path to the folder where the postprocessed data is written
        self.simulation_data = simulation_data
        self.flux_model = flux_model
        # self.pdf_report = PDFreport(fdm=fdm,author=getpass.getuser(),outputs_folder_path=self.simulation_data.solution_folder) if fdm.magnet.postproc.generate_pdf else None

    def colors(self, length):
        """ unify color scheme for all plots """
        return plt.cm.rainbow(np.linspace(0.05, 0.9, length))

    def export2txt(self, data_names, data_columns, filename):
        """ This function can be used to export one or more arrays of simulation data in one txt file (stored in solution folder)."""
        np_data = np.array(data_columns).T
        np.savetxt(os.path.join(self.simulation_data.solution_folder, str(filename) + '.txt'), np_data, header=" ".join(data_names), comments="")

    def plot_power_loss(self):
        """ Compares the losses produced by the ROHF model S_chain to the corresponding filament losses """

        t_final = np.array(self.simulation_data.time)[-1]
        if self.flux_model:
            _, p_irr_rohf, p_eddy_rohf, per_cycle_rohf, _ = self.flux_model.compute(self.simulation_data.time, self.simulation_data.I_transport, sim=self.simulation_data)
        if self.simulation_data.f and 1 / self.simulation_data.f < t_final:
            offset_time = t_final - 1 / self.simulation_data.f
            offset_idx = np.abs(self.simulation_data.time - offset_time).argmin()
            lastp_time = self.simulation_data.time[offset_idx:]
            lastp_I = self.simulation_data.I_transport[offset_idx:]
            lastp_int_flux = self.simulation_data.flux_internal[offset_idx:]
            lastp_filamentloss = self.simulation_data.power["FilamentLoss"][offset_idx:]
            # selffield_power_unitarea_loop_factor = 2 * selffield_power_unitarea # missing 2x radial contribution (eddy)
            print("#### HYSTERETIC SURFACE ####")
            print("simple flux surface:   " + str(np.trapz(lastp_I, lastp_int_flux)))
            print("###### PER CYCLE LOSS ######")
            print("FilamentLoss " + str(self.simulation_data.total_power_per_cycle["FilamentLoss"]))
            if self.flux_model: print("ROHF Pirr:        " + str(per_cycle_rohf))

        colorgrad = self.colors(3)
        #### DYNAMIC LOSS ####
        plt.figure()
        plt.title("Instantaneous power losses")
        plt.plot(self.simulation_data.time, self.simulation_data.power["TotalLoss"], color=colorgrad[0], linestyle='--', label="Total loss")
        plt.plot(self.simulation_data.time, self.simulation_data.power["FilamentLoss"], color=colorgrad[1], linestyle='--', label="Filament loss")
        plt.plot(self.simulation_data.time, self.simulation_data.power["EddyLoss"], color=colorgrad[2], linestyle='--', label="Eddy loss")
        # plt.plot(self.time, graphic_loss, color=self.c_grad[-2], label=r'graphic $P_{\text{irr}}$')
        if self.flux_model:
            plt.plot(self.simulation_data.time, p_irr_rohf + p_eddy_rohf, color=colorgrad[0], label=r'ROHF ($N=$' + str(self.flux_model.N) + r') $P_{\mathrm{total}}$')
            plt.plot(self.simulation_data.time, p_irr_rohf, color=colorgrad[1], label=r'ROHF ($N=$' + str(self.flux_model.N) + r') $P_{\mathrm{irr}}$')
            plt.plot(self.simulation_data.time, p_eddy_rohf, color=colorgrad[2], label=r'ROHF ($N=$' + str(self.flux_model.N) + r') $P_{\mathrm{eddy}}$')
            # plt.plot(self.simulation_data.time[:len(p_irr_rohf)], self.flux_model.Ec_0 * (abs(self.simulation_data.I_transport[:len(p_irr_rohf)])/self.flux_model.Ic_0)**(self.flux_model.n) * abs(self.simulation_data.I_transport[:len(p_irr_rohf)]), color=self.c_grad[-1], label = r'power-law Filament', linestyle='--')
        # plt.plot(self.time, abs(np.gradient(selffield_loss, self.time)) * (np.pi * strand_radius**2) , label=r'TEST selffield loss power')
        plt.xlabel(r'Time [s]')
        plt.ylabel(r"Power per unitlength [W']")
        plt.legend()
        plt.grid(linestyle='dotted')

    def plot_transport(self):
        """ This funcion makes a nice combined plot of Transport current and voltage """
        # make fancy plot

        colors = self.colors(2)
        fig, ax1 = plt.subplots()
        color = 'tab:red'
        ax1.set_title("Transport current and voltage")
        ax1.set_xlabel(r'Time $(s)$')
        ax1.set_ylabel(r'Current $(A)$', color=colors[0])
        ax1.plot(self.simulation_data.time, self.simulation_data.I_transport, color=colors[0])
        ax1.grid(axis='x', linestyle='dotted')
        ax1.tick_params(axis='y', labelcolor=colors[0])

        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel(r'Voltage $(V)$', color=colors[1])
        ax2.plot(self.simulation_data.time, self.simulation_data.V_transport_unitlen, color=colors[1])
        ax2.tick_params(axis='y', labelcolor=colors[1])
        ax2.grid(axis='y', linestyle='dotted')
        fig.tight_layout()

    def plot_phaseshift_voltage(self, phaseshift):
        # removes phaseshift from voltage
        if not self.f:
            raise ValueError(f'No shift plot for selected source type')

        time_delay = phaseshift / (360 * self.f)
        shift_idx = (np.abs(self.simulation_data.time - time_delay)).argmin()
        shifted_V = self.simulation_data.V_transport[shift_idx:]
        shifted_time = self.simulation_data.time[1 + shift_idx:] - self.simulation_data.time[shift_idx]

        # make fancy plot
        fig, ax1 = plt.subplots()
        color = 'tab:red'
        ax1.set_title("shifted voltage (" + str(phaseshift) + " degree)")
        ax1.set_xlabel(r'Time $(s)$')
        ax1.set_ylabel(r'Current $(A)$', color=color)
        ax1.plot(self.simulation_data.time, self.simulation_data.I_transport, color=color)
        ax1.grid(axis='x', linestyle='dotted')
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel(r'Voltage $(V)$', color=color)
        ax2.plot(shifted_time, shifted_V, color=color, linestyle='dashed')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.grid(axis='y', linestyle='dotted')
        fig.tight_layout()

    def plot_flux(self):
        """ This plots the internal flux obtained through two approaches and compares them with an s_chain model """
        # L_base = (self.simulation_data.flux_internal[1]-self.simulation_data.flux_internal[0])/(self.simulation_data.I_transport[1]-self.simulation_data.I_transport[0])
        if self.flux_model:
            flux_rohf, _, _, _, _ = self.flux_model.compute(self.simulation_data.time, self.simulation_data.I_transport, sim=self.simulation_data)

        colors = self.colors(3)
        ### SIMPLE FLUX HOMOGENIZATION ###
        plt.figure()
        plt.title("Internal flux ")
        plt.xlabel(r"Transport current $[A]$")
        plt.ylabel(r"Flux per unitlength $[Tm]$")
        # plt.plot(self.I_transport, self.flux_external, color=self.c_grad[2], label = r'$\Phi_{\text{ext}}$')
        plt.plot(self.simulation_data.I_transport, self.simulation_data.flux_internal, color=colors[0], label=r'$\Phi_{\text{int}}$')
        plt.plot(self.simulation_data.I_transport, constants.mu_0 / (4 * np.pi) * self.simulation_data.I_transport, color=colors[1], label=r"$L'=\mu_0/(4 \pi)$")
        if self.flux_model: plt.plot(self.simulation_data.I_transport, flux_rohf, color=colors[2], label=r'$\Phi_{\text{ROHF}}$ ($N=$' + str(self.flux_model.N) + ')')
        plt.grid(linestyle='dotted')
        plt.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
        plt.legend()
        plt.grid(axis='y', linestyle='dotted')

        ### FLUX BASED VOLTAGE ###
        if self.flux_model: voltage_rohf = -np.gradient((flux_rohf + self.simulation_data.flux_external), self.simulation_data.time)
        plt.figure()
        plt.title("flux based Voltage")
        plt.xlabel(r"Time $[s]$")
        plt.ylabel(r"Voltage per unit-length $\left[\frac{V}{m}\right]$")
        # plt.plot(self.time, -np.gradient((self.flux_internal + self.flux_external), self.time), color=self.c_grad[3], label = r'$-\frac{d\Phi}{dt}$ graphic')
        if self.flux_model: plt.plot(self.simulation_data.time, voltage_rohf, color=colors[2], label=r'$-\frac{d\Phi}{dt}$ ROHF ($N=$' + str(self.flux_model.N) + ')')
        plt.plot(self.simulation_data.time, self.simulation_data.V_transport_unitlen, color=colors[0], linestyle='--', label=r'$V$ transport')
        plt.grid(linestyle='dotted')
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        plt.legend()
        plt.grid(axis='y', linestyle='dotted')

        V = self.simulation_data.V_transport_unitlen
        I = self.simulation_data.I_transport
        idx = min(range(len(V)), key=lambda i: abs(V[i] + 1e-4))
        print("ciritical current: " + str(I[idx]))

        # data = np.vstack([self.simulation_data.I_transport, self.simulation_data.flux_internal, flux_rohf])
        # self.export2txt(['current','internal_flux','rohf_flux'], data, 'flux_hysteresis')

    def plot_current_rings(self):
        """
        This function decomposes the total transport current into an reversible and irreversible part based on inner flux computations of the filaments.
        It is basically the dual approach to the plot_voltage_decomp() function declared here after but shouldnt suffer from its numeric instabilities.
        """

        t_final = np.array(self.simulation_data.time)[-1]
        if not self.simulation_data.f or 1 / self.simulation_data.f > t_final:
            raise ValueError(r'Cant plot current rings')

        ### plot current threshold rings ###
        if self.flux_model:
            jc_real = 3.33e10
            circle_radii = np.sqrt(self.simulation_data.conductor.strand.number_of_filaments * (self.simulation_data.conductor.strand.filament_diameter / 2) ** 2 - np.array(self.flux_model.kappas_bar) / (jc_real * np.pi))
            circle_surfaces = np.pi * circle_radii ** 2
            ringwidth = np.diff(np.flip(circle_radii), prepend=0)

            plt.figure()
            plt.title("ROHF single filament - field free zones")
            for idx, radius in enumerate(circle_radii):
                shells = [plt.Circle((2.05 * circle_radii[0] * idx, 0), radius, color=self.c_grad[idx], hatch='//', label="> " + "{:.2f}".format(self.flux_model.kappas_bar[idx]) + " A", fill=False),
                          plt.Circle((2.05 * circle_radii[0] * idx, 0), circle_radii[0], color='black', fill=False)]  # contour
                for shell in shells: plt.gca().add_patch(shell)
            # core = plt.Circle((0,0), circle_radii[-1], color='white')
            # plt.gca().add_patch(core)
            plt.legend()
            plt.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
            plt.xlim(-1.1 * circle_radii[0], 2.1 * len(circle_radii) * circle_radii[0])
            plt.ylim(-1.1 * circle_radii[0], 1.1 * circle_radii[0])

    def plot_fft_voltage(self):
        """ analyze the transport voltage in the frequency domain """
        if self.simulation_data.f:
            T = 1 / self.simulation_data.f
            start_idx = abs(self.simulation_data.time - (max(self.simulation_data.time) - T)).argmin() - 2
            X = np.fft.fft(self.simulation_data.V_transport_unitlen[start_idx:])
            N = len(X)
            n = np.arange(N)
            freq = n / T

            fig, axs = plt.subplots(2)
            fig.suptitle(r'Frequency domain voltage')
            axs[0].stem(freq, np.abs(X), 'b', markerfmt=" ", basefmt="-b")
            axs[0].set_xlabel('Freq (Hz)')
            axs[0].set_ylabel('FFT Amplitude |X(freq)|')
            axs[0].grid(linestyle='dotted')
            axs[0].set_xlim([0, 10 * self.simulation_data.f])

            axs[1].plot(self.simulation_data.time[:start_idx - 1], self.simulation_data.V_transport_unitlen[:start_idx - 1], '--r')
            axs[1].plot(self.simulation_data.time[start_idx:], np.fft.ifft(X), 'r', label='transport voltage')
            axs[1].set_xlabel('Time (s)')
            axs[1].set_ylabel('Amplitude')
            axs[1].grid(linestyle='dotted')
            axs[1].set_xlim([0, max(self.simulation_data.time)])

    def plot_instantaneous_power(self, show: bool = True, title: str = "Power", save_plot: bool = False, save_folder_path: str = None, save_file_name: str = None, overwrite: bool = False):
        plt.figure()
        plt.plot(self.simulation_data.power['Time'], self.simulation_data.power[self.simulation_data.power_columns[1:]], label=self.simulation_data.power_columns[1:])
        plt.xlabel('Time [s]')
        plt.ylabel('Power [W/m]')
        plt.legend()

        # Configure title:
        # Class attributes can be accessed by using '<< ... >>' in the title string.
        commands = re.findall('<<(.*?)>>', title)
        for c in commands:
            title = title.replace(f"<<{c}>>", str(eval('self.simulation_data.' + c)))
        plt.title(title)

        if save_plot:  # Save the plot
            filePath = os.path.join(save_folder_path, str(save_file_name) + '.png')
            plt.savefig(filePath)

        if show:
            plt.show()
        else:
            plt.close()

    def plot_impedance(self, frequency_range):
        """ This function compares the estimated data impedance with an analytic solution for inductive tranmission """

        if not self.simulation_data.f or not self.simulation_data.analytic_RL:
            raise ValueError(f'No impedance estimate for selected source type')
        analytic_impedance = self.simulation_data.analytic_RL[0] + 1j * 2 * np.pi * frequency_range * self.simulation_data.analytic_RL[1]  # R + jwL

        fig, axs = plt.subplots(2)
        fig.suptitle(r'Simulation Impedance $Z$')
        axs[0].plot(frequency_range, np.abs(np.imag(analytic_impedance)), '-b', label="pure Inductance")
        axs[0].plot(self.simulation_data.f, np.abs(self.simulation_data.data_impedance), 'r', marker="x", label="simulation")
        axs[0].set_xscale('log')
        axs[0].set_yscale('log')
        axs[0].set_ylabel(r'Magnitude $|Z|$')
        axs[0].grid(linestyle='dotted')
        axs[0].legend()

        axs[1].plot(frequency_range, 90 * np.ones((len(frequency_range), 1)), '-b', label="pure Inductance")
        axs[1].plot(self.simulation_data.f, np.angle(self.simulation_data.data_impedance, deg=True), 'r', marker="x", label="simulation")
        axs[1].set_xscale('log')
        axs[1].set_ylim([-15, 105])
        axs[1].set_ylabel(r'Phase $\measuredangle{Z}$' + r' $(deg)$')
        axs[1].set_xlabel(r'Frequency $(Hz)$')
        axs[1].grid(linestyle='dotted')
        axs[1].legend()

    def plot_resistivity(self):

        time, I, flux = self.simulation_data.first_rise(current=True)

        if self.flux_model:
            flux_rohf, p_irr, _, _, _ = self.flux_model.compute(time, I, sim=self.simulation_data)
            # p_ohm_fil, p_ohm_mat, R_fil, R_mat = self.flux_model.ohmic_loss(I, self.simulation_data)

        colors = self.colors(3)
        ### SIMPLE FLUX HOMOGENIZATION ###
        plt.figure(figsize=(5, 8))
        plt.title("Differential resitivity")
        plt.xlabel(r"Transport current $[A]$")
        plt.ylabel(r"Transport voltage per unit length $[V/m]$")
        # plt.plot(self.I_transport, self.flux_external, color=self.c_grad[2], label = r'$\Phi_{\text{ext}}$')
        plt.plot(I, abs(self.simulation_data.V_transport_unitlen[:len(I)]), color=colors[0], label=r'FEM reference')
        # plt.plot(I, (1.68e-10/(0.5*np.pi*(0.5e-3)**2))*I, color=self.c_grad[1], label='RRR100 copper')
        if self.flux_model:
            plt.plot(I, self.flux_model.Ec_0 * (abs(I) / self.flux_model.Ic_0) ** (self.flux_model.n), color=colors[1], label=r'Power-law only')
            plt.plot(I, (p_irr) / I, color=colors[2], label=r'ROHF current sharing')
            plt.axhline(y=self.flux_model.Ec_0, color='black', linestyle='--', label=r'$E_c = 1^{-4} \mathrm{V}/\mathrm{m}$')
            # plt.axis([0.7*self.flux_model.Ic_0, 1.2*self.flux_model.Ic_0, 0, 100*self.flux_model.Ec_0])
        plt.grid(linestyle='dotted')
        plt.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
        plt.legend()
        plt.grid(axis='y', linestyle='dotted')

    def show(self):
        plt.show()


class BatchPlotPythonConductorAC:
    """
    This class loads and stores the data from the simulations specified in a csv file and can apply various postprocessing operations on the data.
    The data from each simulation is saved as a SimulationData object which is subsequently stored in a list in this class.
    """

    def __init__(self, fdm, lossMap_gridData_folder=None, outputs_folder_path='', simulation_collection=None, fluxmodel_collection=None) -> None:
        self.fdm = fdm
        self.outputs_folder_path = os.path.join(outputs_folder_path, fdm.magnet.postproc.output_folder)  # This is the path to the folder where the postprocessed data is written
        self.simulation_collection = simulation_collection
        self.fluxmodel_collection = fluxmodel_collection
        try:
            sp.run(['pdflatex', '--version'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            tex_installation = True
        except:
            tex_installation = False
        self.tex_installation = tex_installation

        if not os.path.exists(self.outputs_folder_path):
            os.makedirs(self.outputs_folder_path)

        if lossMap_gridData_folder is not None:
            self.totalLoss_gridData = self.load_lossMap_gridData('TotalLoss', lossMap_gridData_folder)
            self.filamentLoss_gridData = self.load_lossMap_gridData('FilamentLoss', lossMap_gridData_folder)
            self.eddyLoss_gridData = self.load_lossMap_gridData('EddyLoss', lossMap_gridData_folder)
            self.couplingLoss_gridData = self.load_lossMap_gridData('CouplingLoss', lossMap_gridData_folder)

    def colors(self, length):
        """ unify color scheme for plots """
        return plt.cm.rainbow(np.linspace(0.05, 0.9, length))

    def create_non_overwriting_filepath(self, folder_path, base_name, extension, overwrite):
        """
            Creates a filepath that does not overwrite any existing files.

            This function checks if a file already exists at the specified filepath. If the file exists and `overwrite` is False,
            it modifies the filepath to create a new file instead of overwriting the existing one.
            If `overwrite` is True or the file does not exist, it returns the filepath as it is.

            Parameters
            ----------
            folder_path : str
                The path to the folder where the file will be created.
            base_name : str
                The base name of the file.
            extension : str
                The extension of the file.
            overwrite : bool, optional
                If True, the function will overwrite an existing file. If False, the function will modify the filepath to avoid overwriting. Defaults to False.

            Returns
            -------
            str
                The final filepath. If `overwrite` is False and a file already exists at the original filepath, this will be a new filepath that does not overwrite any existing files.
        """
        if os.path.exists(os.path.join(folder_path, base_name + extension)) and not overwrite:
            counter = 1
            new_name = base_name + f"_{counter}" + extension
            while os.path.exists(os.path.join(folder_path, new_name)):
                new_name = base_name + f"_{counter}" + extension
                counter += 1
            return os.path.join(folder_path, new_name)

        return os.path.join(folder_path, base_name + extension)

    def lossMap_createGridData(self, lossType='TotalLoss', x_val_to_include=None, y_val_to_include=None):
        """
        This function creates the grid data needed for the loss map, based on the yaml input file.
        Given a collection of simulations it interpolates the loss data between the datapoints to a grid and returns the grid data.
        """
        lm = self.fdm.magnet.postproc.batch_postproc.loss_map

        # Extract data from simulation collection and normalize
        x_arr = np.array([eval('sd.' + lm.x_val) / lm.x_norm for sd in self.simulation_collection])
        y_arr = np.array([eval('sd.' + lm.y_val) / lm.y_norm for sd in self.simulation_collection])
        loss = np.array([sd.total_power_per_cycle[lossType] / lm.loss_norm for sd in self.simulation_collection])

        # Logarithmic scaling
        if lm.x_log: x_arr = np.log10(x_arr)
        if lm.y_log: y_arr = np.log10(y_arr)
        if lm.loss_log: loss = np.log10(loss)

        x_arr_interpolated = np.linspace(min(x_arr), max(x_arr), lm.x_steps)
        y_arr_interpolated = np.linspace(min(y_arr), max(y_arr), lm.y_steps)
        # Insert specific values to the grid if they are not already included (useful for cross sections)
        if x_val_to_include is not None and x_val_to_include not in x_arr_interpolated:
            x_arr_interpolated = np.insert(x_arr_interpolated, np.where(x_arr_interpolated > x_val_to_include)[0][0], x_val_to_include)
        if y_val_to_include is not None and y_val_to_include not in y_arr_interpolated:
            y_arr_interpolated = np.insert(y_arr_interpolated, np.where(y_arr_interpolated > y_val_to_include)[0][0], y_val_to_include)

        # Create grid
        X, Y = np.meshgrid(x_arr_interpolated, y_arr_interpolated, indexing='ij')
        gridPoints = np.c_[X.ravel(), Y.ravel()]
        dataPoints = np.c_[x_arr, y_arr]

        # Interpolate the simulation data onto the grid
        V = interpolate.griddata(
            dataPoints,
            loss,
            gridPoints,
            method='linear'  # Cubic produces cleaner plots. Any incentive to go back to linear?
        ).reshape(X.shape)

        return X, Y, V, dataPoints

    def save_lossMap_gridData(self, save_folder_name='lossMap_gridData'):
        """
        This function calls the lossMap_createGridData function and saves the grid data.
        """
        lm = self.fdm.magnet.postproc.batch_postproc.loss_map

        lossTypes = ['TotalLoss', 'FilamentLoss', 'EddyLoss', 'CouplingLoss', 'CouplingLoss_dyn', 'TotalLoss_dyn']  # Only in the case dynamic correction is used, must be changed later
        # 1) Create a folder to store the output files
        gridData_folder_path = self.create_non_overwriting_filepath(self.outputs_folder_path, save_folder_name, '', self.fdm.run.overwrite)
        if not os.path.exists(gridData_folder_path): os.makedirs(gridData_folder_path)
        # 2) Create the grid data for each loss type and save it
        for lossType in lossTypes:
            X, Y, V, _ = self.lossMap_createGridData(lossType)
            if lm.x_log: X = np.power(10, X)
            if lm.y_log: Y = np.power(10, Y)
            if lm.loss_log: V = np.power(10, V)
            np.savetxt(os.path.join(gridData_folder_path, f'{lossType}.txt'), np.column_stack((X.ravel(), Y.ravel(), V.ravel())), delimiter=' ', header=f'{lm.x_val} {lm.y_val} {lossType}', comments='')

    def load_lossMap_gridData(self, lossType='TotalLoss', save_folder_name='lossMap_gridData'):
        """
        This function loads the grid data for a given loss type.
        """
        lm = self.fdm.magnet.postproc.batch_postproc.loss_map
        gridData_folder_path = os.path.join(self.inputs_folder_path, save_folder_name)

        if not os.path.exists(gridData_folder_path):
            raise FileNotFoundError(f'The folder {gridData_folder_path} does not exist.')

        X, Y, V = np.loadtxt(os.path.join(gridData_folder_path, f'{lossType}.txt'), unpack=True, skiprows=1)

        if lm.x_log: X = np.log10(X)
        if lm.y_log: Y = np.log10(Y)
        if lm.loss_log: V = np.log10(V)

        # Get the unique counts of X and Y
        unique_X = np.unique(X)
        unique_Y = np.unique(Y)

        # Reshape the data
        X = X.reshape((len(unique_X), len(unique_Y)))
        Y = Y.reshape((len(unique_X), len(unique_Y)))
        V = V.reshape((len(unique_X), len(unique_Y)))

        return X, Y, V

    def save_magnetization(self):
        """
        This function saves the magnetization data for all simulations in the simulation collection.
        """
        magnetization_folder_path = self.create_non_overwriting_filepath(self.outputs_folder_path, 'magnetization', '', self.fdm.run.overwrite)
        if not os.path.exists(magnetization_folder_path): os.makedirs(magnetization_folder_path)
        for sd in self.simulation_collection:
            magnetization = sd.magn_fil + sd.magn_matrix
            magnetization = np.c_[sd.time, magnetization]
            np.savetxt(os.path.join(magnetization_folder_path, f'magn_f{sd.solve.source_parameters.sine.frequency}_b{sd.solve.source_parameters.sine.field_amplitude}_I{sd.solve.source_parameters.sine.current_amplitude}.txt'), magnetization, delimiter=' ', header='t x y z', comments='')

    def lossMap_crossSection(self, slice_value, axis_to_cut='x'):
        """
        This function returns the data corresponding to a cross section of the loss map, for all loss types.
        Given an axis and a value, it sweeps the other axis for the closest value and returns the data.
        Example: Given slice value 0 and axis x, it returns the data for the cross section at x = 0.
        """

        lm = self.fdm.magnet.postproc.batch_postproc.loss_map
        if axis_to_cut == 'x':
            x_val_to_include = slice_value
            y_val_to_include = None
        elif axis_to_cut == 'y':
            x_val_to_include = None
            y_val_to_include = slice_value
        X, Y, V, dataPoints = self.lossMap_createGridData('TotalLoss', x_val_to_include, y_val_to_include)
        _, _, FilamentLoss, _ = self.lossMap_createGridData('FilamentLoss', x_val_to_include, y_val_to_include)
        _, _, EddyLoss, _ = self.lossMap_createGridData('EddyLoss', x_val_to_include, y_val_to_include)
        _, _, CouplingLoss, _ = self.lossMap_createGridData('CouplingLoss', x_val_to_include, y_val_to_include)

        if axis_to_cut == 'x':
            index = np.abs(X[:, 0] - slice_value).argmin()
            slice_vals = Y[index, :]

        elif axis_to_cut == 'y':
            index = np.abs(Y[0, :] - slice_value).argmin()
            slice_vals = X[:, index]

        # Extract the loss values for the constant frequency across all applied fields
        totalLoss = V[index, :] if axis_to_cut == 'x' else V[:, index]
        filamentLoss = FilamentLoss[index, :] if axis_to_cut == 'x' else FilamentLoss[:, index]
        eddyLoss = EddyLoss[index, :] if axis_to_cut == 'x' else EddyLoss[:, index]
        couplingLoss = CouplingLoss[index, :] if axis_to_cut == 'x' else CouplingLoss[:, index]

        return slice_vals, totalLoss, filamentLoss, eddyLoss, couplingLoss

    def plot_lossMap_crossSection(self):
        """
        This function calls the lossMap_crossSection function and plots the data it returns, which is the loss for all values of one axis, given a constant value of the other axis.
        """

        if self.tex_installation:
            plt.rcParams['text.usetex'] = True
            plt.rcParams['font.family'] = 'times'
            plt.rcParams['font.size'] = 20

        lm = self.fdm.magnet.postproc.batch_postproc.loss_map
        slice_value = lm.cross_section.cut_value
        axis_to_cut = lm.cross_section.axis_to_cut

        if (lm.x_log and axis_to_cut == 'x') or (lm.y_log and axis_to_cut == 'y'):
            slice_value = np.log10(slice_value)

        slice_vals, totalLoss, filamentLoss, eddyLoss, couplingLoss = self.lossMap_crossSection(slice_value, axis_to_cut=axis_to_cut)

        def log_formatter(x, pos):
            """
                Format the tick labels on the plot.
            """
            return f"$10^{{{int(x)}}}$"

        # Plot the loss with respect to applied field for the constant frequency
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(slice_vals, totalLoss, label=f'Total Loss')
        ax.plot(slice_vals, filamentLoss, label=f'Filament Loss')
        ax.plot(slice_vals, eddyLoss, label=f'Eddy Loss')
        ax.plot(slice_vals, couplingLoss, label=f'Coupling Loss')

        tick_formatter = FuncFormatter(log_formatter)
        if lm.x_log and axis_to_cut == 'y' or lm.y_log and axis_to_cut == 'x':
            ax.xaxis.set_major_formatter(tick_formatter)
        if lm.loss_log:
            ax.yaxis.set_major_formatter(tick_formatter)

        title = lm.cross_section.title.replace('<<cut_value>>', str(round(10 ** slice_value, 3)))
        ax.set_title(title)
        ax.set_xlabel(lm.ylabel if axis_to_cut == 'x' else lm.xlabel)
        ax.set_ylabel(lm.cross_section.ylabel)
        ax.legend()

        # np.savetxt(os.path.join(self.outputs_folder_path, 'lossMaps_cut_0p2T_0A.txt'), np.column_stack((10**slice_vals, 10**totalLoss, 10**eddyLoss, 10**couplingLoss, 10**filamentLoss)), delimiter=' ', header='f total eddy coupling filament', comments='')

        if lm.cross_section.save_plot:
            filePath = self.create_non_overwriting_filepath(self.outputs_folder_path, lm.cross_section.filename, '.png', self.fdm.run.overwrite)
            plt.savefig(filePath)

        if self.fdm.run.launch_gui: plt.show()

    def plot_percycle_losses(self, sims, flux_model, title):
        """ This function produces a frequency to per cycle power loss plot used within the ROHF parameter optimization """

        pc_irr_rohf = []
        pc_eddy_rohf = []
        pc_fil_sim = [sim.total_power_per_cycle['FilamentLoss'] for sim in sims]
        pc_eddy_sim = [sim.total_power_per_cycle['EddyLoss'] for sim in sims]
        freq = [sim.f for sim in sims]

        for sim in sims:
            _, _, _, irr, eddy = flux_model.compute(time=sim.time, I=sim.I_transport, sim=sim)
            pc_irr_rohf.append(irr)
            pc_eddy_rohf.append(eddy)

        plt.figure()
        plt.title(title)
        plt.plot(freq, pc_fil_sim, 'o-', label='FilamentLoss')
        plt.plot(freq, pc_irr_rohf, 'x-', label=r'$P_{\mathrm{irr}}$ ROHF')
        plt.plot(freq, pc_eddy_sim, 'o-', label='EddyLoss')
        plt.plot(freq, pc_eddy_rohf, 'x-', label=r'$P_{\mathrm{eddy}}$ ROHF')
        plt.legend()
        plt.xlabel(r'Frequency ($\mathrm{Hz}$)')
        plt.ylabel(r'Per cycle power loss ($\mathrm{W/m}$)')
        plt.xscale('log')
        plt.yscale('log')

    def plot_flux_time_triplet(self, flux_model, title):

        amplitudes = sorted(list(set([sim.I_amp for sim in self.simulation_collection])))

        high_I_sims = []
        mid_I_sims = []
        low_I_sims = []
        for sim in self.simulation_collection:
            if sim.I_amp == amplitudes[-1]:
                high_I_sims.append(sim)
            elif sim.I_amp == amplitudes[-2]:
                mid_I_sims.append(sim)
            elif sim.I_amp == amplitudes[2]:
                low_I_sims.append(sim)

        colors = self.colors(max([len(high_I_sims), len(mid_I_sims), len(low_I_sims)]))
        plt.figure()
        plt.title(title)
        plt.subplot(3, 1, 1)
        for i, sim in enumerate(high_I_sims):
            plt.plot(sim.time * sim.f, sim.flux_internal, color=colors[i], linestyle='--')
            plt.plot(sim.time * sim.f, flux_model.compute(I=sim.I_transport, time=sim.time, sim=sim)[0], color=colors[i], label=str(sim.f) + ' Hz')
        plt.legend()

        plt.subplot(3, 1, 2)
        for i, sim in enumerate(mid_I_sims):
            plt.plot(sim.time * sim.f, sim.flux_internal, color=colors[i], linestyle='--')
            plt.plot(sim.time * sim.f, flux_model.compute(I=sim.I_transport, time=sim.time, sim=sim)[0], color=colors[i], label=str(sim.f) + ' Hz')

        plt.subplot(3, 1, 3)
        for i, sim in enumerate(low_I_sims):
            plt.plot(sim.time * sim.f, sim.flux_internal, color=colors[i], linestyle='--')
            plt.plot(sim.time * sim.f, flux_model.compute(I=sim.I_transport, time=sim.time, sim=sim)[0], color=colors[i], label=str(sim.f) + ' Hz')
            # plt.ylabel(r'Internal Flux per unit length ($\mathrm{Tm}$)')
        plt.text(0.04, 0.5, r'Internal Flux per unit length ($\mathrm{Tm}$)', va='center', rotation='vertical')
        plt.xlabel(r'Time in periods')

    def animate_lossMap_crossSection(self):
        """
        This function is similar to the plot_lossMap_crossSection function, but instead of plotting the loss for at a constant crossection,
        it sweeps the crossection over a chosen axis and plots the loss for each crossection as an animation.
        """
        lm = self.fdm.magnet.postproc.batch_postproc.loss_map
        axis = lm.cross_section_sweep.axis_to_sweep

        X, Y, V, dataPoints = self.lossMap_createGridData('TotalLoss')
        x_vals = X[:, 0]  # x-values from the loss map
        y_vals = Y[0, :]  # y-values from the loss map

        if axis == 'x':
            A = np.zeros((lm.y_steps, 4, lm.x_steps))
            axis_to_sweep = x_vals
            constant_axis = y_vals
        elif axis == 'y':
            A = np.zeros((lm.x_steps, 4, lm.y_steps))
            axis_to_sweep = y_vals
            constant_axis = x_vals

        for i, val in enumerate(axis_to_sweep):
            _, totalLoss, filamentLoss, eddyLoss, couplingLoss = self.lossMap_crossSection(val, axis_to_cut=axis)
            A[:, 0, i] = totalLoss
            A[:, 1, i] = filamentLoss
            A[:, 2, i] = eddyLoss
            A[:, 3, i] = couplingLoss

        # Initialize the plot
        fig, ax = plt.subplots()
        lines = ax.plot(constant_axis, A[:, :, 0], lw=2, label=['total Loss', 'filament Loss', 'eddy Loss', 'coupling Loss'])

        # Set plot limits and labels
        ax.set_xlim(constant_axis[0], constant_axis[-1])
        ax.set_ylim(np.min(A), np.max(A))
        ax.set_xlabel(lm.ylabel if axis == 'x' else lm.xlabel)
        ax.set_ylabel(lm.cross_section_sweep.ylabel)

        # Define the animation update function
        def update(frame):
            for i, line in enumerate(lines):
                line.set_ydata(A[:, i, frame])

            if axis == 'x':
                if lm.x_log:
                    sweep_value = 10 ** x_vals[frame]
                else:
                    sweep_value = x_vals[frame]
            elif axis == 'y':
                if lm.y_log:
                    sweep_value = 10 ** y_vals[frame]
                else:
                    sweep_value = y_vals[frame]

            title = lm.cross_section_sweep.title.replace('<<sweep_value>>', str(round(sweep_value, 3)))
            ax.set_title(title)
            return lines,  # line1, line2, line3, line4

        # Create the animation
        dt = 0.1
        ani = FuncAnimation(fig, update, frames=lm.x_steps if axis == 'x' else lm.y_steps, interval=dt * 1000, blit=False)

        # Show the animation
        plt.legend()
        plt.grid()

        if lm.cross_section_sweep.save_plot:
            filepath = self.create_non_overwriting_filepath(folder_path=self.outputs_folder_path, base_name=lm.cross_section_sweep.filename, extension='.gif', overwrite=self.fdm.run.overwrite)
            ani.save(filepath, writer='imagemagick', fps=1 / dt)

        if self.fdm.run.launch_gui: plt.show()

    def create_lossMap(self):
        """
        This function creates a loss map based on the inputs given in the loss_map section of the input file.
        The loss-map can be plotted and saved as a .png file.
        """
        lm = self.fdm.magnet.postproc.batch_postproc.loss_map

        if self.simulation_collection:
            X, Y, V, dataPoints = self.lossMap_createGridData(lm.loss_type)
        else:
            X, Y, V = self.totalLoss_gridData

        if self.tex_installation:
            plt.rcParams['text.usetex'] = True
            plt.rcParams['font.family'] = 'times'
            plt.rcParams['font.size'] = 20

        fig, ax = plt.subplots(figsize=(10, 8))

        c = plt.pcolormesh(X, Y, V, shading='gouraud', cmap='plasma_r')
        c_min = min([np.ceil(np.min(V)) for V in [V]])
        c_max = max([np.floor(np.max(V)) for V in [V]])
        c_ticks = [int(val) for val in np.arange(c_min, c_max + 1)]
        cont = plt.contour(X, Y, V, c_ticks, colors='k', linestyles='dashed')

        if lm.show_datapoints:
            plt.scatter(dataPoints[:, 0], dataPoints[:, 1], s=50, edgecolors='k')

        if lm.show_loss_type_dominance_contour:
            sigmoid = lambda x: 1 / (1 + np.exp(-x))
            if self.simulation_collection:
                _, _, FilamentLoss, _ = self.lossMap_createGridData(lossType='FilamentLoss')
                _, _, CouplingLoss, _ = self.lossMap_createGridData(lossType='CouplingLoss')
                _, _, EddyLoss, _ = self.lossMap_createGridData(lossType='EddyLoss')
            # else:
            #     _, _, FilamentLoss = self.filamentLoss_gridData
            #     _, _, CouplingLoss = self.couplingLoss_gridData
            #     _, _, EddyLoss = self.eddyLoss_gridData
            fil_vs_coupling_loss = np.maximum(FilamentLoss, EddyLoss) - CouplingLoss
            fil_vs_eddy_loss = EddyLoss - np.maximum(FilamentLoss, CouplingLoss)
            plt.contour(X, Y, sigmoid(fil_vs_coupling_loss), [0.5], colors='k')
            plt.contour(X, Y, sigmoid(fil_vs_eddy_loss), [0.5], colors='k')

        cbar = fig.colorbar(c, ticks=c_ticks)  # , labels=c_labels)
        # cbar.ax.set_xticks([-7, -6, -5, -4, -3, -2, -1, 0, 1])
        # cbar.ax.set_yticklabels([r'$10^{-7}$', r'$10^{-6}$', r'$10^{-5}$', r'$10^{-4}$', r'$10^{-3}$', r'$10^{-2}$', r'$10^{-1}$', r'$10^0$', r'$10^1$'])
        cbar.ax.set_yticklabels([f"$10^{{{val}}}$" for val in c_ticks])
        # plt.grid(alpha=0.5)
        # plt.title(lm.title)
        # plt.xlabel(lm.xlabel)
        # plt.ylabel(lm.ylabel)
        plt.title(r'Loss per cycle (J/m)')
        plt.xlabel(r'Frequency $f$ (Hz)')
        plt.ylabel(r'Field amplitude $b$ (T)')

        # plt.annotate(r'Coupling', (np.log10(1.0), np.log10(0.007)), color='white')
        # plt.annotate(r'Filament', (np.log10(0.012), np.log10(0.74)), color='white')
        # plt.annotate(r'(uncoupled)', (np.log10(0.012), np.log10(0.55)), color='white')
        # plt.annotate(r'Filament', (np.log10(45), np.log10(0.38)), color='white')
        # plt.annotate(r'(coupled)', (np.log10(45), np.log10(0.28)), color='white')
        # plt.annotate(r'Eddy', (np.log10(2000), np.log10(0.03)), color='white')

        # ax.plot(np.log10(0.03), np.log10(0.2),  'o', color='white')#, xytext=(np.log10(0.03), np.log10(0.12)), arrowprops=dict(facecolor='black', shrink=0.02))
        # ax.plot(np.log10(30),   np.log10(1),    'o', color='white')#, xytext=(np.log10(40), np.log10(0.8)), arrowprops=dict(facecolor='black', shrink=0.02))
        # ax.plot(np.log10(3),    np.log10(0.2),  'o', color='white')#, xytext=(np.log10(2), np.log10(0.2)), arrowprops=dict(facecolor='black', shrink=0.02))
        # ax.plot(np.log10(5000), np.log10(0.2),  'o', color='white')#, xytext=(np.log10(5000), np.log10(0.1)), arrowprops=dict(facecolor='black', shrink=0.02))

        # ax.annotate('(a)', xy=(np.log10(0.03), np.log10(0.2)), xycoords='data', ha='right', va='bottom', fontsize=20, color='white')
        # ax.annotate('(b)', xy=(np.log10(3), np.log10(0.2)), xycoords='data', ha='right', va='bottom', fontsize=20, color='white')
        # ax.annotate('(c)', xy=(np.log10(30), np.log10(1)), xycoords='data', ha='right', va='bottom', fontsize=20, color='white')
        # ax.annotate('(d)', xy=(np.log10(5000), np.log10(0.2)), xycoords='data', ha='right', va='bottom', fontsize=20, color='white')

        # Define custom tick labels for x-axis
        x_min_log = int(np.log10(min([eval('sd.' + lm.x_val) for sd in self.simulation_collection])))
        x_max_log = int(np.log10(max([eval('sd.' + lm.x_val) for sd in self.simulation_collection])))
        x = np.arange(x_min_log, x_max_log + 1)
        # Create a list of minor ticks
        minor_x_labels = []
        # 1) Add the ticks from x_min_log to ceil(x_min_log) to the minor_x_test list
        new_ticks = np.linspace(10.0 ** np.floor(x_min_log), 10.0 ** np.ceil(x_min_log), 10)[:-1]
        new_ticks = np.unique(new_ticks[new_ticks >= 10.0 ** x_min_log])
        minor_x_labels.extend(new_ticks)
        # 2) Add the ticks from ceil(x_min_log) to floor(x_max_log) to the minor_x_test list
        for x_val in x:
            new_ticks = np.linspace(10.0 ** x_val, 10.0 ** (x_val + 1), 10)[1:-1]
            if x_val == x[-1]:
                new_ticks = new_ticks[new_ticks <= 10.0 ** x_max_log]
            minor_x_labels.extend(new_ticks)
        minor_x = [np.log10(val) for val in minor_x_labels]

        new_x_labels = [f"$10^{{{val}}}$" for val in x]
        plt.xticks(x, new_x_labels)
        plt.xticks(minor_x, minor=True)

        # Define custom tick labels for y-axis
        y_min_log = np.log10(min([eval('sd.' + lm.y_val) for sd in self.simulation_collection]))
        y_max_log = np.log10(max([eval('sd.' + lm.y_val) for sd in self.simulation_collection]))
        y = np.arange(np.ceil(y_min_log), np.floor(y_max_log) + 1)
        # Create a list of minor ticks
        minor_y_labels = []
        # 1) Add the ticks from y_min_log to ceil(y_min_log) to the minor_y_test list
        new_ticks = np.linspace(10.0 ** np.floor(y_min_log), 10.0 ** np.ceil(y_min_log), 10)[:-1]
        new_ticks = np.unique(new_ticks[new_ticks >= 10.0 ** y_min_log])
        minor_y_labels.extend(new_ticks)
        # 2) Add the ticks from ceil(y_min_log) to floor(y_max_log) to the minor_y_test list
        for y_val in y:
            new_ticks = np.linspace(10.0 ** y_val, 10.0 ** (y_val + 1), 10)[1:-1]
            if y_val == y[-1]:
                new_ticks = new_ticks[new_ticks <= 10.0 ** y_max_log]
            minor_y_labels.extend(new_ticks)

        new_y_labels = [f"$10^{{{int(val)}}}$" for val in y]
        minor_y = [np.log10(val) for val in minor_y_labels]
        plt.yticks(y, new_y_labels)
        plt.yticks(minor_y, minor=True)

        # plt.savefig('C:/Users/jdular/cernbox/Documents/Reports/CERN_Reports/linkedFluxPaper/fig/loss_map_54fil_noI.pdf', bbox_inches='tight')

        if lm.save_plot:
            filePath = self.create_non_overwriting_filepath(self.outputs_folder_path, lm.filename, '.pdf', self.fdm.run.overwrite)
            plt.savefig(filePath, bbox_inches='tight')

        if self.fdm.run.launch_gui: plt.show()

    def create_errorMap(self, flux_model, display=True, iteration=None):
        """ This function creates a error map for a given rohf model on the space spanned by the simulations (f, I_amp) """

        error_type = self.fdm.magnet.postproc.batch_postproc.rohf_on_grid.error_type

        N = len(self.simulation_collection)
        frequencies = np.zeros(N)
        peakCurrents = np.zeros(N)
        pc_error = np.zeros(N)
        dyn_error = np.zeros(N)
        flux_error = np.zeros(N)
        for idx, simulation in enumerate(self.simulation_collection):
            frequencies[idx] = simulation.f
            peakCurrents[idx] = simulation.I_amp
            # compute rohf metrics
            rohf_flux, rohf_dyn_loss, _, rohf_pc_loss, _ = flux_model.compute(simulation.time, simulation.I_transport, sim=simulation)
            # (relative) per cycle loss error
            pc_error[idx] = abs(rohf_pc_loss - simulation.total_power_per_cycle['FilamentLoss']) / simulation.total_power_per_cycle['FilamentLoss']
            # (relative) mean dynamic error
            dyn_error[idx] = np.mean(abs((rohf_dyn_loss - simulation.power['FilamentLoss']) / simulation.power['FilamentLoss']))
            # (relative) mean flux error
            non_zero_idx = np.nonzero(simulation.flux_internal)
            flux_error[idx] = np.mean(abs((rohf_flux[non_zero_idx] - simulation.flux_internal[non_zero_idx]) / simulation.flux_internal[non_zero_idx]))

        if error_type == 'pc_loss':
            error = pc_error
        elif error_type == 'flux':
            error = flux_error
        elif error_type == 'dyn_loss':
            error = dyn_error
        else:
            raise ValueError('Unrecognized error type')

        # plot errorMap result
        if display:

            show_descriptions = False
            freq_i, curr_i = np.linspace(min(frequencies), max(frequencies), 1000), np.linspace(min(peakCurrents), max(peakCurrents), 1000)
            freq_i, curr_i = np.meshgrid(freq_i, curr_i)
            plt.figure()
            ax = plt.gca()
            title = str(error_type) + " map"
            if show_descriptions:
                ax.set_title(title)
                ax.set_xlabel(r'Frequency $f$ ($\mathrm{Hz}$)')
                ax.set_ylabel(r"Transport current ratio $I/I_\mathrm{c}$")
            else:
                ax.set_axis_off()

            if self.fdm.magnet.postproc.batch_postproc.rohf_on_grid.interpolate_error_map:
                rbf = interpolate.Rbf(frequencies, peakCurrents, error, function='linear')
                error_i = rbf(freq_i, curr_i)
                plt.imshow(error_i, vmin=error.min(), vmax=error.max(), origin='lower', aspect='auto',
                           extent=[min(frequencies), max(frequencies), min(peakCurrents) / max(peakCurrents), 1])
            plt.scatter(frequencies, peakCurrents / max(peakCurrents), c=error, edgecolor='w')
            ax.set_xscale('log')
            # ax.set_yscale('log')
            plt.colorbar()
            plt.show()
        else:
            # cumulative error over map
            return sum(error)

    def plot2d(self):
        """
        This function is used to create a 2d plot. It is supposed to be flexible and work for various kinds of plots one may want to create.
        """

        def apply_plot_settings():
            if ref:
                plt.plot(ref_array[0], ref_array[1], linestyle='--', label=self.fdm.magnet.postproc.batch_postproc.plot2d.reference_label)
            if self.fdm.magnet.postproc.batch_postproc.plot2d.legend:
                plt.legend()
            plt.grid(linestyle='dotted')
            plt.xlabel(self.fdm.magnet.postproc.batch_postproc.plot2d.xlabel)
            plt.ylabel(self.fdm.magnet.postproc.batch_postproc.plot2d.ylabel)
            plt.title(title)
            if self.fdm.magnet.postproc.batch_postproc.plot2d.x_log:
                plt.xscale('log')
            if self.fdm.magnet.postproc.batch_postproc.plot2d.y_log:
                plt.yscale('log')

        if self.tex_installation:
            plt.rcParams['text.usetex'] = True
            plt.rcParams['font.family'] = 'times'
            # plt.rcParams['font.size'] = 20

        plotdata_list = []
        # use labelcount to subdevide simulations into sets of equal length
        labellen = int(len(self.fdm.magnet.postproc.batch_postproc.plot2d.labels))
        grplen = int(len(self.simulation_collection) / labellen)

        # Create the title (or titles if combined_plot is False)
        title = self.fdm.magnet.postproc.batch_postproc.plot2d.title
        if self.fdm.magnet.postproc.batch_postproc.plot2d.combined_plot:
            sd = self.simulation_collection[0]
            commands = re.findall('<<(.*?)>>', title)
            for c in commands:
                title = title.replace(f"<<{c}>>", str(eval('sd.' + c)))
        else:
            titles = []
            for sd in self.simulation_collection:
                commands = re.findall('<<(.*?)>>', title)
                title_i = title
                for c in commands:
                    title_i = title_i.replace(f"<<{c}>>", str(eval('sd.' + c)))
                titles.append(title_i)

        # colors = plt.cm.get_cmap('magma').resampled(len(self.simulation_collection)).colors
        max_len = max([len(self.simulation_collection), len(self.fluxmodel_collection)]) if self.fluxmodel_collection else len(self.simulation_collection)
        colors = plt.cm.get_cmap('viridis').resampled(max_len).colors

        # convert selected simulation parameters into list of PlotData
        simulation_idx = []  # nested list with indices
        fluxmodel_idx = []
        style_cycle = ['--', ':', '-.']
        for i, simulation in enumerate(self.simulation_collection):
            # get x_data
            x_data = eval(self.fdm.magnet.postproc.batch_postproc.plot2d.x_val)
            # base label
            if len(self.fdm.magnet.postproc.batch_postproc.plot2d.labels) == len(self.simulation_collection):
                label_idx = i
            else:
                label_idx = 0
            label_cmd = re.findall('<<(.*?)>>', self.fdm.magnet.postproc.batch_postproc.plot2d.labels[label_idx])
            sim_label = self.fdm.magnet.postproc.batch_postproc.plot2d.labels[label_idx].replace(f"<<{label_cmd}>>", str(eval('simulation.' + label_cmd))) if label_cmd else self.fdm.magnet.postproc.batch_postproc.plot2d.labels[label_idx]
            # add (multiple) y_data sets w. label
            for j in range(len(self.fdm.magnet.postproc.batch_postproc.plot2d.y_vals)):
                y_data = eval(self.fdm.magnet.postproc.batch_postproc.plot2d.y_vals[j])

                sublabel = sim_label if len(self.fdm.magnet.postproc.batch_postproc.plot2d.y_vals) == 1 else sim_label + ' (' + str(i) + ')'
                plotdata_list.append(PlotData(x_data=x_data, y_data=y_data, label=sublabel, color=colors[i], linestyle='-'))
                simulation_idx.append(len(plotdata_list) - 1)
            # add multiple fluxmodel results
            if self.fluxmodel_collection:
                for k, fluxmodel in enumerate(self.fluxmodel_collection):
                    y_data = eval(self.fdm.magnet.postproc.batch_postproc.plot2d.y_val_fluxmodel)
                    plotdata_list.append(PlotData(x_data=x_data, y_data=y_data, label=fluxmodel.label + '_' + str(sim_label), color=colors[i], linestyle=style_cycle[k % len(style_cycle)]))
                    fluxmodel_idx.append(len(plotdata_list) - 1)

                    # Load reference - if defined
        ref = self.fdm.magnet.postproc.batch_postproc.plot2d.reference_vals
        ref_array = []
        if ref:
            for i, ref_val in enumerate(ref):
                commands = re.findall('<<(.*?)>>', ref_val)
                for c in commands:
                    ref_val = ref_val.replace(f"<<{c}>>", str('sd.' + c))
                ref_array.append(eval(ref_val))

        # Create result folder:
        if not self.fdm.magnet.postproc.batch_postproc.plot2d.combined_plot and self.fdm.magnet.postproc.batch_postproc.plot2d.save_plot:
            # Create a folder to save the plots if combined_plot is False and save_plot is True:
            filename = self.fdm.magnet.postproc.batch_postproc.plot2d.filename
            folder_path = self.create_non_overwriting_filepath(self.outputs_folder_path, filename, '', self.fdm.run.overwrite)
            if not os.path.exists(folder_path): os.makedirs(folder_path)

        # plot data as continous graphs in one plot if there are no scalars
        scalar_plotdata = any([hasattr(plotdata.x_data, "__len__") for plotdata in plotdata_list])
        if not scalar_plotdata:
            for grp_idx, grp_plotdata in enumerate([plotdata_list[i::labellen] for i in range(labellen)]):
                plt.plot([data.x_data for data in grp_plotdata], [data.y_data for data in grp_plotdata], self.fdm.magnet.postproc.batch_postproc.plot2d.linestyle, label=self.fdm.magnet.postproc.batch_postproc.plot2d.labels[grp_idx], color=colors[-grp_idx])
                if not self.fdm.magnet.postproc.batch_postproc.plot2d.combined_plot:
                    plt.figure()
            if self.fluxmodel_collection:
                for grp_idx, group in enumerate([fluxmodel_idx[i:i + grplen] for i in range(0, len(fluxmodel_idx), grplen)]):
                    plt.plot([plotdata_list[idx].x_data for idx in group], [plotdata_list[idx].y_data for idx in group], '-o', label="ROHF", color='red')
            apply_plot_settings()
        # plot data as points in one graph each in one plot
        else:
            print('test')
            for idx, plotdata in enumerate(plotdata_list):
                plt.plot(plotdata.x_data, plotdata.y_data, linestyle=plotdata.linestyle, label=plotdata.label, color=plotdata.color)
                apply_plot_settings()
        if self.fdm.magnet.postproc.batch_postproc.plot2d.save_plot:
            filename = self.fdm.magnet.postproc.batch_postproc.plot2d.filename
            filePath = self.create_non_overwriting_filepath(self.outputs_folder_path, filename, '.png', self.fdm.run.overwrite)
            plt.savefig(filePath, dpi=300)

        if self.fdm.magnet.postproc.batch_postproc.plot2d.combined_plot and self.fdm.magnet.postproc.batch_postproc.plot2d.save_pgfdata:
            if not scalar_plotdata:
                data_tuple = ()
                data_names = []
                for grp_idx, grp_plotdata in enumerate([plotdata_list[i::labellen] for i in range(labellen)]):
                    data_tuple = data_tuple + ([data.x_data for data in grp_plotdata], [data.y_data for data in grp_plotdata])
                    data_names.extend([self.fdm.magnet.postproc.batch_postproc.plot2d.labels[grp_idx] + str("_x"), self.fdm.magnet.postproc.batch_postproc.plot2d.labels[grp_idx] + str("_y")])
                data = np.vstack(data_tuple).T
                header = " ".join(data_names)
            else:
                max_len = max([len(plotdata.x_data) for plotdata in plotdata_list])
                # pad shorter data columns with nan - is ignored by pgfplots
                data = np.vstack(tuple([np.pad(plotdata.x_data, (0, max_len - len(plotdata.x_data)), "constant", constant_values=(np.nan,)) for plotdata in plotdata_list]
                                       + [np.pad(plotdata.y_data, (0, max_len - len(plotdata.y_data)), "constant", constant_values=(np.nan,)) for plotdata in plotdata_list])).T
                header = " ".join([plotdata.label + '_x' for plotdata in plotdata_list]) + " " + " ".join([plotdata.label + '_y' for plotdata in plotdata_list])
            np.savetxt(os.path.join(self.outputs_folder_path, 'pgfdata.txt'), data, header=header, comments="")

        if self.fdm.run.launch_gui: plt.show()
