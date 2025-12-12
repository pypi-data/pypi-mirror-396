from typing import List
from DUELink.SerialInterface import SerialInterface
from DUELink.Stream import StreamController

class SoundController:
    def __init__(self, transport:SerialInterface, stream:StreamController):
        self.transport = transport
        self.stream = stream

    def Beep(self, pin:int, frequency:int, duration:int)->bool:

        if pin < 0 or pin > self.transport.DeviceConfig.MaxPinIO:
            raise ValueError("Invalid pin")
        #if frequency < 0 or frequency > 10000:
            #raise ValueError("Frequency is within range[0,10000] Hz")
        # if duration < 0 or duration > 1000:
        #     raise ValueError("duration is within range[0,1000] millisecond")
        
        cmd = "beep({0}, {1}, {2})".format(pin, frequency, duration)
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success
    
    def MelodyPlay(self, pin: int, notes: List[float]) -> bool:

        if pin < 0 or pin not in self.transport.DeviceConfig.PWMPins:
            raise ValueError("Invalid pin")
        if not isinstance(notes, list) and all(isinstance(i, float) for i in notes):
            raise ValueError("Notes is not the correct datatype. Enter a list of floats for melody notes.")

        for note in notes:
            if note < 0 or note > 10000:
                raise ValueError("Note Frequency is within range[0,10000] Hz")
        
        #cmd = "MelodyP({0}, {{{1}}})".format(pin, ", ".join(map(str, notes)))
        # declare a9 array
        count = len(notes)
        # declare a9 array
        cmd = f"dim a9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to a9
        ret = self.stream.WriteFloats("a9",notes)

        # write a9 to dmx
        cmd = f"MelodyP({pin},a9)"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        return ret.success

    def MelodyStop(self, pin: int)->bool:

        if pin < 0 or pin not in self.transport.DeviceConfig.PWMPins:
            raise ValueError("Invalid pin")
        
        cmd = "MelodyS({0})".format(pin)
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success
    
    def Wave(self, pin: int, buffer: bytes, offset: int, count: int, freq:int, delay_us:int ) -> bool:
        
        # declare a9 array
        count = len(buffer)
        # declare a9 array
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to a9
        ret = self.stream.WriteBytes("b9",buffer)

        # write a9 
        cmd = f"Wave({pin},b9, {offset}, {count}, {freq}, {delay_us})"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        return ret.success
    
    def Sweep(self, pin: int, freq_start: int, freq_end: int, vol_start: int, vol_end:int, delay:int ) -> bool:            

        # write a9
        cmd = f"Sweep({pin}, {freq_start}, {freq_end}, {vol_start}, {vol_end}, {delay})"
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        return ret.success
        
    
        
