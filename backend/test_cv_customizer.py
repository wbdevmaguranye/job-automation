from utils.cv_customizer import (
    generate_cv,
    extract_relevant_skills,
    PREDEFINED_CATEGORIES,
)
from database import get_connection
from tqdm import tqdm
import boto3
from dotenv import load_dotenv
import os
from botocore.exceptions import NoCredentialsError

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
S3_BUCKET = os.getenv("AWS_S3_BUCKET")
S3_REGION = os.getenv("AWS_REGION")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)

SKILL_MATCH_THRESHOLD = float(os.getenv("SKILL_MATCH_THRESHOLD", 50.0))  # Default: 50%

def calculate_skill_match_level(matched_skills):
    """
    Determine the match level: High, Average, Low, or No Match.
    """
    categories_with_matches = sum(1 for skills in matched_skills.values() if skills)

    if categories_with_matches >= 6:
        return "High Match"
    elif categories_with_matches >= 4:
        return "Average Match"
    elif categories_with_matches >= 2:
        return "Low Match"
    else:
        return "No Match"

def get_all_jobs():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM jobs")
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def update_analytics_table(skill_match_level, location):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO analytics (skill_match_level, location, count)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE count = count + 1
            """,
            (skill_match_level, location)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def save_skill_match_to_db(job_id, skill_match_level, location):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE jobs
            SET skill_match_level = %s
            WHERE id = %s
            """,
            (skill_match_level, job_id),
        )
        update_analytics_table(skill_match_level, location)
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def save_cv_to_s3_and_database(job_id, docx_path):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        file_name = f"job_{job_id}_cv.docx"
        with open(docx_path, "rb") as docx_file:
            s3.upload_fileobj(
                docx_file,
                S3_BUCKET,
                file_name,
                ExtraArgs={"ACL": "private", "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
            )
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"
        cursor.execute(
            """
            INSERT INTO customized_cvs (job_id, file_url, customization_status)
            VALUES (%s, %s, 'success')
            """,
            (job_id, file_url),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def is_cv_saved(job_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM customized_cvs WHERE job_id = %s", (job_id,))
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()
        connection.close()

def process_all_jobs():
    output_dir = os.path.abspath("backend/static/customized_cvs")
    os.makedirs(output_dir, exist_ok=True)
    jobs = get_all_jobs()

    for job in tqdm(jobs, desc="Processing jobs"):
        try:
            job_id = job["id"]
            title = job.get("title", "N/A")
            description = job.get("description", "")
            location = job.get("location", "Unknown")

            matched_skills = extract_relevant_skills(description, PREDEFINED_CATEGORIES)

            skill_match_level = calculate_skill_match_level(matched_skills)

            save_skill_match_to_db(job_id, skill_match_level, location)

            if skill_match_level == "No Match":
                print(f"Job ID {job_id} - {title}: {skill_match_level}. Skipping customization.")
                continue

            if is_cv_saved(job_id):
                print(f"Job ID {job_id} - {title}: CV already exists. Skipping.")
                continue

            template_type = "devops" if any(matched_skills[category] for category in PREDEFINED_CATEGORIES) else "frontend"

            if template_type == "frontend":
                print(f"Job ID {job_id} - {title}: No matching skills found. Skipping customization.")
                continue

            customized_cv_path = generate_cv(job, template_type, output_dir)

            save_cv_to_s3_and_database(job_id, customized_cv_path)

        except Exception as e:
            print(f"Error processing job ID {job_id}: {e}")

if __name__ == "__main__":
    process_all_jobs()
