
import cv2


def cv2TextBoxWithBackground(img, text,
        font=cv2.FONT_HERSHEY_PLAIN,
        pos=(0, 0),
        font_scale=1,
        font_thickness=1,
        text_color=(30, 255, 205),
        text_color_bg=(48, 48, 48)):
    ''' Places a text string in the foreground of an image. '''
    x, y = pos
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_pos = (x, y + text_h + font_scale)
    box_pt1 = pos
    box_pt2 = (x + text_w+2, y + text_h+2)
    cv2.rectangle(img, box_pt1, box_pt2, text_color_bg, cv2.FILLED)
    cv2.putText(img, text, text_pos, font, font_scale, text_color, font_thickness)
    return img


if __name__ == '__main__':
    try:

        # Open the default webcam--Raspberry Pi devices should use picamera2 library
        webcam = cv2.VideoCapture(0)
        if not webcam.isOpened():
            print("Error opening webcam")
            exit()
        ret, frame = webcam.read()
        if not ret:
            print("Error reading webcam")
            exit()

        # Shrink the image for a more responsive interface
        width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f'Webcam Resolution:  {width}x{height}')
        width //= 2
        height //= 2
        print(f'Adjusted for Speed: {width}x{height}')

        # Main command loop displays the camera frame and responds to keypresses
        # Displays the last keypress for short time
        #   <ESC>:  quit
        #   WSAD:   forward, reverse, left, right
        #   [ or ]: pan camera left or right
        cv2.namedWindow("Video Feed")
        frame_count = 0
        message = None
        while True:
            ret, frame = webcam.read() 
            frame = cv2.resize(frame, (width, height))
            key_code = cv2.waitKey(1)
            if key_code == -1:
                if message is not None and frame_count < 10:
                    frame = cv2TextBoxWithBackground(frame, message)
            elif key_code & 0xFF == 27:
                exit()
            else:
                frame_count = 0
                key_code = chr(key_code & 0xFF).lower()
                if key_code == 'w':
                    message = 'FORWARD'
                elif key_code == 's':
                    message = 'REVERSE'
                elif key_code == 'a':
                    message = 'TURN LEFT'
                elif key_code == 'd':
                    message = 'TURN RIGHT'
                elif key_code == '[':
                    message = 'PAN LEFT'
                elif key_code == ']':
                    message = 'PAN RIGHT'
                frame = cv2TextBoxWithBackground(frame, message)
            cv2.imshow("Video Feed", frame)
            frame_count += 1

    except KeyboardInterrupt:
        print(f" User quit with <CTRL+C>")
        
    finally:
        print("Releasing all OpenCV resources")
        cv2.destroyAllWindows()
        webcam.release()
