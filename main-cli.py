import argparse
import ctypes
from ppadb.client import Client
import os
import sys
import time
from subprocess import Popen, PIPE
from scanner import StatsScanner


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


DESC = (
    "This program reads the stats of the top N players in the individual power ranking list. It controls RoK PC "
    "Version or BlueStacks instance via ADB to take and parses them using the Tesseract OCR. "
)

parser = argparse.ArgumentParser(description=DESC)
parser.add_argument(
    "-t",
    "--tag",
    help="The name of the task (for example, KvK-Start, KvK-pass4). It will be used as the name of the output folder.",
    required=True,
)
parser.add_argument(
    "-n",
    "--number",
    help="How many profiles to read from the top of the list",
    required=True,
    type=int,
)
parser.add_argument("-d", "--device", help="Device type: {pc, adb}", required=True)
parser.add_argument(
    "-s",
    "--serial",
    help="(Only with adb) Device serial in adb, such as 127.0.0.1:5585",
    required=False,
)

arguments = parser.parse_args()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":

    # Check if tesseract is installed
    if not StatsScanner.is_tool("tesseract"):
        print(f"{bcolors.FAIL}We could not find the required Tesseract OCR executable in the PATH "
              f"variable.\nPlease refer to the documentation to install Tesseract, add it to the PATH, and restart "
              f"IN A NEW TERMINAL.{bcolors.ENDC}")
        sys.exit()

    params = {
        "device": arguments.device.lower(),
        "window": "Rise of Kingdoms",
        "serial": arguments.serial,
        "count": arguments.number,
        "dir": os.getcwd() + "\\output",
        "tag": arguments.tag
    }

    # Validation
    if params["device"] == "pc":
        # The program must be running in administration mode. If not restart with admin privileges.
        if not is_admin():
            print(f"{bcolors.FAIL}To run with the PC version, this application must run as administrator.\nPlease "
                  f"Start a new terminal AS an ADMINISTRATOR.{bcolors.ENDC}")
            sys.exit()

        print(f"{bcolors.OKGREEN}Required resolution: {bcolors.OKCYAN}Full Screen 1920x1080")
        print(
            f"{bcolors.OKGREEN}RoK must be running at the {bcolors.OKCYAN}individual power ranking{bcolors.OKGREEN} page. Switching to the game in 5 seconds ...{bcolors.ENDC}")
        time.sleep(6)

    elif params["device"] == "adb":
        # Check if adb installed
        if not StatsScanner.is_tool("adb"):
            print(f"{bcolors.FAIL}We could not find the required adb engine in the PATH variable.\nPlease refer to "
                  f"the documentation to install adb, add it to the PATH, and restart the program.{bcolors.ENDC}")
            sys.exit()

        # start the adb server
        # Try to connect to the device to the adb daemon and start the server
        process = Popen(["adb.exe", "connect", params["serial"]], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        print("ADB output: {}".format(output))

        # check if the device is connected
        adb = Client(host='localhost', port=5037)
        devices = adb.devices()

        found = False
        for device in devices:
            if device.serial == params["serial"]:
                found = True
                break

        if not found:
            print(
                f"{bcolors.FAIL}Could not find the device in the connected adb devices.\n\nPlease double-check the serial.{bcolors.ENDC}")
            sys.exit()
    else:
        print(f"{bcolors.FAIL}Unknown device type. Accepted types: {{pc,adb}}{bcolors.ENDC}")
        quit(-1)

    scanner = StatsScanner(params)
    scanner.start()
