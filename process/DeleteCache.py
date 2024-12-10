import os

from process import ReadConfig


def delete(projectPath):
    print("正在清理js本地缓存...")
    fileExts = ReadConfig.ReadConfig().getValue('blacklist', 'resultFiles')[0]
    for i in os.listdir(projectPath):
        filePath = projectPath + i
        flag = 0
        for fileExt in fileExts.split(","):
            if fileExt in filePath:
                flag = 1
        if flag != 1:
            os.remove(filePath)
    print("JS本地缓存清理完成，本次扫描结束！")