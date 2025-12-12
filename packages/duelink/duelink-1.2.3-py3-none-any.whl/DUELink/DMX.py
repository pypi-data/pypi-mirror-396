from enum import Enum
from DUELink.SerialInterface import SerialInterface
from DUELink.Stream import StreamController

class DMXController:   

    def __init__(self, transport:SerialInterface, stream:StreamController):
        self.transport = transport
        self.stream = stream

    def Write(self, channel_data: bytes)->bool:
        count = len(channel_data)
        # declare b9 array
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to b9
        ret = self.stream.WriteBytes("b9",channel_data)

        # write b9 to dmx
        self.transport.WriteCommand("DmxW(b9)")
        ret = self.transport.ReadResponse()

        return ret.success


    def Read(self, channel: int)->int:
        cmd = f"DmxR({channel})"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        if ret.success:            
            try:
                value = int(ret.response)
                return value
            except:
                return -1

        return -1
    
    def Ready(self)->int:
        cmd = f"DmxRdy()"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        if ret.success:            
            try:
                value = int(ret.response)
                return value
            except:
                return 0

        return 0
    
    def Update(self)->bool:
        cmd = f"DmxU()"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        return ret.success
        




       



