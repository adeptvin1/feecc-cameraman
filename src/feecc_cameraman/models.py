import typing as tp
from datetime import datetime

from pydantic import BaseModel


class GenericResponse(BaseModel):
    status: int  # an HTTP status code for a response
    details: str


class StartRecordResponse(GenericResponse):
    record_id: str


class StopRecordResponse(GenericResponse):
    filename: str


class RecordData(BaseModel):
    filename: tp.Optional[str]
    record_id: str
    start_time: tp.Optional[datetime]
    end_time: tp.Optional[datetime]


class RecordList(GenericResponse):
    ongoing_records: tp.List[RecordData]
    ended_records: tp.List[RecordData]


class CameraModel(BaseModel):
    number: int
    host: str
    is_up: bool


class CameraList(GenericResponse):
    cameras: tp.List[CameraModel]
