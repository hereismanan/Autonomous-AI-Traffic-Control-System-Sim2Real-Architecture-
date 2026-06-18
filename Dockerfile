# 1. Use a rock-solid, specific Ubuntu release
FROM ubuntu:22.04

# 2. Prevent the installation from getting stuck asking for timezone input
ENV DEBIAN_FRONTEND=noninteractive

# 3. Install Python, pip, and the tools needed to add custom repositories
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 4. Add the official SUMO PPA (Personal Package Archive) and install SUMO
RUN add-apt-repository ppa:sumo/stable -y \
    && apt-get update \
    && apt-get install -y sumo sumo-tools \
    && rm -rf /var/lib/apt/lists/*

# 5. Point the 'python' command to python3 so our scripts run normally
RUN ln -s /usr/bin/python3 /usr/bin/python

# 6. Set our environment variables
ENV SUMO_HOME=/usr/share/sumo
WORKDIR /app

# 7. Install our Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 8. Copy the project code
COPY . .

# 9. Keep the container alive
CMD ["tail", "-f", "/dev/null"]