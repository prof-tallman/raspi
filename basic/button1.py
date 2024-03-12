
# Prof Tallman
# Help from O'Reilly's Raspberry Pi Cookbook text

import time
from gpiozero import Button

gpio_pin_button = 18

button = Button(gpio_pin_button)

while True:
    if button.is_pressed:
        print(f"Button {gpio_pin_button} Pressed")
    time.sleep(0.5)
