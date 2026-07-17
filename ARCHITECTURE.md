# Architecture

Last updated: 2026-07-06

## Local Repository Architecture

Observed local stack:

- Django 5 application
- Django REST Framework
- PostgreSQL
- Redis
- Celery worker and beat
- Nginx and Certbot in Docker

Observed local apps:

- `starfsfolk`
- `verkefni`
- `vidskiptavinir`
- `reikningar`
- `bokhald`

The local README describes a management system for employees, projects, customers, invoices, and bookkeeping.

## Server Architecture Observed During Hladvarp Review

Server: `72.62.212.222`

Hladvarp.com production stack observed:

- Caddy as public reverse proxy
- Castopod container
- MariaDB container
- Redis container
- Nginx front container
- Studio recorder container
- Restic backups
- Uptime Kuma monitoring

Production compose file observed:

- `/opt/hladvarp-stack/docker-compose.yml`

Custom Hladvarp mounts observed:

- `/opt/hladvarp-custom`
- `/opt/hladvarp-assets`
- `/opt/hladvarp-audit`
- `/opt/hladvarp-front`

## Architecture Risks

- Multiple deploy directories exist on server. Production source of truth must be declared.
- This local repository does not appear to contain the full live Hladvarp customization source.
- Open public ports unrelated to Hladvarp were observed on the same server.

## Architecture Change Rule

Do not silently change architecture. Create an Architecture Change Request before changing service topology, canonical data models, authentication flow, backup strategy, or deployment source of truth.

