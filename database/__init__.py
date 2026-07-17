from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Тип бд которые мв используем
SQL_DATABASE = 'sqlite:///data.db'

# Создаем бд
engine = create_engine(SQL_DATABASE)


# Подключаем к бд
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
