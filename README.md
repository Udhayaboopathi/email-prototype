# Self-Hosted Email Platform

Production-oriented, Dockerized email platform for a Contabo VPS running Ubuntu 24.04 with inbound port 25 open.

## Prerequisites

- Contabo VPS (Ubuntu 24.04) with port 25 open
- Domain pointed to the VPS public IP
- Docker and Docker Compose installed

## Quick Start

1. Clone or copy this project to your server.
2. Configure environment values:
   - `cp .env.example .env`
   - `nano .env`
3. Start services:
   - `make up`
4. Run migrations:
   - `make migrate`
5. Seed super admin:
   - `make seed`
6. Issue TLS cert:
   - `make ssl DOMAIN=mail.yourdomain.com`
7. Open:
   - `https://yourdomain.com/login`

## DNS Records (Manual)

Add these records in your DNS provider:

- `MX`  `@` -> `mail.yourdomain.com` (priority `10`)
- `A`   `mail` -> `YOUR_CONTABO_IP`
- `TXT` `@` -> `v=spf1 ip4:YOUR_CONTABO_IP mx ~all`
- `TXT` `mail._domainkey` -> value from super admin panel after adding domain
- `TXT` `_dmarc` -> `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
- `PTR` configure in Contabo control panel under Reverse DNS Management

## Deliverability Validation

- Send a test message to `check-auth@verifier.port25.com`
- Use `mail-tester.com` and target a `10/10` score

## Service Endpoints

- Frontend: `https://yourdomain.com`
- Backend API: `https://yourdomain.com/api`
- SMTP inbound: `:25`
- SMTP submission: `:587`
- IMAP TLS: `:993`

## Useful Commands

- `make ps` - list containers
- `make logs` - stream backend logs
- `make test-smtp` - quick SMTP banner test
- `make test-imap` - quick IMAP TLS test
- `make backup` - trigger full backup

## Security Notes

- Change `SUPER_ADMIN_PASSWORD` and `JWT_SECRET_KEY` before production.
- Keep `ENCRYPTION_SECRET_KEY` stable for token/key decryption.
- Restrict SSH access and keep OS packages updated.
- Enable firewall rules for only required ports: `22`, `25`, `80`, `443`, `587`, `993`.

## Troubleshooting

- If cert issuance fails, verify DNS A record and open ports 80/443.
- If inbound mail fails, verify provider allows outbound/inbound on 25 and check PTR.
- If API fails healthcheck, run `docker compose logs backend`.
