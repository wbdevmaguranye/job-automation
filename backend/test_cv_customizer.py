import re
import os
from utils.cv_customizer import generate_cv
from database import get_connection
from tqdm import tqdm

def ensure_directory_exists(directory_path):
    """
    Ensure the directory exists; if not, create it.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def sanitize_filename(filename):
    """
    Remove or replace invalid characters from the filename.
    """
    return re.sub(r'[<>:"/\\|?*$,]', '_', filename)

def get_all_jobs():
    """
    Fetch all jobs from the database.
    :return: List of job dictionaries.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM jobs")
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def is_cv_saved(job_id):
    """
    Check if a CV for a given job ID is already saved in the database.
    :param job_id: ID of the job.
    :return: True if a CV already exists, otherwise False.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM customized_cvs WHERE job_id = %s", (job_id,))
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()
        connection.close()

def save_cv_to_database(job_id, docx_path):
    """
    Save the customized CV DOCX content into the database.
    :param job_id: ID of the job associated with the CV.
    :param docx_path: Path to the DOCX file.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        with open(docx_path, "rb") as docx_file:
            docx_content = docx_file.read()

        cursor.execute(
            """
            INSERT INTO customized_cvs (job_id, pdf_content, customization_status)
            VALUES (%s, %s, 'success')
            ON DUPLICATE KEY UPDATE
                pdf_content = VALUES(pdf_content),
                customization_status = VALUES(customization_status),
                created_at = CURRENT_TIMESTAMP;
            """,
            (job_id, docx_content)
        )
        connection.commit()
        print(f"DOCX saved to database for job ID: {job_id}")
    except Exception as e:
        print(f"Error saving DOCX to database for job ID: {job_id} - {e}")
    finally:
        cursor.close()
        connection.close()

def process_all_jobs():
    """
    Process all jobs in the database, customize CVs, save locally, and store in the database.
    """
    # Define the directory for saving locally customized CVs
    output_dir = os.path.abspath("backend/static/customized_cvs")
    ensure_directory_exists(output_dir)

    # Fetch all jobs
    jobs = get_all_jobs()
    if not jobs:
        print("No jobs found in the database.")
        return

    # Process each job
    for job in tqdm(jobs, desc="Processing jobs"):
        try:
            job_id = job["id"]
            if is_cv_saved(job_id):
                print(f"CV already exists for job ID: {job_id}. Skipping.")
                continue

            # Determine the appropriate template type
            template_type = "devops" if "devops" in job["title"].lower() else "frontend"

            # Generate the CV locally and get the path
            customized_cv_path = generate_cv(job, template_type, output_dir)

            # Save the generated CV to the database
            save_cv_to_database(job_id, customized_cv_path)

        except Exception as e:
            print(f"Error processing job ID: {job['id']} - {e}")


if __name__ == "__main__":
    process_all_jobs()
