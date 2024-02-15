
# Prof Tallman
# Helper class and demo code for working with the LCD1602 device from Elegoo.

import RPi.GPIO as GPIO
from time import sleep, time

class DHT11:
    
    _DHT_STATE_IDLE = 0
    _DHT_STATE_SETUP = 1
    _DHT_STATE_SIGNAL_READ = 2
    _DHT_STATE_TAKE_READING = 3
    _DHT_STATE_COOLDOWN = 4

    _DHT11_DELAY_SIGNAL_READ = 0.250  # 250 ms
    _DHT11_DELAY_TAKE_READING = 0.050 # 50 ms
    _DHT11_DELAY_TIMEOUT = 0.000100   # 100 us
    _DHT11_DELAY_COOLDOWN = 2
    _DHT11_DEFAULT_WAIT_PERIOD = 5    # seconds

    def __init__(self, data_pin, wait_period=_DHT11_DEFAULT_WAIT_PERIOD):
        ''' Create and initialize a new DHT11 object. '''
        GPIO.setmode(GPIO.BCM)
        self._pin = data_pin
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, GPIO.HIGH)
        self._state = DHT11._DHT_CMD_IDLE
        self._time = time()
        self._data = 0
        self._wait_period = wait_period
        self._temperature = None
        self._humidity = None
        
    def __del__(self):
        ''' Object destructor cleans up GPIO pins on the Raspberry Pi. '''
        GPIO.cleanup()

    @property
    def temperature(self):

        # If the last reading is stale, make a new reading
        delay = time() - self._time
        if delay > self._wait_period:    
            self._temperature, self._humidity = self._read_sensor()
        return self._temperature
    
    @property
    def humidity(self):

        # If the last reading is stale, make a new reading
        delay = time() - self._time
        if delay > self._wait_period:    
            self._temperature, self._humidity = self._read_sensor()
        return self._humidity
    

    def _read_sensor(self):

        data = []
        time_in_seconds = time()
        
        # pull_up_down=GPIO.PUD_UP
        # Begin by asserting the signal for seconds 250ms (think: reset)
        # Most recent Android code 1.4.6 sets as input and lets pullup resistor change to high
        #GPIO.setup(self._pin, GPIO.OUT, GPIO.PULLUP)
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, GPIO.HIGH)
        sleep(DHT11._DHT11_DELAY_SIGNAL_READ)

        # Signal that we're starting a reading by clearing the signal for 20ms
        GPIO.output(self._pin, GPIO.LOW)
        sleep(DHT11._DHT11_DELAY_TAKE_READING)

        # End the start signal by setting signal high
        GPIO.output(self._pin, GPIO.HIGH)
        sleep(DHT11._DHT11_DELAY_TAKE_READING)

        # This should be atomic... do we dare create a new thread?

        # Signal prolog starts with 80us LOW followed by 80us HIGH
        time_in_seconds = time()
        while GPIO.read(self._pin) == GPIO.LOW:
            if time() - time_in_seconds > DHT11._DHT11_DELAY_TIMEOUT:
                print(f"Reading SETUP A failed")
                break
        
        time_in_seconds = time()
        while GPIO.read(self._pin) == GPIO.HIGH:
            if time() - time_in_seconds > DHT11._DHT11_DELAY_TIMEOUT:
                print(f"Reading SETUP B failed")
                break

        base = []
        data = []
        for i in range(40):
            self._time = time()
            while GPIO.read(self._pin) == GPIO.LOW:
                delay = time() - self._time
                if delay > DHT11.DHT11_DELAY_TIMEOUT:
                    print(f"Reading BIT {i} A failed")
                    break
            base.append(delay)
            
            self._time = time()
            while GPIO.read(self._pin) == GPIO.HIGH:
                delay = time() - self._time
                if delay > DHT11.DHT11_DELAY_TIMEOUT:
                    print(f"Reading BIT {i} B failed")
                    break
            data.append(time())

        print(base)
        print(data)

        bits = []
        assert len(base) == len(data)
        for i in range(len(base)):
            if data < base:
                bit = 0
            else:
                bit = 1
            bits.append(bit)
            print(f"{int(1000000 * base)} {int(1000000 * delay)} {bit}")
        
        print(bits)





    def _read_state_state(self):

        if self._state == DHT11._DHT_STATE_IDLE:
            self._state == DHT11._DHT_STATE_SETUP
            
        elif self._state == DHT11._DHT_STATE_SETUP:
            GPIO.setup(self._pin, GPIO.OUT)
            GPIO.output(self._pin, GPIO.HIGH)
            self._data = 0
            self._time = time()
            self._state == DHT11._DHT_STATE_SIGNAL_READ

        elif self._state == DHT11._DHT_STATE_SIGNAL_READ:
            if time() - self._time > DHT11._DHT11_DELAY_SIGNAL_READ:
                # Pin should still be output from previous state
                GPIO.setup(self._pin, GPIO.OUT)
                GPIO.output(self._pin, GPIO.LOW)
                self._time = time()
                self._state = DHT11._DHT_STATE_TAKE_READING
            
        elif self._state == DHT11._DHT_STATE_TAKE_READING:
            if time() - self._time > DHT11._DHT11_DELAY_TAKE_READING:
                # This should be atomic... do we dare create a new thread?
                GPIO.setup(self._pin, GPIO.OUT)
                GPIO.output(self._pin, GPIO.HIGH)
                sleep(0.000040)
                GPIO.setup(self._pin, GPIO.IN)
                sleep(0.000010)
                
                self._time = time()
                while GPIO.read(self._pin) == GPIO.LOW:
                    if time() - self._time > DHT11._DHT11_DELAY_TIMEOUT:
                        print(f"Reading SETUP A failed")
                        break
                
                self._time = time()
                while GPIO.read(self._pin) == GPIO.HIGH:
                    if time() - self._time > DHT11._DHT11_DELAY_TIMEOUT:
                        print(f"Reading SETUP B failed")
                        break

                base = []
                data = []
                for i in range(40):
                    self._time = time()
                    while GPIO.read(self._pin) == GPIO.LOW:
                        delay = time() - self._time
                        if delay > DHT11.DHT11_DELAY_TIMEOUT:
                            print(f"Reading BIT {i} A failed")
                            break
                    base.append(delay)
                    
                    self._time = time()
                    while GPIO.read(self._pin) == GPIO.HIGH:
                        delay = time() - self._time
                        if delay > DHT11.DHT11_DELAY_TIMEOUT:
                            print(f"Reading BIT {i} B failed")
                            break
                    data.append(time())


                self._time = time()
                self._state = DHT11._DHT_STATE_COOLDOWN

        elif self._state == DHT11._DHT_STATE_COOLDOWN:
            if time() - self._time > DHT11._DHT11_DELAY_COOLDOWN:
                self._state = DHT11._DHT_STATE_IDLE

###############################################################################



def main():
    ''' Test program to demonstrate the LCD1602 object '''
    dht = DHT11(26)
    dht._read_state()
    print("DONE")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f" User quit with <CTRL+C>")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print(f"Program completed successfully")