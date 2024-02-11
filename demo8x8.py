
# Prof Tallman
# Helper library and demo code for working with 8x8 LED Matrix
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
# Looked at luma.core.legacy.show_message source to understand font format
# Idea to use a string to create a simple bitmap thanks to dji_matrix module
# for DJI Tello Talent Drones (but modified to use nicer string interface)
#   https://github.com/damiafuentes/DJITelloPy
# Getting unstuck when trying to convert 1-bit image to PIL image thanks to
# 'hennes' on Stackoverflow:
#   http://stackoverflow.com/questions/32159076/python-pil-bitmap-png-from-array-with-mode-1


import time
import numpy as np
from PIL import Image
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
import luma.core.legacy as legacy
from luma.core.legacy.font import proportional, LCD_FONT


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
    
    # Shift the character over half of the R/L difference to center it
    return (right_count - left_count) // 2


def matrix_8x8text(device, message, scroll=True, delay=0.5):
    '''
    Displays a message on the 8x8 matrix in either scrolling mode or else by
    showing 1 character at a time.

    Args:
     - device: A LUMA max7219 object
     - message: Text string to be displayed
     - scroll: True to scroll the message or False to show 1 letter at a time
     - delay: The speed at which to show the letters
    '''

    if scroll:
        legacy.show_message(device, message, fill='white', 
                            font=proportional(LCD_FONT), scroll_delay=delay)
    else:
        for ch in message:
            # Each frame of the animation must be inside of a 'with' block and
            # the 'sleep' function must be outside of the block.
            with canvas(device) as draw:
                shift = _matrix_8x8_xshift(ch, font=LCD_FONT) # center letter
                legacy.text(draw, (shift, 0), ch, fill="white", font=LCD_FONT)
            time.sleep(delay)
    return
    

def matrix_8x8image(image_str):
    ''' 
    Creates an 8x8 1-bit PIL image from a string. All spaces ' ' are 
    treated as 0s and all other characters are treated as 1s.
    
    For example, an image of an old fashioned skeleton key:
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
    return image


def demo():
    ''' A demo of the matrix8x8 helper module. '''

    # Create a connection to the 8x8 LED matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, width=8, height=8, rotate=2, block_orientation=0)

    # Show text in various formats
    matrix_8x8text(device, '8x8 LED Display Demo', delay=0.1)
    matrix_8x8text(device, 'READY?', delay=0.25)
    device.clear()
    matrix_8x8text(device, '321!', scroll=False, delay=0.75)

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

    # Display an icon
    icon = matrix_8x8image(key_icon)
    for contrast_level in range(200, 0, -10):
        device.contrast(contrast_level)
        device.display(icon)
        time.sleep(0.1)


if __name__ == '__main__':
    try:
        demo()
    except KeyboardInterrupt:
        print(" Program quit with Ctrl-C")
