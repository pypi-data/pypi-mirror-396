import ssl
from pathlib import Path
from loguru import logger

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography import x509
from cryptography.x509.oid import NameOID

PrivateKey = ec.EllipticCurvePrivateKey

HOME_DIRECTORY = Path.home()

PRIVATE_KEY_PATH = Path(HOME_DIRECTORY / ".config" / "primitive" / "private-key.pem")
CERTIFICATE_PATH = Path(HOME_DIRECTORY / ".config" / "primitive" / "certificate.pem")

# NOTE Only used with self-signed server certificate
# THIS IS FOR LOCAL TESTING
SELF_SIGNED_SERVER_CA_PATH = Path(
    HOME_DIRECTORY / ".config" / "primitive" / "server-ca.crt.pem"
)


def are_certificate_files_present() -> bool:
    return PRIVATE_KEY_PATH.exists() and CERTIFICATE_PATH.exists()


def generate_private_key() -> PrivateKey:
    return ec.generate_private_key(
        curve=ec.SECP521R1(),
    )


def read_certificate() -> x509.Certificate:
    cert = x509.load_pem_x509_certificate(CERTIFICATE_PATH.read_bytes())
    return cert


def read_certificate_common_name() -> str:
    cert = read_certificate()

    names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)

    return str(names[0].value)


def create_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context(
        cafile=SELF_SIGNED_SERVER_CA_PATH
        if SELF_SIGNED_SERVER_CA_PATH.exists()
        else None,
        purpose=ssl.Purpose.SERVER_AUTH,
    )
    context.load_cert_chain(
        certfile=CERTIFICATE_PATH,
        keyfile=PRIVATE_KEY_PATH,
    )

    return context


def read_private_key() -> PrivateKey:
    private_key = serialization.load_pem_private_key(
        data=PRIVATE_KEY_PATH.read_bytes(),
        password=None,
    )

    if not isinstance(private_key, PrivateKey):
        raise Exception(
            f"Expected private key type {PrivateKey.__name__}, got {type(private_key).__name__}"
        )

    return private_key


def ensure_private_key() -> PrivateKey:
    private_key_path = PRIVATE_KEY_PATH

    if private_key_path.exists():
        private_key = read_private_key()
    else:
        logger.info("Generating private key.")

        private_key = generate_private_key()

        with private_key_path.open("wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

    return private_key


def write_certificate_pem(certificate_pem: str):
    CERTIFICATE_PATH.write_text(
        data=certificate_pem,
        encoding="utf-8",
    )


def check_certificate():
    try:
        if CERTIFICATE_PATH.exists():
            with CERTIFICATE_PATH.open("rb") as file:
                private_key = read_private_key()
                crt = x509.load_pem_x509_certificate(file.read())

                # NOTE: Make sure certificate match private key
                return crt.public_key() == private_key.public_key()
    except Exception:
        return False

    return False


def generate_csr_pem(hardware_id: str) -> str:
    builder = x509.CertificateSigningRequestBuilder()
    builder = builder.subject_name(
        x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, hardware_id),
            ]
        )
    )
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    csr = builder.sign(
        algorithm=hashes.SHA512(),
        private_key=ensure_private_key(),
    )

    return csr.public_bytes(encoding=serialization.Encoding.PEM).decode(
        encoding="utf-8", errors="strict"
    )
