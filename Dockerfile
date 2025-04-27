# Use a Python image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install the project's dependencies
RUN pip install --no-cache-dir hatchling
RUN pip install --no-cache-dir .

# Set environment variables for Twitter authentication
# These should be provided at runtime for security purposes
ENV TWITTER_USERNAME "@example"
ENV TWITTER_EMAIL "me@example.com"
ENV TWITTER_PASSWORD "secret"

# Set the entrypoint command to run the MCP server
ENTRYPOINT ["twitter-mcp"]