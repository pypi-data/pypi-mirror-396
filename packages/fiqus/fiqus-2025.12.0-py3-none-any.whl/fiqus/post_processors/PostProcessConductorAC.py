import os, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import steammaterials  # TESTING PURPOSES

    steammaterials_flag = False
except:
    steammaterials_flag = True

from scipy import constants, optimize, integrate, signal, interpolate
from fiqus.data.DataFiQuSConductorAC_Strand import CACStrandGeometry, CACStrandMesh, CACStrandSolve
from fiqus.plotters.PlotPythonConductorAC import BatchPlotPythonConductorAC, PlotPythonConductorAC, PDFreport
from fiqus.utils.Utils import FilesAndFolders
import ruamel.yaml


class SimulationData:
    """
    Class used to store and manage data from a single simulation.

    This class is responsible for loading and organizing the data from a single simulation.
    It stores the data in various attributes and provides methods for retrieving and processing the data.

    """

    def __init__(self, model_data_output_path, geometry_name, mesh_name, solution_name, fdm) -> None:
        self.model_data_output_path = model_data_output_path  # This is the path to the folder where the model output data is stored (e.g. geometries)
        self.geometry_name = geometry_name  # Name of the geometry folder
        self.mesh_name = mesh_name  # Name of the mesh folder
        self.solution_name = solution_name  # Name of the solution folder
        self.conductor_name = fdm.magnet.solve.conductor_name

        # Organize the folders:
        self.geometry_folder = os.path.join(self.model_data_output_path, geometry_name)  # Path to the geometry folder
        self.mesh_folder = os.path.join(self.geometry_folder, mesh_name)  # Path to the mesh folder
        self.solution_folder = os.path.join(self.mesh_folder, solution_name)  # Path to the solution folder

        # hacky solution for now ... pass conductor data through fdm because its not stored in geom yaml
        self.conductor = fdm.conductors[self.conductor_name]
        # Store the YAML input-files in a data model, fdm:
        self.geometry, self.mesh, self.solve = self.retrieve_fiqusDataModel()
        # Store losses, simulation time and check if the simulation crashed:
        temp_file_path = os.path.join(self.solution_folder, 'text_output')
        loss_file = [f for f in os.listdir(temp_file_path) if f.startswith('power') and f.endswith('.txt')][0]
        self.power_columns = ['Time', 'FilamentLoss', 'CouplingLoss', 'EddyLoss', 'TotalLoss', 'CouplingLoss_dyn', 'TotalLoss_dyn']  # Only in the case dynamic correction is used, must be changed later
        self.power = pd.read_csv(os.path.join(self.solution_folder, 'text_output', loss_file), sep=' ', names=self.power_columns)  # Store instantaneous losses as pandas dataframe
        # Add a row of zeros at the beginning of the dataframe to account for the initial condition:
        self.power = pd.concat([pd.DataFrame({col: 0 for col in self.power_columns}, index=[0]), self.power]).reset_index(drop=True)
        if self.solve.formulation_parameters.formulation == "CATI" and self.solve.diffusion_barriers:  # Check if dm.solve has the entry for diffusion barriers
            if self.solve.diffusion_barriers.enable:  # Check if diffusion barriers are enabled
                # Load and add the power dissipated in the diffusion barriers (if they are enabled):
                self.power_diffusion_barriers = np.loadtxt(os.path.join(temp_file_path, 'power_diffusion_barrier.txt'), skiprows=1)
                self.power_diffusion_barriers = np.sum(self.power_diffusion_barriers[:, 1:], axis=1)
                self.power['CouplingLoss'] += self.power_diffusion_barriers
                self.power['CouplingLoss_dyn'] += self.power_diffusion_barriers
                self.power['TotalLoss'] += self.power_diffusion_barriers
                self.power['TotalLoss_dyn'] += self.power_diffusion_barriers
        self.crash = True if 'crash_report.txt' in os.listdir(temp_file_path) else False
        # Store simulation time:
        try:
            with open(os.path.join(self.solution_folder, 'text_output', 'simulation_time.txt'), 'r') as f:
                self.simulation_time = float(f.readline().strip())
        except:
            self.simulation_time = None  # If the simulation time file does not exist, the simulation has not finished running.

        # Store the rest of the post-processing data:
        self.time = self.power['Time']
        self.instantaneous_temperature = self.load_standard_data(os.path.join(temp_file_path, 'temperature.txt'), 1, add_initial_zero=True)
        self.temperature = self.load_standard_data(os.path.join(temp_file_path, 'temperature.txt'), 2, add_initial_zero=True)
        self.I_transport = self.load_standard_data(os.path.join(temp_file_path, 'I_transport.txt'), 1)
        self.V_transport = self.load_standard_data(os.path.join(temp_file_path, 'V_transport.txt'), 1)
        self.V_transport_unitlen = self.load_standard_data(os.path.join(temp_file_path, 'V_transport_unitlen.txt'), 1)
        self.hs_val = self.load_standard_data(os.path.join(temp_file_path, 'hs_val.txt'), 1)
        self.magn_fil = self.load_standard_data(os.path.join(temp_file_path, 'magn_fil.txt'), [1, 2, 3])
        self.magn_matrix = self.load_standard_data(os.path.join(temp_file_path, 'magn_matrix.txt'), [1, 2, 3])
        self.I = self.load_standard_data(os.path.join(temp_file_path, 'I.txt'), 1, len(self.time))
        self.V = self.load_standard_data(os.path.join(temp_file_path, 'V.txt'), 1, len(self.time))
        self.I_integral = self.load_standard_data(os.path.join(temp_file_path, 'I_integral.txt'), 1, len(self.time))
        self.I_abs_integral = self.load_standard_data(os.path.join(temp_file_path, 'I_abs_integral.txt'), 1, len(self.time))
        self.magnetic_energy_internal = self.load_standard_data(os.path.join(temp_file_path, 'magnetic_energy_internal.txt'), 1)
        self.magnetic_energy_external = self.load_standard_data(os.path.join(temp_file_path, 'magnetic_energy_external.txt'), 1)
        self.flux_external = self.load_standard_data(os.path.join(temp_file_path, 'flux_external.txt'), 1)
        self.flux_internal = self.load_standard_data(os.path.join(temp_file_path, 'flux_internal.txt'), 1)
        self.selffield_dfluxdt = self.load_standard_data(os.path.join(temp_file_path, 'selffield_dfluxdt.txt'), 1)
        self.Ip = self.load_standard_data(os.path.join(temp_file_path, 'Ip.txt'), 1, len(self.time))
        self.Vp = self.load_standard_data(os.path.join(temp_file_path, 'Vp.txt'), 1, len(self.time))
        # try to init - otherwise NONE
        self.f, self.B_background, self.I_amp, self.T_background = self.get_source_params(verbose=True)
        # self.data_impedance = self.compute_data_impedance(verbose=False)
        # self.analytic_RL = self.compute_analytic_RL()
        # Integrate the losses to obtain the cumulative power and the total power per cycle:
        self.cumulative_power, self.total_power_per_cycle = self.integrate_power()  # Store cumulative power and total cumulative power per cycle

    def export2txt(self, data_names, data_columns, filename):
        """ This function can be used to export one or more arrays of simulation data in one txt file (stored in solution folder)."""
        np_data = np.array(data_columns).T
        np.savetxt(os.path.join(self.solution_folder, str(filename) + '.txt'), np_data, header=" ".join(data_names), comments="")

    def rad_to_deg(self, radiants):
        return radiants / np.pi * 180

    def get_source_params(self, verbose=False):
        source = self.solve.source_parameters.source_type
        T = self.solve.general_parameters.temperature
        if source == "rotating":
            f = self.solve.source_parameters.rotating.frequency
            B = self.solve.source_parameters.rotating.field_magnitude
            I = 0
        elif source == "sine":
            f = self.solve.source_parameters.sine.frequency
            I = self.solve.source_parameters.sine.current_amplitude
            # background field amplitude
            B = self.solve.source_parameters.sine.superimposed_DC.field_magnitude
            if verbose: print("Loading Simulation: f=" + "{:.2f}".format(f) + " [Hz];  B_back=" + "{:.2f}".format(B) + " [T];  I=" + "{:.2f}".format(I) + " [A]")
        else:
            f = None
            B = 0
            I = max(abs(self.I_transport))

        return f, B, I, T

    def first_rise(self, current=False):
        """ returns the time, current and flux on the first penetration interval until the first current peak/saddle is reached """
        first_extrema_idx = signal.argrelextrema(self.I_transport if current else self.flux_internal, np.greater_equal)[0][0]  # first rel extrema
        return self.time[0:first_extrema_idx], self.I_transport[0:first_extrema_idx], self.flux_internal[0:first_extrema_idx]

    def halfcycle(self, current=False):
        """ returns the time, current and flux on the first halfcycle of transport current or flux """
        data = self.I_transport if current else self.flux_internal
        zero_crossings = np.where(np.diff(np.sign(data[1:])))[0] + 1
        return self.time[0:zero_crossings[0]], self.I_transport[0:zero_crossings[0]], self.flux_internal[0:zero_crossings[0]]

    def load_standard_data(self, file_path, columns, reshape=None, add_initial_zero=False):
        """
        There are many output .txt-files with similar format. This function loads the data from one of these files and returns it as a numpy array.
        If the file does not exist, None is returned without raising an error.
        """
        try:
            data = np.loadtxt(file_path, comments='#', usecols=columns)
            if reshape:
                data = data.reshape(-1, reshape).T
        except IOError:
            return None

        if add_initial_zero:
            if len(data.shape) == 1:
                data = np.insert(data, 0, 0)
            else:
                zeros = np.zeros((1, data.shape[1]))
                data = np.vstack((zeros, data))
        return data

    def retrieve_fiqusDataModel(self):
        """
        This function reads the YAML input-files for geometry, mesh and solve and stores them in three dictionaries which are returned.
        This function is to be called only once, when the object is created.
        """
        geometry_dataModel = FilesAndFolders.read_data_from_yaml(os.path.join(self.geometry_folder, 'geometry.yaml'), CACStrandGeometry)
        mesh_dataModel = FilesAndFolders.read_data_from_yaml(os.path.join(self.mesh_folder, 'mesh.yaml'), CACStrandMesh)
        # Now that the solve.yaml file contains more than just the solve part, we query only that part here.
        # solution_dataModel = FilesAndFolders.read_data_from_yaml(os.path.join(self.solution_folder, 'solve.yaml'), CACStrandSolve)
        with open(os.path.join(self.solution_folder, 'solve.yaml'), 'r') as stream:
            yaml = ruamel.yaml.YAML(typ='safe', pure=True)
            yaml_str = yaml.load(stream)
            solution_dataModel = CACStrandSolve(**yaml_str['solve'])
        return geometry_dataModel, mesh_dataModel, solution_dataModel

    def integrate_power(self):
        """
        This function integrates the instantaneous power over time to obtain the cumulative power.
        It also calculates the total cumulative power per cycle.
        The cumulative power is returned as a pandas dataframe and the total cumulative power per cycle is returned as a dictionary.
        """
        find_closest_idx = lambda arr, val: np.abs(arr - val).argmin()

        t = np.array(self.power['Time'])
        t_final = t[-1]
        if self.f:
            t_init = find_closest_idx(t, t_final - 1 / (self.f))
        else:
            t_init = find_closest_idx(t, t_final)

        cumulative_power = pd.DataFrame(columns=self.power_columns)
        total_power_per_cycle = {}

        cumulative_power['Time'] = self.power["Time"]
        for column in self.power_columns[1:]:
            cumulative_power[column] = np.insert(integrate.cumulative_trapezoid(self.power[column], t), 0, 0)
            total_power_per_cycle[column] = (cumulative_power[column].iloc[-1] - cumulative_power[column].iloc[t_init])  # / (np.pi*matrix_radius**2 * loss_factor) # Why do we divide by pi*matrix_radius**2*loss_factor?

        return cumulative_power, total_power_per_cycle

    def compute_data_impedance(self, verbose=False):
        """
        This function estimates a complex impedance per unit length for the OOP based on sinus fits for the transport voltage and current.
        If no sinus fit is possible it returns NONE as impedance estimate.
        """
        if not self.f:
            return None

        I_mean = np.mean(self.I_transport)
        V_mean = np.mean(self.V_transport_unitlen)
        I_peak = max(abs(self.I_transport))
        V_peak = max(abs(self.V_transport_unitlen))
        # ignore values before this index - tweaking parameter depending on source ramping
        N_h = round(len(self.I_transport) / 4)
        # sine fit for current and voltage
        optimize_func_current = lambda x: x[0] * np.sin(x[1] * self.time[N_h:] + x[2]) + x[3] - self.I_transport[N_h:]
        optimize_func_voltage = lambda x: x[0] * np.sin(x[1] * self.time[N_h:] + x[2]) + x[3] - self.V_transport_unitlen[N_h:]
        current_estimate = optimize.leastsq(optimize_func_current, [I_peak - I_mean, self.f, 0, I_mean])[0]  # est_amp, est_freq, est_phase, est_mean
        voltage_estimate = optimize.leastsq(optimize_func_voltage, [V_peak - V_mean, self.f, 0, V_mean])[0]
        delta_phi = abs(voltage_estimate[2] - current_estimate[2]) % (2 * np.pi)
        Z_magnitude = V_peak / I_peak  # both sinus - no formfactor
        L_inductance = abs(np.sin(delta_phi) * Z_magnitude) / (2 * np.pi * self.f)
        R_resistance = abs(np.cos(delta_phi) * Z_magnitude)
        Z_impedance = R_resistance + 2 * np.pi * self.f * L_inductance * 1j
        if verbose:
            print("estimated simulation Impedance: " + str(Z_magnitude) + " Ohm")
            print(" -> L: " + str(L_inductance) + " Henry")
            print(" -> R: " + str(R_resistance) + " Ohm")
            print(" -> Phase: " + str(np.angle(Z_impedance, deg=True)) + " Deg")
        return Z_impedance

    def compute_analytic_RL(self):
        """ This function calculates the analytic impedance parameters R & L per unit length based on reduced telegraphers equations with C, G = 0 """

        rho_CU = 1.81e-10
        coil_radius = self.geometry.coil_radius
        air_radius = self.geometry.air_radius
        strand_radius = self.conductor.strand.diameter / 2
        filament_radius = self.conductor.strand.filament_diameter / 2

        correction_factor = 0.9549  # CATI (needs to be corrected)
        ell = correction_factor * self.conductor.strand.fil_twist_pitch / 6  # CATI

        if self.geometry.type == 'strand_only':
            # single filament in open space
            inductance_L = constants.mu_0 / (2 * np.pi) * np.log(air_radius / filament_radius)  # == coax cable
            resistance_R = rho_CU / (np.pi * (self.conductor.strand.diameter / 2) ** 2) * ell if self.solve.general_parameters.superconductor_linear else 1e-12
        elif self.geometry.type == 'coil':
            # single coil winding closed in infinity
            inductance_L = constants.mu_0 / np.pi * np.log((coil_radius * 2 - strand_radius) / strand_radius)  # + ell * constants.mu_0 / (4 * np.pi)
            resistance_R = 2 * rho_CU / (np.pi * (self.conductor.strand.diameter / 2) ** 2) * ell if self.solve.general_parameters.superconductor_linear else 1e-12
        else:
            return None

        return [resistance_R, inductance_L]


class ROHFmodel:
    """ Base class for a Reduced Order Hysteretic Flux model. Defining a chain of rate dependent cells for flux and loss reconstruction in a homogenized strand model."""

    def __init__(self, N=None, taus=None, kappas_bar=None, alphas=None, simulation=None, filepath=None, filename=None, spacing_type=None, label=''):
        # direct parameter initialization
        self.N = N
        self.kappas_bar = kappas_bar
        self.alphas = alphas
        self.taus = taus
        # Ambient sueprcon parameters
        self.Ic_0 = 2978  # [A]
        self.T_0 = 1.9  # [K]
        self.Ec_0 = 1e-4  # [V/m]
        self.n = 60
        # internal variables
        self.L0 = constants.mu_0 / (4 * np.pi)  # lin. self inductance of cylindric wire
        # optional info for batch plots
        self.label = label
        self.simulation = simulation
        # initialization shortcuts
        if filepath and filename:
            self.import_params(filepath=filepath, filename=filename)  # initialize from file
        elif simulation:  # fit params on the fly
            self.fit_data(simulation=simulation, spacing_type=spacing_type, taus=taus, kappas_bar=kappas_bar, alphas=alphas)

    def update(self, N, taus, kappas_bar, alphas):
        self.N = N
        self.taus = taus
        self.kappas_bar = kappas_bar
        self.alphas = alphas

    def params(self):
        return np.array([self.alphas, self.kappas_bar, self.taus]).T

    def export_params(self, filepath, filename, txt_format=False):
        """Exports the reduced order parameters kappa and alpha as txt file.

        :param filepath: absolute path to storage location
        :param filename: name of the file (without .txt ending)
        """
        if txt_format:
            header = "# fitted on " + self.simulation.solution_name + "\nalphas kappas taus" if self.simulation else "# imported params \nalphas kappas taus"
            np.savetxt(os.path.join(filepath, str(filename) + '.txt'), self.params(), header=header, comments="")
        else:
            df = pd.DataFrame(self.params())
            df.to_csv(os.path.join(filepath, str(filename) + '.csv'), header=['alphas', 'kappas', 'taus'], index=None, float_format='{:e}'.format)

    def import_params(self, filepath, filename, txt_format=False):
        """This function reads the reduced order parameters kappa and alphas from a txt file.

        :param filepath: absolute path to storage location
        :param filename: name of the file (without .txt ending)
        """
        if txt_format:
            data = np.loadtxt(os.path.join(filepath, filename + ".txt"), delimiter=" ", skiprows=2).T  # alphas, kappas, taus
        else:
            data = np.array(pd.read_csv(os.path.join(filepath, filename + ".csv"), sep=',', header=1).values).T
            print(data)
        self.simulation = None
        self.name = filename
        self.update(N=len(data[0]), alphas=data[0], kappas_bar=data[1], taus=data[2])

    def ohmic_loss(self, I, simulation=None):
        """ This function calculates the ohmic loss in filaments and matrix of a homogenized conductor.

        :param I: transport current
        :param simulation: simulation data for conductor information, defaults to None
        :return: array of [p_ohm_fil, p_ohm_mat, R_fil, R_mat] for all current steps
        """

        if steammaterials_flag or simulation is None:
            # print("Assuming zero ohmic loss")
            return np.zeros(len(I)), np.zeros(len(I))

            # geometry parameters
        surf_strand = np.pi * (simulation.conductor.strand.diameter / 2) ** 2
        surf_filaments = simulation.conductor.strand.number_of_filaments * np.pi * (simulation.conductor.strand.filament_diameter / 2) ** 2
        surf_matrix = surf_strand - surf_filaments
        # matrix resistivity
        matpath = os.path.join(os.path.dirname(steammaterials.__file__), 'CFUN')
        Tspace = np.vstack((self.T_0, 0, simulation.conductor.strand.RRR))  # T, B, RRR
        cu_space = steammaterials.SteamMaterials("CFUN_rhoCu_NIST_v2", Tspace.shape[0], Tspace.shape[1], matpath)
        rho_matrix = cu_space.evaluate(Tspace)
        R_matrix = rho_matrix / surf_matrix

        # current sharing between matrix (R const) and filaments (power law) https://ieeexplore.ieee.org/document/8970335
        grid = np.vstack((I / (surf_strand), self.Ec_0 * np.ones(len(I)), self.Ic_0 / (surf_filaments) * np.ones(len(I)), self.n * np.ones(len(I)), rho_matrix * np.ones(len(I)), surf_filaments * np.ones(len(I)), surf_matrix * np.ones(len(I))))
        sharing_space = steammaterials.SteamMaterials("CFUN_HTS_CurrentSharing_homogenized_v1", grid.shape[0], grid.shape[1], matpath)
        lambdas = sharing_space.evaluate(grid)
        # current split associated ohmic losses
        I_filaments = lambdas * I
        I_matrix = (np.ones(len(lambdas)) - lambdas) * I
        p_ohm_filaments = self.Ec_0 * ((abs(I_filaments)) / (self.Ic_0)) ** (self.n) * abs(I_filaments)
        p_ohm_matrix = R_matrix * I_matrix ** 2

        return p_ohm_filaments, p_ohm_matrix

    def fit_scaling(self, simulation):
        """ This method fits the internal kappa_scaling parameter of the ROHFmodel to a given magnetic background field magnitude for NbTi filaments.

        :param B_background: magnitude of the magnetic background field in Tesla.
        """
        verbose = False
        # Scaling params
        B_background = simulation.B_background
        T_background = simulation.T_background
        if verbose: print("ROHF scaling: B=" + str(B_background) + " T=" + str(T_background))

        filament_d = simulation.conductor.strand.filament_diameter
        strand_surf = np.pi * (simulation.conductor.strand.diameter / 2) ** 2
        filament_surf = simulation.conductor.strand.number_of_filaments * np.pi * (filament_d / 2) ** 2
        fill_factor = filament_surf / strand_surf
        Jc_0 = self.Ic_0 / filament_surf

        if steammaterials_flag or B_background is None:
            raise ValueError('cant perform field scaling fit. Need steammaterials and background field amplitude.')
        matpath = os.path.join(os.path.dirname(steammaterials.__file__), 'CFUN')

        # Determine ambient field with no background and max current density
        B_space = np.linspace(0, 14, 5000)
        numpy2d_Bspace = np.vstack((self.T_0 * np.ones(B_space.shape), B_space, 1 * np.ones(B_space.shape)))  # T, B, A
        nbti_space = steammaterials.SteamMaterials("CFUN_IcNbTi_v1", numpy2d_Bspace.shape[0], numpy2d_Bspace.shape[1], matpath)
        jc_nbti_space = nbti_space.evaluate(numpy2d_Bspace)
        ambient_idx = np.abs(jc_nbti_space - Jc_0).argmin()
        B_ambient = B_space[ambient_idx]
        if verbose: print(" Ambient field: " + str(B_ambient) + " [T]")

        # determine absolute field value including a scaled down version of the strand ambient field
        B_abs = B_background + B_ambient
        # determine first scaling factor for the magnetic field
        jc_nbti1 = steammaterials.SteamMaterials("CFUN_IcNbTi_v1", 3, 1, matpath)
        jc_Babs = jc_nbti1.evaluate((T_background, B_abs, 1))
        scaling = jc_Babs / Jc_0
        # determine temperature scaling with finer ambient estimate
        if T_background != self.T_0:
            B_abs = float(B_background + scaling * B_ambient)
            jc_nbti2 = steammaterials.SteamMaterials("CFUN_IcNbTi_v1", 3, 1, matpath)
            jc_Babs = jc_nbti2.evaluate((T_background, B_abs, 1))
            scaling = jc_Babs / Jc_0
        if verbose: print(" Field scaling : " + str(scaling))
        return scaling, fill_factor

    def fit_kappas(self, simulation, spacing_type=None, verbose=False):
        """
        This method fits the coercivity parameters 'kappas_bar' according to a 'spacing_type' and given number of cells 'self.N'.
        The kappas are spread on the virgin rise from zero interval of a given strand simulation and can be seen as list of activation levels for the N cells.

        :param simulation: SimulationData object which the ROHF will get fitted to
        :param spacing_type: Enforce a specfic spacing of the kappas (i.e. 'linear'), defaults to None
        :param verbose: print additional information, defaults to False
        :raises ValueError: Unknown options for spacing_type
        :return: kappas_bar ndarray of N kappas
        """
        _, I_interval, flux_interval = simulation.first_rise()
        if spacing_type:
            if spacing_type == "exponential":
                [a, b], res1 = optimize.curve_fit(lambda x1, a, b: a * np.exp(b * x1), I_interval / max(I_interval), flux_interval / max(flux_interval))
                kappa_spacing = max(I_interval) * np.flip(np.exp(b) - np.exp(b * np.linspace(0, 1, num=self.N + 1))) / (np.exp(b) - 1)
            elif spacing_type == "linear":
                kappa_spacing = np.linspace(min(I_interval), max(I_interval), self.N + 1)
            elif spacing_type == "invlog":
                kappa_spacing = np.insert(max(I_interval) * (1.5 - np.geomspace(1, .5, num=self.N + 1)), 0, 0)
            elif spacing_type == "log":
                kappa_spacing = np.insert(np.geomspace(I_interval[1], max(I_interval), self.N), 0, 0)
            else:
                raise ValueError('Unknown kappa spacing for S_chain fit')
            # get closest matching indices in I_interval as kappas
            kappas = I_interval[self.__closest_matches(I_interval, kappa_spacing)]
        else:
            # calculate kappas based on minimization of linear interpolation error
            def max_abs_error(kappas, flux_spline, I_samples):
                # computes maximum absolute error between rohf and reference simulation on sample points
                rohf_flux = np.interp(I_samples, kappas, flux_spline(kappas))
                return max(abs(rohf_flux - flux_spline(I_samples)))

            # interpolate
            I_samples = np.linspace(0, max(I_interval), 500)
            flux_spline = interpolate.CubicSpline(I_interval, flux_interval, extrapolate=True)
            # minimize on interval
            cons = (optimize.LinearConstraint([np.concatenate(([1], np.zeros(self.N)))], lb=0, ub=0),
                    optimize.LinearConstraint([np.concatenate((np.zeros(self.N), [1]))], lb=max(I_interval), ub=max(I_interval)))
            bounds = ((0, max(I_interval)),) * (self.N + 1)
            kappas = optimize.differential_evolution(max_abs_error, args=(flux_spline, I_samples), x0=np.linspace(0, max(I_interval), self.N + 1),
                                                     disp=True, constraints=cons, bounds=bounds, tol=1e-8).x
            # kappas = np.insert(kappas, 1, 0.08*max(I_interval))
            if verbose:
                plt.figure()
                plt.title("kappa distribution")
                plt.plot(I_interval, flux_interval, '-b')
                plt.plot(kappas, flux_spline(kappas), 'gX')
                plt.show()

        return kappas[:-1]

    def fit_alphas(self, simulation, kappas_bar, dual=False, verbose=False):
        """Calculates the cell weights alpha for each kappa by cellwise recursion, fitting the simulation data given through I_interval and flux_interval.

        :param simulation: SimulationData object which the ROHF will get fitted to
        :param kappas_bar: coercivity currents on virgin I_interval which are used to define N multicell ROHF
        :param verbose: display all information, defaults to False
        :return: kappas_bar, alphas. List of updated kappas and their matching weights. Kappas only change in case of a dual fitting strategy (dual=True)
        """
        _, I_interval, flux_interval = simulation.first_rise(current=True)

        flux_spline = interpolate.CubicSpline(I_interval, flux_interval, extrapolate=True)
        kappas = np.concatenate((kappas_bar, [I_interval[-1]]))  # N + 1 kappas with interval boundary

        # classic coercivity-weight linkage (undershoot PCloss)
        alphas = np.zeros(len(kappas_bar))
        delta_flux = np.diff(flux_spline(kappas))
        delta_current = np.diff(kappas)
        for k in range(0, self.N):
            alphas[k] = 0 if delta_current[k] == 0 else abs(delta_flux[k] / (self.L0 * delta_current[k]) - sum(alphas))
        if verbose: print(" optimized alphas:    " + str(alphas))

        if False:
            # tangential coercivity-weight linkage (overshoot PCloss)
            dflux_dI_spline = flux_spline.derivative(nu=1)
            fluxes = flux_spline(kappas)
            m_slopes = dflux_dI_spline(kappas)
            alphas_tan = np.diff(m_slopes) / self.L0
            m_slopes[0] = 0
            b_offsets = np.zeros(self.N + 1)
            kappas_tan = np.zeros(self.N + 1)
            for k in range(1, self.N + 1):
                b_offsets[k] = fluxes[k] - m_slopes[k] * kappas[k]
                kappas_tan[k] = (b_offsets[k] - b_offsets[k - 1]) / (m_slopes[k - 1] - m_slopes[k])
            kappas_bar_tan = kappas_tan[1:]
            if True:
                plt.figure()
                plt.plot(I_interval, flux_interval, label='reference')
                plt.scatter(kappas_bar, fluxes[:-1], label='k-a-linkage kappas')
                plt.scatter(kappas_bar_tan, np.zeros(len(kappas_bar_tan)), label='new kappas', marker='x')
                for k in range(0, self.N + 1):
                    plt.plot(I_interval, b_offsets[k] + m_slopes[k] * I_interval)
                plt.ylim([0, max(flux_interval)])
                plt.legend()
                plt.plot()
                plt.show()

        return kappas_bar, 0.97 * alphas

    def fit_data(self, simulation, spacing_type=None, dual=False, taus=None, kappas_bar=None, alphas=None, verbose=False):
        """Fits the reduced order model params to a given simulation data by linear interpolation between kappas.

        :param current: transport current of the model
        :param flux: internal flux of the model
        :param spacing_type: kappa distribution type (lin, log, invlog, exponential), defaults to None
        :param verbose: display all information, defaults to False
        """
        if self.N is None:
            if kappas_bar is not None:
                self.N = len(kappas_bar)
            elif taus is not None:
                self.N = len(taus)
            elif alphas is not None:
                self.N = len(alphas)
            else:
                raise ValueError(f'Undefined number of cells. Cant fit to data.')

        # fit taus
        if taus is None:
            taus = [1.5e-5] + (self.N - 1) * [2e-4]
            # taus =  self.N*[0.0] if tau_sweep is None else self.fit_taus(tau_sweep=tau_sweep, verbose=verbose)

        # fit kappas
        if kappas_bar is None:
            kappas_bar = self.fit_kappas(simulation, spacing_type=spacing_type, verbose=verbose)

        # fit alphas
        if alphas is None:
            kappas_bar, alphas = self.fit_alphas(simulation, kappas_bar, verbose=verbose, dual=dual)

        # save fitted params
        self.simulation = simulation
        self.update(len(taus), taus, kappas_bar, alphas)

    def __closest_matches(self, dataset, values):
        return [min(range(len(dataset)), key=lambda i: abs(dataset[i] - value)) for value in values]

    def __flux_multicells(self, Irev):
        flux = 0
        for k in range(self.N):
            flux += self.alphas[k] * self.L0 * Irev[k]
        return flux

    def __g(self, I, Irev_prev, kappa):
        """ 1Dvector/scalar play model for g (=Irev+Ieddy) with coercivity kappas """
        diff = I - Irev_prev
        diff_unit = diff / abs(diff) if diff != 0 else 0
        if abs(diff) >= kappa or diff * (diff - kappa * diff_unit) > 0:
            return I - kappa * diff_unit
        else:
            return Irev_prev

    def compute(self, time, I, sim=None, v=0):
        """ Computing flux and losses on a given interval """
        if (self.N or self.alphas[0] or self.kappas_bar[0] or self.taus[0]) is None:
            raise ValueError(f'Undefined parameters. Cant compute solution.')

        # Background field scaling
        kappa_scaling, fill_factor = [1.0, 0.5] if sim is None else self.fit_scaling(sim)

        # INPUT PARAMETERS -----------------------------------------------
        nbSteps = len(I)
        rel_tol = 1e-5  # Iterations are needed because of the field-dependent parameters.
        iter_max = 100
        weightsum = np.cumsum(self.alphas)
        # RESOLUTION -----------------------------------------------------
        flux = np.zeros((nbSteps,))
        Irev = np.zeros((nbSteps, self.N))
        Iirr = np.zeros((nbSteps, self.N))
        Ieddy = np.zeros((nbSteps, self.N))
        g = np.zeros((nbSteps, self.N))
        iter_tot = 0
        # Computation of the associated flux density
        for i in range(1, nbSteps):
            # Vector hysteresis
            flux[i] = flux[i - 1]
            dt = time[i] - time[i - 1]
            conv_crit = 2
            iter = 0
            # scalar play model
            while conv_crit > 1 and iter < iter_max:
                for k in range(self.N):
                    # update g = Irev + Ieddy with "scalar" play model
                    diff = I[i] - Irev[i - 1, k]
                    diff_unit = diff / abs(diff) if diff != 0 else 0
                    # overcritical
                    if abs(I[i]) >= kappa_scaling * self.Ic_0:
                        Irev[i, k] = Irev[i - 1, k] + (1 - fill_factor) * (I[i] - I[i - 1]) / (2 * weightsum[k])
                        Ieddy[i, k] = Ieddy[i - 1, k] + self.taus[k] * (Irev[i - 1, k] - Irev[i, k]) / (dt)
                        Iirr[i, k] = I[i] - Irev[i, k] - Ieddy[i, k]
                    # undercritical
                    else:
                        if abs(diff) >= kappa_scaling * self.kappas_bar[k] or diff * (diff - kappa_scaling * self.kappas_bar[k] * diff_unit) > 0:
                            g[i, k] = I[i] - kappa_scaling * self.kappas_bar[k] * diff_unit
                        else:
                            g[i, k] = Irev[i - 1, k]
                            # g[i,k] = self.__g(I[i], Irev[i-1,k], self.kappas_bar[k])
                        # update irreversible
                        Iirr[i, k] = I[i] - g[i, k]
                        # update eddy
                        Ieddy[i, k] = self.taus[k] / (dt + self.taus[k]) * (g[i, k] - Irev[i - 1, k])
                        # calculate reversible
                        Irev[i, k] = g[i, k] - Ieddy[i, k]

                flux_new = self.__flux_multicells(Irev[i, :])
                conv_crit = abs((flux_new - flux[i]) / (flux[i] + 1e-10)) / rel_tol
                flux[i] = flux_new
                iter += 1
            iter_tot += iter
            if iter == iter_max:
                print(f"Step {i} reached maximum of {iter} iterations.")
        if v == 1:
            print(f'Finished with {iter_tot / nbSteps} iterations per step on average.')
        # POST-PROCESSING ------------------------------------------------
        # Computation of the stored and dissipated power quantities
        p_ohm_fil, p_ohm_mat = self.ohmic_loss(I, simulation=sim)
        p_rev = 0
        p_irr = 0
        p_eddy = 0
        for k in range(self.N):
            dfluxdt = self.L0 * np.concatenate(([0], np.diff(Irev[:, k]) / np.diff(time)))  # np.gradient(Irev[:,k], time)
            # Instantaneous power. Stored: \sum_k ( alpha_k * Irev_k * dphi_k/dt ). Dissipated: \sum_k ( alpha_k * Iirr_k * dphi_k/dt )
            p_rev += self.alphas[k] * Irev[:, k] * dfluxdt  # See Appendix B.2. of J. Dular's thesis (https://orbi.uliege.be/handle/2268/298054)
            p_irr += self.alphas[k] * Iirr[:, k] * dfluxdt
            p_eddy += self.alphas[k] * Ieddy[:, k] * dfluxdt

        # Per cycle loss
        p_fil_cycle = None
        p_mat_cycle = None
        if sim and sim.f:
            t_end = np.array(time)[-1]
            # Cumulative integration over one cycle
            x_init = self.__closest_matches(time, [t_end - 1 / (sim.f)])[0]
            cumul_p_fil = integrate.cumulative_trapezoid(p_irr + p_ohm_fil, time, initial=0)
            cumul_p_mat = integrate.cumulative_trapezoid(p_eddy + p_ohm_mat, time, initial=0)
            p_fil_cycle = (cumul_p_fil[-1] - cumul_p_fil[x_init])
            p_mat_cycle = (cumul_p_mat[-1] - cumul_p_mat[x_init])

        return flux, p_irr + p_ohm_fil, p_eddy + p_ohm_mat, p_fil_cycle, p_mat_cycle


class PostProcess:
    """
    This class loads and stores the data from a simulation and can apply various postprocessing operations on the data.
    The simulation data is saved as a SimulationData object.
    """

    def __init__(self, fdm, model_data_output_path) -> None:
        self.fdm = fdm
        self.model_data_output_path = model_data_output_path
        self.geometry_name = f"Geometry_{self.fdm.run.geometry}"
        self.mesh_name = f"Mesh_{self.fdm.run.mesh}"
        self.solution_name = f"Solution_{self.fdm.run.solution}"

        self.simulation_data = SimulationData(model_data_output_path, self.geometry_name, self.mesh_name, self.solution_name, self.fdm)
        self.flux_model = ROHFmodel(N=self.fdm.magnet.postproc.plot_flux.rohf_N,
                                    spacing_type=self.fdm.magnet.postproc.plot_flux.rohf_kappa_spacing,
                                    simulation=self.simulation_data,
                                    filename=self.fdm.magnet.postproc.plot_flux.rohf_file,
                                    filepath=os.path.join(self.model_data_output_path, self.geometry_name),
                                    ) if self.fdm.magnet.postproc.plot_flux.rohf else None
        self.plotter = PlotPythonConductorAC(fdm, model_data_output_path, self.simulation_data, self.flux_model)
        self.report = PDFreport(filepath=model_data_output_path,
                                title=f'{self.fdm.run.geometry}_{self.fdm.run.mesh}_{self.fdm.run.solution}' if self.fdm.magnet.postproc.generate_report else None)

    def rohf_background(self):
        """ Test for ROHFmodel background field scaling """
        if steammaterials_flag or self.flux_model is None:
            # skip
            return
        matpath = os.path.join(os.path.dirname(steammaterials.__file__), 'CFUN')

        Ic_0 = 2900
        B_background = self.simulation_data.B_background

        # analytic self-field on strand boundary
        CATI_surf = 54 * np.pi * (4.5e-05) ** 2  # 54 filament surface in CATI paper strand
        Jc_0 = Ic_0 / CATI_surf
        B_space = np.linspace(0, 14, 5000)
        # Determine ambient field with no background field and max current density
        numpy2d_Bspace = np.vstack((1.9 * np.ones(B_space.shape), B_space, 1 * np.ones(B_space.shape)))  # T, B, A
        nbti_space = steammaterials.SteamMaterials("CFUN_IcNbTi_v1", numpy2d_Bspace.shape[0], numpy2d_Bspace.shape[1], matpath)
        jc_nbti_space = nbti_space.evaluate(numpy2d_Bspace)
        B_ambient = B_space[np.abs(jc_nbti_space - Jc_0).argmin()]
        print("B_ambient: " + str(B_ambient) + " [T]")

        # Determine absolute field value which the strand experiences
        B_abs = B_background + (B_ambient / B_background) * B_ambient if B_background > B_ambient else B_background + B_ambient
        # material Jc(B) fit
        jc_nbti = steammaterials.SteamMaterials("CFUN_IcNbTi_v1", 3, 1, matpath)
        jc_Babs = jc_nbti.evaluate((1.9, B_abs, 1))[0]

        # PLOT
        plt.figure()
        plt.plot(B_space, jc_nbti_space, label='CFUN_IcNbTi_v1')
        plt.scatter((B_ambient, B_abs), (Jc_0, jc_Babs), label='Jc(B)', )
        plt.title('Nb-Ti')
        plt.grid()
        plt.legend()
        plt.xlabel("Field (T)")
        plt.ylabel("jc (A/m2)")

        kappa_scaling = jc_Babs / Jc_0
        print(" Kappa scaling factor: " + str(kappa_scaling))
        self.flux_model.kappa_scaling = kappa_scaling
        plt.show()

    def internal_flux(self):
        """ Postproc routine for the internal flux and the related ROHF model """
        self.plotter.plot_transport()
        self.plotter.plot_flux()
        self.plotter.plot_power_loss()
        self.plotter.plot_resistivity()

        # self.flux_model.export_params(filepath=os.path.join(self.model_data_output_path, self.geometry_name), filename="TESTFILE")
        # self.flux_model.import_params(filepath=os.path.join(self.model_data_output_path, self.geometry_name), filename="TESTFILE")

        if self.report and self.flux_model:
            self.report.add_table('ROHF parameters', self.flux_model.params())

    def instantaneous_loss(self):
        print("Total loss: ", self.simulation_data.cumulative_power["TotalLoss"].iloc[-1])
        print("Total filament loss: ", self.simulation_data.cumulative_power["FilamentLoss"].iloc[-1])
        print("Total coupling loss: ", self.simulation_data.cumulative_power["CouplingLoss"].iloc[-1])
        print("Total eddy loss: ", self.simulation_data.cumulative_power["EddyLoss"].iloc[-1])
        plot_options = self.fdm.magnet.postproc.plot_instantaneous_power
        self.plotter.plot_instantaneous_power(
            show=plot_options.show,
            title=plot_options.title,
            save_plot=plot_options.save,
            save_folder_path=os.path.join(self.model_data_output_path, self.geometry_name, self.mesh_name, self.solution_name),
            save_file_name=plot_options.save_file_name,
            overwrite=self.fdm.run.overwrite
        )

    def plot_impedance(self):
        """ Plots the impedance estimate and transport quantities """
        conductor = self.fdm.conductors[self.fdm.magnet.solve.conductor_name]
        frequency_range = np.logspace(-2, 6, 1000)

        self.simulation_data.plot_transport()

        #### VOLTAGE ####
        # self.simulation_data.plot_phaseshift_voltage(90)
        # self.simulation_data.plot_voltage_decomp()

        #### IMPEDANCE ####
        self.simulation_data.compare_impedance(frequency_range)


class BatchPostProcess:
    """
    This class loads and stores data from multiple simulations (+flux models) and performs operations on them
    """

    def __init__(self, fdm, lossMap_gridData_folder, inputs_folder_path, outputs_folder_path) -> None:
        self.fdm = fdm
        self.inputs_folder_path = inputs_folder_path  # This is the path to the folder where the input data is stored
        self.model_data_output_path = outputs_folder_path  # This is the path to the folder where the model output data is stored (e.g. geometries)
        self.outputs_folder_path = os.path.join(outputs_folder_path, fdm.magnet.postproc.output_folder)  # This is the path to the folder where the postprocessed data is written
        self.simulation_collection = self.retrieve_simulation_data()
        self.fluxmodel_collection = self.retrieve_fluxmodel_data()
        self.plotter = BatchPlotPythonConductorAC(
            fdm=self.fdm, lossMap_gridData_folder=lossMap_gridData_folder, outputs_folder_path=outputs_folder_path,
            simulation_collection=self.simulation_collection, fluxmodel_collection=self.fluxmodel_collection
        )
        self.report = PDFreport(filepath=outputs_folder_path, title='BatchPostprocReport') if self.fdm.magnet.postproc.generate_report else None
        self.avg_simulation_time = np.mean([sd.simulation_time for sd in self.simulation_collection])
        self.total_simulation_time = np.sum([sd.simulation_time for sd in self.simulation_collection])
        print('Number of simulations considered: ', len(self.simulation_collection))
        print('Average simulation time: ', self.avg_simulation_time, 's')
        print('Total simulation time: ', self.total_simulation_time, 's')

    def get_base_sim(self):
        """ Find simulation with lowest frequency and highest amplitude"""
        base_sim = self.simulation_collection[0]
        for sim in self.simulation_collection[1:]:
            if sim.f <= base_sim.f and sim.I_amp >= base_sim.I_amp: base_sim = sim
        return base_sim

    def rohf_on_grid(self):
        """ Checks the fit of an existing model to a grid of simulations or fits a new ROHF model to a grid of simulations """

        optimized_rohf = None
        if self.fdm.magnet.postproc.batch_postproc.rohf_on_grid.fit_rohf:

            tausweep_IIC = self.fdm.magnet.postproc.batch_postproc.rohf_on_grid.fit_rohf_tausweep_IIC
            N = self.fdm.magnet.postproc.batch_postproc.rohf_on_grid.fit_rohf_N
            print("FITTING ROHF TO SIMULATIONS:")
            print("-> number of cells N = " + str(N))
            print("-> tausweep IIC = " + str(tausweep_IIC))

            taus = self.optimize_taus(tausweep_IIC=tausweep_IIC, N=N)
            kappas, alphas = self.optimize_kappas(base_taus=taus, N=N)
            # export resulting ROHF
            optimized_rohf = ROHFmodel(N=N, kappas_bar=kappas, alphas=alphas, taus=taus)
            print(optimized_rohf.taus)
            print(optimized_rohf.alphas)
            print(optimized_rohf.kappas_bar)
            self.plotter.plot_flux_time_triplet(flux_model=optimized_rohf, title='Flux in time triplet')

            optimized_rohf.export_params(self.outputs_folder_path, 'optimized')

            if self.report:
                self.report.filename = 'ROHFoptimization.pdf'
                self.report.add_table('Parameter results', optimized_rohf.params())

        if self.fdm.magnet.postproc.batch_postproc.rohf_on_grid.produce_error_map:
            flux_model = optimized_rohf if optimized_rohf is not None else self.fluxmodel_collection[0]
            self.plotter.create_errorMap(flux_model=flux_model)

            if self.report:
                self.report.add_table('Error map parameter', optimized_rohf.params())

    def optimize_kappas(self, N, base_kappas=None, base_taus=None):

        base_sim = self.get_base_sim()
        if base_kappas is None:
            base_kappas = np.linspace(0, base_sim.I_amp, N + 1)[:-1]  # linear spaced over max I range
            # base_kappas = np.geomspace(1, base_sim.I_amp, N+1)[:-1]-1
        if base_taus is None:
            base_taus = np.zeros(N)
        baseROHF = ROHFmodel(simulation=base_sim, taus=base_taus, kappas_bar=base_kappas)

        print(" RUNNING KAPPA & WEIGHT OPTIMIZATION ...")

        # ERROR -------------------------------------------------------------------------------------------------------------------------------
        def fit_error_kappas(normalized_kappas):
            # static alpha fit based on recursion of kappas -> piecewise linear fit
            baseROHF.fit_data(taus=base_taus, simulation=base_sim, kappas_bar=normalized_kappas * base_sim.I_amp)
            flux_error = 0
            for simulation in self.simulation_collection:
                time, I, flux = simulation.halfcycle(current=True)
                rohf_flux, _, _, _, _ = baseROHF.compute(time, I)
                flux_error = flux_error + sum(np.diff(time, prepend=0) * np.absolute(flux - rohf_flux))
            return flux_error
            # BOUNDARIES --------------------------------------------------------------------------------------------------------------------------

        bounds = optimize.Bounds(lb=0, ub=1, keep_feasible=True)
        # OPTIMIZATION 1: KAPPA DISTRIBUTION & WEIGHTS ----------------------------------------------------------------------------------------
        kappa_optimization = optimize.minimize(fit_error_kappas, method='L-BFGS-B', x0=base_kappas / base_sim.I_amp, bounds=bounds, options={"disp": True})
        optimized_kappas = np.sort(kappa_optimization.x * base_sim.I_amp)
        print(" --> OPTIMIZED KAPPAS: " + str(optimized_kappas))

        # ERROR -------------------------------------------------------------------------------------------------------------------------------
        def fit_error_alphas(alphas):
            baseROHF.alphas = alphas
            flux_error = 0
            for simulation in self.simulation_collection:
                time, I, flux = simulation.halfcycle(current=True)
                rohf_flux, _, _, _, _ = baseROHF.compute(time, I)
                flux_error = flux_error + sum(abs(np.diff(I, prepend=0)) * np.diff(time, prepend=0) * np.absolute(flux - rohf_flux))
            return flux_error
            # BOUNDARIES --------------------------------------------------------------------------------------------------------------------------

        bounds = optimize.Bounds(lb=0, ub=10, keep_feasible=True)
        # OPTIMIZATION 2: WEIGHTS ONLY ---------------------------------------------------------------------------------------------------------
        alpha_optimization = optimize.minimize(fit_error_alphas, method='L-BFGS-B', x0=baseROHF.alphas, bounds=bounds, options={"disp": True})
        optimized_alphas = alpha_optimization.x
        print(" --> OPTIMIZED ALPHAS: " + str(optimized_alphas))

        return [optimized_kappas, optimized_alphas]

    def optimize_taus(self, tausweep_IIC, N, base_taus=None, base_kappas=None):

        force_tau1_zero = False
        base_sim = self.get_base_sim()

        amplitudes = sorted(list(set([sim.I_amp for sim in self.simulation_collection])))
        tausweep_I = min(amplitudes, key=lambda x: abs(x - tausweep_IIC * amplitudes[-1]))  # get grid current closest to tausweep IIC
        tau_sweep = [sim for sim in self.simulation_collection if sim.I_amp == tausweep_I]  # get asociated sweep

        freq = sorted(list(set([sim.f for sim in tau_sweep])))
        if base_kappas is None:
            base_kappas = np.linspace(0, amplitudes[-1], N + 1)[:-1]  # start with linear spaced over max_I range
        if base_taus is None:
            # Estimate initial tau values with lowpass approximation
            loss = [sim.total_power_per_cycle['FilamentLoss'] for sim in tau_sweep]
            resamp_freq = np.linspace(freq[0], freq[-1], 500)
            resamp_loss = np.interp(resamp_freq, freq, loss)
            idx = np.abs(loss - resamp_loss[0] * 0.707).argmin()  # -3dB mark -> crit freq
            tau_star = 1 / (2 * np.pi * resamp_freq[idx])  # f_c of lowpass
            base_taus = base_kappas / (N * tausweep_I) * tau_star  # scale estimate down w. cell level

        baseROHF = ROHFmodel(N=N, simulation=base_sim, kappas_bar=base_kappas, taus=base_taus)
        self.plotter.plot_percycle_losses(sims=tau_sweep, flux_model=baseROHF, title='STARTING TAUS')

        if True:
            print(" RUNNING TAU OPTIMIZATION ... ")

            # ERROR -------------------------------------------------------------------------------------------------------------------------------
            def fit_error(taus):
                baseROHF.taus = np.concatenate(([0], taus)) if force_tau1_zero else taus
                error = 0
                for idx, sim in enumerate(self.simulation_collection):
                    time, I, flux = sim.halfcycle(current=True)
                    flux_rohf, fill_rohf, eddy_rohf, _, _ = baseROHF.compute(time=time, I=I)
                    # errors[idx] = abs(sim.total_power_per_cycle['EddyLoss']-eddy_pc_rohf) + abs(sim.total_power_per_cycle['FilamentLoss']-fill_pc_rohf)
                    error = error + sum(abs((sim.power['EddyLoss'][:len(I)] - eddy_rohf)) / np.mean(sim.power['EddyLoss']) + abs((sim.power['FilamentLoss'][:len(I)] - fill_rohf)) / np.mean(sim.power['FilamentLoss']))
                return error
                # BOUNDARIES --------------------------------------------------------------------------------------------------------------------------

            bounds = optimize.Bounds(lb=0.0, ub=0.1)
            # OPTIMIZATION ------------------------------------------------------------------------------------------------------------------------
            optimization = optimize.minimize(fit_error, x0=base_taus, bounds=bounds, options={'disp': True})  # , method='SLSQP'
            optimized_taus = np.concatenate(([0], optimization.x[1:])) if force_tau1_zero else optimization.x

            print(" --> OPTIMIZED TAUS: " + str(optimized_taus))
            baseROHF.fit_data(simulation=base_sim, spacing_type='linear', taus=np.sort(optimized_taus))
            self.plotter.plot_percycle_losses(sims=tau_sweep, flux_model=baseROHF, title='OPTIMIZED TAUS')
            # plt.show()
            return np.sort(optimized_taus)

        else:
            return baseROHF.taus

    def retrieve_simulation_data(self):
        """
        This function iterates over the input CSV-file (specifying which simulations to postprocess) and returns a list of SimulationData objects
        containing all the simulation data. If no CSV-file is specified, the data from the single simulation specified in the input YAML-file is returned.
        """

        simulations_csv = self.fdm.magnet.postproc.batch_postproc.simulations_csv
        if simulations_csv is not None:
            try:
                self.simulations_csv = pd.read_csv(os.path.join(self.inputs_folder_path, f'{simulations_csv}.csv'))  # Read the csv file with the input data
            except:
                raise FileNotFoundError(f'No csv file with the name {simulations_csv}.csv was found in the inputs folder.')

        if self.simulations_csv is not None:
            simulationCollection = []
            for index, row in self.simulations_csv.iterrows():
                if pd.isna(row['input.run.geometry']) and pd.isna(row['input.run.mesh']) and pd.isna(row['input.run.solution']):
                    continue
                geometry_name = 'Geometry_' + str(row['input.run.geometry'])
                mesh_name = 'Mesh_' + str(row['input.run.mesh'])

                if isinstance(row['input.run.solution'], float) and row['input.run.solution'].is_integer():
                    solution_name = 'Solution_' + str(int(row['input.run.solution']))
                else:
                    solution_name = 'Solution_' + str(row['input.run.solution'])

                # Check if the row refers to a valid simulation by checking if the solution folder exists:
                # solution_folder = os.path.join(os.getcwd(), 'tests', '_outputs', self.fdm.general.magnet_name, geometry_name, mesh_name, solution_name)
                solution_folder = os.path.join(self.model_data_output_path, geometry_name, mesh_name, solution_name)
                if os.path.exists(solution_folder):  # If the solution folder exists, add the simulation to the simulationCollection
                    sd = SimulationData(self.model_data_output_path, geometry_name, mesh_name, solution_name, self.fdm)
                    if sd.simulation_time is not None:  # Only add the simulation if it has finished running (and therefore has written the simulation time to a file)
                        simulationCollection.append(sd)
        else:
            simulationCollection = [SimulationData(self.model_data_output_path, 'Geometry_' + self.fdm.run.geometry, 'Mesh_' + self.fdm.run.mesh, 'Solution_' + self.fdm.run.solution)]

        return self.sort_simulationCollection(self.filter_simulationCollection(simulationCollection))

    def filter_simulationCollection(self, simulationCollection):
        """
        This function is used to filter the simulationCollection based on the filter criterion specified in the yaml input file.
        An example of a filter criterion is '<<solve.source_parameters.sine.frequency>> == 18', which will disregard all simulations with frequency != 18Hz.
        """
        if self.fdm.magnet.postproc.batch_postproc.filter.apply_filter:
            filter_criterion = self.fdm.magnet.postproc.batch_postproc.filter.filter_criterion
            class_params = re.findall('<<(.*?)>>', filter_criterion)
            for cp in class_params:
                filter_criterion = filter_criterion.replace(f"<<{cp}>>", 'sd.' + cp)
            filtering_function = eval(f'lambda sd: {filter_criterion}')
            return list(filter(filtering_function, simulationCollection))
        else:
            return simulationCollection

    def sort_simulationCollection(self, simulationCollection):
        """
        This function is used to sort the simulationCollection based on the sort key specified in the yaml input file.
        An example of a sort key is 'solve.source_parameters.sine.frequency', which will sort the simulations based on frequency.
        """
        if self.fdm.magnet.postproc.batch_postproc.sort.apply_sort:
            sorting_function = eval(f'lambda sd: sd.{self.fdm.magnet.postproc.batch_postproc.sort.sort_key}')
            return sorted(simulationCollection, key=sorting_function)
        else:
            return simulationCollection

    def retrieve_fluxmodel_data(self):
        """ Analog function to retrieve_simulation_data but for fluxmodels (Glock-Thesis). """
        fluxmodels_csv = self.fdm.magnet.postproc.batch_postproc.fluxmodels_csv
        if fluxmodels_csv is not None:
            try:
                self.fluxmodels_csv = pd.read_csv(os.path.join(self.inputs_folder_path, f'{fluxmodels_csv}.csv'))  # Read the csv file with the input data
            except:
                raise FileNotFoundError(f'No csv file with the name {fluxmodels_csv}.csv was found in the inputs folder.')

        fluxmodelCollection = []
        if fluxmodels_csv is not None:
            for index, row in self.fluxmodels_csv.iterrows():
                if pd.isna(row['input.run.geometry']) and pd.isna(row['input.run.mesh']) and pd.isna(row['input.run.solution']):
                    continue
                geometry_name = 'Geometry_' + str(row['input.run.geometry'])
                parameterfile_path = os.path.join(self.model_data_output_path, geometry_name)
                parameterfile_name = str(row['input.run.parameterfile'])
                label_name = str(row['input.run.label'])

                fluxmodelCollection.append(ROHFmodel(filepath=parameterfile_path, filename=parameterfile_name, label=label_name))

        return fluxmodelCollection