# Запуск FastAPI приложения
Start-Process -NoNewWindow powershell -ArgumentList "cd $PSScriptRoot; uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Запуск cloudflared для бэка
Write-Host "STARTING BACKEND CLOUDFLARED..."
$backendProc = Start-Process -FilePath "C:\Users\User\AppData\Roaming\npm\cloudflared.cmd" -ArgumentList "tunnel --config $PSScriptRoot\config.yml run chatlux-tunnel" -NoNewWindow -PassThru

# Проверяем существование .env файла
if (-not (Test-Path ".env")) {
    # Если файл не существует, создаем его
    Set-Content -Path ".env" -Value "PUBLIC_BACKEND_URL=https://api.chatlux.ru"
} else {
    # Если файл существует, проверяем наличие PUBLIC_BACKEND_URL
    $envContent = Get-Content ".env"
    if (-not ($envContent -match "PUBLIC_BACKEND_URL")) {
        # Добавляем URL бэкенда, если его нет
        Add-Content -Path ".env" -Value "`nPUBLIC_BACKEND_URL=https://api.chatlux.ru"
    }
}

# Выводим адрес бэкенда
Write-Host "BACKEND URL: https://api.chatlux.ru"
