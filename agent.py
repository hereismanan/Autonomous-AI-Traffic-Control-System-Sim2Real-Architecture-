import os
import sys
import psycopg2
from google import genai  # Modern SDK import structure

class TrafficAgent:
    def __init__(self):
        # Establish database connection
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="root",
            host="db",
            port="5432"
        )
        self.cursor = self.conn.cursor()
        
        # Initialize the current client
        # The SDK automatically looks for the GEMINI_API_KEY environment variable
        self.client = genai.Client()

    def fetch_historical_context(self):
        """Pulls telemetry rows to construct the context window."""
        query = """
        SELECT timestamp_step, vehicle_count, queue_length, active_phase, vip_present 
        FROM junction_telemetry 
        ORDER BY timestamp_step ASC;
        """
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            context_string = "Here is the raw telemetry from junction J1:\n"
            context_string += "Step | Vehicles Present | Queue Length | Active Phase | VIP Present\n"
            context_string += "-----------------------------------------------------------------\n"
            for row in rows:
                context_string += f"Step {row[0]} | Cars: {row[1]} | Queue: {row[2]} | Phase: {row[3]} | VIP: {row[4]}\n"
            return context_string
        except Exception as e:
            return f"Error retrieving metrics from database: {e}"

    def query_intersection(self, user_question):
        """Binds context payload with the user request for inference."""
        print("Gathering database telemetry...")
        telemetry_context = self.fetch_historical_context()
        
        system_instruction = (
            "You are an AI Urban Traffic Management Operator for Delhi NCR. "
            "Analyze the provided simulation logs to answer the user's question directly, "
            "backing up your conclusions with specific step numbers and metrics from the data."
        )
        
        full_prompt = f"{system_instruction}\n\n{telemetry_context}\n\nUser Question: {user_question}"
        
        print("Analyzing data with Gemini...")
        try:
            # Using the modern generation method and production model string
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt,
            )
            return response.text
        except Exception as e:
            return f"[API ERROR] Failed to generate response: {e}"

    def close(self):
        self.cursor.close()
        self.conn.close()

# --- Execution ---
if __name__ == "__main__":
    agent = TrafficAgent()
    
    question = "At what step did congestion peak, and did the AI system successfully flush the lane when the VIP arrived?"
    
    answer = agent.query_intersection(question)
    print("\n=== TRAFFIC OPERATOR INSIGHT ===")
    print(answer)
    
    agent.close()