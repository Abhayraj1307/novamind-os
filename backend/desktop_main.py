import webview
import threading
import uvicorn
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app


def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")


def main():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    time.sleep(1.2)

    webview.create_window(
        "NovaMind Sovereign OS",
        "http://127.0.0.1:8000",
        width=1280,
        height=850,
        resizable=True,
        background_color="#030305",
        text_select=True
    )
    webview.start()


if __name__ == "__main__":
    main()
