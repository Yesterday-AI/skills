#!/bin/bash

# Exa Search — Semantic web search with full-text results
# Usage: ./search.sh "query" [num_results]
#
# Requires: EXA_API_KEY env var or ~/.openclaw/secrets/exa.key

QUERY="$1"
NUM="${2:-5}"

if [ -z "$QUERY" ]; then
  echo "Usage: ./search.sh \"query\" [num_results]"
  exit 1
fi

# Resolve API key
if [ -z "$EXA_API_KEY" ]; then
  KEY_FILE="${HOME}/.openclaw/secrets/exa.key"
  if [ -f "$KEY_FILE" ]; then
    EXA_API_KEY="$(cat "$KEY_FILE")"
  else
    echo "Error: EXA_API_KEY not set and $KEY_FILE not found."
    exit 1
  fi
fi

# Build JSON payload
JSON_PAYLOAD=$(jq -n \
  --arg q "$QUERY" \
  --argjson n "$NUM" \
  '{
    query: $q,
    type: "auto",
    num_results: $n,
    use_autoprompt: true,
    contents: {
      text: { max_characters: 5000 }
    }
  }')

# Execute
curl -s -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD"
