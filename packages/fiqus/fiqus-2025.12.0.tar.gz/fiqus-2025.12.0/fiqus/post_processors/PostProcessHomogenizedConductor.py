import os, re, logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

logger = logging.getLogger('FiQuS')


class PostProcess():
    """Class for python post processing of HomogenizedConductor simulations"""
    def __init__(self, fdm, solution_folder_path):
        self.fdm = fdm
        self.solution_folder_path = solution_folder_path
        # try to create ROHF plots
        self.plot_density_lines()
        self.fluxhyst()
        self.power_loss()
    
    def load_standard_txt(self, rel_file_path, skiprows=0, transpose=True):
        """This function loads standards txt files within the solution folder to numpy arrays.

        :param rel_file_path: relative path with file extension within the solution folder
        """
        abs_file_path = os.path.join(self.solution_folder_path, rel_file_path)
        data = None
        if os.path.isfile(abs_file_path):
            data = np.loadtxt(abs_file_path, skiprows=skiprows).T if transpose else np.loadtxt(abs_file_path, skiprows=skiprows)
        return data
    
    def fluxhyst(self):
        """This function tries to load and display the flux hysteresis (ROHF activated) in the solution data."""

        fluxhyst = self.load_standard_txt('txt_files\\fluxhyst.txt')
        #flux_average = self.load_standard_txt('txt_files\\flux_density_avg.txt')
        #flux_strand = self.load_standard_txt('txt_files\\flux_density_strand_avg.txt')
        
        voltage_rohf = self.load_standard_txt('txt_files\\voltage_rohf.txt')
        It = self.load_standard_txt('txt_files\\It.txt', skiprows=1)
        
        if fluxhyst is not None and It is not None:
            plt.figure(figsize=(10,5))
            plt.subplot(121)
            plt.title('Flux hysteresis')
            plt.plot(It[1], fluxhyst[1])
            #plt.plot(It[1], fluxhyst[1] - mu_0/(4*pi) * It[1])
            plt.xlabel('Transport current (A)')
            plt.ylabel('Internal Flux (Tm)')
            #plt.legend()
            
            plt.subplot(122)
            plt.title('ROHF voltage (unit length)')
            if voltage_rohf is not None: plt.plot(voltage_rohf[0], voltage_rohf[1])
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            #plt.legend()
        else:
            logger.error("POSTPROC: No flux hysteresis data")

    def plot_density_lines(self):

        fluxdens_line = self.load_standard_txt('txt_files\\flux_density_line.txt', transpose=False)
        currentdens_line = self.load_standard_txt('txt_files\\current_density_line.txt', transpose=False)
        It = self.load_standard_txt('txt_files\\It.txt')
        
        idx = 10

        if fluxdens_line is not None and It is not None:
            N_steps = len(It[0])
            time = fluxdens_line[idx][1]
            x_vals = np.zeros(200)
            fluxdens = np.zeros(200)
            for i in range(0,200):
                x_vals[i] = fluxdens_line[idx+i*N_steps][2]
                fluxdens[i] = fluxdens_line[idx+i*N_steps][5]

            plt.figure()
            plt.title('fluxdens at '+str(time) +'s')
            plt.plot(x_vals, fluxdens)
            plt.xlabel('Position on x-axis')
            plt.ylabel('Flux density')

        if currentdens_line is not None and It is not None:
            N_steps = len(It[0])
            time = currentdens_line[idx][1]
            x_vals = np.zeros(200)
            currentdens = np.zeros(200)
            for i in range(0,200):
                x_vals[i] = currentdens_line[idx+i*N_steps][2]
                currentdens[i] = currentdens_line[idx+i*N_steps][7]

            plt.figure()
            plt.title('Current denisty at '+str(time) +'s')
            plt.plot(x_vals, currentdens)
            plt.xlabel('Position on x-axis')
            plt.ylabel('Current density')

    def power_loss(self):
        """This function tries to load and display the power loss from the solution data. Currently only supports ROHF associated losses. """

        power = self.load_standard_txt('txt_files\\power.txt')

        if power is not None and len(power) == 5:
            plt.figure()
            plt.title('Instantaneous power losses')
            plt.plot(power[0], power[2], label=r'$P_{\mathrm{irr}}$')
            plt.plot(power[0], power[3], label=r'$P_{\mathrm{eddy}}$')
            plt.plot(power[0], power[4], label=r'$P_{\mathrm{PL}}$')
            plt.legend()
        else:
            logger.error("POSTPROC: no/wrong power data")

    def show(self):
        """Utility funtion which is called in the end of the python post proc to display all figures at the same time"""
        plt.show() if len(plt.get_fignums()) > 0 else logger.info('- No postproc figures -')
