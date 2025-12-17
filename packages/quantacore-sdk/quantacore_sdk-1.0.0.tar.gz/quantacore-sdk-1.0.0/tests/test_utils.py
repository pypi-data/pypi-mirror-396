"""
Tests for utility functions.
"""

import pytest
from quantacore import utils


class TestHexConversion:
    """Test hex encoding/decoding."""
    
    def test_to_hex(self):
        """Test bytes to hex."""
        assert utils.to_hex(b'\xde\xad\xbe\xef') == 'deadbeef'
        assert utils.to_hex(b'\x00\x01\x02') == '000102'
        assert utils.to_hex(b'') == ''
    
    def test_from_hex(self):
        """Test hex to bytes."""
        assert utils.from_hex('deadbeef') == b'\xde\xad\xbe\xef'
        assert utils.from_hex('DEADBEEF') == b'\xde\xad\xbe\xef'
        assert utils.from_hex('de ad be ef') == b'\xde\xad\xbe\xef'
        assert utils.from_hex('') == b''
    
    def test_roundtrip(self):
        """Test hex roundtrip."""
        data = b'\x00\x01\x02\x03\x04\x05'
        assert utils.from_hex(utils.to_hex(data)) == data


class TestBase64Conversion:
    """Test Base64 encoding/decoding."""
    
    def test_to_base64(self):
        """Test bytes to Base64."""
        assert utils.to_base64(b'Hello') == 'SGVsbG8='
    
    def test_from_base64(self):
        """Test Base64 to bytes."""
        assert utils.from_base64('SGVsbG8=') == b'Hello'
    
    def test_roundtrip(self):
        """Test Base64 roundtrip."""
        data = b'\x00\x01\x02\x03\x04\x05'
        assert utils.from_base64(utils.to_base64(data)) == data


class TestBase64UrlConversion:
    """Test URL-safe Base64 encoding/decoding."""
    
    def test_to_base64url(self):
        """Test bytes to URL-safe Base64."""
        # URL-safe base64 uses - and _ instead of + and /
        result = utils.to_base64url(b'\xfb\xff')
        assert '+' not in result
        assert '/' not in result
        assert '=' not in result
    
    def test_roundtrip(self):
        """Test URL-safe Base64 roundtrip."""
        data = b'\x00\x01\x02\x03\xfb\xff'
        assert utils.from_base64url(utils.to_base64url(data)) == data


class TestSecureOperations:
    """Test secure operations."""
    
    def test_secure_zero(self):
        """Test secure zeroing."""
        buf = bytearray(b'secret data')
        utils.secure_zero(buf)
        assert buf == bytearray(len(buf))
    
    def test_secure_compare_equal(self):
        """Test constant-time comparison of equal values."""
        assert utils.secure_compare(b'test', b'test') is True
        assert utils.secure_compare(b'', b'') is True
    
    def test_secure_compare_not_equal(self):
        """Test constant-time comparison of unequal values."""
        assert utils.secure_compare(b'test', b'test!') is False
        assert utils.secure_compare(b'test', b'tset') is False


class TestByteOperations:
    """Test byte manipulation utilities."""
    
    def test_concat(self):
        """Test byte concatenation."""
        assert utils.concat(b'a', b'b', b'c') == b'abc'
        assert utils.concat() == b''
        assert utils.concat(b'single') == b'single'
    
    def test_copy(self):
        """Test byte copying."""
        original = b'data'
        copy = utils.copy(original)
        assert copy == original
        assert copy is not original
    
    def test_slice_bytes(self):
        """Test byte slicing."""
        data = b'0123456789'
        assert utils.slice_bytes(data, 0, 5) == b'01234'
        assert utils.slice_bytes(data, 5, 5) == b'56789'
        assert utils.slice_bytes(data, 0, 0) == b''
    
    def test_xor_bytes(self):
        """Test XOR operation."""
        a = b'\x00\xff\xaa'
        b = b'\xff\xff\x55'
        assert utils.xor_bytes(a, b) == b'\xff\x00\xff'
    
    def test_xor_bytes_length_mismatch(self):
        """Test XOR with mismatched lengths."""
        with pytest.raises(ValueError):
            utils.xor_bytes(b'abc', b'ab')


class TestPadding:
    """Test PKCS#7 padding."""
    
    def test_pad_pkcs7(self):
        """Test PKCS#7 padding."""
        assert utils.pad_pkcs7(b'', 16) == bytes([16] * 16)
        assert utils.pad_pkcs7(b'a', 16) == b'a' + bytes([15] * 15)
        assert utils.pad_pkcs7(b'a' * 16, 16) == b'a' * 16 + bytes([16] * 16)
    
    def test_unpad_pkcs7(self):
        """Test PKCS#7 unpadding."""
        assert utils.unpad_pkcs7(bytes([16] * 16)) == b''
        assert utils.unpad_pkcs7(b'a' + bytes([15] * 15)) == b'a'
    
    def test_unpad_invalid(self):
        """Test invalid padding detection."""
        with pytest.raises(ValueError):
            utils.unpad_pkcs7(b'')
        with pytest.raises(ValueError):
            utils.unpad_pkcs7(b'\x00')


class TestIntConversion:
    """Test integer/bytes conversion."""
    
    def test_int_to_bytes(self):
        """Test integer to bytes."""
        assert utils.int_to_bytes(256, 2) == b'\x01\x00'
        assert utils.int_to_bytes(256, 2, 'little') == b'\x00\x01'
    
    def test_bytes_to_int(self):
        """Test bytes to integer."""
        assert utils.bytes_to_int(b'\x01\x00') == 256
        assert utils.bytes_to_int(b'\x00\x01', 'little') == 256