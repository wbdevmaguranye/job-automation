from flask import Blueprint, request, jsonify, send_file, abort
from flask_jwt_extended import jwt_required,  get_jwt_identity
from database import get_connection
from botocore.exceptions import NoCredentialsError
import boto3
import os
import io

# Load S3 configuration
S3_BUCKET = os.getenv("AWS_S3_BUCKET")
S3_REGION = os.getenv("AWS_REGION")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize the S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)

# Define a Blueprint for job routes
jobs_bp = Blueprint('jobs', __name__)


# Existing Route: List All Jobs
@jobs_bp.route('/jobs', methods=['GET', 'POST'])
def jobs():
    if request.method == 'GET':
        # Existing GET logic to fetch jobs
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM jobs")
            jobs = cursor.fetchall()
            return jsonify(jobs), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    elif request.method == 'POST':
        # New POST logic to add a job from your web scraper
        job_data = request.get_json()

        # Extract job details from the request
        title = job_data.get('title')
        location = job_data.get('location')
        description = job_data.get('description')
        company = job_data.get('company')
        url = job_data.get('url')

        # Validate that all required fields are provided
        if not all([title, location, description, company, url]):
            return jsonify({"error": "Missing required job fields"}), 400

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO jobs (title, location, description, company, url)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, location, description, company, url))
            connection.commit()
            return jsonify({"message": "Job added successfully!"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Route: List All CVs
@jobs_bp.route('/cvs', methods=['GET'])
@jwt_required()
def get_cvs():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                c.id AS cv_id,
                c.job_id,
                c.file_url,
                c.customization_status,
                c.skills_match_category,
                c.created_at,
                j.title AS job_title,
                j.skill_match_level
            FROM 
                customized_cvs c
            JOIN 
                jobs j 
            ON 
                c.job_id = j.id
        """
        cursor.execute(query)
        cvs = cursor.fetchall()
        return jsonify(cvs), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching CVs: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()




# Route: Get a Specific CV by ID
@jobs_bp.route('/cvs/<int:cv_id>', methods=['GET'])
def get_cv_file(cv_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch the specific CV's file URL
        cursor.execute("SELECT file_url FROM customized_cvs WHERE id = %s", (cv_id,))
        cv = cursor.fetchone()

        if not cv or not cv["file_url"]:
            return jsonify({"error": "CV not found or file URL missing."}), 404

        # Extract the file name from the URL
        file_url = cv["file_url"]
        file_key = file_url.split(f"{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/")[-1]

        # Generate a presigned URL
        try:
            presigned_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': file_key},
                ExpiresIn=3600  # URL expires in 1 hour
            )
            return jsonify({"presigned_url": presigned_url}), 200
        except NoCredentialsError:
            return jsonify({"error": "AWS credentials not found"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()



# Route: Upload a CV to S3 and Update Metadata
@jobs_bp.route('/cvs/<int:cv_id>/upload', methods=['POST'])
@jwt_required()
def upload_cv_to_s3(cv_id):
    if 'cv' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['cv']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Generate a unique file name
        file_name = f"Joel_Maguranye_cv_{cv_id}_{file.filename}"

        # Upload the file to S3
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            file_name,
            ExtraArgs={'ACL': 'private', 'ContentType': file.content_type}
        )

        # Generate the file URL
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"

        # Update the database
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE customized_cvs SET file_url = %s, customization_status = 'updated' WHERE id = %s",
            (file_url, cv_id)
        )
        connection.commit()

        return jsonify({"message": "CV uploaded successfully", "file_url": file_url}), 200
    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not found"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Route: Add a New CV Metadata Record
@jobs_bp.route('/cvs', methods=['POST'])
@jwt_required()
def add_cv_metadata():
    data = request.json
    job_id = data.get("job_id")
    customization_status = data.get("customization_status", "pending")

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO customized_cvs (job_id, customization_status) VALUES (%s, %s)",
            (job_id, customization_status)
        )
        connection.commit()

        return jsonify({"message": "CV metadata added successfully!", "cv_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()



@jobs_bp.route('/dashboard/summary', methods=['GET'])
@jwt_required()
def dashboard_summary():
    try:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

       
        cursor.execute("SELECT COUNT(*) AS total_jobs FROM jobs")
        total_jobs = cursor.fetchone()["total_jobs"]

        cursor.execute("SELECT COUNT(*) AS total_applications FROM applications")
        total_applications = cursor.fetchone()["total_applications"]

        cursor.execute("SELECT COUNT(*) AS total_cvs FROM customized_cvs")
        total_cvs = cursor.fetchone()["total_cvs"]

        cursor.execute("SELECT title, company FROM jobs ORDER BY created_at DESC LIMIT 7")
        recent_jobs = cursor.fetchall()

        # Prepare the summary data
        summary = {
            "total_jobs": total_jobs,
            "total_cvs": total_cvs,
            "recent_jobs": recent_jobs,
            "total_applications": total_applications
        }

    
        return jsonify({"data": summary}), 200
    except Exception as e:
 
        return jsonify({"message": f"Failed to fetch summary: {str(e)}"}), 500
    finally:
      
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# applications
@jobs_bp.route('/applications', methods=['POST'])
@jwt_required()
def submit_application():
    """
    Submit a new application for a job.
    """
    connection = None
    cursor = None
    try:
        data = request.json
        cv_id = data.get("cv_id")
        job_id = data.get("job_id")
        source = data.get("source", "Manual")
        user_id = get_jwt_identity()

        # Validate input
        if not job_id or not cv_id:
            return jsonify({"message": "Job ID and CV ID are required"}), 400

        # Connect to the database
        connection = get_connection()
        cursor = connection.cursor()

        # Check if the provided CV exists
        cursor.execute(
            "SELECT COUNT(*) FROM customized_cvs WHERE id = %s AND job_id = %s",
            (cv_id, job_id),
        )
        cv_exists = cursor.fetchone()[0]
        if not cv_exists:
            return jsonify({"message": "Invalid CV ID for the specified Job ID"}), 400

        # Check if the application already exists
        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE job_id = %s AND user_id = %s",
            (job_id, user_id),
        )
        application_exists = cursor.fetchone()[0]
        if application_exists:
            return jsonify({"message": "Application already submitted for this job"}), 400

        # Insert the application into the database
        cursor.execute(
            """
            INSERT INTO applications (job_id, user_id, cv_id, source, application_date)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (job_id, user_id, cv_id, source),
        )
        connection.commit()

        return jsonify({"message": "Application submitted successfully"}), 201
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@jobs_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_user_applications():
    """
    Retrieve all applications for the logged-in user.
    """
    user_id = get_jwt_identity()
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch user applications with associated CV details
        cursor.execute(
            """
            SELECT a.id AS application_id, a.job_id, j.title AS job_title, 
                   a.application_date, a.status, a.source, c.file_url AS cv_file_url
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            LEFT JOIN customized_cvs c ON a.cv_id = c.id
            WHERE a.user_id = %s
            """,
            (user_id,),
        )
        applications = cursor.fetchall()
        return jsonify({"data": applications}), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching applications: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



@jobs_bp.route('/applications/<int:application_id>', methods=['DELETE'])
@jwt_required()
def delete_application(application_id):
    """
    Delete an application by ID.
    """
    connection = None
    cursor = None
    try:
        user_id = get_jwt_identity()

        # Connect to the database
        connection = get_connection()
        cursor = connection.cursor()

        # Check if the application belongs to the user
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM applications 
            WHERE id = %s AND user_id = %s
            """,
            (application_id, user_id),
        )
        application_exists = cursor.fetchone()[0]

        if not application_exists:
            return jsonify({"message": "Application not found or access denied"}), 404

        # Delete the application
        cursor.execute(
            """
            DELETE FROM applications 
            WHERE id = %s AND user_id = %s
            """,
            (application_id, user_id),
        )
        connection.commit()

        return jsonify({"message": "Application deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



@jobs_bp.route('/apply', methods=['POST'])
@jwt_required()
def apply_to_job():
    """
    Apply to a job using a CV.
    """
    connection = None
    cursor = None
    try:
        data = request.json
        job_id = data.get("job_id")
        cv_id = data.get("cv_id")
        user_id = get_jwt_identity()

        if not job_id or not cv_id:
            return jsonify({"message": "Job ID and CV ID are required"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        # Check if the application already exists
        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE job_id = %s AND user_id = %s",
            (job_id, user_id),
        )
        application_exists = cursor.fetchone()[0]
        if application_exists:
            return jsonify({"message": "Application already submitted for this job"}), 400

        # Insert the application
        cursor.execute(
            """
            INSERT INTO applications (job_id, user_id, cv_id, source, application_date)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (job_id, user_id, cv_id, "Manual"),
        )
        connection.commit()

        return jsonify({"message": "Application successfully recorded"}), 201
    except Exception as e:
        return jsonify({"message": f"Error during application: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


    
@jobs_bp.route('/job-analytics', methods=['GET'])
def get_job_analytics():
    db = None
    cursor = None
    try:
        # Establish DB connection
        db = get_connection()
        cursor = db.cursor(dictionary=True)  

        # Query to fetch job analytics
        query = """
        SELECT 
            skill_match_level, 
            location, 
            count 
        FROM 
            analytics
        ORDER BY 
            skill_match_level, location
        """
        cursor.execute(query)
        analytics_data = cursor.fetchall()

        # Return the data in JSON format
        return jsonify({
            "status": "success",
            "data": analytics_data
        }), 200

    except Exception as e:
        # Handle errors
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if db:
            db.close()

if __name__ == '__main__':
    jobs_bp.run(debug=True)

