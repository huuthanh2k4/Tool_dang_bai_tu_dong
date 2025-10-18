@echo off
REM Dong lenh quan trong: Tu dong chuyen den thu muc chua file .bat nay
cd /d "%~dp0"

echo =======================================================
echo  KHOI DONG CONG CU DANG BAI FACEBOOK - VUI LONG CHO...
echo =======================================================
echo.

REM Truc tiep chay ung dung Streamlit bang Python thuong da duoc cai dat tren may
streamlit run a.py

echo.
echo Ung dung da duoc khoi dong. Vui long kiem tra trinh duyet.

pause