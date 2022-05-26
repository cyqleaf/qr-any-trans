#coding:utf-8

import hashlib


def is_empty(a:str) -> bool:
    '''
    判断字符串是否为None或者空
    '''
    return a is None or a.strip() == ""

def get_md5_lowerhex(content: str) -> bool:
    '''
    生成md5字符串
    '''
    if content == None:
        content = ""

    md5 = hashlib.md5(content.encode("UTF-8"))
    return md5.hexdigest()