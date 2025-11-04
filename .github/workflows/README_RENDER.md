# Deploying to Render (Free)

## Do I need a Render account?
Yes. You'll need a free account at https://render.com/ to host the service online. The Free plan provides a small web service that sleeps when idle.

## Steps

### 1) Create the Render service (one-time, via Blueprint)
1. In Render, click **New** → **Blueprint**.
2. Paste `render.yaml` from this repo.
3. Set repo to this GitHub repository.
4. Fill env vars marked `sync: false`:
   - `MONGO_URI` (e.g., MongoDB Atlas M0 connection string)
   - `JWT_SECRET` (random string)
5. Click **Apply**. After creation, open service → **Settings → Advanced** and copy **Service ID**.

### 2) GitHub secrets for deploy workflow
In GitHub repo → **Settings → Secrets and variables → Actions**:
- `RENDER_SERVICE_ID` — the value you copied
- `RENDER_API_KEY` — create at Render: User menu → Account Settings → **API Keys**

Now on every push to `main`/`master`:
- `docker-publish.yml` builds & pushes `ghcr.io/<owner>/<repo>/app:latest`
- `deploy-render.yml` triggers a redeploy in Render, which pulls the new image.

## Public image (GHCR)
Make sure your GHCR package (`/app`) is public or configure registry credentials in Render.

## Health check
`/healthz` (change in render.yaml as needed).

