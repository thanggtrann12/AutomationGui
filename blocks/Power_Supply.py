import logging
import asyncio


async def set_power_off() -> bool:
    logging.info("Set Power Supply: 0V")
    await asyncio.sleep(1)
    return True


async def set_power_on() -> bool:
    logging.info("Set Power Supply: 12V")
    await asyncio.sleep(1)
    return True


async def set_voltage(voltage) -> bool:
    logging.info(f"Set Power Supply: {voltage}")
    await asyncio.sleep(1)
    return True


BLOCKS = {
    "Turn OFF": set_power_off,
    "Turn ON": set_power_on,
    "Set Voltage (voltage)": set_voltage
}
