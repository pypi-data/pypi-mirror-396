import pytest
import sarhash


def test_hash_password_verify():
    password = "secure_password"
    hashed = sarhash.hash_password(password)

    # Verify hash format (should be PHC string)
    assert hashed.startswith("$argon2") or hashed.startswith("$")

    # Verify correctness
    assert sarhash.verify_password(password, hashed)
    assert not sarhash.verify_password("wrong_password", hashed)


def test_hash_password_empty_raises():
    with pytest.raises(ValueError):
        sarhash.hash_password("")


def test_verify_password_empty_raises():
    with pytest.raises(ValueError, match="Hash cannot be empty"):
        sarhash.verify_password("pass", "")


def test_check_password_strength_weak():
    strength = sarhash.check_password_strength("weak")
    assert strength.score < 3
    assert not strength.is_strong
    assert "Password should be at least 8 characters long" in strength.feedback


def test_check_password_strength_strong():
    strength = sarhash.check_password_strength("StrongP@ssw0rd!")
    assert strength.score >= 3
    assert strength.is_strong
    if strength.score == 4:
        assert "Strong password!" in strength.feedback


def test_hash_multiple():
    passwords = ["pass1", "pass2", "pass3"]
    hashes = sarhash.hash_multiple(passwords)

    assert len(hashes) == 3

    for pwd, h in zip(passwords, hashes):
        assert sarhash.verify_password(pwd, h)


def test_version():
    assert sarhash.__version__ == "0.1.0"
