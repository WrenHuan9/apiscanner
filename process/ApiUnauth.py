from urllib.parse import urlparse
from process.BatchRequest import BatchRequest
from common.utils import Utils


class ApiUnauth():

    def __init__(self, projectPath, options):
        self.options = options
        self.projectPath = projectPath
        self.baseUrlPaths = []
        self.apiPaths = []
        self.completeApis = []

    def apiComplete(self, url):
        if "#" in url:
            url = url.split("#")[0]
        res = urlparse(url)
        tmpUrl = res.path.split("/")
        # IP/domain + port
        hostURL = res.scheme + "://" + res.netloc
        with open(self.projectPath + 'result.txt', 'r', encoding='utf-8', errors='ignore') as apiResult:
            for apiPath in apiResult.readlines():
                self.apiPaths.append(apiPath.replace("\n", ""))
            apiResult.close()
        with open(self.projectPath + 'BaseURLResult.txt', 'r', encoding='utf-8', errors='ignore') as baseURLResult:
            for baseurl in baseURLResult.readlines():
                self.baseUrlPaths.append(baseurl.replace("\n", ""))
            baseURLResult.close()

        for baseurl in self.baseUrlPaths:
            for apiPath in self.apiPaths:
                # 完整请求直接加
                if apiPath[0:4] == 'http':
                    self.completeApis.append(apiPath)
                    continue
                if baseurl == "/":
                    completeUrl = hostURL + apiPath
                    self.completeApis.append(completeUrl)
                elif 'http' in baseurl:
                    completeUrl = baseurl + apiPath
                    self.completeApis.append(completeUrl)
                else:
                    completeUrl = hostURL + baseurl + apiPath
                    self.completeApis.append(completeUrl)
        self.completeApis = list(set(self.completeApis))
        print(Utils().tellTime() + "后端API拼接完毕！")
        self.unauthRequest(self.completeApis)

    def unauthRequest(self, completeApiPaths):
        print(Utils().tellTime() + "正在尝试以GET请求访问API...")
        # todo api未授权访问统计筛选可能存在的问题项，后期命名高亮
        BatchRequest(self.projectPath, self.options, completeApiPaths).run(0, 'api-get.log')
        print(Utils().tellTime() + "后端API GET请求检查完毕！")
        print(Utils().tellTime() + "正在尝试以POST请求访问API...")
        BatchRequest(self.projectPath, self.options, completeApiPaths).run(1, 'api-post.log')
        print(Utils().tellTime() + "后端API POST请求检查完毕！")