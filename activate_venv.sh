#!/bin/bash

# Check if .venv exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "Venv activated. You can now run 'dbt' and 'python' commands."
else
    echo "Error: .venv directory not found. Please run 'uv venv' first."
fi
