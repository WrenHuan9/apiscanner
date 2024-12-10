import os
import sys

from urllib.parse import urlparse

from process import GlobelSearch, DeleteCache
from process.BaseUrlCollect import BaseUrlCollect
from process.CheckPacker import CheckPacker
from process.FrontendUnauth import FrontendUnauth
from process.ParseJs import ParseJs
from process.ApiCollect import ApiCollect
from process.FrontRouteCollect import FrontRouteCollect
from process.ApiUnauth import ApiUnauth
from process import ReadConfig
from process.Recoverspilt import RecoverSpilt
from common.utils import Utils

class Project():

    def __init__(self, url, options):
        self.url = url
        self.codes = {}
        self.options = options
        self.projectTag = Utils().creatTag(6)

    def parseStartWithSimpleMode(self):
        res = urlparse(self.url)
        domain = res.netloc
        if ":" in domain:
            domain = str(domain).replace(":", "_")
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        projectPath = "tmp" + os.sep + self.projectTag + "_" + domain
        os.mkdir(projectPath)
        projectPath = projectPath + os.sep
        print("[!] " + Utils().getMyWord("{project_path}") + os.path.abspath(projectPath))
        # 下载js
        jsPaths = ParseJs(self.projectTag, self.url, self.options).parseJsStart()
        tmpJsPath = []
        for jsPath in jsPaths:
            if '/js' in jsPath or '/script' in jsPath:
                tmpJsPath = str(jsPath).split("/")
        if not tmpJsPath:
            print("读取js路径失败，使用默认路径尝试")
            tmpJsPath = str(jsPaths[0]).split("/")
        jsBaseURL = res.scheme + "://" + res.netloc +"/" + "/".join(tmpJsPath[:-1])
        # 打包器检测 + 动态提取
        checkResult = CheckPacker(self.projectTag, self.url, self.options).checkStart(os.path.abspath(projectPath))
        if checkResult == 1 or checkResult == 777:
            if len(jsPaths) > 0:
                if checkResult != 777:
                    print("[!] " + Utils().getMyWord("{check_pack_s}"))
                RecoverSpilt(self.projectTag, jsBaseURL, self.options).recoverStart(os.path.abspath(projectPath))
        else:
            print("[!] " + Utils().getMyWord("{check_pack_f}"))
        # 提取baseURL（点击脚本？）
        BaseUrlCollect(projectPath, self.options).getBaseurl()
        # 提取前端路由
        FrontRouteCollect(projectPath, self.options).pathCollect()
        # 提取后端api
        ApiCollect(projectPath, self.options).apiCollect(None)
        # 尝试前端未授权
        FrontendUnauth(projectPath, self.options).routeComplete(self.url)
        # api请求尝试（双方法+请求体都在这一步调整）
        ApiUnauth(projectPath, self.options).apiComplete(self.url)
        # 敏感词检索
        self.keyWordsSearch(projectPath, jsBaseURL)
        # 保存本次扫描的参数配置
        with open(projectPath + 'project.ini', 'a', encoding='utf-8', errors='ignore') as configFile:
            print('[configuration]', file=configFile)
            print('url=' + self.url, file=configFile)
            print('ssl=' + self.options.ssl_flag, file=configFile)
            print('proxy=' + self.options.proxy, file=configFile)
            configFile.close()


    def parseStartWithCustomMode(self):
        # 自定义一定要指定工作目录
        if self.options.path is not None:
            projectPath = 'tmp/' + self.options.path + os.sep
            if os.path.exists(projectPath):
                self.url = ReadConfig.ReadConfig().getCustomValue(projectPath + 'project.ini', 'configuration', 'url')[0]
                self.options.ssl_flag = ReadConfig.ReadConfig().getCustomValue(projectPath + 'project.ini', 'configuration', 'ssl')[0]
                self.options.proxy = ReadConfig.ReadConfig().getCustomValue(projectPath + 'project.ini', 'configuration', 'proxy')[0]
                # 前端重放
                if self.options.onlyfront == 'on':
                    if self.options.routehost is not None:
                        baseRoutes = str(self.options.routehost).split(",")
                        for baseRoute in baseRoutes:
                            FrontendUnauth(projectPath, self.options).routeComplete(baseRoute)
                    else:
                        print("请以 --rh 或 --routehost 添加指定前端路由baseURL")
                        sys.exit(0)
                if self.options.particularContent != 'off':
                    ApiCollect(projectPath, self.options).apiCollect(self.options.particularContent)
                    if self.options.onlyback == 'on':
                        ApiUnauth(projectPath, self.options).apiComplete(self.url)
                    else:
                        print("系统检测到您提交了指定的识别文本，是否要使用更新后的提取结果进行API重放尝试？Y/N")
                        choice = input(">")
                        if choice == 'Y' or choice == 'y' or choice == '1':
                            ApiUnauth(projectPath, self.options).apiComplete(self.url)
                        else:
                            print("识别完成，请至" + projectPath + 'result.txt检查新增内容')
                            sys.exit(0)
                if self.options.onlyback == 'on':
                    ApiUnauth(projectPath, self.options).apiComplete(self.url)
                if self.options.keywords is not None:
                    self.keyWordsSearch(projectPath, projectPath)
            else:
                print("工作目录不存在，请检查后重新输入！")
                sys.exit(0)
        else:
            print("未指定工作目录，请以 --pa 或 --path 添加指定工作目录")
            sys.exit(0)

    def keyWordsSearch(self, projectPath, jsBaseURL):
        # 敏感词检索，直接提取存在的用户名密码
        GlobelSearch.search(projectPath, self.options.keywords, jsBaseURL)
        if self.options.cache == 'off':
            DeleteCache.delete(projectPath)

    def run(self):
        if self.options.mode == 'simple':
            self.parseStartWithSimpleMode()
        else:
            self.parseStartWithCustomMode()
