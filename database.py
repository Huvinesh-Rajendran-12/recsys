from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()


def connect_to_db():
    """Connect to the PostgreSQL database server"""
    # create a connection to the PostgreSQL database
    host = os.getenv("POSTGRES_HOST")
    print(host)
    database = os.getenv("POSTGRES_DB")
    print(database)
    user = os.getenv("POSTGRES_USER")
    print(user)
    password = os.getenv("POSTGRES_PASS")
    print(password)
    port = os.getenv("POSTGRES_PORT")
    print(port)
    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
    print(url)
    conn = create_engine(url)
    connection = conn.connect()
    return connection


def get_user_data(userId: int):
    """Get user data from the PostgreSQL database"""
    conn = connect_to_db()
    user = conn.execute(text(f"SELECT id, gender, date_of_birth  FROM users WHERE id = :id"), {'id': userId}).one()
    allergy = conn.execute(text(f"SELECT name FROM allergies  WHERE id = :id order by created_at desc limit 1"), {'id': userId}).one()
    gender = user[1]
    date_of_birth = user[2]
    allergy = allergy[0]
    return gender, date_of_birth, allergy
