import unittest
from tests.utils.fiqus_test_classes import FiQuSGeometryTests


class TestGeometryGenerators(FiQuSGeometryTests):
    def test_Pancake3D(self):
        """
        Checks if Pancake3D geometry generators work correctly by comparing the number
        of entities in the generated geometry file to the reference file that was
        checked manually.
        """
        model_names = [
            "TEST_Pancake3D_REF",
            "TEST_Pancake3D_REFStructured",
            "TEST_Pancake3D_TSA",
            "TEST_Pancake3D_TSAStructured",
            "TEST_Pancake3D_TSAInsulating",
            "TEST_Pancake3D_TSAInsulatingJcVsLength"
        ]

        for model_name in model_names:
            with self.subTest(model_name=model_name):
                data_model = self.get_data_model(model_name)

                # data_model can be modified here if necessary
                # Example:

                # data_model.magnet.geometry.N = 3

                self.generate_geometry(data_model, model_name)

                # Compare the number of entities with the reference file:
                geometry_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name=model_name, file_extension="brep"
                )
                reference_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name=model_name, file_extension="brep"
                )
                self.compare_number_of_entities(geometry_file, reference_file)

                # Compare the volume information files:
                vi_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name=model_name, file_extension="vi"
                )
                reference_vi_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name=model_name, file_extension="vi"
                )
                self.compare_json_or_yaml_files(vi_file, reference_vi_file)

    def test_ConductorAC_Strand(self):
        """
        Checks if ConductorAC geometry generators work correctly by comparing the number
        of entities in the generated geometry file to the reference file that was
        checked manually.
        """
        model_names = [
            "TEST_CAC_Strand_adaptiveMesh",
            "TEST_CAC_Strand_hexFilaments",
            "TEST_CAC_wireInChannel",
        ]

        for model_name in model_names:
            with self.subTest(model_name=model_name):
                data_model = self.get_data_model(model_name)

                # data_model can be modified here if necessary
                # Example:

                # data_model.magnet.geometry.N = 3

                self.generate_geometry(data_model, model_name)

                # Compare the number of entities with the reference file:
                geometry_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name=model_name, file_extension="brep"
                )
                reference_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name=model_name, file_extension="brep"
                )
                self.compare_number_of_entities(geometry_file, reference_file)

                # Compare the Geometry YAML files:
                geometry_yaml_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name='GeometryModel', file_extension="yaml"
                )
                reference_geometry_yaml_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name='GeometryModel', file_extension="yaml"
                )
                print('Comparing:'
                      f'{geometry_yaml_file}'
                      ' with'
                      f'{reference_geometry_yaml_file}')
                self.compare_json_or_yaml_files(geometry_yaml_file, reference_geometry_yaml_file, tolerance=1e-9)

    def test_ConductorAC_Rutherford(self):
            model_names = [
                "TEST_CAC_Rutherford",
            ]

            for model_name in model_names:
                with self.subTest(model_name=model_name):
                    data_model = self.get_data_model(model_name)

                    self.generate_geometry(data_model, model_name)

                    # Compare the number of entities with the reference file:
                    geometry_file = self.get_path_to_generated_file(
                        data_model=data_model, file_name=model_name, file_extension="brep"
                    )
                    reference_file = self.get_path_to_reference_file(
                        data_model=data_model, file_name=model_name, file_extension="brep"
                    )
                    self.compare_number_of_entities(geometry_file, reference_file)

    def test_Multipole(self):
        """
        Checks if Multipole geometry generators work correctly by comparing generated
        geometry files to reference files that were checked manually.
        """
        model_names = [
            "TEST_MULTIPOLE_MBH_1in1_TSA_withQH",
            "TEST_MULTIPOLE_MBH_1in1_TSA",
            "TEST_MULTIPOLE_MBH_1in1_REF",
            "TEST_MULTIPOLE_SMC_TSA_withQH",
            "TEST_MULTIPOLE_SMC_TSA",
            "TEST_MULTIPOLE_SMC_REF",
            "TEST_MULTIPOLE_4COND_TSA",
        ]

        for model_name in model_names:
            with self.subTest(model_name=model_name):
                data_model = self.get_data_model(model_name)

                # data_model can be modified here if necessary
                # Example:

                # data_model.magnet.geometry.N = 3

                self.generate_geometry(data_model, model_name)

                thermal_model_name = f"{model_name}_TH"
                electromagnetic_model_name = f"{model_name}_EM"

                # Compare the number of entities with the reference file:
                geometry_file_EM = self.get_path_to_generated_file(
                    data_model=data_model, file_name=electromagnetic_model_name, file_extension="brep"
                )
                reference_file_EM = self.get_path_to_reference_file(
                    data_model=data_model, file_name=electromagnetic_model_name, file_extension="brep"
                )
                self.compare_number_of_entities(geometry_file_EM, reference_file_EM)

                geometry_file_TH = self.get_path_to_generated_file(
                    data_model=data_model, file_name=thermal_model_name, file_extension="brep"
                )
                reference_file_TH = self.get_path_to_reference_file(
                    data_model=data_model, file_name=thermal_model_name, file_extension="brep"
                )
                self.compare_number_of_entities(geometry_file_TH, reference_file_TH)

                # Compare the aux files:
                aux_file_EM = self.get_path_to_generated_file(
                    data_model=data_model, file_name=electromagnetic_model_name, file_extension="aux"
                )
                reference_aux_file_EM = self.get_path_to_reference_file(
                    data_model=data_model, file_name=electromagnetic_model_name, file_extension="aux"
                )
                self.compare_json_or_yaml_files(aux_file_EM, reference_aux_file_EM)

                aux_file_TH = self.get_path_to_generated_file(
                    data_model=data_model, file_name=thermal_model_name, file_extension="aux"
                )
                reference_aux_file_TH = self.get_path_to_reference_file(
                    data_model=data_model, file_name=thermal_model_name, file_extension="aux"
                )
                self.compare_json_or_yaml_files(aux_file_TH, reference_aux_file_TH)

                # Compare the strs files:
                strs_file_EM = self.get_path_to_generated_file(
                    data_model=data_model, file_name=electromagnetic_model_name, file_extension="strs"
                )
                reference_strs_file_EM = self.get_path_to_reference_file(
                    data_model=data_model, file_name=electromagnetic_model_name, file_extension="strs"
                )
                self.compare_json_or_yaml_files(strs_file_EM, reference_strs_file_EM)

                strs_file_TH = self.get_path_to_generated_file(
                    data_model=data_model, file_name=thermal_model_name, file_extension="strs"
                )
                reference_strs_file_TH = self.get_path_to_reference_file(
                    data_model=data_model, file_name=thermal_model_name, file_extension="strs"
                )
                self.compare_json_or_yaml_files(strs_file_TH, reference_strs_file_TH)

                # Compare the crns files:
                crns_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name=model_name, file_extension="crns"
                )
                reference_crns_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name=model_name, file_extension="crns"
                )
                self.compare_json_or_yaml_files(crns_file, reference_crns_file)

                # Compare the geometry yamls:
                geometry_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name="geometry", file_extension="yaml"
                )
                reference_geometry_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name="geometry", file_extension="yaml"
                )
                self.compare_json_or_yaml_files(geometry_file, reference_geometry_file, excluded_keys="geom_file_path")

if __name__ == "__main__":
    unittest.main()
