# Inicia Vault en modo desarrollo con TLS. Vault genera su propia CA en certs\vault.
# Los datos quedan en memoria: al cerrarlo hay que volver a correr cargar_secretos.ps1.
# Uso: .\scripts\iniciar_vault.ps1   (la ventana queda abierta mientras Vault corre)

$backend = Split-Path -Parent $PSScriptRoot
$dir = Join-Path $backend "certs\vault"
New-Item -ItemType Directory -Force $dir | Out-Null
$vault = "C:\Hashicorp\Vault\vault.exe"
if (-not (Test-Path $vault)) { $vault = "vault" }

# El token raiz solo lo usan los scripts de administracion; cada servicio recibe un token propio
& $vault server -dev-tls -dev-tls-cert-dir="$dir" -dev-root-token-id="dev-only-token"
