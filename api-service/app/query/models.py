from app.data import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime

class Query(Base):
    __tablename__= "query"

    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    rtsp_src: Mapped[int]=mapped_column(String)
    status: Mapped[int]=mapped_column(String)
    created_at: Mapped[int]=mapped_column(DateTime)
