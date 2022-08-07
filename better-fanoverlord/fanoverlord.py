from inspect import _void
from operator import is_
import os
import logging
import subprocess
import time
from math import *
from datetime import datetime
from register_exit_fun import register_exit_fun

# Env Variables
TZ        = os.getenv('TZ', "Asia/Shanghai")
CPU_NUM   = int(os.getenv('CPU_NUM', 1))
FAN_NUM   = int(os.getenv('FAN_NUM', 1))
SPEED_FUNC = os.getenv('SPEED_FUNC', "tanh((t-55)/10)*40 + 50")
TIME_COND = os.getenv('TIME_COND', "1")
IPMI_HOST = os.getenv('IPMI_HOST', "192.168.0.120")
IPMI_USER = os.getenv('IPMI_USER', "root")
IPMI_PW   = os.getenv('IPMI_PW', "calvin")

# Commands
CMD_PREFIX = "ipmitool -I lanplus -H " + IPMI_HOST + " -U " + IPMI_USER + " -P " + IPMI_PW + " "
FAN_SPEED_PREFIX = "raw 0x30 0x30 0x02 0xff "
FAN_CONTROL_PREFIX = "raw 0x30 0x30 0x01 "


# The program terminates itself and give 
# back control if exceeding this temperature
MAX_CPU_TEMP = 80

# The fan speed is kept constant if 
# the current temperature is within 
# +- VIBRANR_RANGE degrees of the
# average of last VIBRANT_COUNT times
# VIBRANT_RANGE = 3
# VIBRANT_COUNT = 5



# Functions

def exit_on_failure(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(func.__name__ + " : " + e)
            on_exit()
            exit(-1)
    return wrapper

@exit_on_failure
def get_cpu_temp():
    output = subprocess.run(CMD_PREFIX + "sdr type temperature | grep '^Temp' | grep -oE '\d{2}'", shell=True, capture_output=True)
    cpu_temp = output.stdout.decode('utf-8').split("\n")[0:CPU_NUM]
    return map(int, cpu_temp)

@exit_on_failure
def get_fan_rpm():
    output = subprocess.run(CMD_PREFIX + "sdr type fan | grep '^Fan' | grep -oE '\d{4}'", shell=True, capture_output=True)
    fan_rpm = output.stdout.decode('utf-8').split("\n")[0:FAN_NUM]
    return fan_rpm

@exit_on_failure
def set_fan_speed(percentage : int):
    subprocess.run(CMD_PREFIX + FAN_SPEED_PREFIX + str(hex(percentage)), shell=True)

def set_fan_control(isTakeover : bool):
    subprocess.run(CMD_PREFIX + FAN_CONTROL_PREFIX + str(hex(int(not isTakeover))), shell=True)

@exit_on_failure
def calc_fan_speed(t : int):
    return int(eval(SPEED_FUNC))

@exit_on_failure
def is_fanoverlord_enabled(t : datetime.time):
    return bool(eval(TIME_COND))

@register_exit_fun
def on_exit():
    logging.warning("Exiting... Give over control to system.")
    set_fan_control(isTakeover=False)

def main():

    # Init
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    os.system("cp /usr/share/zoneinfo/" + TZ + " /etc/localtime")

    # Main Loop

    while True:
        current_cpu_temp = max(get_cpu_temp())
        calculated_fan_speed = calc_fan_speed(current_cpu_temp)

        # emergency happens, give control back to system
        if current_cpu_temp > MAX_CPU_TEMP:
            logging.critical("Emegency, current CPU temp is " + str(current_cpu_temp) + "°.")
            on_exit()
            exit(0)

        # test if fanoverlord is enabled according to condition
        if not is_fanoverlord_enabled(datetime.now().time()):
            logging.warning("Fanoverlord is not enabled, sleep 1 min")
            set_fan_control(isTakeover=False)
            time.sleep(60)
            continue
        
        set_fan_control(isTakeover=True)
        set_fan_speed(calculated_fan_speed)
        logging.info(str(current_cpu_temp) + '° | ' + str(calculated_fan_speed) + '%')

if __name__ == "__main__":
    main()