# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl


# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Copy the start.sh script into the container
COPY start.sh .

# Ensure the start.sh script is executable
RUN chmod +x start.sh

# Expose port (default to 8000)
EXPOSE 8000

# Command to run the start.sh script
# CMD ["python", "main.py"]
CMD ["./start.sh"]
