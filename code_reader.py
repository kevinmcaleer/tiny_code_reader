# SPDX-FileCopyrightText: 2023 Pete Warden
# SPDX-License-Identifier: Apache-2.0
#
# Example of accessing the Tiny Code Reader from Useful Sensors on a Trinkey
# using CircuitPython. See https://usfl.ink/tcr_dev for the full developer guide.
# Modified by Kevin McAleer to run on standard MicroPython (original code was CircuitPython)


from machine import I2C, Pin
import struct
import time

# The code reader has the I2C ID of hex 0c, or decimal 12.
TINY_CODE_READER_I2C_ADDRESS = 0x0C

# How long to pause between sensor polls.
TINY_CODE_READER_DELAY = 0.2

TINY_CODE_READER_LENGTH_OFFSET = 0
TINY_CODE_READER_LENGTH_FORMAT = "H"
TINY_CODE_READER_MESSAGE_OFFSET = TINY_CODE_READER_LENGTH_OFFSET + struct.calcsize(TINY_CODE_READER_LENGTH_FORMAT)
TINY_CODE_READER_MESSAGE_SIZE = 254
TINY_CODE_READER_MESSAGE_FORMAT = "B" * TINY_CODE_READER_MESSAGE_SIZE
TINY_CODE_READER_I2C_FORMAT = TINY_CODE_READER_LENGTH_FORMAT + TINY_CODE_READER_MESSAGE_FORMAT
TINY_CODE_READER_I2C_BYTE_COUNT = struct.calcsize(TINY_CODE_READER_I2C_FORMAT)

i2c = I2C(id=0,sda=Pin(4),scl=Pin(5))

last_message_string = None
last_code_time = 0.0

while True:
    read_data = bytearray(TINY_CODE_READER_I2C_BYTE_COUNT)
    i2c.readfrom_into(TINY_CODE_READER_I2C_ADDRESS, read_data)

    message_length,  = struct.unpack_from(TINY_CODE_READER_LENGTH_FORMAT, read_data, TINY_CODE_READER_LENGTH_OFFSET)
    message_bytes = struct.unpack_from(TINY_CODE_READER_MESSAGE_FORMAT, read_data, TINY_CODE_READER_MESSAGE_OFFSET)

    if message_length > 0:
        message_string = bytearray(message_bytes)[0:message_length].decode("utf-8")
        is_same = (message_string == last_message_string)
        last_message_string = message_string
        current_time = time.time()
        time_since_last_code = current_time - last_code_time
        last_code_time = current_time
        # Debounce the input by making sure there's been a gap in time since we
        # last saw this code.
        if (not is_same) or (time_since_last_code > 1.0):
            print(message_string)
         
            
