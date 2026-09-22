"""Send a message to the LLM with tool access. Execute any tool call it
makes. Return the final assistant message."""
import json
from urllib import request as _urllib_request
from urllib.error import URLError

from . import llm_config
from .tools import tool_schema, call_tool


def _post(url, key, payload, timeout):
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    req = _urllib_request.Request(url, data=body, headers=headers, method="POST")
    with _urllib_request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def converse_turn(history, system_prompt, learner_id="anonymous",
                  max_tool_rounds=1):
    if not llm_config.is_enabled():
        return {"assistant_text": "", "tool_calls_made": [],
                "raw_messages": history, "error": "llm_disabled"}

    url = llm_config.get_url()
    key = llm_config.get_key()
    model = llm_config.get_model()
    timeout = llm_config.get_timeout()

    messages = [{"role": "system", "content": system_prompt}] + list(history)
    tool_calls_made = []

    for round_i in range(max_tool_rounds + 1):
        last_round = (round_i == max_tool_rounds)
        tool_choice = "none" if last_round else "auto"

        payload = {
            "model": model,
            "messages": messages,
            "tools": tool_schema(),
            "tool_choice": tool_choice,
            "temperature": 0.6,
            "max_tokens": 200,
        }
        try:
            data = _post(url, key, payload, timeout)
        except (URLError, KeyError, ValueError, TimeoutError, OSError) as e:
            return {"assistant_text": "", "tool_calls_made": tool_calls_made,
                    "raw_messages": messages, "error": str(e)}

        try:
            msg = data["choices"][0]["message"]
        except (KeyError, IndexError):
            return {"assistant_text": "", "tool_calls_made": tool_calls_made,
                    "raw_messages": messages, "error": "malformed_response"}

        messages.append(msg)
        calls = msg.get("tool_calls") or []
        text = (msg.get("content") or "").strip()

        if text:
            return {"assistant_text": text,
                    "tool_calls_made": tool_calls_made,
                    "raw_messages": messages,
                    "error": None}

        if not calls:
            return {"assistant_text": "",
                    "tool_calls_made": tool_calls_made,
                    "raw_messages": messages,
                    "error": "no_text_no_tool"}

        for c in calls:
            fn = c.get("function", {})
            name = fn.get("name")
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            result = call_tool(name, args)
            tool_calls_made.append({"name": name, "args": args, "result": result})
            messages.append({"role": "tool",
                             "tool_call_id": c.get("id", "call_0"),
                             "content": json.dumps(result)})

    return {"assistant_text": "",
            "tool_calls_made": tool_calls_made,
            "raw_messages": messages, "error": "max_rounds"}
