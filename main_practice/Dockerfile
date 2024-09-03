# Use an clear linux runtime as a parent image
FROM debian:12

RUN apt-get update && apt-get install -y curl


# Set the working directory in the container
WORKDIR /app


# Copy the current directory contents into the container at /app
COPY . .


# Ensure the start.sh script is executable
RUN chmod +x ./practice/create_data_in_DB.sh
