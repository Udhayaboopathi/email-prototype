.PHONY: up down logs migrate seed shell ssl backup restart ps test-smtp test-imap

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f backend

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python seed.py

shell:
	docker compose exec backend bash

ssl:
	docker compose exec nginx certbot --nginx -d $(DOMAIN)

backup:
	docker compose exec backend python -c "import asyncio; from database import async_session_factory; from services.backup_service import create_full_backup; async def run():\n  async with async_session_factory() as db:\n    path = await create_full_backup(db);\n    print(path)\n; asyncio.run(run())"

restart:
	docker compose restart backend

ps:
	docker compose ps

test-smtp:
	echo "EHLO test" | nc localhost 25

test-imap:
	openssl s_client -connect localhost:993
