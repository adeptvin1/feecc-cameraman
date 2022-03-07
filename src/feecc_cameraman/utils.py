import asyncio

from loguru import logger

from .camera import RECORDS


async def end_stuck_records(max_duration: int = 60 * 60, interval: int = 60) -> None:
    """If record length exceeds the maximum duration it is considered
    stuck or forgotten and will be stopped. Checked every interval seconds."""
    logger.info(
        f"A daemon was started to monitor stuck records. Update interval is {interval}s., "
        f"max allowed recording duration is {max_duration}s."
    )

    while True:
        await asyncio.sleep(interval)

        for rec_id, rec in RECORDS.items():
            if rec.is_ongoing and len(rec) >= max_duration:
                await RECORDS[rec_id].stop()
                logger.warning(f"Recording {rec_id} exceeded {max_duration} s. and was stopped.")
