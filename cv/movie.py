
from picamera2.encoders import H264Encoder, Quality
from picamera2 import Picamera2, Preview
import time, libcamera

# Create camera object set for recording 800x600 with a smaller preview window
picam = Picamera2()
video_config = picam.create_video_configuration(
    main={"size": (800, 600)}, 
    lores={"size": (400, 300)}, 
    display="lores")
#video_config["transform"] = libcamera.Transform(vflip=1)

# The H264Encoder works but the quality is so-so
# Raspberry Pi will probably drop frames (boo!)
picam.configure(video_config)
encoder = H264Encoder()
output = "test.h264"
picam.start_preview(Preview.QTGL)
print("GO NOW!")
picam.start_recording(encoder, output, quality=Quality.HIGH)
time.sleep(10)
picam.stop_recording()
picam.stop_preview()
picam.close()
