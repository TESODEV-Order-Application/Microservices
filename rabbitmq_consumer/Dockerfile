# Use an official Python runtime as a parent image
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG conn_str_audit
ENV conn_str_audit=${conn_str_audit}

ARG rabbit_username
ENV rabbit_username=${rabbit_username}

ARG rabbit_password
ENV rabbit_password=${rabbit_password}

ARG ip
ENV ip=${ip}

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5672 available to the world outside this container
EXPOSE 5672

# Define environment variable
ENV NAME RabbitMQConsumer

# Run the consumer script when the container launches
CMD ["python", "consumer.py"]