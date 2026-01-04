"""
Authentication utilities for LogShackBaby
Handles password hashing, MFA, and API key management
"""
import bcrypt
import pyotp
import secrets
import qrcode
import io
import base64
from datetime import datetime
from models import db, User, APIKey


class AuthManager:
    """Manage user authentication, MFA, and API keys"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def generate_mfa_secret():
        """Generate a new TOTP secret for MFA"""
        return pyotp.random_base32()
    
    @staticmethod
    def verify_mfa_token(secret, token):
        """Verify a TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 1 period before/after
    
    @staticmethod
    def generate_qr_code(callsign, secret):
        """
        Generate QR code for MFA setup
        
        Returns:
            Base64 encoded PNG image
        """
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=callsign,
            issuer_name='LogShackBaby Amateur Radio'
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def generate_api_key():
        """
        Generate a new API key
        
        Returns:
            Tuple of (full_key, key_hash, key_prefix)
        """
        # Generate 32-byte random key
        key = secrets.token_urlsafe(32)
        
        # Hash for storage
        key_hash = bcrypt.hashpw(key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Store prefix for identification
        key_prefix = key[:8]
        
        return key, key_hash, key_prefix
    
    @staticmethod
    def verify_api_key(provided_key):
        """
        Verify an API key and return the associated user
        
        Args:
            provided_key: The API key to verify
            
        Returns:
            User object if valid, None otherwise
        """
        # Get prefix to narrow search
        key_prefix = provided_key[:8]
        
        # Find potential matching keys
        api_keys = APIKey.query.filter_by(
            key_prefix=key_prefix,
            is_active=True
        ).all()
        
        # Check each potential match
        for api_key in api_keys:
            if bcrypt.checkpw(provided_key.encode('utf-8'), api_key.key_hash.encode('utf-8')):
                # Update last used timestamp
                api_key.last_used = datetime.utcnow()
                db.session.commit()
                
                return api_key.user
        
        return None
    
    @staticmethod
    def create_user(callsign, email, password):
        """
        Create a new user
        
        Args:
            callsign: User's amateur radio callsign
            email: User's email address
            password: User's password (will be hashed)
            
        Returns:
            Tuple of (user, error_message)
        """
        # Validate callsign format (basic validation)
        callsign = callsign.upper().strip()
        if not callsign or len(callsign) < 3:
            return None, "Invalid callsign format"
        
        # Check if user exists
        if User.query.filter_by(callsign=callsign).first():
            return None, "Callsign already registered"
        
        if User.query.filter_by(email=email).first():
            return None, "Email already registered"
        
        # Create user
        user = User(
            callsign=callsign,
            email=email,
            password_hash=AuthManager.hash_password(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def authenticate_user(callsign, password):
        """
        Authenticate a user with callsign and password
        
        Args:
            callsign: User's callsign
            password: User's password
            
        Returns:
            User object if authenticated, None otherwise
        """
        user = User.query.filter_by(callsign=callsign.upper(), is_active=True).first()
        
        if not user:
            return None
        
        if not AuthManager.verify_password(password, user.password_hash):
            return None
        
        return user
