import os
import requests
from flask import Flask, send_file, abort, Response

app = Flask(__name__)
BASE_DIR = "/data"
REMOTE_BASE_URL = os.environ.get("REMOTE_BASE_URL", "https://here.com")

os.makedirs(BASE_DIR, exist_ok=True)

@app.route('/<path:filename>')
def fetch_or_serve(filename):
    local_path = os.path.join(BASE_DIR, filename)

    # If file is cached, serve with correct headers
    if os.path.isfile(local_path):
        return serve_with_size(local_path, filename)

    # Create subdirs
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    remote_url = f"{REMOTE_BASE_URL}/{filename}"

    try:
        # HEAD for content length
        head = requests.head(remote_url, timeout=5)
        if head.status_code != 200 or 'Content-Length' not in head.headers:
            abort(404)

        total_size = int(head.headers['Content-Length'])
        print(f"Downloading {filename} ({total_size / (1024 * 1024):.2f} MB)")

        # Download
        with requests.get(remote_url, stream=True, timeout=10) as r:
            if r.status_code != 200:
                abort(404)
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

        return serve_with_size(local_path, filename)

    except Exception as e:
        print(f"Error: {e}")
        abort(500)


def serve_with_size(path, filename):
    size = os.path.getsize(path)
    headers = {
        "Content-Length": str(size),
        "Content-Disposition": f"attachment; filename={os.path.basename(filename)}"
    }
    return send_file(path, as_attachment=True, download_name=os.path.basename(filename), headers=headers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
