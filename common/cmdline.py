import optparse
import sys


class CommandLines():

    def cmd(self):
        parse = optparse.OptionParser()
        parse.add_option('-u', '--url', dest='url', help='Please enter the target site')
        parse.add_option('-c', '--cookie', dest='cookie', help='Please enter the site cookies')
        parse.add_option('-d', '--head', dest='head', default='Cache-Control:no-cache',
                         help='Please Enter the extra HTTP head')
        parse.add_option('-b', '--base', dest='baseurl', type=str, help='Please enter the baseurl')

        parse.add_option('-C', '--cache', dest='cache', default='off', type=str,
                         help='Please choose whether to save ths js files or not(on/off), defalut is off')
        parse.add_option('--rh', '--routehost', dest='routehost', type=str,
                         help='RouteHost like: https://pocsir.com:777/')
        parse.add_option('-f', '--flag', dest='ssl_flag', default='0', type=str, help='SSL SEC FLAG')
        parse.add_option('-m', '--mode', dest='mode', default='simple', type=str,
                         help='Please Enter scan mode, simple or custom')
        parse.add_option('-p', '--proxy', dest='proxy', default='noproxy', type=str,
                         help='Please Enter your own Proxy Address')
        # 指定前端baseURL，重放全部前端路由
        parse.add_option('--of', '--onlyfront', dest='onlyfront', default='off', type=str,
                         help='Retry all frontend routes with particular baseURL')
        # 基于两个结果文本，重放全部后端API
        parse.add_option('--ob', '--onlyback', dest='onlyback', default='off', type=str,
                         help='Retry all baseURLs and backend apis with exist result-files')
        # 自定义提取正则
        parse.add_option('-r', '--regex', dest='regex', type=str,
                         help='Please Enter your own Regx Rules, that string will spilt by \',\'')
        (options, args) = parse.parse_args()
        if options.mode == 'simple':
            if options.url is None:
                parse.print_help()
                sys.exit(0)
        return options


if __name__ == '__main__':
    print(CommandLines().cmd().cookie)
