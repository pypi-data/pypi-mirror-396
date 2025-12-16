"""Type stubs for sarhash module"""

__version__: str

class PasswordStrength:
    """Password strength assessment result"""

    score: int
    feedback: list[str]

    def __init__(self, score: int, feedback: list[str]) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def is_strong(self) -> bool:
        """Returns True if password is considered strong (score >= 3)"""
        ...

def hash_password(password: str) -> str:
    """
    Hash a password using the default algorithm.

    Args:
        password: The password to hash

    Returns:
        The hashed password as a string in PHC format

    Raises:
        ValueError: If hashing fails
    """
    ...

def verify_password(password: str, hash: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password: The password to verify
        hash: The hash to verify against

    Returns:
        True if the password matches the hash, False otherwise

    Raises:
        ValueError: If the hash format is invalid
    """
    ...

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
    """
    ...

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
    """
    ...
