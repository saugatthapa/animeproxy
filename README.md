# 🧊 Proxify Streams

A high-performance, unified stream proxy aggregator that consolidates multiple streaming providers into a single, clean Flask API. Aggregate XOR, Base64, and JSON-based proxy logic for Miruro, Anikuro, LunarAnime, and Animanga with zero latency.

![Proxify Streams](https://img.shields.io/badge/Status-Live-34d399?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-818cf8?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-a78bfa?style=for-the-badge&logo=flask&logoColor=white)

---

## ⚡ Features

- **Unified Endpoint**: One request returns proxied URLs from 4 different providers.
- **Complex Encoding**: Handles XOR ciphers (16-byte), Base64URL, and JSON-wrapped headers automatically.
- **Protocol Repair**: Auto-fixes common URL malformations (e.g., `https:/` normalization).
- **Minimalist Documentation**: Premium 3D-styled documentation page served directly from the root.
- **Cross-Platform**: Works anywhere Python and Flask can run.

---

## 🛠️ Tech Stack

- **Backend**: Python / Flask
- **Frontend (Docs)**: HTML5, Vanilla CSS (Glassmorphism), 3D CSS Transforms
- **Fonts**: Inter & JetBrains Mono (Google Fonts)

---

## 🚀 Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/proxify-streams.git
   cd proxify-streams
   ```

2. Install dependencies:
   ```bash
   pip install flask
   ```

3. Start the server:
   ```bash
   python server.py
   ```

The server will be available at `http://127.0.0.1:5555`.

---

## 📖 API Usage

### Root Documentation
Simply navigate to the root URL in your browser to view the interactive documentation:
`http://127.0.0.1:5555/`

### Proxy Endpoint
**GET** `/proxy?data={url}|{referer}`

**Example:**
```bash
curl "http://127.0.0.1:5555/proxy?data=https://example.com/stream.m3u8|https://referer.com/"
```

**Response:**
```json
{
  "proxifiedSource": {
    "miruro": "https://pro.ultracloud.cc/...",
    "anikuro": "https://proxy.anikuro.to/...",
    "lunaranime": "https://cluster.lunaranime.ru/...",
    "animanga": "https://upcloud.animanga.fun/..."
  }
}
```

---

## 🧩 Provider Algorithms

| Provider | Encoding Method | Details |
| :--- | :--- | :--- |
| **Miruro** | XOR + Base64url | 16-byte XOR cipher using a static hex key. |
| **Anikuro** | Base64 + Extension | Concatenates `url\|ref` and appends `.m3u8`/`.mp4`. |
| **LunarAnime** | URL Encoding | Clean percent-encoding pass-through. |
| **Animanga** | JSON Headers | Passes referer inside a JSON-encoded header object. |

---

## ⚠️ Disclaimers & Notes

### 1. Compatibility
**Not every provider supports every URL.** 
Each streaming provider has its own internal whitelist or supported CDN sources. If a provider returns a link that doesn't play, it likely means that specific source is not compatible with their proxy cluster. 

### 2. Hosting & Cloudflare
When you host this API (Vercel, Railway, Heroku, etc.), your server's IP becomes the "requester." Many of these providers or origin CDNs use **Cloudflare** or other anti-bot protections. 
- If your hosting provider's IP range is flagged, you might get **403 Forbidden** or **429 Too Many Requests**.
- **This is entirely up to you to manage.** You may need to use rotating residential proxies or different hosting regions to bypass these blocks.

### 3. Usage
¯\\_(ツ)_/¯ Use it for educational purposes. We are not responsible for how you use these proxied links or if they stop working due to provider-side changes.

---

Built by Waltuh 🥀
