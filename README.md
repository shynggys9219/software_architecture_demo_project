# 🧱 FastAPI + MongoDB Replica Set + NGINX (load-balanced) — Clean Architecture Example

This project demonstrates a **Clean Architecture-based FastAPI backend** running behind an **NGINX load balancer** with **two FastAPI instances** and a **three-node MongoDB replica set** for resilience and fault tolerance.

It’s intentionally minimal yet production-ready to illustrate:
- Layer separation (domain / use case / infrastructure / adapter)
- Stateless application containers
- MongoDB replica-set initialization entirely via Docker (no external scripts)
- JWT authentication with in-memory users
- Example CRUD service (`/items`)
- Horizontal scaling with NGINX load balancing
- Basic security & resilience patterns

---

## 🚀 Quick Start

### 1️⃣ Build
```bash
docker compose build --no-cache
```

### 2️⃣ Run the full stack
```bash
docker compose up
```

Wait 15–30 seconds for the **mongo-setup** container to finish initializing the replica set.

### 3️⃣ Check health
- **API Docs:** http://localhost:8080/docs  
- **Health endpoint:** http://localhost:8080/healthz  
- **Mongo replica set status:**
  ```bash
  docker compose exec mongo1 mongosh --eval 'rs.status().members.map(m => ({name:m.name, state:m.stateStr}))'
  ```
  You should see one **PRIMARY** and two **SECONDARY**.

### 4️⃣ Use the API
1. `POST /auth/signup` → returns a JWT access token  
2. Click **Authorize** in Swagger → paste the token (just the raw token string)  
3. Use `/items` endpoints to create, list, update, delete items

---

## 🧩 Architecture Overview

Clean Architecture divides the project into **independent layers** so that each layer has a single responsibility and minimal coupling.

```
┌──────────────────────────────────────────────┐
│                  NGINX                       │
│      (load balances app1 & app2)             │
└──────────────────────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────┐
│               FastAPI apps                   │
│       (presentation + adapters)              │
└────────────────┬─────────────────────────────┘
                 │
     Dependency Injection / Use-case boundary
                 │
┌────────────────┴─────────────────────────────┐
│         Application (use case) layer          │
│    business logic (ItemService, AuthService)  │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────┐
│         Domain layer (entities + contracts)   │
│  Entities + Repository interfaces (abstract)  │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────┐
│     Infrastructure layer (Mongo, Security)    │
│   Implements repositories + utilities (JWT)   │
└────────────────┬─────────────────────────────┘
                 │
           MongoDB Replica Set
```

### Layer Descriptions

#### 🧠 Domain Layer (`app/domain`)
- **Pure business entities** and **repository interfaces**
- Has no external imports (pure Python, no FastAPI, no MongoDB)
- Defines the shape of the business model (`Item`, `User`) and contracts (`ItemRepository`, `UserRepository`)

#### ⚙️ Use Case Layer (`app/usecase`)
- Contains **application logic** orchestrating domain objects  
- Example: `ItemService` that calls the `ItemRepository` methods to perform CRUD

#### 🏗 Infrastructure Layer (`app/infrastructure`)
- Implements **technical details** like MongoDB connection pooling and JWT hashing  
- Example:  
  - `db.py` – async Motor client factory  
  - `security.py` – password hashing, token generation/verification  
- Completely replaceable (could swap Mongo with Postgres or Redis without touching domain)

#### 🌉 Adapters / Interface Layer (`app/adapters`)
- Bridges the external world to the use cases
- Two major groups:
  - **HTTP routers** (`app/adapters/http`) – REST endpoints using FastAPI
  - **Repository adapters** (`app/adapters/repo`) – implement domain interfaces using Mongo

#### 🧩 DI Container (`app/di.py`)
- Provides dependency injection: creates `Database`, `ItemService`, and `AuthService`
- Keeps construction centralized and allows easy mocking in tests

#### 🧰 Presentation Layer (`app/main.py`)
- Assembles the application
- Adds CORS, routers, and Swagger UI configuration
- Entry point for `uvicorn`

#### 🗄 MongoDB Replica Set (`mongo1`, `mongo2`, `mongo3`)
- Each container runs `mongod --replSet=rs0`
- `mongo-setup` container automatically runs a JS script to initialize the replica set
- Provides resilience: if one node dies, others continue serving reads/writes

#### 🌐 NGINX Load Balancer (`nginx`)
- Receives requests on port 8080 and forwards them to `app1` & `app2`
- Demonstrates horizontal scaling and fault tolerance

---

## 🔑 Authentication Flow

The demo AuthService keeps users in memory (no persistence for simplicity):

1. `POST /auth/signup`  
   - Hashes the password (PBKDF2)  
   - Saves hash in memory dict  
   - Returns JWT token
2. `POST /auth/login`  
   - Verifies password  
   - Returns new JWT
3. Any `/items` route uses dependency `get_current_user` which:  
   - Extracts token from `Authorization: Bearer <token>`  
   - Validates and decodes JWT  
   - Injects the `email` as `user` parameter

---

## 🧾 Configuration (.env)

| Variable | Example | Description |
|-----------|----------|-------------|
| `APP_NAME` | FastAPI Clean | Display name in docs |
| `MONGO_URI` | `mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0&retryWrites=true&w=majority` | Replica set connection string |
| `DB_NAME` | assignmentdb | Database name |
| `JWT_SECRET` | supersecretkey | Secret for signing JWTs |
| `JWT_ALG` | HS256 | Algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiry |
| `CORS_ORIGINS` | `*` | Allowed origins |

---

## ⚖️ Fault Tolerance & Resilience Mechanisms

| Feature | Explanation |
|----------|--------------|
| **MongoDB replica set** | Ensures data redundancy. If `mongo1` fails, a secondary becomes primary automatically. |
| **NGINX load balancing** | Routes requests to either `app1` or `app2`. One app can be restarted while the other serves traffic. |
| **Stateless apps** | JWT-based sessions mean any app instance can serve any user. |
| **Docker healthchecks** | MongoDB containers retry until all nodes are up before the RS init runs. |

---

## 🧰 Developer Notes

### Logs
```bash
docker compose logs -f app1
docker compose logs -f mongo-setup
```

### Enter a container
```bash
docker compose exec app1 bash
docker compose exec mongo1 mongosh
```

### Tear down
```bash
docker compose down -v
```

---

## 🧩 Request Flow Summary

1. **Client** sends `POST /items` with JWT  
2. **NGINX** forwards to one of `app1` or `app2`  
3. **FastAPI route** calls `ItemService` via DI  
4. **ItemService** validates input → calls `ItemRepository`  
5. **MongoItemRepository** performs an async insert via Motor  
6. **MongoDB replica set** writes to PRIMARY, replicates to SECONDARIES  
7. **Result** bubbles up to client

---

## 🩺 Troubleshooting

| Issue | Fix |
|-------|-----|
| `Server selection timed out` in Compass | Use `MODE=host` and connect with `mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0` |
| Replica set shows “not initialized” | Run `docker compose down -v && docker compose up -d` to let `mongo-setup` initialize |
| Swagger endpoints show 401 | Click **Authorize** in Swagger and paste the JWT token |
| Writes not appearing in DB | Ensure app’s `MONGO_URI` matches RS advertised hosts (`internal` vs `host` mode) |
| 503 Docker Hub errors | The compose uses `mirror.gcr.io` base images; if still failing, switch to local registry or another mirror |

---

## 🧪 Extending the Project

Ideas for next steps:
- Persist users (add `MongoUserRepository` & update `AuthService`)
- Add background tasks (e.g., Celery or FastAPI Tasks)
- Integrate Prometheus metrics
- Add integration/unit tests with `pytest-asyncio`
- Introduce message broker (e.g., NATS or Kafka) for event-driven flows

---

**Maintained by:** Lazy Teacher of Yours, I will be king of teachers (not sure)  
**Keywords:** `fastapi`, `mongodb`, `docker`, `replicaset`, `nginx`, `clean-architecture`, `jwt`, `resilience`, `fault-tolerance`
