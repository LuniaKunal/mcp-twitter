# Use a Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better cache utilization
COPY requirements.txt ./

# Install the project's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . /app

# Set environment variables for Twitter authentication
# These should be provided at runtime for security purposes
ENV TWITTER_USERNAME "@example"
ENV TWITTER_EMAIL "me@example.com"
ENV TWITTER_PASSWORD "secret"

# Set the entrypoint command to run the MCP server
ENTRYPOINT ["twitter-mcp"]