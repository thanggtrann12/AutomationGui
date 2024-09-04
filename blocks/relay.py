def disconnect_acc():
    print("Disconnect ACC wire")


def connect_acc():
    print("Disconnect ACC wire")


def diconnect_bat_gnd():
    print("Remove BAT+GND")


def connect_bat_gnd():
    print("Connect BAT+GND")


BLOCKS = {
    "ACC Off": disconnect_acc,
    "ACC On": connect_acc,
    "Remove BAT+GND": diconnect_bat_gnd,
    "Connect BAT+GND": connect_bat_gnd,
}
