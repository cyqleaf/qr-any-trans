#coding:utf-8

from http.client import OK
from TransConfigBase import TransferBase
from TransConfigBase import ConfigBase


class TransferV1(TransferBase):
    '''
    第一版传输器
    '''
    def __init__(self):
        super.__init__()

class HandshakePkg():
    '''
    握手数据包
    '''

    def __init__(self):
        self.success = False
        self.status_code = OK
        self.status_msg_12 = ""
        self.pkg_version = "1.0"
        self.main_data_md5 = ""
        self.hand_shake_data_md5 = ""
        self.uuid = ""

        pass

class HandshakeData():
    '''
    握手传输的主数据
    '''
    def __init__(self):
        self.file_name = ""
        self.file_size_kB = ""
        self.file_type = ""
        self.file_md5 = ""
        self.data_prot = ""
        self.data_prot_v = ""
        self.confirm_method = ConfirmMethod.NO_CFM



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



