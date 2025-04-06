# Use a suitable base image, e.g., Ubuntu LTS
FROM ubuntu:focal

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies (wget for downloading, tar for extracting, Python and pip)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    tar \
    ca-certificates \
    python3 \
    python3-pip \
    python3-setuptools \
    git \
    build-essential \
    autoconf \
    automake \
    libtool \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Define MultiChain version and download URL
ARG MULTICHAIN_VERSION=2.3.3

# Detect architecture and set appropriate URL or build methods
# Default to x86_64 URL for backward compatibility
ARG TARGETARCH
ARG MULTICHAIN_URL=https://www.multichain.com/download/multichain-${MULTICHAIN_VERSION}.tar.gz

# Handle architecture-specific installation
RUN if [ "$TARGETARCH" = "arm64" ]; then \
        echo "ARM64 architecture detected - building from source"; \
        # Clone the MultiChain repository and build from source for ARM64
        cd /tmp && \
        git clone https://github.com/MultiChain/multichain.git && \
        cd multichain && \
        # Try master branch directly since v2.3.3 tag doesn't exist
        git checkout master && \
        ./autogen.sh && \
        ./configure && \
        make -j$(nproc) && \
        cp src/multichaind src/multichain-cli src/multichain-util /usr/local/bin/ && \
        chmod +x /usr/local/bin/multichaind /usr/local/bin/multichain-cli /usr/local/bin/multichain-util; \
    else \
        echo "x86_64 architecture detected - using pre-compiled binaries"; \
        # Download pre-compiled binaries for x86_64
        cd /tmp && \
        wget -q ${MULTICHAIN_URL} -O multichain.tar.gz && \
        tar -xvzf multichain.tar.gz && \
        cd multichain-${MULTICHAIN_VERSION} && \
        mv multichaind multichain-cli multichain-util /usr/local/bin/ && \
        chmod +x /usr/local/bin/multichaind /usr/local/bin/multichain-cli /usr/local/bin/multichain-util; \
    fi && \
    cd / && \
    rm -rf /tmp/*

# Install Python dependencies
RUN pip3 install savoir requests

# Create app directory before copying (in case directory doesn't exist)
RUN mkdir -p /app

# Copy the Python scripts into the container
COPY ./my-chain-data/7_multichain /app

# Add a non-root user (good practice)
RUN groupadd -r multichain && useradd --no-log-init -r -g multichain multichain

# Set up working directory and permissions for MultiChain data
WORKDIR /data
RUN mkdir -p /data/.multichain && \
    chown -R multichain:multichain /data && \
    chown -R multichain:multichain /app

# Set the HOME environment variable to /data
ENV HOME=/data

# Create an entry script to initialize and start the MultiChain daemon
RUN echo '#!/bin/bash\n\
# Check if chain already exists\n\
if [ ! -d "/data/.multichain/chain1" ]; then\n\
  echo "Initializing chain1..."\n\
  cd /data && multichain-util create chain1\n\
  # Configure RPC settings to match the Python scripts\n\
  mkdir -p /data/.multichain/chain1\n\
  echo "rpcuser=multichainrpc" > /data/.multichain/chain1/multichain.conf\n\
  echo "rpcpassword=52TH6uU5onYPrwGoZzMittjoEjg9iZS6rDi8i3aVQjNi" >> /data/.multichain/chain1/multichain.conf\n\
  echo "rpcport=1234" >> /data/.multichain/chain1/multichain.conf\n\
  echo "rpcallowip=0.0.0.0/0" >> /data/.multichain/chain1/multichain.conf\n\
fi\n\
\n\
# Start the MultiChain daemon\n\
echo "Starting MultiChain daemon..."\n\
cd /data && multichaind chain1 -daemon\n\
\n\
# Wait for daemon to start\n\
sleep 5\n\
\n\
# Keep the container running\n\
tail -f /dev/null\n\
' > /app/start.sh && chmod +x /app/start.sh

# Switch to the multichain user
USER multichain

# Define the entry point that starts the MultiChain daemon and keeps the container running
CMD ["/app/start.sh"]
