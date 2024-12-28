FROM python:3.9-alpine

# Install build dependencies for scipy
RUN apk update && \
    apk add --no-cache \
    openblas-dev \
    cmake \
    gcc \
    gfortran \
    libatlas-dev \
    make \
    musl-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Run your application
CMD ["python", "app.py"]
