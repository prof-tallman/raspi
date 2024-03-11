
# Prof Tallman
# Helper class and demo code for working with the LCD1602 device from Elegoo.
#
# https://michaelriedl.com/2022/08/06/rpi-virtualenv.html
# Thanks to Michael Riedl's blog for help with the Python Virtual Environment
# 
# joshau@yosemite:~ $ sudo apt install python3-virtualenv
# joshua@yosemite:~ $ virtualenv venv
# joshua@yosemite:~ $ source venv/bin/activate
# (venv) joshua@yosemite:~ $ pip install RPi.GPIO
# (venv) joshua@yosemite:~ $ 
#
# https://robsraspberrypi.blogspot.com/2016/01/raspberry-pi-controlling-16-x-2-lcd.html
# Thanks to Rob's Raspberry Pi blog for help controlling the LCD with RPi.GPIO
#
# There were other wrappers such as the Adafruit_CharLCD, but I decided on to
# go with RPi.GPIO. Rob used a POWERTIP PC1602LRS-FWA-B-Q LCD which seems to
# have different control codes than my LCD1602 that came from Elegoo. It's
# hard to tell exactly because Rob did not identify the flags that he used.
#
# https://datasheetspdf.com/pdf-files/866421/Qingyuninnovative/LCM1602A/1
# Used the Qingyun datasheet to track down the function codes for our LCD and
# looked at the LiquidCrystal.cpp/.h source code that came with the Elegoo kit
# when the datasheet was hard to follow.
#
# https://raspi.tv/2013/rpi-gpio-basics-3-how-to-exit-gpio-programs-cleanly-avoid-warnings-and-protect-your-pi
# Thanks to Alex Eames of RasPi.TV for a reminder about cleaning up the GPIO
# pins correctly with a 'finally' block to avoid burning out the circuit.
#
# https://stackoverflow.com/questions/842059/is-there-a-portable-way-to-get-the-current-username-in-python
# Thanks to Mateen Ulhaq for explaining how to get the current username in a
# way that is cross-platform and built in to the default Python install.

from datetime import datetime
import socket
import getpass
import RPi.GPIO as GPIO
from time import sleep

class LCD1602:
    
    # RAM address for the 1st and 2nd lines (per Rob)
    _LCD_LINE_1 = 0x80
    _LCD_LINE_2 = 0xC0
    _LCD_WIDTH = 16

    # LCD command codes and flags (per datasheet)
    _LCD_FUNC_SET_FUNCTION = 0x20
    _LCD_OPTION_4BIT = 0x00
    _LCD_OPTION_8BIT = 0x10
    _LCD_OPTION_1LINE = 0x00
    _LCD_OPTION_2LINE = 0x08
    _LCD_OPTION_5X8FONT = 0x00
    _LCD_OPTION_5X10FONT = 0x04

    _LCD_FUNC_CURSOR_SHIFT = 0x10
    _LCD_OPTION_DISPLAY_MOVE = 0x08
    _LCD_OPTION_CURSOR_MOVE = 0x00
    _LCD_OPTION_MOVE_RIGHT = 0x04
    _LCD_OPTION_MOVE_LEFT = 0x00

    _LCD_FUNC_SET_DISPLAY = 0x08
    _LCD_OPTION_DISPLAY_OFF = 0x00
    _LCD_OPTION_DISPLAY_ON = 0x04
    _LCD_OPTION_CURSOR_OFF = 0x00
    _LCD_OPTION_CURSOR_ON = 0x02
    _LCD_OPTION_BLINK_OFF = 0x00
    _LCD_OPTION_BLINK_ON = 0x01

    _LCD_FUNC_SET_ENTRYMODE = 0x04
    _LCD_OPTION_R_TO_L = 0x00
    _LCD_OPTION_L_TO_R = 0x02
    _LCD_OPTION_NO_SHIFT = 0x00
    _LCD_OPTION_SHIFT = 0x01

    _LCD_FUNC_RETURN_HOME = 0x02
    _LCD_FUNC_CLEAR_DISPLAY = 0x01

    # LCD hold times, rounded up (per datasheet)
    _LCD_SETUP_TIME = 0.05000    # 50ms
    _LCD_PULSE_TIME = 0.00005    # 50us
    _LCD_DATA_MODE = True
    _LCD_CMD_MODE = False

    def __init__(self, rs_pin, en_pin, d4_pin, d5_pin, d6_pin, d7_pin):
        ''' Create and initialize a new LCD1602 object. '''
        GPIO.setmode(GPIO.BCM)
        self._rs = rs_pin
        self._en = en_pin
        self._d4 = d4_pin
        self._d5 = d5_pin
        self._d6 = d6_pin
        self._d7 = d7_pin
        self._init_device()

    def __del__(self):
        ''' Object destructor cleans up GPIO pins on the Raspberry Pi. '''
        GPIO.cleanup()

    def _init_device(self):
        '''
        Low-level initialization routine that configures the LCD1602 to work
        in 4-bit, 2-line, 5x8 font, L-to-R mode and clears the display.
        '''
        # Configure the Raspberry Pi pins
        GPIO.setup(self._en, GPIO.OUT)
        GPIO.setup(self._rs, GPIO.OUT)
        GPIO.setup(self._d4, GPIO.OUT)
        GPIO.setup(self._d5, GPIO.OUT)
        GPIO.setup(self._d6, GPIO.OUT)
        GPIO.setup(self._d7, GPIO.OUT)
        
        # Initialize the device by sending the first command multiple times
        GPIO.output(self._rs, False)
        GPIO.output(self._en, False)
        self._send_command(LCD1602._LCD_FUNC_RETURN_HOME |
                           LCD1602._LCD_FUNC_CLEAR_DISPLAY)
        self._send_command(LCD1602._LCD_FUNC_RETURN_HOME)
        
        # Set to 4-bit mode with cursor off, L -> R text
        self._send_command(LCD1602._LCD_FUNC_SET_FUNCTION |
                    LCD1602._LCD_OPTION_4BIT |
                    LCD1602._LCD_OPTION_2LINE | 
                    LCD1602._LCD_OPTION_5X8FONT)
        self._send_command(LCD1602._LCD_FUNC_SET_DISPLAY | 
                    LCD1602._LCD_OPTION_DISPLAY_ON |
                    LCD1602._LCD_OPTION_CURSOR_ON |
                    LCD1602._LCD_OPTION_BLINK_ON)
        self._send_command(LCD1602._LCD_FUNC_SET_ENTRYMODE | 
                    LCD1602._LCD_OPTION_L_TO_R |
                    LCD1602._LCD_OPTION_NO_SHIFT)
        self._send_command(LCD1602._LCD_FUNC_CLEAR_DISPLAY)

    def _send_command(self, command):
        ''' Sends an 8-bit control command to the LCD1602. '''
        self._send_byte(command, LCD1602._LCD_CMD_MODE)
        sleep(LCD1602._LCD_SETUP_TIME)

    def _send_byte(self, data_byte, mode):
        '''
        Write a single byte of data to the LCD1602.
        Args:
         - data_byte: value to be written to the device
         - mode: True for display bytes and False for command codes
        '''
        # LCD character mode vs !command mode
        GPIO.output(self._rs, mode)

        # Set values for the high nibble
        GPIO.output(self._d7, data_byte & 0x80 > 0)
        GPIO.output(self._d6, data_byte & 0x40 > 0)
        GPIO.output(self._d5, data_byte & 0x20 > 0)
        GPIO.output(self._d4, data_byte & 0x10 > 0)
        self._latch_nibble()

        # Set values for the low nibble
        GPIO.output(self._d7, data_byte & 0x08 > 0)
        GPIO.output(self._d6, data_byte & 0x04 > 0)
        GPIO.output(self._d5, data_byte & 0x02 > 0)
        GPIO.output(self._d4, data_byte & 0x01 > 0)
        self._latch_nibble()

    def _latch_nibble(self):
        ''' Writes the current nibble to the LCD1602 device. '''
        sleep(LCD1602._LCD_PULSE_TIME)
        GPIO.output(self._en, True)
        sleep(LCD1602._LCD_PULSE_TIME)
        GPIO.output(self._en, False)
        sleep(LCD1602._LCD_PULSE_TIME)

    def clear_display(self):
        ''' Clears all the text from the LCD1602 device. '''
        self._send_command(LCD1602._LCD_FUNC_CLEAR_DISPLAY)

    def send_string(self, string, line=1):
        ''' 
        Displays a string on the LCD1602 device.
        Args:
         - string: the value to display (truncated to 16 chars)
        '''
        if line == 1:
            self._send_command(LCD1602._LCD_LINE_1)
        elif line == 2:
            self._send_command(LCD1602._LCD_LINE_2)
        else:
            print(f"WARNING: LCD1602 device cannot display on line {line}")
            return
        string = string[:LCD1602._LCD_WIDTH].ljust(LCD1602._LCD_WIDTH, ' ')
        for ch in string:
            self._send_byte(ord(ch), LCD1602._LCD_DATA_MODE)

###############################################################################

LCD_RS = 5
LCD_EN = 6
LCD_D4 = 17
LCD_D5 = 27
LCD_D6 = 23
LCD_D7 = 22

def main():
    ''' Test program to demonstrate the LCD1602 object '''
    lcd = LCD1602(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7)
    hostname = socket.gethostname()
    username = getpass.getuser()
    while(True):
        lcd.send_string(f"{username}@{hostname}", 1)
        lcd.send_string(f"{datetime.now():%a %b %d %H:%m}", 2)
        sleep(5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f" User quit with <CTRL+C>")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print(f"Program completed successfully")