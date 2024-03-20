
# Prof Tallman
# Helper class for the DHT11 temperature and humidity sensor.
#
# Designed after consulting the Arduino DHT sensor library v1.4.6 source code
# in C++ and referencing the AM2302 DHT22 datasheet. Borrowed some ideas from
# Zoltan Szarvas's 100% Python dht11 module that is available on PyPi. Tested
# on the Raspberry 4 model B using the DHT11 device that comes with the Elegoo
# "The Most Complete" starter kit.
#
# https://www.arduino.cc/reference/en/libraries/dht-sensor-library/
# https://datasheetspdf.com/datasheet/AM2302.html
# https://pypi.org/project/dht11/

import statistics as stats
import RPi.GPIO as GPIO
from time import sleep, time

class DHT11:
    '''
    Reads temperature and humidity data from a DHT11 device. This object will
    cache its readings from the DHT11 device. Frequent queries will not read
    return a live value every time. Cached values will sometimes be returned
    instead. The constructor takes a wait period to control the cached value.
    '''

    # The DHT11 device shares a single pin that the host uses to initiate
    # temperature readings and the device uses to communicate data. Since both
    # the host and sensor drive the same signal, it's important that we hold
    # off on the host to avoid a situation where both the host and sensor are
    # driving opposite values. According to the datasheet, a full read from
    # the sensor takes 2 seconds, but our code runs a bit slower on purpose, 
    # so we will wait a full 5 seconds between all read operations.
    _DEFAULT_CACHE_WAIT_SECONDS = 5
    DEG_SYMBOL = '°'

    def __init__(self, data_pin, cache_wait_period=_DEFAULT_CACHE_WAIT_SECONDS):
        '''
        Creates a new DHT11 object.
        
        Read data from the sensor using the `temperature_c`, `temperature_f`, 
        and `humidity` properties. This object caches temperature readings for
        a short period rather than taking live readings every time that the
        properties are invoked. Determine how much time has passed since the
        last live reading with the `seconds_since_last_reading` property.

        If communication with the device fails before reading any valid sensor
        data, all the properties will return None.

        Args:
         - data_pin: The GPIO pin number connected to the DHT11
         - cache_wait_period: Controls how long data is cached before the
         class makes a new reading from the device. Set `None` to disable
         the cache completely and make live reads every time.
        '''
        GPIO.setmode(GPIO.BCM)
        self._dht11_pin = data_pin
        self._wait_period_seconds = cache_wait_period
        self._last_read_time = None
        self._last_temperature = None
        self._last_humidity = None

        # Calculate how long our code should try to read the DHT11 device
        # before timing out. The DHT11 timing is very precise; a CPU context
        # switch might cause us to miss a read operation. This calculation
        # determines how long to wait before giving up.
        #
        # The DHT11 device uses a LOW to HIGH signal to transmit serial data.
        # If the LOW to HIGH signal lasted for 75us it means the device sent
        # a zero whereas a LOW to HIGH signal that lasts for 120us means that
        # the device sent a one. Therefore, if our code detects no signal
        # changes over 150us, it means that our code lost the DHT11 signal.
        #
        # We can't detect the passing of 150us with a direct time measurment
        # because the call to time.sleep() is often slower than 150us on a
        # Raspberry Pi 4B. Instead, we calculate how many times a tight loop
        # will iterate in 150us. Then we set this upper bound on the loops
        # used in all of our read operations.

        wait_period_seconds = 0.000150 # 150us
        loop_iteration_time = self._stopwatch_gpio_input_operation()
        self._wait_cycles = int(wait_period_seconds // loop_iteration_time)

        # Take an initial reading
        self._last_temperature, self._last_humidity = self._read_sensor()
        return


    def __del__(self):
        ''' Object destructor cleans up GPIO pins on the Raspberry Pi. '''
        GPIO.cleanup()
        return


    def __str__(self):
        if self.seconds_since_last_reading is None:
            return f"DHT11 object on GPIO pin {self._dht11_pin} has never been read."
        else:
            return (f"DHT11 object on GPIO pin {self._dht11_pin} last reading was" + 
                    f" {self.seconds_since_last_reading}s ago")


    @property
    def temperature_c(self):
        '''
        Returns the temperature in Degrees Celcius. If an error occurs while
        taking a reading and no cached value exists, the function will return
        `None`.
        '''
        if (self._last_read_time is None
            or self._wait_period_seconds is None
            or self.seconds_since_last_reading > self._wait_period_seconds):
                self._read_sensor()
        return self._last_temperature


    @property
    def temperature_f(self):
        '''
        Returns the temperature in Degrees Farenheit. If an error occurs while
        taking a reading and no cached value exists, the function will return
        `None`.
        '''
        return self.temperature_c * 1.8 + 32


    @property
    def humidity(self):
        '''
        Returns the humidity as a percentage. If an error occurs while taking
        a reading and no cached value exists, the function will return `None`.
        '''
        if (self._last_read_time is None
            or self._wait_period_seconds is None
            or self.seconds_since_last_reading > self._wait_period_seconds):
                self._read_sensor()
        return self._last_humidity


    @property
    def seconds_since_last_reading(self):
        '''
        Returns the number of seconds since the last true sensor reading. If
        the sensor has never been read, the function will return `None`.
        '''
        if self._last_read_time:
            return int(time() - self._last_read_time)
        else:
            return None


    def _stopwatch_gpio_input_operation(self):
        '''
        Measures the length of time to execute a single GPIO read operation
        on the computer that is running this code. This function averages the
        duration of many GPIO read operations performed in a tight loop.
        '''
        GPIO.setup(self._dht11_pin, GPIO.IN, GPIO.PUD_UP)
        start_time = time()
        gpio_loop_count = 10000
        for i in range(gpio_loop_count):
            GPIO.input(self._dht11_pin)
        end_time = time()
        elapsed_time = end_time - start_time
        gpio_read_time = elapsed_time / gpio_loop_count
        return gpio_read_time


    def _read_sensor(self):
        '''
        Reads the current temperature and humidity levels from the device.
        Instead of returning a value, this function sets the object's last
        temperature and last humidity values.

        This method is private; it is not meant to be called directly because
        it circumvents the built-in cache.
        '''
        
        # Send a read request to the DHT11 sensor
        # The datasheet explains that a HIGH signal is the 'free status'
        # and to initiate a read, we must pull the signal low for at least
        # 1-10ms. We pull low for 20ms just to be safe.

        GPIO.setup(self._dht11_pin, GPIO.OUT)
        GPIO.output(self._dht11_pin, GPIO.HIGH)
        sleep(0.050) # 'free state' for at least 50ms should be sufficient 
        GPIO.output(self._dht11_pin, GPIO.LOW)
        sleep(0.020)

        # Receive the humidity and temperature reading from the DHT11 sensor
        # If an error occured, return the last valid reading
        #
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
        #
        # Loop until we receive a prolonged signal that does not toggle btw
        # 0/1. Within the loop we cound how many iterations pass until the
        # signal toggles. Once it toggles we store the count and reset our
        # counter. Repeat until reaching that prolonged constant signal.

        GPIO.setup(self._dht11_pin, GPIO.IN, GPIO.PUD_UP)        
        prev = GPIO.input(self._dht11_pin)
        raw_signal_counts = []
        repeats = 0
        
        while repeats < self._wait_cycles:
            curr = GPIO.input(self._dht11_pin)
            if curr == prev:
                repeats += 1
            else:
                raw_signal_counts.append(repeats)
                repeats = 0
                prev = curr
        
        # Converts the raw signal counts to a sequence of bits from the form:
        #   LOW - HIIIIIGH - LOW - HI - LOW - HI - LOW HIIIIGH...
        # The LOW signals should always stay low for the same length of time
        # whereas the HIGH signals are either short or long depending on if
        # the sensor is transmitting a 0 or a 1.
        #
        # If the HIGH signal lasted for a longer duration than the LOW signal,
        # it means the sensor transmitted a 1. Conversly, if the sensor held 
        # signal HIGH for a shorter duration than the LOW signal, it means the
        # sensor transmitted a one. HIGH signals always *follow* LOW signals.

        if len(raw_signal_counts) < 80:
            #raise EOFError(f"Did not read 80 signals ({len(raw)})")
            return

        odds = raw_signal_counts[-79::2]
        evens = raw_signal_counts[-80::2]
        if stats.stdev(odds) > stats.stdev(evens):
            high_signals = odds
            low_signal_time = stats.mean(evens)
        else:
            high_signals = evens
            low_signal_time = stats.mean(odds)
        bits = [1 if value > low_signal_time else 0 for value in high_signals]

        # Verify the integrity of the data we just read using algorithm from
        # the DHT11 datasheet

        data = self._bits_to_bytes(bits)
        checksum = (data[0] + data[1] + data[2] + data[3]) & 255
        if data[4] != checksum:
            #raise ValueError(f"Calculated checksum '{checksum}' did not " +
            #                 f"match given checksum '{data[4]}'")
            return

        # Convert the received data to humidity and temperature values and
        # store internally within the object

        self._last_humidity = data[0] + data[1] * 0.1
        self._last_temperature = data[2] + data[3] * 0.1
        self._last_read_time = time()
        return
    

    def _convert_raw_to_bits(self, raw):
        '''
        Converts the raw signal counts to a sequence of bits.
        
        Returns a list of bits having either value 0 or 1.
        '''

        # See _read_sensor function for more information
        odds = raw[-79::2]
        evens = raw[-80::2]
        if stats.stdev(odds) > stats.stdev(evens):
            signals = odds
            limit = stats.mean(evens)
        else:
            signals = evens
            limit = stats.mean(odds)
        return [1 if value > limit else 0 for value in signals]


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

def demo():
    ''' Test program to demonstrate the DHT11 object '''
    dht = DHT11(_DHT_PIN)
    print(f'{dht.temperature_c:.2f}{DHT11.DEG_SYMBOL}C / ' +
          f'{dht.temperature_f:.2f}{DHT11.DEG_SYMBOL}F')
    print(f'{dht.humidity}%')

if __name__ == '__main__':
    try:
        demo()
    except KeyboardInterrupt:
        print(f" User quit with <CTRL+C>")
