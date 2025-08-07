#!/usr/bin/env bash

export APP_NAME="app"
USER_ID="user_123"
SESSION_ID="test-plantworx-$(date +%s)"

echo "Creating new session..."
curl -X POST  "http://127.0.0.1:8000/apps/$APP_NAME/users/$USER_ID/sessions/$SESSION_ID" \
  -H "Content-Type: application/json" | jq .

sleep 10

RESPONSE=$(curl -X POST  http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d "{
  \"appName\": \"$APP_NAME\",
    \"userId\": \"$USER_ID\",
    \"sessionId\": \"$SESSION_ID\",
    \"newMessage\": {
      \"role\": \"user\",
      \"parts\": [{
      \"text\": \"how can I grow a red rose in Harrow\"
      }]
    }
}")

echo "Full response 1"
echo "$RESPONSE"

sleep 10

RESPONSE=$(curl -X POST  http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d "{
  \"appName\": \"$APP_NAME\",
    \"userId\": \"$USER_ID\",
    \"sessionId\": \"$SESSION_ID\",
    \"newMessage\": {
      \"role\": \"user\",
      \"parts\": [{
      \"text\": \"specifically in Kenton area of Harrow\"
      }]
    }
}")

echo "Full response 2"
echo "$RESPONSE"