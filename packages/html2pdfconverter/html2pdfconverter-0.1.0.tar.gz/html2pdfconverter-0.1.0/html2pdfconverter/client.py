import hashlib
import hmac
import json
import os
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Union

import requests
from requests import Response, Session


@dataclass
class PdfClientOptions:
    api_key: str
    base_url: str = "https://api.html2pdfconverter.com"
    webhook_secret: Optional[str] = None


@dataclass
class PdfConvertOptions:
    html: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None
    pdf_options: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None
    poll_interval_ms: int = 2000
    timeout_ms: int = 300000
    save_to: Optional[str] = None


@dataclass
class PdfJobResponse:
    jobId: str
    status: str
    downloadUrl: Optional[str] = None
    errorMessage: Optional[str] = None


class PdfClient:
    """
    Python client for https://api.html2pdfconverter.com.
    Provides parity with the Node SDK: create conversion jobs, poll, download, and verify webhooks.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None, webhook_secret: Optional[str] = None):
        if not api_key:
            raise ValueError("Missing api_key")

        self.api_key = api_key
        self.base_url = (base_url or "https://api.html2pdfconverter.com").rstrip("/")
        self.webhook_secret = webhook_secret
        self.retry_attempts = 3
        self.retry_delay_ms = 1500

        self.session: Session = requests.Session()
        self.session.headers.update({"x-api-key": api_key})

    def convert(self, options: Union[PdfConvertOptions, Dict[str, Any]]) -> Union[bytes, str]:
        """
        Convert HTML/URL/File to PDF.
        Returns PDF bytes by default, or a file path when save_to is provided.
        When webhook_url is set, returns the jobId immediately without polling.
        """
        opts = self._normalize_options(options)
        html = opts.get("html")
        url = opts.get("url")
        file_path = opts.get("file_path")
        pdf_options = opts.get("pdf_options") or {}
        poll_interval_ms = opts.get("poll_interval_ms", 2000)
        timeout_ms = opts.get("timeout_ms", 300000)
        save_to = opts.get("save_to")
        webhook_url = opts.get("webhook_url")

        if not html and not url and not file_path:
            raise ValueError("You must provide html, url, or file_path")

        job_id: Optional[str] = None
        temp_path: Optional[str] = None

        if file_path or html:
            if html:
                fd, temp_path = tempfile.mkstemp(prefix="html2pdf-", suffix=".html")
                with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                    tmp.write(html)
                file_path = temp_path

            if not file_path:
                raise ValueError("No file path to send for conversion.")

            try:
                def upload() -> Response:
                    with open(file_path, "rb") as f:
                        files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
                        data = {"options": json.dumps(pdf_options)}
                        if webhook_url:
                            data["webhookUrl"] = webhook_url
                        return self.session.post(f"{self.base_url}/convert", data=data, files=files)

                response = self._with_retry(upload, "PDF conversion upload")
                body = self._json(response)
                job_id = body.get("jobId")
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            payload: Dict[str, Any] = {"url": url, "options": pdf_options}
            if webhook_url:
                payload["webhookUrl"] = webhook_url

            response = self._with_retry(
                lambda: self.session.post(f"{self.base_url}/convert", json=payload),
                "PDF conversion create job",
            )
            body = self._json(response)
            job_id = body.get("jobId")

        if not job_id:
            raise RuntimeError("Failed to create conversion job")

        if webhook_url:
            return job_id

        return self.get_job(job_id, poll_interval_ms=poll_interval_ms, timeout_ms=timeout_ms, save_to=save_to)

    def get_job(
        self,
        job_id: str,
        poll_interval_ms: int = 2000,
        timeout_ms: int = 900000,
        save_to: Optional[str] = None,
    ) -> Union[bytes, str]:
        """
        Poll job status and download PDF when ready.
        Returns bytes by default or the file path when save_to is provided.
        """
        start = time.time()

        while True:
            response = self._with_retry(
                lambda: self.session.get(f"{self.base_url}/jobs/{job_id}"),
                "PDF job poll",
            )
            job: Dict[str, Any] = self._json(response)
            status = job.get("status")
            download_url = job.get("downloadUrl")

            if status == "completed" and download_url:
                if save_to:
                    self._download_to_file(download_url, save_to)
                    return save_to
                return self._download_to_bytes(download_url)

            if status == "failed":
                message = job.get("errorMessage") or "Unknown error"
                raise RuntimeError(f"PDF conversion failed: {message}")

            if (time.time() - start) * 1000 > timeout_ms:
                raise TimeoutError(f"PDF conversion timed out after {timeout_ms / 1000} seconds waiting for completion")

            time.sleep(poll_interval_ms / 1000.0)

    def verify_webhook(self, raw_body: Union[bytes, str], signature: str) -> Dict[str, Any]:
        """
        Verify webhook authenticity and return parsed payload.
        """
        if not self.webhook_secret:
            raise ValueError("Missing webhook_secret in PdfClient constructor")

        if raw_body is None:
            raise ValueError("raw_body is required for verification")
        if not signature:
            raise ValueError("signature is required for verification")

        body_bytes = raw_body if isinstance(raw_body, (bytes, bytearray)) else str(raw_body).encode("utf-8")
        expected_sig = "sha256=" + hmac.new(self.webhook_secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

        if expected_sig != signature:
            raise ValueError("Invalid webhook signature")

        try:
            return json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON in webhook payload") from exc

    # --- helpers ---

    def _download_to_bytes(self, url: str) -> bytes:
        response = self._with_retry(
            lambda: self.session.get(url, stream=False),
            "PDF download buffer",
        )
        return response.content

    def _download_to_file(self, url: str, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        response = self._with_retry(
            lambda: self.session.get(url, stream=True),
            "PDF download stream",
        )
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    def _with_retry(self, operation: Callable[[], Response], context: str) -> Response:
        attempt = 0
        last_error: Optional[Exception] = None
        retryable_statuses = {502, 503, 504}

        while attempt <= self.retry_attempts:
            try:
                response = operation()
                status = response.status_code

                if status in retryable_statuses and attempt < self.retry_attempts:
                    time.sleep(self.retry_delay_ms / 1000.0)
                    attempt += 1
                    continue

                if status >= 400:
                    self._raise_for_status(response, context)
                return response
            except requests.RequestException as error:
                last_error = error
                status = error.response.status_code if getattr(error, "response", None) else None
                should_retry = status in retryable_statuses
                has_attempts_left = attempt < self.retry_attempts

                if should_retry and has_attempts_left:
                    time.sleep(self.retry_delay_ms / 1000.0)
                    attempt += 1
                    continue

                if isinstance(error, requests.HTTPError):
                    raise RuntimeError(
                        f"{context} failed (status: {status or 'unknown'}): {self._extract_error_message(error.response)}"
                    ) from error

                raise RuntimeError(f"{context} failed: {error}") from error

        if last_error:
            raise last_error
        raise RuntimeError(f"{context} failed for an unknown reason")

    def _raise_for_status(self, response: Response, context: str) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            status = response.status_code
            message = self._extract_error_message(response)
            raise RuntimeError(f"{context} failed (status: {status}): {message}") from error

    def _extract_error_message(self, response: Optional[Response]) -> str:
        if not response:
            return "Unknown error"
        try:
            data = response.json()
            return str(data.get("message") or data)
        except ValueError:
            return response.text or "Unknown error"

    def _json(self, response: Response) -> Dict[str, Any]:
        try:
            return response.json()
        except ValueError as exc:
            raise RuntimeError("Unexpected non-JSON response from API") from exc

    def _normalize_options(self, options: Union[PdfConvertOptions, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(options, PdfConvertOptions):
            return {
                "html": options.html,
                "url": options.url,
                "file_path": options.file_path,
                "pdf_options": options.pdf_options,
                "webhook_url": options.webhook_url,
                "poll_interval_ms": options.poll_interval_ms,
                "timeout_ms": options.timeout_ms,
                "save_to": options.save_to,
            }
        if not isinstance(options, dict):
            raise TypeError("options must be a dict or PdfConvertOptions")
        return options

