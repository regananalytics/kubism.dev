import os
import glob
import time
import asyncio
import logging
#from kubism.deploy.io import upstream
from kubio import upstream

# Not sure if we need these inside the container
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

# Assume we've mapped the device folder to /app
# and its where this file is located
device_folder = glob.glob('/sys/bus/w1/devices/28*')[0]
device_file = device_folder + '/w1_slave'


def read_temp_raw():
    
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    print('Reading Temp')
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f




class temp_server(upstream):

    def __init__(self):
        super().__init__()
        print('Setting Callback')
        self.set_callback(self.respond_temp)


    async def respond_temp(self, *args):
        temp_c, temp_f = read_temp()
        temp_string = f'Temp:  {temp_c} C,  {temp_f} F'
        print(temp_string)
        await self.respond_async(temp_string.encode())

print('Starting Server')
temp = temp_server()
asyncio.run(temp.listen_async())