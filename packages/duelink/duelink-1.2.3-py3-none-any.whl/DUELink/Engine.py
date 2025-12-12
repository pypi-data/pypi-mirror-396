import time
from DUELink.SerialInterface import SerialInterface

class EngineController:
    def __init__(self, transport : SerialInterface):
        self.transport = transport
        self.loadscript = ""    

    # run("version()/list") return version string, so need to return a string
    def Run(self) -> str:        
        self.transport.WriteCommand("run")
        
        res = self.transport.ReadResponse()

        return res.response
    
    def Stop(self) -> str:        
        self.transport.DiscardInBuffer()
        self.transport.DiscardOutBuffer()
        
        data = bytearray(1)
        data[0] = 27
        self.transport.WriteRawData(data, 0, len(data))
        
        res = self.transport.ReadResponse()

        return res.response
    
    def Select(self, num)->bool:
        cmd = f"sel({num})"

        self.transport.WriteCommand(cmd)

        res = self.transport.ReadResponse()

        return res.success
    
    def Record(self, script,region) -> bool:
        if region == 0:
            self.transport.WriteCommand("new all")  
            res = self.transport.ReadResponse() 
            if res.success == False:
                return False
        elif region == 1:
            self.transport.WriteCommand("region(1)")  
            res = self.transport.ReadResponse() 
            if res.success == False:
                return False
            
            self.transport.WriteCommand("new")  
            res = self.transport.ReadResponse() 
            if res.success == False:
                return False
        else:
            return False
        
        cmd = "pgmbrst()"

        raw = script.encode('ASCII')

        data = bytearray(len(raw) + 1)

        data[len(raw)] = 0

        data[0:len(raw)] = raw        

        self.transport.WriteCommand(cmd)

        res = self.transport.ReadResponse()

        if (res.success == False) :
            return False
        
        self.transport.WriteRawData(data, 0, len(data))

        res = self.transport.ReadResponse()

        return res.success
            
    def Read(self) -> str:
        cmd = "list"

        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponseRaw()

        return res.response 

    def ExecuteCommand(self, cmd:str) -> float:
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        if ret.success:
            try:
                return float(ret.response)
            except:
                pass

        return 0
    
    def ExecuteCommandRaw(self, cmd:str):
        self.transport.WriteCommand(cmd)
        ret = self.transport.ReadResponse()

        return ret.response


    

       