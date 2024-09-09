def disconnect_acc() -> bool:
    print("Disconnect ACC wire")
    return True


def connect_acc() -> bool:
    print("Disconnect ACC wire")
    return True


def diconnect_bat_gnd() -> bool:
    print("Remove BAT+GND")
    return True


def connect_bat_gnd() -> bool:
    print("Connect BAT+GND")
    return True


BLOCKS = {
    "ACC Off": disconnect_acc,
    "ACC On": connect_acc,
    "Remove BAT+GND": diconnect_bat_gnd,
    "Connect BAT+GND": connect_bat_gnd,
}
