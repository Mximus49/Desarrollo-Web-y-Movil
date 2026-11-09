# Genera una autoridad certificadora local y el certificado TLS que usan el gateway y los servicios.
# Los archivos quedan en certs/ (excluida del repositorio). Solo sirven para el ambiente local.
#
# Uso: python scripts/generar_certificados.py            crea los archivos si no existen
#      python scripts/generar_certificados.py --forzar   los vuelve a crear (rotacion)

from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from pathlib import Path
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

CERTS = Path(__file__).resolve().parent.parent / "certs"


def guardar_clave(clave, ruta: Path):
    ruta.write_bytes(clave.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))


def guardar_cert(cert, ruta: Path):
    ruta.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def nombre(texto: str):
    return x509.Name([x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Queso & Sabor"),
                      x509.NameAttribute(NameOID.COMMON_NAME, texto)])


def main():
    if (CERTS / "servidor.crt").exists() and "--forzar" not in sys.argv:
        print(f"Los certificados ya existen en {CERTS}. Use --forzar para regenerarlos.")
        return
    CERTS.mkdir(exist_ok=True)
    ahora = datetime.now(timezone.utc)

    clave_ca = ec.generate_private_key(ec.SECP256R1())
    ca = (x509.CertificateBuilder()
          .subject_name(nombre("Queso & Sabor CA local")).issuer_name(nombre("Queso & Sabor CA local"))
          .public_key(clave_ca.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(ahora - timedelta(minutes=5)).not_valid_after(ahora + timedelta(days=365))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(digital_signature=True, key_cert_sign=True, crl_sign=True,
                                       content_commitment=False, key_encipherment=False, data_encipherment=False,
                                       key_agreement=False, encipher_only=False, decipher_only=False), critical=True)
          .sign(clave_ca, hashes.SHA256()))

    clave_srv = ec.generate_private_key(ec.SECP256R1())
    servidor = (x509.CertificateBuilder()
                .subject_name(nombre("localhost")).issuer_name(ca.subject)
                .public_key(clave_srv.public_key()).serial_number(x509.random_serial_number())
                .not_valid_before(ahora - timedelta(minutes=5)).not_valid_after(ahora + timedelta(days=90))
                .add_extension(x509.SubjectAlternativeName([
                    x509.DNSName("localhost"), x509.IPAddress(ip_address("127.0.0.1"))]), critical=False)
                .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
                .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
                .sign(clave_ca, hashes.SHA256()))

    guardar_clave(clave_ca, CERTS / "ca.key")
    guardar_cert(ca, CERTS / "ca.crt")
    guardar_clave(clave_srv, CERTS / "servidor.key")
    guardar_cert(servidor, CERTS / "servidor.crt")
    print(f"Certificados creados en {CERTS}: ca.crt (confiar en este), servidor.crt y servidor.key")


if __name__ == "__main__":
    main()
