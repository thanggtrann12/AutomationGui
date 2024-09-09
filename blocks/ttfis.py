from tools.TTFisClient import TTFisClient
import json

config_file = "D:\Python\AutomationGui\configs\hardware.json"

config = None
ttfisClient = None

aurix_log = []


def append_log(log):
    aurix_log.append(log)
    print(log)


with open(config_file, "r") as f:
    config = json.load(f)

    if config:
        ttfisClient = TTFisClient()
        if ttfisClient:
            ttfisClient.registerUpdateTraceCallback(append_log)
            ttfisClient.Connect(config["ttfis_client"]["port"], [
                "C:\\Users\\rhn9hc\\Desktop\\Test\\suzda3_cfg02_board_24.0F2024.35.1.trc"])


def clear_log():
    print("Clear log")
    aurix_log.clear()
    return True


def save_log():
    tffis_path = "D:\\Python\\Demo\\logs\\aurix_log.pro"
    if tffis_path:
        with open(tffis_path, 'w') as file:
            for item in aurix_log:
                file.write(item + '\n')
    return True


BLOCKS = {
    "Clear Log": clear_log,
    "Save Log": save_log
}
