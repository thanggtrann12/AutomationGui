def power_on():
    print("Power supply turned on")

def adjust_voltage(voltage=5):
    print(f"Voltage adjusted to {voltage}V")

def adjust_current(current=1):
    print(f"Current adjusted to {current}A")

def power_off():
    print("Power supply turned off")

BLOCKS = {
    "Power On": power_on,
    "Adjust Voltage": adjust_voltage,
    "Adjust Current": adjust_current,
    "Power Off": power_off,
}
