import requests
import csv
import time
import qm_utils.qm_tools as qm_tools
import random
import re


class qm_tiku:
    def __init__(self, csv_file_path):
        self.tiku = self.loadCSV(csv_file_path)
        self.num = [0, 0]

    def loadCSV(self, csv_file_path):
        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            tiku = list(reader)
        return tiku


class qm_auto:
    def __init__(self, url, tiku, courseId, JSESSIONID="", accuracy=100):
        self.url = url
        self.tiku = tiku
        self.JSESSIONID = JSESSIONID
        self.key_base64 = "ZDBmMTNiZGI3MDRhMWVhMWE3MTcwNjJiNTk0NzY0ODg"
        self.courseId = courseId
        self.accuracy = accuracy
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://112.5.88.114:31101",
            "Pragma": "no-cache",
            "Referer": "http://112.5.88.114:31101/yiban-web/stu/toSubject.jhtml?courseId="
            + self.courseId,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.cookies = {
            "JSESSIONID": (
                self.JSESSIONID if self.JSESSIONID != "" else self.get_cookie_from_url()
            ),
        }
        self.params = {
            "_": str(time.time_ns())[:13],
        }
        self.data = {
            "courseId": self.courseId,
        }

        self.AB = {0: "A", 1: "B", 2: "C", 3: "D"}
        self.num = [0, 0]

    def calculate_accuracy(self):
        if self.num[0] + self.num[1] == 0:
            return 0
        else:
            return self.num[0] / (self.num[0] + self.num[1]) * 100

    def judge_request(self, res):
        if res.status_code != 200:
            print("请求失败，状态码为：" + str(res.status_code))
            return False
        else:
            return True

    def get_cookie_from_url(self):
        res = requests.get(self.url)
        cookie = re.match(r"JSESSIONID=\w*", res.headers["set-cookie"]).group()
        cookie = cookie[len("JSESSIONID=") :]
        print("获取到cookie: " + cookie)
        self.JSESSIONID = cookie
        return cookie

    def do(self):
        ti = requests.post(
            "http://112.5.88.114:31101/yiban-web/stu/nextSubject.jhtml",
            params=self.params,
            cookies=self.cookies,
            headers=self.headers,
            data=self.data,
            verify=False,
        )
        if not self.judge_request(ti):
            return False
        sub_descript = qm_tools.aes_ecb_decrypt(
            ti.json()["data"]["nextSubject"]["subDescript"], self.key_base64
        )
        type = ti.json()["data"]["nextSubject"]["subType"]
        uuid = ti.json()["data"]["uuid"]
        if type not in ["单选题", "判断题", "多选题"]:
            print(f"暂不支持该类型: {type}")
            return False
        elif "刷题" in sub_descript or "请选择" in sub_descript:  # 防刷题题目检测
            print("检测到防刷题题目, 自动跳过")
            return False
        flag = False
        for t in self.tiku:
            if sub_descript == t[4]:
                print(f"查询到题目: {sub_descript}")
                flag = True
                if self.calculate_accuracy() > self.accuracy:
                    print(f"超过准确度要求{self.accuracy}%")
                    right_ans = (
                        self.AB[random.randint(0, 1)]
                        if type == "判断题"
                        else self.AB[random.randint(0, 3)]
                    )
                else:
                    right_ans = t[-1]
                break
        if not flag:
            print(f"未查询到题目: {sub_descript}")
            if self.calculate_accuracy() > self.accuracy:
                print(f"超过准确度要求{self.accuracy}%")
                right_ans = (
                    self.AB[random.randint(0, 1)]
                    if type == "判断题"
                    else self.AB[random.randint(0, 3)]
                )
            else:
                return False
        ans_data = {
            "answer": right_ans,
            "courseId": self.courseId,
            "uuid": uuid,
            "deviceUuid": "",
        }
        ans_res = requests.post(
            "http://112.5.88.114:31101/yiban-web/stu/changeSituation.jhtml",
            params=self.params,
            cookies=self.cookies,
            headers=self.headers,
            data=ans_data,
            verify=False,
        )
        if not self.judge_request(ans_res):
            return False
        if (
            ans_res.status_code == 200
            and ans_res.json()["isSuccess"] == True
            and ans_res.json()["message"] == "回答正确！"
        ):
            self.num[0] += 1
            print(
                f"答题正确, 当前答对{self.num[0]}道，准确率为{self.calculate_accuracy()}",
            )

        else:
            self.num[1] += 1
            print(
                f"答题错误, 当前答错{self.num[1]}道，准确率为{self.calculate_accuracy()}"
            )
        return True

    def auto_do(self, num):
        assert type(num) == int
        if num <= 0:
            while True:
                time.sleep(random.randint(3, 6))
                self.do()
        else:
            for i in range(num):
                time.sleep(random.randint(3, 6))
                self.do()
