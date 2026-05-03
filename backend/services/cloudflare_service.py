import httpx


class CloudflareService:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.cloudflare.com/client/v4"

    async def create_dns_record(self, zone_id: str, record_type: str, name: str, content: str, proxied: bool = False) -> dict[str, object]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self.base_url}/zones/{zone_id}/dns_records",
                headers={"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"},
                json={"type": record_type, "name": name, "content": content, "ttl": 300, "proxied": proxied},
            )
            resp.raise_for_status()
            return resp.json()

    async def list_zones(self) -> list[dict[str, object]]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{self.base_url}/zones",
                headers={"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"},
            )
            resp.raise_for_status()
            payload = resp.json()
            return payload.get("result", [])
