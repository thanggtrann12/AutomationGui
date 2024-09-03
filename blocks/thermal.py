import logging

def print_thermal_status():
    logging.info("Thermal System Status: Active")

def monitor_temperature():
    for i in range(1, 11):
        logging.info(f"Temperature reading {i}: {20 + i}°C")

def check_temperature(temp=25):
    if temp <= 30:
        logging.info(f"Temperature: {temp}°C. Status: Normal")
    else:
        logging.info(f"Temperature: {temp}°C. Status: High - Cooling needed")

BLOCKS = {
    "Print Thermal Status": print_thermal_status,
    "Monitor Temperature": monitor_temperature,
    "Check Temperature": check_temperature,
}
