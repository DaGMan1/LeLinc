import argparse
import json
import time
from pathlib import Path

import requests
import websocket

COOKIES_ROOT = Path("/cookies")

PLATFORM_ACTIONS = {
    "instagram": {
        "like": {"selector": "svg[aria-label='Like']"},
        "comment": {"selector": "textarea[aria-label='Add a comment…']"},
    },
    "linkedin": {
        "connect": {"selector": "button[aria-label^='Invite']"},
        "message": {"selector": "a[data-control-name='message']"},
    },
    "facebook": {
        "like": {"selector": "div[aria-label='Like']"},
        "comment": {"selector": "div[aria-label='Write a comment']"},
    },
    "tiktok": {
        "like": {"selector": "span[data-e2e='like-icon']"},
        "comment": {"selector": "div[data-e2e='comment-input']"},
    },
}


class CDPSession:
    def __init__(self, cdp_host: str = "127.0.0.1", cdp_port: int = 9222):
        self.cdp_host = cdp_host
        self.cdp_port = cdp_port
        self._msg_id = 0
        self.ws = None

    def _next_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    def connect(self, retries: int = 30, delay: float = 1.0):
        base = f"http://{self.cdp_host}:{self.cdp_port}"
        for _ in range(retries):
            try:
                targets = requests.get(f"{base}/json", timeout=2).json()
                page = next((t for t in targets if t.get("type") == "page"), None)
                if page is None:
                    page = requests.put(f"{base}/json/new").json()
                self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=10)
                return
            except Exception:
                time.sleep(delay)
        raise RuntimeError("Could not connect to Cloak Browser CDP")

    def send(self, method: str, params: dict | None = None) -> dict:
        msg = {"id": self._next_id(), "method": method, "params": params or {}}
        self.ws.send(json.dumps(msg))
        while True:
            resp = json.loads(self.ws.recv())
            if resp.get("id") == msg["id"]:
                return resp.get("result", {})

    def navigate(self, url: str):
        self.send("Page.enable")
        return self.send("Page.navigate", {"url": url})

    def screenshot(self) -> str:
        result = self.send("Page.captureScreenshot", {"format": "png"})
        return result.get("data", "")

    def click(self, selector: str):
        return self._run_js(f"document.querySelector({json.dumps(selector)})?.click()")

    def type_text(self, selector: str, text: str):
        js = (
            f"const el = document.querySelector({json.dumps(selector)});"
            f"if (el) {{ el.focus(); el.value = {json.dumps(text)}; "
            "el.dispatchEvent(new Event('input', {bubbles: true})); }"
        )
        return self._run_js(js)

    def _run_js(self, expression: str):
        return self.send("Runtime.evaluate", {"expression": expression})

    def set_cookies(self, cookies: list[dict]):
        return self.send("Network.setCookies", {"cookies": cookies})

    def close(self):
        if self.ws:
            self.ws.close()


def load_client_cookies(client_id: str, cdp_port: int = 9222):
    client_dir = COOKIES_ROOT / client_id
    if not client_dir.exists():
        return
    session = CDPSession(cdp_port=cdp_port)
    session.connect()
    try:
        session.send("Network.enable")
        for cookie_file in client_dir.glob("*.json"):
            record = json.loads(cookie_file.read_text())
            raw_cookies = record.get("cookies")
            if not raw_cookies:
                continue
            cookies = json.loads(raw_cookies) if isinstance(raw_cookies, str) else raw_cookies
            session.set_cookies(cookies)
    finally:
        session.close()


def platform_action(platform: str, action: str, cdp_port: int = 9222):
    spec = PLATFORM_ACTIONS.get(platform, {}).get(action)
    if spec is None:
        raise ValueError(f"No action '{action}' defined for platform '{platform}'")
    session = CDPSession(cdp_port=cdp_port)
    session.connect()
    try:
        return session.click(spec["selector"])
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Cloak Browser CDP handler")
    parser.add_argument("--wait-and-load-cookies", action="store_true")
    parser.add_argument("--client-id", default="default")
    parser.add_argument("--cdp-port", type=int, default=9222)
    args = parser.parse_args()

    if args.wait_and_load_cookies:
        load_client_cookies(args.client_id, cdp_port=args.cdp_port)


if __name__ == "__main__":
    main()
