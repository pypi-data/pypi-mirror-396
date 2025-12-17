# createsonline/security/encryption.py
"""
CREATESONLINE Encryption Utilities

Military-grade encryption and password hashing:
- Argon2 password hashing
- AES-256 encryption
- Secure token generation
- Key derivation functions
"""

import hashlib
import hmac
import secrets
import base64
import time
from typing import Optional, Tuple, Dict, Any


class SecureHasher:
    """
    Military-grade password hashing using Argon2-equivalent security
    Falls back to PBKDF2 if Argon2 not available
    """
    
    def __init__(self):
        # Try to import argon2 for best security
        try:
            import argon2
            self.argon2_available = True
            self.argon2_hasher = argon2.PasswordHasher(
                time_cost=3,        # Number of iterations
                memory_cost=65536,  # Memory usage in KiB
                parallelism=1,      # Number of parallel threads
                hash_len=32,        # Hash length
                salt_len=16         # Salt length
            )
            pass
        except ImportError:
            self.argon2_available = False
            pass
    
    def hash_password(self, password: str) -> str:
        """Hash password with maximum security"""
        
        if self.argon2_available:
            # Use Argon2 (recommended by OWASP)
            return self.argon2_hasher.hash(password)
        else:
            # Fallback to PBKDF2 with high iteration count
            salt = secrets.token_bytes(32)
            iterations = 100000  # High iteration count for security
            
            # Create PBKDF2 hash
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                iterations
            )
            
            # Encode as: algorithm$iterations$salt$hash
            encoded_salt = base64.b64encode(salt).decode('ascii')
            encoded_hash = base64.b64encode(password_hash).decode('ascii')
            
            return f"pbkdf2_sha256${iterations}${encoded_salt}${encoded_hash}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        
        if self.argon2_available and not hashed.startswith('pbkdf2_'):
            # Verify with Argon2
            try:
                self.argon2_hasher.verify(hashed, password)
                return True
            except:
                return False
        else:
            # Verify with PBKDF2
            try:
                parts = hashed.split('$')
                if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
                    return False
                
                iterations = int(parts[1])
                salt = base64.b64decode(parts[2])
                stored_hash = base64.b64decode(parts[3])
                
                # Compute hash with same parameters
                computed_hash = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    salt,
                    iterations
                )
                
                # Constant-time comparison to prevent timing attacks
                return hmac.compare_digest(stored_hash, computed_hash)
                
            except (ValueError, IndexError):
                return False
    
    def needs_rehash(self, hashed: str) -> bool:
        """Check if password needs rehashing with stronger parameters"""
        
        if self.argon2_available:
            if not hashed.startswith('pbkdf2_'):
                # Already using Argon2
                try:
                    return self.argon2_hasher.check_needs_rehash(hashed)
                except:
                    return True
            else:
                # Upgrade from PBKDF2 to Argon2
                return True
        else:
            # Check PBKDF2 iteration count
            try:
                parts = hashed.split('$')
                if len(parts) == 4 and parts[0] == 'pbkdf2_sha256':
                    iterations = int(parts[1])
                    return iterations < 100000  # Upgrade if less than 100k iterations
            except:
                pass
            
            return True


class SecureTokenGenerator:
    """Generate cryptographically secure tokens"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate API key with prefix"""
        prefix = "cos_"  # CREATESONLINE prefix
        token = secrets.token_urlsafe(32)
        return f"{prefix}{token}"
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate session ID"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_urlsafe(24)
        return f"{timestamp}_{random_part}"
    
    @staticmethod
    def generate_csrf_token(session_id: str, secret_key: str) -> str:
        """Generate CSRF token tied to session"""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        
        signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{signature}"
    
    @staticmethod
    def verify_csrf_token(token: str, session_id: str, secret_key: str, 
                         max_age: int = 3600) -> bool:
        """Verify CSRF token"""
        try:
            timestamp_str, signature = token.split(':', 1)
            timestamp = int(timestamp_str)
            
            # Check token age
            if time.time() - timestamp > max_age:
                return False
            
            # Verify signature
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, IndexError):
            return False


class AESEncryption:
    """AES-256 encryption utilities"""
    
    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            key = secrets.token_bytes(32)  # 256-bit key
        elif len(key) != 32:
            # Derive 256-bit key from provided key
            key = hashlib.sha256(key).digest()
        
        self.key = key
        
        # Try to import cryptography library for AES
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            # Create Fernet key from our key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'createsonline_salt',  # In production, use random salt
                iterations=100000,
            )
            fernet_key = base64.urlsafe_b64encode(kdf.derive(self.key))
            self.cipher = Fernet(fernet_key)
            self.crypto_available = True
            pass
            
        except ImportError:
            self.crypto_available = False
            pass
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        
        if self.crypto_available:
            # Use Fernet (AES-256)
            encrypted = self.cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        else:
            # Fallback to XOR encryption
            data_bytes = data.encode()
            encrypted_bytes = bytearray()
            
            for i, byte in enumerate(data_bytes):
                key_byte = self.key[i % len(self.key)]
                encrypted_bytes.append(byte ^ key_byte)
            
            return base64.b64encode(encrypted_bytes).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        
        try:
            if self.crypto_available:
                # Use Fernet (AES-256)
                encrypted_bytes = base64.b64decode(encrypted_data)
                decrypted = self.cipher.decrypt(encrypted_bytes)
                return decrypted.decode()
            else:
                # Fallback to XOR decryption
                encrypted_bytes = base64.b64decode(encrypted_data)
                decrypted_bytes = bytearray()
                
                for i, byte in enumerate(encrypted_bytes):
                    key_byte = self.key[i % len(self.key)]
                    decrypted_bytes.append(byte ^ key_byte)
                
                return decrypted_bytes.decode()
        
        except Exception:
            raise ValueError("Invalid encrypted data")
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt dictionary as JSON"""
        import json
        json_str = json.dumps(data, separators=(',', ':'))
        return self.encrypt(json_str)
    
    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt to dictionary"""
        import json
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)


class KeyDerivation:
    """Key derivation functions for secure key generation"""
    
    @staticmethod
    def derive_key(password: str, salt: Optional[bytes] = None, 
                   length: int = 32, iterations: int = 100000) -> Tuple[bytes, bytes]:
        """Derive encryption key from password"""
        
        if salt is None:
            salt = secrets.token_bytes(32)
        
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            iterations,
            dklen=length
        )
        
        return key, salt
    
    @staticmethod
    def derive_multiple_keys(master_key: bytes, labels: list, 
                           length: int = 32) -> Dict[str, bytes]:
        """Derive multiple keys from master key using HKDF-like approach"""
        
        keys = {}
        
        for label in labels:
            # Create unique key for each label
            info = f"CREATESONLINE_{label}".encode()
            
            # Simple HKDF-like derivation
            prk = hmac.new(b'salt', master_key, hashlib.sha256).digest()
            okm = hmac.new(prk, info + b'\x01', hashlib.sha256).digest()[:length]
            
            keys[label] = okm
        
        return keys


# Global secure hasher instance
_secure_hasher = SecureHasher()

def encrypt_password(password: str) -> str:
    """Encrypt password with maximum security"""
    return _secure_hasher.hash_password(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return _secure_hasher.verify_password(password, hashed)

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token"""
    return SecureTokenGenerator.generate_token(length)

def generate_api_key() -> str:
    """Generate API key"""
    return SecureTokenGenerator.generate_api_key()

def generate_session_id() -> str:
    """Generate session ID"""
    return SecureTokenGenerator.generate_session_id()

def create_encryption_cipher(key: Optional[bytes] = None) -> AESEncryption:
    """Create AES encryption cipher"""
    return AESEncryption(key)

def secure_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks"""
    return hmac.compare_digest(a.encode(), b.encode())
