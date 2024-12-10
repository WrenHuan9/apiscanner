from Controller import Project
from common.TestProxy import testProxy
from common.cmdline import CommandLines


class Program():
    def __init__(self, options):
        self.options = options

    def check(self):
        url = self.options.url
        t = Project(url, self.options)
        t.run()


if __name__ == '__main__':
    cmd = CommandLines().cmd()
    testProxy(cmd)
    APIScanner = Program(cmd)
    APIScanner.check()