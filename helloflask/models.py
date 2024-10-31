from .init_db import Base
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    passwd = Column(String(256))
    nickname = Column(String(31))

    def __init__(self, email=None, passwd=None, nickname=None):
        self.email = email
        self.passwd = passwd
        self.nickname = nickname
        
    def __repr__(self):
        return f"<User(email={self.email!r}, passwd={self.passwd!r}, nickname={self.nickname!r})>"
        # 여기서 !r은 repr() 함수를 사용하여 값을 문자열로 변환하라는 의미입니다. 