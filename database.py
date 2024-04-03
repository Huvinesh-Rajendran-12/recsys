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
    users = conn.execute(text(f"SELECT id, gender  FROM users WHERE id = :id"), {'id': userId})
    consultations = conn.execute(text(f"SELECT doctor_feedback, diagnosis FROM consultations WHERE user_id = :id order by created_at desc limit 1"), {'id': userId})
    allergy = conn.execute(text(f"SELECT name FROM allergies WHERE user_id = :id order by created_at desc limit 1"), {'id': userId})
    gender = users.one()._tuple()[1] 
    consultation = consultations.one()
    allergy = allergy.one()._tuple()[0]
    diagnosis = ""
    if consultation._tuple()[0] is not None and consultation._tuple()[1] is not None:
        diagnosis = consultation._tuple()[0] + " " + consultation._tuple()[1]
    elif consultation._tuple()[0] is None:
        diagnosis = consultation._tuple()[1]
    elif consultation._tuple()[1] is None:
        diagnosis = consultation._tuple()[0] 
    return diagnosis, gender, allergy


(diagnosis, gender, allergy) = get_user_data(311)
print(diagnosis)
print(gender)
print(allergy)
