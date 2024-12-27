import re
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import requests


# def full2half(text):
#     text = re.sub("\s", "", text)
#     text = re.sub("[A-Z]\.", "", text)
#     text = text.replace("（", "(")
#     text = text.replace("）", ")")
#     text = text.replace("，", ",")
#     text = text.replace("。", ".")
#     return text


def fix_base64_padding(b64_string):
    return b64_string + "=" * (-len(b64_string) % 4)


# AES ECB 解密函数
def aes_ecb_decrypt(ciphertext_base64, key_base64):
    ciphertext_base64 = fix_base64_padding(ciphertext_base64)
    key_base64 = fix_base64_padding(key_base64)
    ciphertext = base64.b64decode(ciphertext_base64)
    key = base64.b64decode(key_base64)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_data.decode("utf-8")


def get_cookie_from_url(url):
    res = requests.get(url)
    cookie = re.match(r"JSESSIONID=\w*", res.headers["set-cookie"]).group()
    cookie = cookie[len("JSESSIONID=") :]
    return cookie


def get_courses(JSESSIONID):
    cookies = {
        "JSESSIONID": JSESSIONID,
    }

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Referer": "http://112.5.88.114:31101/yiban-web/stu/homePage.jhtml",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    response = requests.get(
        "http://112.5.88.114:31101/yiban-web/stu/toCourse.jhtml",
        cookies=cookies,
        headers=headers,
        verify=False,
    )
    pattern = r'href="toSubject\.jhtml\?courseId=(\d+)".*?<div class="mui-media-body".*?>(.*?)</div>'
    matches = re.findall(pattern, response.text, re.DOTALL)
    course_dict = {course_id: course_name.strip() for course_id, course_name in matches}
    return course_dict
