import base64
import json
from typing import Any, Dict, List

import aiohttp

from .const import (
    PROVIDER_OPENAI,
    PROVIDER_GEMINI,
)


class LLMClientError(Exception):
    """Raised when the LLM client fails."""


class LLMClient:
    """Provider-agnostic Vision client (OpenAI + Gemini)."""

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str,
        base_url: str | None,
    ) -> None:
        self._provider = provider
        self._api_key = api_key
        self._model = model
        self._base_url = base_url or ""

    async def analyze_image(
        self,
        session: aiohttp.ClientSession,
        image_bytes: bytes,
        room_name: str,
    ) -> Dict[str, Any]:
        """Return dict: {status, tasks, comment}."""
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        if self._provider == PROVIDER_OPENAI:
            return await self._call_openai(session, image_b64, room_name)
        if self._provider == PROVIDER_GEMINI:
            return await self._call_gemini(session, image_b64, room_name)

        raise LLMClientError(
            f"Provider {self._provider!r} not implemented yet. Use OpenAI or Gemini."
        )

    # ---------- Helpers ----------

    @staticmethod
    def _system_prompt(room_name: str) -> str:
        return (
            "You are a tidy-task assistant for a smart home.\n"
            f"The image is from the room/area called: '{room_name}'.\n\n"
            "Your job:\n"
            "1. Decide if there are obvious tidying / cleaning tasks that a human should do RIGHT NOW.\n"
            "2. If yes, output a SHORT checklist of specific tasks.\n"
            "3. If the room already looks fine and there is nothing useful to do, mark it as clean.\n\n"
            "Important rules:\n"
            "- Focus on visible tidying (clear surfaces, put things away, obvious rubbish, etc.).\n"
            "- Do NOT invent tasks unrelated to what you can see.\n"
            "- Keep each task short and actionable.\n"
            "- Respond strictly as a JSON object with this shape:\n"
            "{\n"
            '  \"status\": \"clean\" | \"messy\",\n'
            "  \"tasks\": [\n"
            "    {\n"
            "      \"title\": \"short task name\",\n"
            "      \"description\": \"optional extra detail\",\n"
            "      \"priority\": \"low\" | \"normal\" | \"high\"\n"
            "    }\n"
            "  ],\n"
            "  \"comment\": \"optional short free-text summary\"\n"
            "}\n"
            "- If there is nothing to do, use status \"clean\" and an empty tasks list.\n"
        )

    @staticmethod
    def _default_result_clean() -> Dict[str, Any]:
        return {
            "status": "clean",
            "tasks": [],
            "comment": "Room appears tidy – nothing obvious to do.",
        }

    @staticmethod
    def _validate_response(data: Dict[str, Any]) -> Dict[str, Any]:
        status = data.get("status")
        tasks = data.get("tasks", [])
        comment = data.get("comment")

        if status not in ("clean", "messy"):
            raise LLMClientError(f"Invalid status in response: {status!r}")

        if not isinstance(tasks, list):
            raise LLMClientError("tasks must be a list")

        fixed_tasks: List[Dict[str, Any]] = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            title = task.get("title")
            if not title or not isinstance(title, str):
                continue
            description = task.get("description")
            priority = task.get("priority") or "normal"
            if priority not in ("low", "normal", "high"):
                priority = "normal"
            fixed_tasks.append(
                {
                    "title": title.strip(),
                    "description": (description or "").strip(),
                    "priority": priority,
                }
            )

        if status == "messy" and not fixed_tasks:
            return LLMClient._default_result_clean()

        return {
            "status": status,
            "tasks": fixed_tasks,
            "comment": comment or "",
        }

    # ---------- Provider calls ----------

    async def _call_openai(
        self,
        session: aiohttp.ClientSession,
        image_b64: str,
        room_name: str,
    ) -> Dict[str, Any]:
        url = self._base_url or "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": self._system_prompt(room_name),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyse this room and return the tidy-task JSON."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            },
                        },
                    ],
                },
            ],
        }

        async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise LLMClientError(f"OpenAI HTTP {resp.status}: {text}")

            data = await resp.json()
            try:
                content = data["choices"][0]["message"]["content"]
            except Exception as err:
                raise LLMClientError(f"Malformed OpenAI response: {data}") from err

            if isinstance(content, str):
                parsed = json.loads(content)
            elif isinstance(content, list) and content and isinstance(content[0], dict):
                text_block = next(
                    (c["text"] for c in content if c.get("type") == "text"),
                    None,
                )
                parsed = json.loads(text_block) if text_block else {}
            else:
                parsed = content

        return self._validate_response(parsed)

    async def _call_gemini(
        self,
        session: aiohttp.ClientSession,
        image_b64: str,
        room_name: str,
    ) -> Dict[str, Any]:
        model = self._model or "gemini-1.5-flash-latest"
        base = self._base_url or "https://generativelanguage.googleapis.com/v1beta"
        url = f"{base}/models/{model}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }

        prompt = self._system_prompt(room_name)

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_b64,
                            }
                        },
                    ]
                }
            ]
        }

        async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise LLMClientError(f"Gemini HTTP {resp.status}: {text}")

            data = await resp.json()

        try:
            candidates = data["candidates"]
            first = candidates[0]
            parts = first["content"]["parts"]
            text_block = next((p["text"] for p in parts if "text" in p), None)
            if not text_block:
                raise ValueError("No text content")
            parsed = json.loads(text_block)
        except Exception as err:
            raise LLMClientError(f"Malformed Gemini response: {data}") from err

        return self._validate_response(parsed)
