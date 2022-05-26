#coding:utf-8

from TransConfigBase import *
from utils import StringUtil
import hashlib, json


class TransferV1(TransferBase):
    '''
    第一版传输器
    '''
    def __init__(self):
        super.__init__()

class HandshakeDataV1():
    '''
    握手传输的主数据
    '''
    def __init__(self, file_name, file_size_kB, file_type, file_md5, data_prot, data_prot_v, confirm_method = ConfirmMethod.NO_CFM):
        self.file_name = file_name
        self.file_size_kB = file_size_kB
        self.file_type = file_type
        self.file_md5 = file_md5
        self.data_prot = data_prot
        self.data_prot_v = data_prot_v
        self.confirm_method = confirm_method
        
        pass

class HandshakePkgV1():
    '''
    握手数据包
    '''

    def __init__(self, success:bool, status_code:int, status_msg_12:str, transfer_uuid:str, handshake_data:HandshakeDataV1):
        self.success = success
        self.status_code = status_code
        self.status_msg_12 = status_msg_12
        self.pkg_version = "1.0"
        self.uuid = transfer_uuid
        self.main_data = handshake_data

        self.main_data_md5 = self._gen_hand_shake_main_data_md5()
        self.hand_shake_data_md5 = self._gen_hdsk_md5()
        
        pass

    def gen_hspkg_json(self) -> str:
        return json.dump(self)

    def _verify(self) -> tuple:
        if StringUtil.is_empty(self.main_data_md5):
            return (False, "主数据md5缺失")
        
        if StringUtil.is_empty(self.hand_shake_data_md5):
            return (False, "握手数据md5缺失")

        if StringUtil.is_empty(self.uuid):
            return (False, "传输器UUID缺失")

        return (True, "OK")

    def _gen_hdsk_md5(self) -> str:
        '''
        多端MD5算法必须一致。
        握手包版本号_主数据md5_uuid 算md5
        '''
        return StringUtil.get_md5_lowerhex(f"{self.pkg_version}_{self.main_data_md5}_{self.uuid}")

    def _gen_hand_shake_main_data_md5(self) -> str:
        '''
        多端MD5算法必须一致，现在不需要
        '''
        return "default"

        



