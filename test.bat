echo off
@REM Run tests and generate code coverage if "pip coverage" is installed
@REM this message is above the ceedling call because apparently
@REM you can not make any more calls after ceedling with a batch file
echo [92m -------------------------------------------------------------------------------- [0m
echo [92m -------------------------------------------------------------------------------- [0m
echo.
echo. 
echo [92m OPEN IN BROWSER TO SEE COVERAGE REPORT: [0m
echo [94m %cd%/htmlcov/index.html [0m
echo.
echo.
echo [92m -------------------------------------------------------------------------------- [0m
echo [92m -------------------------------------------------------------------------------- [0m
@REM remove html output dir before creating coverage report
@REM this is done to ensure the html updates correctly
del /f /s /q htmlcov 1>nul
rmdir /s /q htmlcov
@REM if a file argument is not passed, test all files
@REM otherwise, just pass the name of the file you would like to test i.e. "./test.bat lin"
set specific_file=%1
if not defined specific_file (
    set specific_file=
)
python -m coverage run -m pytest %specific_file% -s & python -m coverage html
