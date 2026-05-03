import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.audit import add_audit_logging
from api.middleware.rate_limit import add_rate_limiting
from api.routers import (
    ai as ai_router,
    api_keys,
    auth,
    calendar as cal_router,
    campaigns,
    contacts,
    delegation,
    domain_admin,
    ediscovery,
    folders,
    labels,
    mail,
    notes as notes_router,
    pgp,
    rules,
    send_api,
    shared_mailboxes,
    spam_reports,
    super_admin,
    tasks as tasks_router,
    templates,
    threads,
    tracking,
    webhooks,
)
from config import get_settings
from imap.server import create_imap_server
from smtp.server import create_smtp_servers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    smtp25, smtp587 = await create_smtp_servers()
    imap_task = asyncio.create_task(create_imap_server())
    try:
        yield
    finally:
        smtp25.stop()
        smtp587.stop()
        imap_task.cancel()
        try:
            await imap_task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan, title="Email Platform API")
add_rate_limiting(app)
add_audit_logging(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(super_admin.router, prefix="/api")
app.include_router(domain_admin.router, prefix="/api")
app.include_router(mail.router, prefix="/api")
app.include_router(folders.router, prefix="/api")
app.include_router(threads.router, prefix="/api")
app.include_router(labels.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(cal_router.router, prefix="/api")
app.include_router(tasks_router.router, prefix="/api")
app.include_router(notes_router.router, prefix="/api")
app.include_router(ai_router.router, prefix="/api")
app.include_router(pgp.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(api_keys.router, prefix="/api")
app.include_router(send_api.router, prefix="/api")
app.include_router(tracking.router, prefix="/api")
app.include_router(shared_mailboxes.router, prefix="/api")
app.include_router(delegation.router, prefix="/api")
app.include_router(spam_reports.router, prefix="/api")
app.include_router(ediscovery.router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
