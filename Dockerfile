# Use an official lightweight Python image.
FROM python:3.9-slim

# Set the working directory in the Docker container.
WORKDIR /app

# Copy the current directory contents into the container at /app.
COPY . /app

# Install any needed packages specified in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the script.
CMD ["python3", "./github-contributions.py"]
