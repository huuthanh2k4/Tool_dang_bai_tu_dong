@echo off
REM Tự động chuyển đến thư mục chứa file .bat này
cd /d "%~dp0"

echo =======================================================
echo  KHOI DONG CONG CU DANG BAI FACEBOOK - VUI LONG CHO...
echo =======================================================
echo.

REM Kích hoạt môi trường ảo (chỉ cần gọi python trong .venv là đủ)
REM Chạy streamlit bằng Python trong môi trường ảo
.venv\Scripts\python.exe -m streamlit run a.py

echo.
echo Ung dung da duoc khoi dong. Vui long kiem tra trinh duyet.

pause
