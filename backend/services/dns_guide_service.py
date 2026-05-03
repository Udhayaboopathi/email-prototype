from config import get_settings


class DNSGuideService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def records_for_domain(self, domain: str) -> list[dict[str, str]]:
        selector = self.settings.dkim_selector
        return [
            {"type": "MX", "name": domain, "value": f"10 {self.settings.smtp_hostname}"},
            {"type": "TXT", "name": domain, "value": "v=spf1 mx -all"},
            {
                "type": "TXT",
                "name": f"_dmarc.{domain}",
                "value": "v=DMARC1; p=quarantine; rua=mailto:dmarc@" + domain,
            },
            {
                "type": "TXT",
                "name": f"{selector}._domainkey.{domain}",
                "value": "v=DKIM1; k=rsa; p=<public-key-from-generate_keys.sh>",
            },
        ]
