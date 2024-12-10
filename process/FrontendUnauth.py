from urllib.parse import urlparse

from process.BatchRequest import BatchRequest
from common.utils import Utils


class FrontendUnauth():

    def __init__(self, projectPath, options):
        self.options = options
        self.projectPath = projectPath
        self.frontPaths = []
        self.completeFrontendPaths = []

    def routeComplete(self, url):
        print(Utils().tellTime() + "正在拼接前端路由...")
        # todo +# 好像不能在这里，拼接失效了，前端带anchor还是没办法访问
        if "#" in url:
            url = url.split("#")[0] + "#/"
        res = urlparse(url)
        tmpUrl = res.path.split("/")
        # IP/domain + port
        hostURL = res.scheme + "://" + res.netloc
        with open(self.projectPath + 'FrontResult.txt', 'r', encoding='utf-8', errors='ignore') as frontResult:
            for frontRoute in frontResult.readlines():
                self.frontPaths.append(frontRoute.replace("\n", ""))
            frontResult.close()
        for path in self.frontPaths:
            self.completeFrontendPaths.append(hostURL + "/" + path)
            if len(tmpUrl) > 2:
                tmpUrl[-1] = path
                self.completeFrontendPaths.append(hostURL + "/".join(tmpUrl))
        self.completeFrontendPaths = list(set(self.completeFrontendPaths))
        print(Utils().tellTime() + "前端路由拼接完毕！")
        self.unauthRequest(self.completeFrontendPaths)

    def unauthRequest(self, completeFrontendPaths):
        print(Utils().tellTime() + "正在尝试访问前端路由...")
        # todo 前端未授权访问统计筛选可能存在的问题项，后期命名高亮
        BatchRequest(self.projectPath, self.options, completeFrontendPaths).run(0, 'frontend.log')
        print(Utils().tellTime() + "前端路由检查完毕！")