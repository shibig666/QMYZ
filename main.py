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
man = False  # 是否启用手动答题？
debug = True  # 启用调试
thead = False  # 启用多线程：需要关闭手动答题
thead_n = 8  # 线程数


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
            sub_descript = full2half(aes_ecb_decrypt(ti.json()['data']['nextSubject']['subDescript'], key_base64))
            type = ti.json()['data']['nextSubject']['subType']
            uuid = ti.json()['data']['uuid']
            if type not in ["单选题", "判断题"]:
                if debug:
                    print(f"暂不支持该类型:{type}")
                continue
            count = ti.json()['data']['nextSubject']['optionCount']
            xuan_xiang = []
            for i in range(count):
                try:
                    xuan_xiang.append(
                        full2half(aes_ecb_decrypt(ti.json()['data']['nextSubject']['option' + str(i)], key_base64)))
                except Exception as e:
                    print(e)

            if sub_descript in question_bank:
                print("查到了")
                flag = False
                for i in range(len(xuan_xiang)):
                    if full2half(xuan_xiang[i]) == question_bank[sub_descript][1][0]:
                        right_ans = AB[i]
                        flag = True
                        break
                if flag == False:
                    # 避免题库出现问题，手动修改
                    print("答案不匹配")
                    if man:
                        print(f"答案:{question_bank[sub_descript][1][0]}")
                        print(f"原选项:")
                        for i in range(len(xuan_xiang)):
                            print(f"{AB[i]}:{xuan_xiang[i]}")
                        right_ans = input("手动输入答案")
                    else:
                        continue
            else:
                if man:
                    print("没查到,尝试调用接口")
                    print(f"题目：{sub_descript}")
                    print(f"原选项:")
                    for i in range(len(xuan_xiang)):
                        print(f"{AB[i]}:{xuan_xiang[i]}")
                    api_ans = api.search(sub_descript)
                    while api_ans == False:
                        print("API冷却中")
                        time.sleep(3)
                    print("查询答案:")
                    print(api_ans)
                    right_ans = input("手动输入答案")
                else:
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
    if thead and man == False:
        for i in range(thead_n):
            threading.Thread(target=main).start()
    else:
        main()
