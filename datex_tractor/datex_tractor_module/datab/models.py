from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base


class Issue(Base):
    __tablename__ = "issue"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(256), nullable=False)
    i_number = Column(Integer, nullable=False, index=True, unique=True)
    children = relationship("Codeblock", cascade=["delete"])

    def __repr__(self):
        return f"<Issue(i_number={self.i_number}, path={self.path})>"


class Codeblock(Base):
    __tablename__ = "codeblock"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("issue.i_number"))
    content = Column(String)
    response = Column(String)

    def __repr__(self):
        return f"<Codeblock(parent_id={self.parent_id}, content={self.content[:32]}, response={self.response[:32]})>"
