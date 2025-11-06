#!/bin/bash

# Flight Network Backend Startup Script
echo "🛫 Starting Flight Network Backend on port 5001..."

# Check if port 5001 is available
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 5001 is in use"
    echo "🔄 Please kill the process using port 5001:"
    echo "   lsof -ti:5001 | xargs kill -9"
    echo ""
    exit 1
else
    echo "✅ Port 5001 is available"
fi

# Start the backend
cd "$(dirname "$0")"
python app.py

echo "🏁 Backend startup complete"