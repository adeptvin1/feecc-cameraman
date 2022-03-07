from fastapi import HTTPException, status

from .camera import Camera, Recording, CAMERAS, RECORDS


def get_camera_by_number(camera_number: int) -> Camera:
    """get a camera by its number"""
    if camera_number in CAMERAS:
        return CAMERAS[camera_number]

    raise HTTPException(status.HTTP_404_NOT_FOUND, f"No such camera: {camera_number}")


def get_record_by_id(record_id: str) -> Recording:
    """get a record by its uuid"""
    if record_id in RECORDS:
        return RECORDS[record_id]

    raise HTTPException(status.HTTP_404_NOT_FOUND, f"No such recording: {record_id}")
