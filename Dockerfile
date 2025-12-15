# Dockerfile
FROM python:3.12-slim

# Work inside /app in the container
WORKDIR /app

# Install system build tools (often needed for scientific/python deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list and install Python deps
# If your requirements file has a different name, change this line.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project into the image
COPY . .

# Install the package so imports work
RUN pip install --no-cache-dir .

# Ensure expected directories exist inside the container
# - instance: where parkinsons.db lives
# - data/input: where VCFs are read from
# - data/output: unused for now but nice to have
# - src/logs: where your logger writes log files
# - data/uploads: Where uploaded VCFs will be saved 
RUN mkdir -p instance data/input data/output src/logs data/uploads

# Make Python output unbuffered (nicer logs)
ENV PYTHONUNBUFFERED=1

# All commands will go through run.py
ENTRYPOINT ["python", "run.py"]

# Default behaviour if no extra arguments given: start the web app
CMD ["web"]
