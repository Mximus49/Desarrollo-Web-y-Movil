# Detiene los servicios buscando el proceso que escucha en cada puerto.
# No toca Docker (MongoDB y RabbitMQ) ni Vault.
# Uso: .\scripts\detener_servicios.ps1

$puertos = @(8000, 8100, 9001, 9002, 9003, 9004, 9005, 8090, 8300)
foreach ($puerto in $puertos) {
    $conexion = Get-NetTCPConnection -LocalPort $puerto -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($conexion) {
        Stop-Process -Id $conexion.OwningProcess -Force
        Write-Host "Detenido el proceso del puerto $puerto"
    }
}
# El consumidor STOMP no abre puerto, se busca por su linea de comando
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
    Where-Object { $_.CommandLine -like "*consumidor.py*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host "Detenido el consumidor de notificaciones" }
