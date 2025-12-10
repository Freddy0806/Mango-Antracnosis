@echo off
echo ========================================================
echo   MODO MOVIL - DETECTOR DE ANTRACNOSIS
echo ========================================================
echo.
echo 1. Asegurate de que tu celular y esta PC esten en el mismo WIFI.
echo 2. Busca tu Direccion IP abajo (generalmente comienza con 192.168...):
echo.
ipconfig | findstr "IPv4"
echo.
echo 3. En tu celular, abre Chrome o Safari e ingresa:
echo    http://<TU_IP_AQUI>:8000
echo.
echo    Ejemplo: http://192.168.1.5:8000
echo.
echo ========================================================
echo   Iniciando servidor CUSTOM (Python)... (Cierra esta ventana para detener)
echo ========================================================
python mobile_server.py
pause
