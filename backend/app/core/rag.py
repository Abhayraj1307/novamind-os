import json
import uuid

from app.core.config import settings
from app.core.openai_client import get_openai_client
from app.core.memory import save_msg, get_history, get_facts, save_fact

from app.core.tools import (
    web_search,
    generate_image,
    get_stock_price,
    get_youtube_transcript,
    run_security_scan,
    run_ghost_loop
)

from app.core.swarm import run_swarm_protocol


def _extract_tickers(text: str):
    tokens = []
    for w in text.replace(",", " ").split():
        sym = w.upper().replace("$", "").strip()
        if 1 <= len(sym) <= 6 and sym.isalnum():
            tokens.append(sym)
    return list(dict.fromkeys(tokens))


def answer_with_rag_stream(user_id: str, message: str, mode: str, chat_id: str, image_data=None):
    client = get_openai_client()
    text = (message or "").strip()

    if not chat_id or chat_id == "new":
        chat_id = str(uuid.uuid4())

    save_msg(chat_id, "user", text)

    # -------------------------
    # 1) EXPLICIT COMMAND MODES
    # -------------------------

    # Ghost mode
    if text.lower().startswith("/ghost "):
        objective = text.split(" ", 1)[1].strip()
        reply = run_ghost_loop(objective)
        yield reply
        save_msg(chat_id, "assistant", reply)
        return

    # Swarm mode
    if text.lower().startswith("/swarm"):
        swarm = run_swarm_protocol(text)
        if "logs" in swarm:
            vis = "START_SWARM_UI\n" + json.dumps(swarm["logs"]) + "\nEND_SWARM_UI\n"
            reply = f"{vis}\n{swarm.get('final_answer','')}"
        else:
            reply = swarm.get("final_answer", "Swarm done.")
        yield reply
        save_msg(chat_id, "assistant", reply)
        return

    # Security scan
    if text.lower().startswith("/scan "):
        target = text.split(" ", 1)[1].strip()
        if "." in target:
            report = run_security_scan(target)
            yield report
            save_msg(chat_id, "assistant", report)
            return
        else:
            reply = "Scan Error: Provide a valid domain or host."
            yield reply
            save_msg(chat_id, "assistant", reply)
            return

    # External image generation
    if text.lower().startswith("/image "):
        prompt = text.split(" ", 1)[1].strip()
        reply = generate_image(prompt)
        yield reply
        save_msg(chat_id, "assistant", reply)
        return

    # Stock quick command
    if text.lower().startswith("/stock "):
        sym = text.split(" ", 1)[1].strip()
        reply = get_stock_price(sym)
        yield reply
        save_msg(chat_id, "assistant", reply)
        return

    # YouTube quick command
    if text.lower().startswith("/youtube "):
        url = text.split(" ", 1)[1].strip()
        reply = get_youtube_transcript(url)
        yield reply
        save_msg(chat_id, "assistant", reply)
        return

    # Search quick command
    if text.lower().startswith("/search "):
        q = text.split(" ", 1)[1].strip()
        reply = web_search(q)
        yield reply
        save_msg(chat_id, "assistant", reply)
        return

    # Profiler quick command
    if text.lower().startswith("/profile "):
        q = text.split(" ", 1)[1].strip()
        mode = "profiler"
        context = [f"OSINT DATA:\n{web_search(q, max_results=5)}"]
    else:
        context = []


    # -------------------------
    # 2) SOFT CONTEXT TRIGGERS
    # -------------------------

    # Lightweight stock hints inside normal chat
    if "stock" in text.lower():
        for sym in _extract_tickers(text):
            if sym in ["AAPL", "NVDA", "GOOG", "MSFT", "AMZN", "TSLA", "BTC", "ETH"]:
                context.append(get_stock_price(sym))

    if "youtube.com" in text or "youtu.be" in text:
        context.append(get_youtube_transcript(text))

    if "search" in text.lower() and mode != "profiler":
        context.append(f"WEB:\n{web_search(text)}")

    facts = get_facts()
    if facts:
        context.append("MEMORY:\n" + "\n".join(facts))


    # -------------------------
    # 3) SYSTEM PROMPT
    # -------------------------

    system_prompt = f"""
You are NovaMind (v4.0 Titan).
You are a local-first, tool-using assistant.

Rules:
- Be concise and structured.
- If a tool output is available, use it.
- Do not claim actions you didn't perform.
- Security actions must be permission-based.

MODE: {mode.upper()}
""".strip()

    if context:
        system_prompt += "\n\nCONTEXT:\n" + "\n".join(context)


    # -------------------------
    # 4) HISTORY + USER MSG
    # -------------------------

    msgs = [{"role": "system", "content": system_prompt}]

    hist = get_history(chat_id)[-6:]
    for h in hist:
        if h.get("content") and h["content"] != text:
            msgs.append({"role": h["role"], "content": h["content"]})

    msgs.append({"role": "user", "content": text})


    # -------------------------
    # 5) STREAM OUTPUT
    # -------------------------

    try:
        stream = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=msgs,
            stream=True
        )

        full_text = ""
        for chunk in stream:
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                yield content
                full_text += content

        save_msg(chat_id, "assistant", full_text)

        # MVP memory capture
        if "my name is" in text.lower():
            save_fact(text)

    except Exception as e:
        err = f"Error: {e}"
        yield err
        save_msg(chat_id, "assistant", err)
