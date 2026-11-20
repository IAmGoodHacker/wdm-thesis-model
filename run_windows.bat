@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Розрахункова модель адаптивного термінала WDM
echo ============================================================
echo.

rem --- 1. Пошук Python ---
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [ПОМИЛКА] Python не знайдено.
    echo Встановіть Python з https://www.python.org/downloads/
    echo і обов'язково поставте позначку "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)
echo [1/3] Знайдено Python:
%PY% --version
echo.

rem --- 2. Встановлення бібліотек (лише якщо їх ще немає) ---
%PY% -c "import numpy, scipy, matplotlib" >nul 2>nul
if errorlevel 1 (
    echo [2/3] Встановлення бібліотек NumPy, SciPy, Matplotlib...
    %PY% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ПОМИЛКА] Не вдалося встановити бібліотеки. Перевірте підключення до Інтернету.
        pause
        exit /b 1
    )
) else (
    echo [2/3] Бібліотеки вже встановлено.
)
echo.

rem --- 3. Розрахунок ---
echo [3/3] Виконується розрахунок...
%PY% -X utf8 main.py --figures > results.txt
if errorlevel 1 (
    echo [ПОМИЛКА] Під час розрахунку сталася помилка. Подробиці нижче:
    %PY% -X utf8 main.py
    pause
    exit /b 1
)

echo.
echo Готово!
echo   Таблиці збережено у файл:  results.txt
echo   Рисунки збережено в папку: figures
echo.
start "" notepad "results.txt"
start "" explorer "figures"
pause
