from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """用户注册请求模型"""
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """令牌数据模型"""
    email: Optional[str] = None 