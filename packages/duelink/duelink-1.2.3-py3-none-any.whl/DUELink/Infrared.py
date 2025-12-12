class InfraredController:
    def __init__(self, transport):
        self.transport = transport

    def Read(self)->int:
        cmd = "irread()"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()

        if res.success:
            try:
                return int(res.response)
            except:
                pass
        return -1
    
    def Write(self, command: int)->bool:
        cmd = f"IrWrite({command})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def Enable(self, txpin:int, rxpin: int)->bool:
        cmd = f"iren({txpin}, {rxpin})"
        self.transport.WriteCommand(cmd)

        res = self.transport.ReadResponse()
        return res.success
