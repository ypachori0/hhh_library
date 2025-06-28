# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy all backend source files into /app
COPY . /app

# Make sure the entry script is executable
RUN chmod +x start.sh

# Set environment variables for Flask
ENV FLASK_APP=/app/app.py
ENV FLASK_RUN_PORT=8000
ENV FLASK_ENV=production

# Expose Flask's port
EXPOSE 8000

# Default command to run your startup script
CMD ["bash", "start.sh"]
