# 🚦 Autonomous Urban Traffic Controller (Sim2Real PoC)

This repository contains a containerized Proof of Concept (PoC) for an intelligent, edge-deployed traffic management system. It is specifically designed to address the complexities of chaotic, high-density environments (like Delhi NCR) by combining simulation physics, real-time signal override logic, and an AI-driven RAG analytics operator.

## 🧠 System Architecture

The architecture mimics a modern edge-to-cloud deployment:
1. **Simulation Engine (SUMO):** Runs headless traffic physics, representing the physical intersection.
2. **Control Logic (TraCI / Python):** Acts as the "Edge Device," monitoring lane density and VIP presence to override static traffic light phases dynamically.
3. **Telemetry Store (PostgreSQL):** A time-series database logging intersection state, queue length, and phase changes every second.
4. **Analytics Operator (Gemini 2.5 Flash):** A Retrieval-Augmented Generation (RAG) agent that parses the SQL telemetry to provide natural language operational reports.

## 🚀 Quick Start (Dockerized)

Ensure you have Docker and Docker Compose installed.

**1. Clone and Configure**
```bash
git clone https://github.com/yourusername/traffic_poc.git
cd traffic_poc
# Set your Gemini API key for the analytics agent
export GEMINI_API_KEY="your_api_key_here"
```

**2. Build the Microservices**
```bash
docker-compose up -d --build
```

**3. Initialize the Telemetry Database**
```bash
docker-compose exec db psql -U postgres -d postgres -c "CREATE TABLE junction_telemetry (log_id SERIAL PRIMARY KEY, timestamp_step INT NOT NULL, junction_id VARCHAR(50) NOT NULL, incoming_lane VARCHAR(50) NOT NULL, vehicle_count INT NOT NULL, queue_length INT NOT NULL, active_phase INT NOT NULL, vip_present BOOLEAN NOT NULL, logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
```

**4. Execute a Headless Simulation**
Run the physics engine and the AI control loop. This will simulate traffic, execute signal overrides, and log the data to Postgres in milliseconds.
```bash
docker-compose exec app python runner.py
```

**5. Query the RAG Agent**
Ask the AI operator to analyze the traffic data that was just generated.
```bash
docker-compose exec app python agent.py
```

## 🛣️ Future Roadmap: Sim2Real Transition

The next phase of this project decouples the TraCI simulation telemetry and replaces it with real-world perception.
* **Perception Layer:** Fine-tuning a lightweight Vision Transformer (ViT) or UNet on the **Indian Driving Dataset (IDD)** to segment lane-less, highly occluded traffic (auto-rickshaws, two-wheelers) from raw RTSP CCTV streams.
* **Control Layer:** Upgrading the rules-based TraCI script to output NTCIP 1202 commands to interface with physical Actuated Signal Controllers (ASCs).