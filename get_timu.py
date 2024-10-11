import os

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
courseId = '9'  # 课程id
key_base64 = 'ZDBmMTNiZGI3MDRhMWVhMWE3MTcwNjJiNTk0NzY0ODg'  # SB题库搞NM的加密，如果密钥不变不需要修改
JSESSIONID = ''  # 写你的

def init_csv():
    if 'data' in os.listdir():
        if 'data.csv' in os.listdir('data'):
            print("题库已存在")
            return
    else:
        if not os.path.exists('data'):
            os.mkdir('data')
    print("创建题库")
    with open('data/data.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["courseId", "id","subType","optionCount","subDescript","option0","option1","option2","option3","answer"])

def write_csv(courseId, id, subType,optionCount, subDescript, option0, option1, option2, option3, answer):
    global num
    with open('data/data.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == courseId and row[1] == id:
                return

    with open('data/data.csv', 'a', encoding='utf-8', newline='') as csvfile:
        num+=1
        writer = csv.writer(csvfile)
        writer.writerow([courseId, id, subType,optionCount, subDescript, option0, option1, option2, option3, answer])
        print(f"已经添加:{num}道")


def full2half(text):
    text = re.sub('\s', '', text)
    text = re.sub('[A-Z]\.', '', text)
    text = text.replace('（', '(')
    text = text.replace('）', ')')
    text = text.replace('，', ',')
    text = text.replace('。', '.')

    return text


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
    'Referer': 'http://112.5.88.114:31101/yiban-web/stu/toCombatLoading.jhtml?fightType=1&courseId='+courseId,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
}

params = {
    '_': str(time.time_ns())[:13],
}



AB = {0: "A", 1: "B", 2: "C", 3: "D"}
num = [0, 0]

def main():
    global num
    sub_queue=[]
    get_start = requests.post(
        'http://112.5.88.114:31101/yiban-web/stu/startAnswerByManMachine.jhtml',
        params=params,
        cookies=cookies,
        headers=headers,
        data={'courseId': courseId},
        verify=False,
    )
    # print(get_start.text)
    try:
        status=get_start.json()['isSuccess']
    except Exception as e:
        print("出错了",str(e))
        print(get_start.text)
        return
    roomId = get_start.json()['data']['roomId']
    getSingle = requests.post(
        'http://112.5.88.114:31101/yiban-web/stu/getSinglePersonSituation.jhtml',
        params=params,
        cookies=cookies,
        headers=headers,
        data={'roomId': roomId,'fightType': '1'},
        verify=False,
    )
    nextSub = requests.post(
        'http://112.5.88.114:31101/yiban-web/stu/answerByManMachine.jhtml',
        params=params,
        cookies=cookies,
        headers=headers,
        data={'answer': 'A', 'roomId': roomId, },
        verify=False,
    )
    sub_queue.append(nextSub)
    for i in range(5):
        nextSub = requests.post(
            'http://112.5.88.114:31101/yiban-web/stu/answerByManMachine.jhtml',
            params=params,
            cookies=cookies,
            headers=headers,
            data={'answer': 'A', 'roomId': roomId, },
            verify=False,
        )
        sub_queue.append(nextSub)
        optionCount=sub_queue[0].json()["data"]['subject']['optionCount']

        datas=[sub_queue[0].json()["data"]['subject']["courseId"],
               sub_queue[0].json()["data"]['subject']["id"],
               sub_queue[0].json()["data"]['subject']["subType"],
               sub_queue[0].json()["data"]['subject']["optionCount"],
               sub_queue[0].json()["data"]['subject']["subDescript"]]
        for i in range(int(optionCount)):
            datas.append(sub_queue[0].json()["data"]['subject'][f"option{i}"])
        for j in range(int(optionCount),4):
            datas.append('')
        datas.append(sub_queue[1].json()['data']['subjectCorrect'])

        for i in range(4,5+int(optionCount)):
            datas[i]=aes_ecb_decrypt(datas[i],key_base64)
        write_csv(*datas)
        sub_queue[0]=sub_queue[1]
        sub_queue.pop()




        # time.sleep(1)


if __name__ == "__main__":
    num=0
    init_csv()
    while True:
        main()
