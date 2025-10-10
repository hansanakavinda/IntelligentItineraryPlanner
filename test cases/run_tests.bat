@echo off

echo Activating virtual environment...
call ..\venv\Scripts\activate

echo Running Tests...
python test_haversin_distance.py

echo.
pause