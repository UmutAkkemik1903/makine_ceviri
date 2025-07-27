@echo off
title Makine Ceviri - Kurulum
echo =====================================
echo    MAKINE CEVIRI UYGULAMASI KURULUM
echo =====================================
echo.

echo Python versiyonu kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    echo Lutfen Python 3.8+ surumunu yukleyin: https://python.org
    pause
    exit /b 1
)

echo Python bulundu!
python --version

echo.
echo Gerekli paketler yukluyor...
echo.

pip install customtkinter==5.2.2
if errorlevel 1 (
    echo HATA: CustomTkinter yuklenemedi!
    pause
    exit /b 1
)

pip install Pillow==10.1.0
if errorlevel 1 (
    echo HATA: Pillow yuklenemedi!
    pause
    exit /b 1
)

pip install chardet==5.2.0
if errorlevel 1 (
    echo HATA: chardet yuklenemedi!
    pause
    exit /b 1
)

echo.
echo =====================================
echo        KURULUM TAMAMLANDI!
echo =====================================
echo.
echo Uygulamayi baslatmak icin 'run.bat' dosyasini calistirin.
echo veya 'python main.py' komutunu kullanin.
echo.
echo Test dosyalari test_files/ klasorunde bulunmaktadir.
echo.
pause
