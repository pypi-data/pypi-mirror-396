#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

echo "Starting Ollama server..."
ollama serve &
PID=$!

echo "Waiting for Ollama server to be active..."
timeout=60
counter=0
while ! ollama list > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        echo "Timed out waiting for Ollama server."
        exit 1
    fi
    sleep 1
    counter=$((counter+1))
done
echo "Ollama server is active."

if [ -n "${OLLAMA_MODEL:-}" ]; then
    echo "Pulling model: ${OLLAMA_MODEL}"
    ollama pull "${OLLAMA_MODEL}"
    echo "Model ${OLLAMA_MODEL} pulled successfully."
else
    echo "OLLAMA_MODEL not set, skipping pull."
fi

wait $PID
