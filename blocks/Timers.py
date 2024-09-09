import asyncio
import logging


async def sleep_for(sec=0) -> bool:
    logging.info(f"Test will sleep for {sec}")
    await asyncio.sleep(sec)
    return True


BLOCKS = {
    "Sleep (time)": sleep_for
}
