# Use official Python image (lightweight)
FROM python:3.10.15-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY CapitalGainsService/capital_gains.py .
COPY CapitalGainsService/run.py .

# Set Flask app environment variable
ENV FLASK_APP=run.py
ENV NINJA_API_KEY=T6x6QsSBjaxT+BssCEg4VQ==wwU7bHC7P9hlXitc
# Expose port 8080 for external access
EXPOSE 8080

# Command to run the Flask app
CMD ["python", "run.py"]
