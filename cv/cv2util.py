import cv2

# Adopted from https://medium.com/@mh_yip/opencv-detect-whether-a-window-is-closed-or-close-by-press-x-button-ee51616f7088
# Thanks to David C. for Aspect Ratio workaround to Rasberry Pi cv2 bug:
# https://stackoverflow.com/questions/66431311/python-opencv-on-raspberry-pi-detect-window-closing
def wait_for_window_to_close(window_title):
    """
    Blocks execution until the specified window has been closed. If the user
    presses the <ESC> key, the function will return immediately.
    """

    visible = cv2.getWindowProperty(window_title, cv2.WND_PROP_VISIBLE)
    aratio = cv2.getWindowProperty(window_title, cv2.WND_PROP_ASPECT_RATIO)
    while visible != 0.0 and aratio >= 0:
        visible = cv2.getWindowProperty(window_title, cv2.WND_PROP_VISIBLE)
        aratio = cv2.getWindowProperty(window_title, cv2.WND_PROP_ASPECT_RATIO)
        keyCode = cv2.waitKey(100)
        if (keyCode & 0xFF) == 27:
            print(f"Detected <ESC> Key... Quitting Program")
            cv2.destroyWindow(window_title)
            return

def shrink_to_fit(img, bbox=(640,480)):
    """
    Shrinks an image to fit in a bounding box while preserving aspect ratio.
    """

    bbox_width, bbox_height = bbox
    height, width, channels = img.shape
    factor = min(bbox_width / width, bbox_height / height)
    if factor < 1:
        return cv2.resize(img, (0,0), fx=factor, fy=factor)
    else:
        return img