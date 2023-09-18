import os
import time
from fastapi import FastAPI, Request
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Retrieve environment variables
POSTGRESQL_ADDON_URI = os.environ.get("POSTGRESQL_ADDON_URI", "postgresql://user:password@db/test_db")

# Configure the database
DATABASE_URL = POSTGRESQL_ADDON_URI
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database model
class Counter(Base):
    __tablename__ = 'counter'
    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, default=0)

# Database initialization flag
db_initialized = False

def initialize_db(retry_count=5, delay=5):
    global db_initialized
    if not db_initialized:
        attempts = 0
        while attempts < retry_count:
            try:
                Base.metadata.create_all(bind=engine)
                db_initialized = True
                print("Database initialized.")
                break
            except Exception as e:
                print(f"Error initializing the database: {e}")
                attempts += 1
                print(f"Attempt {attempts} failed. Retrying in {delay} seconds.")
                time.sleep(delay)
        if attempts == retry_count:
            print("Failed to initialize the database after multiple attempts.")

# Create a FastAPI instance
app = FastAPI()

# Middleware to initialize the database
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    initialize_db()
    response = await call_next(request)
    return response

# Function to increment the counter
def increment_field():
    db = SessionLocal()
    counter = db.query(Counter).first()
    if counter is None:
        counter = Counter(count=1)
        db.add(counter)
    else:
        counter.count += 1
    db.commit()
    db.refresh(counter)
    db.close()
    return counter.count

# Routes
@app.get("/")
def hello_world():
    return {"Hello World!"}

@app.get("/increment/")
def read_root():
    count = increment_field()
    return {"message": f"Field incremented in the database. New value: {count}"}
