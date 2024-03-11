
# Prof Tallman
# HAAR facial detection optimized for speed by shrinking images to 640x480
#
# References:
#  - https://github.com/opencv/opencv/tree/master/data/haarcascades
#  - https://github.com/automaticdai/rpi-object-detection/tree/master
#  - https://docs.opencv.org/3.4/db/d28/tutorial_cascade_classifier.html

import time
import cv2
import sys
import os
import cv2util

def main():

    # Load a pre-trained model to detect faces in an image

    haar_weights_file = 'haarcascade_frontalface_default.xml'
    if os.path.exists(haar_weights_file):
        time_start = time.time()
        haar_faces = cv2.CascadeClassifier(haar_weights_file)
        time_end = time.time()
        duration = time_end - time_start
        print(f"HAAR Frontal Face (default) load time {duration:.3f}s")
    else:
        print(f"Error: '{haar_weights_file}' does not exist")
        return

    # Command line parameters must be an image file or a dir containing images

    if len(sys.argv) < 2:
        print(f"Error: missing filename")
        print(f"Usage: python {sys.argv[0]} <file>")
        exit()
    file_arg = sys.argv[1]
    if not os.path.exists(file_arg):
        print(f"Error: '{file_arg}' does not exist")
        exit()
    if os.path.isfile(file_arg):
        image_files = [file_arg]
    else:
        image_files = [f"{file_arg}/{name}" for name in os.listdir(file_arg)]

    # Pass each image file to the HAAR classifier for **SPEED**:
    #  1. Resize image to 640x480 and convert to grayscale
    #  2. Detect faces
    #  3. Draw the image with bounding boxes in a GUI window
    #  4. Wait for the current GUI window to close

    for filename in image_files:
    
        time_start = time.time()
        img = cv2.imread(filename)
        if img is None:
            print(f"Error: cv2 could not open image file '{filename}'")
            continue
        img = cv2util.shrink_to_fit(img, (640, 480))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = haar_faces.detectMultiScale(gray, 1.1, 4)
        time_end = time.time()
        duration = time_end - time_start

        neon = (0, 255, 204)
        print(f'{filename}: detected {len(faces)} faces in {duration:.3f}s')
        for (x, y, w, h) in faces:
            ctr_x = x + w // 2
            ctr_y = y + h // 2
            cv2.rectangle(img, (x, y), (x+w, y+h), neon, 2)
            cv2.line(img, (ctr_x-5, ctr_y), (ctr_x+5, ctr_y), neon, 2)
            cv2.line(img, (ctr_x, ctr_y-5), (ctr_x, ctr_y+5), neon, 2)
            print(f'  => ({ctr_x}, {ctr_y}) bbox {x},{y}->{x+w},{y+h}')

        cv2.namedWindow(filename)
        cv2.imshow(filename, img)
        cv2.moveWindow(filename, 50, 50)
        cv2util.wait_for_window_to_close(filename)


if __name__ == '__main__':
    main()
