
# Prof Tallman
# Helper class for working with 8x8 LED Matrix. This just wraps an object from
# the Luma module to provide some extra functionality.
#
# The 8x8 LED Matrix communicates using the Serial Peripheral Interface (SPI)
# standard. The Raspberry Pi has special pins that simplify communication with
# SPI devices at the hardware level. Although this capability is not required,
# and any GPIO pins *could* be used, the SPI hardware greatly simplifies the
# burden on the programmer. Here are the steps to use the SPI hardware:
#
# Followed directions at https://luma-led-matrix.readthedocs.io/en/latest/install.html
# to learn how to configure Raspberry Pi and install the proper modules.
#   $ lsmod | grep -i spi     (no spi devices shown)
#   $ sudo raspi-config       (enabled automatic loading of SPI interface)
#   $ sudo reboot now
#   $ lsmod | grep -i spi     (spi_bcm2835)
#   $ ls -l /dev/spi*         (/dev/spidev0.0 & /dev/spidev0.1)
#   $ sudo usermod -a -G spi,gpio joshua
#   $ sudo python3 -m pip install luma.led_matrix
#
# Looked at luma.core.legacy.show_message source to understand font format and
# borrowed an idea from the dji_matrix module that uses a string to create a
# simple bitmap for 8x8 displays. Thanks to DJI Tello Talent Drones for the
# original idea, although I've improved their design to make a nicer interface.
#   https://github.com/damiafuentes/DJITelloPy
# I was stuck trying to convert strings to 1-bit image to PIL image; thanks to
# 'hennes' on Stackoverflow for the PIL code.
#   http://stackoverflow.com/questions/32159076/python-pil-bitmap-png-from-array-with-mode-1

import time
import numpy as np
from PIL import Image
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
import luma.core.legacy as legacy
from luma.core.legacy.font import proportional, LCD_FONT


class MAX7219:

    def __init__(self):
        '''
        Create a connection to an 8x8 LED matrix device.
        
        Pins must be connected as follows for the Luma library:
        - VCC: Pin #2 (or any +5V source)
        - GND: Pin #6 (or any other ground)
        - DIN: Pin #19 which is GPIO 10 (MOSI)
        - CS:  Pin #24 which is GPIO 8 (SPI CE0)
        - CLK: Pin #23 which is GPIO 11 (SPI CLK)
        '''
        self._serial = spi(port=0, device=0, gpio=noop())
        self._device = max7219(self._serial, width=8, height=8, 
                               rotate=2, block_orientation=0)
        return


    def __str__(self):
        return f"MAX7219 object using SPI interface (GPIO pins 10, 8, and 11)"


    def display_text(self, message, delay=0.5, scroll=True):
        '''
        Displays a message on the 8x8 matrix in either scrolling mode or else by
        showing 1 character at a time.

        Args:
        - message: Text string to be displayed
        - delay: The speed at which to show the letters, in seconds
        - scroll: True to scroll the message or False to show 1 letter at a time
        '''
        if scroll:
            legacy.show_message(self._device, message, fill='white', 
                                font=proportional(LCD_FONT), scroll_delay=delay)
        else:
            for ch in message:
                # Each frame of the animation must be inside of a 'with' block and
                # the 'sleep' function must be outside of the block.
                # Center the letter
                with canvas(self._device) as draw:
                    shift = MAX7219._matrix_8x8_xshift(ch, font=LCD_FONT)
                    legacy.text(draw, (shift, 0), ch, fill="white", font=LCD_FONT)
                time.sleep(delay)
        return
        

    def _matrix_8x8_xshift(character, font=LCD_FONT):
        ''' Returns the shift amount to center a character on the 8x8 matrix. '''
        
        # Get the 8x8 dot-matrix code for this character in the given font
        ch = font[ord(character)]

        # Calculate how many empty columns show up on the *left* side
        left_position = 0
        left_count = 0
        while left_position < len(ch) and ch[left_position] == 0:
            left_count += 1
            left_position += 1
        
        # Calculate how many empty columns show up on the *right* side
        right_position = -1
        right_count = 0
        while right_position >= -len(ch) and ch[right_position] == 0:
            right_count += 1
            right_position -= 1
        
        # Center the character by shifting it over half of the R/L difference
        return (right_count - left_count) // 2


    def display_image(self, image_str):
        ''' 
        Displays an 8x8 binary image in the LED display. The image is given
        as a list of strings, one string per row. Spaces ' ' turn the LED off
        and all other characters turn the corresponding LED on.
        
        Args:
        - image_str: the 8x8 image as a sequence of 8 strings in a list. Ex:
            [ '  ****  ',
              ' **  ** ',
              ' **  ** ',
              '  ****  ',
              '   **   ',
              '  ***   ',
              '   **   ',
              '  ***   ' ]
        '''
        pixels = []
        if len(image_str) == 64:
            for idx in range(0, 64, 8):
                pixel_row = [0 if ch==' ' else 255 for ch in image_str[idx:idx+8]]
                pixels.append(pixel_row)
        elif len(image_str) == 8:
            for line in image_str:
                pixel_row = [0 if ch==' ' else 255 for ch in line]
                pixels.append(pixel_row)
        else:
            raise ValueError(f"image_str must be an 8x8 iterable")
        
        pixels = np.array(pixels, dtype=np.dtype('uint8'))
        image = Image.fromarray(pixels, mode='L').convert('1')
        self._device.display(image)
        return


    def set_contrast(self, contrast_level):
        ''' Sets the LED brightness from 0 (off) to 255 (brightest). '''
        self._device.contrast(contrast_level)
        return
    

    def clear(self):
        ''' Turns off all the LEDs. '''
        self._device.clear()


def demo():

    # Create a connection to the 8x8 LED matrix device
    device = MAX7219()

    # Show text in various formats
    device.display_text('8x8 LED Display Demo', delay=0.1)
    device.display_text('READY?', delay=0.25)
    device.clear()
    device.display_text('321!', delay=0.75, scroll=False)

    # Display an icon
    # These are the same icon just written different ways
    key_icon = '  ****   **  **  **  **   ****     **     ***      **     ***   '
    key_icon = ['  ****  ',
                ' **  ** ',
                ' **  ** ',
                '  ****  ',
                '   **   ',
                '  ***   ',
                '   **   ',
                '  ***   ']
    for contrast_level in range(200, 0, -50):
        device.contrast(contrast_level)
        device.display_image(key_icon)
        time.sleep(3)
    device.clear()


if __name__ == '__main__':
    try:
        demo()
    except KeyboardInterrupt:
        print(" Program quit with Ctrl-C")
