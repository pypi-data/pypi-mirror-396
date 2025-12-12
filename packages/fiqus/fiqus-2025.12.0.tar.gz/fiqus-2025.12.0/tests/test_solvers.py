import unittest
from tests.utils.fiqus_test_classes import FiQuSSolverTests
from fiqus.data.DataFiQuS import FDM
import fiqus.data.DataFiQuSPancake3D as Pancake3D
import os
import platform
from pathlib import Path

linux_getdp_prefix_path = Path("/bin/cerngetdp/")
windows_getdp_prefix_path = Path("C:/cerngetdp/")


class TestSolvers(FiQuSSolverTests):
    def test_Pancake3D(self):
        """
        Checks if Pancake3D solvers work correctly by comparing the results to the
        reference results that were checked manually.
        """
        if os.getenv("CERNGETDP_VERSION_PANCAKE3D") is not None:
            os_name = platform.system()

            if os_name == "Linux":
                self.getdp_path = linux_getdp_prefix_path / Path(f"pancake3d/bin/getdp_{os.getenv('CERNGETDP_VERSION_PANCAKE3D')}")
            else:
                self.getdp_path = windows_getdp_prefix_path / Path(f"pancake3d/getdp_{os.getenv('CERNGETDP_VERSION_PANCAKE3D')}.exe")
        else:
            print("CERNGETDP_VERSION_PANCAKE3D is not set. Using default getdp path from data settings.")

        model_names = [
            "TEST_Pancake3D_REF",
            "TEST_Pancake3D_REFStructured",
            "TEST_Pancake3D_TSA",
            "TEST_Pancake3D_TSAStructured",
            "TEST_Pancake3D_TSAInsulating",
            "TEST_Pancake3D_TSAInsulatingJcVsLength",
            "TEST_Pancake3D_TSAInsulatingJcVsLength_thermalOnly",
        ]
        solve_types = ["electromagnetic", "weaklyCoupled", "stronglyCoupled", "thermal"]
        for model_name in model_names:
            for solve_type in solve_types:

                if solve_type == "thermal" and not model_name =="TEST_Pancake3D_TSAInsulatingJcVsLength_thermalOnly":
                    continue

                if solve_type != "thermal" and model_name =="TEST_Pancake3D_TSAInsulatingJcVsLength_thermalOnly":
                    continue

                with self.subTest(model_name=model_name, solve_type=solve_type):
                    data_model: FDM = self.get_data_model(model_name)

                    data_model.magnet.solve.type = solve_type

                    data_model.run.solution = solve_type

                    if solve_type in ["weaklyCoupled", "stronglyCoupled"]:
                        data_model.magnet.solve.quantitiesToBeSaved = [
                            Pancake3D.Pancake3DSolveSaveQuantity(
                                quantity="magneticField",
                            ),
                            Pancake3D.Pancake3DSolveSaveQuantity(
                                quantity="currentDensity",
                            ),
                            Pancake3D.Pancake3DSolveSaveQuantity(
                                quantity="temperature",
                            ),
                        ]
                    elif solve_type == "electromagnetic":
                        data_model.magnet.solve.quantitiesToBeSaved = [
                            Pancake3D.Pancake3DSolveSaveQuantity(
                                quantity="magneticField",
                            ),
                            Pancake3D.Pancake3DSolveSaveQuantity(
                                quantity="currentDensity",
                            ),
                        ]
                    elif solve_type == "thermal":
                        data_model.magnet.solve.quantitiesToBeSaved = [
                            Pancake3D.Pancake3DSolveSaveQuantity(
                                quantity="temperature",
                            ),
                        ]

                    self.solve(data_model, model_name)

                    # Compare the pro files:
                    pro_file = self.get_path_to_generated_file(
                        data_model=data_model,
                        file_name=model_name,
                        file_extension="pro",
                    )
                    reference_pro_file = self.get_path_to_reference_file(
                        data_model=data_model,
                        file_name=model_name,
                        file_extension="pro",
                    )
                    self.compare_text_files(pro_file, reference_pro_file)

                    # Compare the results files:
                    if solve_type in ["electromagnetic", "weaklyCoupled", "stronglyCoupled"]:
                        pos_file = self.get_path_to_generated_file(
                            data_model=data_model,
                            file_name="MagneticField-DefaultFormat",
                            file_extension="pos",
                        )
                        reference_pos_file = self.get_path_to_reference_file(
                            data_model=data_model,
                            file_name="MagneticField-DefaultFormat",
                            file_extension="pos",
                        )
                        self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1e-3)

                    if solve_type in ["weaklyCoupled", "stronglyCoupled", "thermal"]:
                        pos_file = self.get_path_to_generated_file(
                            data_model=data_model,
                            file_name="Temperature-DefaultFormat",
                            file_extension="pos",
                        )
                        reference_pos_file = self.get_path_to_reference_file(
                            data_model=data_model,
                            file_name="Temperature-DefaultFormat",
                            file_extension="pos",
                        )
                        self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1e-3)

    def test_ConductorAC_Strand(self):
        """
        Checks if CACStrand solvers work correctly by comparing the results to the
        reference results that were checked manually.
        """
        if os.getenv("CERNGETDP_VERSION_CAC_STRAND") is not None:
            os_name = platform.system()

            if os_name == "Linux":
                self.getdp_path = linux_getdp_prefix_path / Path(f"cac_strand/bin/getdp_{os.getenv('CERNGETDP_VERSION_CAC_STRAND')}")
            else:
                self.getdp_path = windows_getdp_prefix_path / Path(f"cac_strand/getdp_{os.getenv('CERNGETDP_VERSION_CAC_STRAND')}.exe")
        else:
            print("CERNGETDP_VERSION_CAC_STRAND is not set. Using default getdp path from data settings.")


        model_names = [
            "TEST_CAC_Strand_hexFilaments",
            "TEST_CAC_Strand_adaptiveMesh",
            "TEST_CAC_wireInChannel",
        ]
        for model_name in model_names:
            with self.subTest(model_name=model_name):
                data_model: FDM = self.get_data_model(model_name)

                self.solve(data_model, model_name)

                # Compare the pro files: 
                pro_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="pro",
                )
                reference_pro_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="pro",
                )
                # This makes no sense as long as the development on the Strand model pro-template is ongoing ...
                # Comparing the field solutions should ensure solver consistency without relying on the exact template structure. Skipping the pro-templates for now ~ AG
                #self.compare_text_files(pro_file, reference_pro_file)

                # Compare the magnetic flux density files:
                pos_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="b_Omega",
                    file_extension="pos",
                )
                reference_pos_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="b_Omega",
                    file_extension="pos",
                )
                self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1e-10)

                # Compare the current density files:
                pos_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="j_OmegaC",
                    file_extension="pos",
                )
                reference_pos_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="j_OmegaC",
                    file_extension="pos",
                )
                self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1e-10)

    def test_ConductorAC_Rutherford(self):
        """
        Checks if CAC_Rutherford solver works correctly by comparing the results to the
        reference results that were checked manually.
        """
        if os.getenv("CERNGETDP_VERSION_CAC_RUTHERFORD") is not None:
            os_name = platform.system()

            if os_name == "Linux":
                self.getdp_path = linux_getdp_prefix_path / Path(f"cac_rutherford/bin/getdp_{os.getenv('CERNGETDP_VERSION_CAC_RUTHERFORD')}")
            else:
                self.getdp_path = windows_getdp_prefix_path / Path(f"cac_rutherford/getdp_{os.getenv('CERNGETDP_VERSION_CAC_RUTHERFORD')}.exe")
        else:
            print("CERNGETDP_VERSION_CAC_RUTHERFORD is not set. Using default getdp path from data settings.")


        model_names = [
            "TEST_CAC_Rutherford",
        ]
        for model_name in model_names:
            with self.subTest(model_name=model_name):
                data_model: FDM = self.get_data_model(model_name)

                self.solve(data_model, model_name)

                # Compare the current density files:
                pos_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="jz",
                    file_extension="pos",
                )
                reference_pos_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="jz",
                    file_extension="pos",
                )
                self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1E-10)

                # Compare the power loss files:
                pos_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="m",
                    file_extension="pos",
                )
                reference_pos_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="m",
                    file_extension="pos",
                )
                self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1E-10)

    def test_HomogenizedConductor(self):
        """
        Checks if HomogenizedConductor solver works correctly by comparing the results to the
        reference results that were checked manually.
        """
        if os.getenv("CERNGETDP_VERSION_HOMOGENIZED_CONDUCTOR") is not None:
            os_name = platform.system()

            if os_name == "Linux":
                self.getdp_path = linux_getdp_prefix_path / Path(f"homogenized_conductor/bin/getdp_{os.getenv('CERNGETDP_VERSION_HOMOGENIZED_CONDUCTOR')}")
            else:
                self.getdp_path = windows_getdp_prefix_path / Path(f"homogenized_conductor/getdp_{os.getenv('CERNGETDP_VERSION_HOMOGENIZED_CONDUCTOR')}.exe")
        else:
            print("CERNGETDP_VERSION_HOMOGENIZED_CONDUCTOR is not set. Using default getdp path from data settings.")

        model_names = [
            "TEST_HomogenizedConductor",
        ]
        for model_name in model_names:
            with self.subTest(model_name=model_name):
                data_model: FDM = self.get_data_model(model_name)

                self.solve(data_model, model_name)

                # Compare the current density files:
                pos_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="js",
                    file_extension="pos",
                )
                reference_pos_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="js",
                    file_extension="pos",
                )
                self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1E-10)

                # Compare the power loss files:
                pos_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="p_tot",
                    file_extension="pos",
                )
                reference_pos_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="p_tot",
                    file_extension="pos",
                )
                self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1E-10)

    def test_Multipole(self):
        """
        Checks if Multipole solvers work correctly by comparing the results to the
        reference results that were checked manually.
        """
        if os.getenv("CERNGETDP_VERSION_MULTIPOLE") is not None:
            os_name = platform.system()

            if os_name == "Linux":
                self.getdp_path = linux_getdp_prefix_path / Path(f"multipole/bin/getdp_{os.getenv('CERNGETDP_VERSION_MULTIPOLE')}")
            else:
                self.getdp_path = windows_getdp_prefix_path / Path(f"multipole/getdp_{os.getenv('CERNGETDP_VERSION_MULTIPOLE')}.exe")
        else:
            print("CERNGETDP_VERSION_MULTIPOLE is not set. Using default getdp path from data settings.")

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
                data_model: FDM = self.get_data_model(model_name)

                self.solve(data_model, model_name)

                # Compare the pro files: 
                pro_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="pro",
                )
                reference_pro_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name=model_name,
                    file_extension="pro",
                )
                
                self.compare_text_files(pro_file, reference_pro_file, exclude_lines_keywords=["NameOfMesh"], exclude_first_n_lines=1)

                # Compare the magnetic flux density files:
                pos_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="b_Omega",
                    file_extension="pos",
                )
                reference_pos_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="b_Omega",
                    file_extension="pos",
                )
                self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1e-2)

                # Compare the temperature files:
                pos_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="T_Omega_c",
                    file_extension="pos",
                )
                reference_pos_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="T_Omega_c",
                    file_extension="pos",
                )
                self.compare_pos_files(pos_file, reference_pos_file, rel_tolerance=1e-3, abs_tolerance=1e-2)

                # Compare the solve yaml files
                solve_file = self.get_path_to_generated_file(
                    data_model=data_model,
                    file_name="solve",
                    file_extension="yaml",
                )
                reference_solve_file = self.get_path_to_reference_file(
                    data_model=data_model,
                    file_name="solve",
                    file_extension="yaml",
                )
                self.compare_json_or_yaml_files(solve_file, reference_solve_file)


if __name__ == "__main__":
    unittest.main()
