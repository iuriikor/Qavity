import cv2

class Webcam(object):
    def __init__(self, framerate=10, exposure_ms=10, gain=1):
        self.video = cv2.VideoCapture(0)
        self.framerate = framerate
        if(1000/exposure_ms < framerate):
            print('Framerate is too high')
            self.exposure_ms = 1000/self.framerate
        else:
            self.exposure_ms = exposure_ms
        self.streamOn = False

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def stop_stream(self):
        self.streamOn = False

    def start_stream(self):
        self.streamOn = True
