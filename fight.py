import os
import requests
import re
import csv
import time
import json
import qm_tools
# 请填写以下参数
courseId = '10 '  # 课程id
key_base64 = 'ZDBmMTNiZGI3MDRhMWVhMWE3MTcwNjJiNTk0NzY0ODg'  # SB题库搞NM的加密，如果密钥不变不需要修改
JSESSIONID = ''  # 写你的
csv_file_path = "./data/近代史.csv"  # 需要替换为实际CSV文题库路径

timu=[]
def loadCSV(csv_file_path):
    if not os.path.exists(csv_file_path):
        print("新建题库")
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["courseId", "id", "subType", "optionCount", "subDescript", "option0", "option1", "option2",
                 "option3",
                 "answer"])
    with open(csv_file_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)[1:]


def write_csv(courseId, id, subType, optionCount, subDescript, option0, option1, option2, option3, answer,csv_file_path):
    global tiku
    with open(csv_file_path, 'a', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([courseId, id, subType, optionCount, subDescript, option0, option1, option2, option3, answer])
        print(f"添加新题目")
    tiku=loadCSV(csv_file_path)


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
    'Referer': 'http://112.5.88.114:31101/yiban-web/stu/toCombatLoading.jhtml?fightType=1&courseId=' + courseId,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
}

params = {
    '_': str(time.time_ns())[:13],
}


def main():
    global num
    global tiku
    get_start = requests.post(
        'http://112.5.88.114:31101/yiban-web/stu/startAnswerByManMachine.jhtml',
        params=params,
        cookies=cookies,
        headers=headers,
        data={'courseId': courseId},
        verify=False,
    )
    try:
        status = get_start.json()['isSuccess']
    except Exception as e:
        print("出错了", str(e))
        print(get_start.text)
        return
    roomId = get_start.json()['data']['roomId']



    ansFlag=False
    lastSub=None
    start = requests.get(
        'http://112.5.88.114:31101/yiban-web/stu/toAnswer.jhtml',
        params={'roomId': roomId,'fightType': '1',},
        cookies=cookies,
        headers=headers,
        verify=False,
    )
    start_sub=json.loads(re.findall(r'{"courseId":.*}',start.text)[0])  # 获取html中的题目
    flag=False
    ans="A"
    for l in tiku:
        if str(start_sub['subjectId']) == l[1] and str(
                start_sub["courseId"]) == l[0]:
            print("开始找到了")
            ans = l[-1]
            flag = True
            ansFlag=False
            break
    if flag == False:
        print("开始找不到")
        ansFlag=True
        lastSub=start_sub


    for i in range(5):
        nextSub = requests.post(
            'http://112.5.88.114:31101/yiban-web/stu/answerByManMachine.jhtml',
            params=params,
            cookies=cookies,
            headers=headers,
            data={'answer': ans, 'roomId': roomId, },
            verify=False,
        )

        # 新增题目
        if ansFlag:
            optionCount = lastSub['optionCount']
            if "subjectId" in lastSub:
                datas = [lastSub["courseId"],
                         lastSub["subjectId"],
                         lastSub["subType"],
                         lastSub["optionCount"],
                         lastSub["subDescript"]]
            else:
                datas = [lastSub["courseId"],
                         lastSub["id"],
                         lastSub["subType"],
                         lastSub["optionCount"],
                         lastSub["subDescript"]]
            for i in range(int(optionCount)):
                datas.append(lastSub[f"option{i}"])
            for j in range(int(optionCount), 4):
                datas.append('')
            datas.append(nextSub.json()['data']['subjectCorrect'])
            datas.append(csv_file_path)

            for i in range(4, 5 + int(optionCount)):
                datas[i] = qm_tools.aes_ecb_decrypt(datas[i], key_base64)
            try:
                write_csv(*datas)
            except:
                print("存在不兼容题目")

        ans = "A"
        flag=False
        for l in tiku:
            if str(nextSub.json()['data']['subject']["id"])==l[1] and str(nextSub.json()['data']['subject']["courseId"])==l[0]:
                print("找到了")
                ans=l[-1]
                flag=True
                ansFlag=False
                break

        if flag==False:
            print("找不到")
            ansFlag=True
            lastSub=nextSub.json()['data']['subject']

        # time.sleep(0.1)

    requests.post(
        'http://112.5.88.114:31101/yiban-web/stu/answerByManMachine.jhtml',
        params=params,
        cookies=cookies,
        headers=headers,
        data={'answer': ans, 'roomId': roomId, },
        verify=False,
    )


    final = requests.post(
        'http://112.5.88.114:31101/yiban-web/stu/findFightResultByRoomId.jhtml',
        params=params,
        cookies=cookies,
        headers=headers,
        data={'roomId': roomId, },
        verify=False,
    )
    final_list = final.json()["data"]['list']
    for i in final_list:
        if i["studentName"] != "AI":
            print(i["fightResult"])
            print("积分：" + str(i["getIntegral"]))
            num += i["getIntegral"]
            break



if __name__ == "__main__":
    num=0
    tiku = loadCSV(csv_file_path)
    while True:
        try:
            main()
        except Exception as e:
            print("出现异常")
            print(e)