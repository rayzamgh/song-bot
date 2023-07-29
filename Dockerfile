# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Update the package list, install build-essential, and clean up
RUN apt-get update -y && \
    apt-get install build-essential -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install build-essential
RUN apt-get install build-essential -y

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container (if your application is a web server)
EXPOSE 80

# Run your script when the container launches
CMD ["python", "main.py"]
