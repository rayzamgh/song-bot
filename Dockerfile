# Use a smaller base image
FROM python:3.11-slim

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

ARG GOOGLE_API_KEY
ARG GOOGLE_CSE_ID
ARG CLIENT_ID
ARG CLIENT_SECRET
ARG OPENAI_API_KEY
ARG FIREBASE_API_KEY
ARG DISCORD_TOKEN
ARG GOOGLE_APPLICATION_CREDENTIALS
ARG GAMESPOT_API_KEY
ARG ACTIVE_CHANNEL_NAME
ARG ENVIRONMENT

ENV GOOGLE_API_KEY=$GOOGLE_API_KEY
ENV GOOGLE_CSE_ID=$GOOGLE_CSE_ID
ENV CLIENT_ID=$CLIENT_ID
ENV CLIENT_SECRET=$CLIENT_SECRET
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV FIREBASE_API_KEY=$FIREBASE_API_KEY
ENV DISCORD_TOKEN=$DISCORD_TOKEN
ENV GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS
ENV GAMESPOT_API_KEY=$GAMESPOT_API_KEY
ENV ACTIVE_CHANNEL_NAME=$ACTIVE_CHANNEL_NAME
ENV ENVIRONMENT=$ENVIRONMENT

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container (if your application is a web server)
EXPOSE 80

# Run your script when the container launches
CMD ["python", "main.py"]