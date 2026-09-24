@echo off
echo Stopping any running Python processes...
taskkill /F /IM python.exe 2>nul

echo Deleting old databases...
timeout /t 2 /nobreak >nul
del /F /Q "e:\RetailBillingSystem\instance\retail_billing.db" 2>nul
del /F /Q "e:\RetailBillingSystem\RetailBillingSystem\instance\retail_billing.db" 2>nul

echo Creating new database...
cd /d "e:\RetailBillingSystem\RetailBillingSystem"
python setup_db.py

echo.
echo ========================================
echo Database reset complete!
echo ========================================
echo.
echo Now run: python app.py
echo Login with: admin@demo.com / admin123
echo.
pause
