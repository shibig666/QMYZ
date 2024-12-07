import qm_utils
import os

url = input("请输入登录URL: ")
cookie = qm_utils.qm_tools.get_cookie_from_url(url)
courses = qm_utils.qm_tools.get_courses(cookie)
print("课程列表:")
for k, v in courses.items():
    print(f"{k}: {v}")
course = input("请输入课程id: ")
num = int(input("请输入答题量(0为无限): "))
csv_list = os.listdir("qmyz")
if "{}.csv".format(course) not in csv_list:
    print("题库不存在")
    exit(1)
ti = qm_utils.qm.qm_tiku("qmyz/{}.csv".format(course))
qm = qm_utils.qm.qm_auto(url, ti.tiku, course, cookie)
qm.auto_do(num)
