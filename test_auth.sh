#!/bin/bash

# Test authentication flow

echo "=== Testing Django Session Authentication with GraphQL ==="
echo ""

# Step 1: Get CSRF token and session cookie
echo "1. Getting login page and CSRF token..."
CSRF_TOKEN=$(curl -s -c /tmp/test_cookies.txt http://localhost:8000/login/ | grep -o 'csrfmiddlewaretoken[^>]*value="[^"]*"' | sed 's/.*value="\([^"]*\)".*/\1/')
echo "   CSRF Token: ${CSRF_TOKEN:0:20}..."

# Step 2: Login
echo ""
echo "2. Logging in as testuser1..."
LOGIN_RESPONSE=$(curl -s -b /tmp/test_cookies.txt -c /tmp/test_cookies.txt \
  -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser1&password=testpass123&csrfmiddlewaretoken=${CSRF_TOKEN}" \
  -L -w "\n%{http_code}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -1)
echo "   HTTP Code: $HTTP_CODE"

# Step 3: Get new CSRF token for GraphQL
echo ""
echo "3. Getting dashboard CSRF token..."
GRAPHQL_CSRF=$(curl -s -b /tmp/test_cookies.txt http://localhost:8000/ | grep -o 'csrfmiddlewaretoken[^>]*value="[^"]*"' | sed 's/.*value="\([^"]*\)".*/\1/' | head -1)
if [ -z "$GRAPHQL_CSRF" ]; then
  GRAPHQL_CSRF=$CSRF_TOKEN
fi
echo "   New CSRF Token: ${GRAPHQL_CSRF:0:20}..."

# Step 4: Test GraphQL query
echo ""
echo "4. Testing GraphQL energyStats query..."
GRAPHQL_RESPONSE=$(curl -s -b /tmp/test_cookies.txt \
  -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: ${GRAPHQL_CSRF}" \
  -d '{
    "query": "query { energyStats { currentProduction currentConsumption } }"
  }')

echo "   Response:"
echo "$GRAPHQL_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GRAPHQL_RESPONSE"

# Step 5: Test allDevices query
echo ""
echo "5. Testing GraphQL allDevices query..."
DEVICES_RESPONSE=$(curl -s -b /tmp/test_cookies.txt \
  -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: ${GRAPHQL_CSRF}" \
  -d '{
    "query": "query { allDevices { __typename } }"
  }')

echo "   Response:"
echo "$DEVICES_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DEVICES_RESPONSE"

echo ""
echo "=== Test Complete ==="

# Cleanup
rm -f /tmp/test_cookies.txt
