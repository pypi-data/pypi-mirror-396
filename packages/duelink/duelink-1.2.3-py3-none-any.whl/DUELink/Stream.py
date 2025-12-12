from enum import Enum
import time
from DUELink.SerialInterface import SerialInterface
import struct

class StreamController:   

    def __init__(self, transport:SerialInterface):
        self.transport = transport

    def WriteSpi(self, dataWrite: bytes):
        count = len(dataWrite)

        cmd = f"strmspi({count})"
        self.transport.WriteCommand(cmd)

        # wait for prompt &
        while self.transport.BytesToRead() == 0:
            time.sleep(0.001)
        
        prompt = self.transport.ReadByte()

        if prompt != '&':
            raise Exception("Invalid or no responses")
        
        # ready to write data
        self.transport.WriteRawData(dataWrite,0, count)

        # read x\r\n> (asio(1) not return this)
        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return int(ret.response)
            except:
                return 0                
        
        return 0

    def WriteBytes(self, arr: str, dataWrite: bytes):
        if dataWrite is None or dataWrite == 0:
            return 0

        count = len(dataWrite)

        # declare b1 array
        cmd = f"strmwr({arr},{count})"
        self.transport.WriteCommand(cmd)

        # wait for prompt &
        while self.transport.BytesToRead() == 0:
            time.sleep(0.001)
        
        prompt = self.transport.ReadByte()

        if prompt != '&':
            raise Exception("Invalid or no responses")
        
        # ready to write data
        self.transport.WriteRawData(dataWrite,0, count)

        # read x\r\n> (asio(1) not return this)
        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return int(ret.response)
            except:
                return 0                
        
        return 0
    
    def WriteFloats(self, arr: str, dataWrite: float):
        if dataWrite is None or dataWrite == 0:
            return 0
        count = len(dataWrite)

        # declare b1 array
        cmd = f"strmwr({arr},{count})"
        self.transport.WriteCommand(cmd)

        # wait for prompt &
        while self.transport.BytesToRead() == 0:
            time.sleep(0.001)
        
        prompt = self.transport.ReadByte()

        if prompt != '&':
            raise Exception("Invalid or no responses")
        
        # ready to write data
        for i in range (0, count):
            float_bytes = struct.pack('>f', dataWrite[i])
            float_bytes_lsb = float_bytes[::-1]
            self.transport.WriteRawData(float_bytes_lsb,0, 4)        

        # read x\r\n> (asio(1) not return this)
        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return int(ret.response)
            except:
                return 0                
        
        return 0
    
    def ReadBytes(self, arr: str, dataRead: bytes):
        if dataRead is None or dataRead == 0:
            return 0
        count = len(dataRead)

        # declare b1 array
        cmd = f"strmrd({arr},{count})"
        self.transport.WriteCommand(cmd)

        # wait for prompt &
        while self.transport.BytesToRead() == 0:
            time.sleep(0.001)
        
        prompt = self.transport.ReadByte()

        if prompt != '&':
            raise Exception("Invalid or no responses")
        
        # ready to read data
        self.transport.ReadRawData(dataRead,0, count)

        # read x\r\n> (asio(1) not return this)
        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return int(ret.response)
            except:
                return 0                
        
        return 0
    
    def ReadFloats(self, arr: str, dataRead: float):
        if dataRead is None or dataRead == 0:
            return 0
        count = len(dataRead)

        # declare b1 array
        cmd = f"strmrd({arr},{count})"
        self.transport.WriteCommand(cmd)

        # wait for prompt &
        while self.transport.BytesToRead() == 0:
            time.sleep(0.001)
        
        prompt = self.transport.ReadByte()

        if prompt != '&':
            raise Exception("Invalid or no responses")
        
        # ready to read data
        raw_bytes = bytearray(4)
        for i in range (0, count):
            self.transport.ReadRawData(raw_bytes,0, 4)
            raw_bytes_lsb = raw_bytes[::-1]
            dataRead[i] = struct.unpack('f', raw_bytes)[0]        

        # read x\r\n> (asio(1) not return this)
        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return int(ret.response)
            except:
                return 0                
        
        return 0



        





        
    
       
