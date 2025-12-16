import hashlib
import re
from pathlib import Path

from loguru import logger


def calculate_sha256(file_path: str) -> str:
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"File '{file_path}' does not exist.")
        raise FileNotFoundError(file_path)

    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class ChecksumNotFoundInFile(Exception):
    pass


def get_checksum_from_file(checksum_file_path: str, file_name: str) -> str | None:
    checksum_file = Path(checksum_file_path)

    if not checksum_file.exists():
        logger.error(f"File '{checksum_file}' does not exist.")
        raise FileNotFoundError(checksum_file)

    # Ubuntu/Debian style: "<hash>  *<filename>"
    ubuntu_re = re.compile(r"^([a-f0-9]{64})\s+\*?(.+)$", re.IGNORECASE)

    # Rocky/FreeBSD style: "SHA256 (<filename>) = <hash>"
    rocky_re = re.compile(r"^sha256\s*\((.+)\)\s*=\s*([a-f0-9]{64})$", re.IGNORECASE)

    with checksum_file.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            m = ubuntu_re.match(line)
            if m:
                sha256_hash, current_file_name = m.groups()
                if current_file_name == file_name:
                    return sha256_hash
                continue

            m = rocky_re.match(line)
            if m:
                current_file_name, sha256_hash = m.groups()
                if current_file_name == file_name:
                    return sha256_hash

    logger.error(
        f"No matching checksum entry found for {file_name} in {checksum_file_path}."
    )
    raise ChecksumNotFoundInFile(checksum_file_path)
