""" serial-tester.py

Usage:
    serial-tester.py alltests <arduino_port> <ft4232_port>
    serial-tester.py pintest <arduino_port> <ft4232_port>
    serial-tester.py loopback <ft4232_port>
    serial-tester.py flash <arduino_port>

"""

import docopt
import serial
import time
import shutil
import subprocess
from pathlib import Path

from termcolor import colored

THIS_PATH = Path(__file__).parent

class ArduinoCLIInterface:

    def __init__(self, fqbn):
        self.fqbn = fqbn
        self.location = shutil.which("arduino-cli") or shutil.which("arduino-cli.exe")

    def verify(self, sketch_path):
        args = [self.location, "compile", "--fqbn", self.fqbn, str(sketch_path)]
        try:
            result = subprocess.run(args)
        except:
            raise

    def upload(self, sketch_path, port):
        args = [self.location, "upload", "-p", port, "--fqbn", self.fqbn, str(sketch_path)]
        try:
            print(args)
            result = subprocess.run(args)
        except:
            raise

def read_pin(pin, arduino):
    cmd = "READ." + pin + "\n"
    arduino.write(cmd.encode())
    result = arduino.readline()

    if result.startswith(b"1"):
        return True
    elif result.startswith(b"0"):
        return False
    else:
        raise Exception("Expected 1 or 0, got {}".format(result))

def write_pin(pin, arduino, pin_high):

    if pin_high:
        cmd = "WRITE1." + pin + "\n"
    else:
        cmd = "WRITE0." + pin + "\n"

    arduino.write(cmd.encode())

def test_loopback(ft4232):

    count = 0

    for i in range(1000):
        sent = "Loopback Test\n".encode()

        if (i % 10) == 0:
            print(".", end="", flush=True)

        ft4232.write(sent)

        returned = ft4232.readline()

        if returned == sent:
            count += 1

    print("")

    if count == 1000:
        print(colored("Loopback OK", 'green'))
    else:
        print(colored("Loopback failed ({} mismatched strings})".format(1000 - count), 'red'))

def test_5V(arduino):

    result = read_pin("5V", arduino)
    if result:
        print(colored("5V test OK", 'green'))
    else:
        print(colored("5V test failed", 'red'))

def test_3V3(arduino):

    result = read_pin("3V3", arduino)
    
    if result:
        print(colored("3V3 test OK", 'green'))
    else:
        print(colored("3V3 test failed", 'red'))

def test_GND(arduino):

    result = read_pin("GND", arduino)

    if not result:
        print(colored("GND test OK", 'green'))
    else:
        print(colored("GND test failed", 'red'))

def print_result(pin_name, result_that_should_be_true, result_that_should_be_false):
    if result_that_should_be_true and not result_that_should_be_false:
        print(colored(pin_name + " test OK", 'green'))
    else:
        if not result_that_should_be_true:
            print(colored(pin_name + " test failed on HIGH check", 'red'))

        if result_that_should_be_false:
            print(colored(pin_name + " test failed on LOW check", 'red'))

def test_output(pin, arduino, setter):

    setter(True) # Inverse logic
    result_that_should_be_false = read_pin(pin, arduino)

    setter(False) # Inverse logic
    result_that_should_be_true = read_pin(pin, arduino)

    print_result(pin, result_that_should_be_true, result_that_should_be_false)

def test_serial_outputs(ft4232, arduino):

    def dtr_setter(setting):
        ft4232.dtr = setting

    def rts_setter(setting):
        ft4232.rts = setting

    test_5V(arduino)
    test_3V3(arduino)
    test_GND(arduino)
    test_output("RTS", arduino, rts_setter)
    test_output("DTR", arduino, dtr_setter)

def test_input(pin, arduino, reader):

    write_pin(pin,arduino, False)
    time.sleep(0.3)
    expected_true = reader() # Inverse logic

    write_pin(pin,arduino, True)
    time.sleep(0.3)
    expected_false = reader() # Inverse logic

    print_result(pin, expected_true, expected_false)

def test_serial_inputs(ft4232, arduino):

    def cts_reader():
        return ft4232.cts   
    
    def dsr_reader():
        return ft4232.dsr
    
    def dcd_reader():
        return ft4232.cd

    def ri_reader():
        return ft4232.ri

    test_input("CTS", arduino, cts_reader)
    test_input("DSR", arduino, dsr_reader)
    test_input("DCD", arduino, dcd_reader)
    test_input("RI", arduino, ri_reader)

def perform_arduino_tests(ft4232, arduino):

    test_serial_outputs(ft4232, arduino)

    test_serial_inputs(ft4232, arduino)

def flash_arduino(port):

    cli = ArduinoCLIInterface("arduino:avr:nano:cpu=atmega328")
    cli.verify(Path(THIS_PATH, "arduino", "arduino.ino"))
    cli.upload(Path(THIS_PATH, "arduino", "arduino.ino"), port)

if __name__ == "__main__":

    opts = docopt.docopt(__doc__)

    ft4232_port = opts["<ft4232_port>"]
    arduino_port = opts["<arduino_port>"]
    with serial.Serial(ft4232_port, 115200, timeout=1) as ft4232:

        if opts["loopback"] or opts["alltests"]:
            test_loopback(ft4232)
        
        if opts["pintest"] or opts["alltests"]:
            with serial.Serial(arduino_port, 115200, timeout=1) as arduino:

                print("Waiting for arduino...")
                time.sleep(2)

                perform_arduino_tests(ft4232, arduino)

        if opts["flash"]:
            flash_arduino(arduino_port)
    