#coding:utf-8

class TransferBase():
    '''
    传输基础类，定义了传输的基本动作，不含实际逻辑。传输基本动作在其子类中
    '''
    def __init__(self):
        pass

    def loadConfig(self):
        pass


class ConfigBase():
    '''
    配置基础类，定义了一些配置
    '''
    def __init__(self):
        pass

class StatusCode():
    OK = 0
    def __init__(self):
        pass

class ConfirmMethod():
    '''
    确认方式
    '''
    NO_CFM = 0
    QR_CFM = 1
    BEEP_CFM = 2

    def __init__(self):
        pass

    
