
# Prof Tallman
# Help from O'Reilly's Raspberry Pi Cookbook text

from gpiozero import Button, LED
from time import sleep

gpio_pin_button = 18
gpio_pin_led = 23

def button_handler():
    led.toggle()

led = LED(gpio_pin_led)
button = Button(gpio_pin_button)
button.when_pressed = button_handler

while True:
    print("Busy Loop")
    sleep(2)
    