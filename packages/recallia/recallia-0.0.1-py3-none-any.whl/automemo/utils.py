import hashlib
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 for a file."""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()
