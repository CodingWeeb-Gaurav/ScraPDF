# Use an official Python image
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr && apt-get clean

# Set the working directory
WORKDIR /app

# Copy all backend files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask's default port
EXPOSE 8001

# Run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8001", "run:app"]
