# DOCSCRUB API

FastAPI service for stripping hidden metadata, author tags, and XMP data from PDF documents. Built by Rare Frequency Works.

## RapidAPI gateway security

The paid `POST /api/v1/clean-pdf` endpoint now verifies the private header `X-RapidAPI-Proxy-Secret` injected by RapidAPI, comparing it to the environment variable `RAPIDAPI_PROXY_SECRET` stored in Render.

- Missing/mismatched header: **403 Forbidden**
- Missing server configuration: **503 Service Unavailable** (fails closed)
- Valid RapidAPI proxy secret: existing PDF sanitization behavior
- `GET /` remains public for health monitoring.
- Browser `OPTIONS` preflight is allowed, but it never cleans a PDF.

**Deployment caution:** This endpoint becomes RapidAPI-only. Any DOCSCRUB website, Android app, or direct integration that currently posts straight to the Render URL will receive 403. Verify those clients do not depend on this backend, or route them through an independently authenticated first-party server, before merging the change into the branch Render deploys.

RapidAPI's proxy secret must remain server-side. Do not put it in a client app, website JavaScript, public repository, or API documentation. RapidAPI enforces subscriptions and quotas at its gateway; the backend only verifies the forwarding secret.

## Development tests

Install the main application dependencies plus `pytest` and `httpx`, then run:

```sh
python -m pytest -q
```
