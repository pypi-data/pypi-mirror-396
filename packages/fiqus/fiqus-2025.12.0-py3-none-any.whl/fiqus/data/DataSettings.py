from typing import Literal, Optional

from pydantic import BaseModel, Field


class Condor(BaseModel):
    """
    Class for running using HTCondor queuing (only on Linux)
    """

    error: Optional[str] = Field(
        default=None,
        title="error",
        description="Error file name and extension, like error.txt",
    )
    output: Optional[str] = Field(
        default=None,
        title="output",
        description="Output file name and extension, like output.txt",
    )
    log: Optional[str] = Field(
        default=None,
        title="log",
        description="Log file name and extension, like log.txt",
    )
    request_cpus: Optional[int] = Field(
        default=None,
        title="request_cpus",
        description="Number of CPUs to request on each machine",
    )
    request_memory: Optional[str] = Field(
        default=None,
        title="request_memory",
        description="Amount of memory to request on each machine as a string (e.g., '16G')",
    ) 
    request_disk: Optional[str] = Field(
        default=None,
        title="request_disk",
        description="Amount of disk space to request on each machine as a string (e.g., '16G')",
    )
    singularity_image_path: Optional[str] = Field(
        default=None,
        title="SingularityImagePath",
        description="Full path to Singularity image",
    )
    cerngetdp_version: Optional[str] = Field(
        default=None,
        title="CERNGetDP Version",
        description="Version of CERNGetDP to be used",
    )
    should_transfer_files: Literal["YES", "NO"] = Field(
        default="YES",
        title="should_transfer_files",
        description="Sets if files should be transferred",
    )
    max_run_time: Optional[int] = Field(
        default=None,
        title="MaxRuntime",
        description=(
            "Specifies maximum run time in seconds to request for the job to go into"
            " the queue"
        ),
    )
    eos_relative_output_path: Optional[str] = Field(
        default=None,
        title="eos_relative_output_path",
        description=(
            "This is relative path in the user eos folder. This path gets appended to"
            " the root path: root://eosuser.cern.ch//eos/user/u/username"
        ),
    )
    big_mem_job: Optional[bool] = Field(
        default=None,
        title="BigMemJob",
        description=(
            "If true a machine with 1TB of RAM and 24 cores is requested. Expect longer"
            " queuing time"
        ),
    )

class Subproc(BaseModel):
    """
    Class for running using subprocess calls (on Windows)
    """

    executable: Optional[str] = Field(
        default=None,
        title="executable",
        description="Executable or script to run, like run_fiqus.py",
    )
    full_output_path: Optional[str] = Field(
        default=None,
        title="full_output_path",
        description="A full path to the output folder",
    )


class DataSettings(BaseModel):
    """
    Configuration for HTCondor and
    """

    GetDP_path: Optional[str] = Field(
        default=None,
        title="GetDP_path",
        description=(
            "Full path to GetDP executable. This is only needed and used on Windows"
        ),
    )

    base_path_model_files: Optional[str] = Field(
        default=None,
        title="base_path_model_files",
        description=(
            "Path to the base model folder where model files are stored that are needed to run FiQuS."
            "This is only needed when the files are not in the same folder as the input yaml (e.g., on HTCondor)"
        )
    )

    htcondor: Condor = Condor()
    subproc: Subproc = Subproc()