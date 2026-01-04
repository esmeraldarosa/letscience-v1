#!/bin/bash
echo "Starting BioPharma Intelligence Platform..."
echo "Ensure you have the virtual environment activated if not already."
echo "If not: source venv/bin/activate"
echo ""
echo "Server will start at http://127.0.0.1:8000/app/index.html"
# Run uvicorn
# We assume the script is run from BioPharma_Intel root
uvicorn backend.main:app --reload
