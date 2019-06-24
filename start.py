#!/usr/bin/env python

import sys
import time
import json
import requests

from envirophat import light, weather, motion, analog

unit = 'hPa'  # Pressure unit, can be either hPa (hectopascals) or Pa (pascals)
url = 'http://httpbin.org/post'

def write(line):
    sys.stdout.write(line)
    sys.stdout.flush()

def send(data):
    sys.stdout.write(data)
    data_json = json.dumps(data)
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data=data_json, headers=headers)

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
            "system": "rpi_pega",
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
        send(data)
        time.sleep(1)

except KeyboardInterrupt:
    pass
