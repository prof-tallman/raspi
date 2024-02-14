
# Prof Tallman
# Help from O'Reilly's Raspberry Pi Cookbook text
#
# Warning: I edited the code a little bit after disconnecting the circuit
# It *should* work but there are a few untested lines of code

from gpiozero import Motor
from gpiozero import DigitalOutputDevice

_MOTOR_PIN1 = 12
_MOTOR_PIN2 = 13
_MOTOR_ENABLE = 26


try:
    fan = Motor(forward=_MOTOR_PIN1, backward=_MOTOR_PIN2)
    power = DigitalOutputDevice(_MOTOR_ENABLE)

    while True:
        command_str = input("Command, f/r/s 0..9, E.g., f5 or s: ")
        direction = command_str[0].lower()
        if len(command_str) > 1:
            velocity = float(command_str[1]) / 10.0
        
        if direction == 'f':
            if not power.is_active:
                power.on()
            fan.forward(speed=velocity)
        
        elif direction == 'r':
            if not power.is_active:
                power.on()
            fan.backward(speed=velocity)
        
        elif direction == 's':
            fan.stop()
            power.off()

        else:
            break

except KeyboardInterrupt:
    print(f" User quit with <CTRL+C>")

except Exception as e:
    print(f"ERROR: {e}")

finally:
    fan.stop()
    power.off()
    print(f"Program completed successfully")
