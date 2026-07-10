# Base image — which Python version to start from
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (layer caching — this layer only rebuilds when requirements change)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Tell Docker the container listens on port 8000
EXPOSE 8000

# Command to run when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]