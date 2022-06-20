FROM alpine:latest

ENV CPU_NUM=1
ENV TEMP_FUNC="math.exp(0.075 * t) - 0.01 * t**2 + 10"

# Update the base image
RUN apk -U upgrade

# Install impitool and curl
RUN apk add --no-cache ipmitool
RUN apk add --no-cache python3 

# Copy the entrypoint script into the container
COPY fanoverlord.py /

# Load the entrypoint script to be run later
ENTRYPOINT ["/usr/bin/python3", "/fanoverlord.py"]
