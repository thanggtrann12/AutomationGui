def print_ssm_status():
    print("SSM Status: Operational")

def monitor_ssm_parameters():
    parameters = ["Voltage", "Current", "Temperature"]
    for param in parameters:
        print(f"Monitoring {param}...")

def check_ssm_health(health_score=90):
    if health_score >= 80:
        print(f"SSM Health Score: {health_score}. Status: Good")
    else:
        print(f"SSM Health Score: {health_score}. Status: Needs Attention")

BLOCKS = {
    "Print SSM Status": print_ssm_status,
    "Monitor SSM Parameters": monitor_ssm_parameters,
    "Check SSM Health": check_ssm_health,
}
