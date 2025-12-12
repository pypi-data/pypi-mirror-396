from enum import IntEnum
from DUELink.Stream import StreamController


class GraphicsType(IntEnum):    
    I2C = 1
    SPI = 2
    Neo = 3
    Matrix5x5 = 4


class GraphicsController:
    def __init__(self, transport,stream:StreamController):
        self.transport = transport
        self.stream = stream
    
    def Configuration(self, displayType, config, width, height, mode)->bool:

        #if not isinstance(config, list) or not all(isinstance(x, int) and 0 <= x <= 255 for x in config):
        #    raise ValueError("Enter a list with one number into the config with a valid code for a display.")
    
        #inputConfig = map(hex, config)
        
        #inputConfigArray = ",".join(inputConfig)
        
        #inputConfigArray = "{" + inputConfigArray + "}"

        #cmd = "MelodyP({0}, {{{1}}})".format(pin, ", ".join(map(str, notes)))
        # declare a9 array
        count = len(config)
        # declare a9 array
        cmd = f"dim a9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to a9
        ret = self.stream.WriteFloats("a9",config)
        
        cmd = f"gfxcfg({displayType}, a9, {width}, {height}, {mode})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success
        
    def Show(self)->bool:
        cmd = "show()"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def Clear(self, color)->bool:
        cmd = f"clear({color})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def Pixel(self, color, x, y)->bool:
        cmd = f"pixel({color},{x},{y})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def Circle(self, color, x, y, radius)->bool:
        cmd = f"circle({color},{x},{y},{radius})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def Rect(self, color, x, y, width, height)->bool:
        cmd = f"rect({color},{x},{y},{width},{height})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def Fill(self, color, x, y, width, height)->bool:
        cmd = f"fill({color},{x},{y},{width},{height})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def Line(self, color, x1, y1, x2, y2)->bool:
        cmd = f"line({color},{x1},{y1},{x2},{y2})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def Text(self, text, color, x, y)->bool:
        cmd = f"text(\"{text}\",{color},{x},{y})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success
    
    def TextT(self, text, color, x, y)->bool:
        cmd = f"textt(\"{text}\",{color},{x},{y})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    def TextS(self, text, color, x, y, scalewidth, scaleheight)->bool:
        cmd = f"texts(\"{text}\",{color},{x},{y},{scalewidth},{scaleheight})"
        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        return res.success

    # def __Stream(self, data, color_depth: int):
    #     cmd = f"stream({color_depth})"
    #     self.transport.WriteCommand(cmd)
    #     res = self.transport.ReadResponse()

    #     if res.success:
    #         self.transport.WriteRawData(data, 0, len(data))
    #         # time.sleep(10)
    #         res = self.transport.ReadResponse()

    #     return res.success

    def DrawImageScale(self, img, x: int, y: int, width: int, height: int, transform: int, scaleWidth: int, scaleHeight: int) -> bool:

        if width <= 0 or height <= 0 or len(img) < width * height:
            raise Exception("Invalid arguments")

        cmd = f"dim a9[{len(img)}]"

        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()

        written = self.stream.WriteFloats("a9", img)

        
        cmd = f"imgs(a9, {x}, {y}, {width}, {height}, {transform}, {scaleWidth}, {scaleHeight})"

        self.transport.WriteCommand(cmd)
        res = self.transport.ReadResponse()
        
        return res.success

    def DrawImage(self, img, x: int, y: int, width: int, height: int, transform: int) -> bool:
        return self.DrawImageScale(img, x, y, width, height, transform, 1, 1)