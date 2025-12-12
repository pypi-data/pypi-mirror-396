import functools
import itertools
import operator
import os
import unittest
from pathlib import Path

import numpy as np

from fiqus.data.DataFiQuS import FDM
from fiqus.utils.Utils import FilesAndFolders as FFs


class Paths:
    """
    Helper class used in FiQuS tests to get file and folder paths
    :param model_name: name of yaml input file (without .yaml)
    :param f_extension: file extension to apply to the folders, for example '.brep' or '.msh'
    :return: tuple: fdm, outputs_folder, input_folder, input_file, model_folder, model_file, reference_folder, reference_file
    """

    def __init__(self, model_name, f_extension=''):
        self.inputs_folder_name = '_inputs'
        self.outputs_folder_name = '_outputs'
        self.references_folder_name = '_references'

        self.test_outputs_folder = os.path.join(os.getcwd(), self.outputs_folder_name)
        self.inputs_folder = os.path.join(os.getcwd(), self.inputs_folder_name, model_name)
        self.model_folder = os.path.join(os.getcwd(), self.outputs_folder_name, model_name)
        self.references_folder = os.path.join(os.getcwd(), self.references_folder_name, model_name)

        self.input_file = os.path.join(self.inputs_folder, f'{model_name}.yaml')
        self.model_file = os.path.join(self.model_folder, f'{model_name}.{f_extension}')
        self.reference_file = os.path.join(self.references_folder, f'{model_name}.{f_extension}')


def filecmp(filename1, filename2):
    """
    From: https://stackoverflow.com/questions/254350/in-python-is-there-a-concise-way-of-comparing-whether-the-contents-of-two-text
    Do the two files have exactly the same contents?
    """
    with open(filename1, "rb") as fp1, open(filename2, "rb") as fp2:
        print(f'The {filename1} size is: {os.fstat(fp1.fileno()).st_size} b')
        print(f'The {filename2} size is: {os.fstat(fp2.fileno()).st_size} b')
        if os.fstat(fp1.fileno()).st_size != os.fstat(fp2.fileno()).st_size:
            return False  # different sizes ∴ not equal

        # set up one 4k-reader for each file
        fp1_reader = functools.partial(fp1.read, 4096)
        fp2_reader = functools.partial(fp2.read, 4096)

        # pair each 4k-chunk from the two readers while they do not return '' (EOF)
        cmp_pairs = zip(iter(fp1_reader, b''), iter(fp2_reader, b''))

        # return True for all pairs that are not equal
        inequalities = itertools.starmap(operator.ne, cmp_pairs)
        ineqs = []
        for ineq in inequalities:
            ineqs.append(ineq)
        # voila; any() stops at first True value
        print(f'The file comp function gives: {not any(inequalities)}')
        return not any(inequalities)


def assert_two_parameters(true_value, test_value):
    """
     Some functions used in multiple test functions
        **Assert two parameters - accepts multiple types**
    """
    # TODO: improve robustness and readability
    test_case = unittest.TestCase()

    if isinstance(true_value, np.ndarray) or isinstance(true_value, list):
        if len(true_value) == 1:
            true_value = float(true_value)

    if isinstance(test_value, np.ndarray) or isinstance(test_value, list):
        if len(test_value) == 1:
            test_value = float(test_value)

    # Comparison
    if isinstance(test_value, np.ndarray) or isinstance(test_value, list):
        if np.array(true_value).ndim == 2:
            for i, test_row in enumerate(test_value):
                if isinstance(test_row[0], np.floating):
                    test_row = np.array(test_row).round(10)
                    true_value[i] = np.array(true_value[i]).round(10)

                test_case.assertListEqual(list(test_row), list(true_value[i]))
        else:
            if isinstance(test_value[0], np.floating):
                test_value = np.array(test_value).round(10)
                true_value = np.array(true_value).round(10)

            test_case.assertListEqual(list(test_value), list(true_value))
    else:
        test_case.assertEqual(test_value, true_value)
