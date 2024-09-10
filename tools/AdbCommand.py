import subprocess
import asyncio
import logging


class ADBCommand:
    def __init__(self):
        self.swu_timer_reboot_command = ""
        self.toggle_watchdog_command = ""
        self.device_list = self.check_devices()
        self.is_connected = bool(self.device_list)

    def check_devices(self):
        result = subprocess.run(
            ["adb", "devices"], text=True, capture_output=True)
        devices = [line for line in result.stdout.splitlines()
                   if "\tdevice" in line or "\trecovery" in line]
        return devices

    def is_recovery_mode(self) -> bool:
        self.refresh_connection()
        if self.is_connected:
            return any("\trecovery" in device for device in self.device_list)
        return False

    def refresh_connection(self):
        self.device_list = self.check_devices()
        self.is_connected = bool(self.device_list)

    async def set_root_privilege(self) -> bool:
        self.refresh_connection()
        if await self.check_root_privilege():
            return True
        await self.run_subprocess(["adb", "root"])
        await asyncio.sleep(8)
        return await self.check_root_privilege()

    async def check_root_privilege(self) -> bool:
        self.refresh_connection()
        if self.is_recovery_mode():
            return True
        else:
            result = await self.run_subprocess(["adb", "shell", "id"])
            return "uid=0(root)" in result.stdout

    async def run_subprocess(self, command) -> subprocess.CompletedProcess:
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            stdout_decoded = stdout.decode()
            stderr_decoded = stderr.decode()
            return subprocess.CompletedProcess(command, process.returncode, stdout_decoded, stderr_decoded)
        except Exception as e:
            pass

    async def run_adb_shell_command(self, user_command):
        self.refresh_connection()
        base_command = ["adb", "shell"]
        full_command = base_command + user_command.split()
        result = await self.run_subprocess(full_command)
        return result

    async def reboot_to_mode(self, mode="normal"):
        self.refresh_connection()
        if self.is_connected:
            await self.run_subprocess(["adb", "reboot", mode.lower()])
            await asyncio.sleep(5)
            self.refresh_connection()

    async def push_file(self, file_path, des_path):
        if self.is_connected:
            result = await self.run_subprocess(["adb", "push", file_path, des_path])
            success_patterns = ["1 file pushed", "0 skipped"]
            fail_patterns = ["error", "failed to copy"]
            return any(pattern in result.stdout for pattern in success_patterns) and not any(pattern in result.stdout for pattern in fail_patterns)

    def swu_timer_shutdown(self):
        if self.is_connected:
            result = self.run_adb_shell_command(self.swu_timer_reboot_command)
            return result

    def toggle_watchdog(self):
        if self.is_connected:
            result = self.run_adb_shell_command(self.toggle_watchdog_command)
            return result

    async def remount(self):
        if self.is_connected and self.check_root_privilege():
            result = await self.run_subprocess(["adb", "remount"])
            return result


# adb = ADBCommand()
# print(not adb.is_recovery_mode())
# adb.push_file(
#     file_path=r"C:\Users\rhn9hc\Desktop\lib\lcm_dynamic_service", des_path="/")
