import os
import random
import requests
import warnings
from urllib.parse import urlparse
from process import ReadConfig
from common.utils import Utils
from ParseJs import dealJs


class DownloadJs():

    def __init__(self, jsRealPaths, options):
        # 传入的js文件的路径
        warnings.filterwarnings('ignore')
        self.jsRealPaths = jsRealPaths
        self.blacklist_domains = ReadConfig.ReadConfig().getValue('blacklist', 'domain')[0]
        self.blacklistFilenames = ReadConfig.ReadConfig().getValue('blacklist', 'filename')[0]
        self.options = options
        self.proxy_data = {'http': self.options.proxy,'https': self.options.proxy}
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
                          "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
                          "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"]

    def jsBlacklist(self):
        newList = self.jsRealPaths[:]  # 防止遍历不全
        for jsRealPath in newList:  # 遍历js路径
            res = urlparse(jsRealPath)
            jsRealPathDomain = res.netloc.lower()  # js的主域名
            jsRealPathFilename = Utils().getFilename(jsRealPath).lower()  # 获取js名称
            for blacklistDomain in self.blacklist_domains.split(","):  # 遍历黑名单列表
                if blacklistDomain in jsRealPathDomain:
                    flag = 1
                    break
                else:
                    flag = 0
            if flag:  # 判断js路径中是否存在黑名单
                self.jsRealPaths.remove(jsRealPath)  # 如果有就进行删除
            for blacklistFilename in self.blacklistFilenames.split(","):
                if blacklistFilename in jsRealPathFilename:
                    flag = 1
                    break
                else:
                    flag = 0
            if flag:
                if jsRealPath in self.jsRealPaths:
                    self.jsRealPaths.remove(jsRealPath)
        return self.jsRealPaths

    def downloadJs(self, tag, host, spiltId, jsPaths):  # 下载js文件
        # todo 404的count
        if self.options.cookie is not None:
            header = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cookie': self.options.cookie,
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        else:
            header = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        self.jsRealPaths = list(set(self.jsRealPaths))  # list清单去重
        try:
            self.jsRealPaths = self.jsBlacklist()  # 不能放for循环内
            print(Utils().tellTime() + "js黑名单函数正常")
        except Exception as e:
            print("[Err] %s" % e)
        count = 0
        for jsRealPath in self.jsRealPaths:
            jsFilename = Utils().getFilename(jsRealPath)
            jsTag = Utils().creatTag(6)
            print(Utils().tellTime() + Utils().getMyWord("{downloading}") + jsFilename)
            sslFlag = int(self.options.ssl_flag)
            if sslFlag == 1:
                jsFileResponse = requests.get(url=jsRealPath, headers=header, proxies=self.proxy_data, timeout=30,
                                              verify=False)
            else:
                jsFileResponse = requests.get(url=jsRealPath, proxies=self.proxy_data, timeout=30, headers=header)
            if jsFileResponse.status_code == 404:
                count += 1
            else:
                with open("tmp" + os.sep + tag + "_" + host + os.sep + jsTag + "." + jsFilename, "wb") as js_file:
                    js_file.write(jsFileResponse.content)
                    js_file.close()
            if count > len(jsRealPath) * 0.05:
                modify = input("[!] 当前页面关联js超过5%页面不存在，是否进行baseURL手动调整(Y/N):")
                if modify == 'Y' or modify == 'y':
                    baseUrl = input("[!] 请输入新的BaseURL:")
                    dealJs(jsPaths, baseUrl)

    def creatInsideJs(self, tag, host, jstag, scriptInside):  # 生成html的script的文件
        try:
            jsFilename = "MainPage" + jstag
            jsTag = Utils().creatTag(6)
            print(Utils().tellTime() + Utils().getMyWord("{downloading}") + jsFilename)
            with open("tmp" + os.sep + tag + "_" + host + os.sep + jsTag + "." + jsFilename, "wb") as js_file:
                js_file.write(str.encode(scriptInside))
                js_file.close()
                print(Utils().tellTime() + "主页面js提取完成！")
        except Exception as e:
            print("[Err] %s" % e)
