import hashlib
import hmac
import datetime as dt
import base64
import os

class PasswordHasher:
    """
    A class that provides methods for hashing passwords using creation time as salt
    and validating password attempts against stored hashes.
    """

    @staticmethod
    def hash_password(password: str, creation_time: str = None) -> tuple:
        """
        Hash a password using the creation time as salt.
        
        Args:
            password (str): The password to hash
            creation_time (str, optional): Creation timestamp to use as salt. If None, current time is used.
        
        Returns:
            tuple: (hashed_password, creation_time_used_as_salt)
        """
        if creation_time is None:
            creation_time = dt.datetime.now().isoformat()
            
        # Convert the password and salt to bytes
        password_bytes = password.encode('utf-8')
        salt_bytes = creation_time.encode('utf-8')
        
        # Create a hash using PBKDF2 with SHA-256
        # Using 100,000 iterations for security
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password_bytes,
            salt_bytes,
            100000
        )
        
        # Return the hash encoded as base64 and the creation time
        hashed_password = base64.b64encode(key).decode('utf-8')
        return (hashed_password, creation_time)
    
    @staticmethod
    def verify_password(stored_hash: str, provided_password: str, creation_time: str) -> bool:
        """
        Verify if a provided password matches the stored hash.
        
        Args:
            stored_hash (str): The previously stored password hash
            provided_password (str): The password attempt to verify
            creation_time (str): The creation timestamp used as salt during original hashing
            
        Returns:
            bool: True if the password matches, False otherwise
        """
        # Hash the provided password using the same creation time as salt
        new_hash, _ = PasswordHasher.hash_password(provided_password, creation_time)
        
        # Compare the hashes using a constant-time comparison
        # This helps prevent timing attacks
        return hmac.compare_digest(stored_hash, new_hash)
    
#Hello

# Example usage:
if __name__ == "__main__":
    # Example of creating a new password hash
    password = "SecurePassword123"
    hashed_pwd, creation_time = PasswordHasher.hash_password(password)
    print(f"Hashed password: {hashed_pwd}")
    print(f"Creation time (salt): {creation_time}")
    
    # Example of verifying a password
    is_valid = PasswordHasher.verify_password(hashed_pwd, "SecurePassword123", creation_time)
    print(f"Password valid: {is_valid}")
    
    # Example of incorrect password
    is_valid = PasswordHasher.verify_password(hashed_pwd, "WrongPassword", creation_time)
    print(f"Wrong password valid: {is_valid}")