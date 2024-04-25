import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 

engine = sqlalchemy.create_engine(url="")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()