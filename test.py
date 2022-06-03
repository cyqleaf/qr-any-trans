import qrcode, base64, time
import random
from threading import Thread
from multiprocessing import Process
from MyQR import myqr

class MyThread(Thread):
    def __init__(self, target = None):
        Thread.__init__(self, target=target)
        self.finish = False
    
    def run(self):
        Thread.run(self)
        self.finish = True

def mk_qr_imgs_t(qrs, res_list):
    print(f"需要处理{len(qrs)}个图片")
    for qr in qrs:
        res_list.append(qr.make_image())

def test_qrcode(bs:str):
    qrs = []
    ims = []

    st = time.time()
    for i in range(40):
        qr = qrcode.QRCode(version=39, error_correction= qrcode.ERROR_CORRECT_M,box_size=5,border=2)
        random_pos = random.randint(0, len(bs) - 1652)
        encoded = base64.b64encode(bs[random_pos:random_pos + 1650]).decode("utf-8")
        qr.add_data(encoded)
        print(f"v:{qr.version} ", end="")
        qrs.append(qr)
    print()
    end = time.time()
    cost_ms = (end-st) * 1000
    print(f"生成数据耗时{cost_ms:.2f}毫秒")

    T_COUNT = 1


    st = time.time()
    rev_lists = [[]for i in range(T_COUNT)]
    threads = []
    batch_size = len(qrs) // T_COUNT
    for i in range(T_COUNT):
        batch_size_final = batch_size
        if i == T_COUNT - 1:
            batch_size_final = len(qrs)
        st_pos = i * batch_size
        end_pos = i * batch_size + batch_size_final
        print(f"durition:{st_pos}~{end_pos}")
        threads.append(Process(target = mk_qr_imgs_t, args=(qrs[st_pos: end_pos], rev_lists[i])))
    for proc in threads:
        proc.start()
        
    for proc in threads:
        proc.join()
        
    end = time.time()
    cost_ms = (end-st) * 1000
    print(f"耗时{cost_ms:.2f}毫秒, 平均{cost_ms/40:.2f}毫秒")

def test_myqr(bs:str):
    qrs = []
    ims = []

    st = time.time()
    for i in range(40):
        random_pos = random.randint(0, len(bs) - 1652)
        encoded = base64.b64encode(bs[random_pos:random_pos + 1650]).decode("utf-8")
        qrs.append(encoded)
    print()
    end = time.time()
    cost_ms = (end-st) * 1000
    print(f"生成数据耗时{cost_ms:.2f}毫秒")

    st = time.time()
    threads = []
    threads.append(Thread(target=lambda: myqrgen(qrs[:20], "t1"), daemon=True))
    threads.append(Thread(target=lambda: myqrgen(qrs[20:], "t2"), daemon=True))

    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    end = time.time()
    cost_ms = (end-st) * 1000
    print(f"多线程耗时{cost_ms:.2f}毫秒, 每个图片{cost_ms / len(qrs):.2f}毫秒")

    
    
def myqrgen(strs:list, name_fix:str):
    for i in range(len(strs)):
        myqr.run(strs[i],39,'M',save_name=f"test_{i}_{name_fix}.jpg", save_dir="./myqrtest/")

def test_create_and_map():
    from qrcode import QRCode
    from qrcode import util
    import time

    data = "doseslae" * 20000
    data = data.encode("utf-8")
    # print(data)
    qrs = []

    ori_map_data = QRCode.map_data
    def new_map_data(self, data, mask_pattern):
        st = time.time()
        ori_map_data(self, data, mask_pattern)
        end = time.time()
        cost_ms = (end-st) * 1000
        print(f"map_cost:{cost_ms:.2f}毫秒")

    QRCode.map_data=new_map_data

    for i in range(200):
        qr = QRCode(version = 39,mask_pattern=5)
        qr.add_data(util.QRData(data[i:1920+i]))
        qrs.append(qr)
    # qr.best_fit()
    # print(qr.version)
    st = time.time()
    for qr in qrs:
        qr.make_image()
    end = time.time()
    print(f"总时间:{end - st}, 最大帧数:{200 / (end-st):.2f}, 每帧时间:{(end-st)*1000/200:.2f}毫秒")

    # print(qr.modules)


if __name__ == "__main__":
    test_str = "doyouhear the people sing" * 10000
    print(len(test_str))

    bs = test_str.encode("utf-8")
    print(len(bs))

    test_create_and_map()

    # test_myqr(bs)
    # test_qrcode(bs)

    
