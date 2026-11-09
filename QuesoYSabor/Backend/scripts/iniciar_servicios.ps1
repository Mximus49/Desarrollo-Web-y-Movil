# Abre una ventana de PowerShell por servicio.
# Cada servicio recibe un token de Vault propio, con una politica que solo le deja leer sus secretos,
# y escucha con TLS usando el certificado de certs\.
# Antes de usarlo: Vault iniciado, secretos cargados, Docker arriba, base creada y el entorno de conda activado.
# Uso: . .\scripts\entorno.ps1 ; .\scripts\iniciar_servicios.ps1

$backend = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python).Source
$vault = "C:\Hashicorp\Vault\vault.exe"
if (-not (Test-Path $vault)) { $vault = "vault" }
if (-not $env:SSL_CERT_FILE) { throw "Prepare la terminal primero: . .\scripts\entorno.ps1" }

$tls = "--ssl-keyfile '$backend\certs\servidor.key' --ssl-certfile '$backend\certs\servidor.crt'"
$servicios = @(
    @{ nombre = "mensajeria"; carpeta = "mensajeria"; politica = "mensajeria"; comando = "& '$python' -m uvicorn mensajeria_api:app --host 127.0.0.1 --port 8300 $tls" },
    @{ nombre = "auth";       carpeta = "auth-service"; politica = "auth";     comando = "& '$python' -m uvicorn auth_service:app --host 127.0.0.1 --port 8100 $tls" },
    @{ nombre = "inventory";  carpeta = "inventory";  politica = "inventory";  comando = "& '$python' -m uvicorn inventory_api:app --host 127.0.0.1 --port 9001 $tls" },
    @{ nombre = "orders";     carpeta = "orders";     politica = "orders";     comando = "& '$python' -m uvicorn orders_api:app --host 127.0.0.1 --port 9002 $tls" },
    @{ nombre = "clients";    carpeta = "clients";    politica = "clients";    comando = "& '$python' -m uvicorn clients_api:app --host 127.0.0.1 --port 9003 $tls" },
    @{ nombre = "payments";   carpeta = "payments";   politica = "payments";   comando = "& '$python' -m uvicorn payments_api:app --host 127.0.0.1 --port 9004 $tls" },
    @{ nombre = "analytics";  carpeta = "analytics";  politica = "analytics";  comando = "& '$python' -m uvicorn analytics_api:app --host 127.0.0.1 --port 9005 $tls" },
    @{ nombre = "graphql";    carpeta = "graphql";    politica = "graphql";    comando = "node server.js" },
    @{ nombre = "notifications"; carpeta = "notifications"; politica = "notifications"; comando = "& '$python' consumidor.py" },
    # El gateway parte al final; es el unico que escucha en todas las interfaces
    @{ nombre = "gateway";    carpeta = "gateway";    politica = "gateway";    comando = "& '$python' -m uvicorn gateway:app --host 0.0.0.0 --port 8000 $tls" }
)

foreach ($s in $servicios) {
    if ($s.nombre -eq "gateway") { Start-Sleep -Seconds 5 }
    # Token de 24 horas que solo puede leer las rutas de la politica del servicio
    $token = & $vault token create -policy="quesoysabor-$($s.politica)" -ttl=24h -field=token
    if (-not $token) { throw "No se pudo crear el token de Vault para $($s.nombre)" }
    $cmd = "`$host.UI.RawUI.WindowTitle = '$($s.nombre)'; `$env:VAULT_ADDR = '$env:VAULT_ADDR'; `$env:VAULT_TOKEN = '$token'; " +
           "`$env:SSL_CERT_FILE = '$env:SSL_CERT_FILE'; `$env:NODE_EXTRA_CA_CERTS = '$env:SSL_CERT_FILE'; " +
           "cd '$backend\$($s.carpeta)'; $($s.comando)"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
    Write-Host "Iniciado $($s.nombre)"
}
Write-Host "Gateway en https://localhost:8000 (health: https://localhost:8000/health)"
