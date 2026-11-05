@echo off
rem Ingrandisce 4 volte (Real-ESRGAN, sul tuo PC) ogni grafica di stampa in stampa\*\design.png
rem e salva il risultato accanto, come design_x4.png. Le grafiche gia' ingrandite vengono saltate.
cd /d "%~dp0"
for /d %%D in ("..\..\stampa\*") do (
  if exist "%%D\design.png" if not exist "%%D\design_x4.png" (
    echo Ingrandisco %%~nxD ...
    realesrgan-ncnn-vulkan.exe -i "%%D\design.png" -o "%%D\design_x4.png" -n realesrgan-x4plus-anime
  )
)
echo.
echo Fatto. Puoi chiudere questa finestra e avvisare Claude.
pause
