# html2pdfconverter Python SDK

Lightweight Python client for `https://api.html2pdfconverter.com`. Mirrors the Node SDK features: create conversion jobs from HTML, URLs, or local files; poll for completion; download PDFs to memory or disk; and verify webhooks.

## Installation

```bash
pip install html2pdfconverter
```

## Quickstart

```python
from html2pdfconverter import PdfClient

client = PdfClient(api_key="YOUR_API_KEY")

# Convert a URL and get PDF bytes
pdf_bytes = client.convert({"url": "https://example.com"})

# Convert inline HTML and save directly to disk
output_path = client.convert(
    {
        "html": "<h1>Hello</h1>",
        "pdf_options": {"format": "A4"},
        "save_to": "output.pdf",
    }
)

# Submit a job with webhook (returns jobId immediately)
job_id = client.convert({"url": "https://example.com", "webhook_url": "https://yourapp.com/webhook"})
```

## API

### `PdfClient(options)`
- `api_key` (str, required): Your API key.
- `base_url` (str, optional): Defaults to `https://api.html2pdfconverter.com`.
- `webhook_secret` (str, optional): Required for webhook verification.

### `convert(options) -> bytes | str`
Creates a conversion job. Accepts one of:
- `html` (str): Raw HTML string.
- `url` (str): URL to render.
- `file_path` (str): Path to an HTML file.

Optional:
- `pdf_options` (dict): Options passed through to the service.
- `webhook_url` (str): If provided, returns `jobId` immediately and expects webhook delivery.
- `poll_interval_ms` (int): Poll cadence, default `2000`.
- `timeout_ms` (int): Poll timeout, default `300000`.
- `save_to` (str): Path to write the PDF. Returns the path when set; otherwise returns PDF bytes.

### `get_job(job_id, options) -> bytes | str`
Polls for job completion and downloads the PDF (similar options to `convert`).

### `verify_webhook(raw_body, signature) -> dict`
Validates webhook signatures using the `webhook_secret` provided to the client and returns the parsed JSON payload.

## Webhook verification example

```python
from flask import Flask, request, abort
from html2pdfconverter import PdfClient

client = PdfClient(api_key="YOUR_API_KEY", webhook_secret="WEBHOOK_SECRET")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("x-webhook-signature")
    try:
        payload = client.verify_webhook(request.data, signature)
    except Exception:
        abort(400)
    # handle payload...
    return "", 200
```

## Notes

- Retries are automatically applied to transient `502` responses.
- When sending inline HTML, a temporary file is created and cleaned up automatically before upload.
- The download step streams to disk when `save_to` is provided to avoid loading large PDFs into memory.

