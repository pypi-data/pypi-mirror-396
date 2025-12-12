from DUELink.SerialInterface import SerialInterface
from DUELink.Stream import StreamController

class UartController:
    def __init__(self, transport:SerialInterface, stream:StreamController):
        self.transport = transport
        self.stream = stream

    def Configuration(self, baudrate: int, rx_buf_size: int)->bool:
        cmd = "SerCfg({0}, {1})".format(baudrate, rx_buf_size)
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()
        return ret.success

    def WriteByte(self, data: int)->bool:
        cmd = "SerWr({})".format(data)
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()
        return ret.success        
    
    def WriteBytes(self, data: bytes)->int:
        count = len(data)
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        written = self.stream.WriteBytes("b9", data)

        self.transport.WriteCommand("SerWrs(b9)")
        ret = self.transport.ReadResponse()

        if (ret.success):
            return written

        return 0
    
    def ReadByte(self):        
        self.transport.WriteCommand("SerRd()")
        res = self.transport.ReadResponse()
        if res.success:
            try:
                data = int(res.response)
                return data
            except:
                pass
        return 0
    
    def ReadBytes(self, data: bytearray, timeout_ms: int)->int:
        count = len(data)
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        cmd = f"SerRds(b9, {timeout_ms})"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        read = self.stream.ReadBytes("b9",data )

        if (ret.success):
            return read

        return 0

    def BytesToRead(self)->int:        
        self.transport.WriteCommand("SerB2R()")
        ret = self.transport.ReadResponse()
        if ret.success:
            try:
                ready = int(ret.response)
                return ready
            except:
                pass
        return 0
    
    def Discard(self)->bool:        
        self.transport.WriteCommand("SerDisc()")
        ret = self.transport.ReadResponse()
        
        return ret.success
    

    
