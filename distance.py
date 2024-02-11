
# Prof Tallman
# Demonstrates how to measure distance with the HC-SR04 ultrasonic echo sensor
# Help from O'Reilly's Raspberry Pi Cookbook text
# Remember to start the pigpio daemon:
#   > sudo pigpiod

from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device, Button, DistanceSensor

gpio_pin_button = 21
gpio_pin_echo = 18
gpio_pin_trigger = 17

# According to a runtime warning, PiGPIO mode is better for HC-SR04 sensors
Device.pin_factory = PiGPIOFactory()
button = Button(gpio_pin_button, bounce_time=0.1)
sensor = DistanceSensor(echo=gpio_pin_echo, trigger=gpio_pin_trigger)

def print_distance():
    cm = sensor.distance * 100
    inch = cm / 2.5
    if cm < 100:
        print(f'{cm:.02f}cm\t{inch:.02f}"')
    else:
        print('100.00cm\t40"')

button.when_pressed = print_distance

input("Press <ENTER> to quit\n")