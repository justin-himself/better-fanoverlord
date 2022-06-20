import os
import time
import atexit
import logging
import subprocess
from math import *

# Env Variables
CPU_NUM   = int(os.getenv('CPU_NUM', 1))
SPEED_FUNC = os.getenv('SPEED_FUNC', "exp(0.075 * t) - 0.01 * t**2 + 10")
IPMI_HOST = os.getenv('IPMI_HOST', "192.168.0.120")
IPMI_USER = os.getenv('IPMI_USER', "root")
IPMI_PW   = os.getenv('IPMI_PW', "calvin")

# Constants
MAX_CPU_TEMP = 60
CMD_PREFIX = "ipmitool -I lanplus -H " + IPMI_HOST + " -U " + IPMI_USER + " -P " + IPMI_PW + " "
FAN_SPEED_PREFIX = "raw 0x30 0x30 0x02 0xff "
FAN_CONTROL_PREFIX = "raw 0x30 0x30 0x01 "

# Functions

def get_cpu_temp():
    output = subprocess.run(CMD_PREFIX + "sdr type temperature | grep '^Temp' | grep -oE '\d{2}'", shell=True, capture_output=True)
    cpu_temp = output.stdout.decode('utf-8').split("\n")[0:CPU_NUM]
    return map(int, cpu_temp)

def set_fan_speed(percentage : int):
    subprocess.run(CMD_PREFIX + FAN_SPEED_PREFIX + str(hex(percentage)), shell=True)

def set_fan_control(isTakeover : bool):
    subprocess.run(CMD_PREFIX + FAN_CONTROL_PREFIX + str(hex(int(not isTakeover))), shell=True)


def get_fan_speed(t : int):
    # math.exp(0.075 * t) - 0.01 * t**2 + 10
    return int(eval(SPEED_FUNC))

def on_exit():
    logging.warning("Exiting... Give over control to system.")
    set_fan_control(isTakeover=False)

def main():

    # Init
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    set_fan_control(isTakeover=True)
    atexit.register(on_exit)

    while True:
        try:
            current_cpu_temp = max(get_cpu_temp())
            current_fan_speed = get_fan_speed(current_cpu_temp)
            set_fan_speed(current_fan_speed)
        except Exception as e:
            logging.error(e)
            on_exit()
            exit(-1)

        logging.info(str(current_cpu_temp) + '° | ' + str(current_fan_speed) + '%')

        # emergency happens, give control back to system
        if current_cpu_temp > MAX_CPU_TEMP:
            logging.critical("Emegency, current CPU temp is " + str(current_cpu_temp) + "°.")
            set_fan_speed(100)
            on_exit()
            exit(0)

        

if __name__ == "__main__":
    main()

