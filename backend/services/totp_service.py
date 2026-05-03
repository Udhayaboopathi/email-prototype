import pyotp


class TOTPService:
    @staticmethod
    def provisioning_uri(email: str, secret: str, issuer: str = "SelfHostedMail") -> str:
        return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)

    @staticmethod
    def verify(secret: str, code: str) -> bool:
        return pyotp.TOTP(secret).verify(code, valid_window=1)
