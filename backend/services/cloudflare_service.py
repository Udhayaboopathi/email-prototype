"""Cloudflare API service – supports both a global token and per-request tokens."""
from __future__ import annotations

import httpx


class CloudflareService:
    def __init__(self, api_token: str = ""):
        self.api_token = api_token
        self.base_url = "https://api.cloudflare.com/client/v4"

    def _headers(self, token: str | None = None) -> dict[str, str]:
        t = token or self.api_token
        return {"Authorization": f"Bearer {t}", "Content-Type": "application/json"}

    async def get_zone_id(self, domain: str, token: str | None = None) -> str | None:
        """Look up the Cloudflare Zone ID for a given domain name."""
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{self.base_url}/zones",
                headers=self._headers(token),
                params={"name": domain, "per_page": 1},
            )
            resp.raise_for_status()
            results = resp.json().get("result", [])
            return results[0]["id"] if results else None

    async def create_dns_record(
        self,
        zone_id: str,
        record_type: str,
        name: str,
        content: str,
        proxied: bool = False,
        token: str | None = None,
    ) -> dict[str, object]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self.base_url}/zones/{zone_id}/dns_records",
                headers=self._headers(token),
                json={"type": record_type, "name": name, "content": content, "ttl": 300, "proxied": proxied},
            )
            resp.raise_for_status()
            return resp.json()

    async def setup_email_dns(
        self,
        domain: str,
        smtp_hostname: str,
        dkim_selector: str,
        dkim_txt_value: str,
        token: str | None = None,
    ) -> str:
        """
        Automatically create all email DNS records for a domain via Cloudflare.
        Includes MX, SPF, DMARC, and the DKIM TXT record so that outbound mail
        shows 'signed-by: <domain>' instead of the mail server's own domain.
        Returns the Cloudflare zone_id used.
        """
        zone_id = await self.get_zone_id(domain, token=token)
        if not zone_id:
            raise ValueError(f"No Cloudflare zone found for domain '{domain}'. Make sure the domain is added to Cloudflare first.")

        records = [
            ("MX",  domain,                               f"10 {smtp_hostname}"),
            ("TXT", domain,                               "v=spf1 mx -all"),
            ("TXT", f"_dmarc.{domain}",                  f"v=DMARC1; p=quarantine; rua=mailto:dmarc@{domain}"),
            # Per-domain DKIM — makes 'signed-by' match the client domain
            ("TXT", f"{dkim_selector}._domainkey.{domain}", dkim_txt_value),
        ]
        for rtype, rname, rcontent in records:
            try:
                await self.create_dns_record(zone_id, rtype, rname, rcontent, token=token)
            except httpx.HTTPStatusError:
                # Record may already exist (error code 81057) — ignore
                pass

        return zone_id

    async def list_zones(self, token: str | None = None) -> list[dict[str, object]]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{self.base_url}/zones",
                headers=self._headers(token),
            )
            resp.raise_for_status()
            payload = resp.json()
            return payload.get("result", [])
