from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    UserId = Column(String, primary_key=True)
    HashedPassword = Column(String)

    def __repr__(self):
        return "<User(name='%s', HashedPassword='%s')>" % (self.UserId, self.HashedPassword)

class Company(Base):
    __tablename__ = 'Company'
    CompanyId = Column(Integer, primary_key=True)
    Name = Column(String)
    StockTicker = Column(String)

    def __repr__(self):
        return "<User(CompanyId='%s', Name='%s', StockTicker=%s)>" % (self.CompanyId, self.Name, self.StockTicker)

