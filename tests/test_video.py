import os
import time
import typing as tp

from fastapi.testclient import TestClient

from app import app

test_client = TestClient(app)

# Use TESTS_DELAY environ var to control time.sleep length. 2 seconds by default
delay = float(os.environ.get("TESTS_DELAY", 2))
tests_cache: tp.Dict[str, str] = {}


def test_get_video_cameras_list() -> None:
    resp = test_client.get("/video/cameras")
    assert resp.ok, resp.text
    assert resp.json().get("cameras", None) is not None, "No cameras found (check config)"


def test_get_video_records_list() -> None:
    resp = test_client.get("/video/records")
    assert resp.ok, resp.text
    assert not resp.json().get("ongoing_records", None), "when did we started recording?"
    assert not resp.json().get("ended_records", None), "when did we ended recording?"


def test_start_first_record() -> None:
    resp = test_client.post("/video/camera/222/start")
    assert resp.ok, resp.text
    assert resp.status_code == 200, resp.json().get("details", None)

    tests_cache["first_rec"] = resp.json().get("record_id")

    records_list_resp = test_client.get("/video/records")
    assert len(records_list_resp.json().get("ongoing_records", [])) != 0, "recording hasn't started"


def test_stop_first_record() -> None:
    resp = test_client.post(f"/video/record/{tests_cache['first_rec']}/stop")
    assert resp.ok, resp.text
    assert resp.status_code == 200, resp.json().get("details", None)

    records_list_resp = test_client.get("/video/records")
    assert (
        len(records_list_resp.json().get("ongoing_records", [])) == 0
    ), f"recording hasn't stopped: {records_list_resp.json()}"


def test_stop_first_record_again() -> None:
    resp = test_client.post(f"/video/record/{tests_cache['first_rec']}/stop")
    assert resp.json().get("status") == 500, f"stopped nonexistent record: {resp.json().get('details', None)}"


def test_start_second_record() -> None:
    resp = test_client.post("/video/camera/222/start")
    assert resp.ok, resp.text
    assert resp.status_code == 200, resp.json().get("details", None)

    tests_cache["second_rec"] = resp.json().get("record_id")

    records_list_resp = test_client.get("/video/records")
    assert len(records_list_resp.json().get("ongoing_records", [])) != 0, "second recording hasn't started"
    assert len(records_list_resp.json().get("ended_records", [])) == 1, "second recording hasn't started"


def test_stop_second_record() -> None:
    resp = test_client.post(
        f"/video/record/{tests_cache['second_rec']}/stop", json={"record_id": tests_cache["second_rec"]}
    )
    assert resp.ok, resp.text
    assert resp.status_code == 200, resp.json().get("details", None)

    records_list_resp = test_client.get("/video/records")
    assert len(records_list_resp.json().get("ongoing_records", [])) == 0, "recording hasn't stopped"
    assert len(records_list_resp.json().get("ended_records", [])) == 2, "second recording hasn't started"


def test_multiple_records_cycle() -> None:
    first_rec_resp = test_client.post("/video/camera/222/start")
    second_rec_resp = test_client.post("/video/camera/222/start")

    time.sleep(delay)

    records_list_resp = test_client.get("/video/records")
    assert len(records_list_resp.json().get("ongoing_records", [])) == 2, "recordings hasn't started"

    end_second_rec_resp = test_client.post(f"/video/record/{second_rec_resp.json().get('record_id')}/stop")

    time.sleep(delay)

    end_first_rec_resp = test_client.post(f"/video/record/{first_rec_resp.json().get('record_id')}/stop")

    time.sleep(delay)

    assert end_second_rec_resp.ok, end_second_rec_resp.text
    assert end_first_rec_resp.ok, end_first_rec_resp.text
    assert (
        end_first_rec_resp.status_code == end_second_rec_resp.status_code
    ), "An error occurred while trying to stop record 1 or 2"
