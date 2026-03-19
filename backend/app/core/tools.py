import json
import base64
import io
import socket
import requests
import time
from urllib.parse import urlparse, parse_qs

import yfinance as yf
import nmap
from duckduckgo_search import DDGS

from app.core.config import settings
from app.core.openai_client import get_openai_client


# --- 1) NETRUNNER (SECURITY) ---
# Use only permissioned targets.
def run_security_scan(target: str) -> str:
    try:
        parsed = urlparse(target)
        hostname = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
        if not hostname:
            return "Scan Error: Invalid target."

        ip = socket.gethostbyname(hostname)

        report = f"🛡️ SECURITY AUDIT: {hostname} ({ip})\n"

        nm = nmap.PortScanner()
        nm.scan(ip, arguments="-F")

        if ip in nm.all_hosts():
            report += "\nOpen Ports:\n"
            for proto in nm[ip].all_protocols():
                ports = nm[ip][proto].keys()
                for port in sorted(ports):
                    state = nm[ip][proto][port].get("state", "unknown")
                    service = nm[ip][proto][port].get("name", "unknown")
                    report += f"- Port {port} ({service}): {state.upper()}\n"
        else:
            report += "\nNo hosts found.\n"

        # Header check (best-effort)
        try:
            res = requests.get(f"https://{hostname}", timeout=4)
        except:
            try:
                res = requests.get(f"http://{hostname}", timeout=4)
            except:
                res = None

        if res:
            report += "\nSecurity Headers:\n"
            must = [
                "Strict-Transport-Security",
                "X-Frame-Options",
                "Content-Security-Policy"
            ]
            for h in must:
                if h in res.headers:
                    report += f"✅ {h}: Present\n"
                else:
                    report += f"⚠️ {h}: MISSING\n"

        return report

    except Exception as e:
        return f"Scan Error: {e}"


# --- 2) YOUTUBE ---
def get_youtube_transcript(url: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        if "youtu.be" in url:
            vid = url.split("/")[-1].split("?")[0]
        elif "youtube.com" in url:
            vid = parse_qs(urlparse(url).query).get("v", [None])[0]
        else:
            return "Invalid YouTube URL."

        if not vid:
            return "Invalid YouTube video id."

        try:
            data = YouTubeTranscriptApi.get_transcript(vid, languages=["en"])
        except:
            try:
                lst = YouTubeTranscriptApi.list_transcripts(vid)
                data = lst.find_transcript(["en"]).fetch()
            except:
                return "No English captions found."

        full = " ".join([t.get("text", "") for t in data])
        return f"TRANSCRIPT (trimmed):\n{full[:12000]}..."

    except Exception as e:
        return f"YouTube Error: {e}"


# --- 3) STOCKS ---
def get_stock_price(ticker: str) -> str:
    try:
        sym = ticker.upper().replace("$", "")
        t = yf.Ticker(sym)
        info = t.info or {}
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if price is None:
            return f"Stock not found: {sym}"
        cur = info.get("currency", "USD")
        return f"STOCK {sym}: {price} {cur}"
    except Exception:
        return "Stock Error."


# --- 4) WEB SEARCH ---
def web_search(query: str, max_results: int = 3) -> str:
    try:
        with DDGS() as ddgs:
            res = list(ddgs.text(query, max_results=max_results))
        if not res:
            return "No results."
        return "\n".join([f"- {r.get('title','')}: {r.get('body','')}" for r in res])
    except Exception:
        return "Search failed."


# --- 5) IMAGE (external, not local) ---
def generate_image(prompt: str) -> str:
    # External URL — label it honestly.
    safe = prompt.strip().replace(" ", "%20")
    return f"IMAGE_EXTERNAL: https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024"


# --- 6) GHOST MODE (optional + safe import) ---
def run_ghost_loop(objective: str) -> str:
    try:
        import pyautogui  # lazy import
        pyautogui.FAILSAFE = True

        client = get_openai_client()

        ss = pyautogui.screenshot()
        ss.thumbnail((1280, 1280))
        buf = io.BytesIO()
        ss.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        prompt = (
            "GUI Agent. Return JSON ONLY:\n"
            "{'thought': '...', 'actions': [{'type': 'click', 'x': 0, 'y': 0}]}\n"
            f"Goal: {objective}"
        )

        resp = client.chat.completions.create(
            model=settings.VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]
            }]
        )

        raw = resp.choices[0].message.content or ""
        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)
        thought = data.get("thought", "No thought.")
        return f"GHOST_OK: {thought}"

    except Exception as e:
        return f"Ghost Error: {e}"


def system_control(cmd: str):
    # Placeholder for future OS controls
    return None
