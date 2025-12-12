from pydantic import BaseModel, Field
from typing import Dict, List, Union, Literal, Optional, Any

from fiqus.data.DataModelCommon import EnergyExtraction, CLIQ_Class, ESC_Class, E_CLIQ_Class, QuenchDetection, Circuit_Class, PowerSupplyClass, QuenchHeater
from fiqus.data.DataConductor import Conductor
from fiqus.data.DataFiQuSCCT import CCT
from fiqus.data.DataFiQuSMultipole import Multipole
from fiqus.data.DataFiQuSPancake3D import Pancake3D
from fiqus.data.DataFiQuSConductorAC_Strand import CACStrand
from fiqus.data.DataFiQuSHomogenizedConductor import HomogenizedConductor
from fiqus.data.DataFiQuSConductorAC_Rutherford import CACRutherford

class RunFiQuS(BaseModel):
    """
    Class for FiQuS run
    """

    type: Literal[
        "start_from_yaml",
        "mesh_only",
        "geometry_only",
        "geometry_and_mesh",
        "pre_process_only",
        "mesh_and_solve_with_post_process_python",
        "solve_with_post_process_python",
        "solve_only",
        "post_process_getdp_only",
        "post_process_python_only",
        "post_process",
        "plot_python",
        "batch_post_process_python",
        "only_create_pro_file_from_mesh",
        "postprocess_veusz"
    ] = Field(
        default="start_from_yaml",
        title="Run Type of FiQuS",
        description="FiQuS allows you to run the model in different ways. The run type can be specified here. For example, you can just create the geometry and mesh or just solve the model with previous mesh, etc.",
    )
    geometry: Optional[Union[str, int]] = Field(
        default=None,
        title="Geometry Folder Key",
        description="This key will be appended to the geometry folder.",
    )
    mesh: Optional[Union[str, int]] = Field(
        default=None,
        title="Mesh Folder Key",
        description="This key will be appended to the mesh folder.",
    )
    solution: Optional[Union[str, int]] = Field(
        default=None,
        title="Solution Folder Key",
        description="This key will be appended to the solution folder.",
    )
    launch_gui: bool = Field(
        default=False,
        title="Launch GUI",
        description="If True, the GUI will be launched after the run.",
    )
    overwrite: bool = Field(
        default=False,
        title="Overwrite",
        description="If True, the existing folders will be overwritten, otherwise new folders will be created. NOTE: This setting has no effect for HTCondor runs.",
    )
    comments: str = Field(
        default="",
        title="Comments",
        description="Comments for the run. These comments will be saved in the run_log.csv file.",
    )
    verbosity_Gmsh: int = Field(
        default=5,
        title="verbosity_Gmsh",
        description="Level of information printed on the terminal and the message console (0: silent except for fatal errors, 1: +errors, 2: +warnings, 3: +direct, 4: +information, 5: +status, 99: +debug)",
    )
    verbosity_GetDP: int = Field(
        default=5,
        title="verbosity_GetDP",
        description="Level of information printed on the terminal and the message console. Higher number prints more, good options are 5 or 6.",
    )
    verbosity_FiQuS: bool = Field(
        default=True,
        title="verbosity_FiQuS",
        description="Level of information printed on the terminal and the message console by FiQuS. Only True of False for now.",
    )


class GeneralFiQuS(BaseModel):
    """
    Class for FiQuS general
    """

    magnet_name: Optional[str] = None


# class QuenchHeaters(BaseModel):
#     """
#     Level 3: Class for FiQuS
#     """

#     N_strips: Optional[int] = None  # set to 0 to avoid building quench heater thin shells
#     t_trigger: Optional[List[float]] = None
#     U0: Optional[List[float]] = None
#     C: Optional[List[float]] = None
#     R_warm: Optional[List[float]] = None
#     w: Optional[List[float]] = None
#     h: Optional[List[float]] = None
#     h_ins: List[List[float]] = []
#     type_ins: List[List[str]] = []
#     h_ground_ins: List[List[float]] = []
#     type_ground_ins: List[List[str]] = []
#     l: Optional[List[float]] = None
#     l_copper: Optional[List[float]] = None
#     l_stainless_steel: Optional[List[float]] = None
#     ids: Optional[List[int]] = None
#     turns: Optional[List[int]] = None
#     turns_sides: Optional[List[str]] = None



class QuenchProtection(BaseModel):
    """
    Level 2: Class for FiQuS
    """

    energy_extraction: EnergyExtraction = EnergyExtraction()
    quench_heaters: QuenchHeater = QuenchHeater()
    cliq: CLIQ_Class = CLIQ_Class()
    esc: ESC_Class = ESC_Class()
    e_cliq: E_CLIQ_Class = E_CLIQ_Class()


class SolveDumpDataModel(BaseModel):
    solve: Any      # this is populated with magnet.solve section in MainFiQuS when dumping the yaml file for reference. The is no information on type in the solve section, so going for "Any" here
    circuit: Circuit_Class = Circuit_Class()
    power_supply: PowerSupplyClass = PowerSupplyClass()
    quench_protection: QuenchProtection = QuenchProtection()
    quench_detection: QuenchDetection = QuenchDetection()
    conductors: Dict[Optional[str], Conductor] = {}


class FDM(BaseModel):
    """
    Class for FiQuS
    """

    general: GeneralFiQuS = GeneralFiQuS()
    run: RunFiQuS = RunFiQuS()
    magnet: Union[Multipole, CCT, Pancake3D, CACStrand, HomogenizedConductor, CACRutherford] = Field(
        default=Multipole(), discriminator="type"
    )
    circuit: Circuit_Class = Circuit_Class()
    power_supply: PowerSupplyClass = PowerSupplyClass()
    quench_protection: QuenchProtection = QuenchProtection()
    quench_detection: QuenchDetection = QuenchDetection()
    conductors: Dict[Optional[str], Conductor] = {}
