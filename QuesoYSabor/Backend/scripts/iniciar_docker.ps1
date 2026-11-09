# Levanta MongoDB y RabbitMQ en Docker con las claves que estan en Vault y espera a que respondan.
# Requiere Docker Desktop abierto, Vault con secretos cargados y: . .\scripts\entorno.ps1
# Uso: .\scripts\iniciar_docker.ps1        (para bajarlos: docker compose down)

$backend = Split-Path -Parent $PSScriptRoot
$vault = "C:\Hashicorp\Vault\vault.exe"
if (-not (Test-Path $vault)) { $vault = "vault" }

# Las claves viven solo en esta sesion de PowerShell, no se guardan en archivos
$env:MONGO_ROOT_CLAVE = & $vault kv get -field=clave secret/quesoysabor/mongo-admin
$env:BROKER_CLAVE = & $vault kv get -field=clave secret/quesoysabor/broker
if (-not $env:MONGO_ROOT_CLAVE -or -not $env:BROKER_CLAVE) { throw "No se pudieron leer las claves desde Vault" }

Push-Location $backend
# --force-recreate: si Vault se reinicio, las claves cambiaron y los contenedores deben partir de nuevo
docker compose up -d --force-recreate
Pop-Location

foreach ($par in @(@("quesoysabor-mongo", "Waiting for connections"), @("quesoysabor-rabbitmq", "Server startup complete"))) {
    for ($i = 0; $i -lt 40; $i++) {
        if (docker logs $par[0] 2>&1 | Select-String $par[1] -Quiet) { break }
        Start-Sleep 2
    }
    Write-Host "$($par[0]) listo"
}
