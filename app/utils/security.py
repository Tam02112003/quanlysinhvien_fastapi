from passlib.context import CryptContext

# Tạo context mã hóa với bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Mã hóa mật khẩu dạng bcrypt
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    So sánh mật khẩu người dùng nhập với mật khẩu đã mã hóa
    """
    return pwd_context.verify(plain_password, hashed_password)