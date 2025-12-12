from DUELink.Graphics import GraphicsType

class GraphicsTypeController():  
    def __init__(self):
        pass

    def __get_I2C(self):
        return GraphicsType.I2C
    def __get_SPI(self):
        return GraphicsType.SPI
    def __get_Neo(self):
        return GraphicsType.Neo
    def __get_Matrix5x5(self):
        return GraphicsType.Matrix5x5
    
    def __set_empty(self, value: int):
        return   

    I2c = property(__get_I2C, __set_empty)  
    Spi = property(__get_SPI, __set_empty)  
    Neo = property(__get_Neo, __set_empty)  
    Matrix5x5 = property(__get_Matrix5x5, __set_empty)  
    



        



        
    
