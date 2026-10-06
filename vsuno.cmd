@echo off
setlocal
for /f "tokens=2 delims=:" %%C in ('chcp') do set "VSUNO_CP=%%C"
chcp 65001 >nul
set PYTHONUTF8=1
python "%~dp0scripts\vsuno.py" %*
set "VSUNO_EXIT=%errorlevel%"
if defined VSUNO_CP chcp %VSUNO_CP% >nul
exit /b %VSUNO_EXIT%
