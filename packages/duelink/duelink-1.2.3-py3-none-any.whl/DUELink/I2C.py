from typing import Optional
from DUELink.SerialInterface import SerialInterface
from DUELink.Stream import StreamController

class I2cController:
    def __init__(self, transport:SerialInterface, stream:StreamController):
        self.transport = transport
        self.stream = stream
        self.baudrate = 400

    def Configuration(self, baudrate)->bool:

        if not isinstance(baudrate, int):
            raise ValueError("Enter an integer for the baudrate.")

        self.baudrate = baudrate

        cmd = f"i2ccfg({baudrate})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def WriteRead(self, address: int, dataWrite: bytes, dataRead: bytearray) -> bool:
        countWrite = len(dataWrite)
        countRead = len(dataRead)
        

        # declare b9 to write    
        cmd = f"dim b9[{countWrite}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # declare b8 to read
        cmd = f"dim b8[{countRead}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to b9 by stream
        self.stream.WriteBytes("b9", dataWrite)

        # issue i2cwr cmd
        cmd = f"i2cwr({address}, b9, b8)"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # use stream to read data to b8
        self.stream.ReadBytes("b8", dataRead)

        # return true since we can't check status if Asio(1)
        return True
