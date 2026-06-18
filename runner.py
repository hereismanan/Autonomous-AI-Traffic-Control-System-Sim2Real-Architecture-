import os
import sys
import time
from database import TrafficDatabase  # Import your new database handler

# Verify SUMO_HOME environment variable
if 'SUMO_HOME' in os.environ:
    sumo_home = os.environ['SUMO_HOME']
    tools = os.path.join(sumo_home, 'tools')
    sys.path.append(tools)
else:
    sys.exit("[ERROR] SUMO_HOME environment variable is missing!")

import traci

sumo_binary = "sumo" # Removed -gui.exe
sumo_cfg = "data/sim.sumocfg"
sumo_cmd = [sumo_binary, "-c", sumo_cfg, "--delay", "0"] # Remove --start

print("Connecting to database and launching SUMO...")
db = TrafficDatabase()  # Initialize database connection
traci.start(sumo_cmd)

junction_id = "J1" 
target_incoming_lane = "E0_0"
step = 0

try:
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        # 1. Pull Telemetry from Simulation Environment
        vehicle_ids = traci.vehicle.getIDList()
        vehicle_count = traci.lane.getLastStepVehicleNumber(target_incoming_lane)
        queue_length = traci.lane.getLastStepHaltingNumber(target_incoming_lane)
        current_phase = traci.trafficlight.getPhase(junction_id)
        
        # 2. Process AI State Rules
        vip_detected = any(traci.vehicle.getTypeID(veh) == "vip_car" for veh in vehicle_ids)
        
        if vip_detected:
            if current_phase != 0:
                print(f"Step {step}: VIP Convoy Intercepted. Initializing signal override.")
                traci.trafficlight.setPhase(junction_id, 0)
        elif queue_length >= 1:
            if current_phase != 0:
                print(f"Step {step}: Local congestion limit reached. Flushing lane {target_incoming_lane}.")
                traci.trafficlight.setPhase(junction_id, 0)
                
        # 3. Persist State Data to PostgreSQL Telemetry Store
        db.log_telemetry(
            step=step,
            junction_id=junction_id,
            lane_id=target_incoming_lane,
            veh_count=vehicle_count,
            queue=queue_length,
            phase=current_phase,
            vip_flag=vip_detected
        )
        
        step += 1

except Exception as e:
    print(f"[RUNTIME ERROR]: {e}")

finally:
    traci.close()
    db.close()  # Ensure database connection pool closes cleanly
    print("Simulation execution complete. Telemetry stream closed.")