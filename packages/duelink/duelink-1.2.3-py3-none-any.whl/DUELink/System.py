from enum import Enum
import time
import re

class SystemController:
    class ResetOption(Enum):
        SystemReset = 0
        Bootloader = 1


    def __init__(self, transport):
        self.transport = transport
        self.Version = ""         

    def Reset(self, option : int):
        cmd = "reset({0})".format(1 if option == 1 else 0)
        self.transport.WriteCommand(cmd)

        #Erase all send reset twice
        if (option == 1):
            self.transport.ReadResponse()
            self.transport.WriteCommand(cmd)

        # The device will reset in bootloader or system reset
        self.transport.Disconnect()

    def GetTickMicroseconds(self):
        cmd = "tickus()"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        if res.success:
            try:
                return int(res.response)
            except:
                pass
        return -1
    
    def GetTickMilliseconds(self):
        cmd = "tickms()"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        if res.success:
            try:
                return int(res.response)
            except:
                pass
        return -1
    
    # def GetVersion(self):
        # command = "version()"
        # self.transport.WriteCommand(command)

        # version = self.transport.ReadResponse()

        

        # match = re.match(r"^([\w\s]+).*?(v[\d\.].*)", version.response)


        # if version.success:
            # self.transport.TurnEchoOff()
            # self.transport.portName.reset_input_buffer()
            # self.transport.portName.reset_output_buffer()
            # version.response = version.response[len(command):]

        # version_firmware = match.group(2).split(":")[0]
        # prod_id = match.group(2).split(":")[1]
        # version_boot_loader = match.group(2).split(":")[2]


        # return version_firmware, prod_id, version_boot_loader
    
    def Info(self, code):
        cmd = f"info({code})"
        self.transport.WriteCommand(cmd)

        response = self.transport.ReadResponse()

        if response.success:            
            try:
                value = int(response.response)
                return value
            except:
                pass

        return 0
        
    def StatLed(self, highPeriod: int, lowPeriod: int, count: int) -> bool:
        cmd = f"statled({highPeriod},{lowPeriod},{count})"
        self.transport.WriteCommand(cmd)

        res = self.transport.ReadResponse()
        return res.success
    
    def LowPower(self, mode: int, pin:int)-> bool:
        cmd = f"lowpwr({mode},{pin})"
        self.transport.WriteCommand(cmd)

        # shutdown no response
        return True

    






