from pydantic import BaseModel
from typing import Dict, List, Tuple, Optional


class Coord(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None


class Area(BaseModel):
    loop: Optional[int] = None
    surface: Optional[int] = None


class Region(BaseModel):
    points: Dict[str, int] = {}
    lines: Dict[str, int] = {}
    areas: Dict[str, Area] = {}


# class CableInsulated(BaseModel):
#     type: #Literal['Insulated']
#     insulated: Region = Region()
#
#
# class CableBare(BaseModel):
#     type: #Literal['Bare']
#     bare: Region = Region()
#     insulation: Region = Region()


class BlockData(BaseModel):
    half_turns: Region = (
        Region()
    )  # Union[CableInsulated, CableBare] = {'type': 'Insulated'}
    insulation: Region = Region()
    current_sign: Optional[int] = None


class Block(BaseModel):
    blocks: Dict[int, BlockData] = {}
    conductor_name: Optional[str] = None
    conductors_number: Optional[int] = None


class Winding(BaseModel):
    windings: Dict[int, Block] = {}


class Layer(BaseModel):
    layers: Dict[int, Winding] = {}


class Pole(BaseModel):
    poles: Dict[int, Layer] = {}
    type: Optional[str] = None
    bore_center: Coord = Coord()


class Order(BaseModel):
    coil: Optional[int] = None
    pole: Optional[int] = None
    layer: Optional[int] = None
    winding: Optional[int] = None
    block: Optional[int] = None


class AnticlockwiseOrder(BaseModel):
    pole: Optional[int] = None
    winding: Optional[int] = None
    block: Optional[int] = None


class MidLayer(BaseModel):
    half_turn_lists: Dict[str, List[int]] = {}
    point_angles: Dict[str, float] = {}
    mid_layers: Region = Region()


class Iron(BaseModel):
    quadrants: Dict[int, Region] = {}
    max_radius: float = 0.0


class LayerOrder(BaseModel):
    layers: Dict[int, List[AnticlockwiseOrder]] = {}


class CoilOrder(BaseModel):
    coils: Dict[int, LayerOrder] = {}


class Coil(BaseModel):
    coils: Dict[int, Pole] = {}
    physical_order: List[Order] = []
    anticlockwise_order: CoilOrder = CoilOrder()
    concentric_coils: Dict[Tuple[float, float], List[int]] = {}
    max_radius: float = 0.0


class InsulationThickness(BaseModel):
    mid_pole: Dict[str, float] = {}
    mid_layer: Dict[str, float] = {}
    mid_winding: Dict[str, float] = {}


class ThinShell(BaseModel):
    mid_layers_ht_to_ht: Dict[str, MidLayer] = {}
    mid_layers_wdg_to_ht: Dict[str, Region] = {}
    mid_layers_ht_to_wdg: Dict[str, Region] = {}
    mid_layers_wdg_to_wdg: Dict[str, Region] = {}
    mid_poles: Dict[str, Region] = {}
    mid_windings: Dict[str, Region] = {}
    mid_turn_blocks: Dict[str, Region] = {}
    mid_wedge_turn: Dict[str, Region] = {}
    mid_layers_aux: Dict[str, Region] = {}
    ins_thickness: InsulationThickness = InsulationThickness()


class WedgeRegion(BaseModel):
    wedges: Dict[int, Region] = {}
    block_prev: Dict[int, int] = {}
    block_next: Dict[int, int] = {}


class WedgeLayer(BaseModel):
    layers: Dict[int, WedgeRegion] = {}


class Wedge(BaseModel):
    coils: Dict[int, WedgeLayer] = {}


class InsulationRegion(BaseModel):
    ins: Region = Region()
    blocks: List[List[int]] = []
    wedges: List[List[int]] = []


class InsulationGroup(BaseModel):
    group: Dict[int, InsulationRegion] = {}


class Insulation(BaseModel):
    coils: Dict[int, InsulationGroup] = {}


class Geometry(BaseModel):
    coil: Coil = Coil()
    iron: Iron = Iron()
    wedges: Wedge = Wedge()
    air: Region = Region()
    air_inf: Region = Region()
    symmetric_boundaries: Region = Region()
    thin_shells: ThinShell = ThinShell()
    insulation: Insulation = Insulation()


# Domain classes #
class MidLayerLine(BaseModel):
    inner: Dict[str, int] = {}
    outer: Dict[str, int] = {}


class GroupType(BaseModel):
    curves: Dict[str, int] = {}
    surfaces: Dict[str, int] = {}


class PoweredGroup(BaseModel):
    tag: Optional[int] = None
    group: Optional[str] = None
    lines: Dict[str, int] = {}
    mid_layer_lines: MidLayerLine = MidLayerLine()
    mid_pole_lines: Dict[str, int] = {}
    mid_winding_lines: Dict[str, int] = {}
    mid_turn_lines: Dict[str, int] = {}
    aux_lines: Dict[str, int] = {}


class WedgeGroup(BaseModel):
    tag: Optional[int] = None
    group: Optional[str] = None
    lines: Dict[str, int] = {}
    mid_layer_lines: MidLayerLine = MidLayerLine()
    mid_turn_lines: Dict[str, int] = {}
    aux_lines: Dict[str, int] = {}


class PoweredBlock(BaseModel):
    half_turns: Dict[int, PoweredGroup] = {}
    current_sign: Optional[int] = None
    conductor: Optional[str] = None


class SymmetryGroup(BaseModel):
    normal_free: Optional[int] = None
    tangential_free: Optional[int] = None


class PhysicalGroup(BaseModel):
    blocks: Dict[int, PoweredBlock] = {}
    wedges: Dict[int, WedgeGroup] = {}
    insulations: GroupType = GroupType()
    iron: GroupType = GroupType()
    air_inf: Optional[int] = None
    air_inf_bnd: Optional[int] = None
    air: Optional[int] = None
    symmetric_boundaries: SymmetryGroup = SymmetryGroup()
    half_turns_points: Optional[int] = None


class SymmetryBoundaries(BaseModel):
    x: List[int] = []
    y: List[int] = []


class GroupEntities(BaseModel):
    iron: Dict[str, List[int]] = {}
    air: List[int] = []
    symmetric_boundaries: SymmetryBoundaries = SymmetryBoundaries()


class Domain(BaseModel):
    groups_entities: GroupEntities = GroupEntities()
    physical_groups: PhysicalGroup = PhysicalGroup()


class MultipoleData(BaseModel):
    geometries: Geometry = Geometry()
    domains: Domain = Domain()


#######################################


class NeighbourNode(BaseModel):
    groups: Dict[str, List[float]] = {}


class IsothermalNodes(BaseModel):
    conductors: Dict[str, Dict[int, List[float]]] = {}
    wedges: Dict[str, Dict[int, List[float]]] = {}
    thin_shells: Dict[int, List[float]] = {}


class MultipoleRegionCoordinate(BaseModel):
    isothermal_nodes: IsothermalNodes = IsothermalNodes()
    neighbouring_nodes: NeighbourNode = NeighbourNode()


