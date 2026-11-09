# Carga en Vault las claves de cada servicio y crea una politica de solo lectura por servicio.
# Las claves se generan al azar cada vez, por eso no aparecen en el codigo ni en el README.
# Requiere Vault iniciado (iniciar_vault.ps1) y la terminal preparada con: . .\scripts\entorno.ps1
# Uso: .\scripts\cargar_secretos.ps1

$vault = "C:\Hashicorp\Vault\vault.exe"
if (-not (Test-Path $vault)) { $vault = "vault" }
if (-not $env:VAULT_CACERT) { throw "Prepare la terminal primero: . .\scripts\entorno.ps1" }
& $vault status *> $null
if ($LASTEXITCODE -ne 0) { throw "Vault no responde en $env:VAULT_ADDR. Inicie Vault (iniciar_vault.ps1) y vuelva a preparar la terminal." }

function Nueva-Clave {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return -join ($bytes | ForEach-Object { $_.ToString("x2") })
}

# 1. Clave de servicio: quien llama a un servicio usa la clave de ese servicio
foreach ($servicio in @("auth", "inventory", "orders", "clients", "payments", "analytics", "graphql")) {
    & $vault kv put "secret/quesoysabor/$servicio" service_key="$(Nueva-Clave)" | Out-Null
    Write-Host "Clave de servicio: secret/quesoysabor/$servicio"
}

# 2. Usuario de MongoDB propio de cada servicio, con permiso solo sobre su base (lo crea crear_bd.py)
foreach ($servicio in @("auth", "inventory", "orders", "clients", "payments", "notifications")) {
    $usuario = "qys_$servicio"
    $clave = Nueva-Clave
    $uri = "mongodb://${usuario}:${clave}@127.0.0.1:27018/?authSource=admin"
    & $vault kv put "secret/quesoysabor/db/$servicio" usuario="$usuario" clave="$clave" base="quesoysabor_$servicio" uri="$uri" | Out-Null
    Write-Host "Credencial de base de datos: secret/quesoysabor/db/$servicio"
}
& $vault kv put secret/quesoysabor/mongo-admin usuario="admin" clave="$(Nueva-Clave)" | Out-Null
Write-Host "Administrador de MongoDB: secret/quesoysabor/mongo-admin"

# 3. Integraciones externas y broker
& $vault kv put secret/quesoysabor/pasarela webhook_secret="$(Nueva-Clave)" | Out-Null
& $vault kv put secret/quesoysabor/mensajeria api_key="$(Nueva-Clave)" | Out-Null
& $vault kv put secret/quesoysabor/broker usuario="queso" clave="$(Nueva-Clave)" | Out-Null
Write-Host "Integraciones: pasarela, mensajeria y broker"

# 4. Politicas: cada servicio solo puede leer las rutas que necesita
$permisos = @{
    "gateway"       = @("auth", "inventory", "orders", "clients", "payments", "analytics", "graphql")
    "auth"          = @("auth", "db/auth", "mensajeria")
    "inventory"     = @("inventory", "db/inventory")
    "clients"       = @("clients", "db/clients", "auth")
    "orders"        = @("orders", "db/orders", "inventory", "clients", "broker")
    "payments"      = @("payments", "db/payments", "orders", "pasarela")
    "analytics"     = @("analytics", "orders")
    "graphql"       = @("graphql", "orders", "inventory", "analytics")
    "notifications" = @("db/notifications", "broker", "mensajeria", "auth")
    "mensajeria"    = @("mensajeria")
}
$archivo = [System.IO.Path]::GetTempFileName()
foreach ($servicio in $permisos.Keys) {
    $hcl = ($permisos[$servicio] | ForEach-Object { "path `"secret/data/quesoysabor/$_`" { capabilities = [`"read`"] }" }) -join "`n"
    # Se escribe sin BOM: Vault no acepta el BOM que agrega PowerShell al usar una tuberia
    [System.IO.File]::WriteAllText($archivo, $hcl)
    & $vault policy write "quesoysabor-$servicio" $archivo | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear la politica quesoysabor-$servicio" }
    Write-Host "Politica quesoysabor-${servicio}: $($permisos[$servicio] -join ', ')"
}
Remove-Item $archivo

Write-Host ""
Write-Host "Listo. Para ver una referencia: $vault kv get secret/quesoysabor/inventory"
