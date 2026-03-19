import pyautogui
import base64
import io
import json
import time
import logging
import platform
from app.core.config import settings
from app.core.openai_client import get_openai_client

# 1. DISABLE FAILSAFE (Stop the crashing)
pyautogui.FAILSAFE = False
logger = logging.getLogger(__name__)

# 2. DETECT MAC RETINA SCALING
# On Macs, screenshots are 2x the size of the mouse grid.
IS_MAC = platform.system() == "Darwin"
SCALE_FACTOR = 2 if IS_MAC else 1

def _take_screenshot() -> str:
    """Capture screen and return base64 string."""
    try:
        screenshot = pyautogui.screenshot()
        # Resize to standard 1080p to help the AI understand standard layouts
        screenshot.thumbnail((1920, 1080)) 
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return ""

def execute_action(act: dict):
    try:
        # Get actual screen dimensions in "Points" (Mouse coordinates)
        screen_w, screen_h = pyautogui.size()
        
        action_type = act.get('type')
        
        if action_type == 'click':
            x = act.get('x')
            y = act.get('y')

            if x is not None and y is not None:
                # 3. SCALING FIX
                # If we resized the image sent to AI, we might need to adjust logic here.
                # But usually, just clamping to screen size is safer.
                
                # Clamp coordinates to stay inside the screen
                target_x = max(10, min(x, screen_w - 10))
                target_y = max(10, min(y, screen_h - 10))
                
                print(f"Ghost moving to: {target_x}, {target_y}")
                pyautogui.moveTo(target_x, target_y, duration=0.5) 
                pyautogui.click()
                
        elif action_type == 'type':
            text = act.get('text')
            if text:
                pyautogui.write(text, interval=0.05)
                
        elif action_type == 'press':
            key = act.get('key')
            if key:
                # Mac mapping
                if key == "win" or key == "super": key = "command"
                if key == "ctrl" and IS_MAC: key = "command"
                pyautogui.press(key)
                
        elif action_type == 'wait':
            time.sleep(act.get('seconds', 1))
            
    except Exception as e:
        logger.error(f"Ghost Action failed: {e}")

def run_ghost_loop(objective: str) -> str:
    client = get_openai_client()
    img = _take_screenshot()
    if not img: return "Ghost Error: Blind."
    
    # Get current screen size to tell the AI
    w, h = pyautogui.size()
    
    prompt = f"""
    You are a GUI Agent. You see the user's screen.
    User's Screen Resolution: {w}x{h}.
    Goal: {objective}
    
    Return JSON ONLY. No markdown.
    Format: {{"thought": "reasoning...", "actions": [{{"type": "click", "x": 100, "y": 200}}]}}
    
    CRITICAL: 
    1. Coordinates MUST be within 0-{w} (width) and 0-{h} (height).
    2. Do NOT guess coordinates outside this range.
    """
    
    try:
        resp = client.chat.completions.create(
            model=settings.MODEL_NAME, 
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}
                ]}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        raw = resp.choices[0].message.content
        clean_json = raw.replace("```json", "").replace("```", "").strip()
        plan = json.loads(clean_json)
        
        for act in plan.get('actions', []):
            execute_action(act)
            
        return f"Ghost Action: {plan.get('thought')}"
    except Exception as e:
        return f"Ghost Failed: {e}"