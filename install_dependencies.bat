@echo off
REM Tu dong chuyen den thu muc chua file .bat nay
cd /d "%~dp0"

echo ===================================================================
echo  BAT DAU QUA TRINH CAI DAT MOI TRUONG VA CAC THU VIEN CAN THIET
echo  Vui long khong tat cua so nay cho den khi hoan tat.
echo ===================================================================
echo.

REM Kiem tra xem Python da duoc cai dat chua
python --version >nul 2>&1
if %errorlevel% neq 0 (
echo [LOI] Khong tim thay Python. Vui long cai dat Python truoc khi chay file nay.
pause
exit /b
)

echo [Buoc 1/2] Dang tao moi truong ao (.venv)...
python -m venv .venv
echo    -> Tao moi truong ao thanh cong!
echo.

echo [Buoc 2/2] Dang cai dat cac thu vien tu requirements.txt...
REM Goi truc tiep pip tu moi truong ao de dam bao cai dat dung noi
.venv\Scripts\pip.exe install -r requirements.txt
echo    -> Cai dat thu vien hoan tat!
echo.

echo ===================================================================
echo  CAI DAT HOAN TAT!
echo  Tu bay gio, ban chi can chay file "start_app.bat" de khoi dong.
echo  Cua so nay se tu dong dong sau 5 giay...
echo ===================================================================
echo.
pause