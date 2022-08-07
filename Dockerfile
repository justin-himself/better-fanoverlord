FROM alpine:latest

ENV CPU_NUM=1
ENV SPEED_FUNC="tanh((t-55)/10)*40 + 50"

# Update the base image
RUN apk -U upgrade

# Install impitool and curl
RUN apk add --no-cache ipmitool
RUN apk add --no-cache python3 

# Copy the entrypoint script into the container
COPY fanoverlord.py /

# Load the entrypoint script to be run later
ENTRYPOINT ["/usr/bin/python3", "/fanoverlord.py"]
