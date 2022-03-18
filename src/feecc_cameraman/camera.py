from __future__ import annotations

import asyncio
import json
import os
import socket
import typing as tp
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from loguru import logger

MINIMAL_RECORD_DURATION_SEC: int = 3
FFMPEG_COMMAND: str = os.getenv(
    "FFMPEG_COMMAND", 'ffmpeg -loglevel warning -rtsp_transport tcp -i "RTSP_STREAM" -r 25 -c copy -map 0 FILENAME'
)


@dataclass(frozen=True)
class Camera:
    """a wrapper for the video camera config"""

    number: int
    socket_address: str
    rtsp_stream_link: str

    def __post_init__(self) -> None:
        self.is_up()

    def __str__(self) -> str:
        return f"Camera no.{self.number} host at {self.socket_address}"

    def is_up(self) -> bool:
        """check if camera is reachable on the specified port and ip"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.25)

        try:
            ip, port = self.socket_address.split(":", 1)
            s.connect((ip, int(port)))
            is_up = True
            logger.debug(f"{self} is up")
        except socket.error:
            is_up = False
            logger.warning(f"{self} is unreachable")

        s.close()
        return is_up


@dataclass
class Recording:
    """a recording object represents one ongoing recording process"""

    rtsp_steam: str
    filename: tp.Optional[str] = None
    process_ffmpeg: tp.Optional[asyncio.subprocess.Process] = None
    record_id: str = field(default_factory=lambda: uuid4().hex)
    start_time: tp.Optional[datetime] = None
    end_time: tp.Optional[datetime] = None

    def __post_init__(self) -> None:
        self.filename = self._get_video_filename()

    def __len__(self) -> int:
        """calculate recording duration in seconds"""
        if self.start_time is None:
            return 0

        if self.end_time is not None:
            duration = self.end_time - self.start_time
        else:
            duration = datetime.now() - self.start_time

        return int(duration.total_seconds())

    def _get_video_filename(self, dir_: str = "output/video") -> str:
        """determine a valid video name not to override an existing video"""
        if not os.path.isdir(dir_):
            os.makedirs(dir_)
        return f"{dir_}/{self.record_id}.mp4"

    @property
    def is_ongoing(self) -> bool:
        return self.start_time is not None and self.end_time is None

    @logger.catch(reraise=True)
    async def start(self) -> None:
        """Execute ffmpeg command"""
        # ffmpeg -loglevel warning -rtsp_transport tcp -i "rtsp://login:password@ip:port/Streaming/Channels/101" \
        # -c copy -map 0 vid.mp4
        command = FFMPEG_COMMAND
        command = command.replace("RTSP_STREAM", self.rtsp_steam, 1)
        command = command.replace("FILENAME", str(self.filename), 1)

        self.process_ffmpeg = await asyncio.subprocess.create_subprocess_shell(
            cmd=command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        self.start_time = datetime.now()
        logger.info(f"Started recording video '{self.filename}' using ffmpeg. {self.process_ffmpeg.pid=}")

    @logger.catch(reraise=True)
    async def stop(self) -> None:
        """stop recording a video"""
        if self.process_ffmpeg is None:
            logger.error(f"Failed to stop record {self.record_id}")
            logger.debug(f"Operation ongoing: {self.is_ongoing}, ffmpeg process: {bool(self.process_ffmpeg)}")
            return

        if len(self) < MINIMAL_RECORD_DURATION_SEC:
            logger.warning(
                f"Recording {self.record_id} duration is below allowed minimum ({MINIMAL_RECORD_DURATION_SEC=}s). "
                "Waiting for it to reach it before stopping."
            )
            await asyncio.sleep(MINIMAL_RECORD_DURATION_SEC - len(self))

        logger.info(f"Trying to stop record {self.record_id} process {self.process_ffmpeg.pid=}")

        stdout, stderr = await self.process_ffmpeg.communicate(input=b"q")
        await self.process_ffmpeg.wait()
        return_code = self.process_ffmpeg.returncode

        if return_code == 0:
            logger.debug("Got a zero return code from ffmpeg subprocess. Assuming success.")
        else:
            logger.error(f"Got a non zero return code from ffmpeg subprocess: {return_code}")
            logger.debug(f"{stdout=} {stderr=}")

        self.process_ffmpeg = None
        self.end_time = datetime.now()

        logger.info(f"Finished recording video for record {self.record_id}")


RECORDS: tp.Dict[str, Recording] = {}
CAMERAS: tp.Dict[int, Camera] = {}

cameras_config: tp.Optional[str] = os.getenv("CAMERAS_CONFIG")
assert cameras_config, "CAMERAS_CONFIG environment variable has not been provided"
config: tp.List[str] = json.loads(cameras_config)

for entry in config:
    number, socket_address, rtsp = entry.split("-", 2)
    CAMERAS[int(number)] = Camera(
        number=int(number),
        socket_address=socket_address,
        rtsp_stream_link=rtsp,
    )

logger.info(f"Initialized {len(CAMERAS)} cameras")
