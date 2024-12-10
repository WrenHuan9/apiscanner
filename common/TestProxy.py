import requests

def testProxy(options):
    try:
        # url = "http://api.ipify.org/?format=txt"
        if options.proxy == 'noproxy':
            options.proxy = ''
        proxy_data = {
            'http': options.proxy,
            'https': options.proxy
        }
        ipAddr = "127.0.0.1"
        # ipAddr = requests.get(url, proxies=proxy_data, timeout=7, verify=False).text.strip()
        return ipAddr
    except:
        return ipAddr
