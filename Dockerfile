# Lightweight Python image
FROM python:3.9-slim

# Avoid Python buffering issues
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements_online.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements_online.txt

# Copy the rest of the project
COPY . .

# Expose Streamlit port
EXPOSE 8502

# Run Streamlit app
CMD ["streamlit", "run", "ui.py", "--server.port=8502", "--server.address=0.0.0.0"]
