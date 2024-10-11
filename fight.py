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
csv_file_path = "./qmyz/马克思主义基本原理/question_main.csv"  # 需要替换为实际CSV文题库路径


# def full2half(s):
#     n = ''
#     for char in s:
#         num = ord(char)
#         if num == 0x3000:  #将全角空格转成半角空格
#             num = 32
#         elif 0xFF01 <= num <= 0xFF5E:  #将其余全角字符转成半角字符
#             num -= 0xFEE0
#         num = chr(num)
#         n += num
#
#     return n.replace(' ', '')

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


def load_question_bank(csv_file_path):
    question_bank = {}
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳过第一行标题
        for row in reader:
            question = row[0].strip()
            options = ast.literal_eval(row[1])  # 将字符串列表解析为实际的列表
            correct_answer = ast.literal_eval(row[2])  # 解析正确答案
            question_bank[question] = (options, correct_answer)
    return question_bank


question_bank = load_question_bank(csv_file_path)

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
    nextSub=requests.post(
        'http://112.5.88.114:31101/yiban-web/stu/answerByManMachine.jhtml',
        params=params,
        cookies=cookies,
        headers=headers,
        data={'answer': 'A','roomId': roomId,},
        verify=False,
    )
    for i in range(5):
        sub_descript = full2half(aes_ecb_decrypt(nextSub.json()['data']['subject']['subDescript'], key_base64))
        count = nextSub.json()['data']['subject']['optionCount']
        xuan_xiang = []
        for i in range(count):
            xuan_xiang.append(
                full2half(aes_ecb_decrypt(nextSub.json()['data']['subject']['option' + str(i)], key_base64)))

        flag = False
        if sub_descript in question_bank:
            # print("查到了")
            for i in range(len(xuan_xiang)):
                if full2half(xuan_xiang[i]) == question_bank[sub_descript][1][0]:
                    right_ans = AB[i]
                    flag = True
                    break
        if flag == False:
            # 避免题库出现问题，手动修改
            # print("答案不匹配或找不到")
            right_ans="A"


        nextSub = requests.post(
            'http://112.5.88.114:31101/yiban-web/stu/answerByManMachine.jhtml',
            params=params,
            cookies=cookies,
            headers=headers,
            data={'answer': right_ans, 'roomId': roomId, },
            verify=False,
        )

        try:
            right_ans=nextSub.json()['data']['subjectCorrect']
            # print(right_ans)
        except Exception as e:
            print(nextSub.json())
            return
        # time.sleep(1)

    final = requests.post(
        'http://112.5.88.114:31101/yiban-web/stu/findFightResultByRoomId.jhtml',
        params=params,
        cookies=cookies,
        headers=headers,
        data={'roomId': roomId,},
        verify=False,
    )
    final_list=final.json()["data"]['list']
    for i in final_list:
        if i["studentName"]!="AI":
            print(i["fightResult"])
            # if i["fightResult"]=="失败":
            #     print(i)
            print("积分："+str(i["getIntegral"]))
            num+=i["getIntegral"]
            break


if __name__ == "__main__":
    num=0
    while True:
        main()
        print("获得积分:",num)