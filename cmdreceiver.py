#coding:utf-8
from ast import Bytes
import base64
from hashlib import md5
import hashlib
import sys,os
import cv2
from pyzbar import pyzbar
import json
import traceback
from io import BytesIO


class DecodeInfo():
    TMP_FILE_TYPE = ".qtt"
    def __init__(self):
        self.rec_file_name = ""
        self.file_md5 = ""
        self.total_frame_count = 0
        self.file_bytes_buffer = []
        self.miss_frame_indexes = []

    def write_full_file(self):
        file_complete = True
        bio = BytesIO()
        with open(self.rec_file_name, "wb") as rec_file:
            for i in range(len(self.file_bytes_buffer)):
                cur_bytes = bytes(self.file_bytes_buffer[i])
                rec_file.write(cur_bytes)
                bio.write(cur_bytes)
                if len(self.file_bytes_buffer[i]) == 0:
                    file_complete = False
            
        bio.seek(0, 0)
        decode_md5 = hashlib.md5(bio.read()).hexdigest()

        print(f"文件 [{self.rec_file_name}] 已写入。{'但由于有丢帧，不保证准确性' if not file_complete else ''}")
        print(f"已校验文件MD5, {'与源文件一致！' if decode_md5.strip() == self.file_md5 else '与源文件有出入，请谨慎采纳'}。 接收文件MD5:{[decode_md5]}\n 源文件的MD5:{self.file_md5}")

    def write_tmp_file(self):
        if len(self.miss_frame_indexes) == 0:
            print("Warning: 文件已无丢帧情况，但仍将按要求写入临时文件")

        # 临时文件结构:base64(json) 
        '''
        第一层base64解码后：
        {rec_file_name:"xx", file_md5:"xx", total_frame_count:"", self.file_bytes_buffer:{1:[base64],2:[base64]}, miss_frame_indexes:[number,number] }
        '''
        # 先制作主数据buffer
        buffer_dict_base_64 = dict()

        for i in range(len(self.file_bytes_buffer)):
            if len(self.file_bytes_buffer[i]) > 0:
                buffer_dict_base_64[i] = base64.b64encode(self.file_bytes_buffer[i]).decode("utf-8")
        
        tmp_file_dict = dict()
        tmp_file_dict["rec_file_name"] = self.rec_file_name
        tmp_file_dict["file_md5"] = self.file_md5
        tmp_file_dict["total_frame_count"] = self.total_frame_count
        tmp_file_dict["file_bytes_buffer"] = buffer_dict_base_64
        tmp_file_dict["miss_frame_indexes"] = self.miss_frame_indexes

        tmp_file_dict_json = json.dumps(tmp_file_dict)

        tmp_file_base64 = base64.b64encode(tmp_file_dict_json.encode("utf-8"))

        tmp_file_name = self.rec_file_name + DecodeInfo.TMP_FILE_TYPE
        with open(tmp_file_name, "wb") as tmp_file:
            tmp_file.write(tmp_file_base64)

        print(f"已写入临时文件 [{tmp_file_name}] 。")

def read_from_tmp_file(tmp_file_name:str, decode_info: DecodeInfo):
    tmp_file_dict = dict()

    with open(tmp_file_name, "rb") as tmp_file:
        tmp_file_bytes = tmp_file.read()
        tmp_file_json = base64.b64decode(tmp_file_bytes).decode("utf-8")

        tmp_file_dict = json.loads(tmp_file_json)

    decode_info.rec_file_name = tmp_file_dict["rec_file_name"]
    decode_info.file_md5 = tmp_file_dict["file_md5"]
    decode_info.total_frame_count = int(tmp_file_dict["total_frame_count"])
    decode_info.miss_frame_indexes = tmp_file_dict["miss_frame_indexes"]

    decode_info.file_bytes_buffer = [[] for i in range(decode_info.total_frame_count)]

    for key in tmp_file_dict["file_bytes_buffer"].keys():
        decode_info.file_bytes_buffer[int(key)] = base64.b64decode(tmp_file_dict["file_bytes_buffer"][key])

    if len(decode_info.miss_frame_indexes) > 0:
        print(f"识别临时文件后总丢帧情况：{decode_info.miss_frame_indexes}")
        return False
    else:
        print(f"识别临时文件完成无丢帧")
        return True


def main():
    print(sys.argv)
    if len(sys.argv) < 2:
        print("请提供文件名")
        return
    print(f"准备解析{len(sys.argv) - 1}个文件，其中，1个主文件，{len(sys.argv[2:])} 个补丁文件")
    if os.path.isfile(sys.argv[1]) == False:
        print(f"主文件{sys.argv[1]}不存在，请提供合法文件名")
        return
    for i in range(2,len(sys.argv)):
        if os.path.isfile(sys.argv[i]) == False:
            print(f"补丁文件{sys.argv[i]} 不存在，请提供合法文件名")
            return

    # 主视频文件名
    main_file_name = sys.argv[1]
    # file_name = "~/Downloads/IMG_0560.MOV"

    # 补丁视频文件名
    patch_files = sys.argv[2:]

    # TODO 补充补丁文件解析、设立文件内容缓冲区
    decode_info = DecodeInfo()
    
    try:
        finish = True
        if main_file_name.strip().endswith(".qtt"):
            finish = read_from_tmp_file(main_file_name, decode_info=decode_info)
        else:
            finish = decode_frames(main_file_name, False, decode_info=decode_info)

        print("检查补丁文件。。。" if len(patch_files) > 0 else "")
        for patch_file_name in patch_files:
            if finish is True:
                break
            print(f"检查补丁文件 [{patch_file_name}]")
            finish = decode_frames(patch_file_name, True, decode_info=decode_info)

        if decode_info.rec_file_name.strip() == "":
            print("未获取到文件名，失败")
            return
        
        if finish == False:
            print(f"仍有丢帧情况，但文件将如实写入，同时写入临时文件，请检查能否打开")
            decode_info.write_tmp_file()
        
        decode_info.write_full_file()
        

    except Exception as e:
        print(f"解析失败, {e}")
        traceback.print_exc()
    

    return

def decode_frames(video_file_name:str, is_patch:bool, decode_info:DecodeInfo) -> bool:
    cap = cv2.VideoCapture(video_file_name)
    video_frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    wait_for_meta = True
    rec_file_name = ""
    total_frame_count = 0
    transfer_uuid = ""
    file_md5 = ""
    pre_frame = -1

    c_index = 0
    pre_data = []
    found = 0
    has_next = True
    last_detected_frame_index = 0
    while c_index < video_frame_count:
        _, im = cap.read()
        decode_res = list(filter(lambda dr: dr.type == "QRCODE", pyzbar.decode(im)))
        c_index += 1
        if len(decode_res) > 0 and decode_res[0].data[:30] != pre_data[:30]:
            found += 1
            pre_data = decode_res[0].data
            cur_data = decode_res[0].data

            # 处理meta帧
            if wait_for_meta is True:
                hand_shake_str = bytes(cur_data).decode("utf-8")
                hand_shake_jsonobj = json.loads(hand_shake_str)
                transfer_uuid = hand_shake_jsonobj["uuid"]
                rec_file_name = hand_shake_jsonobj["main_data"]["file_name"]
                file_md5 = hand_shake_jsonobj["main_data"]["file_md5"]

                data_prot = hand_shake_jsonobj["main_data"]["data_prot"]
                total_frame_count = hand_shake_jsonobj["main_data"]["total_data_frame_count"]

                # 首次，记录信息，补丁，核对信息，但，transferUUID是每次不同的，不必核对
                if is_patch == False:
                    decode_info.rec_file_name = rec_file_name
                    decode_info.file_md5 = file_md5
                    decode_info.total_frame_count = total_frame_count
                    decode_info.file_bytes_buffer =  [[] for i in range(total_frame_count)]
                    print(f"接收文件 {decode_info.rec_file_name}  中")
                else:
                    if decode_info.file_md5 != file_md5:
                        raise Exception(f"补丁MD5 {file_md5} 与原始文件MD5{decode_info.file_md5}不同")
                        return

                if data_prot != "BYTES":
                    print(f"数据协议{data_prot}不支持")
                    return
                # rec_file_obj = open(rec_file_name,"wb")
                wait_for_meta = False
                print(f"scaned {c_index:5d}, found{found:5d}\r",end="")
            else:
                #处理数据帧
                decode_bytes = base64.b85decode(cur_data)
                fix_head = int.from_bytes(decode_bytes[:4], byteorder="big")

                # 获取是否有后续
                has_next = ((fix_head & 0x80000000) >> 31)== 1

                # 获取是否使用额外存储空间
                ext_meta_use = ((fix_head & 0x7e000000) >> 25)

                # 获取当前帧index
                cur_frame_index = (fix_head & 0x01ffffff)

                # 发生中间丢帧
                if is_patch == False and cur_frame_index - pre_frame > 1:
                    tmp_miss_frames = list(range(pre_frame + 1, cur_frame_index))
                    print(f"发生丢帧,{pre_frame}后识别出{cur_frame_index}, 缺失{str(tmp_miss_frames)}帧")
                
                pre_frame = cur_frame_index

                rec_part_md5 = decode_bytes[4:20].decode("utf-8")

                pure_data_stream = decode_bytes[20 + ext_meta_use:]

                if check_part_md5(transfer_uuid, pure_data_stream, cur_frame_index, total_frame_count ,rec_part_md5) == False:
                    print(f"第{cur_frame_index}帧md5异常！计入丢帧")
                else:
                    decode_info.file_bytes_buffer[cur_frame_index] = pure_data_stream
                
                print(f"scaned {c_index:5d}, found{found:5d}\r",end="")
                last_detected_frame_index = cur_frame_index
                if is_patch == False and has_next == False:
                    break
    
    # 检查是否缺失末帧
    if is_patch == False and last_detected_frame_index < total_frame_count - 1:
        tmp_miss_frames = list(range(last_detected_frame_index+ 1, total_frame_count))
        print(f"发生丢帧,{last_detected_frame_index}后未识别直至末尾。缺失{str(tmp_miss_frames)}帧")

    # 计算丢帧情况
    decode_info.miss_frame_indexes = []
    for i in range(decode_info.total_frame_count):
        if decode_info.file_bytes_buffer[i] is None or len(decode_info.file_bytes_buffer[i]) == 0:
            decode_info.miss_frame_indexes.append(i)
    

    if len(decode_info.miss_frame_indexes) > 0:
        print(f"本次识别后总丢帧情况：{decode_info.miss_frame_indexes}")
        return False
    else:
        print(f"识别完成无丢帧")
        return True

def check_part_md5(transfer_uuid, pure_stream, cur_frame, total_frame, target_md5):
    md5_source = pure_stream + bytes(str(cur_frame), encoding="utf-8") + bytes(str(total_frame), encoding="utf-8") + bytes(transfer_uuid, encoding="utf-8")
    calc_md5 = hashlib.md5(md5_source).hexdigest()[8:24]
    return calc_md5 == target_md5

if __name__ == "__main__":
    main()