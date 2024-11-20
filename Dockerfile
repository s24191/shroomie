# Use Python 3.12-slim or 3.10-slim as the base image
FROM python:3.10-slim

# Install necessary system packages (build tools, libraries for numpy, h5py, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libatlas-base-dev \
    libopenblas-dev \
    libclang-dev \
    cmake \
    ninja-build \
    patchelf

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install Python dependencies (you can also try the `--prefer-binary` flag instead of `--no-binary`)
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
