import os
import requests
from flask import Flask, send_from_directory, abort

app = Flask(__name__)
BASE_DIR = "/data"
REMOTE_BASE_URL = os.environ.get("REMOTE_BASE_URL", "https://download.jetbrains.com")

os.makedirs(BASE_DIR, exist_ok=True)

@app.route('/<path:filename>')
def fetch_or_serve(filename):
    local_path = os.path.join(BASE_DIR, filename)
    
    # If file exists, serve it
    if os.path.isfile(local_path):
        return send_from_directory(BASE_DIR, filename)

    # Create dirs if needed
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    # Remote download URL
    remote_url = f"{REMOTE_BASE_URL}/{filename}"
    try:
        print(f"Downloading {remote_url}...")
        r = requests.get(remote_url, stream=True)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"Saved to {local_path}")
            return send_from_directory(BASE_DIR, filename)
        else:
            print(f"Failed to fetch: {r.status_code}")
            abort(404)
    except Exception as e:
        print(f"Error: {e}")
        abort(500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
