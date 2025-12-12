from typing import Optional

import time
from DUELink.SerialInterface import SerialInterface
from DUELink.Stream import StreamController

class SpiController:
    def __init__(self, transport:SerialInterface, stream:StreamController):
        self.transport = transport
        self.stream = stream

    # def Write(self, dataWrite: bytes, offset: int = 0, length: Optional[int] = None, chipselect: int = -1) -> bool:
    #     if length is None:
    #         length = len(dataWrite)

    #     return self.WriteRead(dataWrite, offset, length, None, 0, 0, chipselect)

    def Configuration(self, mode, frequency)->bool:
        
        if not isinstance(mode, int) or mode not in {0,1,2,3}:
            raise ValueError("Invalid mode. Enter an integer between 0-3.")
        
        if not isinstance(frequency, int) or (not 200 <= frequency <= 24000):
            raise ValueError("Invalid frequency. Enter an integer between 200-24000.")
    
        cmd = f"spicfg({mode}, {frequency})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success
    
    def WriteByte(self, data: int)->int:
        
        if not isinstance(data, int) or (not 0 <= data <= 255):
            raise ValueError("Enter only one byte as an integer into the data parameter.")
    
        cmd = f"spiwr({data})"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()
        if ret.success:            
            try:
                value = int(ret.response)
                return value
            except:
                pass

        return 0

    # def Read(self, dataRead: bytearray, offset: int = 0, length: Optional[int] = None, chipselect: int = -1) -> bool:
    #     if length is None:
    #         length = len(dataRead)

    #     return self.WriteRead(None, 0, 0, dataRead, offset, length, chipselect)

    def WriteRead(self, dataWrite: bytes, dataRead: bytearray) -> bool:
        countWrite = len(dataWrite)
        countRead = len(dataRead)
        written = 0
        read = 0
        

        # declare b9 to write
        if countWrite > 0:    
            cmd = f"dim b9[{countWrite}]"
            self.transport.WriteCommand(cmd)
            self.transport.ReadResponse()

        # declare b8 to read
        if countRead > 0:
            cmd = f"dim b8[{countRead}]"
            self.transport.WriteCommand(cmd)
            self.transport.ReadResponse()

        # write data to b9 by stream
        if countWrite > 0:    
            written = self.stream.WriteBytes("b9", dataWrite)

        # issue spi cmd
        if countWrite > 0 and countRead > 0:
            cmd = f"SpiWrs(b9, b8)"
        elif countWrite > 0:
            cmd = f"SpiWrs(b9, 0)"
        else:
            cmd = f"SpiWrs(0, b8)"

        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # use stream to read data to b8
        if countRead > 0:
            read = self.stream.ReadBytes("b8", dataRead)

        # return true since we can't check status if Asio(1)
        return (written == countWrite) and (read == countRead)

        # while countWrite > 0 or countRead > 0:
        #     num = countRead

        #     if countWrite < countRead:
        #         num = countWrite

        #     if countWrite == 0 :
        #         num = countRead

        #     if countRead == 0 :
        #         num = countWrite

        #     if (num > self.transport.TransferBlockSizeMax) :
        #         num = self.transport.TransferBlockSizeMax

        #     if countWrite > 0:
        #         self.transport.WriteRawData(dataWrite, offsetWrite, num)
        #         offsetWrite += num
        #         countWrite -= num

        #     if countRead > 0:
        #         self.transport.ReadRawData(dataRead, offsetRead, num)
        #         offsetRead += num
        #         countRead -= num            

    
    
    
    # def Configuration(self,mode: int,  frequencyKHz: int)-> bool:
    #     if mode > 3 or mode < 0:
    #         raise ValueError("Mode must be in range 0...3.")
        
    #     if frequencyKHz < 200  or frequencyKHz > 20000:
    #         raise ValueError("FrequencyKHz must be in range 200KHz to 20MHz.")
        
    #     cmd = f"palette({mode},{frequencyKHz})"

    #     self.transport.WriteCommand(cmd)

    #     res = self.transport.ReadResponse()
    #     return res.success
    

