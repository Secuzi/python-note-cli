import requests
from dotenv import load_dotenv
import os
from test.tester import testerino
from test.test2.teste import pastil

# Load environment variables
load_dotenv()
testerino()
# Test the setup
print("✅ Packages imported successfully!")

# Test environment variable
api_key = os.environ.get("API_KEY", "not-set")
print(f"✅ API_KEY: {api_key}")

# Test requests
response = requests.get("https://api.github.com")
print(f"✅ GitHub API status: {response.status_code}")
