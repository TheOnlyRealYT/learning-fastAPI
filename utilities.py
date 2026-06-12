from argon2 import PasswordHasher

password_context = PasswordHasher()


def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(hashed_password: str, password: str) -> bool:
    return password_context.verify(hashed_password, password)