import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details (from .env file)
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def create_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        if connection.is_connected():
            print("Connected to MySQL server")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")

def create_tables(connection):
    try:
        connection.database = DB_NAME
        cursor = connection.cursor()

        # Create users table (no foreign key dependencies)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE DEFAULT NULL,
            password VARCHAR(255) DEFAULT NULL
        )
        """)

        # Create jobs table (no foreign key dependencies)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            company VARCHAR(255) NOT NULL,
            url TEXT NOT NULL,
            description TEXT DEFAULT NULL,
            date_posted DATE DEFAULT NULL,
            location VARCHAR(255) DEFAULT NULL,
            benefits TEXT DEFAULT NULL,
            schedule VARCHAR(255) DEFAULT NULL,
            application_questions TEXT DEFAULT NULL,
            work_authorisation VARCHAR(255) DEFAULT NULL,
            skills_match_percentage INT DEFAULT 0,
            skill_match_level VARCHAR(20) DEFAULT 'No Match',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            skills TEXT DEFAULT NULL
        )
        """)

        # Create customized_cvs table (references jobs)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customized_cvs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id INT NOT NULL UNIQUE,
            customization_status ENUM('success', 'no_skills_matched') DEFAULT 'success',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_url VARCHAR(255) NOT NULL,
            skills_match_category ENUM('High', 'Low', 'No Match') DEFAULT 'No Match',
            skills TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
        """)

        # Create applications table (references users, jobs, customized_cvs)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            job_id INT NOT NULL,
            cv_id INT DEFAULT NULL,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('Pending', 'Submitted', 'Rejected', 'Accepted') DEFAULT 'Pending',
            feedback TEXT DEFAULT NULL,
            source VARCHAR(255) DEFAULT 'Manual',
            application_type ENUM('Direct', 'Referral', 'Internal') DEFAULT 'Direct',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (cv_id) REFERENCES customized_cvs(id)
        )
        """)

        # Create analytics table (no dependencies)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            skill_match_level ENUM('High Match', 'Average Match', 'Low Match', 'No Match') DEFAULT NULL,
            count INT NOT NULL DEFAULT 0,
            location VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)

        print("All tables created successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")


def main():
    connection = create_connection()
    if connection:
        create_database(connection)
        create_tables(connection)
        connection.close()

if __name__ == "__main__":
    main()
