"""
Sarhash - Fast and secure password hashing library powered by Rust

This module provides high-performance password hashing using industry-standard
algorithms: Argon2, bcrypt, and scrypt.
"""

import re

# Import the Rust extension module functions
# The Rust module is compiled as '_rusthash' and provides hash_password and verify_password
try:
    from sarhash._sarhash import hash_password as _rust_hash_password
    from sarhash._sarhash import verify_password as _rust_verify_password
except ImportError:
    # If running from source without build, provide helpful error
    raise ImportError(
        "Rust extension not found. Please build the package with 'maturin develop'"
    )

__version__ = "0.1.0"
__all__ = [
    "hash_password",
    "verify_password",
    "hash_multiple",
]

# Type alias for supported algorithms
# HashAlgorithm = Literal["argon2", "bcrypt", "scrypt"]


class PasswordStrength:
    """Password strength assessment result"""

    def __init__(self, score: int, feedback: list[str]):
        self.score = score  # 0-4 (weak to strong)
        self.feedback = feedback

    def __repr__(self) -> str:
        strength_labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
        return f"PasswordStrength(score={self.score}, strength='{strength_labels[self.score]}')"

    @property
    def is_strong(self) -> bool:
        """Returns True if password is considered strong (score >= 3)"""
        return self.score >= 3


def hash_password(password: str) -> str:
    """
    Hash a password using the default algorithm.

    Args:
        password: The password to hash

    Returns:
        The hashed password as a string in PHC format

    Raises:
        ValueError: If hashing fails

    Examples:
        >>> hashed = hash_password("my_password")
        >>> hashed.startswith("$argon2")
        True
    """
    if not password:
        raise ValueError("Password cannot be empty")

    return _rust_hash_password(password)


def verify_password(password: str, hash: str) -> bool:
    """
    Verify a password against a hash.

    Automatically detects the algorithm from the hash format.

    Args:
        password: The password to verify
        hash: The hash to verify against

    Returns:
        True if the password matches the hash, False otherwise

    Raises:
        ValueError: If the hash format is invalid

    Examples:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    if not password:
        return False

    if not hash:
        raise ValueError("Hash cannot be empty")

    return _rust_verify_password(password, hash)


def check_password_strength(password: str) -> PasswordStrength:
    """
    Check the strength of a password.

    Evaluates password based on:
    - Length
    - Character diversity (lowercase, uppercase, digits, special chars)
    - Common patterns

    Args:
        password: The password to check

    Returns:
        PasswordStrength object with score (0-4) and feedback

    Examples:
        >>> strength = check_password_strength("password123")
        >>> strength.score
        1
        >>> strength.is_strong
        False

        >>> strength = check_password_strength("MyS3cure!Pass@2024")
        >>> strength.is_strong
        True
    """
    score = 0
    feedback = []

    # Check length
    if len(password) < 8:
        feedback.append("Password should be at least 8 characters long")
    elif len(password) >= 12:
        score += 1
        if len(password) >= 16:
            score += 1
    else:
        score += 1

    # Check character diversity
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    diversity_count = sum([has_lower, has_upper, has_digit, has_special])

    if diversity_count >= 3:
        score += 1
    if diversity_count == 4:
        score += 1

    if not has_lower:
        feedback.append("Add lowercase letters")
    if not has_upper:
        feedback.append("Add uppercase letters")
    if not has_digit:
        feedback.append("Add numbers")
    if not has_special:
        feedback.append("Add special characters")

    # Check for common patterns
    common_patterns = [
        r"(.)\1{2,}",  # Repeated characters
        r"(012|123|234|345|456|567|678|789)",  # Sequential numbers
        r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",  # Sequential letters
    ]

    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            feedback.append("Avoid common patterns and sequences")
            score = max(0, score - 1)
            break

    # Common weak passwords
    weak_passwords = ["password", "12345678", "qwerty", "abc123", "letmein"]
    if password.lower() in weak_passwords:
        score = 0
        feedback.append("This is a commonly used password")

    if score >= 3 and not feedback:
        feedback.append("Strong password!")

    return PasswordStrength(min(score, 4), feedback)


def hash_multiple(passwords: list[str]) -> list[str]:
    """
    Hash multiple passwords.

    Useful for batch operations.

    Args:
        passwords: List of passwords to hash

    Returns:
        List of hashed passwords in the same order

    Raises:
        ValueError: If any password is invalid or hashing fails

    Examples:
        >>> passwords = ["pass1", "pass2", "pass3"]
        >>> hashes = hash_multiple(passwords)
        >>> len(hashes)
        3
        >>> all(h.startswith("$argon2") for h in hashes)
        True
    """
    return [hash_password(pwd) for pwd in passwords]
