from DUELink.SerialInterface import SerialInterface

class AnalogController:
    def __init__(self, transport:SerialInterface):
        self.transport = transport
        self.Fixed_Frequency = 50

    def VoltRead(self, pin):

        if pin not in self.transport.DeviceConfig.AnalogPins:
            raise ValueError("Invalid pin. Enter a valid analog pin.")

        cmd = "vread({0})".format(pin)

        self.transport.WriteCommand(cmd)

        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return float(ret.response)
            except:
                pass

        return -1
    
    def Read(self, pin):

        if pin not in self.transport.DeviceConfig.AnalogPins:
            raise ValueError("Invalid pin. Enter a valid analog pin.")

        cmd = "aread({0})".format(pin)

        self.transport.WriteCommand(cmd)

        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return float(ret.response)
            except:
                pass

        return -1
    
    def Write(self, pin, duty_cycle):
        
        if pin not in self.transport.DeviceConfig.PWMPins: # Led
            raise ValueError('Invalid pin. Enter a valid pwm pin.')

        if duty_cycle < 0 or duty_cycle > 1:
            raise ValueError('Duty cycle must be in the range 0..1')

        cmd = f'awrite({pin}, {duty_cycle})'
        self.transport.WriteCommand(cmd)

        ret = self.transport.ReadResponse()

        return ret.success
    
    def ReadVcc(self):
        cmd = f"readvcc()"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return float(ret.response)
            except:
                pass

        return -1
