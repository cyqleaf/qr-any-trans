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


if __name__ == "__main__":
    test_str = "doyouhear the people sing" * 10000
    print(len(test_str))

    bs = test_str.encode("utf-8")
    print(len(bs))

    # test_myqr(bs)
    test_qrcode(bs)

    
