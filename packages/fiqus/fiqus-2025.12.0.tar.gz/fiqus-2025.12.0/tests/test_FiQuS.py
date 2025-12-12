import unittest
import os
from pathlib import Path
import gmsh
import numpy as np
import pandas as pd
import getpass

from fiqus.data.DataFiQuS import FDM
from fiqus.MainFiQuS import MainFiQuS
from fiqus.parsers.ParserMSH import ParserMSH
from fiqus.parsers.ParserPOS import ParserPOS
import tests.utils.helpers as tuh
from fiqus.utils.Utils import GmshUtils
from fiqus.utils.Utils import FilesAndFolders as FFs
from fiqus.utils.Utils import RoxieParsers as Pars


class TestFiQuS(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('Test is run from folder: {}'.format(os.getcwd()))

        self.model_names = ['MCBRD_2d2a_2n2a_0i']

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_01_GenerateAllGeometryOnly(self):
        """
            Check that geometry file (.brep) can be generated and is the same as the reference.
        """
        # arrange
        for model_name in self.model_names:
            p = tuh.Paths(model_name, 'brep')
            FFs.prep_folder(p.test_outputs_folder)

            fdm = FFs.read_data_from_yaml(p.input_file, FDM)
            fdm.run.type = 'geometry_only'
            fdm.run.geometry = 1
            fdm.run.overwrite = True

            # act
            main_fiqus = MainFiQuS(input_file_path=p.input_file, model_folder=p.model_folder, fdm=fdm)

            # assert
            gu = GmshUtils(model_name, True)
            gu.initialize()

            print('Comparing model and reference .brep files')
            print(f'Model file: {main_fiqus.main_magnet.model_file}')
            gmsh.open(main_fiqus.main_magnet.model_file)
            model_entities = []
            for dim in range(4):
                model_entities.append(sorted(gmsh.model.getEntities(dim=dim)))
            gmsh.clear()

            print(f'Reference file: {p.reference_file}')
            gmsh.open(p.reference_file)
            reference_entities = []
            for dim in range(4):
                reference_entities.append(sorted(gmsh.model.getEntities(dim=dim)))
            gmsh.clear()

            self.assertEqual(len(model_entities), len(reference_entities))
            for model_ents, reference_ents in zip(model_entities, reference_entities):
                self.assertEqual(len(model_ents), len(reference_ents))
                for model_ent, reference_ent in zip(model_ents, reference_ents):
                    self.assertEqual(model_ent[1], reference_ent[1], msg=f'Models elements are not equal for dimension: {reference_ent[0]}!')
            print('The number of points, lines, surfaces and volumes in the .brep files match!')

    def test_02_GenerateAllMeshOnly(self):
        """
            Check that mesh file with correct physical names gets generated
        """
        # arrange
        for model_name in self.model_names:
            p = tuh.Paths(model_name, 'msh')
            FFs.prep_folder(p.test_outputs_folder)

            fdm = FFs.read_data_from_yaml(p.input_file, FDM)
            fdm.run.type = 'mesh_only'
            fdm.run.geometry = 1
            fdm.run.mesh = 1
            fdm.run.overwrite = True

            # act
            main_fiqus = MainFiQuS(input_file_path=p.input_file, model_folder=p.model_folder, fdm=fdm)

            # assert
            # this only compares if physical group names in the mesh files are equal. i.e. are all regions created, including cuts in a correct way.
            print('Comparing physical group names in the output and reference .msh files')
            print(f'Model file: {main_fiqus.main_magnet.model_file}')
            print(f'Reference file: {p.reference_file}')
            output_physical_names = ParserMSH(main_fiqus.main_magnet.model_file).physical_names
            reference_physical_names = ParserMSH(p.reference_file).physical_names
            print(f'Output physical group names:'
                  f'{output_physical_names}')
            print(f'Reference physical group names:'
                  f'{reference_physical_names}')
            self.assertEqual(output_physical_names, reference_physical_names)
            print('The mesh files physical group names match!')

    def test_03_AllSolveOnly(self):
        """
            Check that Solution pos file is identical to the reference one
        """
        # arrange
        for model_name in self.model_names:
            p = tuh.Paths(model_name, '')
            FFs.prep_folder(p.test_outputs_folder)

            fdm = FFs.read_data_from_yaml(p.input_file, FDM)
            fdm.run.type = 'solve_only'
            fdm.run.geometry = 1
            fdm.run.mesh = 1
            fdm.run.solution = 1
            fdm.run.overwrite = True
            # fdm.run.launch_gui = True

            # act
            main_fiqus = MainFiQuS(input_file_path=p.input_file, model_folder=p.model_folder, fdm=fdm)

            # assert
            columns = ['x', 'y', 'z', 'NaN1', 'NaN2', 'Bx', 'By', 'Bz', 'NaN3', 'NaN4']
            delimiter = ' '
            print('Comparing magnetic field csv files')
            model_file = main_fiqus.main_magnet.model_file
            print(f'Output file: {model_file}')
            model_df = pd.read_csv(model_file, delimiter=delimiter, header=None, engine='python', names=columns)
            reference_file = os.path.join(p.references_folder, 'Center_line.csv')
            print(f'Reference file: {reference_file}')
            reference_df = pd.read_csv(reference_file, delimiter=delimiter, header=None, engine='python', names=columns)

            coord_atol = 1e-9
            field_atol = 1e-3
            comparison_atol = [coord_atol, coord_atol, coord_atol, None, None, field_atol, field_atol, field_atol, None, None]
            for column, atol in zip(columns, comparison_atol):
                if atol:
                    print(f'Comparing {column} values with absolute tolerance of {atol}')
                    comparison_result = np.isclose(np.mean(model_df[column]), np.mean(reference_df[column]), rtol=0.05, atol=atol, equal_nan=True).all()
                    self.assertTrue(comparison_result)
                    print(f'Data in {column} are within tolerance')
            print('The magnetic field values in csv files satisfy test criteria')

    def test_04_PostProcessCCTGetDPOnly(self):
        """
            Check that post processing step defined in the .pro file can be run in GetDP. This is helper tests for debugging postprocessing step of GetDP
        """
        # arrange
        for model_name in self.model_names:
            p = tuh.Paths(model_name, '')
            FFs.prep_folder(p.test_outputs_folder)

            fdm = FFs.read_data_from_yaml(p.input_file, FDM)
            if fdm.magnet.type == 'CCT_straight':
                fdm.run.type = 'post_process_getdp_only'
                fdm.run.geometry = 1
                fdm.run.mesh = 1
                fdm.run.solution = 1

                # act
                main_fiqus = MainFiQuS(input_file_path=p.input_file, model_folder=p.model_folder, fdm=fdm)

                # assert
                model_df = pd.read_csv(os.path.join(main_fiqus.main_magnet.model_folder, 'Magnetic_energy.dat'))
                print(f"Magnetic_energy: {model_df}")
                model_df = pd.read_csv(os.path.join(main_fiqus.main_magnet.model_folder, 'Inductance.dat'))
                print(f"Inductance: {model_df}")

    def test_05_PostProcessMultipoleGetDPOnly(self):
        pass

    def test_06_PostProcessCCTPythonOnly(self):
        """
            Check that post processing of getdp ouput .pos file with magnetic field by python into csv file for LEDET is identical to the reference one
        """
        # arrange
        for model_name in self.model_names:
            p = tuh.Paths(model_name, '')
            FFs.prep_folder(p.test_outputs_folder)

            fdm = FFs.read_data_from_yaml(p.input_file, FDM)
            if fdm.magnet.type == 'CCT_straight':
                fdm.run.type = 'post_process_python_only'
                fdm.run.geometry = 1
                fdm.run.mesh = 1
                fdm.run.solution = 1

                # act
                main_fiqus = MainFiQuS(input_file_path=p.input_file, model_folder=p.model_folder, fdm=fdm)

                # assert
                print('Comparing magnetic field csv files')
                model_file = main_fiqus.main_magnet.model_file
                print(f'Model file: {model_file}')
                model_df = pd.read_csv(model_file)
                reference_file = os.path.join(p.references_folder, 'field_map_3D.csv')
                print(f'Reference file: {reference_file}')
                reference_df = pd.read_csv(reference_file)

                for column in reference_df:
                    if column in ['Bx [T]', 'By [T]', 'Bz [T]', 'Bl [T]', 'Bh [T]', 'Bw [T]']:
                        comp_abs_tol = 5e-3  # this is comparing averages, not very robust and needs improvement
                        print(f'Comparing {column} average absolute tolerance of {comp_abs_tol}')
                        comparison_result = np.isclose(model_df[column].mean(), reference_df[column].mean(), rtol=0, atol=comp_abs_tol, equal_nan=True)
                    else:
                        comp_abs_tol = 1e-9
                        print(f'Comparing {column} values with absolute tolerance of {comp_abs_tol}')
                        comparison_result = np.isclose(model_df[column], reference_df[column], rtol=0, atol=comp_abs_tol, equal_nan=True).all()
                    self.assertTrue(comparison_result)
                    print(f'Data in {column} are within tolerance')
                print('The magnetic field values in csv files satisfy test criteria')

                # assert        # this is done to improve coverage by testing ParserPOS. Test only if ParserPOS does not produce error.
                file_name = 'b_Omega_p.pos'
                model_file = os.path.join(main_fiqus.main_magnet.model_folder, file_name)
                print(f'Parsing file: {model_file}')
                ParserPOS(model_file)
                print(f'Parsing of {model_file} with ParserPOS was successful.')

    def test_07_PostProcessMultipolePythonOnly(self):
        """
            Check that post processing csv/map2d file for LEDET is identical to the reference one
        """
        # arrange
        for model_name in self.model_names:
            p = tuh.Paths(model_name, '')
            FFs.prep_folder(p.test_outputs_folder)

            fdm = FFs.read_data_from_yaml(p.input_file, FDM)
            if fdm.magnet.type == 'multipole':
                fdm.run.type = 'post_process_python_only'
                fdm.run.geometry = 1
                fdm.run.mesh = 1
                fdm.run.solution = 1

                # act
                main_fiqus = MainFiQuS(input_file_path=p.input_file, model_folder=p.model_folder, fdm=fdm)

                # assert
                p.reference_file = Path(f"{p.reference_file}map2d")
                print('Comparing map2d files')
                reference_map2d = Pars.parseMap2d(map2dFile=p.reference_file)
                output_map2d = Pars.parseMap2d(map2dFile=main_fiqus.main_magnet.model_file)
                comp_abs_tol = 5e-2
                for i, row in enumerate(reference_map2d):
                    print(f'Comparing values of row {i} with absolute tolerance of {comp_abs_tol}')
                    for j, entry in enumerate(row):
                        comparison_result = np.isclose(entry, output_map2d[i][j], rtol=0, atol=comp_abs_tol, equal_nan=True)
                        self.assertTrue(comparison_result)
                print('The magnetic field values in map2d files satisfy test criteria')

    def test_08_PostProcessMultipolePythonOnlyCompRoxie(self):
        """
            Check that post processing csv/map2d file for LEDET is identical to the reference one from ROXIE
        """
        # arrange
        for model_name in self.model_names:
            p = tuh.Paths(model_name, 'map2d')
            FFs.prep_folder(p.test_outputs_folder)

            fdm = FFs.read_data_from_yaml(p.input_file, FDM)

            if fdm.magnet.type == 'multipole':
                fdm.run.type = 'post_process_python_only'
                fdm.run.geometry = 1
                fdm.run.mesh = 1
                fdm.run.solution = 1
                fdm.magnet.postproc.compare_to_ROXIE = os.path.join(os.path.dirname(p.input_file), os.path.basename(p.model_file))

                # act
                main_fiqus = MainFiQuS(input_file_path=p.input_file, model_folder=p.model_folder, fdm=fdm)

                # assert
                print('Comparing map2d files')
                reference_map2d = Pars.parseMap2d(map2dFile=Path(os.path.join(p.references_folder, model_name + '_ROXIE.map2d')))
                output_map2d = Pars.parseMap2d(map2dFile=main_fiqus.main_magnet.model_file)
                comp_abs_tol = 5e-2
                for i, row in enumerate(reference_map2d):
                    print(f'Comparing values of row {i} with absolute tolerance of {comp_abs_tol}')
                    for j, entry in enumerate(row):
                        comparison_result = np.isclose(entry, output_map2d[i][j], rtol=0, atol=comp_abs_tol, equal_nan=True)
                        self.assertTrue(comparison_result)
                print('The magnetic field values in map2d files satisfy test criteria')

    def test_09_PostProcessMultipolePythonOnlyPlots(self):
        """
            Check that plots are produced correctly
        """
        # arrange
        for model_name in self.model_names:
            p = tuh.Paths(model_name, 'map2d')
            FFs.prep_folder(p.test_outputs_folder)

            fdm = FFs.read_data_from_yaml(p.input_file, FDM)

            if fdm.magnet.type == 'multipole':
                fdm.run.type = 'post_process_python_only'
                fdm.run.geometry = 1
                fdm.run.mesh = 1
                fdm.run.solution = 1
                fdm.magnet.postproc.compare_to_ROXIE = os.path.join(os.path.dirname(p.input_file), os.path.basename(p.model_file))
                fdm.magnet.postproc.plot_all = 'test'

                # act and assert
                MainFiQuS(input_file_path=p.input_file, model_folder=p.model_folder, fdm=fdm)
                print('The plotting functions satisfy test criteria')

    def test_10_TestGUILaunch(self):
        """
            Check if interactive gui can be launched
        """
        print('Initializing gmsh and launching graphical user interface. It will be open for 0.5 s')
        gu = GmshUtils('test', True)
        gu.initialize()
        user_name = getpass.getuser()
        if user_name != 'root':
            gu.launch_interactive_GUI(close_after=0.5)
        print('Gui was launched and closed successfully')





