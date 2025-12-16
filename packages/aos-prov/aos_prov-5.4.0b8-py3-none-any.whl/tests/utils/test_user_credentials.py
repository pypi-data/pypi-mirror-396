#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import tempfile
import unittest

import pytest

from aos_prov.utils.errors import UserCredentialsError
from aos_prov.utils.user_credentials import TempCredentials, UserCredentials
from cryptography.hazmat.primitives._serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from tests.fixtures import (
    generate_ca_key_and_cert,
    generate_test_key_certificate,
    key_cert_to_pkcs12,
)


def test_context_management():
    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)

    cert_pem_bytes = cert.public_bytes(encoding=Encoding.PEM)

    private_key_pem_bytes = key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    with TempCredentials(cert_pem_bytes, private_key_pem_bytes, None, None) as temp_creds:
        assert temp_creds.cert_file_name is not None
        assert temp_creds.key_file_name is not None


def test_user_cered_create_with_pkcs12(tmp_path):
    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)
    pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

    temp_cert = tmp_path / "cert_file.p12"
    temp_cert.write_bytes(pkcs_12_cert)
    uc = UserCredentials(str(temp_cert.resolve()))

    uc.cert_type = 'type1'
    assert uc.cert_type == 'type1'

    uc.certificate = 'some cert 1'
    assert uc.certificate == 'some cert 1'

    uc.csr = 'csr'
    assert uc.csr == 'csr'

    assert uc.cloud_url == 'developer.test.local'
    assert uc.user_credentials is not None


def test_file_not_found():
    with pytest.raises(UserCredentialsError) as exc:
        UserCredentials('fake_pkcs12')

    assert str(exc.value) == 'PKCS12 key: fake_pkcs12 not found.'
