class DeviceConfiguration:
    def __init__(self):
        self.MaxPinIO = 27
        self.MaxPinAnalog = 10
        self.PWMPins = {1, 2, 3, 4, 5, 6, 7, 8, 11}
        self.InterruptPins = {1, 2, 3, 4, 5, 6, 7, 12}
        self.AnalogPins = {1, 2, 3, 4, 5, 6, 7, 8, 9, 17, 23}

