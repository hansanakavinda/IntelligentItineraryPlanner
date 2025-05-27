@echo off
echo Activating virtual environment...
call venv\Scripts\activate

echo Starting Streamlit app...
streamlit run app\main.py

pause
