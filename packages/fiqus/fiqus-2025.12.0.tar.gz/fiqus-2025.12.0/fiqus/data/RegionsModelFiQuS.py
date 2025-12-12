from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Literal


class Region(BaseModel):
    name: Optional[str] = None
    number: Optional[int] = None


class Regions(BaseModel):
    names: Optional[List[str]] = None
    numbers: Optional[List[int]] = None


class Regions2(BaseModel):
    names: Optional[List[List[str]]] = None
    numbers: Optional[List[List[int]]] = None


class TwoParBoundaryRegions(Regions2):
    values: Optional[List[List[Union[float, str]]]] = None


class TwoParBoundaryRegions2(Regions):
    values: Optional[List[Union[float, str]]] = None


class OneParBoundaryRegions(Regions2):
    value: Optional[List[float]] = None

class InducedRegions(Regions):
    sigmas: Optional[List[float]] = None
    mu_rs: Optional[List[float]] = None


class PoweredRegions(InducedRegions):
    currents: Optional[List[float]] = None


class InsulatorRegions(InducedRegions):
    pass # duplicate class


class IronRegions(InducedRegions):
    pass # duplicate class


class AirRegion(Region):
    sigma: Optional[float] = None
    mu_r: Optional[float] = None


class AirFarFieldRegions(Regions):
    radius_in: Optional[float] = None
    radius_out: Optional[float] = None


class NonPermeableSourceRegion(AirRegion):
    pass # duplicate class


class SourceFreeRegion(AirRegion):
    pass # duplicate class


class Iron(BaseModel):
    vol: IronRegions = IronRegions()  # volume region
    surf: Regions = Regions()  # surface region
    curves: Dict[str, List[str]] = {}  # curves region


class Induced(BaseModel):
    vol: InducedRegions = InducedRegions()  # volume region
    surf_th: Regions = Regions()  # surface region
    surf_in: Regions = Regions()  # input terminal surface region
    surf_out: Regions = Regions()  # output terminal surface region
    cochain: Regions = Regions()  # winding cochain (cut)

class Insulator(BaseModel):
    vol: InsulatorRegions = InsulatorRegions()  # volume region
    surf: Regions = Regions()  # surface region
    curve: Regions = Regions()  # curve region

class Powered(Induced, Insulator):
    vol: PoweredRegions = PoweredRegions()  # volume region
    vol_in: Region = Region()  # input terminal volume region
    vol_out: Region = Region()  # output terminal volume region
    conductors: Dict[str, List[str]] = {}  # conductor types
    surf_insul: Regions = Regions()  # turn-to-turn insulation surfaces


class Air(BaseModel):
    vol: AirRegion = AirRegion()  # volume region
    surf: Region = Region()  # surface region
    line: Region = Region()  # line region
    point: Regions = Regions()  # point region
    cochain: Regions = Regions()  # air cochain (cut)


class AirFarField(BaseModel):
    vol: AirFarFieldRegions = AirFarFieldRegions()  # volume region
    surf: Region = Region()  # surface region


class NonPermeableSource(BaseModel):
    vol: NonPermeableSourceRegion = NonPermeableSourceRegion()  # volume region
    surf: Region = Region()  # surface region


class SourceFree(BaseModel):
    vol: SourceFreeRegion = SourceFreeRegion()  # volume region
    surf: Region = Region()  # surface region

class RobinCondition_collar(BaseModel):
    bc: TwoParBoundaryRegions2 = TwoParBoundaryRegions2()

class RobinCondition_grouped(BaseModel):
    bc: TwoParBoundaryRegions = TwoParBoundaryRegions()
    groups: Dict[str, List[int]] = {}

class NeumannCondition_grouped(BaseModel):
    bc: OneParBoundaryRegions = OneParBoundaryRegions()
    groups: Dict[str, List[int]] = {}

class DirichletCondition_grouped(BaseModel):
    bc: OneParBoundaryRegions = OneParBoundaryRegions()
    groups: Dict[str, List[int]] = {}


class ThermalBoundaryConditions(BaseModel):
    temperature: DirichletCondition_grouped = DirichletCondition_grouped()
    heat_flux: NeumannCondition_grouped = NeumannCondition_grouped()
    cooling: RobinCondition_grouped = RobinCondition_grouped()
    collar: RobinCondition_collar = RobinCondition_collar()


class SymmetryBoundaryConditions(BaseModel):
    normal_free: Region = Region()
    tangential_free: Region = Region()


class BoundaryConditions(BaseModel):
    thermal: ThermalBoundaryConditions = ThermalBoundaryConditions()
    symmetry: SymmetryBoundaryConditions = SymmetryBoundaryConditions()


class InsulationType(BaseModel):
    layers_number: List[int] = []
    thin_shells: List[List[int]] = []
    layers_material: List[List[str]] = []
    thicknesses: List[List[float]] = []
    correction_factors: List[float] = [] # same correction factor per group. Can be used to scale the thin shell length
    label: List[List[Union[int, None]]] = (
        []
    )  # useful to indicate which quench heater a SS element refers to


class ThinShell(BaseModel):
    groups: Dict[str, List[int]] = {} # -> Checkboard convention of the hts
    mid_turns_layers_poles: Optional[List[int]] = None # indices of midlayers between HT, layers and poles
    ts_collar_groups: Dict[str, List[int]] = {} # groups of mid collar thin shells -> Checkboard convention
    ts_pole_groups: Dict[str, List[int]] = {} # groups of mid collar thin shells -> Checkboard convention

    second_group_is_next: Dict[str, List[int]] = {}
    normals_directed: Dict[str, List[int]] = {}
    bdry_curves: Dict[Literal["collar", "poles", "outer_collar"], List[int]] = {} # save the boundary curves of a specific region, used in TSA

    # insulation types, only mid layers
    insulation_types: InsulationType = InsulationType() # todo: merge all types into one @emma, consider dict ?
    quench_heaters: InsulationType = InsulationType()
    collar: InsulationType = InsulationType()
    poles: InsulationType = InsulationType()

class PostProc(BaseModel):
    vol: Regions = Regions()  # postprocessing volumes general
    surf: Regions = Regions()  # postprocessing volumes general
    line: Regions = Regions()  # postprocessing volumes general
    point: Regions = Regions()  # postprocessing volumes general


class RegionsModel(BaseModel):
    powered: Dict[str, Powered] = {} #coils
    induced: Dict[str, Induced] = {} #wedges
    insulator: Insulator = Insulator()
    iron_yoke: Iron = Iron() # iron yoke
    collar: Iron = Iron() # collar is a type of iron region
    ref_mesh: Iron = Iron()  # reference mesh
    poles: Iron = Iron()  # poles

    air: Air = Air()
    air_far_field: AirFarField = AirFarField()
    thin_shells: ThinShell = ThinShell() # Includes collar thin shells
    projection_points: Region = Region()
    boundaries: BoundaryConditions = BoundaryConditions()
    postproc_th: PostProc = PostProc()
    postproc_em: PostProc = PostProc()

