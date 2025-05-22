import os
import requests
from flask import Flask, Response, abort, stream_with_context

app = Flask(__name__)
BASE_DIR = "/data"
REMOTE_BASE_URL = os.environ.get("REMOTE_BASE_URL", "https://download-cdn.jetbrains.com")

os.makedirs(BASE_DIR, exist_ok=True)

@app.route('/<path:filename>')
def fetch_or_stream(filename):
    local_path = os.path.join(BASE_DIR, filename)

    # Serve cached file
    if os.path.isfile(local_path):
        print(f"Serving cached: {filename}", flush=True)
        return stream_local_file(local_path)

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    remote_url = f"{REMOTE_BASE_URL}/{filename}"

    try:
        print(f"Streaming and caching: {remote_url}", flush=True)

        head = requests.head(remote_url, timeout=5)
        if head.status_code != 200 or 'Content-Length' not in head.headers:
            abort(404)
        content_length = head.headers['Content-Length']

        r = requests.get(remote_url, stream=True, timeout=10)
        if r.status_code != 200:
            abort(404)

        def generate():
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        yield chunk

        return Response(
            stream_with_context(generate()),
            headers={
                "Content-Length": content_length,
                "Content-Disposition": f"attachment; filename={os.path.basename(filename)}"
            },
            mimetype='application/octet-stream'
        )

    except Exception as e:
        print(f"Error: {e}", flush=True)
        abort(500)


def stream_local_file(path):
    def generate():
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk

    size = os.path.getsize(path)
    return Response(
        stream_with_context(generate()),
        headers={
            "Content-Length": str(size),
            "Content-Disposition": f"attachment; filename={os.path.basename(path)}"
        },
        mimetype='application/octet-stream'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
