from sqlalchemy import Column, Integer, String, ForeignKey
from db_connect import Base
from sqlalchemy.orm import relationship


class Files(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    size = Column(Integer)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String)
    password = Column(String)
    key = Column(String)
    c_0 = Column(String)


# class UserFiles(Base):
#     __tablename__ = 'user_files'
#
#     user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
#     user = relationship("User")
#     import db_models
