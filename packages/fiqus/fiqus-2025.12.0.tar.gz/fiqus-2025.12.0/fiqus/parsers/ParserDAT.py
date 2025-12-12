import pandas as pd


class ParserDAT:

    def __init__(self, dat_file_path):
        """
        Read dat file and returns its content as object attribute .pqv (postprocessed quantity value) that is a float
        :param dat_file_path: Full path to .pos file, including file name and extension.
        :return: nothing, keeps attribute pqv (postprocessed quantity value)
        """
        pqn = 'pqn'  # postprocessed quantity name
        delimiter = ' '
        columns = ['NaN', pqn]
        df = pd.read_csv(dat_file_path, delimiter=delimiter, header=None, engine='python', names=columns, skipinitialspace=True)
        self.pqv = float(df[pqn][0])
