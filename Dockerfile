FROM alpine:latest
ENV TZ="Asia/Shanghai"
ENV CPU_NUM=1
ENV SPEED_FUNC="tanh((t-55)/10)*40 + 50"
ENV TIME_COND=1
WORKDIR /

# Install impitool and curl
RUN apk add --no-cache -U ipmitool  tzdata python3 

# Copy the entrypoint script into the container
COPY better-fanoverlord/* /

# Load the entrypoint script to be run later
ENTRYPOINT ["/usr/bin/python3", "/fanoverlord.py"]
