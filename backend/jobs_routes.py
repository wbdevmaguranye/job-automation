from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database import get_connection  # Ensure you're importing get_connection

# Define a Blueprint for job routes
jobs_bp = Blueprint('jobs', __name__)

# Route: List All Jobs
@jobs_bp.route('/jobs', methods=['GET'])
def get_jobs():
    connection = get_connection()  # Corrected function call
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Jobs")
        jobs = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()  # Ensure the connection is closed
    return jsonify(jobs), 200

# Route: Add a Job
@jobs_bp.route('/jobs', methods=['POST'])
@jwt_required()
def add_job():
    data = request.json
    title = data.get("title")
    company = data.get("company")
    location = data.get("location")
    url = data.get("url")
    description = data.get("description")
    benefits = data.get("benefits")
    schedule = data.get("schedule")
    application_questions = data.get("application_questions")
    work_authorisation = data.get("work_authorisation")
    date_posted = data.get("date_posted")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO Jobs (title, company, location, url, description, benefits, schedule, application_questions, work_authorisation, date_posted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, company, location, url, description, benefits, schedule, application_questions, work_authorisation, date_posted))
        connection.commit()
    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 400
    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "Job added successfully!"}), 201

# Route: Get a Job by ID
@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_by_id(job_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Jobs WHERE id = %s", (job_id,))
        job = cursor.fetchone()
        if not job:
            return jsonify({"message": "Job not found"}), 404
    finally:
        cursor.close()
        connection.close()
    return jsonify(job), 200

# Route: Update a Job
@jobs_bp.route('/jobs/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    data = request.json
    updates = {key: value for key, value in data.items() if value is not None}

    if not updates:
        return jsonify({"message": "No updates provided"}), 400

    columns = ", ".join(f"{key} = %s" for key in updates.keys())
    values = list(updates.values()) + [job_id]

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(f"UPDATE Jobs SET {columns} WHERE id = %s", values)
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Job not found or no changes made"}), 404
    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "Job updated successfully!"}), 200

# Route: Delete a Job
@jobs_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM Jobs WHERE id = %s", (job_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Job not found"}), 404
    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "Job deleted successfully!"}), 200
