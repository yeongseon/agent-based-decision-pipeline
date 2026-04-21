from hashlib import sha256
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LICENSE_PATH = REPO_ROOT / "LICENSE"

EXPECTED_LICENSE_NAME = "Apache License"
EXPECTED_LICENSE_VERSION = "Version 2.0, January 2004"
EXPECTED_LICENSE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"


def test_license_file_exists_and_matches_canonical_apache_2_0_text() -> None:
    assert LICENSE_PATH.is_file()

    license_bytes = LICENSE_PATH.read_bytes()
    license_text = license_bytes.decode("utf-8")

    assert EXPECTED_LICENSE_NAME in license_text
    assert EXPECTED_LICENSE_VERSION in license_text
    assert sha256(license_bytes).hexdigest() == EXPECTED_LICENSE_SHA256
