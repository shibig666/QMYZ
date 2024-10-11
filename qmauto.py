import requests
import csv
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import ast
import threading
import re
import api
import time

# 请填写以下参数
courseId = '521'  # 课程id
key_base64 = 'ZDBmMTNiZGI3MDRhMWVhMWE3MTcwNjJiNTk0NzY0ODg'  # SB题库搞NM的加密，如果密钥不变不需要修改
JSESSIONID = ''  # 写你的
csv_file_path = "./qmyz/新生入学.csv"  # 需要替换为实际CSV文题库路径



def fix_base64_padding(b64_string):
    return b64_string + '=' * (-len(b64_string) % 4)


# AES ECB 解密函数
def aes_ecb_decrypt(ciphertext_base64, key_base64):
    ciphertext_base64 = fix_base64_padding(ciphertext_base64)
    key_base64 = fix_base64_padding(key_base64)
    ciphertext = base64.b64decode(ciphertext_base64)
    key = base64.b64decode(key_base64)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_data.decode('utf-8')


def loadCSV(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)[1:]



# 请求相关参数
cookies = {
    'JSESSIONID': JSESSIONID,
}

headers = {
    'Accept': 'application/json',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://112.5.88.114:31101',
    'Pragma': 'no-cache',
    'Referer': 'http://112.5.88.114:31101/yiban-web/stu/toSubject.jhtml?courseId=' + courseId,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
}

params = {
    '_': str(time.time_ns())[:13],
}

data = {
    'courseId': courseId,
}

AB = {0: "A", 1: "B", 2: "C", 3: "D"}
num = [0, 0]

tiku=loadCSV(csv_file_path)

def main():
    global num

    while True:
        ti = requests.post(
            'http://112.5.88.114:31101/yiban-web/stu/nextSubject.jhtml',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data,
            verify=False,
        )
        if ti.status_code == 200 and ti.json()['isSuccess'] == True:
            sub_descript = aes_ecb_decrypt(ti.json()['data']['nextSubject']['subDescript'], key_base64)
            type = ti.json()['data']['nextSubject']['subType']
            uuid = ti.json()['data']['uuid']
            if type not in ["单选题", "判断题","多选题"]:
                print(f"暂不支持该类型:{type}")
                continue
            flag=False
            for t in tiku:
                if sub_descript ==t[4]:
                    print("查到了")
                    right_ans=t[-1]
                    flag=True
                    break
            if flag==False:
                print("没查到")
                print(sub_descript)
                continue
            ans_data = {
                'answer': right_ans,
                'courseId': courseId,
                'uuid': uuid,
                'deviceUuid': '',
            }

            ans_res = requests.post(
                'http://112.5.88.114:31101/yiban-web/stu/changeSituation.jhtml',
                params=params,
                cookies=cookies,
                headers=headers,
                data=ans_data,
                verify=False,
            )
            if ans_res.status_code == 200 and ans_res.json()['isSuccess'] == True and ans_res.json()[
                'message'] == "回答正确！":
                num[0] += 1
                print(f"答题成功!,答对{num[0]}道")
            else:
                num[1] += 1
                print(f"答题失败!,答错{num[1]}道")


if __name__ == "__main__":

    main()
