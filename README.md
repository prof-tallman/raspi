# raspi
A collection of Python demo scripts that connect a Raspberry Pi to some of the components that come in the electronics starter kits.
- Buttons and simple LEDs
- 16x2 LCD1602 Liquid Crystal Display
- 8x8 MAX7219 LED Display
- DHT11 Temperature Humidity Sensor
- HC-SR04 Ultrasonic Echo Sensor
- DC Motor
- Photos and Movies
- Computer Vision (simple)
The scripts are organized into subdirectories for basic scripts, modules, and computer vision. The `basic` scripts demonstrate how to use objects that come with standard Raspberry Pi libraries like gpiozero and RPi.GPIO. The `modules` directory contains simple classes that interact with I/O components not included in `gpiozero` and `RPi.GPIO`. And the `cv` folder is a handful of scripts for interacting with a Raspberry Pi camera via the Picamera2 class including some code for object detection with OpenCV.

## Basic Directory
The basic directory contains files for working with buttons, LEDs, and DC motors. The most complex component is an HC-SR04 ultransonic sensor, but `gpiozero` has a class called `DistanceSensor` that seems to work well.

## Modules Directory
Some electronic components did not appear to have any classes associated with them in the common mouldes like `gpiozero` and `RPi.GPIO`. Students found modules on the internet that were supposed to interface with these components, but had trouble getting them to work. The modules contained herein seemed to work better and are available for others to use.
| Module Name | Description |
| ----------- | ----------- |
| `dht11.py` | Reads the temperature and humidity from a DHT11 sensor. |
| `lcd16x2.py` | Prints text to a standard 16x2 LCD screen. |
| `matrix8x8.py` | Displays binary "pictures" on an 8x8 LED matrix screen. |

## CV Directory


## Testing
This module was tested on a Raspberry Pi 4 Model B with 8 GB of RAM and sensor parts coming from the Elegoo "The Most Complete" Starter Kit.
