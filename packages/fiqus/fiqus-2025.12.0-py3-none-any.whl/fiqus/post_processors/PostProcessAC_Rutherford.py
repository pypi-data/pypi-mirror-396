import os, logging
import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger('FiQuS')

class PostProcess:
    def __init__(self, solution_folder_path):
        self.solution_folder_path = solution_folder_path

        self.plot_transport()
        # self.plot_strand_split()
        self.plot_fluxhyst()
        self.plot_power_rohf()

    def load_standard_txt(self, file_rel_path, skiprows=1):
        """Load the content of a txt file into a nested numpy array

        :param file_rel_path: relative file path in the solution folder (with file extension)
        :param skiprows: number of rows to skip at the top of the txt file, defaults to 1
        :return: nested np.array with time at index 0
        """
        file_path = os.path.join(self.solution_folder_path, file_rel_path)
        return np.loadtxt(file_path, skiprows=skiprows).T if os.path.isfile(file_path) else None

    def plot_transport(self):
        """ Plots transport current and voltage over time if existing """

        Vt_data = self.load_standard_txt('txt_files\\Vt.txt')
        It_data = self.load_standard_txt('txt_files\\It.txt') 

        if all(x is not None for x in (It_data, Vt_data)):
            fig, ax1 = plt.subplots()
            ax1.set_title("Transport current and voltage")
            ax1.set_xlabel(r'Time $(s)$')
            ax1.set_ylabel(r'Current $(A)$', color = 'red')
            ax1.plot(It_data[0], It_data[1], color = 'red')
            ax1.grid(axis='x', linestyle='dotted')
            ax1.tick_params(axis='y', labelcolor = 'red')
            
            ax2 = ax1.twinx()
            ax2.set_ylabel(r'Voltage $(V)$', color = 'blue')
            ax2.plot(Vt_data[0], Vt_data[1], color = 'blue')
            ax2.tick_params(axis='y', labelcolor = 'blue')
            ax2.grid(axis='y', linestyle='dotted')
            fig.tight_layout()

    def plot_fluxhyst(self):
        """ Plots the internal flux hysteresis and resulting voltages if existing (ROHF enabled and stranded strands) """

        fluxhyst_data = self.load_standard_txt('txt_files\\flux_hyst.txt')
        voltage_rohf = self.load_standard_txt('txt_files\\voltage_rohf.txt')
        Is_data = self.load_standard_txt('txt_files\\Is.txt')  

        if all(x is not None for x in (fluxhyst_data, Is_data)):
            # plot only the first quarter of the strands because of symmetry ...
            q_idx = round((len(fluxhyst_data)-1) / 4)
            colors = plt.cm.rainbow(np.linspace(0,1,q_idx))
            plt.figure(figsize=(10,5))
            # Flux in strand currents
            plt.subplot(121)
            plt.title('ROHF Flux hysteresis')
            for i in range(1,q_idx+1):
                plt.plot(Is_data[i], fluxhyst_data[i], label='Strand '+str(i), color=colors[i-1]) 
            plt.xlabel(r"Strand current (A)")
            plt.ylabel(r'Internal flux (Wb/m$)')
            plt.legend()  

            # Resulting strand ROHF voltages
            plt.subplot(122)
            plt.title('ROHF voltages')
            if voltage_rohf is not None:
                for i in range(1, q_idx+1):
                    plt.plot(voltage_rohf[0], voltage_rohf[i], label='Strand '+str(i), color=colors[i-1])
                    #plt.plot(self.linflux_voltage[0], self.linflux_voltage[i], linestyle='dashed', color=colors[i-1])
            plt.xlabel('Time (s)')
            plt.ylabel(r'Voltage (V/m)')
            plt.legend()

    def plot_strand_split(self):
        """ Plots the Strand currents and voltages for stranded strands enabled """

        Vt_data = self.load_standard_txt('txt_files\\Vt.txt')
        It_data = self.load_standard_txt('txt_files\\It.txt') 
        Vs_data = self.load_standard_txt('txt_files\\Vs.txt')
        Is_data = self.load_standard_txt('txt_files\\Is.txt')  

        if all(x is not None for x in (It_data, Vt_data, Is_data, Vs_data)):
            # plot only the first quarter of the strands because of symmetry ...
            q_idx = round((len(Vs_data)-1) / 4)
            colors = plt.cm.rainbow(np.linspace(0,1,q_idx))

            plt.figure(figsize=(9,5))
            plt.subplot(121)
            plt.title('Strand voltages')
            plt.plot(Vt_data[0], Vt_data[1], label='Total transport voltage')
            for i in range(1,q_idx+1):
                plt.plot(Vs_data[0], Vs_data[i], label='Strand '+str(i), color=colors[i-1])  
            plt.plot(Vs_data[0], sum(Vs_data[1:]), 'r.--', label=r'$\sum \ V_s$')
            #plt.scatter(self.Vs_data[0], self.Vs_data[36], marker='x', label='Strand 36')
            plt.xlabel(r"Time (s)")
            plt.ylabel(r'Voltage (V/m)')
            plt.legend()       

            plt.subplot(122)
            plt.title('Strand currents')
            plt.plot(It_data[0], It_data[1], label='Total transport current')
            for i in range(1,q_idx+1):
                plt.plot(Is_data[0], Is_data[i], label='Strand '+str(i), color=colors[i-1])
            plt.plot(Is_data[0], sum(Is_data[1:]), 'r.--', label=r'$\sum \ I_s$')  
            #plt.scatter(self.Is_data[0], self.Is_data[36], marker='x', label='Strand 36')
            plt.xlabel(r"Time (s)")
            plt.ylabel(r'Current (A)')       
            plt.legend()  

    def plot_power_rohf(self):
        """ Plots the ROHF related power contributions if existing """

        power = self.load_standard_txt('txt_files\\power.txt')
        power_hyst_rohf = self.load_standard_txt('txt_files\\power_hyst_ROHF.txt')
        power_eddy_rohf = self.load_standard_txt('txt_files\\power_eddy_ROHF.txt')

        if power is not None and len(power) == 5:
            colors = plt.cm.rainbow(np.linspace(0,1,4))

            plt.figure()
            plt.title('Instantaneous power loss contributions')
            #plt.plot(self.power[0], self.power[1], label='Total', color=colors[0])   
            plt.plot(power[0], power[2], label='hyst powerfile', linestyle='--', color=colors[1])
            plt.plot(power_hyst_rohf[0], sum(power_hyst_rohf[1:]), label='Hyst', color=colors[1])
            plt.plot(power[0], power[3], label='Eddy powerfile', linestyle='--', color=colors[2])
            plt.plot(power_eddy_rohf[0], sum(power_eddy_rohf[1:]), label='Eddy', color=colors[2]) 
            #plt.plot(power_hyst_strands[0], sum(power_hyst_strands[1:]), label='strands sum')
            plt.xlabel(r"Time (s)")
            plt.ylabel(r'Power loss (W/m)') 
            plt.legend()
        
    def show(self):
        """ Display all generated plots at once """
        plt.show() if len(plt.get_fignums()) > 0 else logger.info('- NO POSTPROC DATA -')


