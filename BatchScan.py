import os

if __name__ == '__main__':
    with open('site.txt') as siteFile:
        sites = siteFile.readlines()
        for site in sites:
            site = site.replace("\n", "")
            cmd = "python3 apiscanner.py -u {} -m=normal".format(site)
            try:
                result = os.system(cmd)
            except:
                with open('executeResult.log', 'a', encoding='utf-8', errors='ignore') as executeResultFile:
                    print(site + '出错了', file=executeResultFile)
                    executeResultFile.close()
            with open('executeResult.log', 'a', encoding='utf-8', errors='ignore') as executeResultFile:
                print(site + '已完成', file=executeResultFile)
                executeResultFile.close()