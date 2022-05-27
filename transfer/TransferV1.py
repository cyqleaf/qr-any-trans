#coding:utf-8

from io import BytesIO
from tempfile import TemporaryFile
from TransConfigBase import ConfirmMethod, StatusCode, TransferBase
import StringUtil
import hashlib, json, base64, math, uuid
import qrcode

DATA_PROT_SINGLE_CLR = "single-color"
DATA_PROT_RGB = "rgb"
BATCH_SIZE_BYTE = 1536

DATA_PROT_V_1 = 1

class TransferV1(TransferBase):

    '''
    第一版传输器
    实现功能：base64编码、next函数、定位到任意位函数
    '''
    def __init__(self, file_name: str, bio: BytesIO, data_prot:str, data_prot_v: int, confirm_method: int = ConfirmMethod.NO_CFM):
        TransferBase.__init__(self)
        self.file_name = file_name
        self.file_bio = bio
        self.data_prot = data_prot
        self.confirm_method = confirm_method
        self.index = 0
        self.data_prot_v = data_prot_v
        if "." in self.file_name:
            self.file_type = self.file_name[::-1].split(".")[0][::-1]
        
        # 生成UUID
        self.trans_uuid = str(uuid.uuid4()).replace("-","")

        # 计算文件大小和总批次数
        self.file_bio.seek(0, 2)
        self.file_size_Byte = self.file_bio.tell()
        self.total_batch_count = int(math.ceil(self.file_size_Byte / BATCH_SIZE_BYTE))

        # 计算文件MD5
        self.file_bio.seek(0)
        self.file_md5 = hashlib.md5(self.file_bio.read()).hexdigest()

        #恢复文件指针
        self.file_bio.seek(0,0)

        # 生成握手包
        self.hand_shake_pkg = self._gen_handshake_pkg()

    def next_batch(self):
        self.index  = (self.index + 1) % self.total_batch_count
        return self.index

    def gen_cur_qr(self):
        json_str = self.gen_batch_data_json()
        qr = qrcode.QRCode(30)
        try:
            qr.add_data(json_str)
            qr.best_fit()
            return qr.make_image()
        except Exception as e:
            print(f"生成二维码失败,{e}")
            return None
        
    def gen_batch_data_json(self):
        
        main_data = self._gen_main_data()

        json_str = ""

        try:
            json_str = json.dumps(main_data.__dict__)
        except Exception as e:
            print(e)
        
        return json_str
        

    def _gen_main_data(self):
        part_bytes = self.file_bio.read(BATCH_SIZE_BYTE)
        part_md5 = hashlib.md5(part_bytes).hexdigest()

        data_b64 = base64.b64encode(part_bytes).decode("utf-8")

        main_data = MainDataV1(data_b64, self.index, self.total_batch_count, self.trans_uuid, part_md5)

        return main_data

        

        

    def _gen_handshake_pkg(self):
        handshake_data = HandshakeDataV1(self.file_name, int(self.file_size_Byte / 1024), self.file_type, self.file_md5, self.data_prot,\
            self.data_prot_v, self.confirm_method)

        hand_shake_pkg = HandshakePkgV1(True, StatusCode.OK, "ok", self.trans_uuid, handshake_data)

        return hand_shake_pkg



class HandshakeDataV1():
    '''
    握手传输的主数据
    '''
    def __init__(self, file_name:str, file_size_kB:int, file_type:str, file_md5:str, data_prot:str, data_prot_v:str, confirm_method:int = ConfirmMethod.NO_CFM):
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
        self.main_data = handshake_data.__dict__

        self.main_data_md5 = self._gen_hand_shake_main_data_md5()
        self.hand_shake_data_md5 = self._gen_hdsk_md5()
        
        pass

    def gen_hspkg_json(self) -> str:
        return json.dumps(self)

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

class MainDataV1():
    '''
    主数据包，相对简单，一个数据包的__dict__对应一个二维码
    '''
    def __init__(self, data_b64:str, index: int, total: int, uuid: str, md5:str):
        self.data_b64 = data_b64
        self.index = index
        self.total = total
        self.uuid = uuid
        self.md5 = md5
        

def main():
    bio = BytesIO()
    with open("../../this.pdf", "rb") as afile:
        bio.write(afile.read())

    transfer = TransferV1("this.pdf", bio, DATA_PROT_SINGLE_CLR, DATA_PROT_V_1)

    print(transfer.total_batch_count)

    

    pass

if __name__ == "__main__":
    main()
    pass
