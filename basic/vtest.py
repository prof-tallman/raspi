
# Prof Tallman
# Needed to verify the output voltage of Raspberry Pi GPIO pins (3.3V)

from gpiozero import Button, LED
from time import sleep

gpio_pin_output = 21
led = LED(gpio_pin_output)

print(f"\nMeasure the voltage of Raspberry Pi GPIO Pin {gpio_pin_output}\n")
print(f"Pin {gpio_pin_output} will alternate between HIGH and LOW twice.")
print(f"It will hold each voltage for approximately 5 seconds.")
print(f"Once the test begins, you have 5 seconds to get the probes ready.\n")

input(f"Press <ENTER> to begin")
for timer in range(5, 0, -1):
    print(f"{timer}...", end="", flush=True)
    sleep(1)
print("Go!\n")

print(f"Pin #{gpio_pin_output}: HIGH")
led.on()
sleep(5)
print(f"Pin #{gpio_pin_output}: LOW")
led.off()
sleep(5)
print(f"Pin #{gpio_pin_output}: HIGH")
led.on()
sleep(5)
led.off()
print(f"Pin #{gpio_pin_output}: LOW")

print(f"Test complete\n")