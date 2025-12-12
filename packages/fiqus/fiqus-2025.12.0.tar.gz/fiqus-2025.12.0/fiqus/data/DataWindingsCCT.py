from pydantic import BaseModel
from typing import List, Optional


class Terminal(BaseModel):
    vol_st: Optional[List[int]] = None  # volume number for terminal in for straightening
    surf_st: Optional[List[int]] = None  # surface number for terminal in for straightening
    vol_et: Optional[List[int]] = None  # volume number for terminal in for extending
    surf_et: Optional[List[int]] = None  # surface number for terminal in for extending
    lc_st: Optional[List[List[List[int]]]] = None  # line connections for straightening terminals
    lc_et: Optional[List[List[List[int]]]] = None  # line connections for extending terminals
    z_air: Optional[float] = None
    z_add: Optional[float] = None
    ndpterms: Optional[List[int]] = None  # number of divisions per terminal


class Winding(BaseModel):
    names: Optional[List[str]] = None  # name to use in gmsh and getdp
    t_in: Terminal = Terminal()     # Terminal in
    t_out: Terminal = Terminal()    # Terminal in


class WindingsInformation(BaseModel):
    magnet_name: Optional[str] = None
    windings_avg_length: Optional[float] = None
    windings: Winding = Winding()
    w_names: Optional[List[str]] = None
    f_names: Optional[List[str]] = None
    formers: Optional[List[str]] = None
    air: Optional[str] = None


class SpliterBrep(BaseModel):  # Brep file model splitter data
    magnet_name: Optional[str] = None
    file_name: Optional[str] = None           # full file name for the brep file
    vol_firsts: Optional[List[int]] = None    # list of first volumes for the partitioned model
    vol_lasts: Optional[List[int]] = None      # list of last volumes for the partitioned model
