from sqlalchemy import create_engine
from sensor import *

if __name__ == "__main__":
    engine = create_engine("sqlite:///db.sqlite3", echo=True)
    Base.metadata.create_all(engine)
