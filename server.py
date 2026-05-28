import base64, os
import requests as http_requests
from flask import Flask, jsonify, request, send_from_directory, Response as FlaskResponse
from werkzeug.routing import BaseConverter
from urllib.parse import quote, unquote, urljoin

class EverythingConverter(BaseConverter):
    regex = '.*'

app = Flask(__name__)
app.url_map.converters['everything'] = EverythingConverter

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    return response

class ProxyGenerator:
    def __init__(self):
        self.miruro_key = bytes.fromhex("a54d389c18527d9fd3e7f0643e27edbe")

    def miruro(self, url, referer):
        def encode_param(text):
            b = text.encode('utf-8')
            c = bytes([b[i] ^ self.miruro_key[i % 16] for i in range(len(b))])
            return base64.urlsafe_b64encode(c).decode('utf-8').rstrip('=')
        return f"https://pro.ultracloud.cc/m3u8/?u={encode_param(url)}&r={encode_param(referer)}"

    def anikuro(self, url, referer):
        b64 = base64.b64encode(f"{url}|{referer}".encode()).decode()
        ext = ".m3u8" if ".m3u8" in url.lower() else ".mp4"
        return f"https://proxy.anikuro.to/{b64}{ext}"

    def lunaranime(self, url, referer):
        return f"https://cluster.lunaranime.ru/api/proxy/hls/custom?url={quote(url, safe=':/')}&referer={quote(referer, safe=':/')}"

    def animanga(self, url, referer):
        import json
        headers = json.dumps({"Referer": referer, "User-Agent": DEFAULT_USER_AGENT})
        return f"https://upcloud.animanga.fun/proxy?url={quote(url, safe=':/')}&headers={quote(headers, safe=':/')}"

    def animekai(self, url, referer):
        return self.animanga(url, referer)

    def reanime(self, url, _referer=None):
        """Real byte-level proxy for flixcloud HLS streams.
        Returns a URL to this same server which fetches the stream with
        the correct Referer header (browsers can't set Referer cross-origin).
        """
        proxy_base = request.scheme + "://" + request.host
        return f"{proxy_base}/reanime-proxy?url={quote(url, safe='')}"

generator = ProxyGenerator()

# ── Byte-level proxy for Re:ANIME / Flixcloud ─────────────────────────────────

@app.route('/reanime-proxy')
def reanime_proxy():
    """Fetch flixcloud HLS content with Referer: https://reanime.to/ header.
    Rewrites m3u8 playlists so segment requests also route through this proxy.
    """
    url = request.args.get('url', '')
    if not url:
        return jsonify({"error": "No url provided"}), 400

    headers = {
        "Referer": "https://reanime.to/",
        "User-Agent": DEFAULT_USER_AGENT,
    }

    try:
        resp = http_requests.get(url, headers=headers, timeout=25)
        resp.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Fetch failed: {type(e).__name__}: {str(e)[:100]}"}), 502

    ctype = resp.headers.get('content-type', '')

    # Rewrite m3u8 so all segment URLs route back through this proxy
    if 'm3u8' in ctype or url.endswith('.m3u8'):
        base = url.rsplit('/', 1)[0]
        lines = []
        for line in resp.text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                lines.append(stripped)
            else:
                abs_url = urljoin(base, stripped)
                lines.append(f"/reanime-proxy?url={quote(abs_url)}")
        content = '\n'.join(lines)
        return FlaskResponse(content, mimetype=ctype or 'application/vnd.apple.mpegurl')

    return FlaskResponse(resp.content, mimetype=ctype or 'application/octet-stream')


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def docs():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/health')
def health():
    return jsonify({"ok": True, "providers": ["animekai", "animanga", "anikuro", "lunaranime", "miruro", "reanime"]})

@app.route('/proxy/<everything:data>')
@app.route('/proxy')
def get_proxy(data=None):
    try:
        if not data:
            data = request.args.get('data')
        if not data:
            return jsonify({"error": "No data provided"}), 400

        data = unquote(data)

        if "https:/" in data and "https://" not in data:
            data = data.replace("https:/", "https://")
        elif "http:/" in data and "http://" not in data:
            data = data.replace("http:/", "http://")

        if "|" not in data:
            return jsonify({"error": "Invalid format (expected url|referer)", "received": data}), 400

        url, referer = data.rsplit("|", 1)

        return jsonify({
            "proxifiedSource": {
                "reanime": generator.reanime(url),
                "animekai": generator.animekai(url, referer),
                "miruro": generator.miruro(url, referer),
                "anikuro": generator.anikuro(url, referer),
                "lunaranime": generator.lunaranime(url, referer),
                "animanga": generator.animanga(url, referer),
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=False)

app = app
