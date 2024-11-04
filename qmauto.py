import requests
import csv
import time
import qm_tools
import random
import re

# 请手动填写参数: courseId, url或JESSIONID
courseId = '12'  # 课程id
# 常见courseId如下：
# 形势与政策 15 毛泽东思想和中国特色社会主义理论体系概论 7
# 思想道德与法治 8 马克思主义基本原理 9
# 中国近现代史纲要 10 习近平新时代中国特色社会主义思想概论 12
JESSIONID = ''
url = '' # 主界面(有视频的那个)右上角复制链接获取
# JESSIONID和url选择一个填写即可
csv_file_path = "qmyz/习近平.csv"  # 需要替换为实际CSV文题库路径
# 请手动填写以上参数

# 方法载入
def loadCSV(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)[1:]


def get_cookie_from_url(url):
    res = requests.get(url, headers=headers)
    cookie = re.match(r'JSESSIONID=\w*', res.headers['set-cookie']).group()
    print('获取到cookie: ' + cookie)
    return cookie

# 固定参数
key_base64 = 'ZDBmMTNiZGI3MDRhMWVhMWE3MTcwNjJiNTk0NzY0ODg'  # SB题库搞NM的加密，如果密钥不变不需要修改
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
    'Cookies': 'JESSIONID=' + JESSIONID if JESSIONID != '' else get_cookie_from_url(url),
}

# 请求相关参数
params = {
    '_': str(time.time_ns())[:13],
}

data = {
    'courseId': courseId,
}

AB = {0: "A", 1: "B", 2: "C", 3: "D"}
num = [0, 0]

tiku = loadCSV(csv_file_path)


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
            sub_descript = qm_tools.aes_ecb_decrypt(ti.json()['data']['nextSubject']['subDescript'], key_base64)
            type = ti.json()['data']['nextSubject']['subType']
            uuid = ti.json()['data']['uuid']
            if type not in ["单选题", "判断题", "多选题"]:
                print(f"暂不支持该类型: {type}")
                continue
            elif "刷题" in sub_descript or "请选择" in sub_descript:  # 防刷题题目检测
                print('检测到防刷题题目, 自动跳过')
            flag = False
            for t in tiku:
                if sub_descript == t[4]:
                    print(f"查询到题目: {sub_descript}")
                    right_ans = t[-1]
                    flag = True
                    break
            if not flag:
                print(f"未查询到题目: {sub_descript}")
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
            if ans_res.status_code == 200 and ans_res.json()['isSuccess'] == True and ans_res.json()['message'] == "回答正确！":
                num[0] += 1
                print(f"答题正确, 当前答对{num[0]}道")
            else:
                num[1] += 1
                print(f"答题错误, 当前答错{num[1]}道")
        
        time.sleep(random.randint(4,10)) # 随机休眠，防止被检测



if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"出现异常: {e}")
