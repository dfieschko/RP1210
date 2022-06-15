@ECHO OFF
ECHO This script will replace your existing RP1210 installation with
ECHO an RP1210 package downloaded from PyPi (the offical package).
py -m pip uninstall RP1210
py -m pip install RP1210
PAUSE
