# Use official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# --- START Java Installation for language-tool-python ---
# Update package lists
RUN apt-get update

# Install default JRE (usually OpenJDK)
# This is a more generic package name that should pull in a suitable JRE
RUN apt-get install -y default-jre && \
    # Clean up apt cache to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable (may vary slightly based on default-jre installation)
# For default-jre on Debian/Ubuntu, it's often /usr/lib/jvm/default-java
ENV JAVA_HOME=/usr/lib/jvm/default-java
# Add Java's bin directory to the PATH
ENV PATH=$JAVA_HOME/bin:$PATH

# Verify Java installation (for debugging purposes during build)
# This command will print the Java version if successful
RUN java -version
# --- END Java Installation ---

# Copy only requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the backend port
EXPOSE 5001

# Command to run the FastAPI app with reload
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
