#!/bin/bash
# Run auth server in background
python auth.py &
AUTH_PID=$!

# Run Gradio dashboard
python dashboard/app.py &
GRADIO_PID=$!

# Wait for both
wait $AUTH_PID $GRADIO_PID
