# Backend Dockerfile

FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install required system packages, including mysql-client
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file from the backend directory into the container
COPY ./backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend source code into the container
COPY ./backend /app

# Copy the wait-for-db.sh script from the root context into the container
COPY ./backend/wait-for-db.sh /wait-for-db.sh

# Make the wait-for-db.sh script executable
RUN chmod +x /wait-for-db.sh

# Expose the application port
EXPOSE 5000

# Command to wait for the database to be ready and then start the application
CMD ["/wait-for-db.sh", "db", "python", "app.py"]
