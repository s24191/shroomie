FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies (you can also try the `--prefer-binary` flag instead of `--no-binary`)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app

# Expose the port the app runs on
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
