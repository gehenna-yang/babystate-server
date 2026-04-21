from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DB_URL 형식: postgresql://사용자명:비밀번호@호스트:포트/데이터베이스명
SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB 세션 의존성 (API 호출 시마다 DB 연결을 관리해줌)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()