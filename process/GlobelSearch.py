import os
import re
from process import ReadConfig
from common.utils import Utils


def search(projectPath, keyWordsOptions, jsBaseURL):
    print(Utils().tellTime() + "正在检测JS敏感词...")
    keyWords = ReadConfig.ReadConfig().getValue('vuln', 'keywords')[0]
    keyWordsSearchResults = []
    if keyWordsOptions is not None:
        keyWords = str(keyWordsOptions)
    keyWords = str(keyWords).split(',')
    for keyword in keyWords:
        regex = r'{}'.format(keyword)
        for i in os.listdir(projectPath):
            if i[-3:] == '.js':
                with open(projectPath + i, 'r', encoding='utf-8', errors='ignore') as jsFile:
                    jsStr = jsFile.read()
                    results = re.findall(regex, jsStr)
                    results = list(set(results))
                    for result in results:
                        keyWordsSearchResults.append(result)
                    jsFile.close()
                if len(keyWordsSearchResults) > 0:
                    # todo 提取数量有问题
                    with open(projectPath + 'PasswordShowOn.txt', 'a', encoding='utf-8', errors='ignore') as resultFile:
                        if jsBaseURL != projectPath:
                            print('关键字正则：' + keyword + '，关键字js文件位置：' + jsBaseURL + '/' + ".".join(i.split(".")[1:]) + '，该文件共提取到' + str(len(keyWordsSearchResults)) + '处', file=resultFile)
                        else:
                            print('关键字正则：' + keyword + '，关键字js文件位置：' + jsBaseURL + i + '，该文件共提取到' + str(len(keyWordsSearchResults)) + '处', file=resultFile)
                        keyWordsSearchResults = []
                        resultFile.close()
    print(Utils().tellTime() + "JS敏感词检测完毕！")