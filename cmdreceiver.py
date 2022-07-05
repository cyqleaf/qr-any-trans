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
    print(f"准备解析{len(sys.argv) - 1}个文件，其中，1个主文件，{len(sys.argv)} 个补丁文件")
    if os.path.isfile(sys.argv[1]) == False:
        print(f"主文件{sys.argv[1]}不存在，请提供合法文件名")
        return
    for i in range(2,len(sys.argv)):
        if os.path.isfile(sys.argv[i]) == False:
            print(f"补丁文件{sys.argv[i]} 不存在，请提供合法文件名")
            return

    # 主视频文件名
    file_name = sys.argv[1]
    # file_name = "~/Downloads/IMG_0560.MOV"

    # 补丁视频文件名
    patch_files = sys.argv[2:]

    # TODO 补充补丁文件解析、设立文件内容缓冲区

    cap = cv2.VideoCapture(file_name)
    video_frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    wait_for_meta = True
    rec_file_name = ""
    total_frame_count = 0
    transfer_uuid = ""
    rec_file_obj = None
    file_md5 = ""
    pre_frame = -1

    rec_file_bytes_buffer = []

    miss_frame_indexes = []


    c_index = 0
    pre_data = []
    found = 0
    while c_index < video_frame_count:
        _, im = cap.read()
        decode_res = pyzbar.decode(im)
        if len(decode_res) > 0 and decode_res[0].data[:50] != pre_data[:50]:
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
                rec_file_bytes_buffer = [[] for i in total_frame_count]
                if data_prot != "BYTES":
                    print(f"数据协议{data_prot}不支持")
                    return
                rec_file_obj = open(rec_file_name,"wb")
                wait_for_meta = False
                c_index += 1
                print(f"scaned {c_index:5d}, found{found:5d}\r",end="")
            else:
                #处理数据帧
                decode_bytes = base64.b64decode(cur_data)
                fix_head = int.from_bytes(decode_bytes[:4], byteorder="big")

                # 获取是否有后续
                has_next = ((fix_head & 0x80000000) >> 31)== 1

                # 获取是否使用额外存储空间
                ext_meta_use = ((fix_head & 0x7e000000) >> 25)

                # 获取当前帧index
                cur_frame_index = (fix_head & 0x01ffffff)

                # 发生中间丢帧
                if cur_frame_index - pre_frame > 1:
                    tmp_miss_frames = list(range(pre_frame + 1, cur_frame_index))
                    print(f"发生跳帧,{pre_frame}后识别出{cur_frame_index}, 缺失{str(tmp_miss_frames)}帧")
                    miss_frame_indexes.extend(tmp_miss_frames)
                
                pre_frame = cur_frame_index

                rec_part_md5 = decode_bytes[4:20].decode("utf-8")

                pure_data_stream = decode_bytes[20 + ext_meta_use:]

                if check_part_md5(transfer_uuid, pure_data_stream, cur_frame_index, total_frame_count ,rec_part_md5) == False:
                    print(f"第{cur_frame_index}帧md5异常！")
                
                rec_file_obj.write(pure_data_stream)
                c_index += 1
                print(f"scaned {c_index:5d}, found{found:5d}\r",end="")
                if has_next == False:
                    rec_file_obj.close()
                    print(f"\nFound Last Frame, File Saved to {rec_file_name}")
                    break
    return

def check_part_md5(transfer_uuid, pure_stream, cur_frame, total_frame, target_md5):
    md5_source = pure_stream + bytes(str(cur_frame), encoding="utf-8") + bytes(str(total_frame), encoding="utf-8") + bytes(transfer_uuid, encoding="utf-8")
    calc_md5 = hashlib.md5(md5_source).hexdigest()[8:24]
    return calc_md5 == target_md5

if __name__ == "__main__":
    main()