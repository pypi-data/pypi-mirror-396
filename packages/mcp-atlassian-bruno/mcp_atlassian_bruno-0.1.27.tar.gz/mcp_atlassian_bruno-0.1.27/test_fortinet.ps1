# Script para probar FortiGate response handling
$env:PYTHONIOENCODING="utf-8"

# Iniciar servidor en background
Write-Host "Iniciando servidor MCP..." -ForegroundColor Green
$serverProcess = Start-Process -FilePath "python.exe" `
    -ArgumentList "-m","mcp_atlassian.servers.main" `
    -WorkingDirectory "c:\Users\bruno.izaguirre\Documents\mcp-atlassian" `
    -NoNewWindow `
    -PassThru `
    -RedirectStandardOutput "server_output.log" `
    -RedirectStandardError "server_error.log"

Start-Sleep -Seconds 3

Write-Host "Servidor iniciado con PID: $($serverProcess.Id)" -ForegroundColor Green
Write-Host "Verifica server_output.log y server_error.log para ver los logs"
Write-Host ""
Write-Host "Para detener el servidor, ejecuta:"
Write-Host "Stop-Process -Id $($serverProcess.Id)"
