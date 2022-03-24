from operator import contains
import sys, os, configparser, pytest

path = sys.argv
config = configparser.ConfigParser()

if(not os.path.isabs(path)):
    path = os.path.join(os.curdir, path)

if(not os.path.isfile):
    path += "/RP121032.ini"

config.read(path)
argstemplate = "-l -v -ra --tb=long --cov=RP1210 --cov func --cov-branch --cov-report term-missing"
testapis = list(map(int, config.get("RP1210Support", "APIImplementations").split(',')))
for api in testapis:
    args_str = argstemplate + "--apiname " + api
    args = args_str.split(" ")
    pytest.main(args)