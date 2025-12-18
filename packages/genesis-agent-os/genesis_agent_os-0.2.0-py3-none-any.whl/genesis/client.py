import requests
import time
import sys


class Genesis:
    """
    The main entry point for the Genesis Framework.

    Genesis is a framework for creating recursive agentic intelligence systems.
    It enables developers to build self-organizing agent swarms that can solve
    complex, multi-step problems through recursive decomposition.

    Attributes:
        api_key (str): The OpenAI API key for authentication
        base_url (str): The base URL for the Genesis API server
    """

    def __init__(self, api_key: str, base_url: str = "https://genesis-framework.vercel.app/api"):
        """
        Initialize the Genesis client.

        Args:
            api_key (str): Your OpenAI API key for authentication
            base_url (str, optional): The base URL for the Genesis API server.
                                    Defaults to "https://genesis-framework.vercel.app/api".
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        print(f"🔌 Genesis Core Connected")
        print(f"🌐 API Endpoint: {self.base_url}")

    def create_swarm(self, goal: str, depth: int = 3, name: str = "Genesis_Agent"):
        """
        Initializes a new recursive swarm with the specified parameters.

        This method creates a swarm of agents that work together to achieve the
        specified goal. The swarm can recursively create sub-agents up to the
        specified depth to solve complex problems in parallel.

        Args:
            goal (str): The primary objective for the swarm to achieve
            depth (int, optional): The maximum recursion depth for sub-agent creation.
                                 Defaults to 3.
            name (str, optional): A custom name for the swarm. Defaults to "Genesis_Agent".

        Returns:
            dict or None: Response data from the API if successful, None otherwise
        """
        print(f"🚀 Initializing Swarm: {name}")
        print(f"🎯 Primary Objective: {goal}")
        print(f"🔍 Recursion Depth: {depth}")
        print(f"⚡ Activating recursive intelligence protocols...")

        payload = {
            "api_key": self.api_key,
            "agent_name": name,
            "goal": goal,
            "recursion_depth": depth
        }

        try:
            print(f"📡 Sending deployment request...")
            response = requests.post(f"{self.base_url}/run", json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Swarm Successfully Deployed!")
                print(f"🆔 Session ID: {data.get('session_id')}")
                print(f"📊 Real-time dashboard: https://genesis-framework.vercel.app/dashboard")
                print(f"🔗 Monitoring recursive processes...")
                return data
            else:
                print(f"❌ Deployment Failed: {response.text}")
                print(f"⚠️  Status Code: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print(f"⏰ Request Timeout: Server took too long to respond")
            return None
        except requests.exceptions.ConnectionError:
            print(f"🌐 Connection Error: Unable to reach Genesis server")
            return None
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return None

    def check_status(self):
        """
        Check the status of the Genesis API connection.

        This method verifies that the client can communicate with the Genesis API
        server and that the API key is valid.

        Returns:
            dict or None: Status information if successful, None otherwise
        """
        print(f"🔍 Checking Genesis API connectivity...")

        try:
            # Make a simple status request to the API
            response = requests.get(f"{self.base_url}/status", timeout=10)

            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ Genesis API Status: {status_data.get('status', 'Unknown')}")
                print(f"📈 Server Health: Operational")
                return status_data
            else:
                print(f"❌ API Status Check Failed: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error during status check: {e}")
            return None