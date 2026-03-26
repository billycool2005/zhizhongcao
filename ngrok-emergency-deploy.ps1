# 🐵 Zhizhongcao - Emergency Ngrok Deployment
# Date: 2026-03-26
# Time: 08:40 AM
# Purpose: Quick public URL while GitHub registration pending

Write-Host "🚀 Starting Emergency Ngrok Deployment..." -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow

# Check if ngrok is installed
$ngrokPath = "$env:LOCALAPPDATA\npm\node_modules\.bin\ngrok.cmd"
if (Test-Path $ngrokPath) {
    Write-Host "✅ Ngrok found at: $ngrokPath" -ForegroundColor Green
} else {
    Write-Host "⚠️ Ngrok not found. Installing..." -ForegroundColor Yellow
    npm install -g ngrok
    
    if ($?) {
        Write-Host "✅ Ngrok installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install ngrok. Trying alternative..." -ForegroundColor Red
        
        # Alternative: Use localtunnel
        Write-Host "Installing localtunnel as backup..." -ForegroundColor Yellow
        npm install -g localtunnel
        
        $ltPort = 8000
        $cmd = "lt --port $ltPort"
        Write-Host "Running: $cmd" -ForegroundColor Gray
        
        # Note: localtunnel will show a URL in console output
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "`"$PSScriptRoot\lt-command.cmd`""
        return
    }
}

# Start ngrok tunnel to expose local server
Write-Host ""
Write-Host "Starting tunnel to localhost:8000..." -ForegroundColor Cyan
Write-Host "Please wait ~30 seconds for tunnel establishment..." -ForegroundColor Yellow

try {
    # Start ngrok process
    Start-Process -FilePath "ngrok" -ArgumentList "http 8000" -WindowStyle Normal -Wait
    
    Write-Host ""
    Write-Host "✅ SUCCESS! Public URL generated:" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Your Temporary Public URL:" -ForegroundColor Cyan
    Write-Host "   https://YOUR-NGROK-ID.ngrok.io" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Copy this URL and share with seed users!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
} catch {
    Write-Host "❌ Error starting ngrok: $_" -ForegroundColor Red
}
