import subprocess


class ADBCommand:
    def __init__(self):
        self.swu_timer_reboot_command = ""
        self.toggle_watchdog_command = ""
        self.device_list = self.check_devices()
        self.is_connected = bool(self.device_list)
        self.mode = "Normal"

    def check_devices(self):
        result = subprocess.run(
            ["adb", "devices"], text=True, capture_output=True)
        devices = [line.split()[0] for line in result.stdout.splitlines()
                   if "\tdevice" in line or "\trecovery" in line]
        if devices:
            self.mode = "Recovery" if "recovery" in result.stdout.splitlines()[
                1] else "Normal"
        return devices

    def refresh_connection(self):
        self.device_list = self.check_devices()
        self.is_connected = bool(self.device_list)

    def set_root_privilege(self) -> bool:
        self.run_subprocess(["adb", "root"])

    def check_root_privilege(self) -> bool:
        result = self.run_subprocess(["adb", "shell", "id"])
        return "uid=0(root)" in result.stdout

    def run_subprocess(self, command):
        result = subprocess.run(command, shell=True,
                                capture_output=True, text=True)
        print(result.stdout)

    def run_adb_shell_command(self, user_command):
        base_command = ["adb", "shell"]
        full_command = base_command + user_command.split()
        self.run_subprocess(full_command)

    def reboot_to_recovery_mode(self):
        if self.is_connected:
            self.run_subprocess(["adb", "reboot", "recovery"])

    def reboot_to_normal_mode(self):
        if self.is_connected:
            self.run_subprocess(["adb", "reboot", "normal"])

    def push_file(self, file_path, des_path):
        if self.is_connected:
            result = self.run_subprocess(["adb", "push", file_path, des_path])
            success_patterns = ["1 file pushed", "0 skipped"]
            return any(pattern in result.stdout for pattern in success_patterns)

    def swu_timer_shutdown(self):
        if self.is_connected:
            result = self.run_adb_shell_command(self.swu_timer_reboot_command)
            return result

    def toggle_watchdog(self):
        if self.is_connected:
            result = self.run_adb_shell_command(self.toggle_watchdog_command)
            return result

    def remount(self):
        if self.is_connected:
            result = self.run_subprocess(["adb", "remount"])
            return result
