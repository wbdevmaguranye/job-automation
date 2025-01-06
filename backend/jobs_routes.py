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
    url = data.get("url")
    description = data.get("description")
    date_posted = data.get("date_posted")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO Jobs (title, company, url, description, date_posted)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, company, url, description, date_posted))
        connection.commit()
    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 400
    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "Job added successfully!"}), 201
