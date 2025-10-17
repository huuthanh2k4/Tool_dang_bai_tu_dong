@echo off
echo =======================================================
echo  KHOI DONG CONG CU DANG BAI FACEBOOK - VUI LONG CHO...
echo =======================================================

REM Kich hoat moi truong ao va chay ung dung Streamlit
call .venv\Scripts\activate && streamlit run a.py

echo.
echo Ung dung da duoc khoi dong. Vui long kiem tra trinh duyet.
echo Cua so nay se tu dong dong sau khi ban tat ung dung.

pause