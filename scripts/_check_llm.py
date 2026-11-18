import sys
sys.path.insert(0, '.')
try:
    from src.tutor.llm_config import get_api_key
    key = get_api_key()
    if key:
        print(f"LLM API key: PRESENT (starts with {key[:4]}...)")
    else:
        print("LLM API key: MISSING (returns None)")
except Exception as e:
    print(f"LLM config error: {e}")
