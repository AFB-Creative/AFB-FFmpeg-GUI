@echo off
python "%~dp0afb-ffmpeg-gui.py" %*
REM pause

REM ## A simple batch file to run the AFB FFmpeg GUI
REM ## (afb-ffmpeg-gui.py must be in the same folder)
REM ## If encountering errors, remove "REM " in the "REM pause" line to keep the terminal open and see error report