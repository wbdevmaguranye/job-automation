from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required ,get_jwt_identity
from jobs_routes import jobs_bp
import mysql.connector
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
import os

# Load environment variables
load_dotenv()
# S3 Configuration
S3_BUCKET = os.getenv("AWS_S3_BUCKET")
S3_REGION = os.getenv("AWS_REGION")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)
# Connect to MySQL database
connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # This will allow requests from any origin by default
app.config["JWT_SECRET_KEY"] = "testing" 
bcrypt = Bcrypt(app)
jwt = JWTManager(app)




# Route: Register User
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

  
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO Users (name, email, password)
            VALUES (%s, %s, %s)
        """, (name, email, hashed_password))
        connection.commit()
    except mysql.connector.Error as err:
        return jsonify({"message": "Error: {}".format(err)}), 400
    finally:
        cursor.close()

    return jsonify({"message": "User registered successfully!"}), 201


# Route: Login User
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Fetch user from the database
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Convert user ID to string before creating the access token
    access_token = create_access_token(identity=str(user["id"]))
    return jsonify({"access_token": access_token}), 200


# Route: Protected Profile
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    return jsonify({"message": f"Welcome, User {current_user}"}), 200

# Register the Blueprint
app.register_blueprint(jobs_bp)


# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
