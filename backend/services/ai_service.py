import httpx

from config import get_settings


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = "claude-sonnet-4-20250514"

    async def _call(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text_chunks = [part.get("text", "") for part in data.get("content", []) if part.get("type") == "text"]
            return "\n".join(text_chunks).strip()

    async def summarize_email(self, body: str) -> str:
        if not self.settings.ai_summary_enabled:
            return body[:200]
        return await self._call(f"Summarize this email in 3 bullet points:\n\n{body}")

    async def smart_reply(self, body: str) -> str:
        if not self.settings.ai_smart_reply_enabled:
            return "Thanks for your email. I'll review and reply shortly."
        return await self._call(f"Write a concise professional reply to:\n\n{body}")

    async def priority_score(self, subject: str, body: str) -> int:
        if not self.settings.ai_priority_inbox_enabled:
            return 50
        text = await self._call(
            "Rate urgency from 1 to 100. Return number only.\n"
            f"Subject: {subject}\nBody: {body[:2000]}"
        )
        try:
            score = int("".join(ch for ch in text if ch.isdigit())[:3] or "50")
            return max(1, min(100, score))
        except ValueError:
            return 50
