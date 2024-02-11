
# Prof Tallman
# Help from O'Reilly's Raspberry Pi Cookbook text

import time
from gpiozero import Button

gpio_pin_button = 18

def button_callback():
    print(f"Button {gpio_pin_button} Pressed")

button = Button(gpio_pin_button)
button.when_pressed = button_callback

while True:
    print("Main thread")
    time.sleep(2)
