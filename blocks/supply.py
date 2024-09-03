def print_supply_status():
    print("Power Supply Status: Active")

def monitor_supply_levels():
    levels = ["Voltage", "Current", "Power"]
    for level in levels:
        print(f"Monitoring {level}...")

def check_supply_efficiency(efficiency=95):
    if efficiency >= 90:
        print(f"Power Supply Efficiency: {efficiency}%. Status: Optimal")
    else:
        print(f"Power Supply Efficiency: {efficiency}%. Status: Needs Improvement")

BLOCKS = {
    "Print Supply Status": print_supply_status,
    "Monitor Supply Levels": monitor_supply_levels,
    "Check Supply Efficiency": check_supply_efficiency,
}
