import os
import re

from common.cmdline import CommandLines
from common.utils import Utils
from process import ReadConfig


class BaseUrlCollect():

    def __init__(self, projectPath, options):
        self.options = options
        self.projectPath = projectPath
        self.baseUrlRegxs = [r'baseURL\:\"(.*?)\"',
                             r'baseUrl\:\"(.*?)\"',
                             r'url.?\s?\=\s?\"(.*?)\"',
                             r'host\s?\:\s?\"(.*?)\"']
        self.baseUrlPaths = []
        self.apiExts = ReadConfig.ReadConfig().getValue('blacklist', 'apiExts')[0]

    def getBaseurl(self):
        print(Utils().tellTime() + "正在提取BaseURL...")
        baseURL = CommandLines().cmd().baseurl
        if baseURL is None:
            if "/" not in self.baseUrlPaths:
                self.baseUrlPaths.append("/")  # 加入一个默认的
            for i in os.listdir(self.projectPath):
                with open(self.projectPath + i, 'r', encoding='utf-8', errors='ignore') as jsFile:
                    baseUrlStr = jsFile.read()
                    for baseurlRegx in self.baseUrlRegxs:
                        baseurLists = re.findall(baseurlRegx, baseUrlStr)
                        for baseurlPath in baseurLists:
                            if baseurlPath != '' and '/' in baseurlPath and baseurlPath != "/" and len(baseurlPath) > 3:
                                for apiExt in self.apiExts.split(","):
                                    if apiExt not in baseurlPath:
                                        flag = 1
                                    else:
                                        flag = 0
                                        break
                                if flag:
                                    if baseurlPath[0] == "/":
                                        baseurlPath = baseurlPath[1:]
                                    if "?" in baseurlPath:
                                        baseurlPath = baseurlPath.split("?")[0]
                                        self.baseUrlPaths.append(baseurlPath)
                                    else:
                                        self.baseUrlPaths.append(baseurlPath)
                    jsFile.close()
        else:
            baseURLs = baseURL.split(',')
            self.baseUrlPaths = baseURLs
        self.baseUrlPaths = list(set(self.baseUrlPaths))
        with open(self.projectPath + 'BaseURLResult.txt', 'a') as resultFile:
            for baseURL in self.baseUrlPaths:
                if baseURL[0] != '/' and baseURL[0:4] != 'http':
                    baseURL = '/' + baseURL
                print(baseURL, file=resultFile)
            resultFile.close()
            print(Utils().tellTime() + "BaseURL提取完毕！")