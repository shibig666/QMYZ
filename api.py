import requests

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://mooc1.chaoxing.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
}

json_data = {
    'plat': None,
    'qid': None,
    'question': '',
    'options': [],
    'options_id': [],
}

def search(q):
    json_data['question'] = q
    response = requests.post('https://lyck6.cn/scriptService/api/autoFreeAnswer', headers=headers, json=json_data)
    if response.status_code == 200 and "error_msg" not in response.text:
        return response.json()['result']['answers']
    else:
        print(response.json()["error_msg"])
        return False