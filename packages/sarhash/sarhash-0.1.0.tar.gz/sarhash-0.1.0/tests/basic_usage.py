import sarhash


def main():
    print("Sarhash Basic Usage Example")
    print("-" * 30)

    # 1. Basic Hashing (Default Strong Algorithm)
    password = "my_secure_password"
    print(f"\nHashing password: '{password}'")
    hashed = sarhash.hash_password(password)
    print(f"Hashed: {hashed}")

    # 2. Verify Password
    print("\nVerifying password...")
    is_valid = sarhash.verify_password(password, hashed)
    print(f"Is valid: {is_valid}")  # True

    is_valid_wrong = sarhash.verify_password("wrong_password", hashed)
    print(f"Is 'wrong_password' valid: {is_valid_wrong}")  # False

    # 3. Password Strength
    print("\nChecking Password Strength:")
    weak_pass = "password123"
    strength = sarhash.check_password_strength(weak_pass)
    print(f"Password: '{weak_pass}'")
    print(f"Score: {strength.score}/4")
    print(f"Feedback: {strength.feedback}")

    strong_pass = "MyS3cure!Pass@2024"
    strength_strong = sarhash.check_password_strength(strong_pass)
    print(f"\nPassword: '{strong_pass}'")
    print(f"Score: {strength_strong.score}/4")
    print(f"Is strong: {strength_strong.is_strong}")


if __name__ == "__main__":
    main()
