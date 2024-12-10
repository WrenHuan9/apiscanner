from urllib.parse import urlparse

import node_vm2
import os
import re

from process.DownloadJs import DownloadJs
from common.utils import Utils


class RecoverSpilt():

    def __init__(self, projectTag, jsBaseURL, options):
        self.name_list = []
        self.jsBaseURL = jsBaseURL
        self.remotePaths = []
        self.jsFileNames = []
        self.localFileNames = []
        self.remoteFileURLs = []
        self.js_compile_results = []
        self.projectTag = projectTag
        self.options = options

    def jsCodeCompile(self, jsCode, jsFilePath):
        try:
            print(Utils().tellTime() + Utils().getMyWord("{get_codesplit}"))
            variable = re.findall(r'\[.*?\]', jsCode)
            if "[" and "]" in variable[0]:
                variable = variable[0].replace("[", "").replace("]", "")
            jsCodeFunc = "function js_compile(%s){js_url=" % (variable) + jsCode + "\nreturn js_url}"
            pattern_jscode = re.compile(r"\(\{\}\[(.*?)\]\|\|.\)", re.DOTALL)
            flag_code = pattern_jscode.findall(jsCodeFunc)
            if flag_code:
                jsCodeFunc = jsCodeFunc.replace("({}[%s]||%s)" % (flag_code[0], flag_code[0]), flag_code[0])
            pattern1 = re.compile(r"\{(.*?)\:")
            pattern2 = re.compile(r"\,(.*?)\:")
            nameList1 = pattern1.findall(jsCode)
            nameList2 = pattern2.findall(jsCode)
            nameList = nameList1 + nameList2
            nameList = list(set(nameList))
            jsUrlPath = self.jsBaseURL
            with node_vm2.VM() as vm:
                vm.run(jsCodeFunc)
                for name in nameList:
                    if "\"" in name:
                        name = name.replace("\"", "")
                    if "undefined" not in vm.call("js_compile", name):
                        jsFileName = vm.call("js_compile", name)
                        self.jsFileNames.append(jsFileName)
            print(Utils().tellTime() + Utils().getMyWord("{run_codesplit_s}") + str(len(self.jsFileNames)))
            print(jsUrlPath)
            for jsPath1 in self.jsFileNames:
                print(jsPath1)
            self.getRealFilePath(self.jsFileNames, jsUrlPath)
            print(Utils().tellTime() + "jscodecomplie模块正常")
        except Exception as e:
            print("[Err] %s" % e)  # 这块有问题，逻辑要改进
            return 0

    def checkCodeSpilting(self, jsFilePath):
        jsOpen = open(jsFilePath, 'r', encoding='UTF-8', errors="ignore")  # 防编码报错
        jsFile = jsOpen.readlines()
        jsOpen.close()
        jsFile = str(jsFile)  # 二次转换防报错
        if "document.createElement(\"script\");" in jsFile:
            print(
                Utils().tellTime() + Utils().getMyWord("{maybe_have_codesplit}") + Utils().getFilename(jsFilePath))
            pattern = re.compile(r"\w\.p\+\"(.*?)\.js", re.DOTALL)
            if pattern:
                jsCodeList = pattern.findall(jsFile)
                for jsCode in jsCodeList:
                    if len(jsCode) < 30000:
                        jsCode = "\"" + jsCode + ".js\""
                        self.jsCodeCompile(jsCode, jsFilePath)

    def getRealFilePath(self, jsFileNames, jsUrlpath):
        # 我是没见过webpack异步加载的js和放异步的js不在同一个目录下的，这版先不管不同目录的情况吧
        jsRealPaths = []
        res = urlparse(jsUrlpath)
        tmpUrl = jsUrlpath.split("/")
        base_url = "/".join(tmpUrl) + "/"
        for jsFileName in jsFileNames:
            jsFileName = Utils().getFilename(jsFileName)  # 获取js名称
            jsFileName = base_url + jsFileName
            jsRealPaths.append(jsFileName)
        try:
            domain = res.netloc
            if ":" in domain:
                domain = str(domain).replace(":", "_")
            DownloadJs(jsRealPaths, self.options).downloadJs(self.projectTag, domain, 1)
            print("downjs功能正常")
        except Exception as e:
            print("[Err] %s" % e)

    def recoverStart(self, projectPath):
        for parent, dirnames, filenames in os.walk(projectPath + '/', followlinks=True):
            for filename in filenames:
                filePath = os.path.join(parent, filename)
                self.checkCodeSpilting(filePath)
        print(Utils().tellTime() + Utils().getMyWord("{check_js_fini}"))
