# io3

A community index for discovering queer and erotic indie games that have been de-indexed on itch.io. Like AO3 or VNDB for games — metadata and links only, never hosting downloads.

Built on the [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template).

## Stack

FastAPI + SQLModel + PostgreSQL on the backend. React + TypeScript + Vite + TanStack Router/Query on the frontend. Docker Compose for local dev and deployment.

## Local development

Start the stack:

```bash
docker compose watch
```

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>
- Mailcatcher (local email): <http://localhost:1080>

On first boot the backend seeds the tag taxonomy and creates the superuser from `.env`.

Copy `.env` from the template defaults and change at least `SECRET_KEY` and `POSTGRES_PASSWORD` before deploying. Set `ITCH_OWNER_USERNAME` to your itch.io username (the site owner). Generate secrets with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

See [development.md](./development.md) for running services outside Docker, local domains, and pre-commit hooks.

## Tests

Backend (from `backend/`):

```bash
bash scripts/test.sh
```

Frontend E2E (from `frontend/`):

```bash
npx playwright test
```

## Deployment

See [deployment.md](./deployment.md). The upstream template covers Traefik, HTTPS, and multi-environment setup in detail.

## License

MIT — see [LICENSE](./LICENSE).
