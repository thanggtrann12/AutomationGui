import logging


def print_thermal_status() -> bool:
    logging.info("Thermal System Status: Active")
    return True


def monitor_temperature() -> bool:
    for i in range(1, 11):
        logging.info(f"Temperature reading {i}: {20 + i}°C")
    return True


def check_temperature() -> bool:
    logging.info(f"Temperature: 25°C. Status: Normal")
    return True


BLOCKS = {
    "Print Thermal Status": print_thermal_status,
    "Monitor Temperature": monitor_temperature,
    "Check Temperature": check_temperature,
}
