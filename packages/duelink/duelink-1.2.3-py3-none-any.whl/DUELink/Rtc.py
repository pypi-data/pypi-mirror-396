from enum import Enum
from DUELink.SerialInterface import SerialInterface
from DUELink.Stream import StreamController

class RtcController:   

    def __init__(self, transport:SerialInterface, stream:StreamController):
        self.transport = transport
        self.stream = stream

    def Write(self, rtc_timedate: bytes)->bool:
        count = len(rtc_timedate)
        # declare b9 array
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to b9
        ret = self.stream.WriteBytes("b9",rtc_timedate)

        # write b9 to rtc
        self.transport.WriteCommand("RtcW(b9)")
        ret = self.transport.ReadResponse()

        return ret.success

    def Read(self, rtc_timedate: bytearray)->int:
        count = len(rtc_timedate)
        # declare b9 array
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        cmd = f"RtcR(b9)"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        ret = self.stream.ReadBytes("b9",rtc_timedate)

        return ret
        
    def Alarm(self, rtc_timedate: bytes)->bool:
        count = len(rtc_timedate)
        # declare b9 array
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to b9
        ret = self.stream.WriteBytes("b9",rtc_timedate)

        # write b9 to rtc
        self.transport.WriteCommand("RtcA(b9)")
        ret = self.transport.ReadResponse()

        return ret.success
        
        




       



