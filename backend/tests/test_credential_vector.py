import base64
import hashlib
import unittest


class CredentialVectorTests(unittest.TestCase):
    def test_pbkdf2_sha256_credential_vector_matches_worker_contract(self):
        salt=bytes.fromhex('00112233445566778899aabbccddeeff')
        derived=hashlib.pbkdf2_hmac('sha256',b'AIOps-Academy vector password',salt,600_000,32)
        encoded=base64.urlsafe_b64encode(derived).rstrip(b'=').decode('ascii')
        self.assertEqual(encoded,'zAhH72rWsTArKoEnyqwUzO9ZOGD1CIzAeyhM0LN4Jj8')
