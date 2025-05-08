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

# Запуск cloudflared для фронта
Write-Host "STARTING FRONTEND CLOUDflared..."
$frontendProc = Start-Process -FilePath "C:\Users\User\AppData\Roaming\npm\cloudflared.cmd" -ArgumentList "tunnel --url http://localhost:3000 2>&1" -NoNewWindow -RedirectStandardOutput "frontend_url.txt" -PassThru

# Ждём появления адреса
$frontendUrl = $null
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Path "frontend_url.txt") {
        $lines = Get-Content "frontend_url.txt"
        foreach ($line in $lines) {
            if ($line -match "https://[a-zA-Z0-9.-]+\.trycloudflare\.com") {
                $frontendUrl = $Matches[0]
                break
            }
        }
    }
    if ($frontendUrl) { break }
}
if (-not $frontendUrl) {
    Write-Host "FAILED TO GET FRONTEND URL FROM CLOUDFLARED."
    exit 1
}

# Обновляем .env файл, сохраняя существующие настройки
$envContent = Get-Content ".env"
$newContent = @()
$backendUrlAdded = $false
$frontendUrlAdded = $false

foreach ($line in $envContent) {
    if ($line -match "^PUBLIC_BACKEND_URL=") {
        $newContent += "PUBLIC_BACKEND_URL=https://api.chatlux.ru"
        $backendUrlAdded = $true
    } elseif ($line -match "^PUBLIC_FRONTEND_URL=") {
        $newContent += "PUBLIC_FRONTEND_URL=$frontendUrl"
        $frontendUrlAdded = $true
    } else {
        $newContent += $line
    }
}

if (-not $backendUrlAdded) {
    $newContent += "PUBLIC_BACKEND_URL=https://api.chatlux.ru"
}
if (-not $frontendUrlAdded) {
    $newContent += "PUBLIC_FRONTEND_URL=$frontendUrl"
}

$newContent | Set-Content ".env"

# Выводим только адреса с пометкой
Write-Host "BACKEND URL: https://api.chatlux.ru"
Write-Host "FRONTEND URL: $frontendUrl"