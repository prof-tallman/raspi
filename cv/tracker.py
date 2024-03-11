
from picamera2 import Picamera2
import time
import cv2
import sys
import os
import cv2util

def main():

    # Turn off informational log messages (errors still shown)
    os.environ["LIBCAMERA_LOG_LEVELS"] = "3"
    Picamera2.set_logging(Picamera2.ERROR)

    # Load the HAAR Cascade weights file for faces
    haar_weights_file = 'haarcascade_frontalface_default.xml'
    if not os.path.exists(haar_weights_file):
        print(f"Error: '{haar_weights_file}' does not exist")
        return
    haar_faces = cv2.CascadeClassifier(haar_weights_file)

    # Start the camera and display window
    picam = Picamera2()
    picam.start()
    cv2.namedWindow('TRACKER')
    window = (640, 480)
    middle = (window[0] // 2, window[1] // 2)

    # Loop until the user presses <ESC>
    while cv2.waitKey(1) & 0xFF != 27:
        
        # Capture a frame and convert it to 640x480 grayscale
        frame = picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB) 
        frame = cv2util.shrink_to_fit(frame, window)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        boxes = haar_faces.detectMultiScale(gray, 1.1, 4)
        neon = (0, 255, 204)
        for (x, y, w, h) in boxes:
            ctr_x = x + w // 2
            ctr_y = y + h // 2
            cv2.rectangle(frame, (x, y), (x+w, y+h), neon, 1)
            cv2.line(frame, (ctr_x-5, ctr_y), (ctr_x+5, ctr_y), neon, 2)
            cv2.line(frame, (ctr_x, ctr_y-5), (ctr_x, ctr_y+5), neon, 2)
            #cv2.line(frame, (ctr_x, ctr_y), middle, neon, 1)
        cv2.imshow('TRACKER', frame)

    picam.stop()
    picam.close()


if __name__ == '__main__':
    main()