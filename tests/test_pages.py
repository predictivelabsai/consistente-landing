"""
Boots the FastHTML app in a subprocess, visits each route with Playwright
(sync API), writes a full-page screenshot into screenshots/, and asserts the
expected h1 is present.

Run:
    pip install playwright pytest
    python -m playwright install chromium
    python -m pytest tests/test_pages.py -v
"""

import subprocess
import time
import socket
from pathlib import Path

import pytest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pytest.skip("playwright not installed", allow_module_level=True)


ROOT = Path(__file__).parent.parent
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

HOST = "127.0.0.1"
PORT = 5011

ROUTES = [
    ("/", "home", "enterprise scale"),
    ("/team", "team", "small group"),
    ("/contact", "contact", "programme"),
]


def _wait_for_port(host: str, port: int, timeout: float = 15.0):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket() as s:
            try:
                s.connect((host, port))
                return
            except OSError:
                time.sleep(0.2)
    raise TimeoutError(f"server on {host}:{port} did not come up")


@pytest.fixture(scope="session")
def server():
    env_cmd = [".venv/bin/python", "-c", f"import os; os.environ.setdefault('PORT','{PORT}'); import main; main.serve(port={PORT})"]
    proc = subprocess.Popen(
        env_cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_port(HOST, PORT)
        yield f"http://{HOST}:{PORT}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.mark.parametrize("path,slug,expected", ROUTES)
def test_route(server, path, slug, expected):
    url = f"{server}{path}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")

        h1_text = page.locator("h1").first.inner_text()
        assert expected.lower() in h1_text.lower(), f"{path}: h1 '{h1_text}' does not contain '{expected}'"

        page.screenshot(path=str(SCREENSHOTS / f"test-{slug}.png"), full_page=True)
        browser.close()
