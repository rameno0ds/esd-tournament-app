# Dockerfile for finalize_match_outcome.py
FROM python:3.10-slim

WORKDIR /app

# Copy service code
COPY finalize_match_outcome_service.py .

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Run the service
CMD ["python", "finalize_match_outcome_service.py"]
