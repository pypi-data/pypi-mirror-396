import pandas as pd
import re
from collections import defaultdict

class ParserRES:

    def __init__(self, res_file_path, write_data=None):
        """
        TO BE DONE!!
        Read res file and returns its content as object attribute .pqv (postprocessed quantity value) that is a float
        :param dat_file_path: Full path to .pos file, including file name and extension.
        :return: nothing, keeps attribute pqv (postprocessed quantity value)
        """
        self._res_format_markers = {'s': '$ResFormat', 'e': '$EndResFormat'}
        self._getdp_version_markers = {'s': '/* ', 'e': ','}
        self._encoding_markers = {'s': ', ', 'e': ' */'}
        # the 1.1 is hard-coded according to the GetDP documentation, 
        # see https://getdp.info/doc/texinfo/getdp.html#File-formats
        self._res_file_format = {'s': '1.1 ', 'e': '\n$EndResFormat'}

        self.solution = defaultdict(dict)
        
        if write_data:
            self._res_file_path = res_file_path
            self._write_data = write_data
            self._write_res_file()
        else:
            # read contents of .res file
            with open(res_file_path) as f:
                self._contents = f.read()
            self._parse_res_file()


    def __get_content_between_markers(self, markers_dict):
            """
            Gets text string between two markers specified in markers_dict
            """
            return self._contents[self._contents.find(markers_dict['s']) + len(markers_dict['s']):self._contents.find(markers_dict['e'])]

    def _res_header(self):
        """
        Parse the header of the .res file.
        Add the attributes: 
        - getdp_version: GetDP version that created the .res file
        - encoding: encoding of the .res file
        - res_file_format: format of the .res file
        """
        self.getdp_version = self.__get_content_between_markers(self._getdp_version_markers)
        self.encoding = self.__get_content_between_markers(self._encoding_markers)
        self.res_file_format = self.__get_content_between_markers(self._res_file_format)

    def _get_all_solution_blocks(self):
        """
        Add all unparsed solution blocks to the attribute _solution_blocks
        using regular expressions. It is a list of lists which each sub-list 
        containing exactly one solution block.
        """
        solution_string = self._contents[self._contents.find('$Solution'):]
        self._solution_blocks = re.findall(r'\$Solution.*?\$EndSolution', solution_string, re.DOTALL)

    def _parse_res_file_single_solution_block(self, solution_block_split_by_line):

        # the first line is ignored 
        header = solution_block_split_by_line[1]
        header_split = header.split()
        dof_data = int(header_split[0])
        time_real = float(header_split[1])
        time_imag = float(header_split[2])
        time_step = int(header_split[3])
        solution = [float(entry) for entry in solution_block_split_by_line[2:-1]]

        if "time_real" not in self.solution: 
            self.solution['time_real'] = [time_real]
        else: 
            self.solution['time_real'].append(time_real)

        if "time_imag" not in self.solution: 
            self.solution['time_imag'] = [time_imag]
        else: 
            self.solution['time_imag'].append(time_imag)

        if "time_step" not in self.solution: 
            self.solution['time_step'] = [time_step]
        else: 
            self.solution['time_step'].append(time_step)

        if "dof_data" not in self.solution: 
            self.solution['dof_data'] = [dof_data]
        else: 
            self.solution['dof_data'].append(dof_data)

        if "solution" not in self.solution: 
            self.solution['solution'] = [solution]
        else: 
            self.solution['solution'].append(solution)

    @staticmethod
    def __get_lines(data_str):
        """
        Converts text string into a list of lines
        """
        data_str = re.sub('\n', "'", data_str)
        data_str = re.sub('"', '', data_str)
        str_list = re.split("'", data_str)
        return str_list

    def _parse_res_file_solution_blocks(self):
        """
        
        """
        for solution_block in self._solution_blocks:
            # split by line
            solution_block_split_by_line = self.__get_lines(solution_block)
            self._parse_res_file_single_solution_block(solution_block_split_by_line)

    def _parse_res_file(self): 
        self._res_header()
        self._get_all_solution_blocks()
        self._parse_res_file_solution_blocks()

    def _write_res_file(self):
        with open(self._res_file_path, "w") as f:
            # write header
            f.write(f"$ResFormat /* {self._write_data.getdp_version}, {self._write_data.encoding} */\n")
            # write res file format
            f.write(f"1.1 {self._write_data.res_file_format}\n")
            f.write(f"$EndResFormat\n")

            self._write_solution_block(f)

    def _write_solution_block(self, f):
        for time_real, time_imag, time_step, dof_data, solution in zip(self._write_data.solution['time_real'], self._write_data.solution['time_imag'], self._write_data.solution['time_step'], self._write_data.solution['dof_data'], self._write_data.solution['solution']):
        
            f.write(f"$Solution  /* DofData #{dof_data} */\n")
            f.write(f"{dof_data} {time_real:.16g} {time_imag:.16g} {time_step}\n")
            f.write('\n'.join('{0:.16g}'.format(sol_entry) for sol_entry in solution))
            f.write(f"\n$EndSolution\n")

# ==============================================================================
#parsedRes = ParserRES('test.res')
#ParserRES('test_written.res', write_data=parsedRes)
#import filecmp 
#print(filecmp.cmp('test.res', 'test_written.res'))