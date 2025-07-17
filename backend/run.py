#!/usr/bin/env python3
"""
Entry point script to ensure proper Python path setup
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the app
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)