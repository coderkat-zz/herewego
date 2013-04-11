from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref


# db interactions with sessions
engine = create_engine("sqlite:///news.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base() # required for sqlalchemy magics
Base.query = session.query_property()

class Stories(Base):
	__tablename__ = "stories" # store instances of this class in tbl 'stories'

	id = Column(Integer, primary_key=True)
	title = Column(String(128))
	abstract = Column(String(256))
	url = Column(String(128))

class Tags(Base):
	__tablename__ = "tags" 

	id = Column(Integer, primary_key=True)
	story_id = Column(Integer, ForeignKey("stories.id"))
	tag = Column(String(128), nullable=True)

	story = relationship("Stories", backref=backref("tags", order_by=id))


def main():
	"""For when we need to, you know, do stuff"""
	pass

if __name__ == "__main__":
	main()