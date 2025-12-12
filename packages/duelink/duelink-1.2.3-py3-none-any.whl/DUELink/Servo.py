from DUELink.SerialInterface import SerialInterface

class ServoController:
    def __init__(self, transport:SerialInterface):
        self.transport = transport

    def Set(self, pin, position)->bool:
        if pin < 0 or pin >= self.transport.DeviceConfig.MaxPinIO or pin not in self.transport.DeviceConfig.PWMPins:
            raise ValueError('Invalid pin. Enter a valid PWM pin.')
        if position < 0 or position > 180:
            raise ValueError('Position must be in the range 0..180')

        cmd = 'servost({}, {})'.format(pin, position)
        self.transport.WriteCommand(cmd)

        response = self.transport.ReadResponse()

        return response.success
