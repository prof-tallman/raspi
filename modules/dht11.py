
# Prof Tallman
# Helper class and demo for the DHT11 temperature and humidity sensor.
#
# Designed after consulting the Arduino DHT sensor library v1.4.6 source code
# in C++ and referencing the AM2302 DHT22 datasheet. Borrowed some ideas from
# Zoltan Szarvas's 100% Python dht11 module that is available on PyPi. Tested
# on the Raspberry 4 model B using the DHT11 device that comes with the Elegoo
# "The Most Complete" starter kit.
#
# https://www.arduino.cc/reference/en/libraries/dht-sensor-library/
# https://cdn-shop.adafruit.com/datasheets/Digital%20humidity%20and%20temperature%20sensor%20AM2302.pdf
# https://pypi.org/project/dht11/

import statistics as stats
import RPi.GPIO as GPIO
from time import sleep, time


###############################################################################


class DHT11:
    ''' Reads temperature and humidity data from a DHT11 device. '''
    DEG_SYMBOL = '°'
    _DEFAULT_WAIT_SECONDS = 5

    def __init__(self, data_pin, wait_seconds=_DEFAULT_WAIT_SECONDS):
        '''
        Create and initialize a new DHT11 object.

        Args:
         - data_pin: the GPIO pin number connected to the DHT11
         - wait_seconds: controls how long data is cached before the object
         makes a new reading from the device
        '''
        GPIO.setmode(GPIO.BCM)
        self._pin = data_pin
        self._wait_period = wait_seconds
        self._temperature = None
        self._humidity = None
        self._valid_data = False
        self._read_time = None

        # To complete a read operation, the device sends 40 bits of serial
        # data in a row. According to the datasheet, 0s will take 75us and
        # 1s take 120us (50us LOW setup followed by 25us HIGH signal vs 50us
        # LOW setup followed by a 70us HIGH signal). After the 40 bits have
        # been transferred, the device will hold a steady signal. This module
        # assumes that if 150us have passed without a change in signal that
        # the transfer is complete.
        #
        # But we don't measure the passing of time by actually measuring time.
        # Instead, we count the number of iteratons through a loop and then
        # estimate how much time that represents (it's a faster operation
        # then calling time()). To make the estimate accurate, we need to
        # measure the length of time for a single GPIO.input operation and
        # then calculate how many input operations it takes to fill 150us.

        hold_period_seconds = 0.000150 # 150us
        self._gpio_read_time = self._stopwatch_gpio_input_operation()
        self._wait_cycles = int(hold_period_seconds // self._gpio_read_time)

        # Take an initial reading
        self._temperature, self._humidity = self.read_sensor()
        return


    def __del__(self):
        ''' Object destructor cleans up GPIO pins on the Raspberry Pi. '''
        GPIO.cleanup()
        return


    @property
    def temperature_c(self):
        ''' Temperature in Degrees Celcius. '''
        if not self._read_time or self.last_reading > self._wait_period:
            self._temperature, self._humidity = self.read_sensor()
        return self._temperature

    @property
    def temperature_f(self):
        ''' Temperature in Degrees Farenheit. '''
        return self.temperature_c * 1.8 + 32

    @property
    def humidity(self):
        ''' Humidity as a percentage. '''
        if not self._read_time or self.last_reading > self._wait_period:
            self._temperature, self._humidity = self.read_sensor()
        return self._humidity
    
    @property
    def valid_reading(self):
        ''' Returns whether the temperature and humidity values are valid. '''
        return self._valid_data

    @property
    def last_reading(self):
        ''' Number of seconds since the last true sensor reading. '''
        if self._read_time:
            return int(time() - self._read_time)
        else:
            return None
           

    def _stopwatch_gpio_input_operation(self):
        '''
        Measures the length of time to execute a single GPIO read operation.
        '''
        GPIO.setup(self._pin, GPIO.IN, GPIO.PUD_UP)
        start_time = time()
        gpio_loop_count = 10000
        for i in range(gpio_loop_count):
            GPIO.input(self._pin)
        end_time = time()
        elapsed_time = end_time - start_time
        gpio_read_time = elapsed_time / gpio_loop_count
        return gpio_read_time


    def read_sensor(self):
        '''
        Reads the current temperature and humidity levels from the device.
        Although this method is exposed publically, it is not meant to be
        called directly because it circumvents the object's built-in cache.

        Returns a tuple (temperature °C, humidity %)
        '''
        
        # Send a read request to the sensor and then parse the response
        self._request_sensor_data()
        raw = self._receive_data_stream()
        if len(raw) < 80:
            raise EOFError(f"Did not read 80 signals ({len(raw)})")
        bits = self._convert_raw_to_bits(raw)
        data = self._bits_to_bytes(bits)
        checksum = self._calculate_checksum(data)
        if data[4] != checksum:
            raise ValueError(f"Calculated checksum '{checksum}' did not " +
                             f"match given checksum '{data[4]}'")

        # Convert the received data to humidity and temperature values
        humidity = data[0] + data[1] * 0.1
        temperature = data[2] + data[3] * 0.1
        self._valid_data = True
        self._read_time = time()
        return (temperature, humidity)


    def _request_sensor_data(self):
        ''' Signal the DHT11 device that we want a sensor reading. '''
        # Signal the DHT11 that we want a temperature & humidity reading
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, GPIO.HIGH)
        sleep(0.050) 
        GPIO.output(self._pin, GPIO.LOW)
        sleep(0.020)
        return


    def _receive_data_stream(self):
        '''
        Read the DHT11 signal from the GPIO pin.
        
        Returns a list of counts that indicate how long the signal stayed
        high or low. The list alternates between a series of calibration
        values and the actual low/high signals. Signals that are larger than
        the calibration values correspond to logical 1s and signals with
        counts lower than the calibration values reperesent logical 0s.
        '''

        # Reading the datasheet, the information contained in the DHT11 signal
        # is largely time-based. The device will alternate between LOW and
        # HIGH. The LOW periods last for 50us and are markers to separate the
        # information. The HIGH period represents a 1 if the signal holds for
        # 70us and it represents a 0 if it is held for 26-28us.
        # 
        # Measuring the time using a Python function call such as time.time()
        # is prohibitively slow on a Raspberry Pi processor. By the time that
        # the function call completes, it is already too late.
        #
        # Zoltan Szarvas uses a different technique that is a little less
        # intuitive but much faster. He creates a fast, tight loop that simply
        # counts the number of iterations between signal changes (LOW->HIGH
        # HIGH->LOW). It doesn't really matter how *many* changes occur, just
        # the relative difference between LOW markers and the HIGH signals
        # that contain information. If the HIGH signal iteration count is 
        # greater than the LOW signal iteration, then it must be 70us signal
        # which represtns a 1. If the HIGH signal iteration count is less than
        # the LOW signal iteration, then it must be a 26-28us signal which
        # represents a 0. Thanks to Zoltan for for the idea.

        GPIO.setup(self._pin, GPIO.IN, GPIO.PUD_UP)        
        prev = GPIO.input(self._pin)
        counts = []
        repeats = 0
        
        # Loop until we receive a prolonged signal that does not toggle btw
        # 0/1. Within the loop we cound how many iterations pass until the
        # signal toggles. Once it toggles we store the count and reset our
        # counter. Repeat until reaching that prolonged constant signal.

        while repeats < self._wait_cycles:
            curr = GPIO.input(self._pin)
            if curr == prev:
                repeats += 1
            else:
                counts.append(repeats)
                repeats = 0
                prev = curr
        return counts
    

    def _convert_raw_to_bits(self, raw):
        '''
        Converts raw signal counts to a sequence of bits.
        
        Returns a list of bits having either value 0 or 1.
        '''
        odds = raw[-79::2]
        evens = raw[-80::2]
        if stats.stdev(odds) > stats.stdev(evens):
            signals = odds
            limit = stats.mean(evens)
        else:
            signals = evens
            limit = stats.mean(odds)
        return [1 if value > limit else 0 for value in signals]


    def _calculate_checksum(self, data):
        ''' Checksum is the sum of the first four bytes. '''
        return 255 & (data[0] + data[1] + data[2] + data[3])        


    def _bits_to_bytes(self, bits):
        '''
        Converts an array of bits (list of integers 0/1) into a byte string.
        For example _bit_to_bytes([1,0,1,0,0,1,0,1]) => b"\xA5"
        '''
        result = []
        byte = 0
        for idx, bit in enumerate(bits):
            pos = idx % 8
            byte += bit << (7 - pos)
            if pos == 7:
                result += [byte]
                byte = 0
        return bytes(result)


###############################################################################


_DHT_PIN = 26

def main():
    ''' Test program to demonstrate the DHT11 object '''
    dht = DHT11(_DHT_PIN)
    print(f'{dht.temperature_c:.2f}{DHT11.DEG_SYMBOL}C / ' +
          f'{dht.temperature_f:.2f}{DHT11.DEG_SYMBOL}F')
    print(f'{dht.humidity}%')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f" User quit with <CTRL+C>")
