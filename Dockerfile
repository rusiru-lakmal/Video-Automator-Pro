# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    git \
    fonts-noto-color-emoji \
    fonts-font-awesome \
    fonts-dejavu \
    fonts-liberation \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install build dependencies and torch separately to avoid basicsr hang
RUN pip install --no-cache-dir numpy==1.26.4 cython setuptools wheel && \
    pip install --no-cache-dir torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Patch basicsr for numpy and torchvision compatibility
RUN find /usr/local/lib/python3.11/site-packages/basicsr -type f -exec sed -i 's/np.int/int/g' {} + && \
    find /usr/local/lib/python3.11/site-packages/basicsr -type f -exec sed -i 's/torchvision.transforms.functional_tensor/torchvision.transforms.functional/g' {} +

# Copy the rest of the application code
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
