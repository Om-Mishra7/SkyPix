# Use Python 3.9-alpine as the base image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Install build dependencies (compilers) required for installing Python packages with native extensions
RUN apk add --no-cache \
    build-base \
    meson \
    gcc \
    g++ \
    libffi-dev \
    python3-dev \
    gfortran  # Add gfortran for Fortran support

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set the working directory for the backend app
WORKDIR /app/backend

# Set the command to run the application using gunicorn
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:7001", "server:app"]
