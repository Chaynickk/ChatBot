# Запуск FastAPI приложения
Start-Process -NoNewWindow powershell -ArgumentList "cd $PSScriptRoot; uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Запуск cloudflared для бэка
Write-Host "STARTING BACKEND CLOUDFLARED..."
$backendProc = Start-Process -FilePath "C:\Users\User\AppData\Roaming\npm\cloudflared.cmd" -ArgumentList "tunnel --config $PSScriptRoot\config.yml run chatlux-tunnel" -NoNewWindow -PassThru

# Записываем URL бэкенда в .env
Set-Content -Path ".env" -Value "PUBLIC_BACKEND_URL=https://api.chatlux.ru"

# Выводим адрес бэкенда
Write-Host "BACKEND URL: https://api.chatlux.ru"
