import uuid
import json
import logging
from app.core.config import settings
from app.core.openai_client import get_openai_client
from app.core.memory import save_msg, get_history, get_facts, save_fact
from app.core.tools import web_search, system_control, generate_image, get_stock_price, get_youtube_transcript, run_ghost_loop
from app.core.swarm import run_swarm_protocol

logger = logging.getLogger(__name__)

def think(user_id, message, chat_id=None, image_data=None):
    if not chat_id: chat_id = str(uuid.uuid4())
    save_msg(chat_id, "user", message)

    client = get_openai_client()
    history = get_history(chat_id)[-6:]
    facts = get_facts()
    
    # 1. THE INNER MONOLOGUE (The "Human" Element)
    # Nova plans its move before acting.
    plan_prompt = f"""
    You are NovaMind, an Autonomous Intelligence.
    User Input: "{message}"
    
    Available Tools: [STOCK_PRICE, WEB_SEARCH, YOUTUBE_ANALYSIS, IMAGE_GEN, SYSTEM_CONTROL, GHOST_MODE]
    
    THINK STEP-BY-STEP:
    1. What is the user really asking? (Intent)
    2. Do I need external data? If yes, which tool?
    3. If I use a tool and it fails, what is my backup plan?
    4. Construct the best response.

    Return JSON: {{"thought": "I need to check X...", "tool": "TOOL_NAME_OR_NONE", "arg": "argument"}}
    """

    try:
        # Step A: The Planning Phase
        plan_resp = client.chat.completions.create(
            model=settings.SMART_MODEL, # Use configured smart model for planning
            messages=[{"role": "system", "content": plan_prompt}]
        )
        raw_plan = plan_resp.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        plan = json.loads(raw_plan)
        
        # Save thought for the user to see (Metacognition)
        thought_msg = f"<think>{plan['thought']}</think>"
        
        tool_output = ""
        
        # Step B: The Execution Phase (Self-Correction)
        if plan["tool"] != "NONE":
            tool_cmd = plan["tool"]
            arg = plan["arg"]
            
            if tool_cmd == "STOCK_PRICE":
                tool_output = get_stock_price(arg)
            elif tool_cmd == "WEB_SEARCH":
                tool_output = web_search(arg)
            elif tool_cmd == "YOUTUBE_ANALYSIS":
                tool_output = get_youtube_transcript(arg)
            elif tool_cmd == "IMAGE_GEN":
                # Images return immediately
                img_url = generate_image(arg)
                save_msg(chat_id, "assistant", img_url)
                return {"reply": img_url, "mode": "creative", "chat_id": chat_id}
            elif tool_cmd == "GHOST_MODE":
                ghost_rep = run_ghost_loop(arg)
                save_msg(chat_id, "assistant", ghost_rep)
                return {"reply": ghost_rep, "mode": "ghost", "chat_id": chat_id}
            elif tool_cmd == "SYSTEM_CONTROL":
                sys_rep = system_control(arg)
                if sys_rep: tool_output = sys_rep

        # Step C: The Synthesis Phase (Final Answer)
        final_system = f"""
        You are NovaMind. 
        Context from Tools: {tool_output}
        User Memory: {facts}
        
        Answer the user naturally. Do not mention "I used a tool". Just give the answer.
        """
        
        final_msgs = [{"role": "system", "content": final_system}] + history
        final_msgs.append({"role": "user", "content": message})
        
        final_resp = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=final_msgs,
            temperature=0.4
        )
        
        final_reply = final_resp.choices[0].message.content
        
        # Combine thought + answer for the UI
        full_response = f"{thought_msg}\n\n{final_reply}"
        
        # Learning Step
        if "my name is" in message.lower(): save_fact(message)
        
        save_msg(chat_id, "assistant", full_response)
        return {"reply": full_response, "mode": "operator", "chat_id": chat_id}

    except Exception as e:
        return {"reply": f"Cognitive Error: {e}", "chat_id": chat_id}
