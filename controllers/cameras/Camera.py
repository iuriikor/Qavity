class Camera:
    def __init__(self, cam_id):
        self._id = cam_id
        self._camera = None # Camera object for the external program to use - if needed
        self.exposure_ms = None # Exposure time in ms
        self.framerate = None # Desired framerate - can't be higher than 1000/exposure_ms
        self.gain = None # Gain
        self.rotate_img = False # May be easier to rotate image in camera class
        # Region of interest
        self.roi_x_tl = None # Top left X
        self.roi_y_tl = None # Top left Y
        self.roi_x_br = None  # Bottom right X
        self.roi_y_br = None  # Bottom right Y
        # Sensor size in pixels
        self.sensor_width = None
        self.sensor_height = None

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
