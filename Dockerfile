# Use Python base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy project files to the container
COPY . /app

# Install dependencies via setup.py
RUN pip install --upgrade pip && pip install .

# Expose the port Flask (or another service) runs on
EXPOSE 5000

# Define the command to run the application
CMD ["python", "run.py"]
