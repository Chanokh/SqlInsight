@echo off
call venv\Scripts\activate.bat
SET PYTHONPATH=%cd%
SET PYTHONPATH
python -m cProfile -s time %cd%\sqlinsight.py C:\Users\glombard\Desktop\databases