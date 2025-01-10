from utils.cv_customizer import generate_cv
from database import get_connection

def get_job_from_database(job_id):
    """
    Retrieve a job from the database using the job ID.
    :param job_id: ID of the job to fetch.
    :return: Dictionary containing job details.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

# Fetch a job from the database
job_id = 7  # Replace with actual job ID
job_data = get_job_from_database(job_id)

if not job_data:
    print(f"No job found with ID {job_id}")
else:
    template_type = "devops" if "devops" in job_data['title'].lower() else "frontend"
    output_dir = "backend/static/customized_cvs"

    # Generate the customized CV
    customized_cv_path = generate_cv(job_data, template_type, output_dir)
    print(f"Customized CV saved at: {customized_cv_path}")
