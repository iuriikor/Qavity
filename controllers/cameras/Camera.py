class Camera:
    def __init__(self, cam_id):
        self._id = cam_id
        self._camera = None # Camera object for the external program to use - if needed
        self.exposure_ms = None # Exposure time in ms
        self.framerate = None # Desired framerate - can't be higher than 1000/exposure_ms
        self.gain = None # Gain

        # Helper variables
        self.streamOn = False

    def open(self):
        pass

    def getImage(self):
        pass

    def close(self):
        pass

    @property
    def id(self):
        return self._id