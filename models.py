import bcrypt
import psycopg2
from typing import Optional, Tuple
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
FOOD_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


def connect_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL)


def create_users_table():
    """Create tables if they don't exist."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    firstname VARCHAR(50),
                    lastname VARCHAR(50),
                    dob DATE,
                    gender CHAR(1),
                    email VARCHAR(100) UNIQUE,
                    password TEXT,
                    is_admin TEXT
                );
            """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS nutrition (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    food_name VARCHAR(100),
                    calories FLOAT,
                    protein FLOAT,
                    carbohydrates FLOAT,
                    fat FLOAT,
                    consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )
            conn.commit()


def hash_password(plain_text_password: str) -> str:
    """Hash the user's password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_text_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def check_user_credentials(email: str, plain_password: str) -> Tuple[bool, Optional[dict]]:
    """Verify user credentials and return user details if successful."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT firstname, lastname, password, id, is_admin FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            if result:
                print(result)
                firstname, lastname, stored_password, id, is_admin = result[0], result[1], bytes(result[2], encoding='utf8'), result[3], result[4]
                # Compare hashed password with the plain password
                if bcrypt.checkpw(plain_password.encode("utf-8"), stored_password):
                    return True, {"firstname": firstname, "lastname": lastname, "id": id, "is_admin": is_admin}
    return False, None


def add_user(firstname: str, lastname: str, dob: str, gender: str, email: str, password: str):
    """Add a new user to the Users table."""
    hashed_password = hash_password(password)
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (firstname, lastname, dob, gender, email, password)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (firstname, lastname, dob, gender, email, hashed_password),
            )
            conn.commit()
    return check_user_credentials(email, password)


def add_nutrition_entry(user_id: int, food_name: str, calories: float, protein: float, carbohydrates: float, fat: float):
    """Add a new nutrition entry to the Nutrition table."""
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO nutrition (user_id, food_name, calories, protein, carbohydrates, fat)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, food_name, calories, protein, carbohydrates, fat),
                )
                conn.commit()
    except psycopg2.Error as e:
        print(f"Error adding nutrition entry: {e}")
        raise


def get_nutrition_data(query: str, params: tuple) -> list:
    """Execute the provided query and return the fetched data."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            data = cur.fetchall()
            return data
