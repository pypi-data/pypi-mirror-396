from DUELink.SerialInterface import SerialInterface

class DistanceSensorController:
    def __init__(self, transport:SerialInterface):
        self.transport = transport

    def Read(self, trigPin, echoPin)->float:
        cmd = f'dist({trigPin},{echoPin})'
        self.transport.WriteCommand(cmd)

        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return float(ret.response)
            except ValueError:
                pass

        return -1
