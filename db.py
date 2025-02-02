import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# Create a base class for our class definitions
Base = declarative_base()

# Define a model (table)
class ScreenShot(Base):
    __tablename__ = 'screenshots'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    stored_at = Column(String)
    text = Column(String) # The text extracted from the screenshot
    def __repr__(self):
        # return f"<User(name={self.name}, email={self.email})>"
        return f"<ScreenShot(created_at={self.created_at}, stored_at={self.stored_at}, text={self.text})>"

# Create an engine that stores data in the local directory's sqlite file.
engine = create_engine('sqlite:///math_ocr.db', echo=True)

# Create all tables in the engine (if they don't exist yet)
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)