from config import get_settings


class DNSGuideService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def records_for_domain(
        self,
        domain: str,
        dkim_txt_value: str | None = None,
    ) -> list[dict[str, str]]:
        """
        Return the required DNS records for *domain*.

        If *dkim_txt_value* is supplied (from the freshly generated key pair),
        it is used directly.  Otherwise a placeholder is returned so the admin
        knows they still need to generate and add the DKIM record.
        """
        selector = self.settings.dkim_selector

        dkim_value = dkim_txt_value or (
            f"v=DKIM1; k=rsa; p=<generate key with infra/dkim/generate_keys.sh {domain}>"
        )

        return [
            {
                "type": "MX",
                "name": domain,
                "value": f"10 {self.settings.smtp_hostname}",
                "purpose": "Receive email for this domain",
            },
            {
                "type": "TXT",
                "name": domain,
                "value": "v=spf1 mx -all",
                "purpose": "SPF — authorise the mail server to send",
            },
            {
                "type": "TXT",
                "name": f"_dmarc.{domain}",
                "value": f"v=DMARC1; p=quarantine; rua=mailto:dmarc@{domain}",
                "purpose": "DMARC policy",
            },
            {
                "type": "TXT",
                "name": f"{selector}._domainkey.{domain}",
                "value": dkim_value,
                "purpose": "DKIM — makes 'signed-by' show your domain",
            },
        ]
