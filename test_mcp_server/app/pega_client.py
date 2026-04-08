from __future__ import annotations

from typing import Any

import httpx
import base64
import tempfile
import os
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper


class PegaClientError(RuntimeError):
    """Exception raised for Pega API errors"""
    pass


class TemporaryFileServer:
    """Simple HTTP server to serve temporary files for Pega attachments"""

    def __init__(self):
        self.server = None
        self.port = None
        self.temp_dir = tempfile.mkdtemp(prefix="pega_attachments_")
        self.files = {}  # filename -> file_path mapping

    def start(self):
        """Start the file server on an available port"""
        if self.server:
            return

        # Find an available port
        for port in range(8081, 8181):  # Try ports 8081-8180
            try:
                self.server = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
                self.server.timeout = 1  # Short timeout for serving
                self.port = port
                break
            except OSError:
                continue

        if not self.server:
            raise RuntimeError("Could not find an available port for file server")

        # Change to temp directory
        os.chdir(self.temp_dir)

        # Start server in background thread
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

    def stop(self):
        """Stop the file server and clean up"""
        if self.server:
            self.server.shutdown()
            self.server = None

        # Clean up temp files
        for file_path in self.files.values():
            try:
                os.unlink(file_path)
            except:
                pass

        try:
            os.rmdir(self.temp_dir)
        except:
            pass

    def _run_server(self):
        """Run the server (called in background thread)"""
        try:
            self.server.serve_forever()
        except:
            pass  # Server was shut down

    def add_file(self, filename: str, content: str) -> str:
        """Add a base64 encoded file and return its URL"""
        if not self.server:
            self.start()

        # Decode base64 content
        file_data = base64.b64decode(content)

        # Save to temp file
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)

        self.files[filename] = file_path

        # Return the URL
        return f"http://localhost:{self.port}/{filename}"


class PegaCaseClient:
    def __init__(self, settings: PegaSettings, token_helper: PegaTokenHelper) -> None:
        self._settings = settings
        self._token_helper = token_helper
        self._client = httpx.AsyncClient(
            base_url=settings.pega_application_api_base,
            timeout=settings.request_timeout_seconds,
        )
        self._file_server = TemporaryFileServer()

    def cleanup(self):
        """Clean up resources including the file server"""
        if hasattr(self, '_file_server'):
            self._file_server.stop()
 
    async def create_case(
        self,
        payload: dict[str, Any],
        view_type: str = "none",
        page_name: str | None = None,
        origin_channel: str | None = None,
    ) -> dict[str, Any]:
        return await self._request_json(
            "POST",
            "/cases",
            params=self._compact_params({"viewType": view_type, "pageName": page_name}),
            headers_extra=self._compact_headers({"x-origin-channel": origin_channel}),
            json=payload,
        )

    async def add_attachment(
        self,
        case_id: str,
        file_name: str,
        file_content: str | None = None,
        attachment_url: str | None = None,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        content_type = content_type or "application/octet-stream"

        # Prefer explicit attachment URL when provided
        if attachment_url:
            final_attachment_url = attachment_url
        # Handle direct URL passed in file_content
        elif file_content and file_content.startswith(('http://', 'https://')):
            # If it's already a URL, use it directly
            final_attachment_url = file_content
        elif file_content:
            # For base64 content, create a temporary file and get its URL
            final_attachment_url = self._file_server.add_file(file_name, file_content)
        else:
            raise ValueError("Either file_content or attachment_url must be provided")

        payload = {
            "attachments": [
                {
                    "type": "URL",
                    "name": file_name,
                    "pyLabel": file_name,
                    "url": final_attachment_url,
                    "category": "URL",
                    "contentType": content_type,
                }
            ]
        }
        return await self._request_json(
            "POST",
            f"/cases/{case_id}/attachments",
            json=payload,
        )

    async def _request_json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        headers_extra = kwargs.pop("headers_extra", {})
        headers = self._headers(await self._token_helper.get_valid_token())
        headers.update(headers_extra)
 
        response = await self._client.request(method, path, headers=headers, **kwargs)
 
        if response.status_code == 401:
            new_token = await self._token_helper.force_new_token()
            headers["Authorization"] = f"Bearer {new_token}"
            response = await self._client.request(method, path, headers=headers, **kwargs)
 
        if response.status_code >= 400:
            body = response.text[:500]
            raise PegaClientError(
                f"Pega API request failed with status {response.status_code}: {body}"
            )
 
        if response.status_code == 204 or not response.content:
            return {"status": "ok", "status_code": response.status_code}
 
        payload = response.json()
        if isinstance(payload, dict):
            return payload
        return {"data": payload}
 
    @staticmethod
    def _headers(token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
 
    @staticmethod
    def _compact_params(values: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in values.items() if v is not None}
 
    @staticmethod
    def _compact_headers(values: dict[str, Any]) -> dict[str, str]:
        return {k: str(v) for k, v in values.items() if v is not None}