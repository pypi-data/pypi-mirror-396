from enum import Enum
from DUELink.SerialInterface import SerialInterface


class PulseController:   

    def __init__(self, transport:SerialInterface):
        self.transport = transport


    def Read(self, pin: int, charge_t: int, charge_s: int, timeout: int):
        cmd = "PulseIn({0}, {1}, {2}, {3})".format(pin, charge_t, charge_s, timeout)
        self.transport.WriteCommand(cmd)        

        ret = self.transport.ReadResponse()

        if ret.success:            
            try:
                value = int(ret.response)
                return value
            except:
                pass

        return 0

        
        




       



