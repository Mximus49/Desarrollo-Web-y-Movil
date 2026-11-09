# Configura la terminal actual para administrar el backend. Se ejecuta con punto al inicio:
#   . .\scripts\entorno.ps1
# Define la direccion de Vault, el token de administracion y los certificados de confianza.

$backend = Split-Path -Parent $PSScriptRoot
$env:VAULT_ADDR = "https://127.0.0.1:8200"
$env:VAULT_CACERT = Join-Path $backend "certs\vault\vault-ca.pem"
if (-not $env:VAULT_TOKEN) { $env:VAULT_TOKEN = "dev-only-token" }

# confianza.pem junta la CA local (gateway y servicios) con la CA que genero Vault al partir
$ca = Join-Path $backend "certs\ca.crt"
$confianza = Join-Path $backend "certs\confianza.pem"
if ((Test-Path $ca) -and (Test-Path $env:VAULT_CACERT)) {
    Get-Content $ca, $env:VAULT_CACERT | Set-Content -Encoding ascii $confianza
    $env:SSL_CERT_FILE = $confianza
    $env:NODE_EXTRA_CA_CERTS = $confianza
    Write-Host "Entorno listo: Vault en $env:VAULT_ADDR, certificados de confianza en certs\confianza.pem"
} else {
    Write-Warning "Faltan certificados. Corra 'python scripts\generar_certificados.py' y verifique que Vault este iniciado."
}
