from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,func
from sqlalchemy.orm import relationship
from src.data.clients.postgres_client import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    country_code = Column(String(5), nullable=False)
    phone_no = Column(String(15), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", backref="users")

    created_at = Column(DateTime(timezone=True), default=func.now())