# Current State

Last updated: 2026-07-06

## Repository

- Path: `C:\Users\Notandi\Documents\New project`
- Git repository: present
- Worktree state: many untracked files; no clean tracked baseline observed
- Primary local project observed: Django-based Kaupfjelag management system
- Additional local folder observed: `home-dashboard`

## Verified Files

Observed local project files include:

- `README.md`
- `UPPSETNING.md`
- `docker-compose.yml`
- `manage.py`
- `requirements.txt`
- Django apps: `bokhald`, `starfsfolk`, `verkefni`, `vidskiptavinir`, `reikningar`
- `home-dashboard/`

## Documentation State

The previous governance files were missing before this baseline was created:

- `README_AI.md`
- `CURRENT_STATE.md`
- `ENGINEERING_DASHBOARD.md`
- `PROJECT_MEMORY.md`
- `ROADMAP.md`
- `ARCHITECTURE.md`
- `VALIDATION_STATUS.md`
- `CURRENT_MILESTONE.md`
- `THREAD_RESTART_SUMMARY.md`
- `docs/index.md`

Existing Icelandic documentation appears to have character encoding damage in rendered text. This should be fixed as a documentation quality task.

## Live Server State From 2026-07-06 Review

Server reviewed: `72.62.212.222`

Hladvarp.com launch review found:

- `hladvarp_castopod`: running and healthy
- `hladvarp_front`: running
- `hladvarp_mariadb`: running
- `hladvarp_redis`: running
- `hladvarp_studio_recorder`: running
- disk use: about 35 percent
- daily restic backup observed as successful on 2026-07-06

Public Hladvarp endpoints tested successfully during launch review:

- `https://hladvarp.com/`
- `https://hladvarp.com/@kaffisopinn/feed.xml`
- `https://hladvarp.com/@thitthladvarp/feed.xml`
- `https://hladvarp.com/nytt-hladvarp`
- `https://hladvarp.com/tilkynningar`
- `https://hladvarp.com/cp-auth/login`

## Known Risks

- Governance baseline is newly created and incomplete.
- Git repository has no clean tracked baseline.
- Open public ports on server included `3000` and `8080` during review; ownership/need should be confirmed.
- Temporary server password used during review should be rotated.
- Documentation encoding issues reduce maintainability.
- Multiple deploy/archive directories exist on server; source of truth should be clarified.

