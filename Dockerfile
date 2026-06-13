# Use an official lightweight Python runtime
FROM python:3.11-slim

# Set system configurations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Establish our working directory inside the container
WORKDIR /app

# Install system dependencies required by packages like scikit-survival
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gfortran \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- FIXES APPLIED BELOW TO MATCH NEW REPO STRUCTURE ---

# Create the structural directories inside the container workspace
RUN mkdir -p data model

# Copy the files out of your new local subfolders into the container
COPY app/app.py ./app/
COPY model/pipeline.py ./model/
COPY data/consumibles.xlsx* data/infotec.xlsx* data/*.csv ./data/

# Expose the default Streamlit network port
EXPOSE 8501

# Configure container health-check flags
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]