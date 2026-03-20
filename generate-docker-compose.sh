#!/bin/bash
# DEPRECATED: This script is now a wrapper around generate_compose.py
# The Python version provides better maintainability and testability.
# Use: python3 generate_compose.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Note: Using Python-based compose generator (generate_compose.py)"
python3 "${SCRIPT_DIR}/generate_compose.py"
