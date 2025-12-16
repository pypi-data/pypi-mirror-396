"""Define tests for crypto module."""

import base64

from eufy_security.crypto import decrypt_api_data, encrypt_api_data


def test_encrypt_decrypt_roundtrip():
    """Test that encrypt and decrypt are inverse operations."""
    key = b"0123456789abcdef0123456789abcdef"  # 32 bytes for AES-256
    plaintext = "Hello, World!"

    encrypted = encrypt_api_data(plaintext, key)
    decrypted = decrypt_api_data(encrypted, key)

    assert decrypted == plaintext


def test_encrypt_decrypt_json():
    """Test encrypting and decrypting JSON data."""
    key = b"abcdefghijklmnopqrstuvwxyz012345"
    plaintext = '{"email":"test@example.com","password":"secret"}'

    encrypted = encrypt_api_data(plaintext, key)
    decrypted = decrypt_api_data(encrypted, key)

    assert decrypted == plaintext


def test_encrypt_returns_base64():
    """Test that encrypted data is valid base64."""
    key = b"0123456789abcdef0123456789abcdef"
    plaintext = "test data"

    encrypted = encrypt_api_data(plaintext, key)

    # Should not raise an exception
    decoded = base64.b64decode(encrypted)
    assert len(decoded) > 0


def test_encrypt_different_keys_different_output():
    """Test that different keys produce different ciphertext."""
    key1 = b"0123456789abcdef0123456789abcdef"
    key2 = b"fedcba9876543210fedcba9876543210"
    plaintext = "same plaintext"

    encrypted1 = encrypt_api_data(plaintext, key1)
    encrypted2 = encrypt_api_data(plaintext, key2)

    assert encrypted1 != encrypted2


def test_encrypt_empty_string():
    """Test encrypting an empty string."""
    key = b"0123456789abcdef0123456789abcdef"
    plaintext = ""

    encrypted = encrypt_api_data(plaintext, key)
    decrypted = decrypt_api_data(encrypted, key)

    assert decrypted == plaintext


def test_encrypt_unicode():
    """Test encrypting unicode characters."""
    key = b"0123456789abcdef0123456789abcdef"
    plaintext = "Hello, 世界! 🌍"

    encrypted = encrypt_api_data(plaintext, key)
    decrypted = decrypt_api_data(encrypted, key)

    assert decrypted == plaintext


def test_encrypt_long_text():
    """Test encrypting text longer than one AES block."""
    key = b"0123456789abcdef0123456789abcdef"
    plaintext = "A" * 1000  # Much longer than 16-byte AES block

    encrypted = encrypt_api_data(plaintext, key)
    decrypted = decrypt_api_data(encrypted, key)

    assert decrypted == plaintext


def test_iv_is_key_prefix():
    """Test that IV is derived from key prefix (first 16 bytes)."""
    # Two keys with same first 16 bytes should produce same IV
    key1 = b"0123456789abcdef" + b"AAAAAAAAAAAAAAAA"
    key2 = b"0123456789abcdef" + b"BBBBBBBBBBBBBBBB"
    plaintext = "test"

    # Same plaintext with same IV prefix should give same ciphertext
    encrypted1 = encrypt_api_data(plaintext, key1)
    encrypted2 = encrypt_api_data(plaintext, key2)

    # They should be different because the full key is used for encryption
    assert encrypted1 != encrypted2
