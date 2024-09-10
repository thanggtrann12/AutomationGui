from tools.AdbCommand import ADBCommand

import logging
import asyncio

adb_device = ADBCommand()


async def enable_root_privilege() -> bool:
    logging.info("Enabling root privilege...")
    await adb_device.set_root_privilege()
    return await adb_device.check_root_privilege()


async def remount_device() -> bool:
    logging.info("Remounting device...")
    if await adb_device.check_root_privilege():
        await adb_device.remount()
        return True
    return False


async def reboot_to_recovery_mode() -> bool:
    logging.info("Rebooting into recovery mode...")
    await adb_device.reboot_to_mode("Recovery")
    logging.info("Checking if device is in recovery mode...")
    await asyncio.sleep(3)
    return adb_device.is_recovery_mode


async def reboot_to_normal_mode() -> bool:
    logging.info("Rebooting into normal mode...")
    await adb_device.reboot_to_mode()
    logging.info("Checking if device is in normal mode...")
    await asyncio.sleep(3)
    if not adb_device.is_recovery_mode():
        return True
    return False


async def push_service_file_to_device() -> bool:
    logging.info("Pushing service file to device...")
    return await adb_device.push_file(file_path=r"C:\Users\rhn9hc\Desktop\lib\lcm_dynamic_service", des_path="/vendor/bin")


async def trigger_property(property) -> bool:
    logging.info(f"Executed with property {property}")
    return await adb_device.run_adb_shell_command(property)


BLOCKS = {
    "Enable Root Privilege": enable_root_privilege,
    "Remount Device": remount_device,
    "Push Service File": push_service_file_to_device,
    "Reboot to Recovery Mode": reboot_to_recovery_mode,
    "Reboot to Normal Mode": reboot_to_normal_mode,
    "Trigger Property": trigger_property,
    "Reboot to  Mode": reboot_to_recovery_mode,
    "Reboot to Normal ": reboot_to_normal_mode,
    "Trigger ": trigger_property,
    "to  Mode": reboot_to_recovery_mode,
    "to Normal ": reboot_to_normal_mode,
    "Triggear ": trigger_property,
}
