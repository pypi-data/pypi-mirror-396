import os
import shutil

import fiqus.data.DataFiQuSPancake3D as Pancake3D
from fiqus.data.DataFiQuS import FDM
from fiqus.utils.Utils import FilesAndFolders as Util
from fiqus import MainFiQuS as mf


# Generate reference files for the models below:
model_names = [
    "TEST_Pancake3D_REF",
    "TEST_Pancake3D_REFStructured",
    "TEST_Pancake3D_TSA",
    "TEST_Pancake3D_TSAStructured",
    "TEST_Pancake3D_TSAInsulating"
]

for model_name in model_names:
    input_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "_inputs",
        model_name,
        f"{model_name}.yaml",
    )
    # select _references folder as the output folder:
    output_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "_references", model_name
    )

    # Cast input yaml file to FDM
    data_model: FDM = Util.read_data_from_yaml(input_file, FDM)

    data_model.run.overwrite = True
    data_model.run.launch_gui = False

    # if the output folder exists, remove it and create a new one:
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        # Create the output folder:
        os.makedirs(output_folder)

    # Solve the same model three times with different solve types:
    solve_types = [
        "weaklyCoupled",
        "stronglyCoupled",
        "electromagnetic",
    ]
    for i, solve_type in enumerate(solve_types):
        if i == 0:
            # Make the run type start_from_yaml:
            data_model.run.type = "start_from_yaml"
        else:
            # Make the run type solve_only:
            data_model.run.type = "solve_only"

        # data_model.run.type = "post_process"
        # data_model.run.type = "solve_only"

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

        fiqus_instance = mf.MainFiQuS(fdm=data_model, model_folder=output_folder)

        # remove fiqus_instance to avoid memory issues:
        del fiqus_instance

        # # remove logs directory and run_log.csv inside the output folder:
        # shutil.rmtree(os.path.join(output_folder, "logs"))
        # os.remove(os.path.join(output_folder, "run_log.csv"))
