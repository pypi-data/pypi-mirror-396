import os
import shutil
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))) # Add the path to the fiqus package to the system path
from fiqus.data.DataFiQuS import FDM
from fiqus.utils.Utils import FilesAndFolders as Util
from fiqus import MainFiQuS as mf


# Generate reference files for the models below:
model_names = [
    "TEST_CAC_Strand_adaptiveMesh",
    "TEST_CAC_Strand_hexFilaments",
    "TEST_CAC_wireInChannel",
]
# The run types for the models above:
run_types = [
    'geometry_and_mesh', 
    'start_from_yaml', 
    'start_from_yaml',
]

for model_name, run_type in zip(model_names, run_types):
    # get path to the input file:
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

    # if the output folder exists, remove it:
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    # Create the output folder:
    os.makedirs(output_folder)

    # Cast input yaml file to FDM
    data_model: FDM = Util.read_data_from_yaml(input_file, FDM)

    data_model.run.overwrite = True

    # Make the run type start_from_yaml:
    data_model.run.type = run_type

    fiqus_instance = mf.MainFiQuS(
        fdm=data_model, model_folder=output_folder, input_file_path=input_file
    )

    # remove fiqus_instance to avoid memory issues:
    del fiqus_instance
