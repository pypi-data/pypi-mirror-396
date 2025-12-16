from typing import TypedDict
from ..config import Config


class MetadataProcessor(TypedDict):
    temperature: float
    fs_pickup: float
    fs_signal: float


class tTDOProcessor:
    cfg: Config
    _meas_name: str
    _tdo_name: str
    _tdo_det_inc_name: str
    _tdo_det_dec_name: str
    _tdo_inv_inc_name: str
    _tdo_inv_dec_name: str
    npoints_raw: int
    inds_inc: slice
    inds_dec: slice
    is_cropped: dict[str, bool]
