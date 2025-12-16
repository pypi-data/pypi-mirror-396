#!/bin/bash

set -o errexit
set -o nounset

# Start Ollama server in the background
ollama serve &

# Wait for the server to be ready
sleep 5

# Pull the model if OLLAMA_MODEL is set
if [ -n "${OLLAMA_MODEL:-}" ]; then
    echo "Pulling model: ${OLLAMA_MODEL}"
    ollama pull "${OLLAMA_MODEL}"
fi

# Keep the container running by waiting for the background process
wait
