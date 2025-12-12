import unittest
from tests.utils.fiqus_test_classes import FiQuSMeshTests


class TestMeshGenerators(FiQuSMeshTests):
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

                # data_model.magnet.mesh.wi.axne = 30

                self.generate_mesh(data_model, model_name)

                # Compare the number of entities with the reference file:
                mesh_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name=model_name, file_extension="msh"
                )
                reference_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name=model_name, file_extension="msh"
                )
                self.compare_mesh_qualities(mesh_file, reference_file)

                # Compare the regions files:
                regions_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="regions",
                )
                reference_regions_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="regions",
                )
                self.compare_json_or_yaml_files(regions_file, reference_regions_file)

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

                # data_model.magnet.mesh.wi.axne = 30

                self.generate_mesh(data_model, model_name)

                # Compare the number of entities with the reference file:
                mesh_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name=model_name, file_extension="msh"
                )
                reference_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name=model_name, file_extension="msh"
                )
                self.compare_mesh_qualities(mesh_file, reference_file)

                # Compare the regions files:
                regions_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="regions",
                )
                reference_regions_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="regions",
                )
                print('Comparing'
                      f'{regions_file}'
                      'with'
                      f'{reference_regions_file}'
                      )
                self.compare_json_or_yaml_files(regions_file, reference_regions_file)

    def test_ConductorAC_Rutherford(self):
        """
        Checks if mesh generators work correctly by comparing the number
        of entities in the generated geometry file to the reference file that was
        checked manually.
        """
        model_names = [
            "TEST_CAC_Rutherford",
        ]

        for model_name in model_names:
            with self.subTest(model_name=model_name):
                data_model = self.get_data_model(model_name)

                self.generate_mesh(data_model, model_name)

                # Compare the number of entities with the reference file:
                mesh_file = self.get_path_to_generated_file(
                    data_model=data_model, file_name=model_name, file_extension="msh"
                )
                reference_file = self.get_path_to_reference_file(
                    data_model=data_model, file_name=model_name, file_extension="msh"
                )
                self.compare_mesh_qualities(mesh_file, reference_file)

                # Compare the regions files:
                regions_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="regions",
                )
                reference_regions_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="regions",
                )
                self.compare_json_or_yaml_files(regions_file, reference_regions_file)

    # def test_CCT(self):
    #     """
    #     Checks if CCT geometry generators work correctly by comparing the number
    #     of entities in the generated geometry file to the reference file that was
    #     checked manually.
    #     """
    #     model_names = [
    #         "MCBRD_2d2a_2n2a_0i",
    #     ]

    #     for model_name in model_names:
    #         with self.subTest(model_name=model_name):
    #             data_model = self.get_data_model(model_name)

    #             # data_model can be modified here if necessary
    #             # Example:

    #             # data_model.magnet.mesh.wi.axne = 30

    #             self.generate_mesh(data_model, model_name)

    #             # Compare the number of entities with the reference file:
    #             mesh_file = self.get_path_to_generated_file(
    #                 data_model=data_model, file_name=model_name, file_extension="msh"
    #             )
    #             reference_file = self.get_path_to_reference_file(
    #                 data_model=data_model, file_name=model_name, file_extension="msh"
    #             )
    #             self.compare_mesh_qualities(mesh_file, reference_file)


    def test_Multipole(self):
        """
        Checks if Multipole mesh generators work correctly by comparing against
        reference files that were checked manually.
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

                is_TSA = "TSA" in model_name

                self.generate_mesh(data_model, model_name)

                thermal_model_name = f"{model_name}_TH"
                electromagnetic_model_name = f"{model_name}_EM"

                # Compare mesh qualities with the reference file:
                mesh_file_EM = self.get_path_to_generated_file(
                    data_model=data_model, file_name=electromagnetic_model_name, file_extension="msh"
                )
                reference_file_EM = self.get_path_to_reference_file(
                    data_model=data_model, file_name=electromagnetic_model_name, file_extension="msh"
                )
                self.compare_mesh_qualities(mesh_file_EM, reference_file_EM)

                mesh_file_TH = self.get_path_to_generated_file(
                    data_model=data_model, file_name=thermal_model_name, file_extension="msh"
                )
                reference_file_TH = self.get_path_to_reference_file(
                    data_model=data_model, file_name=thermal_model_name, file_extension="msh"
                )
                self.compare_mesh_qualities(mesh_file_TH, reference_file_TH)

                # Compare the reg files:
                regions_file_EM = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=electromagnetic_model_name,
                    file_extension="reg",
                )
                reference_regions_file_EM = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=electromagnetic_model_name,
                    file_extension="reg",
                )
                self.compare_json_or_yaml_files(regions_file_EM, reference_regions_file_EM)

                regions_file_TH = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=thermal_model_name,
                    file_extension="reg",
                )
                reference_regions_file_TH = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=thermal_model_name,
                    file_extension="reg",
                )
                self.compare_json_or_yaml_files(regions_file_TH, reference_regions_file_TH)

                # Compare the aux files:
                aux_file_EM = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=electromagnetic_model_name,
                    file_extension="aux",
                )
                reference_aux_file_EM = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=electromagnetic_model_name,
                    file_extension="aux",
                )
                self.compare_json_or_yaml_files(aux_file_EM, reference_aux_file_EM)

                aux_file_TH = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=thermal_model_name,
                    file_extension="aux",
                )
                reference_aux_file_TH = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=thermal_model_name,
                    file_extension="aux",
                )
                self.compare_json_or_yaml_files(aux_file_TH, reference_aux_file_TH)

                if is_TSA:
                    # Compare the reco file:
                    reco_file = self.get_path_to_generated_file(
                        data_model=data_model,
                        file_name=thermal_model_name,
                        file_extension="reco",
                    )
                    reference_reco_file = self.get_path_to_reference_file(
                        data_model=data_model,
                        file_name=thermal_model_name,
                        file_extension="reco",
                    )
                    self.compare_json_or_yaml_files(reco_file, reference_reco_file)

                # Compare the mesh.yaml file:
                mesh_yaml_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="mesh",
                    file_extension="yaml",
                )
                reference_mesh_yaml_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="mesh",
                    file_extension="yaml",
                )
                self.compare_json_or_yaml_files(mesh_yaml_file, reference_mesh_yaml_file)


if __name__ == "__main__":
    unittest.main()
