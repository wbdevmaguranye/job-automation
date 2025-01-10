from dotenv import load_dotenv
import os
import mysql.connector

# Load environment variables
load_dotenv()

# Retrieve database credentials
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Function to get a new connection
def get_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Create Tables (Optional for setup scripts)
if __name__ == "__main__":
    connection = get_connection()
    cursor = connection.cursor()

    # Create Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE,
            password VARCHAR(255)
        );
    """)

    # Create Jobs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            company VARCHAR(255) NOT NULL,
            url VARCHAR(255) NOT NULL,
            description TEXT,
            date_posted DATE
        );
    """)

    # Alter the Jobs table to add new columns
    alter_statements = [
        "ALTER TABLE Jobs ADD COLUMN location VARCHAR(255)",
        "ALTER TABLE Jobs ADD COLUMN benefits TEXT",
        "ALTER TABLE Jobs ADD COLUMN schedule VARCHAR(255)",
        "ALTER TABLE Jobs ADD COLUMN application_questions TEXT",
        "ALTER TABLE Jobs ADD COLUMN work_authorisation VARCHAR(255)"
    ]

    for statement in alter_statements:
        try:
            cursor.execute(statement)
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print(f"Column already exists: {statement}")
            else:
                print(f"Error altering table: {e}")

    # Create Applications Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Applications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id INT NOT NULL,
            date_applied DATE NOT NULL,
            status VARCHAR(50) DEFAULT 'Pending',
            cv_version VARCHAR(255),
            FOREIGN KEY (job_id) REFERENCES Jobs(id)
        );
    """)

    # Commit changes and close connection
    connection.commit()
    cursor.close()
    connection.close()

    print("Database and tables created successfully!")
