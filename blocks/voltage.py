def print_voltage_status():
    print("Voltage Status: Stable")

def monitor_voltage_levels():
    for i in range(1, 11):
        print(f"Voltage reading {i}: {110 + i}V")

def check_voltage(voltage=120):
    if 110 <= voltage <= 130:
        print(f"Voltage: {voltage}V. Status: Normal")
    else:
        print(f"Voltage: {voltage}V. Status: Out of range")

BLOCKS = {
    "Print Voltage Status": print_voltage_status,
    "Monitor Voltage Levels": monitor_voltage_levels,
    "Check Voltage": check_voltage,
}
