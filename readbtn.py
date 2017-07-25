#!/bin/python3

import smbus
import time

address = 0x65

adc = smbus.SMBus(1)

#ddadc.read_byte_data (
adc.write_byte_data(address,0x00,0xF0)
while True:
	lower = adc.read_byte_data(address,0x00)
	upper = adc.read_byte_data(address,0x01)
	sum = lower + upper
	if (sum > 255):
		print ("Button pressed. Analog value: " + str(sum))
	time.sleep(.5)

