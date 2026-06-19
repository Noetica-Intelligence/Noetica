# Use the official Python 3.11 image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend and the database
COPY backend/ ./backend/
COPY src/ ./src/
COPY data/ ./data/
COPY scientific_intel_v2.db .

# Expose the port Hugging Face expects
EXPOSE 7860

# Command to run the FastAPI server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
