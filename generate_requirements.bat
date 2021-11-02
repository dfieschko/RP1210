@ECHO OFF
@ECHO Running...
py -m pip install -U -q pipreqs
cd RP1210
pipreqs --force
PAUSE
