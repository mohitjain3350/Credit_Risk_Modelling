# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements_online.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements_online.txt

# Copy the rest of the application code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "online_brain.py", "--server.port=8501", "--server.address=0.0.0.0"]
