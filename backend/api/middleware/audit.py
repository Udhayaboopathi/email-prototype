from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from database import SessionLocal
from models.audit_log import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            async with SessionLocal() as db:
                db.add(
                    AuditLog(
                        user_id=None,
                        action=request.method,
                        target=request.url.path,
                        ip_address=request.client.host if request.client else "unknown",
                        extra={"status_code": str(response.status_code)},
                    )
                )
                await db.commit()
        return response


def add_audit_logging(app) -> None:  # type: ignore[no-untyped-def]
    app.add_middleware(AuditMiddleware)
