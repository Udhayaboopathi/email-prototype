import asyncio
import json
import mailbox as py_mailbox
import tarfile
import tempfile
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from models.alias import Alias
from models.backup_job import BackupJob
from models.contact import Contact
from models.domain import Domain
from models.mailbox import Mailbox


def _backup_root() -> Path:
    root = Path("/var/backups/email-platform")
    root.mkdir(parents=True, exist_ok=True)
    return root


async def export_mailbox_mbox(mailbox_id: str, db: AsyncSession) -> str:
    mailbox_row = await db.scalar(select(Mailbox).where(Mailbox.id == mailbox_id))
    if not mailbox_row:
        raise ValueError("Mailbox not found")
    address = getattr(mailbox_row, "full_address", None) or getattr(mailbox_row, "address", "unknown@example.com")
    local, domain = address.split("@", 1)
    src = Path(get_settings().maildir_base) / domain / local
    out_file = _backup_root() / f"{mailbox_id}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.mbox"

    def _write() -> None:
        mdir = py_mailbox.Maildir(src.as_posix(), create=True)
        mbox = py_mailbox.mbox(out_file.as_posix())
        for message in mdir:
            mbox.add(message)
        mbox.flush()
        mbox.close()

    await asyncio.to_thread(_write)
    return out_file.as_posix()


async def export_mailbox_zip(mailbox_id: str, db: AsyncSession) -> str:
    mailbox_row = await db.scalar(select(Mailbox).where(Mailbox.id == mailbox_id))
    if not mailbox_row:
        raise ValueError("Mailbox not found")
    address = getattr(mailbox_row, "full_address", None) or getattr(mailbox_row, "address", "unknown@example.com")
    local, domain = address.split("@", 1)
    src = Path(get_settings().maildir_base) / domain / local
    out_file = _backup_root() / f"{mailbox_id}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.zip"

    def _write() -> None:
        with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in src.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(src))

    await asyncio.to_thread(_write)
    return out_file.as_posix()


async def import_mbox(mailbox_id: str, mbox_path: str, db: AsyncSession) -> dict[str, int]:
    mailbox_row = await db.scalar(select(Mailbox).where(Mailbox.id == mailbox_id))
    if not mailbox_row:
        raise ValueError("Mailbox not found")
    address = getattr(mailbox_row, "full_address", None) or getattr(mailbox_row, "address", "unknown@example.com")
    local, domain = address.split("@", 1)
    target = Path(get_settings().maildir_base) / domain / local
    imported = 0
    failed = 0

    def _import() -> tuple[int, int]:
        nonlocal imported, failed
        mbox = py_mailbox.mbox(mbox_path)
        mdir = py_mailbox.Maildir(target.as_posix(), create=True)
        for msg in mbox:
            try:
                mdir.add(msg)
                imported += 1
            except Exception:
                failed += 1
        return imported, failed

    imported, failed = await asyncio.to_thread(_import)
    return {"imported": imported, "failed": failed, "skipped": 0}


async def import_eml_zip(mailbox_id: str, zip_path: str, db: AsyncSession) -> dict[str, int]:
    mailbox_row = await db.scalar(select(Mailbox).where(Mailbox.id == mailbox_id))
    if not mailbox_row:
        raise ValueError("Mailbox not found")
    address = getattr(mailbox_row, "full_address", None) or getattr(mailbox_row, "address", "unknown@example.com")
    local, domain = address.split("@", 1)
    target = Path(get_settings().maildir_base) / domain / local

    def _import() -> tuple[int, int]:
        imported = 0
        failed = 0
        mdir = py_mailbox.Maildir(target.as_posix(), create=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                if not name.lower().endswith(".eml"):
                    continue
                try:
                    raw = zf.read(name)
                    mdir.add(raw)
                    imported += 1
                except Exception:
                    failed += 1
        return imported, failed

    imported, failed = await asyncio.to_thread(_import)
    return {"imported": imported, "failed": failed}


async def create_domain_backup(domain_id: str, db: AsyncSession) -> str:
    domain = await db.scalar(select(Domain).where(Domain.id == domain_id))
    if not domain:
        raise ValueError("Domain not found")

    mailboxes = list(await db.scalars(select(Mailbox).where(Mailbox.domain_id == domain_id)))
    aliases = list(await db.scalars(select(Alias).where(Alias.domain_id == domain_id)))
    contacts = list(await db.scalars(select(Contact)))

    backup_name = _backup_root() / f"domain-{domain_id}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.tar.gz"
    manifest = {
        "domain": {"id": domain.id, "name": domain.name},
        "mailboxes": [{"id": m.id, "address": getattr(m, "address", "")} for m in mailboxes],
        "aliases": [{"source": getattr(a, "source_address", ""), "destination": getattr(a, "destination_address", "")} for a in aliases],
        "contacts": [{"email": c.email, "name": c.name} for c in contacts],
    }

    def _pack() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_path = tmp_path / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            with tarfile.open(backup_name, "w:gz") as tar:
                tar.add(manifest_path, arcname="manifest.json")
                for mailbox_row in mailboxes:
                    addr = getattr(mailbox_row, "full_address", None) or getattr(mailbox_row, "address", "")
                    if "@" not in addr:
                        continue
                    local, dn = addr.split("@", 1)
                    maildir_path = Path(get_settings().maildir_base) / dn / local
                    if maildir_path.exists():
                        tar.add(maildir_path, arcname=f"maildir/{dn}/{local}")

    await asyncio.to_thread(_pack)
    return backup_name.as_posix()


async def restore_domain_backup(domain_id: str, backup_path: str, db: AsyncSession) -> dict[str, str]:
    domain = await db.scalar(select(Domain).where(Domain.id == domain_id))
    if not domain:
        raise ValueError("Domain not found")

    target = Path(get_settings().maildir_base)

    def _restore() -> None:
        with tarfile.open(backup_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.startswith("maildir/"):
                    tar.extract(member, path=target)

    await asyncio.to_thread(_restore)
    return {"status": "restored", "domain_id": domain_id}


async def create_full_backup(db: AsyncSession) -> str:
    backup_name = _backup_root() / f"full-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.tar.gz"
    maildir_root = Path(get_settings().maildir_base)

    def _pack() -> None:
        with tarfile.open(backup_name, "w:gz") as tar:
            if maildir_root.exists():
                tar.add(maildir_root, arcname="maildir")

    await asyncio.to_thread(_pack)
    db.add(BackupJob(type="full", status="done", file_path=backup_name.as_posix(), file_size_mb=backup_name.stat().st_size / (1024 * 1024)))
    await db.commit()
    return backup_name.as_posix()


async def restore_full_backup(backup_path: str, db: AsyncSession) -> dict[str, str]:
    target = Path(get_settings().maildir_base)

    def _restore() -> None:
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(path=target)

    await asyncio.to_thread(_restore)
    db.add(BackupJob(type="full", status="done", file_path=backup_path, completed_at=datetime.now(UTC)))
    await db.commit()
    return {"status": "restored"}


async def schedule_auto_backup(db: AsyncSession) -> None:
    await create_full_backup(db)
    retention_days = get_settings().backup_retention_days
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    jobs = list(await db.scalars(select(BackupJob).where(BackupJob.created_at < cutoff)))
    for job in jobs:
        path = Path(job.file_path)
        if path.exists():
            path.unlink(missing_ok=True)
        await db.delete(job)
    await db.commit()
