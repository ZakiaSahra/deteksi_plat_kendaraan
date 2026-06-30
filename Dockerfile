FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (required for easyocr / torch if needed, though headless opencv avoids libGL issues)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user specifically for Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Change working directory to user home and copy app
WORKDIR $HOME/app
COPY --chown=user . $HOME/app

# Hugging Face runs on port 7860
EXPOSE 7860

# Run the Flask app with gunicorn or just built-in server (built-in is fine for spaces demo)
CMD ["flask", "run", "--host=0.0.0.0", "--port=7860"]
