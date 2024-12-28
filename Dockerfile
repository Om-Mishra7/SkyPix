FROM python:3.9-slim


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Run your application
CMD ["python", "app.py"]
