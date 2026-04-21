from hashlib import sha256
from pathlib import Path


def test_license_file_exists_and_matches_canonical_apache_2_0_text() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    license_path = repo_root / "LICENSE"

    assert license_path.is_file()

    license_bytes = license_path.read_bytes()
    license_text = license_bytes.decode("utf-8")

    assert "Apache License" in license_text
    assert "Version 2.0, January 2004" in license_text
    assert sha256(license_bytes).hexdigest() == "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
