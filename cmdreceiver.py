#coding:utf-8
import base64
from hashlib import md5
import hashlib
import sys,os
import cv2
from pyzbar import pyzbar
import json


def main():
    print(sys.argv)
    if len(sys.argv) < 2:
        print("请提供文件名")
        return
    if os.path.isfile(sys.argv[1]) == False:
        print("请提供合法文件名")
        return

    file_name = sys.argv[1]
    # file_name = "~/Downloads/IMG_0560.MOV"

    cap = cv2.VideoCapture(file_name)
    video_frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    wait_for_meta = True
    rec_file_name = ""
    total_frame_count = 0
    transfer_uuid = ""
    rec_file_obj = None
    file_md5 = ""
    pre_frame = -1


    c_index = 0
    pre_data = []
    found = 0
    while c_index < video_frame_count:
        _, im = cap.read()
        decode_res = pyzbar.decode(im)
        if len(decode_res) > 0 and decode_res[0].data != pre_data:
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
                if data_prot != "BYTES":
                    print(f"数据协议{data_prot}不支持")
                    return
                rec_file_obj = open(rec_file_name,"wb")
                wait_for_meta = False
            else:
                #处理数据帧
                decode_bytes = base64.b64decode(cur_data)
                fix_head = int.from_bytes(decode_bytes[:4], byteorder="big")

                has_next = ((fix_head & 0x80000000) >> 31)== 1
                ext_meta_use = ((fix_head & 0x7e000000) >> 25)
                cur_frame = (fix_head & 0x01ffffff)

                if cur_frame - pre_frame > 1:
                    print(f"发生跳帧,{pre_frame}后识别出{cur_frame}, 缺失{str(list(range(pre_frame+1, cur_frame)))}帧")
                
                pre_frame = cur_frame

                rec_part_md5 = decode_bytes[4:36].decode("utf-8")

                pure_data_stream = decode_bytes[36 + ext_meta_use:]

                if check_part_md5(transfer_uuid, pure_data_stream, cur_frame, rec_part_md5) == False:
                    print(f"第{cur_frame}帧md5异常！")
                
                rec_file_obj.write(pure_data_stream)
                if has_next == False:
                    rec_file_obj.close()
                    break

            # 处理收到的UNIQUE数据
            
        c_index += 1
        print(f"scaned {c_index:5d}, found{found:5d}\r",end="")
    
    # rec_file_obj.close()


    pass

def check_part_md5(transfer_uuid, pure_stream, cur_frame, target_md5):
    md5_source = pure_stream + bytes(str(cur_frame), encoding="utf-8") + bytes(transfer_uuid, encoding="utf-8")
    calc_md5 = hashlib.md5(md5_source).hexdigest()
    return calc_md5 == target_md5

if __name__ == "__main__":
    main()