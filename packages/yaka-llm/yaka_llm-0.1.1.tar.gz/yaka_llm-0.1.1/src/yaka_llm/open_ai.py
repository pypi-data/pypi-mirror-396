import json
import time
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple
import urllib.request
import urllib.error

JSONSchema = Dict[str, Any]


def _pytype_to_json_schema(py_type: Any) -> str:
    if py_type in (int, float):
        return "number"
    if py_type is bool:
        return "boolean"
    if py_type is str:
        return "string"
    return "string"


class ChatGPTModel:
    """
    OpenAI / OpenRouter compatible chat client with tool-calling loop.
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        url: str,
        max_iterations: int = 6,
        sleep_between: float = 0.2,
    ):
        self.model = model
        self.api_key = api_key
        self.url = url
        self.max_iterations = max_iterations
        self.sleep_between = sleep_between

        self._functions: Dict[str, Callable[..., Any]] = {}
        self._tools: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------ TOOLS

    def tool(self, fn: Optional[Callable] = None, *, name: Optional[str] = None):
        def register(f: Callable):
            tool_name = name or f.__name__
            self._functions[tool_name] = f
            self._rebuild_tools()
            return f

        return register(fn) if fn else register

    def _rebuild_tools(self):
        tools = []

        for name, fn in self._functions.items():
            sig = inspect.signature(fn)
            properties = {}
            required = []

            for pname, p in sig.parameters.items():
                ann = p.annotation if p.annotation is not inspect._empty else str
                properties[pname] = {"type": _pytype_to_json_schema(ann)}
                if p.default is inspect._empty:
                    required.append(pname)

            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": fn.__doc__ or "",
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "required": required,
                        },
                    },
                }
            )

        self._tools = tools

    # ------------------------------------------------------------- HTTP CALL

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")
            raise RuntimeError(f"HTTP {e.code}: {body}")
        except Exception as e:
            raise RuntimeError(f"Network error: {e}")

    # --------------------------------------------------------- TOOL EXECUTION

    def _execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        fn = self._functions.get(name)
        if not fn:
            return {"error": f"Tool '{name}' not registered"}

        try:
            return fn(**args)
        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------------ CALL

    def call(self, history: List[str], prompt: str, role: str = "user") -> Optional[str]:
        self._rebuild_tools()

        messages = [{"role": "user", "content": h} for h in history]
        messages.append({"role": role, "content": prompt})

        for _ in range(self.max_iterations):
            payload = {
                "model": self.model,
                "messages": messages,
            }

            if self._tools:
                payload["tools"] = self._tools
                payload["tool_choice"] = "auto"

            resp = self._post(payload)
            choices = resp.get("choices", [])

            for choice in choices:
                msg = choice.get("message", {})

                # ---------------- TOOL CALL
                if "tool_calls" in msg:
                    for call in msg["tool_calls"]:
                        name = call["function"]["name"]
                        args = json.loads(call["function"].get("arguments", "{}"))

                        result = self._execute_tool(name, args)

                        messages.append(msg)
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call["id"],
                                "content": json.dumps(result),
                            }
                        )

                        time.sleep(self.sleep_between)
                        break
                    else:
                        continue
                    break

                # ---------------- FINAL TEXT
                content = msg.get("content")
                if content:
                    messages.append(msg)
                    return content

            return None

        return None


__all__ = ["ChatGPTModel"]
