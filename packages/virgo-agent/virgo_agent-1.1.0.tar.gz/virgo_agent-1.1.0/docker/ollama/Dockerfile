FROM ollama/ollama:latest

# Copy start script and make it executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Override the default entrypoint so we can run our script
ENTRYPOINT []
CMD ["/start.sh"]
