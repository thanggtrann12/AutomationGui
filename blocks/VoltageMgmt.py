# from tools.ToellnerDriver import ToellnerDriver
import logging
import asyncio


async def set_voltage_state(state) -> bool:
    logging.info("Voltage Status: Stable %d", state)
    await asyncio.sleep(1)
    return True


async def powerloss_warning() -> bool:
    await set_voltage_state(3)
    return True


async def critical_low() -> bool:
    await set_voltage_state(6.7)
    return True


async def low() -> bool:
    await set_voltage_state(7)
    return True


async def normal() -> bool:
    await set_voltage_state(13)
    return True


async def high() -> bool:
    await set_voltage_state(18)
    return True


async def critical_high() -> bool:
    await set_voltage_state(25)
    return True


BLOCKS = {
    "Power Loss": powerloss_warning,
    "Critical Low": critical_low,
    "Low": low,
    "Normal": normal,
    "High": high,
    "Critical High": critical_high,
}
