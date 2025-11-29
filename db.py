from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# print("DATABASE_URL =", DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)

# Session
Session = sessionmaker(bind=engine)
session = Session()
