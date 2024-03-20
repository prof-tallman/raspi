
# Prof Tallman
# Helper class for working with a 74HC165 8-bit parallel to serial converter.
#
# Used the Texas Instruments datasheets to understand the pins and timing.
# https://www.ti.com/lit/ds/symlink/sn74hc165.pdf
#
# Thanks to Martijn at Stackoverflow for demonstrating how to quickly convert
# a bit array to an integer. Although I have written similar bit-shifting code
# in the past, my version converted a bit array to a Python byte string, and
# byte strings just seemed to be the wrong datatype for this class. It was 
# late at night when I wrote this module and I didn't want to think about the
# differences between byte strings to integers, so I used Martijn's code.
# https://stackoverflow.com/questions/12461361/bits-list-to-integer-in-python

import RPi.GPIO as GPIO
from time import sleep, time

class SN74HC165:
    '''
    Reads an 8-bit parallel input through a serial connection that uses three
    pins. This class was designed for a particular integrated circuit, the 
    SN74HC165. The implementation details are well within the specifications
    for the SN74HC165, so the class *should* work fine on slower 8-bit parallel
    to serial converters, as long as their input signals behave the same way.
    '''

    # Datasheets indicate 225ns to be the longest switching delay for the 74HC165, 
    # which is encountered at a 2V operating voltage. I used 10us instead because
    # it's longer than the 225ns but seemed fast enough for most Python code.
    _DELAY_TIME_SECONDS = 0.000010 # 10us

    def __init__(self, clock_pin, shift_pin, data_pin):
        '''
        Creates a new SN74HC165 object. No special purpose pins are necessary.
        Every connection can be through a standard GPIO pin.

        Args:
         - clock_pin: Rasberry Pi pin connected to the 74HC165's clock
         - shift_pin: Rasberry Pi pin connected to the 74HC165's SH/^LD
         - data_pin: Rasberry Pi pin connected to the 74HC165's Q output
        '''
        self._clock_pin = clock_pin
        self._shift_pin = shift_pin
        self._data_pin = data_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._data_pin, GPIO.IN, GPIO.PUD_DOWN) # PUD_OFF?
        GPIO.setup(self._clock_pin, GPIO.OUT)
        GPIO.setup(self._shift_pin, GPIO.OUT)
        GPIO.output(self._shift_pin, GPIO.HIGH)
        return


    def __del__(self):
        ''' Object destructor cleans up GPIO pins on the Raspberry Pi. '''
        GPIO.cleanup()
        return
    

    def __str__(self):
        return (f"SN74HC165 object on GPIO pins {self._clock_pin} (CLK)," +
                f" {self._shift_pin} (SH/^LD), and {self._data_pin} (Q)")

    
    @property
    def read(self):
        '''
        Reads all eight of the parallel binary inputs and returns their values
        as an 8-element binary list. Input "A" on the SN74HC165 is at index 0
        in the list and input "H" is at index 7.
        '''
        parallel_data = [ 0, 0, 0, 0, 0, 0, 0, 0 ]

        # Latch the eight input bits into the SN74HC165.
        # Set LOW to latch the inputs and the back HIGH to send serial data.
        GPIO.output(self._shift_pin, GPIO.LOW)
        sleep(SN74HC165._DELAY_TIME_SECONDS)
        GPIO.output(self._shift_pin, GPIO.HIGH)

        # Read the serial output 1 bit at a time from the SN74HC165.
        # The datasheet says that clocking occurs on low to high transition
        # but experiments show that the signal was most accurate just prior
        # to the L->H clock transition.
        for i in range(8):
            GPIO.output(self._clock_pin, GPIO.LOW)
            sleep(SN74HC165._DELAY_TIME_SECONDS)
            parallel_data[i] = GPIO.input(self._data_pin)
            GPIO.output(self._clock_pin, GPIO.HIGH)
            sleep(SN74HC165._DELAY_TIME_SECONDS)

        return parallel_data
    
    @property
    def read_byte(self):
        '''
        Reads all eight of the parallel binary inputs and returns their value
        as an integer. Input "A" on the SN74HC165 corresponds to bit 7 of the
        return value (most significant) and input "H" corresponds to bit 0
        (the least significant bit).
        '''
        parallel_data = 0
        for bit in self.read():
            parallel_data = (parallel_data << 1) | bit
        return parallel_data

###############################################################################

_CLOCK_PIN = 20
_READ_PIN = 21
_DATA_PIN = 16

def demo():
    device = SN74HC165(_CLOCK_PIN, _READ_PIN, _DATA_PIN)
    print(device.read)
    print(device.read_byte)

if __name__ == '__main__':
    demo()


