from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from time import sleep

import random
import requests
import urllib3
from tqdm import trange


class BatchRequest(object):
    def __init__(self, projectPath, options, urls):
        self.UserAgent = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
                          "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
                          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                          "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
                          "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
                          "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
                          "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
                          "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",
                          "Opera/9.80 (Windows NT 6.1; U; en) Praesto/2.8.131 Version/11.11",
                          "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"]
        self.codes = []
        self.url = []
        self.urls = urls
        self.res = []
        self.options = options
        self.projectPath = projectPath
        self.proxy_data = {'http': self.options.proxy, 'https': self.options.proxy}

    def checkGet(self, url):
        self.doRequest(0, url, 'url')

    def checkPost(self, url):
        self.doRequest(1, url, 'url')
        self.doRequest(1, url, 'json')

    def doRequest(self, reqType, url, encode):
        urllib3.disable_warnings()  # 禁止跳出来对warning
        contenttype = 'application/x-www-form-urlencoded'
        if encode == 'json':
            contenttype = 'application/json'
        if self.options.cookie is not None:
            headers = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': contenttype,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cookie': self.options.cookie,
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        else:
            headers = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': contenttype,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        sslFlag = int(self.options.ssl_flag)
        try:
            if reqType == 0:
                s = requests.Session()
                s.keep_alive = False
                if sslFlag == 1:
                    res = s.get(url, headers=headers, timeout=6, proxies=self.proxy_data, verify=False)
                else:
                    res = s.get(url, headers=headers, timeout=6, proxies=self.proxy_data)
            else:
                data = "a=1"
                if encode == 'json':
                    data = '{"a": "1"}'
                if sslFlag == 1:
                    res = requests.post(url, headers=headers, timeout=6, data=data, proxies=self.proxy_data,verify=False)
                else:
                    res = requests.post(url, headers=headers, timeout=6, data=data, proxies=self.proxy_data)
            code = str(res.status_code)
            size = str(res.headers.get('Content-Length'))
            self.res.append(url + "   " + code + "   " + size)
        except Exception as e:
            print("[Err] %s" % e)

    def run(self, reqType, logName):
        # 0 - GET, 1 - POST
        nums = len(self.urls)
        for _ in trange(nums):
            sleep(0.01)
        pool = ThreadPoolExecutor(20)
        if reqType == 1:
            allTask = [pool.submit(self.checkPost, url) for url in self.urls]
        else:
            allTask = [pool.submit(self.checkGet, url) for url in self.urls]
        wait(allTask, return_when=ALL_COMPLETED)
        with open(self.projectPath + logName, 'a', encoding='utf-8') as log:
            for result in self.res:
                print(result, file=log)
            log.close()