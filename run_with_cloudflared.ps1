# Запуск cloudflared для бэка
Write-Host "STARTING BACKEND CLOUDFLARED..."
$backendProc = Start-Process -FilePath "C:\Users\User\AppData\Roaming\npm\cloudflared.cmd" -ArgumentList "tunnel run chatlux-tunnel" -NoNewWindow -PassThru

# Записываем URL бэкенда в .env
Set-Content -Path ".env" -Value "PUBLIC_BACKEND_URL=https://api.chatlux.ru"

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

# Записываем оба адреса в .env
Set-Content -Path ".env" -Value "PUBLIC_BACKEND_URL=https://api.chatlux.ru`nPUBLIC_FRONTEND_URL=$frontendUrl"

# Выводим только адреса с пометкой
Write-Host "BACKEND URL: https://api.chatlux.ru"
Write-Host "FRONTEND URL: $frontendUrl"