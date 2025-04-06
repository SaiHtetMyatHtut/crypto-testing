# MultiChain Docker Environment

This repository contains a Docker setup for running MultiChain blockchain with Python client scripts. The setup supports both x86_64/amd64 and ARM64 architectures (like Apple Silicon M1/M2/M3).

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)
- Basic understanding of blockchain concepts and MultiChain
- Familiarity with Docker commands

## Building the Docker Image

Build the Docker image with the following command:

```sh
docker build -t multichain-node .
```

This builds an image that:
- Is based on Ubuntu Focal (20.04 LTS)
- Installs MultiChain 2.3.3
- Installs Python 3 with required dependencies (`savoir` and `requests`)
- Creates a non-root user named `multichain` for better security
- Automatically detects architecture and uses appropriate installation method

## Using Docker Compose (Recommended)

For easier management, you can use Docker Compose:

```sh
# Start the container
docker-compose up -d

# Stop the container
docker-compose down

# View logs
docker-compose logs -f multichain
```

The Docker Compose setup:
- Builds and starts the container automatically
- Sets up volume mapping for data persistence
- Exposes the RPC port (1234)
- Configures automatic restart
- Includes a health check

## Testing Your Setup

After starting the container, verify everything is working:

```sh
# Check logs for successful startup
docker logs my-multichain-daemon

# Test the MultiChain node with the sample Python client
docker exec -it my-multichain-daemon python3 /app/1_client.py

# Verify architecture
docker exec -it my-multichain-daemon uname -m
```

You should see output showing the node information and no error messages.

## Architecture Support

The Dockerfile automatically handles different architectures:
- On **x86_64/amd64**: Uses pre-compiled binaries from the official MultiChain download site
- On **ARM64 (aarch64)**: Automatically builds MultiChain from source code

## Building for Multiple Architectures (ARM64/AMD64)

To build the image for both ARM-based (like Mac M1/M2/M3) and x86-based systems:

```sh
# Set up buildx (one-time setup)
docker buildx create --name multiarch-builder --use

# Build and push to registry
docker buildx build --platform linux/amd64,linux/arm64 -t username/multichain-node:latest --push .

# To use locally, you'll need to specify platform when running
docker run --platform linux/amd64 -d --name my-multichain-daemon -v ./my-chain-data:/data username/multichain-node
```

Replace `username` with your Docker Hub username or registry path.

## Running the Container (Without Docker Compose)

Start the container with:

```sh
docker run -d --name my-multichain-daemon -v ./my-chain-data:/data multichain-node
```

This command:
- Runs the container in detached mode (`-d`)
- Names it `my-multichain-daemon`
- Mounts the local `./my-chain-data` directory to `/data` inside the container
- Initializes a MultiChain blockchain named `chain1` if it doesn't exist
- Configures RPC settings to match the Python scripts
- Starts the MultiChain daemon

## Accessing the Container

You can get an interactive shell inside the container with:

```sh
docker exec -it my-multichain-daemon sh
```

## Running Python Scripts

Run the Python scripts with:

```sh
docker exec -it my-multichain-daemon python3 /app/1_client.py
```

Replace `1_client.py` with the name of the script you want to run.

## Working with Live Code Updates

The Docker image copies the Python scripts from your local system during the build process. If you want to make changes to the scripts and see them immediately without rebuilding:

1. Create a symbolic link in the container to the mounted volume:

```sh
docker exec -u root my-multichain-daemon ln -sf /data/7_multichain /app_live
```

2. Set proper permissions:

```sh
docker exec -u root my-multichain-daemon chown -R multichain:multichain /app_live
```

3. Run scripts from the linked directory:

```sh
docker exec -it my-multichain-daemon python3 /app_live/1_client.py
```

Now you can edit files in `./my-chain-data/7_multichain` on your host machine, and the changes will be immediately available inside the container.

## MultiChain Configuration

The container is configured with the following RPC settings:
- Username: `multichainrpc`
- Password: `52TH6uU5onYPrwGoZzMittjoEjg9iZS6rDi8i3aVQjNi`
- Host: `127.0.0.1` (inside container)
- Port: `1234`
- Chain name: `chain1`
- RPC allowed from: any IP (0.0.0.0/0)

These match the settings in the Python utility module.

## External RPC Access

The RPC port is exposed to the host machine, allowing you to connect to the blockchain from outside the container. To connect from your host machine or other containers:

```python
import requests

# Connect to the MultiChain RPC from host or other containers
url = 'http://localhost:1234'  # Or container IP if accessing from another container
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
auth = ('multichainrpc', '52TH6uU5onYPrwGoZzMittjoEjg9iZS6rDi8i3aVQjNi')
data = '{"method": "getinfo", "params": [], "id": 1, "chain_name": "chain1"}'

response = requests.post(url, data=data, headers=headers, auth=auth).json()
print(response)
```

## Container Lifecycle Management

- **Stop the container**: `docker stop my-multichain-daemon`
- **Restart the container**: `docker start my-multichain-daemon`
- **Remove the container**: `docker rm -f my-multichain-daemon`
- **View container logs**: `docker logs my-multichain-daemon`

## Data Persistence

All blockchain data is stored in the mounted volume (`./my-chain-data`), so it persists even if the container is removed. This ensures you don't lose your blockchain data between container restarts.

## Troubleshooting

1. **Port Conflicts**: If you receive an error about port 1234 being in use, change the port mapping in `docker-compose.yml`
2. **Permission Issues**: If you encounter permission problems with mapped volumes, ensure the host directory has appropriate permissions
3. **Architecture Detection**: If running on an unusual architecture, you may need to manually set `TARGETARCH` in the build command
4. **Container Already Exists**: If you get an error about the container name being in use:
   ```
   docker rm -f my-multichain-daemon  # Remove the existing container
   docker-compose up -d               # Start fresh
   ```