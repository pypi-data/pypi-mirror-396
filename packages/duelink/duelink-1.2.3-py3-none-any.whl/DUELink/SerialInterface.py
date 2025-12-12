import time
import serial
from datetime import datetime, timedelta
from DUELink.DeviceConfiguration import DeviceConfiguration
import re

class SerialInterface:
    CommandCompleteText = ">"
    DefaultBaudRate = 115200

    DeviceConfig : DeviceConfiguration

    def __init__(self, portName):        
        self.ReadTimeout = 3
        self.portName = portName
        self.echo = True 
    

    def Connect(self):
        self.portName = serial.Serial(self.portName, self.DefaultBaudRate, parity=serial.PARITY_NONE, bytesize=8, stopbits=serial.STOPBITS_ONE)
        self.portName.timeout = self.ReadTimeout        
        time.sleep(0.1)
        self.Synchronize()


    def Disconnect(self):
        try:
            self.portName.close()
        except:
            pass
        self.port = None

    def Synchronize(self):
        cmd = bytearray(1)
        cmd[0] = 10 # do not terminal loop since we support asio(1) host runs

        self.WriteRawData(cmd, 0, 1)
        
        time.sleep(0.4)

        self.WriteCommand("sel(1)")

        end = datetime.now() + timedelta(seconds=self.ReadTimeout)

        while datetime.now() < end and self.portName.in_waiting == 0:
            time.sleep(0.001) # wait 1ms for sure

        if  datetime.now() > end:
            raise Exception("Sync device failed.")
                
        self.portName.reset_input_buffer()
        self.portName.reset_output_buffer() 
        
        
    #def RemoveEchoRespone(self, response, cmd):
    #    if cmd in response:
    #        response = response[len(cmd):]
    #
    #    return response

    # def CheckResult(self, actual, expected):
    #     if actual != expected:
    #         raise Exception(f"Expected {expected}, got {actual}.")
    
    def DiscardInBuffer(self):
        self.portName.reset_input_buffer()

    def DiscardOutBuffer(self):
        self.portName.reset_output_buffer()

    def WriteCommand(self, cmd):
        self.DiscardInBuffer()
        self.DiscardOutBuffer()

        #command = cmd.lower()
        # these commands - statement can't use with println        
        #statement_list = ["print", "dim", "run"]
        #for statement in statement_list:
        #    i = command.index(statement)
        #    if i == 0:
        #        break


        #if (
        #    command.find('print') == 0 or 
        #    command.find('dim') == 0 or
        #    command.find('run') == 0 or
        #    command.find('list') == 0 or
        #    command.find('new') == 0 or
        #    command.find('echo') == 0 or
        #    command.find('sel') == 0 or
        #    command.find('version') == 0 or
        #    command.find('alias') == 0 or            
        #    command.find('sprintf') == 0 
        #):
        #    self.__WriteLine(cmd)
        #elif self.EnabledAsio == True:
        #    newcmd = f"println({cmd})"
        #    self.__WriteLine(newcmd)
        #else:
        #    self.__WriteLine(cmd)
        self.__WriteLine(cmd)

    def __WriteLine(self, string):
        string += "\n"
        # print(string)
        self.portName.write(bytes(string, 'utf-8'))

    def ReadResponse(self):
        str = ""
        end = datetime.now() + timedelta(seconds=self.ReadTimeout)

        resp = CmdRespone()

        responseValid = True
        dump = 0
        total_receviced = 0

        while datetime.now() < end or self.portName.in_waiting > 0:
            if self.portName.in_waiting > 0:
                data = self.portName.read(1)
                str += data.decode()
                
                total_receviced = total_receviced + 1
                
                if data.decode()[0] == '\n':
                    end_newline_expired = datetime.now() + timedelta(milliseconds=50) # 50ms timeout for \n

                    while (self.portName.in_waiting == 0 and datetime.now() < end_newline_expired ):
                        time.sleep(0)
                    
                    # next byte can be >, &, !, $
                    if (self.portName.in_waiting > 0):
                        dump = self.portName.read(1)

                        if (dump.decode()[0] == '>' or dump.decode()[0] == '!' or dump.decode()[0] == '$'):
                            #valid data      
                            time.sleep(0.001) # wait 1ms for sure

                            if (self.portName.in_waiting > 0):
                                responseValid = False
                        elif (dump.decode()[0] == '\r'): #there is case 0\r\n\r\n> if use println("btnup(0)") example, this is valid
                            if (self.portName.in_waiting == 0):
                                time.sleep(0.001) 

                            if (self.portName.in_waiting > 0):
                                dump = self.portName.read(1)

                                if (dump.decode()[0] == '\n'):
                                    if (self.portName.in_waiting > 0):
                                        dump = self.portName.read(1)
                                else:
                                    responseValid = False
                            else:
                                responseValid = False
                        else:
                            # bad data
                            # One cmd send suppose one response, there is no 1234\r\n5678.... this will consider invalid response
                            responseValid = False
                    
                    if responseValid == False:
                        d = 0

                        while d != '\n' and datetime.now() < end:
                            if (self.portName.in_waiting > 0):
                                dump = self.portName.read(1)
                                d = dump.decode()[0]
                            else:
                                time.sleep(0.001) 
                            
                            if d == '\n':
                                if (self.portName.in_waiting > 0): # still bad data, repeat clean up
                                    d = 0 #reset to repeat the condition while loop

                    if str == "" or len(str) < 2: #reponse valid has to be xxx\r\n or \r\n, mean idx >=2
                        responseValid = False
                    elif responseValid == True:
                        if str[len(str)-2] != '\r':
                            responseValid = False
                        else:
                            str = str.replace("\n", "")
                            str = str.replace("\r", "")

                    break
                elif data.decode()[0] == '>' or data.decode()[0] == '&':
                    if total_receviced == 1:
                        time.sleep(0.002)
                        if (self.portName.in_waiting == 0):
                            resp.success = True
                            resp.response = ""
                            return resp
                    
                end = datetime.now() + timedelta(seconds=self.ReadTimeout) #reset timeout after valid data 

                

        self.portName.reset_input_buffer()
        self.portName.reset_output_buffer()

        resp.success = (total_receviced > 1) and (responseValid == True)
        resp.response = str

        return resp
    
    def ReadResponseRaw(self):
        str = ""
        end = datetime.now() + timedelta(seconds=self.ReadTimeout)

        resp = CmdRespone()

        while datetime.now() < end:
            if self.portName.in_waiting > 0:
                data = self.portName.read()
                str += data.decode()
                end = datetime.now() + timedelta(seconds=self.ReadTimeout)

        self.portName.reset_input_buffer()
        self.portName.reset_output_buffer()

        if str != "":
            if len(str) >= 3:
                resp.response= str[0:len(str)-3]

            resp.success = True

        return resp

    TransferBlockSizeMax = 512
    TransferBlockDelay = 0.005

    def WriteRawData(self, buffer, offset, count):
        block = int(count / self.TransferBlockSizeMax)
        remain = int(count % self.TransferBlockSizeMax)

        idx = offset

        while block > 0:
            self.portName.write(buffer[idx:idx + self.TransferBlockSizeMax])
            idx += self.TransferBlockSizeMax
            block -= 1
            time.sleep(self.TransferBlockDelay)

        if remain > 0:
            self.portName.write(buffer[idx:idx + remain])

            #time.sleep(self.TransferBlockDelay)

    def ReadRawData(self, buffer, offset, count):
        end = datetime.now() + timedelta(seconds=self.ReadTimeout)


        countleft = count
        totalRead = 0

        
        #while end > datetime.now():
            #read = self.portName.readinto(buffer[offset + totalRead:offset + count])
            #totalRead += read

            #if read > 0:
            #    end = datetime.now() + timedelta(seconds=self.ReadTimeout)

            #if totalRead == count:
            #    break

        #return totalRead

        data = self.portName.read(count)

        if len(data) == 0:
            return 0 

        for i in range(offset,offset + count):
            buffer[i] = data[i-offset]


        return count
    
    def BytesToRead(self):
        return self.portName.in_waiting
    
    def ReadByte(self):
        data = self.portName.read(1)
        return data.decode()[0]

class CmdRespone:
    def __init__(self):
        self.response = ""
        self.success = False
    ######################################## OLD VERSION #####################################################
    # def CmdResponse(self):
    #     self.response = ""
    #     self.success = False
    #
    # def ReadResponse(self) -> CmdResponse:
    #     str = self.leftOver
    #     end = datetime.now() + timedelta(seconds=self.ReadTimeout)
    #
    #     resp = SerialInterface.CmdResponse
    #
    #     while end > datetime.now():
    #         data = self.portName.read()
    #
    #         str += data.decode('utf-8')
    #
    #         str = str.replace("\n", "")
    #
    #         idx1 = str.find(">")
    #         idx2 = str.find("&")
    #
    #         if idx1 == -1 and idx2 == -1:
    #             continue
    #
    #         idx = idx1 if idx1 != -1 else idx2
    #
    #         self.leftOver = str[idx + 1:]
    #         resp.success = True
    #         resp.response = str[:idx]
    #
    #         idx3 = str.find("!")
    #         if idx3 != -1 and "error" in resp.response:
    #             resp.success = False
    #
    #         return resp
    #
    #     self.leftOver = ""
    #     self.portName.reset_input_buffer()
    #     self.portName.reset_output_buffer()
    #
    #     resp.success = False
    #     resp.response = ""
    #
    #     return resp
    #
    # TransferBlockSizeMax = 256
    # TransferBlockDelay = 1
    #
    #
    #
    # def GetVersion(self):
    #     command = "version()"
    #     self.WriteCommand(command)
    #     version = self.ReadResponse()
    #     self.ReadCommandComplete()
    #     if version["success"]:
    #         if self.echo and command in version["response"]:
    #             # echo is on => need to turn off
    #             self.TurnEchoOff()
    #             self.portName.reset_input_buffer()
    #             self.portName.reset_output_buffer()
    #             version["response"] = version["response"][len(command):]
    #     return version["response"]
    #
    # def RemoveEchoRespone(self, response, cmd):
    #     if cmd in response:
    #         response = response[len(cmd):]
    #     return response
    #
    # def WriteCommand(self, command):
    #     self.WriteCommand(command)
    #
    # def WriteCommand(self, string):
    #     string += "\n"
    #     print(string)
    #     self.portName.write(bytes(string, 'utf-8'))
    #
    # def ReadCommandComplete(self):
    #     self.check_result(str(self.ReadResponse()), self.CommandCompleteText)


    ############################### This Function delay the process too much ###########################################
    # def check_result(self,actual: str, expected: str):
    #     if actual != expected:
    #         raise ValueError(f"Expected {expected}, got {actual}.")

    ####################################################################################################################


    # class CmdResponse:
    #     def __init__(self):
    #         self.response = ""
    #         self.success = False


