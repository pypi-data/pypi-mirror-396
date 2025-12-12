from DUELink.Analog import AnalogController
from DUELink.Button import ButtonController
from DUELink.Digital import DigitalController
from DUELink.Graphics import GraphicsController
from DUELink.GraphicsType import GraphicsTypeController
from DUELink.DistanceSensor import DistanceSensorController
from DUELink.Frequency import FrequencyController
from DUELink.I2C import I2cController
from DUELink.Infrared import InfraredController
from DUELink.System import SystemController
from DUELink.SerialInterface import SerialInterface
from DUELink.Servo import ServoController
from DUELink.Spi import SpiController
from DUELink.Engine import EngineController
from DUELink.DeviceConfiguration import DeviceConfiguration
from DUELink.Temperature import TemperatureController
from DUELink.Humidity import HudimityController
from DUELink.Sound import SoundController
from DUELink.Temperature import TemperatureSensorType
from DUELink.Humidity import HumiditySensorType
from DUELink.Stream import StreamController
from DUELink.DMX import DMXController
from DUELink.FileSystem import FileSystemController
from DUELink.Otp import OtpController
from DUELink.Pulse import PulseController
from DUELink.Rtc import RtcController
from DUELink.Uart import UartController

from enum import Enum
import platform
class DUELinkController:

    def __init__(self, comPort: str):
        if comPort is None:
            raise ValueError(f"Invalid comport: {comPort}")
        try:
            self.__Connect(comPort)
        except:
            raise Exception(f"Could not connect to the comport: {comPort}")
        
        if self.transport is None:
            raise Exception(f"transport is null")
        
        self.Stream = StreamController(self.transport)
        self.Analog = AnalogController(self.transport)
        self.Digital = DigitalController(self.transport)        
        self.Servo = ServoController(self.transport)
        self.Frequency = FrequencyController(self.transport)        
        self.Infrared = InfraredController(self.transport)
        self.Button = ButtonController(self.transport)
        self.Distance = DistanceSensorController(self.transport)                        
        self.Engine = EngineController(self.transport)
        self.Temperature = TemperatureController(self.transport)
        self.Humidity = HudimityController(self.transport)
        self.System = SystemController(self.transport)        
        self.GraphicsType = GraphicsTypeController()                
        self.TemperatureSensorType = TemperatureSensorType()
        self.HumiditySensorType = HumiditySensorType()       
        self.Pulse = PulseController(self.transport)        
        
        self.DMX = DMXController(self.transport,self.Stream)
        self.FileSystem = FileSystemController(self.transport,self.Stream)
        self.Otp = OtpController(self.transport,self.Stream)        
        self.Rtc = RtcController(self.transport,self.Stream)
        self.I2c = I2cController(self.transport,self.Stream)
        self.Spi = SpiController(self.transport,self.Stream)
        self.Uart = UartController(self.transport,self.Stream)
        self.Sound = SoundController(self.transport,self.Stream)
        self.Graphics = GraphicsController(self.transport,self.Stream)
        
        
    
    def __Connect(self, comPort: str):
        self.transport = SerialInterface(comPort)
        self.transport.Connect()

        # self.Version = self.transport.GetVersion()[1].strip()

        # if self.Version == "" or self.Version == "GHI Electronics DUELink v00.00:0000:00.09":
        #     raise Exception("The device is not supported.")
        
        self.DeviceConfig = DeviceConfiguration()

        # if self.Version[len(self.Version) -1] == 'P':
        #     self.DeviceConfig.IsPulse = True
        #     self.DeviceConfig.MaxPinIO = 23
        #     self.DeviceConfig.MaxPinAnalog = 29
        # elif self.Version[len(self.Version) -1] == 'I':
        #     self.DeviceConfig.IsPico = True
        #     self.DeviceConfig.MaxPinIO = 29
        #     self.DeviceConfig.MaxPinAnalog = 29  
        # elif self.Version[len(self.Version) -1] == 'F':
        #     self.DeviceConfig.IsFlea = True
        #     self.DeviceConfig.MaxPinIO = 11
        #     self.DeviceConfig.MaxPinAnalog = 29    
        # elif self.Version[len(self.Version) -1] == 'E':
        #     self.DeviceConfig.IsEdge = True
        #     self.DeviceConfig.MaxPinIO = 22
        #     self.DeviceConfig.MaxPinAnalog = 11  
        # elif self.Version[len(self.Version) -1] == 'R':
        #     self.DeviceConfig.IsRave = True
        #     self.DeviceConfig.MaxPinIO = 23
        #     self.DeviceConfig.MaxPinAnalog = 29
        # elif self.Version[len(self.Version) -1] == 'T':
        #     self.DeviceConfig.IsTick = True
        #     self.DeviceConfig.MaxPinIO = 23
        #     self.DeviceConfig.MaxPinAnalog = 11
        # elif self.Version[len(self.Version) -1] == 'D':
        #     self.DeviceConfig.IsDue = True
        #     self.DeviceConfig.MaxPinIO = 15
        #     self.DeviceConfig.MaxPinAnalog = 10

        self.transport.DeviceConfig = self.DeviceConfig        

    def Disconnect(self):
        self.transport.Disconnect()
    
    def Shutdown(self, pin: int):
        cmd = f'shtdn({pin})'
        self.transport.WriteCommand(cmd)
        response = self.transport.ReadResponse()
        return response.success    

    def GetConnectionPort():
        try:
            from serial.tools.list_ports import comports
        except ImportError:
            return ""
        
        if comports:
            com_ports_list = list(comports())
            ebb_ports_list = []
            for port in com_ports_list:               
                if port.vid ==0x1B9F and port.pid==0xF300:
                    if (platform.system() == 'Windows'):
                        return port.name                    
                    else:
                        return port.device

        return ""
    
    def __get_ReadTimeout(self):
        return self.transport.ReadTimeout

    def __set_ReadTimeout(self, value: int):
        self.transport.ReadTimeout = value 

    ReadTimeout = property(__get_ReadTimeout, __set_ReadTimeout)

    def __get_EnabledAsio(self):
        return self.transport.EnabledAsio

    def __set_EnabledAsio(self, value: int):
        self.transport.EnabledAsio = value 

    EnabledAsio = property(__get_EnabledAsio, __set_EnabledAsio)
   
         

        
        


