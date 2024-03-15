
#
# Prof Tallman
# Helper class and demo for the SN74HC165N 8-bit parallel to serial converter.
#
# Used the Texas Instruments datasheets to understand the pins and timing
#
# Thanks to Martijn for quickly converting a bit array to an integer. I have 
# a bunch of similar code for working with byte strings but thought that an
# 8-bit integer would be better... and it was too late to think through myself
# https://stackoverflow.com/questions/12461361/bits-list-to-integer-in-python
#

import RPi.GPIO as GPIO
from time import sleep, time

_IC_DELAY_TIME_SECONDS = 0.00001

class IO74HC165:
    ''' Reads 8 parallel inputs serially through a 3 pin connection. '''

    def __init__(self, clock_pin, shift_pin, data_pin):
        '''
        Creates a new 74HC165 object. No special purpose pins are necessary.
        Every connection can be through any of the GPIO pins.

        Args
         - clock_pin: Rasberry Pi pin connected to the 74HC165's clock
         - shift_pin: Rasberry Pi pin connected to the 74HC165's SH/^LD
         - data_pin: Rasberry Pi pin connected to the 74HC165's Q output
        '''
        self._clock_pin = clock_pin
        self._shift_pin = shift_pin
        self._data_pin = data_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._clock_pin, GPIO.OUT)
        GPIO.setup(self._shift_pin, GPIO.OUT)
        GPIO.setup(self._data_pin, GPIO.IN, GPIO.PUD_DOWN)
        return

    def __del__(self):
        ''' Object destructor cleans up GPIO pins on the Raspberry Pi. '''
        GPIO.cleanup()
        return
    
    @property
    def read(self):
        ''' Reads 8 parallel inputs as an 8-element binary list. '''
        data = [ 0, 0, 0, 0, 0, 0, 0, 0 ]

        # Latch the parallel inputs
        GPIO.output(self._shift_pin, GPIO.LOW)
        sleep(_IC_DELAY_TIME_SECONDS)
        GPIO.output(self._shift_pin, GPIO.HIGH)

        # Read the serial output 1 bit at a time
        for i in range(8):
            GPIO.output(self._clock_pin, GPIO.LOW)
            sleep(_IC_DELAY_TIME_SECONDS)
            data[i] = GPIO.input(self._data_pin)
            GPIO.output(self._clock_pin, GPIO.HIGH)
            sleep(_IC_DELAY_TIME_SECONDS)

        return data
    
    @property
    def read_byte(self):
        ''' Reads 8 parallel inputs as a single byte value. '''
        data = 0
        for bit in self.read():
            data = (data << 1) | bit
        return data


def main():
    device = IO74HC165(20, 21, 16)
    print(device.read)
    print(device.read_byte)

if __name__ == '__main__':
    main()


