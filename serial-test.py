#!/usr/bin/python

import aioserial
import asyncio
from pathlib import Path

serial = '/dev/ttyACM0'
if not Path(serial).exists():
   serial = '/dev/ttyACM1'
   print("Trying "+serial)

if Path(serial).exists():
   print("Using "+serial)
else:
   print("Could not find the serial port.")
   exit()


async def read_and_print(aioserial_instance: aioserial.AioSerial):
    while True:
        print((await aioserial_instance.read_async()).decode(errors='ignore'), end='', flush=True)

asyncio.run(read_and_print(aioserial.AioSerial(port=serial)))

