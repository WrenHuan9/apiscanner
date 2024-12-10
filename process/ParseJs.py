import re
import requests
import warnings
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from process.DownloadJs import DownloadJs
from common.utils import Utils


class ParseJs():

    def __init__(self, projectTag, url, options):
        warnings.filterwarnings('ignore')
        self.url = url
        self.jsPaths = []
        self.jsRealPaths = []
        self.jsPathList = []
        self.projectTag = projectTag
        self.options = options
        self.proxy_data = {'http': self.options.proxy, 'https': self.options.proxy}
        if self.options.cookie is not None:
            self.header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
                "Cookie": options.cookie,
                self.options.head.split(':')[0]: self.options.head.split(':')[1],
                }
        else:
            self.header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }

    def requestUrl(self):
        headers = self.header
        url = self.url
        print(Utils().tellTime() + "目标站点：" + url)
        print(Utils().tellTime() + "正在解析网页中...")
        sslFlag = int(self.options.ssl_flag)
        if sslFlag == 1:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data, timeout=30, verify=False).text
        else:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data, timeout=30).text
        demo = demo.replace("<!--", "").replace("-->", "")
        soup = BeautifulSoup(demo, "html.parser")
        # 主页面js提取
        for item in soup.find_all("script"):
            jsPath = item.get("src")
            if jsPath:
                self.jsPaths.append(jsPath)
        # 防止使用link标签情况
        for item in soup.find_all("link"):
            jsPath = item.get("href")
            try:
                if jsPath[-2:] == "js":  # 防止提取css
                    self.jsPaths.append(jsPath)
            except:
                pass
        try:
            jsInScript = self.scriptCrawling(demo)
            print(Utils().tellTime() + "scriptCrawling模块正常")
            for jsPath in jsInScript:
                self.jsPaths.append(jsPath)
        except Exception as e:
            print("[Err] %s" % e)
        try:
            self.dealJs(self.jsPaths)
            print(Utils().tellTime() + "dealjs函数正常")
        except Exception as e:
            print("[Err] %s" % e)

    def dealJs(self, js_paths):  # 生成js绝对路径
        # todo 这段有问题
        res = urlparse(self.url)  # 处理url多余部分
        if res.path == "":
            baseUrl = res.scheme + "://" + res.netloc + "/"
        else:
            baseUrl = res.scheme + "://" + res.netloc + res.path
            if res.path[-1:] != "/":  # 文件夹没"/",若输入的是文件也会被加上，但是影响不大
                baseUrl = baseUrl + "/"
        if self.url[-1:] != "/":  # 有文件的url
            tmpPath = res.path.split('/')
            tmpPath = tmpPath[:]  # 防止解析报错
            del tmpPath[-1]
            baseUrl = res.scheme + "://" + res.netloc + "/".join(tmpPath) + "/"
        for jsPath in js_paths:  # 路径处理多种情况./ ../ / http
            if jsPath[:2] == "./":
                jsPath = jsPath.replace("./", "")
                jsRealPath = baseUrl + jsPath
                self.jsRealPaths.append(jsRealPath)
            elif jsPath[:3] == "../":
                tmpPath = res.path.split('/')
                if res.path[-1] != "/":
                    tmpPath = res.path + "/"
                    tmpPath = tmpPath.split('/')
                new_tmpPath = tmpPath[:]  # 防止解析报错
                dirCount = jsPath.count('../') + 1
                tmpCount = 1
                jsPath = jsPath.replace("../", "")
                while tmpCount <= dirCount:
                    del new_tmpPath[-1]
                    tmpCount = tmpCount + 1
                baseUrl = res.scheme + "://" + res.netloc + "/".join(new_tmpPath) + "/"
                jsRealPath = baseUrl + jsPath
                self.jsRealPaths.append(jsRealPath)
            elif jsPath[:2] == "//":  # 自适应域名js
                jsRealPath = res.scheme + ":" + jsPath
                self.jsRealPaths.append(jsRealPath)
            elif jsPath[:1] == "/":
                jsRealPath = res.scheme + "://" + res.netloc + jsPath
                self.jsRealPaths.append(jsRealPath)
            elif jsPath[:4] == "http":
                jsRealPath = jsPath
                self.jsRealPaths.append(jsRealPath)
            else:
                jsRealPath = baseUrl + jsPath
                self.jsRealPaths.append(jsRealPath)
        print(Utils().tellTime() + Utils().getMyWord("{pares_js_fini_1}") + str(len(self.jsRealPaths)) + Utils().getMyWord("{pares_js_fini_2}"))
        domain = res.netloc
        if ":" in domain:
            domain = str(domain).replace(":", "_")
        DownloadJs(self.jsRealPaths, self.options).downloadJs(self.projectTag, domain, 0)

    def scriptCrawling(self, demo):
        res = urlparse(self.url)
        domain = res.netloc
        if ":" in domain:
            domain = str(domain).replace(":", "_")
        scriptInside = ""
        soup = BeautifulSoup(demo, "html.parser")
        for item in soup.find_all("script"):
            scriptString = str(item.string)  # 防止特殊情况报错
            listSrc = re.findall(r'src=\"(.*?)\.js', scriptString)
            if not listSrc == []:
                for jsPath in listSrc:
                    self.jsPathList.append(jsPath)
            if scriptString != "None":  # None被转成字符串了
                scriptInside = scriptInside + scriptString
        if scriptInside != "":
            DownloadJs(self.jsRealPaths, self.options).creatInsideJs(self.projectTag, domain, Utils().creatTag(6), scriptInside)
        return self.jsPathList

    def parseJsStart(self):
        self.requestUrl()
        return self.jsPaths