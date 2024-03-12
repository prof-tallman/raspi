# raspi
A collection of Python demo scripts that connect a Raspberry Pi to some of the components that come in the electronics starter kits. The scripts are organized into subdirectories for Basic Scripts, Modules, and Computer Vision (CV). The `basic` scripts demonstrate how to use objects that come with standard Raspberry Pi libraries like gpiozero and RPi.GPIO. The `modules` directory contains simple classes that interact with I/O components not included in `gpiozero` and `RPi.GPIO`. And the `cv` folder is a handful of scripts for interacting with a Raspberry Pi camera via the Picamera2 class including some code for object detection with OpenCV.

## Basic Directory
The basic directory contains files for working with buttons, LEDs, and DC motors. The most complex component is an HC-SR04 Ultransonic Echo Sensor, but `gpiozero` has a class called `DistanceSensor` that seems to work well.

## Modules Directory
Some electronic components did not appear to have any classes associated with them in the common mouldes like `gpiozero` and `RPi.GPIO`. Students found modules on the internet that were supposed to interface with these components, but had trouble getting them to work. The modules contained herein seemed to work better and are available for others to use.
| Module Name | Description |
| ----------- | ----------- |
| `dht11.py` | Reads the temperature and humidity from a sensor (DHT11). |
| `lcd16x2.py` | Prints text to a standard 16x2 LCD screen (LCD1602). |
| `matrix8x8.py` | Displays binary "pictures" on an 8x8 LED matrix screen (MAX7219). |

## CV Directory
The python files in this dictory deal with Raspberry Pi Cameras and Computer Vision using the OpenCV module. Some of these scripts would run just fine on any desktop computer because they interact with image files on disk. But the scripts that interact directly with a camera depend on the Raspberry Pi-specific libraries rather than the more generic, OpenCV.
| Python Program | Description |
| -------------- | ----------- |
| `cv2util.py` | Some helper functions that add on to OpenCV functionality |
| `photo.py` | Take a photo with a Raspberry Pi |
| `movie.py` | Take a 10 second video encoded with the H.264 codec |
| `yolo.py` | Object classification using You Only Look Once model that draws boxes around people in an image |
| `hog.py` | Person detection using the Histogram of Oriented Gradients (HOG) that is built into OpenCV (relatively slow and low accuracy) |
| `haar.py` | Face detection using a pretrained Haar Cascade Classifier (on small images, it might achieve 3-4 fps) |
| `tracker.py` | Face tracking on a live video feed using the HAAR model |

## Testing
This module was tested on a Raspberry Pi 4 Model B with 8 GB of RAM and sensor parts coming from the Elegoo "The Most Complete" Starter Kit.
