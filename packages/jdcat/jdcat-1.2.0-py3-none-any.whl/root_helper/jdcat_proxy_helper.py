"""
JDcat Root Proxy Helper
Minimal HTTP server running as root (via launchd) to control macOS HTTP/HTTPS system proxy.
Exposes:
- GET /health -> 200 ok
- POST /enable -> body: {host, port, services:[], bypass:[]}
- POST /restore -> body: {services:[]}
Constraints:
- Bind to 127.0.0.1 only
- Use absolute /usr/sbin/networksetup commands
- Drop environment variables for subprocess calls (minimal PATH)
- Allow only fixed subcommand set
"""
from __future__ import annotations

import json
import logging
import argparse
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Any, Dict, List

_logger = logging.getLogger("jdcat.root_proxy_helper")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    _h = logging.StreamHandler()
    _h.setLevel(logging.INFO)
    _h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
    _logger.addHandler(_h)

NETWORKSETUP = "/usr/sbin/networksetup"
ALLOWED_SUBCOMMANDS = {
    "-setwebproxy",
    "-setsecurewebproxy",
    "-setwebproxystate",
    "-setsecurewebproxystate",
    "-setproxybypassdomains",
}

def _minimal_env() -> Dict[str, str]:
    # Provide minimal environment; avoid inheriting user env
    return {"PATH": "/usr/sbin:/usr/bin:/bin"}

def _run_networksetup(args: List[str]) -> tuple[int, str, str]:
    """
    Run networksetup with absolute path and minimal env.
    """
    if not args or args[0] != NETWORKSETUP:
        return 1, "", "invalid binary path"
    if len(args) < 2 or args[1] not in ALLOWED_SUBCOMMANDS:
        return 1, "", "subcommand not allowed"
    try:
        p = subprocess.run(args, capture_output=True, text=True, env=_minimal_env())
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        return int(p.returncode or 0), out, err
    except Exception as e:
        return 1, "", str(e)

class _JSONResponseMixin:
    def _send_json(self, code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

class RootProxyHelperHandler(_JSONResponseMixin, BaseHTTPRequestHandler):
    server_version = "JDcatProxyHelper/1.0"

    def log_message(self, format: str, *args) -> None:
        # Reduce noise; rely on _logger
        _logger.info("[helper] " + format, *args)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except Exception:
            length = 0
        raw = b""
        if length > 0:
            try:
                raw = self.rfile.read(length)
            except Exception:
                raw = b""
        try:
            body = json.loads(raw.decode("utf-8") if raw else "{}")
            if not isinstance(body, dict):
                body = {}
        except Exception as e:
            self._send_json(400, {"ok": False, "error": f"invalid json: {e}"})
            return

        if self.path == "/enable":
            self._handle_enable(body)
            return
        if self.path == "/restore":
            self._handle_restore(body)
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def _handle_enable(self, body: Dict[str, Any]) -> None:
        host = str(body.get("host") or "").strip()
        port = int(body.get("port") or 0)
        services = body.get("services") or []
        bypass = body.get("bypass") or []
        if not isinstance(services, list):
            services = []
        if not isinstance(bypass, list):
            bypass = []
        if not host or not port or port <= 0 or not services:
            self._send_json(400, {"ok": False, "error": "missing required fields: host, port, services"})
            return

        # Execute per service
        for svc in services:
            svc_name = str(svc).strip()
            if not svc_name:
                continue
            cmds = [
                [NETWORKSETUP, "-setwebproxy", svc_name, host, str(port)],
                [NETWORKSETUP, "-setsecurewebproxy", svc_name, host, str(port)],
                [NETWORKSETUP, "-setwebproxystate", svc_name, "on"],
                [NETWORKSETUP, "-setsecurewebproxystate", svc_name, "on"],
            ]
            # Bypass only if provided
            if bypass:
                bypass_args = [NETWORKSETUP, "-setproxybypassdomains", svc_name] + [str(d).strip() for d in bypass if str(d).strip()]
                if len(bypass_args) > 3:
                    cmds.append(bypass_args)
            for args in cmds:
                code, out, err = _run_networksetup(args)
                _logger.info("[enable] svc=%s cmd=%s code=%s err=%s", svc_name, " ".join(args), code, (err or "")[:200])
                if code != 0:
                    self._send_json(500, {"ok": False, "service": svc_name, "error": err or out or "failed"})
                    return

        self._send_json(200, {"ok": True, "services": [str(s).strip() for s in services if str(s).strip()], "host": host, "port": port, "bypass": bypass})

    def _handle_restore(self, body: Dict[str, Any]) -> None:
        services = body.get("services") or []
        if not isinstance(services, list) or not services:
            self._send_json(400, {"ok": False, "error": "missing required field: services"})
            return
        for svc in services:
            svc_name = str(svc).strip()
            if not svc_name:
                continue
            cmds = [
                [NETWORKSETUP, "-setwebproxystate", svc_name, "off"],
                [NETWORKSETUP, "-setsecurewebproxystate", svc_name, "off"],
            ]
            for args in cmds:
                code, out, err = _run_networksetup(args)
                _logger.info("[restore] svc=%s cmd=%s code=%s err=%s", svc_name, " ".join(args), code, (err or "")[:200])
                if code != 0:
                    self._send_json(500, {"ok": False, "service": svc_name, "error": err or out or "failed"})
                    return
        self._send_json(200, {"ok": True, "services": [str(s).strip() for s in services if str(s).strip()]})

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="JDcat Root Proxy Helper")
    parser.add_argument("--port", type=int, default=17901, help="listen port (default: 17901)")
    args = parser.parse_args(argv)
    host = "127.0.0.1"
    port = int(args.port or 17901)
    if port <= 0:
        port = 17901
    srv = ThreadingHTTPServer((host, port), RootProxyHelperHandler)
    _logger.info("Starting JDcat Proxy Helper on %s:%s", host, port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
       _logger.info("Shutting down JDcat Proxy Helper")
       try:
           srv.shutdown()
       except Exception:
           pass

if __name__ == "__main__":
    main()