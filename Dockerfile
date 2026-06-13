# Use an official lightweight Python runtime
FROM python:3.11-slim

# Set system configurations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Establish our working directory inside the container
WORKDIR /app

# Install system dependencies if required by packages like scikit-survival/gfortran
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gfortran \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code assets and reference Excel/CSV raw datasets into the container
COPY app.py pipeline.py ./
COPY consumibles.xlsx* infotec.xlsx* ./
# Copy any underlying sub-sheets if they are separate files in your folder
COPY *.csv ./ 

# Expose the default Streamlit network port
EXPOSE 8501

# Configure container health-check flags
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]