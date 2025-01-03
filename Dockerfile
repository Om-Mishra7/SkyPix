FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set the working directory for the backend app
WORKDIR /app/backend

# Set the command to run the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7001", "server:app"]
