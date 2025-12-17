"""
Tests for Digital Signature operations.
"""

import pytest
import quantacore
from quantacore import SignAlgorithm


class TestSign:
    """Test signature operations."""
    
    def test_generate_keypair_44(self, sign):
        """Test ML-DSA-44 key generation."""
        with sign.generate_keypair(SignAlgorithm.ML_DSA_44) as kp:
            assert kp.public_key is not None
            assert kp.secret_key is not None
            assert len(kp.public_key) == SignAlgorithm.ML_DSA_44.public_key_size
            assert len(kp.secret_key) == SignAlgorithm.ML_DSA_44.secret_key_size
    
    def test_generate_keypair_65(self, sign):
        """Test ML-DSA-65 key generation."""
        with sign.generate_keypair(SignAlgorithm.ML_DSA_65) as kp:
            assert kp.public_key is not None
            assert kp.secret_key is not None
            assert len(kp.public_key) == SignAlgorithm.ML_DSA_65.public_key_size
            assert len(kp.secret_key) == SignAlgorithm.ML_DSA_65.secret_key_size
    
    def test_sign_verify(self, sign):
        """Test signing and verification."""
        message = b"Test message for signing"
        
        with sign.generate_keypair(SignAlgorithm.ML_DSA_65) as kp:
            # Sign
            signature = sign.sign(kp.secret_key, message, SignAlgorithm.ML_DSA_65)
            assert signature is not None
            assert len(signature) > 0
            
            # Verify
            valid = sign.verify(kp.public_key, message, signature, SignAlgorithm.ML_DSA_65)
            assert valid is True
    
    def test_sign_verify_string(self, sign):
        """Test signing string messages."""
        message = "Hello, World!"
        
        with sign.generate_keypair_65() as kp:
            signature = sign.sign_65(kp.secret_key, message)
            valid = sign.verify_65(kp.public_key, message, signature)
            assert valid is True
    
    def test_verify_invalid(self, sign):
        """Test that invalid signatures are rejected."""
        message = b"Original message"
        modified = b"Modified message"
        
        with sign.generate_keypair_65() as kp:
            signature = sign.sign_65(kp.secret_key, message)
            
            # Verification with wrong message should fail
            valid = sign.verify_65(kp.public_key, modified, signature)
            assert valid is False
    
    def test_verify_or_raise(self, sign):
        """Test verify_or_raise method."""
        message = b"Test message"
        
        with sign.generate_keypair_65() as kp:
            signature = sign.sign_65(kp.secret_key, message)
            
            # Should not raise for valid signature
            sign.verify_or_raise(kp.public_key, message, signature, SignAlgorithm.ML_DSA_65)
            
            # Should raise for invalid signature
            with pytest.raises(quantacore.VerificationError):
                sign.verify_or_raise(kp.public_key, b"wrong", signature, SignAlgorithm.ML_DSA_65)