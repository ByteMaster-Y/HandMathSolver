from sqlalchemy import create_engine, Table, Column
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


mysql_url = "mysql+pymysql://capstone:capstone@localhost/handwritten_db"

# 데이터베이스 엔진 생성 (커넥션 풀 설정 추가)
engine = create_engine(mysql_url, echo=True, pool_size=20, max_overflow=0)

# Session 생성 및 Base 설정
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Create SqlAlchemy Base Instance
Base = declarative_base()
Base.query = db_session.query_property()

def init_database():
    # 데이터베이스 초기화
    Base.metadata.create_all(bind=engine)
