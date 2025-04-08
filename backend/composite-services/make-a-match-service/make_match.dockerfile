# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir flask flask-cors requests

# Expose the port Flask runs on
EXPOSE 5007

# Run the app
CMD ["python", "make_match.py"]
