from enum import Enum
from DUELink.SerialInterface import SerialInterface
from DUELink.Stream import StreamController

class OtpController:   

    def __init__(self, transport:SerialInterface, stream:StreamController):
        self.transport = transport
        self.stream = stream

    def Write(self, address: int, data: bytes)->bool:
        count = len(data)
        # declare b9 array
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to b9
        ret = self.stream.WriteBytes("b9",data)

        # write b9 to dmx
        cmd = f"OtpW({address},b9)"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        return ret.success

    def Read(self, address: int)->int:
        cmd = f"OtpR({address})"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        if ret.success:            
            try:
                value = int(ret.response)
                return value
            except:
                pass

        return -1
        
        




       



