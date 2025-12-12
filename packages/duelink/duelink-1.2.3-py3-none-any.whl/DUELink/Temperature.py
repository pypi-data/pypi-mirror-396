class TemperatureSensorType():  
    def __init__(self):
        pass

    def __get_Cpu(self):
        return 0
    def __get_Dht11(self):
        return 1
    def __get_Dht12(self):
        return 1
    def __get_Dht21(self):
        return 3
    def __get_Dht22(self):
        return 4

    def __set_empty(self, value: int):
        return   

    CPU = property(__get_Cpu, __set_empty)
    DHT11 = property(__get_Dht11, __set_empty)  
    DHT12 = property(__get_Dht12, __set_empty)  
    DHT21 = property(__get_Dht21, __set_empty)  
    DHT22 = property(__get_Dht22, __set_empty)    

class TemperatureController:
    def __init__(self, transport):
        self.transport = transport

    def Read(self, pin: int, sensortype: int) -> float:
        cmd = f"temp({pin},{sensortype})"
        self.transport.WriteCommand(cmd)

        res = self.transport.ReadResponse()
        return float(res.response)
        
