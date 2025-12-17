import requests
import time
import sys


class Genesis:
    """
    The main entry point for the Genesis Framework.
    """
    def __init__(self, api_key: str, base_url: str = "https://genesis-framework.vercel.app/api"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        print(f"🔌 Genesis Core Connected")

    def create_swarm(self, goal: str, depth: int = 3, name: str = "Genesis_Agent"):
        """
        Initializes a new recursive swarm.
        """
        print(f"🚀 Deploying Swarm: {name}")
        print(f"🎯 Objective: {goal}")

        payload = {
            "api_key": self.api_key,
            "agent_name": name,
            "goal": goal,
            "recursion_depth": depth
        }

        try:
            response = requests.post(f"{self.base_url}/run", json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Swarm Active | Session ID: {data.get('session_id')}")
                print(f"📊 Monitor here: https://genesis-framework.vercel.app/dashboard")
                return data
            else:
                print(f"❌ Launch Failed: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None