#!/usr/bin/env python3
"""Test the production GraphQL endpoint for flow data."""
import requests
import json

# Production endpoint
url = "https://web-production-970f8.up.railway.app/graphql/"

# Test query
query = """
query {
  allDevices {
    __typename
    ... on BatteryType {
      id
      name
      status
      currentFlowW
    }
    ... on ElectricVehicleType {
      id
      name
      status
      mode
      currentFlowW
    }
  }
}
"""

# You'll need to get the session cookie from your browser
# For now, test without auth to see if schema is correct
response = requests.post(url, json={"query": query})
print("Status:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))
