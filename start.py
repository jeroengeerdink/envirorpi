#!/usr/bin/env python

import sys
import time
import json
import requests

from envirophat import light, weather, motion, analog

unit = 'hPa'  # Pressure unit, can be either hPa (hectopascals) or Pa (pascals)

#url = 'http://172.31.26.234:7003/stream/RPiEvent'
url = 'https://ibestuur.pegatsdemo.com/prweb/PRRestService/RPiEnviro/v1/rpi/enviro/event'

previous = {
    "systemid": "rpi_pega",
    "timestamp": 0.0,
    "temperature": 0.0,
    "pressure": 0.0,
    "altitude": 0.0,
    "light": 0,
    "redlight": 0,
    "greenlight": 0,
    "bluelight": 0,
    "heading": 0.0,
    "magneto_x": 0,
    "magneto_y": 0,
    "magneto_z": 0,
    "accel_x": 0,
    "accel_y": 0,
    "accel_z": 0,
    "analog_0": 0,
    "analog_1": 0,
    "analog_2": 0,
    "analog_3": 0
}

def write(line):
    sys.stdout.write(line)
    sys.stdout.flush()

def detectEvent(data):
    global previous
    if abs(data["accel_x"]) < abs(previous["accel_x"])*1.1:
        send(data)
    elif abs(data["accel_y"]) < abs(previous["accel_y"])*1.1:
        send(data)
    elif abs(data["accel_z"]) < abs(previous["accel_z"])*1.1:
        send(data)
    previous = data

def send(data):
    data_json = json.dumps(data)
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data=data_json, headers=headers, auth=('raspberrypi', 'install12345!'))

write("--- Enviro pHAT Monitoring ---")

try:
    while True:
        rgb = light.rgb()
        analog_values = analog.read_all()
        mag_values = motion.magnetometer()
        acc_values = [round(x, 2) for x in motion.accelerometer()]

        output = """
Temp: {t:.2f}c
Pressure: {p:.2f}{unit}
Altitude: {a:.2f}m
Light: {c}
RGB: {r}, {g}, {b}
Heading: {h}
Magnetometer: {mx} {my} {mz}
Accelerometer: {ax}g {ay}g {az}g
Analog: 0: {a0}, 1: {a1}, 2: {a2}, 3: {a3}

""".format(
            unit=unit,
            a=weather.altitude(),  # Supply your local qnh for more accurate readings
            t=weather.temperature(),
            p=weather.pressure(unit=unit),
            c=light.light(),
            r=rgb[0],
            g=rgb[1],
            b=rgb[2],
            h=motion.heading(),
            a0=analog_values[0],
            a1=analog_values[1],
            a2=analog_values[2],
            a3=analog_values[3],
            mx=mag_values[0],
            my=mag_values[1],
            mz=mag_values[2],
            ax=acc_values[0],
            ay=acc_values[1],
            az=acc_values[2]
        )

        data = {
            "systemid": "rpi_pega",
            "timestamp": time.time(),
            "temperature": weather.temperature(),
            "pressure": weather.pressure(unit=unit),
            "altitude": weather.altitude(),
            "light": light.light(),
            "redlight": rgb[0],
            "greenlight": rgb[1],
            "bluelight": rgb[2],
            "heading": motion.heading(),
            "magneto_x": mag_values[0],
            "magneto_y": mag_values[1],
            "magneto_z": mag_values[2],
            "accel_x": acc_values[0],
            "accel_y": acc_values[1],
            "accel_z": acc_values[2],
            "analog_0": analog_values[0],
            "analog_1": analog_values[1],
            "analog_2": analog_values[2],
            "analog_3": analog_values[3]
        }

        output = output.replace("\n", "\n\033[K")
        write(output)
        lines = len(output.split("\n"))
        write("\033[{}A".format(lines - 1))
        detectEvent(data)
        time.sleep(.2)

except KeyboardInterrupt:
    pass
