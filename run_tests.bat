@ECHO OFF
ECHO ..............................................................................................
ECHO :                  Welcome to the RP1210.py automatic-ish test suite!                        :
ECHO ..............................................................................................
ECHO Preparing...
REM ECHO Checking pytest installation...
REM py -m pip install -U -q pytest
REM py -m pip install -U -q pytest-cov
ECHO Preparing test directory...
ECHO Removing old source code from Test directory...
rmdir /s /q Test\RP1210
ECHO Copying source code into Test directory...
xcopy /v /s /y /q RP1210 Test\RP1210\
cd Test
ECHO Done!
ECHO ..............................................................................................
ECHO Disconnect all RP1210 adapters before continuing.
pause
@SETLOCAL ENABLEDELAYEDEXPANSION & python -x "%~f0" %* & EXIT /B !ERRORLEVEL!
from operator import contains
import sys, os, configparser, pytest

config = configparser.ConfigParser()
path = os.curdir + "/test-files/RP121032.ini"
config.read(path)
argstemplate = "-l -v -ra --tb=long --cov=RP1210 --cov func --cov-branch --cov-report term-missing"
testapis = list(map(int, config.get("RP1210Support", "APIImplementations").split(',')))
for api in testapis:
    args_str = argstemplate + "--apiname " + api
    args = args_str.split(" ")
    pytest.main(args)
pause
