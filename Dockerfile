FROM python:3.13-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make entry point script executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port Streamlit runs on
EXPOSE 8501

# Use the entry point script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
