import os
import sys

# Ensure the root project directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Disable reloader if needed, but debug=True is fine for development
    app.run(host='0.0.0.0', port=port, debug=True)
