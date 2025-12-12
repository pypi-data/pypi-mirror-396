class FrequencyController:
    def __init__(self, transport):
        self.transport = transport
        self.MaxFrequency = 24000000
        self.MinFrequency = 16

    def Write(self, pin: int, frequency, duration_ms=0, dutycyle=50)->bool:
        if frequency < self.MinFrequency or frequency > self.MaxFrequency:
            raise ValueError("Frequency must be in range 16Hz...24000000Hz")



        if dutycyle < 0 or dutycyle > 1:
            raise ValueError("dutycyle must be in range 0..100")
        
        if pin not in self.transport.DeviceConfig.PWMPins:
            raise ValueError("Invalid pin used for frequency")

        cmd = "freq({}, {}, {}, {})".format(pin, frequency, duration_ms, dutycyle)
        self.transport.WriteCommand(cmd)

        res = self.transport.ReadResponse()

        return res.success
