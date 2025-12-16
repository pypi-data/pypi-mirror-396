import cv2 as cv
import os
from glob import glob
import time
import string


class CaptureRead:
    def __init__(self, path, mode="rgb"):
        self.path = path
        self.mode = mode
        self._media = ""
        self.image_path = []
        self.convert_color = lambda image: image if self.mode == "bgr" else cv.cvtColor(image, cv.COLOR_BAYER_BGR2RGB)
        if os.path.isdir(self.path):
            self._media = "folder"
            self.image_path = glob(os.path.join(self.path, "*.*"))
        elif (isinstance(self.path, int) and self.path>=0):
            self._media = "webcam"
            self.cap = cv.VideoCapture(self.path)
        elif (isinstance(self.path, str) and self.path.startswith("rtsp")):
            self._media = "rtsp"
            self.cap = cv.VideoCapture(self.path)
        elif (isinstance(self.path, str) and os.path.isfile(self.path)):
            self._media = "videofile"
            self.cap = cv.VideoCapture(self.path)
        else:
            raise NotImplementedError()

    def _read_image(self, path):
        image = self.convert_color(cv.imread(path, cv.IMREAD_COLOR))
        return image 
        
    def next(self):
        if self._media == "folder":
            if len(self.image_path) > 0:
                while True:
                    for path in self.image_path:
                        image = self._read_image(path)
                        yield image
            else:
                raise "Folder has zero images"
        
        elif self._media == "webcam" or self._media == "rtsp" or self._media == "videofile":
            if hasattr(self, "cap"):
                if self.cap.isOpened():
                    while True:
                        self.cap = cv.VideoCapture(self.path)
                        ret = True
                        while ret:
                            ret, image = self.cap.read()
                            image = self.convert_color(image)
                            yield image
            else:
                raise "Check your input. No device is initialized."
        else:
            raise NotImplementedError()