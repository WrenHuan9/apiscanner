import os
import re
from process import ReadConfig
from common.utils import Utils


class ApiCollect():

    def __init__(self, projectPath, options):
        self.options = options
        self.projectPath = projectPath
        self.regxs = [r'\w\.get\(\"(.*?)\"\,',
                      r'\w\.post\(\"(.*?)\"\,',
                      r'\w\.post\(\"(.*?)\"',
                      r'\w\.get\(\"(.*?)\"',
                      r'\w\+\"(.*?)\"\,',
                      r'url\:\"(.*?)\"',
                      r'url\:\w+\"(.*?)\"',
                      r'\"http:\/\/(.*?)\"',
                      r'\"https:\/\/(.*?)\"',
                      r'return\s.*?\[\".\"\]\.post\(\"(.*?)\"',
                      r'return\s.*?\[\".\"\]\.get\(\"(.*?)\"']
        self.chineseRegx = r'[\u4e00-\u9fa5]'
        self.apiPaths = []
        self.apiExts = ReadConfig.ReadConfig().getValue('blacklist', 'apiExts')[0]
        self.typeExt = ReadConfig.ReadConfig().getValue('blacklist', 'resultExts')[0]

    def apiCollect(self, path):
        # 默认 append 模式
        if self.options.regex is not None:
            for reg in self.options.regex.split(','):
                self.regxs.append(reg)
        print(Utils().tellTime() + "正在提取后端API接口...")
        if path != None:
            length = self.execute(path)
            print(Utils().tellTime() + '指定文件提取完毕, 该文件共提取到' + str(length) + '条API')
        else:
            for i in os.listdir(self.projectPath):
                jsPath = self.projectPath + i
                flag = 0
                for typeExt in self.typeExt.split(","):
                    if typeExt in jsPath:
                        flag = 1
                if flag != 1:
                    length = self.execute(jsPath)
                    num = len(self.apiPaths) - length
                    print(Utils().tellTime() + 'js文件:' + i + '提取完毕, 该文件共提取到' + str(num) + '条API')
        # api提取完毕后进行去重排序，做一些预处理
        self.apiPaths = list(set(self.apiPaths))
        self.apiPaths.sort()
        with open(self.projectPath + 'result.txt', 'a', encoding='utf-8') as resultFile:
            if path != None:
                print("=========================" + Utils().tellTime() + "   自定义文本提取内容  =========================", file=resultFile)
            for api in self.apiPaths:
                # 去除可能无意义的短链接
                if len(api) < 3:
                    continue
                # 去除中文
                if len(re.findall(self.chineseRegx, api)) > 0:
                    continue
                if '<' in api or '[' in api or ']' in api or '@' in api or '|' in api:
                    continue
                if api[0] != '/':
                    if '://' in api:
                        # 带协议头的三方链接直接跳过
                        continue
                    elif '/' in api:
                        # 不以 / 开头但为路径格式的字符串添加/开头
                        api = '/' + api
                print(api, file=resultFile)
            resultFile.close()
            print(Utils().tellTime() + "后端API接口提取完毕！")

    def execute(self, jsPath):
        length = len(self.apiPaths)
        with open(jsPath, 'r', encoding='utf-8', errors='ignore') as jsFile:
            apiStr = jsFile.read()
            for regx in self.regxs:
                apiLists = re.findall(regx, apiStr)
                for apiPath in apiLists:
                    if apiPath != '' and '/' in apiPath:
                        for apiExt in self.apiExts.split(","):
                            if apiExt not in apiPath:
                                flag = 1
                            else:
                                flag = 0
                                break
                        if flag:
                            if "?" in apiPath:
                                apiPath = apiPath.split("?")[0]
                                self.punctuationRemoval(apiPath)
                                if regx == r'\"http:\/\/(.*?)\"':
                                    apiPath = 'http://' + apiPath
                                elif regx == r'\"https:\/\/(.*?)\"':
                                    apiPath = 'https://' + apiPath
                                self.apiPaths.append(apiPath)
                            else:
                                self.punctuationRemoval(apiPath)
                                if regx == r'\"http:\/\/(.*?)\"':
                                    apiPath = 'http://' + apiPath
                                elif regx == r'\"https:\/\/(.*?)\"':
                                    apiPath = 'https://' + apiPath
                                self.apiPaths.append(apiPath)
                        else:
                            try:
                                self.apiTwiceCollect(apiPath)
                            except Exception as e:
                                print("[Err] %s" % e)
            jsFile.close()
        return length

    def apiTwiceCollect(self, api_str):
        for regx in self.regxs:
            apiLists = re.findall(regx, api_str)
            for apiPath in apiLists:
                if apiPath != '' and '/' in apiPath:
                    for api_ext in self.apiExts.split(","):
                        if api_ext not in apiPath:
                            flag = 1
                        else:
                            flag = 0
                            break
                    if flag:
                        self.punctuationRemoval(apiPath)
                        self.apiPaths.append(apiPath)

    def punctuationRemoval(self, apiPath):
        for i in '{}\",()+;':
            apiPath = apiPath.replace(i, "")