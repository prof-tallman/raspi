# sudo apt install -y python3-matplotlib
# sudo apt install -y python3-numpy
# sudo apt install -y python3-pandas
# sudo apt install -y python3-opencv
# sudo apt install -y opencv-data
# sudo apt update
# sudo apt upgrade

from picamera2 import Picamera2, Preview
from PIL import Image
import time, libcamera

picam = Picamera2()
image_filename = 'portrait.jpg'

# Take a 1600x1200 photo
# Flip the camera vertically due to how it's currently arranged
#config = picam.create_preview_configuration(main={"size":(1600,1200)})
#config["transform"] = libcamera.Transform(vflip=1)
#picam.configure(config)

# Make the preview window only 800x600
# Preview.DRM instead of Preview.QTGL for headless installs
picam.start_preview(Preview.QTGL, x=100, y=100, width=800, height=600)
picam.start()

# Countdown
print("Taking photo in 3... ", end='', flush=True); time.sleep(1)
print("2... ", end='', flush=True); time.sleep(1)
print("1... ", end='', flush=True); time.sleep(1)
print("say 'CHEESE!'")

# Take the picture
picam.capture_file(image_filename)

# Close up the camera
picam.close()

# Show the image
image = Image.open(image_filename)
image.show()



