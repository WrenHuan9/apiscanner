import os
import re

from common.utils import Utils


class FrontRouteCollect():

    def __init__(self, projectPath, options):
        self.options = options
        self.projectPath = projectPath
        self.regex = r'path\:\"(.*?)\"'
        self.frontPaths = []

    def pathCollect(self):
        print(Utils().tellTime() + "正在提取前端路由...")
        for i in os.listdir(self.projectPath):
            with open(self.projectPath + i, 'r', encoding='utf-8', errors='ignore') as jsFile:
                apiStr = jsFile.read()
                apiLists = re.findall(self.regex, apiStr)
                for apiPath in apiLists:
                    if apiPath != '' and '/' in apiPath:
                        if ":" in apiPath:
                            apiPath = apiPath.split(":")[0]
                            self.frontPaths.append(apiPath)
                        else:
                            self.frontPaths.append(apiPath)
                jsFile.close()
        self.frontPaths = list(set(self.frontPaths))
        self.frontPaths.sort()
        with open(self.projectPath + 'FrontResult.txt', 'a') as resultFile:
            for route in self.frontPaths:
                if route[0] == '/':
                    route = route[1:]
                print(route, file=resultFile)
            resultFile.close()
            print(Utils().tellTime() + "前端路由提取完毕！")
